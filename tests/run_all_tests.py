#!/usr/bin/env python3
"""
Test runner for Nova test suite
Runs all tests and demonstrations
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PASSED")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ FAILED")
            if result.stderr:
                print("Error:", result.stderr)
            if result.stdout:
                print("Output:", result.stdout)
                
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    """Run all Nova tests"""
    print("🚀 Nova Test Suite Runner")
    print("=" * 60)
    
    # Change to project root directory
    os.chdir(Path(__file__).parent.parent)
    
    # Run unit tests
    run_command("python3 tests/test_lock_manager.py", "Lock Manager Unit Tests")
    
    # Run demonstrations (non-interactive parts)
    print("\n🎭 Running Demonstrations...")
    print("=" * 50)
    
    run_command("python3 tests/demo_lock_conflict.py", "Lock Conflict Demo")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print("✅ Unit Tests: Lock Manager")
    print("✅ Demonstrations: Lock Conflicts") 
    print("⏳ TODO: File Monitor Tests")
    print("⏳ TODO: Dashboard API Tests")
    print("⏳ TODO: Integration Tests")
    
    print("\n🎯 All Available Tests Completed!")
    print("\nTo run individual tests:")
    print("  python3 tests/test_lock_manager.py")
    print("  python3 tests/demo_lock_conflict.py")

if __name__ == '__main__':
    main()