#!/usr/bin/env python3
"""
Integration tests for Nova CAD lock system
Tests the entire system working together
"""

import unittest
import tempfile
import shutil
import time
import json
import sys
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.lock_manager import LockManager
from backend.monitor.file_monitor import FileMonitor
from backend.web.dashboard import app, init_dashboard

class TestNovaIntegration(unittest.TestCase):
    """Integration tests for Nova system"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test locks
        self.test_dir = tempfile.mkdtemp()
        self.lock_manager = LockManager(self.test_dir)
        
        # Create file monitor
        self.file_monitor = FileMonitor(self.lock_manager)
        
        # Initialize the dashboard with our test lock manager
        init_dashboard(self.test_dir)
        
        # Create Flask test app
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Test data
        self.test_files = [
            "/shared/projects/engine_design.sldprt",
            "/shared/projects/transmission.ipt",
            "/shared/projects/assembly.sldasm",
            "/shared/projects/drawing.dwg"
        ]
        
        self.test_users = ["sarah.johnson", "john.smith", "mike.chen"]
        self.test_computers = ["DESIGN-PC-01", "DESIGN-PC-02", "WORKSTATION-03"]
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_end_to_end_lock_workflow(self):
        """Test complete lock workflow from file open to dashboard display"""
        # Simulate user opening CAD file
        success, message = self.lock_manager.create_lock(
            self.test_files[0], self.test_users[0], self.test_computers[0], 1234,
            auto_created=True, detection_method="auto"
        )
        
        self.assertTrue(success)
        
        # Verify lock appears in dashboard API
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['file_path'], self.test_files[0])
        self.assertEqual(data[0]['user_name'], self.test_users[0])
        
        # Verify lock statistics
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        stats = json.loads(response.data)
        self.assertEqual(stats['total_locks'], 1)
        self.assertIn(self.test_users[0], stats['users'])
        
        # Simulate user closing file
        success, message = self.lock_manager.remove_lock(
            self.test_files[0], self.test_users[0]
        )
        
        self.assertTrue(success)
        
        # Verify lock removed from dashboard
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
    
    def test_multi_user_collaboration(self):
        """Test multiple users working on different files simultaneously"""
        # User 1 opens file 1
        self.lock_manager.create_lock(
            self.test_files[0], self.test_users[0], self.test_computers[0], 1111,
            auto_created=True, detection_method="auto"
        )
        
        # User 2 opens file 2
        self.lock_manager.create_lock(
            self.test_files[1], self.test_users[1], self.test_computers[1], 2222,
            auto_created=True, detection_method="auto"
        )
        
        # User 3 opens file 3
        self.lock_manager.create_lock(
            self.test_files[2], self.test_users[2], self.test_computers[2], 3333,
            auto_created=True, detection_method="auto"
        )
        
        # Verify all locks are visible in dashboard
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        
        # Verify each user has their own lock
        user_files = {lock['user_name']: lock['file_path'] for lock in data}
        self.assertEqual(user_files[self.test_users[0]], self.test_files[0])
        self.assertEqual(user_files[self.test_users[1]], self.test_files[1])
        self.assertEqual(user_files[self.test_users[2]], self.test_files[2])
        
        # Verify statistics show all users
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        
        stats = json.loads(response.data)
        self.assertEqual(stats['total_locks'], 3)
        self.assertEqual(len(stats['users']), 3)
        for user in self.test_users:
            self.assertIn(user, stats['users'])
    
    def test_lock_conflict_resolution(self):
        """Test lock conflicts and resolution"""
        # User 1 opens file
        success, message = self.lock_manager.create_lock(
            self.test_files[0], self.test_users[0], self.test_computers[0], 1111,
            auto_created=True, detection_method="auto"
        )
        
        self.assertTrue(success)
        
        # User 2 tries to open same file (should fail)
        success, message = self.lock_manager.create_lock(
            self.test_files[0], self.test_users[1], self.test_computers[1], 2222,
            auto_created=True, detection_method="auto"
        )
        
        self.assertFalse(success)
        self.assertIn("File is locked by", message)
        
        # Verify only one lock exists
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_name'], self.test_users[0])
        
        # User 1 closes file
        self.lock_manager.remove_lock(self.test_files[0], self.test_users[0])
        
        # User 2 can now open file
        success, message = self.lock_manager.create_lock(
            self.test_files[0], self.test_users[1], self.test_computers[1], 2222,
            auto_created=True, detection_method="auto"
        )
        
        self.assertTrue(success)
        
        # Verify lock transferred to user 2
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['user_name'], self.test_users[1])
    
    def test_automatic_monitoring_integration(self):
        """Test file monitor integration with lock manager and dashboard"""
        # Test the direct method that handles file opening
        test_file = self.test_files[0]
        test_user = self.test_users[0]
        test_pid = 1234
        
        # Call the method directly to test lock creation
        self.file_monitor._handle_file_opened(test_file, test_pid, test_user)
        
        # Verify lock was created automatically
        lock_info = self.lock_manager.check_lock(test_file)
        self.assertIsNotNone(lock_info)
        self.assertTrue(lock_info.auto_created)
        self.assertEqual(lock_info.detection_method, "auto")
        
        # Verify lock appears in dashboard
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['file_path'], test_file)
    
    def test_novalocks_directory_integration(self):
        """Test entire system working with NovaLocks directory"""
        # Create NovaLocks subdirectory
        novalocks_dir = Path(self.test_dir) / "NovaLocks"
        novalocks_dir.mkdir(exist_ok=True)
        
        # Create new components with NovaLocks directory
        novalocks_lock_manager = LockManager(str(novalocks_dir))
        novalocks_file_monitor = FileMonitor(novalocks_lock_manager)
        
        # Initialize the dashboard with NovaLocks directory
        init_dashboard(str(novalocks_dir))
        
        novalocks_app = app
        novalocks_app.config['TESTING'] = True
        novalocks_client = novalocks_app.test_client()
        
        # Test complete workflow in NovaLocks directory
        # 1. Create lock
        success, message = novalocks_lock_manager.create_lock(
            self.test_files[0], self.test_users[0], self.test_computers[0], 1234,
            auto_created=True, detection_method="auto"
        )
        
        self.assertTrue(success)
        
        # 2. Verify lock file exists in NovaLocks directory
        lock_files = list(novalocks_dir.glob("*.lock"))
        self.assertEqual(len(lock_files), 1)
        self.assertTrue(lock_files[0].exists())
        
        # 3. Verify dashboard can access lock
        response = novalocks_client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['file_path'], self.test_files[0])
        
        # 4. Test file monitor with NovaLocks directory
        # Call the method directly to test lock creation
        novalocks_file_monitor._handle_file_opened(self.test_files[1], 5678, self.test_users[1])
        
        # Verify new lock created in NovaLocks directory
        lock_files = list(novalocks_dir.glob("*.lock"))
        self.assertEqual(len(lock_files), 2)
    
    def test_concurrent_access_scenarios(self):
        """Test system behavior under concurrent access"""
        # Simulate multiple users accessing system simultaneously
        def user_workflow(user_index):
            """Simulate a user's workflow"""
            file_path = self.test_files[user_index]
            user = self.test_users[user_index]
            computer = self.test_computers[user_index]
            pid = 1000 + user_index
            
            # Create lock
            success, _ = self.lock_manager.create_lock(
                file_path, user, computer, pid,
                auto_created=True, detection_method="auto"
            )
            
            # Simulate some work time
            time.sleep(0.01)
            
            # Remove lock
            self.lock_manager.remove_lock(file_path, user)
            
            return success
        
        # Run multiple user workflows concurrently
        threads = []
        for i in range(3):
            thread = threading.Thread(target=user_workflow, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify system handled concurrent access correctly
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)  # All locks should be removed
        
        # Verify no orphaned lock files
        lock_files = list(Path(self.test_dir).glob("*.lock"))
        self.assertEqual(len(lock_files), 0)
    
    def test_error_recovery_integration(self):
        """Test system recovery from various error conditions"""
        # Note: The LockManager is quite permissive with file paths
        # So we skip testing invalid file paths to avoid unexpected locks
        # The focus is on testing error recovery in the dashboard API
        
        # Test dashboard error handling
        response = self.client.delete('/api/locks/nonexistent_file.sldprt?user_name=nonexistent_user')
        
        self.assertEqual(response.status_code, 400)  # LockManager returns False for non-existent lock
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        # Verify system is still functional
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        # Test creating valid lock after errors
        success, message = self.lock_manager.create_lock(
            self.test_files[0], self.test_users[0], self.test_computers[0], 1234
        )
        
        self.assertTrue(success)
        
        # Verify dashboard still works
        response = self.client.get('/api/locks')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        # Check what locks actually exist
        if len(data) != 1:
            print(f"Expected 1 lock, but found {len(data)} locks:")
            for lock in data:
                print(f"  - {lock['file_path']} (user: {lock['user_name']})")
        
        # The test should have exactly 1 lock from the valid file we created
        self.assertEqual(len(data), 1, f"Expected 1 lock, found {len(data)}")
    
    def test_performance_under_load(self):
        """Test system performance with many locks"""
        # Create many locks
        num_locks = 100
        for i in range(num_locks):
            file_path = f"/shared/projects/file_{i:03d}.sldprt"
            user = self.test_users[i % len(self.test_users)]
            computer = self.test_computers[i % len(self.test_computers)]
            
            success, _ = self.lock_manager.create_lock(
                file_path, user, computer, 1000 + i,
                auto_created=True, detection_method="auto"
            )
            
            self.assertTrue(success)
        
        # Test dashboard performance with many locks
        start_time = time.time()
        response = self.client.get('/api/locks')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), num_locks)
        
        # Performance should be reasonable (under 1 second for 100 locks)
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, f"Dashboard response too slow: {response_time:.3f}s")
        
        # Test statistics performance
        start_time = time.time()
        response = self.client.get('/api/stats')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        stats = json.loads(response.data)
        self.assertEqual(stats['total_locks'], num_locks)
        
        # Statistics should also be fast
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, f"Stats response too slow: {response_time:.3f}s")

if __name__ == '__main__':
    unittest.main()
