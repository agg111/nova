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

def get_lock_directory():
    """Get the shared lock directory like CADLock"""
    # Check for environment variable first (like CADLock)
    if 'NOVA_LOCKS_DIR' in os.environ:
        lock_dir = Path(os.environ['NOVA_LOCKS_DIR'])
    else:
        # Default shared locations similar to CADLock
        if os.name == 'nt':
            # Windows: Try common shared network locations
            possible_paths = [
                r"\\server\shared\Nova\Locks",
                r"G:\Shared drives\Engineering\Nova\Locks", 
                r"C:\Shared\Nova\Locks",
                r"Z:\Nova\Locks"
            ]
        else:
            # Linux/Mac: Network mount locations
            possible_paths = [
                "/mnt/shared/nova/locks",
                "/shared/nova/locks", 
                "/network/nova/locks"
            ]
        
        # Find first accessible path
        lock_dir = None
        for path in possible_paths:
            test_path = Path(path)
            try:
                if test_path.exists() and os.access(test_path, os.W_OK):
                    lock_dir = test_path
                    break
                elif test_path.parent.exists() and os.access(test_path.parent, os.W_OK):
                    # Parent exists and writable, we can create the locks dir
                    lock_dir = test_path
                    break
            except (PermissionError, OSError):
                continue
        
        # Fallback to local shared directory
        if lock_dir is None:
            if os.name == 'nt':
                lock_dir = Path("C:/Nova/Locks")
            else:
                lock_dir = Path("/opt/nova/locks")
    
    # Create directory if it doesn't exist
    try:
        lock_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify it's writable
        if not os.access(lock_dir, os.W_OK):
            raise PermissionError(f"Cannot write to lock directory: {lock_dir}")
            
        logger.info(f"Using Nova lock directory: {lock_dir}")
        return str(lock_dir)
        
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create/access lock directory {lock_dir}: {e}")
        logger.error("Nova requires write access to the shared lock directory for team collaboration")
        logger.error("Set NOVA_LOCKS_DIR environment variable to a shared network path")
        raise SystemExit(f"Cannot initialize Nova lock directory: {e}")

class NovaCLI:
    """Command-line interface for Nova system"""
    
    def __init__(self):
        self.lock_manager = None
        self.file_monitor = None
        self.manual_monitor = None
    
    def setup_lock_manager(self):
        """Initialize the lock manager"""
        lock_directory = get_lock_directory()
        self.lock_manager = LockManager(lock_directory)
        self.manual_monitor = ManualFileMonitor(self.lock_manager)
        logger.info(f"Lock manager initialized with directory: {lock_directory}")
    
    def start_monitor(self, check_interval: float = 2.0):
        """Start automatic file monitoring"""
        self.setup_lock_manager()
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
    
    def lock_file(self, file_path: str):
        """Manually lock a CAD file"""
        self.setup_lock_manager()
        
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return
        
        success, message = self.manual_monitor.lock_file(file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def unlock_file(self, file_path: str):
        """Manually unlock a CAD file"""
        self.setup_lock_manager()
        
        success, message = self.manual_monitor.unlock_file(file_path)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def check_lock(self, file_path: str):
        """Check if a file is locked"""
        self.setup_lock_manager()
        
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
    
    def unlock_all(self):
        """Unlock all files for the current user"""
        self.setup_lock_manager()
        
        count = self.manual_monitor.unlock_all_files()
        print(f"✅ Unlocked {count} files")
    
    def cleanup(self, max_age_hours: int = 24):
        """Clean up stale locks"""
        self.setup_lock_manager()
        
        count = self.lock_manager.cleanup_stale_locks(max_age_hours)
        print(f"✅ Cleaned up {count} stale locks")
    
    def list_locks(self):
        """List all active locks with rich analytics"""
        self.setup_lock_manager()
        
        locks = self.lock_manager.get_all_locks()
        
        if not locks:
            print("No active locks found")
            return
        
        print(f"Active locks ({len(locks)} total):")
        print("-" * 80)
        
        for lock in locks:
            print(f"File: {lock.file} ({lock.original_path})")
            print(f"User: {lock.user_name} on {lock.computer_name}")
            print(f"Created: {lock.lock_time}")
            print(f"Last seen: {lock.last_seen}")
            print(f"Method: {lock.detection_method} ({'auto' if lock.auto_created else 'manual'})")
            if lock.process_id:
                print(f"Process: {lock.process_id}")
            print(f"Lock ID: {lock.lock_id}")
            print("-" * 80)
    
    def show_analytics(self):
        """Show lock analytics dashboard"""
        self.setup_lock_manager()
        
        analytics = self.lock_manager.get_lock_analytics()
        
        print("📊 Nova Lock Analytics")
        print("=" * 50)
        print(f"Total active locks: {analytics['total_locks']}")
        print(f"Active users: {len(analytics['active_users'])}")
        print(f"User list: {', '.join(analytics['active_users'])}")
        print()
        
        print("🔍 Detection Methods:")
        for method, count in analytics['detection_methods'].items():
            print(f"  {method}: {count}")
        print()
        
        print("🤖 Creation Type:")
        print(f"  Automatic: {analytics['auto_vs_manual']['auto']}")
        print(f"  Manual: {analytics['auto_vs_manual']['manual']}")
        print()
        
        if analytics['lock_ages']:
            print(f"⏰ Average lock age: {analytics['average_lock_age']:.1f} hours")
            print(f"⚠️  Stale locks (>4h inactive): {analytics['stale_locks']}")
        
        print("=" * 50)
    
    def start_dashboard(self, host: str = '0.0.0.0', port: int = 5000):
        """Start the web dashboard"""
        lock_directory = get_lock_directory()
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
  nova monitor
  
  # Manually lock a file
  nova lock "path/to/file.sldprt"
  
  # Check if file is locked
  nova check "path/to/file.sldprt"
  
  # List all locks with details
  nova list
  
  # Show analytics dashboard
  nova analytics
  
  # Start web dashboard
  nova dashboard
  
  # Clean up stale locks
  nova cleanup --max-age 12

Shared Lock Directory (like CADLock):
  Set NOVA_LOCKS_DIR environment variable or auto-detects:
  Windows: \\\\server\\shared\\Nova\\Locks, G:\\Shared drives\\Engineering\\Nova\\Locks
  Linux/Mac: /mnt/shared/nova/locks, /shared/nova/locks
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start automatic file monitoring')
    monitor_parser.add_argument('--check-interval', type=float, default=2.0, help='Check interval in seconds')
    
    # Lock command
    lock_parser = subparsers.add_parser('lock', help='Manually lock a CAD file')
    lock_parser.add_argument('file_path', help='Path to the CAD file to lock')
    
    # Unlock command
    unlock_parser = subparsers.add_parser('unlock', help='Manually unlock a CAD file')
    unlock_parser.add_argument('file_path', help='Path to the CAD file to unlock')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if a file is locked')
    check_parser.add_argument('file_path', help='Path to the CAD file to check')
    
    # Unlock all command
    unlock_all_parser = subparsers.add_parser('unlock-all', help='Unlock all files for current user')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up stale locks')
    cleanup_parser.add_argument('--max-age', type=int, default=24, help='Maximum age in hours')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all active locks with details')
    
    # Analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Show lock analytics dashboard')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Start web dashboard')
    dashboard_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    dashboard_parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = NovaCLI()
    
    try:
        if args.command == 'monitor':
            cli.start_monitor(args.check_interval)
        elif args.command == 'lock':
            cli.lock_file(args.file_path)
        elif args.command == 'unlock':
            cli.unlock_file(args.file_path)
        elif args.command == 'check':
            cli.check_lock(args.file_path)
        elif args.command == 'unlock-all':
            cli.unlock_all()
        elif args.command == 'cleanup':
            cli.cleanup(args.max_age)
        elif args.command == 'list':
            cli.list_locks()
        elif args.command == 'analytics':
            cli.show_analytics()
        elif args.command == 'dashboard':
            cli.start_dashboard(args.host, args.port)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
