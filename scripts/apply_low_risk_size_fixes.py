#!/usr/bin/env python3
"""Apply narrowly scoped, approved Release size build-setting fixes to target-level pbxproj blocks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

SUPPORTED_SETTINGS = {
    "COPY_PHASE_STRIP": "YES",
    "STRIP_INSTALLED_PRODUCT": "YES",
}


def load_approved_settings(path: Path) -> List[str]:
    payload = json.loads(path.read_text())
    approved = payload.get("approved_settings", [])
    return [item for item in approved if item in SUPPORTED_SETTINGS]


def is_target_level_release_block(body: str) -> bool:
    return "PRODUCT_NAME =" in body or "PRODUCT_BUNDLE_IDENTIFIER =" in body


def apply_setting_to_release_blocks(content: str, setting: str, value: str) -> Tuple[str, int]:
    pattern = re.compile(
        r"(?P<header>\s+[A-F0-9]+ /\* Release \*/ = \{\n\s+isa = XCBuildConfiguration;\n\s+buildSettings = \{\n)(?P<body>.*?)(?P<footer>\n\s+\};\n\s+name = Release;\n\s+\};)",
        re.DOTALL,
    )
    replacements = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal replacements
        body = match.group("body")
        if not is_target_level_release_block(body):
            return match.group(0)

        setting_pattern = re.compile(rf"(\n\s+{re.escape(setting)} = )[^;]+;")
        next_body = body
        if setting_pattern.search(body):
            next_body = setting_pattern.sub(rf"\1{value};", body)
        else:
            next_body = body + f"\n\t\t\t\t{setting} = {value};"

        if next_body != body:
            replacements += 1
        return match.group("header") + next_body + match.group("footer")

    return pattern.sub(replace, content), replacements


def apply_settings(pbxproj_path: Path, settings: Iterable[str]) -> Dict[str, List[str]]:
    original = pbxproj_path.read_text()
    updated = original
    applied: List[str] = []
    for setting in settings:
        value = SUPPORTED_SETTINGS[setting]
        next_content, replacements = apply_setting_to_release_blocks(updated, setting, value)
        if replacements > 0:
            applied.append(setting)
            updated = next_content

    if updated != original:
        pbxproj_path.write_text(updated)

    return {"applied_settings": applied}


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply approved low-risk Release size fixes.")
    parser.add_argument("--pbxproj", required=True, help="Path to project.pbxproj")
    parser.add_argument("--approved-json", required=True, help="JSON file containing an approved_settings array")
    args = parser.parse_args()

    pbxproj_path = Path(args.pbxproj).resolve()
    approved_path = Path(args.approved_json).resolve()
    settings = load_approved_settings(approved_path)
    result = apply_settings(pbxproj_path, settings)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
