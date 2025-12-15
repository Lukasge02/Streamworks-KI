import requests
import sys

BASE_URL = "http://localhost:8000"


def log(msg, success=True):
    icon = "✅" if success else "❌"
    print(f"{icon} {msg}")


def test_health():
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            log("Health Check Passed")
            return True
        else:
            log(f"Health Check Failed: {r.status_code}", False)
            return False
    except Exception as e:
        log(f"Health Check Exception: {e}", False)
        return False


def test_documents_list():
    try:
        r = requests.get(f"{BASE_URL}/api/documents/list")
        if r.status_code == 200:
            data = r.json()
            count = len(data)
            log(f"Documents List Passed (Found {count} docs)")
            return True
        else:
            log(f"Documents List Failed: {r.status_code}", False)
            return False
    except Exception as e:
        log(f"Documents List Exception: {e}", False)
        return False


def test_categories():
    try:
        r = requests.get(f"{BASE_URL}/api/documents/categories/counts")
        if r.status_code == 200:
            log("Categories Counts Passed")
            return True
        else:
            log(f"Categories Counts Failed: {r.status_code}", False)
            return False
    except Exception as e:
        log(f"Categories Exception: {e}", False)
        return False


def test_access_endpoint():
    try:
        # Just check if /accessible returns 200
        r = requests.get(f"{BASE_URL}/api/documents/accessible")
        if r.status_code == 200:
            log("Access Endpoint Passed")
            return True
        else:
            log(f"Access Endpoint Failed: {r.status_code}", False)
            return False
    except Exception as e:
        log(f"Access Endpoint Exception: {e}", False)
        return False


def main():
    print(f"Testing Live System at {BASE_URL}...")
    results = [
        test_health(),
        test_documents_list(),
        test_categories(),
        test_access_endpoint(),
    ]

    if all(results):
        print("\n🎉 ALL LIVE SYSTEMS OPERATIONAL")
        sys.exit(0)
    else:
        print("\n⚠️ SOME CHECKS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
