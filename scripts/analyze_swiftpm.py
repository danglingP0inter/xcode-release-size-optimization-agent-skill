#!/usr/bin/env python3
"""Summarize SwiftPM usage and detect limited-support dependency managers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_package_resolved(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    if "pins" in payload:
        return payload["pins"]
    if "object" in payload and isinstance(payload["object"], dict):
        return payload["object"].get("pins", [])
    return []


def detect_workspace(root: Path) -> dict[str, Any]:
    resolved_candidates = [
        root / "Package.resolved",
        root / ".swiftpm" / "Package.resolved",
    ]
    resolved_candidates.extend(root.glob("*.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved"))
    resolved_candidates.extend(root.glob("*.xcworkspace/xcshareddata/swiftpm/Package.resolved"))

    packages: list[dict[str, Any]] = []
    package_resolved_path = None
    for candidate in resolved_candidates:
        pins = load_package_resolved(candidate)
        if pins:
            package_resolved_path = candidate
            packages = pins
            break

    warnings: list[str] = []
    limited_support: list[str] = []
    if (root / "Podfile").exists() or (root / "Pods").exists():
        limited_support.append("CocoaPods detected")
    if (root / "Cartfile").exists() or (root / "Carthage").exists():
        limited_support.append("Carthage detected")

    normalized_packages = []
    for item in packages:
        state = item.get("state", {})
        normalized_packages.append(
            {
                "identity": item.get("identity") or item.get("package"),
                "location": item.get("location") or item.get("repositoryURL"),
                "revision": state.get("revision"),
                "version": state.get("version"),
                "branch": state.get("branch"),
            }
        )

    return {
        "package_resolved_path": str(package_resolved_path) if package_resolved_path else None,
        "swiftpm_package_count": len(normalized_packages),
        "packages": normalized_packages,
        "limited_support": limited_support,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze SwiftPM metadata for an Xcode workspace.")
    parser.add_argument("workspace_root", help="Workspace or repository root")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    if not root.exists():
        raise SystemExit(f"Workspace root not found: {root}")

    report = detect_workspace(root)
    payload = json.dumps(report, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
