"""Utility helpers for loading AI orchestration workflow templates."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any, Dict

import yaml

WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / "orchestration" / "workflows"


class WorkflowNotFoundError(FileNotFoundError):
    """Raised when the requested workflow definition cannot be located."""


@functools.lru_cache(maxsize=16)
def load_workflow(name: str) -> Dict[str, Any]:
    """Load a workflow YAML definition by name.

    Args:
        name: Workflow name (file stem without extension).

    Returns:
        Parsed workflow dictionary.

    Raises:
        WorkflowNotFoundError: If no matching YAML file exists.
        ValueError: If the workflow file is empty or invalid.
    """

    workflow_path = WORKFLOWS_DIR / f"{name}.yaml"
    if not workflow_path.exists():
        raise WorkflowNotFoundError(f"Workflow definition '{name}' not found at {workflow_path}.")

    with workflow_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    if not isinstance(data, dict) or "name" not in data:
        raise ValueError(f"Workflow definition '{name}' is malformed. Expected dict with 'name'.")

    return data
