#!/usr/bin/env python3
"""
Test script for Nova background monitoring commands
"""

import subprocess
import time
import sys

def test_nova_commands():
    """Test the nova start, stop, and status commands"""
    
    print("🧪 Testing Nova background monitoring commands...")
    print("=" * 50)
    
    # Test 1: Check initial status
    print("\n1. Checking initial status...")
    result = subprocess.run(['python', '-m', 'backend.cli.main', 'status'], 
                           capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Test 2: Start monitoring
    print("\n2. Starting Nova monitor in background...")
    result = subprocess.run(['python', '-m', 'backend.cli.main', 'start'], 
                           capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Wait a moment for process to start
    time.sleep(3)
    
    # Test 3: Check status again
    print("\n3. Checking status after start...")
    result = subprocess.run(['python', '-m', 'backend.cli.main', 'status'], 
                           capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Test 4: Stop monitoring
    print("\n4. Stopping Nova monitor...")
    result = subprocess.run(['python', '-m', 'backend.cli.main', 'stop'], 
                           capture_output=True, text=True)
    print(result.stdout.strip())
    
    # Wait a moment for process to stop
    time.sleep(2)
    
    # Test 5: Check final status
    print("\n5. Checking final status...")
    result = subprocess.run(['python', '-m', 'backend.cli.main', 'status'], 
                           capture_output=True, text=True)
    print(result.stdout.strip())
    
    print("\n✅ Testing complete!")

if __name__ == '__main__':
    try:
        test_nova_commands()
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
