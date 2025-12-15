import sys
import os
from pathlib import Path

# Fix path to include backend root
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from services.db import db


def verify():
    print("🔍 Verifying Database Connection (Supabase)...")

    if not db.client:
        print("❌ DB Client not initialized. Check .env")
        return

    try:
        # Check connection by querying a table
        print("   Checking 'sessions' table access...")
        res = db.client.table("sessions").select("id").limit(1).execute()
        print(
            f"   ✅ Connection successful. Data retrieved: {len(res.data)} rows (limit 1)"
        )

        print("   Checking 'projects' table access...")
        res = db.client.table("projects").select("id").limit(1).execute()
        print(
            f"   ✅ Connection successful. Data retrieved: {len(res.data)} rows (limit 1)"
        )

    except Exception as e:
        print(f"❌ Database check failed: {e}")


if __name__ == "__main__":
    verify()
