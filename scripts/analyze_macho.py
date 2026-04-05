#!/usr/bin/env python3
"""Inspect executables, frameworks, and architecture slices for size analysis."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional


def run_command(command: list[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def executable_for_framework(path: Path) -> Optional[Path]:
    candidate = path / path.stem
    if candidate.exists():
        return candidate
    binaries = [item for item in path.iterdir() if item.is_file() and os.access(item, os.X_OK)]
    return binaries[0] if binaries else None


def slice_info(binary: Path) -> list[str]:
    output = run_command(["xcrun", "lipo", "-info", str(binary)])
    if not output:
        return []
    if "Non-fat file:" in output and "is architecture:" in output:
        return [output.split("is architecture:", 1)[1].strip()]
    if "Architectures in the fat file:" in output:
        tail = output.split("are:", 1)[-1]
        return [value.strip() for value in tail.split() if value.strip()]
    return []


def macho_breakdown(binary: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(binary),
        "size_bytes": binary.stat().st_size,
        "size_human": human_bytes(binary.stat().st_size),
        "bundle_size_bytes": binary.stat().st_size,
        "bundle_size_human": human_bytes(binary.stat().st_size),
        "architectures": slice_info(binary),
    }
    size_output = run_command(["xcrun", "size", "-m", "-l", str(binary)])
    if size_output:
        info["size_output"] = size_output
    return info


def collect(app_path: Path) -> dict[str, Any]:
    frameworks_dir = app_path / "Frameworks"
    binaries: list[dict[str, Any]] = []

    main_binary = app_path / app_path.stem
    if main_binary.exists():
        binaries.append({"kind": "app-executable", **macho_breakdown(main_binary)})

    if frameworks_dir.exists():
        for framework in sorted(frameworks_dir.glob("*.framework")):
            executable = executable_for_framework(framework)
            framework_info: dict[str, Any] = {
                "kind": "framework",
                "path": str(framework),
                "bundle_size_bytes": sum(
                    child.stat().st_size for child in framework.rglob("*") if child.is_file()
                ),
            }
            framework_info["bundle_size_human"] = human_bytes(framework_info["bundle_size_bytes"])
            if executable:
                framework_info["binary"] = macho_breakdown(executable)
            binaries.append(framework_info)

    binaries.sort(key=lambda item: item.get("bundle_size_bytes", item.get("size_bytes", 0)), reverse=True)
    total_framework_bytes = sum(item.get("bundle_size_bytes", 0) for item in binaries if item["kind"] == "framework")

    return {
        "app_path": str(app_path),
        "total_framework_bytes": total_framework_bytes,
        "total_framework_human": human_bytes(total_framework_bytes),
        "entries": binaries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze binary and framework size within an .app bundle.")
    parser.add_argument("app_path", help="Path to the built .app bundle")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    app_path = Path(args.app_path).resolve()
    if not app_path.exists():
        raise SystemExit(f"App bundle not found: {app_path}")

    report = collect(app_path)
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
