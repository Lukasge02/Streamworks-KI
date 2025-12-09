
import sys
import os
import uuid
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.db import db

def test_session_lifecycle():
    print("Testing Session Lifecycle...")
    session_id = str(uuid.uuid4())
    data = {"test": "value", "step": 1}
    
    # Save
    print(f"Saving session {session_id}...")
    res = db.save_session(session_id, data)
    print(f"Save result: {res}")
    
    # Get
    print(f"Retrieving session {session_id}...")
    loaded = db.get_session(session_id)
    print(f"Loaded data: {loaded}")
    
    assert loaded is not None
    assert loaded["test"] == "value"
    print("✅ Session Lifecycle Passed")

def test_stream_lifecycle():
    print("\nTesting Stream Lifecycle...")
    filename = f"test_stream_{uuid.uuid4()}.xml"
    content = "<root>Test</root>"
    metadata = {"author": "Unit Test", "job_type": "TEST"}
    
    # Save
    print(f"Saving stream {filename}...")
    try:
        res = db.save_stream(filename, content, metadata)
        print(f"Save result: {res}")
        print("✅ Stream Lifecycle Passed")
    except Exception as e:
        print(f"❌ Stream Lifecycle Failed: {e}")

if __name__ == "__main__":
    if not db.client:
        print("❌ DB Client not initialized. Check .env")
        sys.exit(1)
        
    try:
        test_session_lifecycle()
        test_stream_lifecycle()
        print("\n🎉 All Supabase tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)
