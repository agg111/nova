#!/usr/bin/env python3
"""
Demonstrate what happens in Nova when a user tries to open a locked file
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.lock_manager import LockManager

def demo_lock_conflict():
    """Demonstrate lock conflict scenario"""
    
    print("🔒 Nova Lock Conflict Demo")
    print("=" * 50)
    
    # Show NovaLocks directory structure
    print("📁 Nova uses dedicated NovaLocks directory:")
    print("   G:\\Shared drives\\Cosmic\\Engineering\\50 - CAD Data\\")
    print("   ├── Locks\\          ← CadLock's locks")
    print("   └── NovaLocks\\      ← Nova's locks")
    print()
    
    # Initialize lock manager with NovaLocks directory
    lock_manager = LockManager('./NovaLocks')
    
    # Test file path
    test_file = "/shared/projects/engine_design.dwg"
    
    print(f"📁 Test file: {test_file}")
    print()
    
    # Scenario 1: Sarah opens the file first (successful auto-detection)
    print("👩‍💻 Scenario: Sarah opens the file")
    success1, message1 = lock_manager.create_lock(
        test_file, 
        "sarah.johnson", 
        "DESIGN-PC-03", 
        2756,
        auto_created=True,
        detection_method="temp_file"
    )
    
    print(f"   Result: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"   Message: {message1}")
    print()
    
    # Scenario 2: John tries to open the same file (conflict!)
    print("👨‍💻 Scenario: John tries to open the same file")
    success2, message2 = lock_manager.create_lock(
        test_file,
        "john.smith",
        "DESIGN-PC-01", 
        3421,
        auto_created=True,
        detection_method="auto"
    )
    
    print(f"   Result: {'✅ Success' if success2 else '❌ Failed'}")
    print(f"   Message: {message2}")
    print()
    
    # Show current lock status with enhanced analytics
    print("🔍 Current lock status:")
    lock_info = lock_manager.check_lock(test_file)
    if lock_info:
        print(f"   🔒 File is locked by: {lock_info.user_name}")
        print(f"   💻 On computer: {lock_info.computer_name}")
        print(f"   ⏰ Locked since: {lock_info.lock_time}")
        print(f"   👁️  Last seen: {lock_info.last_seen}")
        print(f"   🤖 Detection: {lock_info.detection_method} ({'auto' if lock_info.auto_created else 'manual'})")
        print(f"   🆔 Process ID: {lock_info.process_id}")
        print(f"   📄 File: {lock_info.file}")
        print(f"   🔗 Lock ID: {lock_info.lock_id[:8]}...")
    else:
        print("   🔓 File is not locked")
    
    print()
    
    # Scenario 3: Mike also tries to open (another conflict!)
    print("👨‍💻 Scenario: Mike also tries to open the file")
    success3, message3 = lock_manager.create_lock(
        test_file,
        "mike.chen",
        "WORKSTATION-07",
        1892,
        auto_created=False,
        detection_method="manual"
    )
    
    print(f"   Result: {'✅ Success' if success3 else '❌ Failed'}")
    print(f"   Message: {message3}")
    print()
    
    # What happens in real Nova workflow
    print("🔄 In Real Nova Workflow:")
    print("   1. Sarah opens engine_design.dwg in AutoCAD")
    print("   2. Nova agent detects file opening → Creates lock")
    print("   3. John tries to open same file in AutoCAD")
    print("   4. Nova agent tries to create lock → FAILS")
    print("   5. AutoCAD opens file in READ-ONLY mode")
    print("   6. John sees warning: 'File locked by sarah.johnson'")
    print()
    
    # What Nova does differently from CADLock
    print("🆚 Nova vs CADLock Behavior:")
    print("   CADLock: Uses open-cad.bat wrapper script")
    print("   Nova: Automatic detection + read-only enforcement")
    print()
    
    # Cleanup
    print("🧹 Cleanup: Sarah closes the file")
    success4, message4 = lock_manager.remove_lock(test_file, "sarah.johnson")
    print(f"   Result: {'✅ Success' if success4 else '❌ Failed'}")
    print(f"   Message: {message4}")
    print()
    
    # Now John can open it
    print("✅ Now John can open the file")
    success5, message5 = lock_manager.create_lock(
        test_file,
        "john.smith", 
        "DESIGN-PC-01",
        3421,
        auto_created=True,
        detection_method="auto"
    )
    print(f"   Result: {'✅ Success' if success5 else '❌ Failed'}")
    print(f"   Message: {message5}")
    print()
    
    # Show analytics summary
    print("📊 Lock Analytics Summary:")
    analytics = lock_manager.get_lock_analytics()
    print(f"   Total locks: {analytics['total_locks']}")
    print(f"   Active users: {len(analytics['active_users'])}")
    if analytics['detection_methods']:
        print(f"   Detection methods: {analytics['detection_methods']}")
    if analytics['auto_vs_manual']:
        print(f"   Auto vs Manual: {analytics['auto_vs_manual']}")
    
    # Final cleanup
    lock_manager.remove_lock(test_file, "john.smith")

if __name__ == '__main__':
    demo_lock_conflict()