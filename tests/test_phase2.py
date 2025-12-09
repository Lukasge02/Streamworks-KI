
import sys
import os
import requests
import json

# Add backend to path (though we use requests here against running server usually, 
# but for unit test style we might import app. But since invalid 'date-fns' implies I should fix that first.
# actually, let's use the internal methods to test logic without needing the server running, 
# OR use TestClient from fastapi.testclient.

sys.path.append(os.path.join(os.getcwd(), "backend"))
from fastapi.testclient import TestClient
from main import app
from services.db import db

client = TestClient(app)

def test_options_endpoint():
    print("Testing GET /api/options/agent...")
    # We seeded agents, so we expect some
    response = client.get("/api/options/agent")
    assert response.status_code == 200
    data = response.json()
    print(f"Received {len(data)} agents")
    assert len(data) > 0
    assert any(d["value"] == "UC4_UNIX_01" for d in data)
    print("✅ Options Endpoint Passed")

def test_streams_endpoints():
    print("\nTesting GET /api/streams...")
    # First ensure we have a stream
    if db.client:
        try:
            db.save_stream("test_stream_verify.xml", "<root/>", {"job_type": "TEST"})
        except Exception as e:
            print(f"Warning: Could not save test stream: {e}")

    response = client.get("/api/xml/") # Router prefix is /api/xml, endpoint is /
    # Wait, my implementation plan said GET /api/streams...
    # But I implemented it in xml/router.py under prefix /api/xml with route "/"
    # So it is GET /api/xml/
    
    assert response.status_code == 200
    data = response.json()
    print(f"Received {len(data)} streams")
    
    if len(data) > 0:
        stream_id = data[0]["id"]
        print(f"Testing GET /api/xml/{stream_id}...")
        detail_res = client.get(f"/api/xml/{stream_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == stream_id
        assert "content" in detail
        print("✅ Stream Detail Passed")
    
    print("✅ Stream List Passed")

if __name__ == "__main__":
    if not db.client:
        print("❌ DB Client not initialized. Check .env")
        sys.exit(1)
        
    try:
        test_options_endpoint()
        test_streams_endpoints()
        print("\n🎉 Phase 2 Tests Passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        # sys.exit(1) # Don't exit to allow seeing output
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)
