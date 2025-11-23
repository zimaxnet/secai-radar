#!/usr/bin/env python3
"""
Render a lightweight markdown summary report from the normalized control CSVs.

This provides a demo-friendly stand-in for the final Word/PDF deliverable.
Extend or replace with DOCX templating when ready.
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
OUTPUT_DIR_DEFAULT = CURRENT_DIR / "report"


def load_domain_metrics(csv_path: Path) -> dict[str, dict[str, int]]:
    metrics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with csv_path.open("r", newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            domain = (
                row.get("DomainName")
                or row.get("Domain")
                or row.get("DomainTitle")
                or "Uncategorized"
            )
            status = (
                row.get("ComplianceStatus")
                or row.get("Status")
                or row.get("DocStatus")
                or "Unknown"
            ).title()
            metrics[domain]["TotalControls"] += 1
            metrics[domain][status] += 1
    return metrics


def render_markdown(metrics: dict[str, dict[str, int]]) -> str:
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    lines = [
        "# SecAI Radar – Assessment Summary (Demo)",
        "",
        f"_Generated: {generated}_",
        "",
        "This markdown summary mirrors the structure that the automated Word report will follow.",
        "",
        "| Domain | Total | Compliant | Partially Compliant | Non-Compliant | Unknown |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    domain_rows = []
    for domain, counts in metrics.items():
        total = counts.get("TotalControls", 0)
        compliant = counts.get("Compliant", 0)
        partial = counts.get("Partially Compliant", 0)
        non_compliant = counts.get("Non-Compliant", 0)
        unknown = counts.get("Unknown", total - compliant - partial - non_compliant)
        domain_rows.append((domain, total, compliant, partial, non_compliant, unknown))

    for row in sorted(domain_rows):
        domain, total, compliant, partial, non_compliant, unknown = row
        lines.append(
            f"| {domain} | {total} | {compliant} | {partial} | {non_compliant} | {unknown} |"
        )

    lines.append("")
    lines.append("## Next Steps")
    lines.append("")
    lines.append("- Fill in tenant-specific narrative content.")
    lines.append("- Embed evidence highlights referenced in the CSV metadata.")
    lines.append("- Export to DOCX/PDF using the preferred template tooling.")
    lines.append("")
    return "\n".join(lines)


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a demo assessment summary report.")
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
        help="Destination folder for rendered report (default: analysis/security_domains/output/report)",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="",
        help="Optional explicit filename (default: summary_<timestamp>.md).",
    )
    args = parser.parse_args()

    csv_path = args.csv.resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    metrics = load_domain_metrics(csv_path)
    markdown = render_markdown(metrics)

    output_dir = ensure_output_dir(args.output_dir.resolve())
    if args.filename:
        output_file = output_dir / args.filename
    else:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_file = output_dir / f"summary_{timestamp}.md"

    output_file.write_text(markdown, encoding="utf-8")
    print(f"Report written to {output_file}")


if __name__ == "__main__":
    main()

