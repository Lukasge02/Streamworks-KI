
import sys
import os
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.db import db

def seed_dropdowns():
    print("Seeding Dropdown Options...")
    
    # Define options
    options = [
        # Agents
        {"category": "agent", "label": "UC4_Agent_Unix_01", "value": "UC4_UNIX_01"},
        {"category": "agent", "label": "UC4_Agent_Windows_01", "value": "UC4_WIN_01"},
        {"category": "agent", "label": "SAP_Agent_P01", "value": "SAP_P01"},
        {"category": "agent", "label": "FileTransfer_Gateway_01", "value": "FT_GW_01"},
        {"category": "agent", "label": "Database_Agent_ORA", "value": "DB_ORA_01"},
        
        # Calendars
        {"category": "calendar", "label": "Every Day", "value": "EVERY_DAY"},
        {"category": "calendar", "label": "Working Days (Mo-Fr)", "value": "WORKDAYS"},
        {"category": "calendar", "label": "Weekends", "value": "WEEKENDS"},
        {"category": "calendar", "label": "First Working Day of Month", "value": "1ST_WORKDAY_MONTH"},
        {"category": "calendar", "label": "Last Working Day of Month", "value": "LAST_WORKDAY_MONTH"},
        
        # Script / Job Types (Optional if dynamic)
        {"category": "script_type", "label": "Bash Script", "value": "BASH"},
        {"category": "script_type", "label": "PowerShell", "value": "POWERSHELL"},
        {"category": "script_type", "label": "Python", "value": "PYTHON"},
    ]
    
    count = 0
    errors = 0
    
    for opt in options:
        try:
            # Check if exists to avoid duplicates (naive check)
            # For simplicity, we just insert. Unique constraint could be added to DB but MVP is fine.
            # Ideally we'd upsert based on category+value.
            
            # Using upsert requires a unique constraint or primary key. 
            # We don't have a unique constraint on (category, value) yet in the migration.
            # So we check first.
            
            existing = db.client.table("dropdown_options")\
                .select("id")\
                .eq("category", opt["category"])\
                .eq("value", opt["value"])\
                .execute()
                
            if existing.data:
                print(f"Skipping existing: {opt['category']} - {opt['value']}")
                continue
                
            db.client.table("dropdown_options").insert(opt).execute()
            print(f"Inserted: {opt['category']} - {opt['value']}")
            count += 1
        except Exception as e:
            print(f"Error inserting {opt}: {e}")
            errors += 1
            
    print(f"\nSeeding complete. Inserted: {count}, Errors: {errors}")

if __name__ == "__main__":
    if not db.client:
        print("❌ DB Client not initialized. Check .env")
        sys.exit(1)
    
    seed_dropdowns()
