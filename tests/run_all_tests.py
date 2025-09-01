#!/usr/bin/env python3
"""
Test runner for Nova test suite
Runs all tests and demonstrations
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def parse_test_results(output):
    """Parse test output to extract pass/fail counts"""
    if not output:

        return 0, 0, 0
    

    
    # Look for patterns like "Ran 9 tests in 1.014s" and "FAILED (failures=2)"
    ran_match = re.search(r'Ran (\d+) tests?', output)
    
    if not ran_match:

        return 0, 0, 0
    
    total = int(ran_match.group(1))

    
    # Check if tests failed or passed
    if 'FAILED' in output:

        # Parse failure count
        failures_match = re.search(r'FAILED \(failures=(\d+)\)', output)
        errors_match = re.search(r'FAILED \(failures=(\d+), errors=(\d+)\)', output)
        
        failures = int(failures_match.group(1)) if failures_match else 0
        errors = int(errors_match.group(2)) if errors_match else 0
        
        # If we found errors, add them to failures
        if errors > 0:
            failures += errors
        
        passed = total - failures
    else:

        # All tests passed
        passed = total
        failures = 0
    

    return total, passed, failures

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Parse test results - check both stdout and stderr
        # Python unittest often outputs to stderr instead of stdout
        output = result.stdout if result.stdout else result.stderr
        total, passed, failed = parse_test_results(output)
        
        if result.returncode == 0:
            if failed == 0:
                print(f"✅ PASSED ({passed}/{total} tests)")
            else:
                print(f"⚠️  PARTIAL ({passed}/{total} tests passed, {failed} failed)")
        else:
            print(f"❌ FAILED ({passed}/{total} tests passed, {failed} failed)")
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
        return total, passed, failed
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 0, 0, 0

def main():
    """Run all Nova tests"""
    print("🚀 Nova Test Suite Runner")
    print("=" * 60)
    
    # Change to project root directory
    os.chdir(Path(__file__).parent.parent)
    
    # Track overall results
    total_tests = 0
    total_passed = 0
    total_failed = 0
    test_results = []
    
    # Run unit tests
    print("\n📋 Running Unit Tests...")
    print("=" * 50)
    
    total, passed, failed = run_command("python3 tests/test_lock_manager.py", "Lock Manager Unit Tests")
    test_results.append(("Lock Manager", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    total, passed, failed = run_command("python3 tests/test_file_monitor.py", "File Monitor Unit Tests")
    test_results.append(("File Monitor", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    total, passed, failed = run_command("python3 tests/test_dashboard.py", "Dashboard API Unit Tests")
    test_results.append(("Dashboard API", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    total, passed, failed = run_command("python3 tests/test_cli_commands.py", "CLI Commands Unit Tests")
    test_results.append(("CLI Commands", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    total, passed, failed = run_command("python3 tests/test_service_management.py", "Service Management Unit Tests")
    test_results.append(("Service Management", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    total, passed, failed = run_command("python3 tests/test_integration.py", "System Integration Tests")
    test_results.append(("System Integration", total, passed, failed))
    total_tests += total
    total_passed += passed
    total_failed += failed
    
    # Run demonstrations (non-interactive parts)
    print("\n🎭 Running Demonstrations...")
    print("=" * 50)
    
    # Demo scripts don't output test results, they're demonstrations
    print("\n🎭 Running Demonstrations...")
    print("=" * 50)
    
    print("\n🧪 Lock Conflict Demo")
    print("=" * 50)
    try:
        result = subprocess.run("python3 tests/demo_lock_conflict.py", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Demo completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Demo failed")
            if result.stderr:
                print("Error:", result.stderr)
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Add demo as "completed" rather than "tests passed"
    test_results.append(("Lock Conflict Demo", 0, 0, 0))  # Not a test suite
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    for name, total, passed, failed in test_results:
        if name == "Lock Conflict Demo":
            print(f"🎭 {name}: Demonstration completed")
        elif failed == 0:
            print(f"✅ {name}: {passed}/{total} tests passed")
        else:
            print(f"❌ {name}: {passed}/{total} tests passed, {failed} failed")
    
    print(f"\n🎯 Overall Results: {total_passed}/{total_tests} tests passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total_failed} test(s) failed. Check the output above for details.")
    
    print("\nTo run individual tests:")
    print("  python3 tests/test_lock_manager.py")
    print("  python3 tests/test_file_monitor.py")
    print("  python3 tests/test_dashboard.py")
    print("  python3 tests/test_cli_commands.py")
    print("  python3 tests/test_service_management.py")
    print("  python3 tests/test_integration.py")
    print("  python3 tests/demo_lock_conflict.py")

if __name__ == '__main__':
    main()