"""
Workflow Phases Module

Implements the three-phase workflow for Project Aethelgard:
1. Assessment and Discovery
2. Design and Conflict Resolution
3. Migration Planning
"""

from .assessment import AssessmentPhase
from .design import DesignPhase
from .migration import MigrationPhase

__all__ = [
    "AssessmentPhase",
    "DesignPhase",
    "MigrationPhase"
]

