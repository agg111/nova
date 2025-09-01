#!/usr/bin/env python3
"""
Test script to demonstrate automatic file monitoring with NovaLocks directory
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.lock_manager import LockManager
from backend.monitor.file_monitor import FileMonitor
import time
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s')

def main():
    # Initialize lock manager and file monitor with NovaLocks directory
    lock_manager = LockManager('./NovaLocks')
    file_monitor = FileMonitor(lock_manager)
    
    print("🔄 Starting automatic CAD file monitoring...")
    print("📁 Using NovaLocks directory for lock storage")
    print(f"📁 Lock directory: {lock_manager.lock_directory}")
    print("📁 Monitoring processes:", file_monitor.cad_processes)
    print("⏰ Check interval: 2 seconds")
    print()
    
    # Start monitoring
    file_monitor.start_monitoring()
    
    print("✅ File monitor is now running!")
    print("💡 Try opening a CAD file (SolidWorks, AutoCAD, etc.) and it will auto-lock")
    print("📁 Locks will be stored in the NovaLocks directory")
    print("🛑 Press Ctrl+C to stop monitoring")
    
    try:
        # Keep the script running
        while True:
            # Show current locks every 10 seconds
            locks = lock_manager.get_all_locks()
            if locks:
                print(f"🔒 Current auto-locks in NovaLocks: {len(locks)} files")
                for lock in locks[-3:]:  # Show last 3 locks
                    print(f"   └─ {lock.file_path.split('/')[-1]} by {lock.user_name}")
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping file monitor...")
        file_monitor.stop_monitoring()
        print("✅ Monitor stopped")

if __name__ == '__main__':
    main()