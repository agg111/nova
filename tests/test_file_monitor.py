#!/usr/bin/env python3
"""
Unit tests for Nova File Monitor
"""

import unittest
import tempfile
import shutil
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.lock_manager import LockManager
from backend.monitor.file_monitor import FileMonitor


class TestFileMonitor(unittest.TestCase):
    """Test cases for FileMonitor class"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test locks
        self.test_dir = tempfile.mkdtemp()
        self.lock_manager = LockManager(self.test_dir)
        self.file_monitor = FileMonitor(self.lock_manager)

        # Test file paths
        self.test_files = [
            "/shared/projects/test_file.sldprt",
            "/shared/projects/assembly.sldasm",
            "/shared/projects/drawing.dwg"
        ]

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    # -----------------------------
    # Helper to make mock processes
    # -----------------------------
    def make_mock_process(self, name, pid, user, open_files):
        proc = Mock()
        # Set up the info dict that FileMonitor expects
        proc.info = {"pid": pid, "name": name, "username": user}
        proc.pid = pid
        proc.name.return_value = name
        proc.username.return_value = user
        proc.open_files.return_value = [Mock(path=f) for f in open_files]
        return proc

    def test_cad_process_detection(self):
        """Test that CAD processes are correctly identified"""
        # Test case-insensitive matching (the method converts to lowercase)
        # Use the exact process names that FileMonitor has, plus variations
        cad_processes = [
            "SLDWORKS.exe", "sldworks.exe", "solidworks.exe", "SOLIDWORKS.exe",
            "acad.exe", "ACAD.exe", "ACAD.EXE", "Acad.exe",
            "Inventor.exe", "inventor.exe", "INVENTOR.EXE", "inventor.EXE"
        ]
        
        for process_name in cad_processes:
            self.assertTrue(self.file_monitor.is_cad_process(process_name), 
                          f"Process {process_name} should be recognized as CAD")

        non_cad_processes = [
            "notepad.exe", "chrome.exe", "explorer.exe",
            "python.exe", "java.exe", "node.exe"
        ]
        for process_name in non_cad_processes:
            self.assertFalse(self.file_monitor.is_cad_process(process_name),
                           f"Process {process_name} should NOT be recognized as CAD")

    def test_cad_file_detection(self):
        """Test that CAD files are correctly identified"""
        cad_files = [
            "test.sldprt", "test.sldasm", "test.slddrw",
            "test.dwg", "test.dxf", "test.ipt", "test.iam",
            "test.step", "test.stp", "test.iges", "test.igs"
        ]
        for file_path in cad_files:
            self.assertTrue(self.file_monitor.is_cad_file(file_path))

        non_cad_files = [
            "test.txt", "test.pdf", "test.doc", "test.exe",
            "test.jpg", "test.png", "test.mp4"
        ]
        for file_path in non_cad_files:
            self.assertFalse(self.file_monitor.is_cad_file(file_path))

    def test_process_file_mapping(self):
        """Test mapping between processes and open files"""
        mock_process = self.make_mock_process(
            "solidworks.exe", 1234, "test_user",
            ["/shared/projects/test.sldprt", "/shared/projects/assembly.sldasm"]
        )
        files = self.file_monitor.get_process_files(mock_process)
        self.assertEqual(len(files), 2)
        self.assertIn("/shared/projects/test.sldprt", files)
        self.assertIn("/shared/projects/assembly.sldasm", files)

    def test_automatic_lock_creation(self):
        """Test automatic lock creation when CAD files are opened"""
        # Test the direct method that handles file opening
        test_file = self.test_files[0]
        test_user = "test_user"
        test_pid = 1234
        
        # Call the method directly to test lock creation
        self.file_monitor._handle_file_opened(test_file, test_pid, test_user)
        
        # Check that lock was created
        lock_info = self.lock_manager.check_lock(test_file)
        self.assertIsNotNone(lock_info, 
                           f"Lock should be created for {test_file}")
        self.assertEqual(lock_info.user_name, test_user)
        self.assertEqual(lock_info.process_id, test_pid)
        self.assertTrue(lock_info.auto_created)
        self.assertEqual(lock_info.detection_method, "auto")

    def test_automatic_lock_removal(self):
        """Test automatic lock removal when CAD files are closed"""
        # First create a lock
        self.lock_manager.create_lock(
            self.test_files[0], "test_user", "TEST-PC", 1234,
            auto_created=True, detection_method="auto"
        )
        lock_info = self.lock_manager.check_lock(self.test_files[0])
        self.assertIsNotNone(lock_info)

        # Test the direct method that handles file closing
        self.file_monitor._handle_file_closed(self.test_files[0], 1234, "test_user")
        
        # Check that lock was removed
        lock_info = self.lock_manager.check_lock(self.test_files[0])
        self.assertIsNone(lock_info, "Lock should be removed when file is closed")

    def test_multiple_cad_processes(self):
        """Test monitoring multiple CAD processes simultaneously"""
        # Test the direct methods that handle file opening for multiple processes
        test_file1 = self.test_files[0]
        test_file2 = self.test_files[1]
        
        # Simulate user1 opening file1
        self.file_monitor._handle_file_opened(test_file1, 1234, "user1")
        
        # Simulate user2 opening file2
        self.file_monitor._handle_file_opened(test_file2, 5678, "user2")
        
        # Check that both locks were created
        lock1 = self.lock_manager.check_lock(test_file1)
        lock2 = self.lock_manager.check_lock(test_file2)
        
        self.assertIsNotNone(lock1, f"Lock should be created for {test_file1}")
        self.assertIsNotNone(lock2, f"Lock should be created for {test_file2}")
        self.assertEqual(lock1.user_name, "user1")
        self.assertEqual(lock2.user_name, "user2")

    def test_novalocks_directory_usage(self):
        """Test that FileMonitor uses NovaLocks directory correctly"""
        novalocks_dir = Path(self.test_dir) / "NovaLocks"
        novalocks_dir.mkdir(exist_ok=True)

        novalocks_lock_manager = LockManager(str(novalocks_dir))
        novalocks_file_monitor = FileMonitor(novalocks_lock_manager)

        # Test the direct method that handles file opening
        test_file = self.test_files[0]
        test_user = "test_user"
        test_pid = 1234
        
        # Call the method directly to test lock creation in NovaLocks directory
        novalocks_file_monitor._handle_file_opened(test_file, test_pid, test_user)
        
        # Check that lock file was created in NovaLocks directory
        lock_files = list(novalocks_dir.glob("*.lock"))
        self.assertEqual(len(lock_files), 1, f"Expected 1 lock file, found {len(lock_files)}")
        self.assertTrue(lock_files[0].exists())
        
        # Verify the lock was created in the LockManager
        lock_info = novalocks_lock_manager.check_lock(test_file)
        self.assertIsNotNone(lock_info, "Lock should be created in NovaLocks directory")

    def test_monitoring_start_stop(self):
        """Test that monitoring can be started and stopped correctly"""
        self.assertFalse(self.file_monitor.is_monitoring())
        self.file_monitor.start_monitoring()
        self.assertTrue(self.file_monitor.is_monitoring())
        self.file_monitor.stop_monitoring()
        self.assertFalse(self.file_monitor.is_monitoring())

    def test_error_handling(self):
        """Test error handling during monitoring"""
        with patch("psutil.process_iter") as mock_process_iter:
            mock_process_iter.side_effect = Exception("Process iteration error")
            try:
                self.file_monitor.start_monitoring()
                time.sleep(0.1)
                self.file_monitor.stop_monitoring()
            except Exception as e:
                self.fail(f"FileMonitor should handle errors gracefully: {e}")


if __name__ == "__main__":
    unittest.main()
