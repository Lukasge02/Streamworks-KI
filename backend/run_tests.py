#!/usr/bin/env python3
"""
Test runner script for StreamWorks-KI Backend
Provides convenient ways to run different test suites
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# Add backend root to Python path
BACKEND_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(BACKEND_ROOT))


def run_pytest(args, description):
    """Run pytest with given arguments"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    cmd = ["python3", "-m", "pytest"] + args
    
    try:
        result = subprocess.run(cmd, cwd=BACKEND_ROOT)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def run_unit_tests(args):
    """Run unit tests"""
    pytest_args = [
        "tests/unit/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html:reports/coverage/unit",
        "--html=reports/reports/unit.html",
        "--self-contained-html"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, "Running Unit Tests")


def run_integration_tests(args):
    """Run integration tests"""
    pytest_args = [
        "tests/integration/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html:reports/coverage/integration",
        "--html=reports/reports/integration.html",
        "--self-contained-html"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, "Running Integration Tests")


def run_performance_tests(args):
    """Run performance tests"""
    pytest_args = [
        "tests/performance/",
        "-v",
        "--tb=short",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-group-by=name"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, "Running Performance Tests")


def run_e2e_tests(args):
    """Run end-to-end tests"""
    pytest_args = [
        "tests/e2e/",
        "-v",
        "--tb=short",
        "--selenium",
        "--html=reports/reports/e2e.html",
        "--self-contained-html"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, "Running End-to-End Tests")


def run_all_tests(args):
    """Run all tests"""
    pytest_args = [
        "tests/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=term-missing",
        "--cov-report=html:reports/coverage/all",
        "--html=reports/reports/all.html",
        "--self-contained-html"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    # Exclude slow tests unless specifically requested
    if not args.include_slow:
        pytest_args.extend(["-m", "not slow"])
    
    return run_pytest(pytest_args, "Running All Tests")


def run_specific_tests(args):
    """Run specific test file or test"""
    if not args.test_path:
        print("❌ Error: --test-path is required for specific tests")
        return False
    
    pytest_args = [
        args.test_path,
        "-v",
        "--tb=short"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, f"Running Specific Test: {args.test_path}")


def run_marked_tests(args):
    """Run tests with specific marker"""
    if not args.marker:
        print("❌ Error: --marker is required for marked tests")
        return False
    
    pytest_args = [
        "-m",
        args.marker,
        "-v",
        "--tb=short"
    ]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.fail_fast:
        pytest_args.append("-x")
    
    return run_pytest(pytest_args, f"Running Tests with Marker: {args.marker}")


def generate_report():
    """Generate comprehensive test report"""
    print("\n📊 Generating Test Report")
    print("=" * 50)
    
    # Create reports directory
    reports_dir = BACKEND_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Check if coverage reports exist
    coverage_dir = reports_dir / "coverage"
    if coverage_dir.exists():
        print("✅ Coverage reports found")
        print(f"   Open file://{coverage_dir / 'index.html'} for detailed coverage")
    
    # Check if test reports exist
    test_reports_dir = reports_dir / "reports"
    if test_reports_dir.exists():
        print("✅ Test reports found")
        for report_file in test_reports_dir.glob("*.html"):
            print(f"   Open file://{report_file} for test results")
    
    # Generate summary
    summary = []
    summary.append("StreamWorks-KI Test Suite Summary")
    summary.append("=" * 40)
    summary.append("")
    summary.append("Test Categories:")
    summary.append("  • Unit Tests: Core functionality and business logic")
    summary.append("  • Integration Tests: API endpoints and service interactions")
    summary.append("  • Performance Tests: Response times and resource usage")
    summary.append("  • E2E Tests: Complete user workflows")
    summary.append("")
    summary.append("Test Markers:")
    summary.append("  • unit: Unit tests")
    summary.append("  • integration: Integration tests")
    summary.append("  • performance: Performance tests")
    summary.append("  • e2e: End-to-end tests")
    summary.append("  • slow: Slow running tests")
    summary.append("  • database: Tests requiring database")
    summary.append("  • api: Tests requiring API server")
    summary.append("  • rag: Tests requiring RAG services")
    summary.append("  • embedding: Tests requiring embedding services")
    summary.append("")
    summary.append("To run specific test types:")
    summary.append("  python run_tests.py --unit")
    summary.append("  python run_tests.py --integration")
    summary.append("  python run_tests.py --performance")
    summary.append("  python run_tests.py --e2e")
    summary.append("  python run_tests.py --marker database")
    summary.append("")
    
    summary_text = "\n".join(summary)
    print(summary_text)
    
    # Save summary
    summary_path = reports_dir / "test_summary.txt"
    with open(summary_path, "w") as f:
        f.write(summary_text)
    
    print(f"📄 Summary saved to: {summary_path.relative_to(BACKEND_ROOT)}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="StreamWorks-KI Backend Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --unit                    # Run unit tests only
  python run_tests.py --integration             # Run integration tests only
  python run_tests.py --performance             # Run performance tests only
  python run_tests.py --e2e                     # Run end-to-end tests only
  python run_tests.py --all                     # Run all tests
  python run_tests.py --test-path tests/unit/test_models.py  # Run specific file
  python run_tests.py --marker database         # Run tests with specific marker
  python run_tests.py --report                  # Generate test report
        """
    )
    
    # Test type arguments
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Specific test arguments
    parser.add_argument("--test-path", type=str, help="Run specific test file or test")
    parser.add_argument("--marker", type=str, help="Run tests with specific marker")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fail-fast", "-x", action="store_true", help="Stop on first failure")
    parser.add_argument("--include-slow", action="store_true", help="Include slow tests when running all tests")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    args = parser.parse_args()
    
    # Set up environment
    os.environ["TESTING"] = "True"
    
    # Create reports directory
    reports_dir = BACKEND_ROOT / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    # Run appropriate tests
    success = True
    
    if args.unit:
        success = run_unit_tests(args)
    elif args.integration:
        success = run_integration_tests(args)
    elif args.performance:
        success = run_performance_tests(args)
    elif args.e2e:
        success = run_e2e_tests(args)
    elif args.test_path:
        success = run_specific_tests(args)
    elif args.marker:
        success = run_marked_tests(args)
    elif args.all:
        success = run_all_tests(args)
    elif args.report:
        generate_report()
        return
    else:
        # Default: run unit tests
        success = run_unit_tests(args)
    
    # Final status
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    
    print(f"📊 Reports available in: reports/")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)