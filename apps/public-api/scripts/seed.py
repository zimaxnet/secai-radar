#!/usr/bin/env python3
"""
Seed script for sample data
"""

import os
import psycopg2
from datetime import datetime, timedelta
import random

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://secairadar:password@localhost:5432/secairadar"
)


def generate_id() -> str:
    """Generate a 16-character hex ID"""
    return format(random.randint(0, 16**16-1), '016x')


def seed_data():
    """Insert sample data"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            # Insert sample providers
            providers = [
                ("Anthropic", "anthropic.com", "Vendor"),
                ("OpenAI", "openai.com", "Vendor"),
                ("Google", "google.com", "Vendor"),
                ("Microsoft", "microsoft.com", "Vendor"),
            ]
            
            for name, domain, ptype in providers:
                provider_id = generate_id()
                cur.execute("""
                    INSERT INTO providers (provider_id, provider_name, primary_domain, provider_type)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (provider_id) DO NOTHING
                """, (provider_id, name, domain, ptype))
            
            # Insert sample servers
            # TODO: Add more realistic sample data
            
            conn.commit()
            print("✅ Seed data inserted")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed_data()
