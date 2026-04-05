#!/usr/bin/env python3
"""Inspect Release build settings relevant to size, stripping, and debug payloads."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

INTERESTING_KEYS = [
    "PRODUCT_NAME",
    "COPY_PHASE_STRIP",
    "STRIP_INSTALLED_PRODUCT",
    "STRIP_STYLE",
    "DEAD_CODE_STRIPPING",
    "DEBUG_INFORMATION_FORMAT",
    "DEPLOYMENT_POSTPROCESSING",
]


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


def run(command: List[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def normalize_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    upper = value.strip().upper()
    if upper in {"YES", "TRUE"}:
        return True
    if upper in {"NO", "FALSE"}:
        return False
    return None


def evaluate_entry(entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    settings = entry.get("buildSettings", {})
    product_name = settings.get("PRODUCT_NAME") or entry.get("target")
    findings: List[Dict[str, Any]] = []

    copy_phase_strip = normalize_bool(settings.get("COPY_PHASE_STRIP"))
    if copy_phase_strip is False:
        findings.append(
            {
                "id": "BIN003",
                "title": f"Enable stripping for Release product copy phase in {product_name}",
                "area": "binary",
                "impact": "Low to moderate",
                "risk": "medium",
                "confidence": "high",
                "fixer_eligible": "yes",
                "setting": "COPY_PHASE_STRIP",
                "target": product_name,
                "recommended_value": "YES",
                "evidence": f"COPY_PHASE_STRIP is {settings.get('COPY_PHASE_STRIP')}.",
                "why": "Release builds that skip product stripping can ship avoidable symbol payload.",
            }
        )

    strip_installed = normalize_bool(settings.get("STRIP_INSTALLED_PRODUCT"))
    if strip_installed is False:
        findings.append(
            {
                "id": "BIN003",
                "title": f"Review installed-product stripping in {product_name}",
                "area": "binary",
                "impact": "Low to moderate",
                "risk": "medium",
                "confidence": "medium",
                "fixer_eligible": "yes",
                "setting": "STRIP_INSTALLED_PRODUCT",
                "target": product_name,
                "recommended_value": "YES",
                "evidence": f"STRIP_INSTALLED_PRODUCT is {settings.get('STRIP_INSTALLED_PRODUCT')}.",
                "why": "Installed product stripping may reduce shipped binary size when disabled.",
            }
        )

    dead_code = normalize_bool(settings.get("DEAD_CODE_STRIPPING"))
    if dead_code is False:
        findings.append(
            {
                "id": "BIN001",
                "title": f"Enable dead code stripping in {product_name}",
                "area": "binary",
                "impact": "Potentially meaningful",
                "risk": "medium",
                "confidence": "medium",
                "fixer_eligible": "no",
                "setting": "DEAD_CODE_STRIPPING",
                "target": product_name,
                "recommended_value": "YES",
                "evidence": f"DEAD_CODE_STRIPPING is {settings.get('DEAD_CODE_STRIPPING')}.",
                "why": "Dead code stripping being disabled can retain unused code in the shipped executable.",
            }
        )

    return findings


def inspect(args: argparse.Namespace) -> Dict[str, Any]:
    enforce_release_only(args.configuration)

    workspace_root = Path(args.workspace_root).resolve()
    command = ["xcodebuild"]
    workspace_path = resolve_input_path(args.workspace, workspace_root)
    project_path = resolve_input_path(args.project, workspace_root)
    if args.workspace:
        command.extend(["-workspace", str(workspace_path)])
    if args.project:
        command.extend(["-project", str(project_path)])
    if args.scheme:
        command.extend(["-scheme", args.scheme])
    command.extend(["-configuration", args.configuration, "-showBuildSettings", "-json"])

    result = run(command, workspace_root)
    payload: Dict[str, Any] = {
        "workspace_root": str(workspace_root),
        "scheme": args.scheme,
        "configuration": args.configuration,
        "entries": [],
        "warnings": [],
        "recommendations": [],
    }
    if result.returncode != 0:
        payload["warnings"].append("Unable to read build settings; see xcodebuild-build-settings.log.")
        payload["stdout"] = result.stdout
        payload["stderr"] = result.stderr
        return payload

    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload["warnings"].append("xcodebuild -showBuildSettings did not return valid JSON.")
        payload["stdout"] = result.stdout
        payload["stderr"] = result.stderr
        return payload

    normalized_entries = []
    recommendations: List[Dict[str, Any]] = []
    for entry in entries:
        settings = entry.get("buildSettings", {})
        normalized_entries.append(
            {
                "target": entry.get("target"),
                "project": entry.get("project"),
                "settings": {key: settings.get(key) for key in INTERESTING_KEYS if key in settings},
            }
        )
        recommendations.extend(evaluate_entry(entry))

    payload["entries"] = normalized_entries
    payload["recommendations"] = recommendations
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Release build settings for size-related recommendations.")
    parser.add_argument("--workspace-root", default=".", help="Workspace root containing the Xcode project")
    parser.add_argument("--workspace", help="Path to .xcworkspace")
    parser.add_argument("--project", help="Path to .xcodeproj")
    parser.add_argument("--scheme", help="Xcode scheme name")
    parser.add_argument("--configuration", default="Release", help="Build configuration")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--log-output", help="Optional log output path")
    args = parser.parse_args()

    report = inspect(args)
    payload = json.dumps(report, indent=2)
    if args.log_output:
        log_path = Path(args.log_output)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(f"{report.get('stdout', '')}\n{report.get('stderr', '')}")
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
