#!/usr/bin/env python3
"""Measure iOS Release artifacts and emit normalized evidence into .size-analysis."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any, List, Optional, Tuple

from analyze_build_settings import inspect as inspect_build_settings


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def enforce_release_only(configuration: str) -> None:
    if configuration != "Release":
        raise SystemExit(
            f"This suite only supports Release size optimization. Received configuration: {configuration}"
        )


def resolve_input_path(raw_path: Optional[str], workspace_root: Path) -> Optional[Path]:
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate

    from_cwd = candidate.resolve()
    if from_cwd.exists():
        return from_cwd

    return (workspace_root / candidate).resolve()


def run(command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def bundle_size(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def first_app(root: Path) -> Optional[Path]:
    apps = sorted(root.rglob("*.app"))
    return apps[0] if apps else None


def detect_compatibility(workspace_root: Path) -> dict[str, Any]:
    warnings: List[str] = []
    limited_support: List[str] = []
    if (workspace_root / "Podfile").exists() or (workspace_root / "Pods").exists():
        limited_support.append("CocoaPods detected; analysis will stay conservative.")
    if (workspace_root / "Cartfile").exists() or (workspace_root / "Carthage").exists():
        limited_support.append("Carthage detected; framework attribution may be partial.")
    if not list(workspace_root.glob("*.xcodeproj")) and not list(workspace_root.glob("*.xcworkspace")):
        warnings.append("No .xcodeproj or .xcworkspace found at the workspace root.")
    return {"limited_support": limited_support, "warnings": warnings}


def archive_project(args: argparse.Namespace, artifacts_dir: Path) -> Tuple[Optional[Path], List[str]]:
    log: List[str] = []
    workspace_root = Path(args.workspace_root).resolve()
    if args.app_path:
        app_path = resolve_input_path(args.app_path, workspace_root)
        return app_path, log

    build_root = artifacts_dir / "build"
    build_root.mkdir(parents=True, exist_ok=True)
    derived_data_path = artifacts_dir / "DerivedData"
    derived_data_path.mkdir(parents=True, exist_ok=True)
    archive_path = build_root / "App.xcarchive"
    destination = args.destination or "generic/platform=iOS"

    command = ["xcodebuild"]
    workspace_path = resolve_input_path(args.workspace, workspace_root)
    project_path = resolve_input_path(args.project, workspace_root)
    if args.workspace:
        command.extend(["-workspace", str(workspace_path)])
    if args.project:
        command.extend(["-project", str(project_path)])
    if args.scheme:
        command.extend(["-scheme", args.scheme])
    command.extend(
        [
            "-configuration",
            args.configuration,
            "-destination",
            destination,
            "-derivedDataPath",
            str(derived_data_path),
            "-archivePath",
            str(archive_path),
            "archive",
            "SKIP_INSTALL=NO",
            "BUILD_LIBRARY_FOR_DISTRIBUTION=NO",
            "CODE_SIGNING_ALLOWED=NO",
            "CODE_SIGNING_REQUIRED=NO",
            "CODE_SIGN_IDENTITY=",
        ]
    )

    result = run(command, cwd=workspace_root)
    (artifacts_dir / "xcodebuild-archive.log").write_text(result.stdout + "\n" + result.stderr)
    if result.returncode != 0:
        log.append("xcodebuild archive failed; see xcodebuild-archive.log.")
        return None, log

    app = first_app(archive_path / "Products" / "Applications")
    if not app:
        log.append("Archive completed but no .app was found in Products/Applications.")
        return None, log
    return app, log


def export_ipa(
    args: argparse.Namespace,
    archive_app: Optional[Path],
    artifacts_dir: Path,
) -> Tuple[Optional[Path], List[str], Optional[str]]:
    log: List[str] = []
    workspace_root = Path(args.workspace_root).resolve()
    if args.ipa_path:
        ipa_path = resolve_input_path(args.ipa_path, workspace_root)
        return ipa_path, log, "provided"
    if not args.export_ipa or not archive_app:
        return None, log, None

    archive_root = archive_app.parents[2]
    export_path = artifacts_dir / "exported"
    export_path.mkdir(parents=True, exist_ok=True)
    export_options = artifacts_dir / "ExportOptions.plist"

    thinning_value = None if args.thinning in {None, "", "none"} else args.thinning
    if thinning_value and args.export_method == "app-store":
        log.append(
            "App thinning was requested for an App Store export; local thinning is not representative for App Store delivery."
        )

    thinning_block = ""
    if thinning_value:
        thinning_block = f"  <key>thinning</key>\n  <string>{thinning_value}</string>\n"

    export_options.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>method</key>
  <string>{method}</string>
  <key>destination</key>
  <string>export</string>
  <key>signingStyle</key>
  <string>automatic</string>
  <key>stripSwiftSymbols</key>
  <{strip_swift_symbols}/>
{thinning_block}</dict>
</plist>
""".format(
            method=args.export_method,
            strip_swift_symbols="true" if args.strip_swift_symbols else "false",
            thinning_block=thinning_block,
        )
    )

    command = [
        "xcodebuild",
        "-exportArchive",
        "-archivePath",
        str(archive_root),
        "-exportPath",
        str(export_path),
        "-exportOptionsPlist",
        str(export_options),
    ]
    result = run(command, cwd=workspace_root)
    (artifacts_dir / "xcodebuild-export.log").write_text(result.stdout + "\n" + result.stderr)
    if result.returncode != 0:
        packaged_ipa = package_unsigned_ipa(archive_app, artifacts_dir)
        if packaged_ipa:
            log.append("IPA export failed; created an unsigned packaged IPA fallback instead.")
            return packaged_ipa, log, "unsigned-packaged-fallback"
        log.append("IPA export failed; see xcodebuild-export.log.")
        return None, log, None

    ipa_files = sorted(export_path.glob("*.ipa"))
    return (ipa_files[0] if ipa_files else None), log, "xcodebuild-export"


def package_unsigned_ipa(app_path: Optional[Path], artifacts_dir: Path) -> Optional[Path]:
    if not app_path or not app_path.exists():
        return None
    export_path = artifacts_dir / "exported"
    payload_dir = export_path / "Payload"
    payload_dir.mkdir(parents=True, exist_ok=True)
    packaged_app = payload_dir / app_path.name
    if packaged_app.exists():
        shutil.rmtree(packaged_app)
    shutil.copytree(app_path, packaged_app)
    if not packaged_app.exists():
        return None

    ipa_path = export_path / f"{app_path.stem}-unsigned.ipa"
    with zipfile.ZipFile(ipa_path, "w", compression=zipfile.ZIP_DEFLATED) as handle:
        for item in payload_dir.rglob("*"):
            handle.write(item, item.relative_to(export_path))
    return ipa_path


def binary_path(app_path: Path) -> Optional[Path]:
    candidate = app_path / app_path.stem
    return candidate if candidate.exists() else None


def measure(args: argparse.Namespace) -> dict[str, Any]:
    enforce_release_only(args.configuration)

    workspace_root = Path(args.workspace_root).resolve()
    artifacts_dir = workspace_root / ".size-analysis"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    compatibility = detect_compatibility(workspace_root)
    (artifacts_dir / "compatibility.json").write_text(json.dumps(compatibility, indent=2) + "\n")

    build_settings_report: dict[str, Any] = {"entries": [], "recommendations": [], "warnings": []}
    if args.project or args.workspace:
        build_settings_args = argparse.Namespace(
            workspace_root=str(workspace_root),
            workspace=args.workspace,
            project=args.project,
            scheme=args.scheme,
            configuration=args.configuration,
        )
        build_settings_report = inspect_build_settings(build_settings_args)
        (artifacts_dir / "build-settings.json").write_text(json.dumps(build_settings_report, indent=2) + "\n")
        if build_settings_report.get("stdout") or build_settings_report.get("stderr"):
            (artifacts_dir / "xcodebuild-build-settings.log").write_text(
                f"{build_settings_report.get('stdout', '')}\n{build_settings_report.get('stderr', '')}"
            )

    app_path, archive_warnings = archive_project(args, artifacts_dir)
    if not app_path:
        baseline = {
            "run_label": args.run_label,
            "workspace_root": str(workspace_root),
            "scheme": args.scheme,
            "configuration": args.configuration,
            "artifact_source": "archive_failed",
            "export_method": args.export_method,
            "strip_swift_symbols": args.strip_swift_symbols,
            "thinning": args.thinning,
            "warnings": archive_warnings
            + compatibility["warnings"]
            + compatibility["limited_support"]
            + build_settings_report.get("warnings", []),
        }
        (artifacts_dir / "baseline.json").write_text(json.dumps(baseline, indent=2) + "\n")
        return baseline

    ipa_path, export_warnings, ipa_generation_mode = export_ipa(args, app_path, artifacts_dir)
    executable = binary_path(app_path)
    frameworks_dir = app_path / "Frameworks"
    plugins_dir = app_path / "PlugIns"
    executable_name = app_path.stem

    resource_bytes = sum(
        item.stat().st_size
        for item in app_path.rglob("*")
        if item.is_file()
        and "Frameworks" not in item.parts
        and "PlugIns" not in item.parts
        and "_CodeSignature" not in item.parts
        and not (item.parent == app_path and item.name == executable_name)
    )
    framework_bytes = bundle_size(frameworks_dir) if frameworks_dir.exists() else 0
    plugin_bytes = bundle_size(plugins_dir) if plugins_dir.exists() else 0
    executable_size = executable.stat().st_size if executable else 0
    app_bundle_bytes = bundle_size(app_path)
    ipa_size = ipa_path.stat().st_size if ipa_path and ipa_path.exists() else None

    top_recommendations: List[dict[str, Any]] = []
    if framework_bytes > executable_size and framework_bytes > 20 * 1024 * 1024:
        top_recommendations.append(
            {
                "id": "BIN004",
                "title": "Review oversized embedded frameworks",
                "area": "binary",
                "impact": "Potential multi-megabyte win",
                "risk": "medium",
                "confidence": "high",
                "fixer_eligible": "no",
                "evidence": f"Embedded frameworks total {human_bytes(framework_bytes)}.",
                "why": "Third-party frameworks dominate more of the shipped payload than the main executable.",
            }
        )
    if resource_bytes > app_bundle_bytes * 0.5:
        top_recommendations.append(
            {
                "id": "RES001",
                "title": "Audit the largest packaged resources",
                "area": "resources",
                "impact": "Likely high",
                "risk": "low",
                "confidence": "high",
                "fixer_eligible": "no",
                "evidence": f"Resources account for {human_bytes(resource_bytes)} of {human_bytes(app_bundle_bytes)} app bundle size.",
                "why": "Assets and bundled data appear to outweigh code and frameworks.",
            }
        )
    if compatibility["limited_support"]:
        top_recommendations.append(
            {
                "id": "STR002",
                "title": "Review limited-support packaging signals before applying fixes",
                "area": "structure",
                "impact": "Protects analysis quality",
                "risk": "low",
                "confidence": "high",
                "fixer_eligible": "no",
                "evidence": "; ".join(compatibility["limited_support"]),
                "why": "Unsupported packaging paths can distort dependency and resource attribution.",
            }
        )
    if args.thinning not in {None, "", "none"}:
        top_recommendations.append(
            {
                "id": "BIN006",
                "title": "Interpret thinning results carefully",
                "area": "binary",
                "impact": "Context-dependent",
                "risk": "low",
                "confidence": "medium",
                "fixer_eligible": "no",
                "evidence": f"Local export used thinning={args.thinning} with export method {args.export_method}.",
                "why": "Local thinning variants are useful for exploration, but App Store delivery applies Apple-managed processing.",
            }
        )
    top_recommendations.extend(build_settings_report.get("recommendations", []))

    baseline = {
        "run_label": args.run_label,
        "workspace_root": str(workspace_root),
        "scheme": args.scheme,
        "configuration": args.configuration,
        "artifact_source": "app_path" if args.app_path else "xcodebuild archive",
        "archive_path": str(app_path.parents[2]) if len(app_path.parents) >= 3 and app_path.parents[2].suffix == ".xcarchive" else None,
        "app_path": str(app_path),
        "ipa_path": str(ipa_path) if ipa_path else None,
        "ipa_generation_mode": ipa_generation_mode,
        "export_method": args.export_method,
        "strip_swift_symbols": args.strip_swift_symbols,
        "thinning": args.thinning,
        "app_bundle_size_bytes": app_bundle_bytes,
        "app_bundle_size_human": human_bytes(app_bundle_bytes),
        "executable_size_bytes": executable_size,
        "executable_size_human": human_bytes(executable_size),
        "frameworks_size_bytes": framework_bytes,
        "frameworks_size_human": human_bytes(framework_bytes),
        "plugins_size_bytes": plugin_bytes,
        "plugins_size_human": human_bytes(plugin_bytes),
        "resource_size_bytes": resource_bytes,
        "resource_size_human": human_bytes(resource_bytes),
        "ipa_size_bytes": ipa_size,
        "ipa_size_human": human_bytes(ipa_size) if ipa_size is not None else None,
        "build_settings_summary": build_settings_report.get("entries", []),
        "warnings": archive_warnings
        + export_warnings
        + compatibility["warnings"]
        + compatibility["limited_support"]
        + build_settings_report.get("warnings", []),
        "recommendations": top_recommendations,
    }
    (artifacts_dir / "baseline.json").write_text(json.dumps(baseline, indent=2) + "\n")
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure iOS Release build size and emit .size-analysis artifacts.")
    parser.add_argument("--workspace-root", default=".", help="Workspace root containing the Xcode project")
    parser.add_argument("--workspace", help="Path to .xcworkspace to archive")
    parser.add_argument("--project", help="Path to .xcodeproj to archive")
    parser.add_argument("--scheme", help="Xcode scheme name")
    parser.add_argument("--configuration", default="Release", help="Build configuration")
    parser.add_argument("--destination", help="xcodebuild destination, defaults to generic/platform=iOS")
    parser.add_argument("--app-path", help="Use an existing .app bundle instead of archiving")
    parser.add_argument("--ipa-path", help="Use an existing .ipa for IPA size measurement")
    parser.add_argument("--export-ipa", action="store_true", help="Export an IPA after archiving")
    parser.add_argument("--export-method", default="app-store", help="Export method used for xcodebuild -exportArchive")
    parser.add_argument(
        "--strip-swift-symbols",
        dest="strip_swift_symbols",
        action="store_true",
        default=True,
        help="Enable stripSwiftSymbols during IPA export (default: enabled)",
    )
    parser.add_argument(
        "--no-strip-swift-symbols",
        dest="strip_swift_symbols",
        action="store_false",
        help="Disable stripSwiftSymbols during IPA export",
    )
    parser.add_argument(
        "--thinning",
        default="none",
        help="Optional export thinning value. Use 'none' for no thinning.",
    )
    parser.add_argument("--run-label", default="baseline", help="Label to write into baseline.json")
    args = parser.parse_args()

    baseline = measure(args)
    print(json.dumps(baseline, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
