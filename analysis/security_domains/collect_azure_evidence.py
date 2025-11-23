#!/usr/bin/env python3
"""
Execute Azure CLI evidence commands defined in YAML and push the outputs
into the per-domain CSVs so SecAI Radar can import evidence-aware data.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

CURRENT_DIR = Path(__file__).resolve().parent
ROOT = CURRENT_DIR.parents[1]

if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from build_domain_csvs import CSV_HEADERS, load_domain_codes, slugify  # type: ignore

CONFIG_DEFAULT = CURRENT_DIR / "evidence_commands.yaml"
CSV_DIR_DEFAULT = CURRENT_DIR / "csv"
EVIDENCE_DIR_DEFAULT = CURRENT_DIR / "evidence_artifacts"
MAPPING_JSON = CURRENT_DIR / "control_mappings.json"


def resolve_value(value):
    if isinstance(value, str) and value.startswith("env:"):
        env_key = value.split("env:", 1)[1]
        return os.getenv(env_key, "")
    return value


def merge_context(base: Dict[str, str], override: Dict[str, str] | None) -> Dict[str, str]:
    merged = dict(base)
    if override:
        for key, value in override.items():
            merged[key] = resolve_value(value)
    return merged


def safe_step_name(name: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", name).strip("-")
    return cleaned or fallback


def run_command(command: str, dry_run: bool) -> Dict[str, str | int]:
    if dry_run:
        return {"status": "dry-run", "stdout": "", "stderr": "", "exit_code": 0}
    try:
        completed = subprocess.run(
            command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )
        status = "success" if completed.returncode == 0 else "error"
        return {
            "status": status,
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
            "exit_code": completed.returncode,
        }
    except FileNotFoundError as exc:
        return {
            "status": "error",
            "stdout": "",
            "stderr": str(exc),
            "exit_code": 127,
        }


def write_artifact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_for_control(
    control_id: str,
    control_cfg: dict,
    base_context: Dict[str, str],
    evidence_dir: Path,
    dry_run: bool,
) -> Tuple[List[dict], int]:
    evidence_steps = control_cfg.get("evidence") or []
    if not evidence_steps:
        return [], 0

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    control_dir = evidence_dir / control_id
    artifacts: List[dict] = []

    for idx, step in enumerate(evidence_steps, start=1):
        step_name = step.get("name") or f"step{idx}"
        safe_name = safe_step_name(step_name, f"step{idx}")
        vars_override = step.get("vars") or {}
        context = {k: str(v) for k, v in merge_context(base_context, vars_override).items()}
        command_tpl = step.get("command")
        if not command_tpl:
            artifacts.append({
                "name": step_name,
                "status": "error",
                "error": "Missing 'command' in config",
            })
            continue
        try:
            command = command_tpl.format(**context)
        except KeyError as exc:
            artifacts.append({
                "name": step_name,
                "status": "error",
                "error": f"Missing placeholder {exc}",
                "command": command_tpl,
            })
            continue

        output_format = (step.get("output") or "json").lower()
        ext_map = {
            "json": "json",
            "txt": "txt",
            "text": "txt",
            "csv": "csv",
            "tsv": "tsv",
        }
        extension = ext_map.get(output_format, "txt")
        artifact_path = control_dir / f"{timestamp}_{safe_name}.{extension}"

        result = run_command(command, dry_run)
        if dry_run:
            content = f"[DRY RUN] Would run:\n{command}\n"
        else:
            stdout = result.get("stdout") or ""
            stderr = result.get("stderr") or ""
            content = stdout if stdout.strip() else stderr
        write_artifact(artifact_path, content)

        try:
            rel_path = artifact_path.relative_to(ROOT)
        except ValueError:
            rel_path = artifact_path

        artifact_meta = {
            "name": step_name,
            "command": command,
            "path": str(rel_path),
            "capturedAt": timestamp,
            "status": result.get("status"),
            "exitCode": result.get("exit_code"),
        }
        stderr_text = result.get("stderr")
        if stderr_text:
            artifact_meta["stderr"] = str(stderr_text)[:4000]
        artifacts.append(artifact_meta)

    success_count = sum(1 for a in artifacts if a.get("status") in {"success", "dry-run"})
    return artifacts, success_count


def update_csv(csv_path: Path, updates: Dict[str, dict]) -> None:
    if not csv_path.exists() or not updates:
        return
    with csv_path.open("r", newline="", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        rows = list(reader)
        fieldnames = reader.fieldnames or CSV_HEADERS

    dirty = False
    for row in rows:
        control_id = row.get("ControlID")
        if control_id in updates:
            row.update(updates[control_id])
            dirty = True

    if not dirty:
        return

    with csv_path.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_mapping(path: Path) -> Dict[str, dict]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Azure evidence and update SecAI domain CSVs.")
    parser.add_argument("--config", type=Path, default=CONFIG_DEFAULT, help="YAML file describing evidence commands.")
    parser.add_argument("--csv-dir", type=Path, default=CSV_DIR_DEFAULT, help="Directory containing domain CSVs.")
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE_DIR_DEFAULT, help="Where to store raw evidence artifacts.")
    parser.add_argument("--control", action="append", help="Limit run to specific control IDs (can repeat).")
    parser.add_argument("--dry-run", action="store_true", help="Skip executing Azure CLI commands; still writes placeholders.")
    parser.add_argument("--skip-csv", action="store_true", help="Do not update CSV files (useful for smoke tests).")
    args = parser.parse_args()

    if not args.config.exists():
        raise FileNotFoundError(f"Config not found: {args.config}")

    config = yaml.safe_load(args.config.read_text()) or {}
    base_context = {k: str(resolve_value(v)) for k, v in (config.get("context") or {}).items()}
    tenant = config.get("tenant", "")
    controls_cfg: Dict[str, dict] = {str(k).upper(): v for k, v in (config.get("controls") or {}).items()}

    selected_controls = None
    if args.control:
        selected_controls = {c.upper() for c in args.control}

    mapping = load_mapping(MAPPING_JSON)
    domain_codes = load_domain_codes()
    domain_file_map = {
        code: args.csv_dir / f"{code}_{slugify(name)}.csv"
        for code, name in domain_codes.items()
    }
    aggregate_csv = args.csv_dir / "ALL_CONTROLS.csv"

    updates: Dict[str, dict] = {}
    total_artifacts = 0
    domains_to_touch: set[str] = set()

    for control_id, control_cfg in controls_cfg.items():
        if selected_controls and control_id not in selected_controls:
            continue
        mapping_entry = mapping.get(control_id)
        domain_code = control_cfg.get("domain") or (mapping_entry.get("domainCode") if mapping_entry else "")
        if not domain_code:
            print(f"[WARN] No domain code for {control_id}; skipping.")
            continue
        artifacts, success_count = collect_for_control(
            control_id,
            control_cfg,
            base_context,
            args.evidence_dir,
            args.dry_run,
        )
        if not artifacts:
            print(f"[WARN] No evidence steps for {control_id}; skipping.")
            continue
        total_artifacts += len(artifacts)
        summary = json.dumps(artifacts, indent=2)
        updates[control_id] = {
            "EvidenceArtifacts": summary,
            "AvailableEvidenceCount": str(success_count),
            "EvidenceLastCollected": datetime.now(timezone.utc).isoformat(),
        }
        print(f"[INFO] {control_id}: captured {success_count}/{len(artifacts)} artifacts.")

        domain_csv = domain_file_map.get(domain_code)
        if not domain_csv or not domain_csv.exists():
            print(f"[WARN] Domain CSV missing for {domain_code} ({control_id}).")
            continue
        domains_to_touch.add(domain_code)

    if args.skip_csv or not updates:
        print("[INFO] No CSV updates requested." if args.skip_csv else "[INFO] Nothing to update.")
        return

    for domain_code in domains_to_touch:
        csv_path = domain_file_map.get(domain_code)
        if csv_path:
            update_csv(csv_path, updates)
    update_csv(aggregate_csv, updates)

    print(f"[INFO] Updated {len(updates)} controls ({total_artifacts} artifacts). Tenant={tenant}")


if __name__ == "__main__":
    main()
