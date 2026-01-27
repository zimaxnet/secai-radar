"""
Drift Sentinel Worker (T-074) — Detects score/tier/flag/evidence changes.
Writes drift_events with severity; produces top movers/downgrades candidate lists.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar",
)

EVENT_TYPES = (
    "ScoreChanged",
    "FlagChanged",
    "EvidenceAdded",
    "EvidenceRemoved",
)
SEVERITIES = ("Critical", "High", "Medium", "Low")


def _hash16(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _severity_for_score_drop(delta: float) -> str:
    if delta <= -15:
        return "Critical"
    if delta <= -10:
        return "High"
    if delta <= -5:
        return "Medium"
    return "Low"


def _severity_for_score_gain(delta: float) -> str:
    if delta >= 15:
        return "Medium"
    if delta >= 10:
        return "Low"
    return "Low"


def _get_current_and_previous(cur, server_id: str, from_staging: bool = False) -> Optional[Tuple[dict, dict]]:
    ptr = "latest_scores_staging" if from_staging else "latest_scores"
    cur.execute(
        f"""
        SELECT ls.server_id, ss.score_id, ss.assessed_at, ss.trust_score, ss.tier,
               ss.fail_fast_flags, ss.risk_flags
        FROM {ptr} ls
        JOIN score_snapshots ss ON ls.score_id = ss.score_id
        WHERE ls.server_id = %s
        """,
        (server_id,),
    )
    row = cur.fetchone()
    if not row:
        return None
    current = {
        "server_id": row[0],
        "score_id": row[1],
        "assessed_at": row[2],
        "trust_score": float(row[3]),
        "tier": row[4],
        "fail_fast_flags": row[5] or [],
        "risk_flags": row[6] or [],
    }
    cur.execute(
        """
        SELECT score_id, assessed_at, trust_score, tier, fail_fast_flags, risk_flags
        FROM score_snapshots
        WHERE server_id = %s AND assessed_at < %s
        ORDER BY assessed_at DESC
        LIMIT 1
        """,
        (server_id, current["assessed_at"]),
    )
    prev_row = cur.fetchone()
    if not prev_row:
        return None
    previous = {
        "score_id": prev_row[0],
        "assessed_at": prev_row[1],
        "trust_score": float(prev_row[2]),
        "tier": prev_row[3],
        "fail_fast_flags": prev_row[4] or [],
        "risk_flags": prev_row[5] or [],
    }
    return (current, previous)


def _evidence_count(cur, server_id: str, before: Optional[datetime]) -> int:
    if before is None:
        cur.execute("SELECT COUNT(*) FROM evidence_items WHERE server_id = %s", (server_id,))
    else:
        cur.execute(
            "SELECT COUNT(*) FROM evidence_items WHERE server_id = %s AND captured_at < %s",
            (server_id, before),
        )
    return cur.fetchone()[0]


def _flags_equal(a: List, b: List) -> bool:
    return json.dumps(a or [], sort_keys=True) == json.dumps(b or [], sort_keys=True)


def _detect_and_write_drift(
    cur,
    server_id: str,
    current: dict,
    previous: dict,
    evidence_current: int,
    evidence_previous: int,
    now: datetime,
) -> List[Dict[str, Any]]:
    written: List[Dict[str, Any]] = []
    delta = current["trust_score"] - previous["trust_score"]

    if delta != 0:
        severity = _severity_for_score_drop(delta) if delta < 0 else _severity_for_score_gain(delta)
        summary = f"Trust score {previous['trust_score']:.1f} → {current['trust_score']:.1f} (Δ{delta:+.1f}); tier {previous['tier']} → {current['tier']}"
        diff = {"trust_score_old": previous["trust_score"], "trust_score_new": current["trust_score"], "tier_old": previous["tier"], "tier_new": current["tier"]}
        ts = getattr(current["assessed_at"], "isoformat", lambda: str(current["assessed_at"]))()
        drift_id = _hash16(f"{server_id}|ScoreChanged|{ts}|{delta}")
        cur.execute(
            """
            INSERT INTO drift_events (drift_id, server_id, detected_at, severity, event_type, summary, diff_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (drift_id) DO NOTHING
            """,
            (drift_id, server_id, now, severity, "ScoreChanged", summary, json.dumps(diff)),
        )
        if cur.rowcount:
            written.append({"event_type": "ScoreChanged", "severity": severity, "delta": delta})

    if not _flags_equal(current.get("fail_fast_flags") or [], previous.get("fail_fast_flags") or []) or not _flags_equal(
        current.get("risk_flags") or [], previous.get("risk_flags") or []
    ):
        severity = "High" if (current.get("fail_fast_flags") or []) and not (previous.get("fail_fast_flags") or []) else "Medium"
        summary = "Fail-fast or risk flags changed"
        diff = {"fail_fast_old": previous.get("fail_fast_flags"), "fail_fast_new": current.get("fail_fast_flags"), "risk_old": previous.get("risk_flags"), "risk_new": current.get("risk_flags")}
        ts = getattr(current["assessed_at"], "isoformat", lambda: str(current["assessed_at"]))()
        drift_id = _hash16(f"{server_id}|FlagChanged|{ts}")
        cur.execute(
            """
            INSERT INTO drift_events (drift_id, server_id, detected_at, severity, event_type, summary, diff_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (drift_id) DO NOTHING
            """,
            (drift_id, server_id, now, severity, "FlagChanged", summary, json.dumps(diff)),
        )
        if cur.rowcount:
            written.append({"event_type": "FlagChanged", "severity": severity})

    if evidence_current > evidence_previous:
        severity = "Low"
        summary = f"Evidence items {evidence_previous} → {evidence_current}"
        diff = {"count_old": evidence_previous, "count_new": evidence_current}
        ts = getattr(current["assessed_at"], "isoformat", lambda: str(current["assessed_at"]))()
        drift_id = _hash16(f"{server_id}|EvidenceAdded|{ts}")
        cur.execute(
            """
            INSERT INTO drift_events (drift_id, server_id, detected_at, severity, event_type, summary, diff_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (drift_id) DO NOTHING
            """,
            (drift_id, server_id, now, severity, "EvidenceAdded", summary, json.dumps(diff)),
        )
        if cur.rowcount:
            written.append({"event_type": "EvidenceAdded"})
    elif evidence_current < evidence_previous:
        severity = "Medium"
        summary = f"Evidence items {evidence_previous} → {evidence_current}"
        diff = {"count_old": evidence_previous, "count_new": evidence_current}
        ts = getattr(current["assessed_at"], "isoformat", lambda: str(current["assessed_at"]))()
        drift_id = _hash16(f"{server_id}|EvidenceRemoved|{ts}")
        cur.execute(
            """
            INSERT INTO drift_events (drift_id, server_id, detected_at, severity, event_type, summary, diff_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (drift_id) DO NOTHING
            """,
            (drift_id, server_id, now, severity, "EvidenceRemoved", summary, json.dumps(diff)),
        )
        if cur.rowcount:
            written.append({"event_type": "EvidenceRemoved"})

    return written


def _use_staging_as_current(conn) -> bool:
    """Use latest_scores_staging as 'current' when it has rows (pipeline ran scorer with WRITE_TO_STAGING)."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM latest_scores_staging LIMIT 1")
            return cur.fetchone() is not None
    except Exception:
        return False


def run_drift_sentinel() -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    conn = psycopg2.connect(DATABASE_URL)
    try:
        use_staging = _use_staging_as_current(conn)
        ptr = "latest_scores_staging" if use_staging else "latest_scores"
        with conn.cursor() as cur:
            cur.execute(f"SELECT server_id FROM {ptr}")
            server_ids = [r[0] for r in cur.fetchall()]
        movers: List[Dict[str, Any]] = []
        downgrades: List[Dict[str, Any]] = []
        events_written = 0
        for server_id in server_ids:
            with conn.cursor() as cur:
                pair = _get_current_and_previous(cur, server_id, from_staging=use_staging)
            if not pair:
                continue
            current, previous = pair
            evidence_current = 0
            evidence_previous = 0
            with conn.cursor() as cur:
                evidence_current = _evidence_count(cur, server_id, None)
                evidence_previous = _evidence_count(cur, server_id, previous["assessed_at"])
            with conn.cursor() as cur:
                written = _detect_and_write_drift(
                    cur, server_id, current, previous,
                    evidence_current, evidence_previous, now,
                )
                events_written += len(written)
            delta = current["trust_score"] - previous["trust_score"]
            if delta > 0:
                movers.append({"server_id": server_id, "delta": round(delta, 2), "trust_score": current["trust_score"], "tier": current["tier"]})
            elif delta < 0:
                downgrades.append({"server_id": server_id, "delta": round(delta, 2), "trust_score": current["trust_score"], "tier": current["tier"]})
        conn.commit()
        movers.sort(key=lambda x: -x["delta"])
        downgrades.sort(key=lambda x: x["delta"])
        return {
            "success": True,
            "driftEventsWritten": events_written,
            "topMovers": movers[:20],
            "topDowngrades": downgrades[:20],
            "serversChecked": len(server_ids),
            "completedAt": now.isoformat(),
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "error": str(e),
            "completedAt": now.isoformat(),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    result = run_drift_sentinel()
    print(json.dumps(result, indent=2))
