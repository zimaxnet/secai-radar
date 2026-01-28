#!/usr/bin/env python3
"""
Seed script for sample data: providers, mcp_servers, score_snapshots.
Run refresh_latest_scores.py after seeding (or re-run seed with --refresh).
"""

import os
import sys
import subprocess
import psycopg2
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random

_SCRIPT_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)

# Domains used for providers; seed resolves provider_id from DB after upsert
PROVIDER_DOMAINS = [
    ("Anthropic", "anthropic.com", "Vendor"),
    ("OpenAI", "openai.com", "Vendor"),
    ("Google", "google.com", "Vendor"),
    ("Microsoft", "microsoft.com", "Vendor"),
    ("GitHub", "github.com", "Vendor"),
]
METHODOLOGY_VERSION = "2024.1"


def generate_id() -> str:
    """Generate a 16-character hex ID"""
    return format(random.randint(0, 16**16 - 1), "016x")


def seed_providers(cur) -> dict:
    """Insert sample providers; idempotent on primary_domain. Returns domain -> provider_id."""
    for name, domain, ptype in PROVIDER_DOMAINS:
        pid = generate_id()
        cur.execute("""
            INSERT INTO providers (provider_id, provider_name, primary_domain, provider_type)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (primary_domain) DO NOTHING
        """, (pid, name, domain, ptype))
    cur.execute(
        "SELECT primary_domain, provider_id FROM providers WHERE primary_domain = ANY(%s)",
        ([d[1] for d in PROVIDER_DOMAINS],),
    )
    domain_to_id = {row[0]: row[1] for row in cur.fetchall()}
    print("  Providers upserted")
    return domain_to_id


def seed_servers(cur, domain_to_provider_id: dict) -> list:
    """Insert sample mcp_servers. Returns list of (server_id, server_slug)."""
    now = datetime.now(timezone.utc).isoformat()
    # server_id, server_slug, server_name, provider_id, category_primary, deployment_type, auth_model, tool_agency, status, first_seen_at, last_seen_at
    rows = [
        ("s100000000000001", "filesystem", "Filesystem", domain_to_provider_id.get("anthropic.com"), "Tools", "Local", "APIKey", "ReadWrite", "Active", now, now),
        ("s100000000000002", "github", "GitHub", domain_to_provider_id.get("microsoft.com"), "Tools", "Remote", "OAuthOIDC", "ReadWrite", "Active", now, now),
        ("s100000000000003", "slack", "Slack", domain_to_provider_id.get("google.com"), "Tools", "Remote", "OAuthOIDC", "ReadOnly", "Active", now, now),
        ("s100000000000004", "fetch", "Fetch", domain_to_provider_id.get("anthropic.com"), "Tools", "Remote", "APIKey", "ReadOnly", "Active", now, now),
    ]
    rows = [r for r in rows if r[3] is not None]  # skip if no provider for domain
    for row in rows:
        cur.execute("""
            INSERT INTO mcp_servers (
                server_id, server_slug, server_name, provider_id, category_primary,
                deployment_type, auth_model, tool_agency, status, first_seen_at, last_seen_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::timestamptz, %s::timestamptz)
            ON CONFLICT (server_id) DO NOTHING
        """, row)
    print(f"  MCP servers upserted ({len(rows)})")
    return [(r[0], r[1]) for r in rows]


def seed_score_snapshots(cur, server_ids: list) -> None:
    """Insert one score_snapshot per server with valid schema."""
    # score_id, server_id, methodology_version, assessed_at, d1..d6, trust_score, tier, enterprise_fit, evidence_confidence, fail_fast_flags, risk_flags, explainability_json, created_at
    explain = '{"methodology_version": "' + METHODOLOGY_VERSION + '", "summary": "Seed snapshot"}'
    now = datetime.now(timezone.utc)
    # Vary tier/score for ranking variety
    configs = [
        (85.5, "A", "Regulated", 2),
        (72.0, "B", "Standard", 2),
        (58.0, "C", "Standard", 1),
        (91.0, "A", "Regulated", 3),
    ]
    for i, (server_id, _) in enumerate(server_ids):
        ts, tier, fit, conf = configs[i % len(configs)]
        score_id = ("sc" + server_id[2:].zfill(14))[:16]  # deterministic for idempotent seed
        assessed = (now - timedelta(hours=i * 6)).isoformat()
        cur.execute("""
            INSERT INTO score_snapshots (
                score_id, server_id, methodology_version, assessed_at,
                d1, d2, d3, d4, d5, d6, trust_score, tier, enterprise_fit, evidence_confidence,
                fail_fast_flags, risk_flags, explainability_json, created_at
            )
            VALUES (%s, %s, %s, %s::timestamptz, 4, 4, 4, 4, 4, 4, %s, %s, %s, %s, '[]'::jsonb, '[]'::jsonb, %s::jsonb, %s::timestamptz)
            ON CONFLICT (score_id) DO NOTHING
        """, (score_id, server_id, METHODOLOGY_VERSION, assessed, ts, tier, fit, conf, explain, now.isoformat()))
    print(f"  Score snapshots inserted ({len(server_ids)})")


# Demo tenant/user for Phase 3 Private Registry (T-091)
DEMO_WORKSPACE_ID = "ws-demo-00000001"
DEMO_TENANT_ID = "demo-tenant-001"
DEMO_USER_ID = "demo-admin-user"


def seed_workspaces_and_members(cur) -> None:
    """Insert one demo workspace + admin user for registry (T-091). Idempotent."""
    cur.execute("""
        INSERT INTO workspaces (workspace_id, tenant_id, name, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON CONFLICT (workspace_id) DO NOTHING
    """, (DEMO_WORKSPACE_ID, DEMO_TENANT_ID, "Demo Registry",))
    cur.execute("""
        INSERT INTO workspace_members (workspace_id, user_id, role, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON CONFLICT (workspace_id, user_id) DO NOTHING
    """, (DEMO_WORKSPACE_ID, DEMO_USER_ID, "RegistryAdmin",))
    print("  Workspace + admin member upserted (demo)")


def seed_data(do_refresh: bool = False) -> None:
    """Insert sample data. If do_refresh, run latest_scores + mat view refresh after."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            domain_to_id = seed_providers(cur)
            servers = seed_servers(cur, domain_to_id)
            seed_score_snapshots(cur, servers)
            try:
                seed_workspaces_and_members(cur)
            except psycopg2.Error:
                pass  # workspaces/workspace_members absent if 004 not applied
            conn.commit()
        if do_refresh:
            r = subprocess.run(
                [sys.executable, str(_SCRIPT_DIR / "refresh_latest_scores.py")],
                env=os.environ.copy(),
                capture_output=True,
                text=True,
                cwd=str(_SCRIPT_DIR),
            )
            if r.returncode != 0:
                print(r.stderr or r.stdout or "refresh_latest_scores failed", file=sys.stderr)
                raise RuntimeError("refresh_latest_scores.py failed")
            print("  Ran refresh_latest_scores.py")
        print("✅ Seed data inserted")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding data: {e}", file=sys.stderr)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    do_refresh = "--refresh" in sys.argv
    seed_data(do_refresh=do_refresh)
