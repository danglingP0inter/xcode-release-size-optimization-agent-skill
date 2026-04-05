#!/usr/bin/env python3
"""Render the main markdown optimization report from collected JSON artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}


def metric_line(title: str, value: Optional[int]) -> str:
    if value is None:
        return f"- {title}: unavailable"
    return f"- {title}: {value:,} bytes"


def format_bool(value: Any) -> str:
    if value is True:
        return "enabled"
    if value is False:
        return "disabled"
    return str(value)


def relativize_path(label: Any, workspace_root: Path) -> str:
    if not isinstance(label, str):
        return str(label)
    try:
        path = Path(label)
        if path.is_absolute():
            return str(path.resolve().relative_to(workspace_root.resolve()))
    except Exception:
        return label
    return label


def top_lines(items: list[dict[str, Any]], label_key: str, size_key: str, workspace_root: Path, limit: int = 5) -> list[str]:
    lines = []
    for item in items[:limit]:
        label = relativize_path(item.get(label_key, "unknown"), workspace_root)
        lines.append(f"- {label}: {item.get(size_key, 0):,} bytes")
    return lines or ["- None detected"]


def compatibility_lines(compatibility: dict[str, Any]) -> list[str]:
    warnings = compatibility.get("limited_support", []) + compatibility.get("warnings", [])
    if not warnings:
        return ["- Full support path detected"]
    return [f"- {warning}" for warning in warnings]


def render(artifacts_dir: Path) -> str:
    baseline = load_json(artifacts_dir / "baseline.json")
    build_settings = load_json(artifacts_dir / "build-settings.json")
    binaries = load_json(artifacts_dir / "top_binaries.json")
    resources = load_json(artifacts_dir / "top_resources.json")
    swiftpm = load_json(artifacts_dir / "swiftpm-summary.json")
    compatibility = load_json(artifacts_dir / "compatibility.json")
    comparison = load_json(artifacts_dir / "comparison.json")
    workspace_root = Path(baseline.get("workspace_root") or artifacts_dir.parent)

    recommendations = baseline.get("recommendations", [])
    recommendation_lines = []
    for item in recommendations:
        recommendation_lines.append(
            "\n".join(
                [
                    f"### [{item.get('id', 'REC')}] {item.get('title', 'Recommendation')}",
                    f"- Area: {item.get('area', 'general')}",
                    f"- Impact: {item.get('impact', 'TBD')}",
                    f"- Risk: {item.get('risk', 'unknown')}",
                    f"- Confidence: {item.get('confidence', 'unknown')}",
                    f"- Fixer eligible: {item.get('fixer_eligible', 'no')}",
                    f"- Evidence: {item.get('evidence', 'See JSON artifacts')}",
                    f"- Why it matters: {item.get('why', 'Improve shipping size with evidence-driven changes.')}",
                    "- Approval: [ ]",
                ]
            )
        )
    if not recommendation_lines:
        recommendation_lines.append(
            "### [INFO] No automatic recommendations generated\n"
            "- Review the binary and resource rankings and add manual follow-up items if needed.\n"
            "- Approval: [ ]"
        )

    verification_lines = ["- No post-change comparison yet"]
    if comparison.get("metrics"):
        verification_lines = []
        for key, item in comparison["metrics"].items():
            verification_lines.append(
                f"- {key}: {item['before']:,} -> {item['after']:,} bytes ({item['delta_human']})"
            )

    build_setting_lines = ["- Build settings unavailable"]
    if build_settings.get("entries"):
        build_setting_lines = []
        for entry in build_settings["entries"]:
            settings = entry.get("settings", {})
            rendered_settings = ", ".join(f"{key}={value}" for key, value in settings.items())
            build_setting_lines.append(f"- {entry.get('target', 'unknown target')}: {rendered_settings}")

    lines = [
        "# Xcode Release Size Optimization Plan",
        "",
        "## Project Context and Assumptions",
        f"- Workspace root: {workspace_root}",
        f"- Scheme: {baseline.get('scheme', 'unknown')}",
        f"- Configuration: {baseline.get('configuration', 'Release')}",
        f"- Artifact source: {baseline.get('artifact_source', 'unknown')}",
        f"- IPA generation: {baseline.get('ipa_generation_mode', 'not requested')}",
        f"- Export method: {baseline.get('export_method', 'unknown')}",
        f"- stripSwiftSymbols: {format_bool(baseline.get('strip_swift_symbols', 'unknown'))}",
        f"- Thinning: {baseline.get('thinning', 'none')}",
        *(f"- Warning: {warning}" for warning in baseline.get("warnings", [])),
        "",
        "## Compatibility Status",
        *compatibility_lines(compatibility or swiftpm),
        "",
        "## Baseline Measurements",
        metric_line("App bundle", baseline.get("app_bundle_size_bytes")),
        metric_line("Executable", baseline.get("executable_size_bytes")),
        metric_line("Embedded frameworks", baseline.get("frameworks_size_bytes")),
        metric_line("Plug-ins", baseline.get("plugins_size_bytes")),
        metric_line("Resources", baseline.get("resource_size_bytes")),
        metric_line("IPA", baseline.get("ipa_size_bytes")),
        "",
        "## Build and Export Settings",
        *build_setting_lines,
        "",
        "## Size Attribution Summary",
        "### Top binaries",
        *top_lines(binaries.get("entries", []), "path", "bundle_size_bytes", workspace_root),
        "### Top resources",
        *top_lines(resources.get("top_resources", []), "path", "size_bytes", workspace_root),
        "",
        "## Prioritized Recommendations",
        *recommendation_lines,
        "",
        "## Approval Checklist",
        "- [ ] Approve selected low-risk fixer-eligible items",
        "- [ ] Confirm any medium-risk symbol or optimization changes",
        "- [ ] Leave advisory-only items for manual follow-up",
        "",
        "## Verification Summary",
        *verification_lines,
        "",
        "## Unsupported or Partially Supported Findings",
        *compatibility_lines(compatibility or swiftpm),
    ]
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render size-optimization-plan.md from .size-analysis JSON artifacts.")
    parser.add_argument("--artifacts-dir", default=".size-analysis", help="Directory containing size-analysis JSON files")
    parser.add_argument("--output", default=".size-analysis/size-optimization-plan.md", help="Markdown output path")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir).resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report = render(artifacts_dir)
    output_path = Path(args.output).resolve()
    output_path.write_text(report)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
