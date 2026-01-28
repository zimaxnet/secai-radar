"""
Daily Brief generator (T-075) — Sage Meridian integration stub.
Builds DailyBrief from movers/downgrades/new/drift; uses template; stores narrativeShort + narrativeLong in daily_briefs.
"""

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar",
)
METHODOLOGY_VERSION = os.getenv("METHODOLOGY_VERSION", "v1.0")
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _load_template() -> str:
    p = _TEMPLATE_DIR / "daily_brief.txt"
    if p.exists():
        return p.read_text(encoding="utf-8").strip()
    return (
        "MCP Trust Radar daily brief for {date}. {movers_phrase} {downgrades_phrase} {drift_phrase}\n\n"
        "Highlights:\n{highlights_list}"
    )


def _gather_from_drift(conn, brief_date: date) -> Dict[str, Any]:
    """Query drift_events for brief_date to build movers, downgrades, notable drift."""
    start = datetime(brief_date.year, brief_date.month, brief_date.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    movers: List[Dict[str, Any]] = []
    downgrades: List[Dict[str, Any]] = []
    notable: List[Dict[str, Any]] = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT server_id, event_type, severity, summary, diff_json, detected_at
            FROM drift_events
            WHERE detected_at >= %s AND detected_at < %s
            ORDER BY detected_at DESC
            """,
            (start, end),
        )
        for row in cur.fetchall():
            server_id, event_type, severity, summary, diff_json, detected_at = row
            rec = {"server_id": server_id, "event_type": event_type, "severity": severity, "summary": summary, "detected_at": detected_at.isoformat() if hasattr(detected_at, "isoformat") else str(detected_at)}
            if diff_json:
                rec["diff"] = diff_json if isinstance(diff_json, dict) else (json.loads(diff_json) if isinstance(diff_json, str) else {})
            else:
                rec["diff"] = {}
            notable.append(rec)
            if event_type == "ScoreChanged" and isinstance(rec.get("diff"), dict):
                delta = (rec["diff"].get("trust_score_new") or 0) - (rec["diff"].get("trust_score_old") or 0)
                entry = {"server_id": server_id, "delta": delta, "summary": summary, **rec["diff"]}
                if delta > 0:
                    movers.append(entry)
                elif delta < 0:
                    downgrades.append(entry)
    movers.sort(key=lambda x: -(x.get("delta") or 0))
    downgrades.sort(key=lambda x: x.get("delta") or 0)
    return {"movers": movers[:20], "downgrades": downgrades[:20], "notableDrift": notable[:30]}


def _new_entrants(conn, brief_date: date) -> List[Dict[str, Any]]:
    """
    Servers whose first score_snapshot was assessed on brief_date.
    Deduplicates by server_id to avoid multiple entries for the same server.
    """
    start = datetime(brief_date.year, brief_date.month, brief_date.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT ON (ss.server_id)
                ss.server_id, ss.trust_score, ss.tier, ss.assessed_at
            FROM score_snapshots ss
            WHERE ss.assessed_at >= %s AND ss.assessed_at < %s
            AND NOT EXISTS (
                SELECT 1 FROM score_snapshots ss2
                WHERE ss2.server_id = ss.server_id AND ss2.assessed_at < %s
            )
            ORDER BY ss.server_id, ss.assessed_at ASC
            """,
            (start, end, start),
        )
        results = cur.fetchall()
        # Additional deduplication by server_id (in case DISTINCT ON doesn't work as expected)
        seen_server_ids = set()
        deduplicated = []
        for r in results:
            server_id = r[0]
            if server_id not in seen_server_ids:
                seen_server_ids.add(server_id)
                deduplicated.append({
                    "server_id": server_id,
                    "trust_score": float(r[1]),
                    "tier": r[2],
                    "assessed_at": r[3].isoformat() if hasattr(r[3], "isoformat") else str(r[3])
                })
        return deduplicated


def _build_highlights(movers: List, downgrades: List, new_entrants: List, notable: List) -> List[str]:
    highlights: List[str] = []
    if movers:
        highlights.append(f"{len(movers)} server(s) improved in trust score.")
    if downgrades:
        highlights.append(f"{len(downgrades)} server(s) declined.")
    if new_entrants:
        highlights.append(f"{len(new_entrants)} new server(s) assessed.")
    if notable:
        crit = sum(1 for n in notable if n.get("severity") == "Critical")
        if crit:
            highlights.append(f"{crit} critical drift event(s).")
    if not highlights:
        highlights.append("No notable score or drift activity for this period.")
    return highlights


def _render_narrative_short(
    brief_date: date,
    movers: List,
    downgrades: List,
    new_entrants: List,
    notable: List,
    highlights: List[str],
) -> str:
    template = _load_template()
    n_movers, n_down, n_new = len(movers), len(downgrades), len(new_entrants)
    movers_phrase = f"{n_movers} server(s) improved." if n_movers else "No movers."
    downgrades_phrase = f"{n_down} declined." if n_down else "No downgrades."
    drift_phrase = f"{len(notable)} drift event(s)." if notable else "No drift events."
    highlights_list = "\n".join(f"- {h}" for h in highlights)
    out = template.format(
        date=brief_date.isoformat(),
        movers_phrase=movers_phrase,
        downgrades_phrase=downgrades_phrase,
        drift_phrase=drift_phrase,
        highlights_list=highlights_list,
    )
    return out[:600] if len(out) > 600 else out


def _render_narrative_long(
    brief_date: date,
    movers: List,
    downgrades: List,
    new_entrants: List,
    notable: List,
    highlights: List[str],
) -> str:
    # Placeholder / extended version; can be replaced by LLM-generated content later.
    short = _render_narrative_short(brief_date, movers, downgrades, new_entrants, notable, highlights)
    extra = []
    if movers:
        extra.append("Top movers (by score delta): " + ", ".join(f"{m.get('server_id', '')} (+{m.get('delta', 0):.1f})" for m in movers[:5]))
    if downgrades:
        extra.append("Top downgrades: " + ", ".join(f"{d.get('server_id', '')} ({d.get('delta', 0):.1f})" for d in downgrades[:5]))
    if extra:
        return short + "\n\n" + "\n".join(extra)
    return short


def run_daily_brief(brief_date: Optional[date] = None) -> Dict[str, Any]:
    brief_date = brief_date or date.today()
    conn = psycopg2.connect(DATABASE_URL)
    now = datetime.now(timezone.utc)
    try:
        drift_data = _gather_from_drift(conn, brief_date)
        new_entrants = _new_entrants(conn, brief_date)
        movers = drift_data["movers"]
        downgrades = drift_data["downgrades"]
        notable = drift_data["notableDrift"]
        highlights = _build_highlights(movers, downgrades, new_entrants, notable)
        headline = f"MCP Trust Radar — {brief_date.isoformat()}"
        narrative_short = _render_narrative_short(brief_date, movers, downgrades, new_entrants, notable, highlights)
        narrative_long = _render_narrative_long(brief_date, movers, downgrades, new_entrants, notable, highlights)
        payload = {
            "date": brief_date.isoformat(),
            "headline": headline,
            "narrativeShort": narrative_short,
            "narrativeLong": narrative_long,
            "highlights": highlights,
            "movers": movers,
            "downgrades": downgrades,
            "newEntrants": new_entrants,
            "notableDrift": notable,
            "tipOfTheDay": None,
            "methodologyVersion": METHODOLOGY_VERSION,
            "generatedAt": now.isoformat(),
        }
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO daily_briefs (date, headline, narrative_long, narrative_short, highlights, payload_json, methodology_version, generated_at, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    headline = EXCLUDED.headline,
                    narrative_long = EXCLUDED.narrative_long,
                    narrative_short = EXCLUDED.narrative_short,
                    highlights = EXCLUDED.highlights,
                    payload_json = EXCLUDED.payload_json,
                    methodology_version = EXCLUDED.methodology_version,
                    generated_at = EXCLUDED.generated_at
                """,
                (brief_date, headline, narrative_long, narrative_short, json.dumps(highlights), json.dumps(payload), METHODOLOGY_VERSION, now, now),
            )
        conn.commit()
        return {
            "success": True,
            "date": brief_date.isoformat(),
            "headline": headline,
            "highlightsCount": len(highlights),
            "moversCount": len(movers),
            "downgradesCount": len(downgrades),
            "newEntrantsCount": len(new_entrants),
            "completedAt": now.isoformat(),
        }
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "date": brief_date.isoformat() if brief_date else None,
            "error": str(e),
            "completedAt": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    d = None
    if len(sys.argv) > 1:
        from datetime import datetime as dt
        d = dt.strptime(sys.argv[1], "%Y-%m-%d").date()
    result = run_daily_brief(d)
    print(json.dumps(result, indent=2))
