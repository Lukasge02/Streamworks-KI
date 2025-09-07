#!/usr/bin/env python3
"""
PDF Processing Monitor
Tracks file deletion during upload processing to identify exact moment PDFs disappear
"""

import time
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
import subprocess
import sys
import json

class PDFProcessingMonitor:
    def __init__(self, storage_root="storage/documents"):
        self.storage_root = Path(storage_root)
        self.monitoring = False
        self.log_file = Path("pdf_monitor.log")
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
    
    def get_hash_path(self, filename):
        """Calculate expected storage path based on filename hash"""
        file_hash = hashlib.sha256(filename.encode()).hexdigest()[:8]
        return self.storage_root / f"{file_hash[:2]}/{file_hash[2:4]}/{file_hash}_{filename}"
    
    def start_monitoring(self, expected_filename):
        """Start monitoring for file existence"""
        expected_path = self.get_hash_path(expected_filename)
        self.log(f"🔍 Starting monitor for: {expected_filename}")
        self.log(f"   Expected path: {expected_path}")
        
        self.monitoring = True
        last_exists = None
        
        while self.monitoring:
            try:
                exists = expected_path.exists()
                
                # Log state changes
                if exists != last_exists:
                    if exists:
                        size = expected_path.stat().st_size if exists else 0
                        self.log(f"✅ FILE APPEARED: {expected_path} ({size} bytes)")
                    else:
                        self.log(f"❌ FILE DISAPPEARED: {expected_path}")
                
                # Log periodic status
                elif exists:
                    size = expected_path.stat().st_size
                    self.log(f"📁 File exists: {size} bytes")
                else:
                    self.log("⏳ File not yet created...")
                    
                last_exists = exists
                time.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                self.log("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.log(f"❌ Monitor error: {str(e)}")
                break
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        self.log("🏁 Monitoring stopped")
    
    def analyze_storage(self):
        """Analyze current storage state"""
        self.log("📊 STORAGE ANALYSIS:")
        
        if not self.storage_root.exists():
            self.log("   ❌ Storage directory does not exist")
            return
        
        pdf_count = 0
        png_count = 0
        other_count = 0
        
        for file_path in self.storage_root.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                size = file_path.stat().st_size
                
                if suffix == '.pdf':
                    pdf_count += 1
                    self.log(f"   📄 PDF: {file_path.name} ({size} bytes)")
                elif suffix == '.png':
                    png_count += 1  
                    self.log(f"   🖼️  PNG: {file_path.name} ({size} bytes)")
                else:
                    other_count += 1
                    self.log(f"   📎 OTHER: {file_path.name} ({size} bytes)")
        
        self.log(f"   📈 SUMMARY: {pdf_count} PDFs, {png_count} PNGs, {other_count} others")
    
    async def upload_test_file(self, file_path):
        """Upload test file via curl to backend"""
        self.log(f"🚀 Uploading test file: {file_path}")
        
        try:
            # Use curl to upload file
            cmd = [
                'curl', '-X', 'POST',
                'http://localhost:8000/api/v1/documents/upload',
                '-F', f'file=@{file_path}',
                '-F', 'folder_id=', # Default folder
                '-v'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            self.log(f"📤 Upload response status: {result.returncode}")
            if result.stdout:
                self.log(f"📤 Upload response: {result.stdout[:200]}...")
            if result.stderr:
                self.log(f"⚠️  Upload stderr: {result.stderr[:200]}...")
                
            return result.returncode == 0
            
        except Exception as e:
            self.log(f"❌ Upload failed: {str(e)}")
            return False

async def main():
    if len(sys.argv) < 2:
        print("Usage: python monitor_pdf_processing.py <command>")
        print("Commands:")
        print("  monitor <filename>  - Monitor processing of uploaded file")
        print("  analyze            - Analyze current storage state")
        print("  upload <filepath>  - Upload and monitor test file")
        return
    
    monitor = PDFProcessingMonitor()
    command = sys.argv[1]
    
    if command == "monitor" and len(sys.argv) >= 3:
        filename = sys.argv[2]
        monitor.start_monitoring(filename)
        
    elif command == "analyze":
        monitor.analyze_storage()
        
    elif command == "upload" and len(sys.argv) >= 3:
        file_path = Path(sys.argv[2])
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
            
        filename = file_path.name
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(
            asyncio.get_event_loop().run_in_executor(
                None, monitor.start_monitoring, filename
            )
        )
        
        # Wait a moment then upload
        await asyncio.sleep(2)
        success = await monitor.upload_test_file(file_path)
        
        if success:
            monitor.log("✅ Upload initiated successfully")
            # Monitor for 30 more seconds
            await asyncio.sleep(30)
        else:
            monitor.log("❌ Upload failed")
        
        monitor.stop_monitoring()
        await monitor_task
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    asyncio.run(main())