"""
File monitoring system for CAD files
Watches for file open/close events and manages locks automatically
"""

import os
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
import logging

from ..core.lock_manager import LockManager

logger = logging.getLogger(__name__)

class FileMonitor:
    """Monitors CAD file operations and manages locks automatically"""
    
    def __init__(self, lock_manager: LockManager, 
                 cad_processes: List[str] = None,
                 check_interval: float = 2.0):
        """
        Initialize the file monitor
        
        Args:
            lock_manager: Lock manager instance
            cad_processes: List of CAD process names to monitor
            check_interval: How often to check for file operations (seconds)
        """
        self.lock_manager = lock_manager
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        
        # Default CAD processes to monitor
        self.cad_processes = cad_processes or [
            'SLDWORKS.exe',      # SolidWorks
            'Inventor.exe',      # Inventor
            'acad.exe',          # AutoCAD
            'proe.exe',          # Pro/Engineer
            'creo.exe',          # Creo
            'fusion360.exe',     # Fusion 360
            'nx.exe',            # Siemens NX
            'catia.exe',         # CATIA
        ]
        
        # Track open files per process
        self.process_files: Dict[int, List[str]] = {}
        self.user_name = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
        self.computer_name = os.getenv('COMPUTERNAME') or os.getenv('HOSTNAME') or 'Unknown'
        
        logger.info(f"File monitor initialized for user: {self.user_name}")
        logger.info(f"Monitoring CAD processes: {self.cad_processes}")
    
    def start_monitoring(self):
        """Start the file monitoring in a separate thread"""
        if self.running:
            logger.warning("File monitor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("File monitoring started")
    
    def stop_monitoring(self):
        """Stop the file monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("File monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_cad_processes()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)
    
    def _check_cad_processes(self):
        """Check for CAD processes and their open files"""
        current_process_files = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'open_files']):
            try:
                if proc.info['name'] in self.cad_processes:
                    pid = proc.info['pid']
                    open_files = self._get_process_files(proc)
                    current_process_files[pid] = open_files
                    
                    # Check for new files (files that weren't tracked before)
                    if pid in self.process_files:
                        new_files = set(open_files) - set(self.process_files[pid])
                        for file_path in new_files:
                            self._handle_file_opened(file_path, pid)
                    
                    # Check for closed files (files that were tracked but are no longer open)
                    if pid in self.process_files:
                        closed_files = set(self.process_files[pid]) - set(open_files)
                        for file_path in closed_files:
                            self._handle_file_closed(file_path, pid)
                            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.error(f"Error checking process {proc.info.get('name', 'unknown')}: {e}")
        
        # Handle processes that have terminated
        terminated_pids = set(self.process_files.keys()) - set(current_process_files.keys())
        for pid in terminated_pids:
            for file_path in self.process_files[pid]:
                self._handle_file_closed(file_path, pid)
        
        self.process_files = current_process_files
    
    def _get_process_files(self, proc) -> List[str]:
        """Get list of open files for a process"""
        try:
            files = []
            for file in proc.open_files():
                if file.path and self.lock_manager.is_cad_file(file.path):
                    files.append(file.path)
            return files
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return []
    
    def _handle_file_opened(self, file_path: str, process_id: int):
        """Handle when a CAD file is opened"""
        try:
            success, message = self.lock_manager.create_lock(
                file_path, self.user_name, self.computer_name, process_id
            )
            
            if success:
                logger.info(f"Auto-locked file: {file_path}")
            else:
                logger.warning(f"Failed to auto-lock {file_path}: {message}")
                
        except Exception as e:
            logger.error(f"Error handling file opened event for {file_path}: {e}")
    
    def _handle_file_closed(self, file_path: str, process_id: int):
        """Handle when a CAD file is closed"""
        try:
            success, message = self.lock_manager.remove_lock(file_path, self.user_name)
            
            if success:
                logger.info(f"Auto-unlocked file: {file_path}")
            else:
                logger.warning(f"Failed to auto-unlock {file_path}: {message}")
                
        except Exception as e:
            logger.error(f"Error handling file closed event for {file_path}: {e}")
    
    def get_current_locks(self) -> List[str]:
        """Get list of files currently locked by this user"""
        all_locks = self.lock_manager.get_all_locks()
        return [lock.file_path for lock in all_locks if lock.user_name == self.user_name]
    
    def cleanup_user_locks(self) -> int:
        """Remove all locks for the current user"""
        return self.lock_manager.remove_user_locks(self.user_name)

class ManualFileMonitor:
    """Manual file monitor for explicit lock/unlock operations"""
    
    def __init__(self, lock_manager: LockManager):
        self.lock_manager = lock_manager
        self.user_name = os.getenv('USERNAME') or os.getenv('USER') or 'Unknown'
        self.computer_name = os.getenv('COMPUTERNAME') or os.getenv('HOSTNAME') or 'Unknown'
    
    def lock_file(self, file_path: str) -> tuple[bool, str]:
        """Manually lock a CAD file"""
        return self.lock_manager.create_lock(
            file_path, self.user_name, self.computer_name
        )
    
    def unlock_file(self, file_path: str) -> tuple[bool, str]:
        """Manually unlock a CAD file"""
        return self.lock_manager.remove_lock(file_path, self.user_name)
    
    def check_file_lock(self, file_path: str):
        """Check if a file is locked"""
        return self.lock_manager.check_lock(file_path)
    
    def unlock_all_files(self) -> int:
        """Unlock all files for the current user"""
        return self.lock_manager.remove_user_locks(self.user_name)
