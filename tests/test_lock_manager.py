#!/usr/bin/env python3
"""
Unit tests for Nova Lock Manager
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.lock_manager import LockManager

class TestLockManager(unittest.TestCase):
    """Test cases for LockManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test locks
        self.test_dir = tempfile.mkdtemp()
        self.lock_manager = LockManager(self.test_dir)
        self.test_file = "/shared/projects/test_file.sldprt"
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_create_lock_success(self):
        """Test successful lock creation with enhanced analytics in NovaLocks directory"""
        success, message = self.lock_manager.create_lock(
            self.test_file, "test_user", "TEST-PC", 1234, auto_created=False, detection_method="manual"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Lock created successfully")
        
        # Verify lock exists with all new fields
        lock_info = self.lock_manager.check_lock(self.test_file)
        self.assertIsNotNone(lock_info)
        self.assertEqual(lock_info.user_name, "test_user")
        self.assertEqual(lock_info.computer_name, "TEST-PC")
        self.assertEqual(lock_info.process_id, 1234)
        
        # Test new analytics fields
        self.assertEqual(lock_info.file, "test_file.sldprt")
        self.assertEqual(lock_info.original_path, self.test_file)
        self.assertFalse(lock_info.auto_created)
        self.assertEqual(lock_info.detection_method, "manual")
        self.assertIsNotNone(lock_info.lock_time)
        self.assertIsNotNone(lock_info.last_seen)
        self.assertIsNotNone(lock_info.lock_id)
        self.assertIsNotNone(lock_info.lock_file)
        
        # Verify lock file is created in the test directory
        lock_files = list(Path(self.test_dir).glob("*.lock"))
        self.assertEqual(len(lock_files), 1)
        self.assertTrue(lock_files[0].exists())
    
    def test_create_lock_conflict(self):
        """Test lock creation when file is already locked"""
        # Create initial lock
        self.lock_manager.create_lock(self.test_file, "user1", "PC1", 1111, auto_created=True, detection_method="auto")
        
        # Try to create conflicting lock
        success, message = self.lock_manager.create_lock(
            self.test_file, "user2", "PC2", 2222, auto_created=False, detection_method="manual"
        )
        
        self.assertFalse(success)
        self.assertIn("File is locked by user1", message)
    
    def test_remove_lock_success(self):
        """Test successful lock removal"""
        # Create lock with analytics
        self.lock_manager.create_lock(self.test_file, "test_user", "TEST-PC", 1234, auto_created=False, detection_method="manual")
        
        # Remove lock
        success, message = self.lock_manager.remove_lock(self.test_file, "test_user")
        
        self.assertTrue(success)
        self.assertEqual(message, "Lock removed successfully")
        
        # Verify lock is gone
        lock_info = self.lock_manager.check_lock(self.test_file)
        self.assertIsNone(lock_info)
    
    def test_remove_lock_wrong_user(self):
        """Test lock removal by wrong user"""
        # Create lock with analytics
        self.lock_manager.create_lock(self.test_file, "user1", "PC1", 1111, auto_created=True, detection_method="temp_file")
        
        # Try to remove with different user
        success, message = self.lock_manager.remove_lock(self.test_file, "user2")
        
        self.assertFalse(success)
        self.assertIn("Lock belongs to user1", message)
    
    def test_remove_nonexistent_lock(self):
        """Test removing a lock that doesn't exist"""
        success, message = self.lock_manager.remove_lock(self.test_file, "test_user")
        
        self.assertFalse(success)
        self.assertIn("No lock found", message)
    
    def test_is_cad_file(self):
        """Test CAD file detection"""
        cad_files = [
            "test.sldprt", "test.sldasm", "test.slddrw",
            "test.dwg", "test.dxf", "test.ipt", "test.iam"
        ]
        
        non_cad_files = [
            "test.txt", "test.pdf", "test.doc", "test.exe"
        ]
        
        for file_path in cad_files:
            self.assertTrue(self.lock_manager.is_cad_file(file_path))
        
        for file_path in non_cad_files:
            self.assertFalse(self.lock_manager.is_cad_file(file_path))
    
    def test_get_all_locks(self):
        """Test getting all active locks with analytics"""
        # Create multiple locks with different analytics
        files_and_methods = [
            ("/path/to/file1.sldprt", "manual", False),
            ("/path/to/file2.dwg", "auto", True), 
            ("/path/to/file3.ipt", "temp_file", True)
        ]
        
        for i, (file_path, method, auto) in enumerate(files_and_methods):
            self.lock_manager.create_lock(file_path, f"user{i}", f"PC{i}", 1000+i, auto_created=auto, detection_method=method)
        
        # Get all locks
        locks = self.lock_manager.get_all_locks()
        
        self.assertEqual(len(locks), 3)
        
        # Verify lock details including analytics
        files = [item[0] for item in files_and_methods]
        for lock in locks:
            self.assertIn(lock.file_path, files)
            self.assertTrue(lock.user_name.startswith("user"))
            self.assertTrue(lock.computer_name.startswith("PC"))
            
            # Verify analytics fields
            self.assertIsNotNone(lock.detection_method)
            self.assertIn(lock.detection_method, ["manual", "auto", "temp_file"])
            self.assertIsNotNone(lock.lock_time)
            self.assertIsNotNone(lock.last_seen)
            self.assertIsNotNone(lock.lock_id)
    
    def test_lock_analytics(self):
        """Test lock analytics functionality"""
        # Create locks with different characteristics
        self.lock_manager.create_lock("/path/file1.sldprt", "user1", "PC1", auto_created=True, detection_method="auto")
        self.lock_manager.create_lock("/path/file2.dwg", "user2", "PC2", auto_created=False, detection_method="manual")
        self.lock_manager.create_lock("/path/file3.ipt", "user1", "PC1", auto_created=True, detection_method="temp_file")
        
        # Get analytics
        analytics = self.lock_manager.get_lock_analytics()
        
        # Verify analytics data
        self.assertEqual(analytics['total_locks'], 3)
        self.assertEqual(len(analytics['active_users']), 2)  # user1 and user2
        self.assertIn('user1', analytics['active_users'])
        self.assertIn('user2', analytics['active_users'])
        
        # Check detection methods
        self.assertEqual(analytics['detection_methods']['auto'], 1)
        self.assertEqual(analytics['detection_methods']['manual'], 1)
        self.assertEqual(analytics['detection_methods']['temp_file'], 1)
        
        # Check auto vs manual
        self.assertEqual(analytics['auto_vs_manual']['auto'], 2)
        self.assertEqual(analytics['auto_vs_manual']['manual'], 1)
        
        # Check other fields exist
        self.assertIsNotNone(analytics['lock_ages'])
        self.assertIsNotNone(analytics['average_lock_age'])
        self.assertIsNotNone(analytics['stale_locks'])
    
    def test_update_lock_activity(self):
        """Test updating lock activity timestamp"""
        # Create lock
        self.lock_manager.create_lock(self.test_file, "test_user", "TEST-PC", auto_created=False, detection_method="manual")
        
        # Get original last_seen time
        original_lock = self.lock_manager.check_lock(self.test_file)
        original_last_seen = original_lock.last_seen
        
        # Wait a bit and update activity
        import time
        time.sleep(1)
        success, message = self.lock_manager.update_lock_activity(self.test_file, "test_user")
        
        self.assertTrue(success)
        self.assertEqual(message, "Lock activity updated")
        
        # Verify last_seen was updated
        updated_lock = self.lock_manager.check_lock(self.test_file)
        self.assertNotEqual(original_last_seen, updated_lock.last_seen)
    
    def test_cadlock_style_file_naming(self):
        """Test CADLock-style lock file naming"""
        test_files = [
            "/path/to/test file.sldprt",  # spaces
            "/path/with/special:chars*.dwg",  # special characters
            "/very/long/path/to/engine_part.sldprt"
        ]
        
        for file_path in test_files:
            # Create lock
            success, _ = self.lock_manager.create_lock(file_path, "test_user", "TEST-PC", auto_created=False, detection_method="manual")
            self.assertTrue(success)
            
            # Check lock file path is safe
            lock_file_path = self.lock_manager.get_lock_file_path(file_path)
            lock_filename = lock_file_path.name
            
            # Should not contain unsafe characters
            unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']
            for char in unsafe_chars:
                if char in lock_filename:
                    self.fail(f"Unsafe character '{char}' found in lock filename: {lock_filename}")
            
            # Should have .lock extension
            self.assertTrue(lock_filename.endswith('.lock'))
            
            # Should contain hash prefix
            self.assertTrue('_' in lock_filename)
    
    def test_novalocks_directory_structure(self):
        """Test that Nova creates and uses NovaLocks directory structure"""
        # Test that the lock manager works with NovaLocks directory naming
        test_dir = tempfile.mkdtemp()
        novalocks_dir = Path(test_dir) / "NovaLocks"
        novalocks_dir.mkdir(exist_ok=True)
        
        try:
            lock_manager = LockManager(str(novalocks_dir))
            
            # Create a lock
            success, message = lock_manager.create_lock(
                self.test_file, "test_user", "TEST-PC", 1234, auto_created=False, detection_method="manual"
            )
            
            self.assertTrue(success)
            
            # Verify lock file is in NovaLocks directory
            lock_files = list(novalocks_dir.glob("*.lock"))
            self.assertEqual(len(lock_files), 1)
            self.assertTrue(lock_files[0].exists())
            
            # Verify the directory name contains "NovaLocks"
            self.assertIn("NovaLocks", str(novalocks_dir))
            
        finally:
            # Clean up
            shutil.rmtree(test_dir)

if __name__ == '__main__':
    unittest.main()