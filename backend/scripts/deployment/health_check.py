#!/usr/bin/env python3
"""
System Health Validation Script
Performs comprehensive health checks for production deployment
"""
import os
import sys
import logging
import asyncio
import requests
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HealthChecker:
    """System health validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API health endpoint"""
        try:
            logger.info("🔍 Checking API health...")
            
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info("✅ API health check passed")
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "data": health_data
                }
            else:
                logger.error(f"❌ API health check failed: {response.status_code}")
                return {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response_time": response.elapsed.total_seconds()
                }
                
        except Exception as e:
            logger.error(f"❌ API health check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity via API"""
        try:
            logger.info("🔍 Checking database connectivity...")
            
            response = self.session.get(f"{self.base_url}/api/v1/system/health")
            
            if response.status_code == 200:
                health_data = response.json()
                db_status = health_data.get("database", {}).get("status")
                
                if db_status == "healthy":
                    logger.info("✅ Database connectivity check passed")
                    return {
                        "status": "healthy",
                        "data": health_data.get("database", {})
                    }
                else:
                    logger.error(f"❌ Database unhealthy: {db_status}")
                    return {
                        "status": "unhealthy",
                        "error": f"Database status: {db_status}"
                    }
            else:
                logger.error(f"❌ Database check failed: {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Database connectivity check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_qa_functionality(self) -> Dict[str, Any]:
        """Test Q&A system functionality"""
        try:
            logger.info("🔍 Testing Q&A functionality...")
            
            test_question = "Was ist StreamWorks?"
            
            response = self.session.post(
                f"{self.base_url}/api/v1/qa/ask",
                json={"question": test_question}
            )
            
            if response.status_code == 200:
                qa_response = response.json()
                
                if qa_response.get("answer") and len(qa_response["answer"]) > 10:
                    logger.info("✅ Q&A functionality check passed")
                    return {
                        "status": "healthy",
                        "response_time": response.elapsed.total_seconds(),
                        "answer_length": len(qa_response["answer"])
                    }
                else:
                    logger.error("❌ Q&A returned empty or invalid answer")
                    return {
                        "status": "unhealthy",
                        "error": "Empty or invalid answer"
                    }
            else:
                logger.error(f"❌ Q&A check failed: {response.status_code}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Q&A functionality check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def check_file_upload(self) -> Dict[str, Any]:
        """Test file upload functionality"""
        try:
            logger.info("🔍 Testing file upload functionality...")
            
            # Create a small test file
            test_content = "Test document for health check"
            
            files = {
                'file': ('test_health_check.txt', test_content, 'text/plain')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/files/upload",
                files=files,
                data={'category_id': '1', 'folder_id': '1'}
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ File upload functionality check passed")
                return {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                logger.warning(f"⚠️ File upload check returned: {response.status_code}")
                return {
                    "status": "warning",
                    "error": f"HTTP {response.status_code}",
                    "note": "May be expected if categories/folders not configured"
                }
                
        except Exception as e:
            logger.error(f"❌ File upload functionality check failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("🚀 Starting comprehensive health check...")
        
        start_time = time.time()
        
        checks = {
            "api_health": self.check_api_health(),
            "database": self.check_database_connectivity(),
            "qa_system": self.check_qa_functionality(),
            "file_upload": self.check_file_upload()
        }
        
        # Calculate overall status
        statuses = [check["status"] for check in checks.values()]
        
        if all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        elif any(status == "error" for status in statuses):
            overall_status = "error"
        else:
            overall_status = "warning"
        
        total_time = time.time() - start_time
        
        result = {
            "overall_status": overall_status,
            "checks": checks,
            "total_check_time": total_time,
            "timestamp": time.time()
        }
        
        logger.info(f"🏁 Health check completed - Status: {overall_status}")
        return result


def main():
    """Main health check interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Check for StreamWorks-KI')
    parser.add_argument('--url', type=str, default='http://localhost:8000',
                       help='Base URL for health checks')
    parser.add_argument('--output', type=str,
                       help='Output file for health check results (JSON)')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Timeout for individual checks in seconds')
    
    args = parser.parse_args()
    
    checker = HealthChecker(args.url)
    checker.session.timeout = args.timeout
    
    try:
        results = checker.run_comprehensive_check()
        
        # Print summary
        print(f"\n🏥 Health Check Results:")
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Total Check Time: {results['total_check_time']:.2f}s")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results['timestamp']))}")
        
        print(f"\n📋 Individual Checks:")
        for check_name, check_result in results['checks'].items():
            status = check_result['status']
            emoji = "✅" if status == "healthy" else "⚠️" if status == "warning" else "❌"
            print(f"{emoji} {check_name}: {status}")
            
            if 'error' in check_result:
                print(f"    Error: {check_result['error']}")
            if 'response_time' in check_result:
                print(f"    Response Time: {check_result['response_time']:.3f}s")
        
        # Save to file if requested
        if args.output:
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {args.output}")
        
        # Exit with appropriate code
        if results['overall_status'] == 'error':
            sys.exit(1)
        elif results['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()