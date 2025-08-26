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
    """Information about a file lock"""
    file_path: str
    user_name: str
    computer_name: str
    lock_time: str
    process_id: Optional[int] = None
    file_hash: Optional[str] = None
    lock_id: Optional[str] = None

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
        """Get the path for the lock file corresponding to a CAD file"""
        # Create a hash of the file path to avoid long filenames
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.lock_directory / f"{file_hash}.lock"
    
    def create_lock(self, file_path: str, user_name: str, computer_name: str, 
                   process_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Create a lock for a CAD file
        
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
                
                # Check if lock is stale (older than 24 hours)
                lock_time = datetime.fromisoformat(existing_lock['lock_time'])
                if datetime.now() - lock_time > timedelta(hours=24):
                    logger.warning(f"Removing stale lock for {file_path}")
                    lock_file_path.unlink()
                else:
                    return False, f"File is locked by {existing_lock['user_name']} on {existing_lock['computer_name']}"
            except (json.JSONDecodeError, KeyError):
                # Corrupted lock file, remove it
                lock_file_path.unlink()
        
        # Create new lock
        lock_info = LockInfo(
            file_path=file_path,
            user_name=user_name,
            computer_name=computer_name,
            lock_time=datetime.now().isoformat(),
            process_id=process_id,
            lock_id=hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
        )
        
        try:
            with open(lock_file_path, 'w') as f:
                json.dump(asdict(lock_info), f, indent=2)
            
            logger.info(f"Created lock for {file_path} by {user_name}")
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
