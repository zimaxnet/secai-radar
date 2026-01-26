"""
Summary service - business logic for summary endpoint
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session


def get_summary_data(db: Session, window: str) -> Dict[str, Any]:
    """
    Get summary KPIs and highlights for a given time window.
    Shape matches frontend SummaryResponse (serversTracked, topMovers, etc.).
    """
    if window == "24h":
        delta = timedelta(days=1)
    elif window == "7d":
        delta = timedelta(days=7)
    else:
        delta = timedelta(days=30)
    cutoff_time = datetime.utcnow() - delta

    # TODO: Replace with real DB queries (count servers, tier, evidence, highlights)
    return {
        "serversTracked": 0,
        "providersTracked": 0,
        "tierCounts": {"A": 0, "B": 0, "C": 0, "D": 0},
        "evidenceConfidenceCounts": {"0": 0, "1": 0, "2": 0, "3": 0},
        "failFastCount": 0,
        "topMovers": [],
        "topDowngrades": [],
        "newEntrants": [],
        "notableDrift": [],
    }
