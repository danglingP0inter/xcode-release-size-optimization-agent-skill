#!/usr/bin/env python3
"""Analyze app bundle resources and group them by category and duplicate content."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


RESOURCE_GROUPS = {
    ".png": "images",
    ".jpg": "images",
    ".jpeg": "images",
    ".heic": "images",
    ".gif": "images",
    ".pdf": "images",
    ".car": "asset-catalog",
    ".json": "data",
    ".plist": "data",
    ".db": "data",
    ".sqlite": "data",
    ".strings": "localization",
    ".stringsdict": "localization",
    ".storyboardc": "ui",
    ".xib": "ui",
    ".nib": "ui",
    ".ttf": "fonts",
    ".otf": "fonts",
    ".mp3": "media",
    ".mp4": "media",
    ".mov": "media",
}


def human_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{value} B"


def categorize(path: Path) -> str:
    if ".lproj" in path.parts:
        return "localization"
    if path.suffix.lower() in RESOURCE_GROUPS:
        return RESOURCE_GROUPS[path.suffix.lower()]
    return "other"


def sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(app_path: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    category_totals: Counter[str] = Counter()
    duplicates: defaultdict[str, list[str]] = defaultdict(list)
    executable_name = app_path.stem

    for path in sorted(app_path.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(app_path)
        if relative.parts and relative.parts[0] in {"Frameworks", "PlugIns", "_CodeSignature"}:
            continue
        if relative.name == executable_name and len(relative.parts) == 1:
            continue
        size = path.stat().st_size
        category = categorize(relative)
        category_totals[category] += size
        fingerprint = sha1(path)
        duplicates[fingerprint].append(str(relative))
        files.append(
            {
                "path": str(relative),
                "size_bytes": size,
                "size_human": human_bytes(size),
                "category": category,
            }
        )

    files.sort(key=lambda item: item["size_bytes"], reverse=True)
    duplicate_entries = [
        {"hash": fingerprint, "paths": paths, "duplicate_count": len(paths)}
        for fingerprint, paths in duplicates.items()
        if len(paths) > 1
    ]
    duplicate_entries.sort(key=lambda item: item["duplicate_count"], reverse=True)

    return {
        "app_path": str(app_path),
        "category_totals": {
            key: {"bytes": value, "human": human_bytes(value)}
            for key, value in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        },
        "top_resources": files[:100],
        "duplicate_resources": duplicate_entries[:100],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze resource size within an .app bundle.")
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
