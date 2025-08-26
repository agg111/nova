"""
Main CLI interface for Nova system
Provides command-line tools for managing CAD file locks
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from ..core.lock_manager import LockManager
from ..monitor.file_monitor import FileMonitor, ManualFileMonitor
from ..web.dashboard import start_dashboard, init_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NovaCLI:
    """Command-line interface for Nova system"""
    
    def __init__(self):
        self.lock_manager = None
        self.file_monitor = None
        self.manual_monitor = None
    
    def setup_lock_manager(self, lock_directory: str):
        """Initialize the lock manager"""
        self.lock_manager = LockManager(lock_directory)
        self.manual_monitor = ManualFileMonitor(self.lock_manager)
        logger.info(f"Lock manager initialized with directory: {lock_directory}")
    
    def start_monitor(self, lock_directory: str, check_interval: float = 2.0):
        """Start automatic file monitoring"""
        self.setup_lock_manager(lock_directory)
        self.file_monitor = FileMonitor(self.lock_manager, check_interval=check_interval)
        
        print("Starting CAD file monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            self.file_monitor.start_monitoring()
            
            # Keep the main thread alive
            while True:
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping file monitoring...")
            self.file_monitor.stop_monitoring()
            print("File monitoring stopped")
    
    def lock_file(self, file_path: str, lock_directory: str):
        """Manually lock a CAD file"""
        self.setup_lock_manager(lock_directory)
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return
        
        success, message = self.manual_monitor.lock_file(file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def unlock_file(self, file_path: str, lock_directory: str):
        """Manually unlock a CAD file"""
        self.setup_lock_manager(lock_directory)
        
        success, message = self.manual_monitor.unlock_file(file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def check_lock(self, file_path: str, lock_directory: str):
        """Check if a file is locked"""
        self.setup_lock_manager(lock_directory)
        
        lock_info = self.manual_monitor.check_file_lock(file_path)
        if lock_info:
            print(f"🔒 File is locked:")
            print(f"   User: {lock_info.user_name}")
            print(f"   Computer: {lock_info.computer_name}")
            print(f"   Locked since: {lock_info.lock_time}")
            if lock_info.process_id:
                print(f"   Process ID: {lock_info.process_id}")
        else:
            print("🔓 File is not locked")
    
    def unlock_all(self, lock_directory: str):
        """Unlock all files for the current user"""
        self.setup_lock_manager(lock_directory)
        
        count = self.manual_monitor.unlock_all_files()
        print(f"✅ Unlocked {count} files")
    
    def cleanup(self, lock_directory: str, max_age_hours: int = 24):
        """Clean up stale locks"""
        self.setup_lock_manager(lock_directory)
        
        count = self.lock_manager.cleanup_stale_locks(max_age_hours)
        print(f"✅ Cleaned up {count} stale locks")
    
    def list_locks(self, lock_directory: str):
        """List all active locks"""
        self.setup_lock_manager(lock_directory)
        
        locks = self.lock_manager.get_all_locks()
        
        if not locks:
            print("No active locks found")
            return
        
        print(f"Active locks ({len(locks)} total):")
        print("-" * 80)
        
        for lock in locks:
            print(f"File: {lock.file_path}")
            print(f"User: {lock.user_name} on {lock.computer_name}")
            print(f"Locked: {lock.lock_time}")
            if lock.process_id:
                print(f"Process: {lock.process_id}")
            print("-" * 80)
    
    def start_dashboard(self, lock_directory: str, host: str = '0.0.0.0', port: int = 5000):
        """Start the web dashboard"""
        init_dashboard(lock_directory)
        print(f"Starting Nova dashboard on http://{host}:{port}")
        print("Press Ctrl+C to stop")
        
        try:
            start_dashboard(host=host, port=port)
        except KeyboardInterrupt:
            print("\nDashboard stopped")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Nova - CAD file locking system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start automatic monitoring
  nova monitor --lock-dir ./locks
  
  # Manually lock a file
  nova lock "path/to/file.sldprt" --lock-dir ./locks
  
  # Check if file is locked
  nova check "path/to/file.sldprt" --lock-dir ./locks
  
  # Start web dashboard
  nova dashboard --lock-dir ./locks
  
  # List all locks
  nova list --lock-dir ./locks
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start automatic file monitoring')
    monitor_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    monitor_parser.add_argument('--check-interval', type=float, default=2.0, help='Check interval in seconds')
    
    # Lock command
    lock_parser = subparsers.add_parser('lock', help='Manually lock a CAD file')
    lock_parser.add_argument('file_path', help='Path to the CAD file to lock')
    lock_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    
    # Unlock command
    unlock_parser = subparsers.add_parser('unlock', help='Manually unlock a CAD file')
    unlock_parser.add_argument('file_path', help='Path to the CAD file to unlock')
    unlock_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if a file is locked')
    check_parser.add_argument('file_path', help='Path to the CAD file to check')
    check_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    
    # Unlock all command
    unlock_all_parser = subparsers.add_parser('unlock-all', help='Unlock all files for current user')
    unlock_all_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up stale locks')
    cleanup_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    cleanup_parser.add_argument('--max-age', type=int, default=24, help='Maximum age in hours')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all active locks')
    list_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start web dashboard')
    dashboard_parser.add_argument('--lock-dir', required=True, help='Directory to store lock files')
    dashboard_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = NovaCLI()
    
    try:
        if args.command == 'monitor':
            cli.start_monitor(args.lock_dir, args.check_interval)
        elif args.command == 'lock':
            cli.lock_file(args.file_path, args.lock_dir)
        elif args.command == 'unlock':
            cli.unlock_file(args.file_path, args.lock_dir)
        elif args.command == 'check':
            cli.check_lock(args.file_path, args.lock_dir)
        elif args.command == 'unlock-all':
            cli.unlock_all(args.lock_dir)
        elif args.command == 'cleanup':
            cli.cleanup(args.lock_dir, args.max_age)
        elif args.command == 'list':
            cli.list_locks(args.lock_dir)
        elif args.command == 'dashboard':
            cli.start_dashboard(args.lock_dir, args.host, args.port)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
