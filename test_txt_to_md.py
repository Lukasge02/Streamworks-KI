#!/usr/bin/env python3
"""
Test-Skript für TXT zu MD Konverter
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.txt_to_md_converter import txt_to_md_converter

async def test_txt_to_md_converter():
    """Teste den TXT zu MD Konverter"""
    
    print("🧪 Testing TXT zu MD Converter")
    print("=" * 50)
    
    # Create test TXT file
    test_content = """STREAMWORKS FAQ

1. Was ist Batch-Verarbeitung?
Batch-Verarbeitung ist die Ausführung von Jobs in Stapeln ohne Benutzerinteraktion.

F: Wie funktioniert Error-Handling?
A: Bei Fehlern stoppt der Job und erhält Error-Status. Optional kann Retry konfiguriert werden.

WICHTIG: Schedule-Konfiguration
- Täglich um 2 Uhr: 0 2 * * *
- Stündlich: 0 * * * *

API Endpoints:
- GET /api/jobs - List all jobs
- POST /api/jobs - Create new job
- DELETE /api/jobs/{id} - Delete job

XML Konfiguration:
<?xml version="1.0" encoding="UTF-8"?>
<stream>
    <job id="daily_backup">
        <schedule>0 2 * * *</schedule>
        <script>backup.ps1</script>
    </job>
</stream>

Tipps für bessere Performance:
- Verwende kleine Batch-Größen
- Aktiviere Monitoring
- Regelmäßige Backups"""

    # Write test file
    test_file = Path("test_streamworks_faq.txt")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"📝 Created test file: {test_file}")
    
    try:
        # Convert to MD
        print("🔄 Converting TXT to MD...")
        md_file = await txt_to_md_converter.convert_txt_to_md(test_file)
        
        print(f"✅ Conversion successful!")
        print(f"📄 Original: {test_file}")
        print(f"📝 Optimized: {md_file}")
        
        # Read and display MD content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        print("\n" + "="*50)
        print("📋 OPTIMIZED MARKDOWN CONTENT:")
        print("="*50)
        print(md_content)
        
        # Cleanup
        test_file.unlink()
        md_file.unlink()
        print(f"\n🧹 Cleaned up test files")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        # Cleanup on error
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    asyncio.run(test_txt_to_md_converter())