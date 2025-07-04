#!/usr/bin/env python3
"""
Test das Upload-System direkt
"""

import requests
import json
from pathlib import Path

def test_upload_api():
    """Teste das Upload API direkt"""
    
    print("🧪 Testing Upload API")
    print("=" * 50)
    
    # Create test file
    test_content = """STREAMWORKS TEST FAQ

F: Was ist ein Batch-Job?
A: Ein Batch-Job ist ein automatisierter Verarbeitungsauftrag.

Wichtig: Regelmäßige Backups durchführen!
"""
    
    test_file = Path("test_upload_file.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 Created test file: {test_file}")
    
    try:
        # Test upload
        url = "http://localhost:8000/api/v1/training/upload"
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'text/plain')}
            data = {'category': 'help_data'}
            
            print(f"📤 Uploading to {url}")
            response = requests.post(url, files=files, data=data)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Upload failed!")
            print(f"📄 Response: {response.text}")
        
        # Test list files
        print("\n" + "="*30)
        print("📋 Testing file list...")
        
        list_response = requests.get("http://localhost:8000/api/v1/training/files")
        print(f"📊 List Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            files_list = list_response.json()
            print(f"📁 Found {len(files_list)} files")
            for file_info in files_list:
                print(f"  - {file_info.get('filename')} ({file_info.get('status')})")
        else:
            print(f"❌ List failed: {list_response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the backend running on port 8000?")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        print(f"🧹 Cleaned up test file")

if __name__ == "__main__":
    test_upload_api()