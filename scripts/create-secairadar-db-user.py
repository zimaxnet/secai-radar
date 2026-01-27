#!/usr/bin/env python3
"""
Create a dedicated PostgreSQL user for the secairadar database on ctxeco-db.
Uses admin connection (ctxecoadmin). Idempotent: safe to re-run.

Requires: ADMIN_DATABASE_URL or DATABASE_URL (postgresql://ctxecoadmin:<pass>@ctxeco-db.../secairadar)
Optional: SECAIRADAR_APP_PASSWORD — if unset, a password is generated and printed (store in KV).

Output: connection string for the new user, to use as DATABASE_URL and store in Key Vault.
"""

import os
import secrets
import string
import sys

try:
    import psycopg2
except ImportError:
    print("Install psycopg2: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)

APP_USER = "secairadar_app"
APP_DB = "secairadar"

def main() -> None:
    admin_url = os.getenv("ADMIN_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not admin_url:
        print(
            "Set ADMIN_DATABASE_URL or DATABASE_URL (ctxecoadmin connection to secairadar).\n"
            "Example: postgresql://ctxecoadmin:<PASSWORD>@ctxeco-db.postgres.database.azure.com:5432/secairadar",
            file=sys.stderr,
        )
        sys.exit(1)

    password = os.getenv("SECAIRADAR_APP_PASSWORD")
    if not password:
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for _ in range(24))
        print(f"Generated password for {APP_USER} (store in Key Vault):", file=sys.stderr)
        print(password, file=sys.stderr)

    conn = psycopg2.connect(admin_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Create user (idempotent: alter password if exists)
            cur.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s",
                (APP_USER,),
            )
            if cur.fetchone():
                cur.execute("ALTER USER secairadar_app WITH PASSWORD %s", (password,))
                print(f"Updated password for existing user {APP_USER}.", file=sys.stderr)
            else:
                cur.execute(
                    "CREATE USER secairadar_app WITH PASSWORD %s",
                    (password,),
                )
                print(f"Created user {APP_USER}.", file=sys.stderr)

            # Grants (admin_url must target database secairadar)
            cur.execute("GRANT CONNECT ON DATABASE secairadar TO secairadar_app")
            cur.execute("GRANT USAGE ON SCHEMA public TO secairadar_app")
            cur.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO secairadar_app")
            cur.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO secairadar_app")
            cur.execute("GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO secairadar_app")
            cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO secairadar_app")
            cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO secairadar_app")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

    # Build app connection string (same host/db as admin URL, different user)
    from urllib.parse import urlparse, urlunparse
    p = urlparse(admin_url)
    host = p.hostname or "localhost"
    port = p.port or 5432
    path = p.path or f"/{APP_DB}"
    safe = password.replace("%", "%25").replace("@", "%40")
    netloc = f"{APP_USER}:{safe}@{host}:{port}"
    app_url = urlunparse((p.scheme, netloc, path, "", "", ""))
    print("\nUse this as DATABASE_URL and store in Key Vault (database-url):")
    print(app_url)

if __name__ == "__main__":
    main()
