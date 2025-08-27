"""
Core lock management system for CAD files
Handles lock creation, validation, and cleanup
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class LockInfo:
    """Information about a file lock - enhanced with CADLock analytics"""
    # Original file information
    file_path: str              # Full path to the CAD file
    original_path: str          # Original path (same as file_path for compatibility)
    file: str                   # Just the filename
    
    # User and system information  
    user_name: str              # User who locked the file
    computer_name: str          # Computer name where lock was created
    
    # Timing information
    lock_time: str              # When lock was created (timestamp)
    last_seen: str              # Last activity/heartbeat (timestamp) 
    
    # Lock metadata
    lock_file: str              # Path to the lock file itself
    lock_id: str                # Unique lock identifier
    
    # Analytics data (like CADLock)
    auto_created: bool          # True if auto-detected, False if manual
    detection_method: str       # How the lock was detected: 'auto', 'manual', 'temp_file'
    
    # Optional fields
    process_id: Optional[int] = None
    file_hash: Optional[str] = None

class LockManager:
    """Manages file locks for CAD files"""
    
    def __init__(self, lock_directory: str, supported_extensions: List[str] = None):
        """
        Initialize the lock manager
        
        Args:
            lock_directory: Directory to store lock files
            supported_extensions: List of supported file extensions
        """
        self.lock_directory = Path(lock_directory)
        self.lock_directory.mkdir(parents=True, exist_ok=True)
        
        # Default supported CAD file extensions
        self.supported_extensions = supported_extensions or [
            '.sldprt', '.sldasm', '.slddrw',  # SolidWorks
            '.prt', '.asm', '.drw',           # Pro/Engineer, Creo
            '.ipt', '.iam', '.idw',           # Inventor
            '.dwg', '.dxf',                   # AutoCAD
            '.f3d', '.f3z',                   # Fusion 360
            '.step', '.stp', '.iges', '.igs'  # Neutral formats
        ]
        
        logger.info(f"Lock manager initialized with directory: {self.lock_directory}")
        logger.info(f"Supported extensions: {self.supported_extensions}")
    
    def is_cad_file(self, file_path: str) -> bool:
        """Check if a file is a supported CAD file"""
        return Path(file_path).suffix.lower() in self.supported_extensions
    
    def get_lock_file_path(self, file_path: str) -> Path:
        """Get the path for the lock file corresponding to a CAD file (CADLock style)"""
        # Convert path to filesystem-safe name like CADLock
        rel_path = os.path.basename(file_path)  # Start with filename
        safe_path = rel_path.replace('\\', '_').replace('/', '_').replace(':', '_')
        safe_path = safe_path.replace('*', '_').replace('?', '_').replace('"', '_')
        safe_path = safe_path.replace('<', '_').replace('>', '_').replace('|', '_')
        safe_path = safe_path.replace(' ', '_')  # Also replace spaces
        
        # Add hash prefix to ensure uniqueness for files with same name
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        lock_filename = f"{file_hash}_{safe_path}.lock"
        
        return self.lock_directory / lock_filename
    
    def create_lock(self, file_path: str, user_name: str, computer_name: str, 
                   process_id: Optional[int] = None, auto_created: bool = False,
                   detection_method: str = 'manual') -> Tuple[bool, str]:
        """
        Create a lock for a CAD file with rich analytics like CADLock
        
        Args:
            file_path: Path to the CAD file
            user_name: Name of the user creating the lock
            computer_name: Name of the computer
            process_id: Process ID if available
            auto_created: True if auto-detected, False if manual
            detection_method: How lock was detected ('manual', 'auto', 'temp_file')
        
        Returns:
            Tuple of (success, message)
        """
        if not self.is_cad_file(file_path):
            return False, f"File {file_path} is not a supported CAD file"
        
        lock_file_path = self.get_lock_file_path(file_path)
        
        # Check if file is already locked
        if lock_file_path.exists():
            try:
                with open(lock_file_path, 'r') as f:
                    existing_lock = json.load(f)
                
                # Check if lock is stale using last_seen if available
                last_activity = existing_lock.get('last_seen', existing_lock.get('lock_time'))
                if last_activity:
                    last_time = datetime.fromisoformat(last_activity)
                    if datetime.now() - last_time > timedelta(hours=24):
                        logger.warning(f"Removing stale lock for {file_path}")
                        lock_file_path.unlink()
                    else:
                        return False, f"File is locked by {existing_lock['user_name']} on {existing_lock['computer_name']}"
                
            except (json.JSONDecodeError, KeyError):
                # Corrupted lock file, remove it
                lock_file_path.unlink()
        
        # Create new lock with rich analytics (CADLock format)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lock_info = LockInfo(
            # File information
            file_path=file_path,
            original_path=file_path,
            file=os.path.basename(file_path),
            
            # User information
            user_name=user_name,
            computer_name=computer_name,
            
            # Timing
            lock_time=current_time,
            last_seen=current_time,
            
            # Lock metadata
            lock_file=str(lock_file_path),
            lock_id=hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest(),
            
            # Analytics (like CADLock)
            auto_created=auto_created,
            detection_method=detection_method,
            
            # Optional
            process_id=process_id,
            file_hash=hashlib.md5(file_path.encode()).hexdigest()
        )
        
        try:
            with open(lock_file_path, 'w') as f:
                json.dump(asdict(lock_info), f, indent=2)
            
            logger.info(f"Created {detection_method} lock for {file_path} by {user_name}")
            return True, f"Lock created successfully"
            
        except Exception as e:
            logger.error(f"Failed to create lock for {file_path}: {e}")
            return False, f"Failed to create lock: {e}"
    
    def remove_lock(self, file_path: str, user_name: str) -> Tuple[bool, str]:
        """
        Remove a lock for a CAD file
        
        Returns:
            Tuple of (success, message)
        """
        lock_file_path = self.get_lock_file_path(file_path)
        
        if not lock_file_path.exists():
            return False, f"No lock found for {file_path}"
        
        try:
            with open(lock_file_path, 'r') as f:
                lock_info = json.load(f)
            
            # Only allow the user who created the lock to remove it
            if lock_info['user_name'] != user_name:
                return False, f"Lock belongs to {lock_info['user_name']}, not {user_name}"
            
            lock_file_path.unlink()
            logger.info(f"Removed lock for {file_path} by {user_name}")
            return True, f"Lock removed successfully"
            
        except Exception as e:
            logger.error(f"Failed to remove lock for {file_path}: {e}")
            return False, f"Failed to remove lock: {e}"
    
    def check_lock(self, file_path: str) -> Optional[LockInfo]:
        """Check if a file is locked and return lock information"""
        lock_file_path = self.get_lock_file_path(file_path)
        
        if not lock_file_path.exists():
            return None
        
        try:
            with open(lock_file_path, 'r') as f:
                lock_data = json.load(f)
            
            # Check if lock is stale
            lock_time = datetime.fromisoformat(lock_data['lock_time'])
            if datetime.now() - lock_time > timedelta(hours=24):
                logger.warning(f"Found stale lock for {file_path}, removing")
                lock_file_path.unlink()
                return None
            
            return LockInfo(**lock_data)
            
        except Exception as e:
            logger.error(f"Error reading lock file for {file_path}: {e}")
            return None
    
    def get_all_locks(self) -> List[LockInfo]:
        """Get all active locks"""
        locks = []
        
        for lock_file in self.lock_directory.glob("*.lock"):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                lock_info = LockInfo(**lock_data)
                
                # Check if lock is stale
                lock_time = datetime.fromisoformat(lock_data['lock_time'])
                if datetime.now() - lock_time > timedelta(hours=24):
                    logger.warning(f"Removing stale lock: {lock_file}")
                    lock_file.unlink()
                    continue
                
                locks.append(lock_info)
                
            except Exception as e:
                logger.error(f"Error reading lock file {lock_file}: {e}")
                # Remove corrupted lock file
                lock_file.unlink()
        
        return locks
    
    def cleanup_stale_locks(self, max_age_hours: int = 24) -> int:
        """
        Remove locks older than specified hours
        
        Returns:
            Number of locks removed
        """
        removed_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for lock_file in self.lock_directory.glob("*.lock"):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                lock_time = datetime.fromisoformat(lock_data['lock_time'])
                if lock_time < cutoff_time:
                    lock_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed stale lock: {lock_file}")
                    
            except Exception as e:
                logger.error(f"Error processing lock file {lock_file}: {e}")
                # Remove corrupted lock file
                lock_file.unlink()
                removed_count += 1
        
        logger.info(f"Cleaned up {removed_count} stale locks")
        return removed_count
    
    def remove_user_locks(self, user_name: str) -> int:
        """
        Remove all locks for a specific user
        
        Returns:
            Number of locks removed
        """
        removed_count = 0
        
        for lock_file in self.lock_directory.glob("*.lock"):
            try:
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                if lock_data['user_name'] == user_name:
                    lock_file.unlink()
                    removed_count += 1
                    logger.info(f"Removed lock for user {user_name}: {lock_file}")
                    
            except Exception as e:
                logger.error(f"Error processing lock file {lock_file}: {e}")
        
        logger.info(f"Removed {removed_count} locks for user {user_name}")
        return removed_count
    
    def update_lock_activity(self, file_path: str, user_name: str) -> Tuple[bool, str]:
        """
        Update the last_seen timestamp for a lock (heartbeat)
        
        Args:
            file_path: Path to the CAD file
            user_name: User name to verify ownership
        
        Returns:
            Tuple of (success, message)
        """
        lock_file_path = self.get_lock_file_path(file_path)
        
        if not lock_file_path.exists():
            return False, f"No lock found for {file_path}"
        
        try:
            with open(lock_file_path, 'r') as f:
                lock_data = json.load(f)
            
            # Verify ownership
            if lock_data['user_name'] != user_name:
                return False, f"Lock belongs to {lock_data['user_name']}, not {user_name}"
            
            # Update last_seen timestamp
            lock_data['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(lock_file_path, 'w') as f:
                json.dump(lock_data, f, indent=2)
            
            return True, "Lock activity updated"
            
        except Exception as e:
            logger.error(f"Failed to update lock activity for {file_path}: {e}")
            return False, f"Failed to update lock activity: {e}"
    
    def get_lock_analytics(self) -> Dict[str, any]:
        """
        Get analytics about all locks (like CADLock dashboard)
        
        Returns:
            Dictionary with analytics data
        """
        all_locks = self.get_all_locks()
        
        if not all_locks:
            return {
                'total_locks': 0,
                'active_users': [],
                'detection_methods': {},
                'auto_vs_manual': {'auto': 0, 'manual': 0},
                'lock_ages': [],
                'stale_locks': 0
            }
        
        # Analyze locks
        users = set()
        detection_methods = {}
        auto_count = 0
        manual_count = 0
        lock_ages = []
        stale_count = 0
        
        current_time = datetime.now()
        
        for lock in all_locks:
            users.add(lock.user_name)
            
            # Count detection methods
            method = lock.detection_method
            detection_methods[method] = detection_methods.get(method, 0) + 1
            
            # Count auto vs manual
            if lock.auto_created:
                auto_count += 1
            else:
                manual_count += 1
            
            # Calculate lock age
            try:
                lock_time = datetime.strptime(lock.lock_time, "%Y-%m-%d %H:%M:%S")
                age_hours = (current_time - lock_time).total_seconds() / 3600
                lock_ages.append(age_hours)
                
                # Check for stale locks (no activity for 4+ hours)
                last_seen = datetime.strptime(lock.last_seen, "%Y-%m-%d %H:%M:%S")
                inactive_hours = (current_time - last_seen).total_seconds() / 3600
                if inactive_hours > 4:
                    stale_count += 1
            except:
                pass
        
        return {
            'total_locks': len(all_locks),
            'active_users': list(users),
            'detection_methods': detection_methods,
            'auto_vs_manual': {'auto': auto_count, 'manual': manual_count},
            'lock_ages': lock_ages,
            'average_lock_age': sum(lock_ages) / len(lock_ages) if lock_ages else 0,
            'stale_locks': stale_count
        }
