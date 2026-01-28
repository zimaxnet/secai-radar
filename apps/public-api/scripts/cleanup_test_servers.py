#!/usr/bin/env python3
"""
Cleanup Test Servers Script

Marks test servers (server_id LIKE 's10000000000000%') as 'Deprecated'
and removes them from latest_scores_staging and latest_scores tables.
"""

import os
import subprocess
import sys

import psycopg2

# Get database URL from Azure Key Vault or environment
def get_database_url():
    """Get DATABASE_URL from Azure Key Vault or environment variable."""
    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"]
    
    # Try Azure Key Vault
    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", "secai-radar-kv", 
             "--name", "database-url", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: DATABASE_URL not found in environment and Azure CLI not available.")
        print("Please set DATABASE_URL environment variable or ensure Azure CLI is installed and configured.")
        sys.exit(1)


def cleanup_test_servers():
    """Mark test servers as Deprecated and remove from staging/stable tables."""
    database_url = get_database_url()
    conn = psycopg2.connect(database_url)
    
    try:
        with conn.cursor() as cur:
            # Count test servers before cleanup
            cur.execute("""
                SELECT COUNT(*) FROM mcp_servers 
                WHERE server_id LIKE 's10000000000000%'
            """)
            test_server_count = cur.fetchone()[0]
            print(f"Found {test_server_count} test servers to clean up")
            
            if test_server_count == 0:
                print("No test servers found. Nothing to clean up.")
                return
            
            # Show which servers will be affected
            cur.execute("""
                SELECT server_id, server_name, status 
                FROM mcp_servers 
                WHERE server_id LIKE 's10000000000000%'
                ORDER BY server_id
            """)
            test_servers = cur.fetchall()
            print("\nTest servers to deprecate:")
            for server_id, server_name, status in test_servers:
                print(f"  - {server_id}: {server_name} (current status: {status})")
            
            # Mark test servers as Deprecated
            cur.execute("""
                UPDATE mcp_servers 
                SET status = 'Deprecated',
                    updated_at = NOW()
                WHERE server_id LIKE 's10000000000000%'
            """)
            deprecated_count = cur.rowcount
            print(f"\nMarked {deprecated_count} test servers as 'Deprecated'")
            
            # Remove from latest_scores_staging
            cur.execute("""
                DELETE FROM latest_scores_staging 
                WHERE server_id LIKE 's10000000000000%'
            """)
            staging_removed = cur.rowcount
            print(f"Removed {staging_removed} test servers from latest_scores_staging")
            
            # Remove from latest_scores (stable)
            cur.execute("""
                DELETE FROM latest_scores 
                WHERE server_id LIKE 's10000000000000%'
            """)
            stable_removed = cur.rowcount
            print(f"Removed {stable_removed} test servers from latest_scores (stable)")
            
            # Commit changes
            conn.commit()
            print("\nCleanup completed successfully!")
            
            # Verify cleanup
            cur.execute("""
                SELECT COUNT(*) FROM mcp_servers 
                WHERE server_id LIKE 's10000000000000%' AND status = 'Active'
            """)
            remaining_active = cur.fetchone()[0]
            if remaining_active > 0:
                print(f"WARNING: {remaining_active} test servers still marked as Active")
            else:
                print("All test servers successfully deprecated")
                
    except Exception as e:
        conn.rollback()
        print(f"Error during cleanup: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    cleanup_test_servers()
