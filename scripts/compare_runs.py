#!/usr/bin/env python3
"""Compare baseline JSON reports and produce verification deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def human_bytes(value: int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    units = ["B", "KB", "MB", "GB"]
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{sign}{size:.1f} {unit}" if unit != "B" else f"{sign}{int(size)} B"
        size /= 1024
    return f"{sign}{value} B"


def extract_metrics(payload: dict[str, Any]) -> dict[str, int]:
    return {
        "app_bundle_size_bytes": int(payload.get("app_bundle_size_bytes") or 0),
        "executable_size_bytes": int(payload.get("executable_size_bytes") or 0),
        "frameworks_size_bytes": int(payload.get("frameworks_size_bytes") or 0),
        "plugins_size_bytes": int(payload.get("plugins_size_bytes") or 0),
        "resource_size_bytes": int(payload.get("resource_size_bytes") or 0),
        "ipa_size_bytes": int(payload.get("ipa_size_bytes") or 0),
    }


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_metrics = extract_metrics(before)
    after_metrics = extract_metrics(after)
    deltas = {}
    for key, before_value in before_metrics.items():
        after_value = after_metrics[key]
        delta = after_value - before_value
        deltas[key] = {
            "before": before_value,
            "after": after_value,
            "delta": delta,
            "delta_human": human_bytes(delta),
        }
    return {"before": before.get("run_label"), "after": after.get("run_label"), "metrics": deltas}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two size-analysis baseline JSON files.")
    parser.add_argument("before", help="Path to baseline JSON before changes")
    parser.add_argument("after", help="Path to baseline JSON after changes")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    before_payload = json.loads(Path(args.before).read_text())
    after_payload = json.loads(Path(args.after).read_text())
    report = compare(before_payload, after_payload)
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
