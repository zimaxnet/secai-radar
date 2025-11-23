#!/usr/bin/env python3
"""
Generate a sanitized questionnaire markdown file from the normalized CSVs.

The script reads ALL_CONTROLS.csv (or the domain CSVs) and emits grouped
questions per security domain so consultants can walk stakeholders through
the assessment in a consistent order.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT = CURRENT_DIR.parents[1]
CSV_DEFAULT = ROOT / "security_domains" / "csv" / "ALL_CONTROLS.csv"
OUTPUT_DIR_DEFAULT = CURRENT_DIR / "output"


def load_controls(csv_path: Path) -> dict[str, list[dict[str, str]]]:
    rows_by_domain: dict[str, list[dict[str, str]]] = defaultdict(list)
    with csv_path.open("r", newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            domain = (
                row.get("DomainName")
                or row.get("Domain")
                or row.get("DomainTitle")
                or "Uncategorized"
            )
            rows_by_domain[domain].append(row)
    for controls in rows_by_domain.values():
        controls.sort(key=lambda r: r.get("ControlID", ""))
    return rows_by_domain


def render_markdown(rows_by_domain: dict[str, list[dict[str, str]]]) -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    lines = [
        "# SecAI Radar – Assessment Questionnaire",
        "",
        f"_Generated: {timestamp}_",
        "",
        "Use this walkthrough to capture stakeholder responses before running the evidence collector.",
        "",
    ]

    for domain, controls in sorted(rows_by_domain.items()):
        lines.append(f"## {domain}")
        lines.append("")
        for control in controls:
            control_id = control.get("ControlID", "UNKNOWN")
            question = (
                control.get("AssessmentQuestion")
                or control.get("Question")
                or control.get("ControlDescription")
                or "Describe the control posture."
            )
            evidence = (
                control.get("EvidenceChecklist")
                or control.get("RequiredEvidence")
                or control.get("EvidenceItems")
                or ""
            )
            lines.append(f"### {control_id}")
            lines.append("")
            lines.append(f"**Question:** {question}")
            if evidence:
                lines.append("")
                lines.append(f"**Suggested Evidence:** {evidence}")
            lines.append("")
            lines.append("*Notes:*")
            lines.append("")
            lines.append("---")
            lines.append("")
    return "\n".join(lines).strip() + "\n"


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the SecAI Radar questionnaire from CSVs.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=CSV_DEFAULT,
        help="Path to ALL_CONTROLS.csv (default: analysis/security_domains/csv/ALL_CONTROLS.csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR_DEFAULT,
        help="Destination folder for generated questionnaire (default: questionnaire/output)",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="",
        help="Optional explicit filename (default: timestamp-based).",
    )
    args = parser.parse_args()

    csv_path = args.csv.resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    rows_by_domain = load_controls(csv_path)
    markdown = render_markdown(rows_by_domain)

    output_dir = ensure_output_dir(args.output_dir.resolve())
    if args.filename:
        output_file = output_dir / args.filename
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_file = output_dir / f"questionnaire_{timestamp}.md"

    output_file.write_text(markdown, encoding="utf-8")
    print(f"Questionnaire written to {output_file}")


if __name__ == "__main__":
    main()

