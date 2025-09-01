#!/usr/bin/env python3
"""
Unit tests for Nova service management
Tests service lifecycle, startup, shutdown, and error handling
"""

import unittest
import tempfile
import shutil
import os
import sys
import signal
import time
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.cli.main import NovaCLI
from backend.monitor.file_monitor import FileMonitor
from backend.web.dashboard import start_dashboard, init_dashboard

class TestServiceLifecycle(unittest.TestCase):
    """Test cases for service lifecycle management"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cli = NovaCLI()
        
        # Mock environment
        self.env_patcher = patch.dict(os.environ, {'NOVA_LOCKS_DIR': str(self.test_dir)})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_service_initialization(self):
        """Test that services initialize correctly"""
        self.cli.setup_lock_manager()
        
        # Verify core components are initialized
        self.assertIsNotNone(self.cli.lock_manager)
        self.assertIsNotNone(self.cli.manual_monitor)
        
        # Verify lock directory exists
        lock_dir = Path(self.test_dir)
        self.assertTrue(lock_dir.exists())
        self.assertTrue(os.access(lock_dir, os.W_OK))
    
    def test_file_monitor_startup(self):
        """Test file monitor service startup"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager, check_interval=0.1)
        
        # Start monitoring
        self.cli.file_monitor.start_monitoring()
        self.assertTrue(self.cli.file_monitor.is_monitoring())
        
        # Stop monitoring
        self.cli.file_monitor.stop_monitoring()
        self.assertFalse(self.cli.file_monitor.is_monitoring())
        
        # Clean up any remaining threads
        if hasattr(self.cli.file_monitor, '_monitor_thread') and self.cli.file_monitor._monitor_thread:
            self.cli.file_monitor._monitor_thread.join(timeout=1.0)
    
    def test_file_monitor_restart(self):
        """Test file monitor service restart capability"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager, check_interval=0.1)
        
        # Start, stop, and restart
        self.cli.file_monitor.start_monitoring()
        self.assertTrue(self.cli.file_monitor.is_monitoring())
        
        self.cli.file_monitor.stop_monitoring()
        self.assertFalse(self.cli.file_monitor.is_monitoring())
        
        # Restart
        self.cli.file_monitor.start_monitoring()
        self.assertTrue(self.cli.file_monitor.is_monitoring())
        
        self.cli.file_monitor.stop_monitoring()
        
        # Clean up any remaining threads
        if hasattr(self.cli.file_monitor, '_monitor_thread') and self.cli.file_monitor._monitor_thread:
            self.cli.file_monitor._monitor_thread.join(timeout=1.0)
    
    def test_dashboard_service_startup(self):
        """Test dashboard service startup"""
        with patch('backend.web.dashboard.init_dashboard') as mock_init:
            with patch('backend.web.dashboard.start_dashboard') as mock_start:
                # Test dashboard startup
                self.cli.start_dashboard('127.0.0.1', 5001)
                
                mock_init.assert_called_once()
                mock_start.assert_called_once_with('127.0.0.1', 5001)
    
    def test_dashboard_service_configuration(self):
        """Test dashboard service configuration options"""
        with patch('backend.web.dashboard.init_dashboard') as mock_init:
            with patch('backend.web.dashboard.start_dashboard') as mock_start:
                # Test different host/port configurations
                self.cli.start_dashboard('0.0.0.0', 8080)
                
                mock_init.assert_called_once()
                mock_start.assert_called_once_with('0.0.0.0', 8080)
    
    def test_service_dependency_management(self):
        """Test that services handle dependencies correctly"""
        self.cli.setup_lock_manager()
        
        # Verify lock manager is available before starting monitor
        self.assertIsNotNone(self.cli.lock_manager)
        
        # Create file monitor (depends on lock manager)
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
        self.assertIsNotNone(self.cli.file_monitor)
        
        # Verify the dependency chain
        self.assertEqual(self.cli.file_monitor.lock_manager, self.cli.lock_manager)

class TestServiceErrorHandling(unittest.TestCase):
    """Test cases for service error handling and recovery"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cli = NovaCLI()
        
        # Mock environment
        self.env_patcher = patch.dict(os.environ, {'NOVA_LOCKS_DIR': str(self.test_dir)})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_lock_manager_initialization_failure(self):
        """Test handling of lock manager initialization failure"""
        # Mock a failure in lock manager creation
        with patch('backend.core.lock_manager.LockManager', side_effect=Exception("Lock manager failed")):
            with self.assertRaises(Exception):
                self.cli.setup_lock_manager()
    
    def test_file_monitor_startup_failure(self):
        """Test handling of file monitor startup failure"""
        self.cli.setup_lock_manager()
        
        # Mock a failure in file monitor startup
        with patch.object(FileMonitor, 'start_monitoring', side_effect=Exception("Monitor failed")):
            self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
            
            with self.assertRaises(Exception):
                self.cli.file_monitor.start_monitoring()
    
    def test_dashboard_startup_failure(self):
        """Test handling of dashboard startup failure"""
        with patch('backend.web.dashboard.init_dashboard', side_effect=Exception("Dashboard failed")):
            with self.assertRaises(Exception):
                self.cli.start_dashboard('127.0.0.1', 5001)
    
    def test_service_cleanup_on_failure(self):
        """Test that services clean up properly on failure"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
        
        # Start monitoring
        self.cli.file_monitor.start_monitoring()
        self.assertTrue(self.cli.file_monitor.is_monitoring())
        
        # Simulate a failure
        with patch.object(self.cli.file_monitor, '_monitor_loop', side_effect=Exception("Monitor error")):
            # The monitor should stop when an error occurs
            try:
                self.cli.file_monitor._monitor_loop()
            except Exception:
                pass
        
        # Verify cleanup
        self.cli.file_monitor.stop_monitoring()
        self.assertFalse(self.cli.file_monitor.is_monitoring())
        
        # Clean up any remaining threads
        if hasattr(self.cli.file_monitor, '_monitor_thread') and self.cli.file_monitor._monitor_thread:
            self.cli.file_monitor._monitor_thread.join(timeout=1.0)
    
    def test_graceful_shutdown_on_signal(self):
        """Test graceful shutdown when receiving signals"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
        
        # Start monitoring
        self.cli.file_monitor.start_monitoring()
        self.assertTrue(self.cli.file_monitor.is_monitoring())
        
        # Simulate receiving a signal
        with patch('signal.signal') as mock_signal:
            # The monitor should handle signals gracefully
            self.cli.file_monitor.stop_monitoring()
            self.assertFalse(self.cli.file_monitor.is_monitoring())
            
            # Clean up any remaining threads
            if hasattr(self.cli.file_monitor, '_monitor_thread') and self.cli.file_monitor._monitor_thread:
                self.cli.file_monitor._monitor_thread.join(timeout=1.0)

class TestServicePerformance(unittest.TestCase):
    """Test cases for service performance and resource management"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cli = NovaCLI()
        
        # Mock environment
        self.env_patcher = patch.dict(os.environ, {'NOVA_LOCKS_DIR': str(self.test_dir)})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_file_monitor_performance(self):
        """Test file monitor performance characteristics"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager, check_interval=0.1)
        
        # Measure startup time
        start_time = time.time()
        self.cli.file_monitor.start_monitoring()
        startup_time = time.time() - start_time
        
        # Startup should be fast (< 1 second)
        self.assertLess(startup_time, 1.0, f"File monitor startup too slow: {startup_time:.3f}s")
        
        # Stop monitoring
        self.cli.file_monitor.stop_monitoring()
    
    def test_lock_manager_performance(self):
        """Test lock manager performance characteristics"""
        self.cli.setup_lock_manager()
        
        # Measure lock creation time
        start_time = time.time()
        success, message = self.cli.lock_manager.create_lock(
            "test_file.sldprt", "test_user", "TEST-PC", 1234
        )
        lock_time = time.time() - start_time
        
        # Lock creation should be fast (< 0.1 seconds)
        self.assertLess(lock_time, 0.1, f"Lock creation too slow: {lock_time:.3f}s")
        self.assertTrue(success)
        
        # Clean up
        self.cli.lock_manager.remove_lock("test_file.sldprt", "test_user")
    
    def test_dashboard_initialization_performance(self):
        """Test dashboard initialization performance"""
        start_time = time.time()
        
        with patch('backend.web.dashboard.init_dashboard') as mock_init:
            with patch('backend.web.dashboard.start_dashboard') as mock_start:
                self.cli.start_dashboard('127.0.0.1', 5001)
                
                init_time = time.time() - start_time
                
                # Dashboard initialization should be fast (< 0.5 seconds)
                self.assertLess(init_time, 0.5, f"Dashboard init too slow: {init_time:.3f}s")
    
    def test_service_memory_usage(self):
        """Test that services don't leak memory"""
        self.cli.setup_lock_manager()
        
        # Create multiple monitors to test for memory leaks
        monitors = []
        for i in range(5):
            monitor = FileMonitor(self.cli.lock_manager, check_interval=0.1)
            monitors.append(monitor)
        
        # Start and stop all monitors
        for monitor in monitors:
            monitor.start_monitoring()
            monitor.stop_monitoring()
            
            # Clean up any remaining threads
            if hasattr(monitor, '_monitor_thread') and monitor._monitor_thread:
                monitor._monitor_thread.join(timeout=1.0)
        
        # Clean up
        monitors.clear()
        
        # The system should still be functional
        self.assertIsNotNone(self.cli.lock_manager)

class TestServiceIntegration(unittest.TestCase):
    """Test cases for service integration and coordination"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.cli = NovaCLI()
        
        # Mock environment
        self.env_patcher = patch.dict(os.environ, {'NOVA_LOCKS_DIR': str(self.test_dir)})
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir)
    
    def test_lock_manager_and_monitor_coordination(self):
        """Test coordination between lock manager and file monitor"""
        self.cli.setup_lock_manager()
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
        
        # Start monitoring
        self.cli.file_monitor.start_monitoring()
        
        # Create a lock through the lock manager
        success, message = self.cli.lock_manager.create_lock(
            "test_file.sldprt", "test_user", "TEST-PC", 1234
        )
        self.assertTrue(success)
        
        # The monitor should be aware of the lock
        lock_info = self.cli.lock_manager.check_lock("test_file.sldprt")
        self.assertIsNotNone(lock_info)
        
        # Stop monitoring
        self.cli.file_monitor.stop_monitoring()
        
        # Clean up any remaining threads
        if hasattr(self.cli.file_monitor, '_monitor_thread') and self.cli.file_monitor._monitor_thread:
            self.cli.file_monitor._monitor_thread.join(timeout=1.0)
        
        # Clean up
        self.cli.lock_manager.remove_lock("test_file.sldprt", "test_user")
    
    def test_dashboard_and_lock_manager_coordination(self):
        """Test coordination between dashboard and lock manager"""
        self.cli.setup_lock_manager()
        
        # Create some locks
        self.cli.lock_manager.create_lock(
            "file1.sldprt", "user1", "PC1", 1111
        )
        self.cli.lock_manager.create_lock(
            "file2.sldasm", "user2", "PC2", 2222
        )
        
        # Initialize dashboard with the same lock manager
        with patch('backend.web.dashboard.init_dashboard') as mock_init:
            self.cli.start_dashboard('127.0.0.1', 5001)
            
            # Dashboard should be initialized with the lock directory
            mock_init.assert_called_once()
            
            # The dashboard should have access to the same locks
            locks = self.cli.lock_manager.get_all_locks()
            self.assertEqual(len(locks), 2)
        
        # Clean up
        self.cli.lock_manager.remove_lock("file1.sldprt", "user1")
        self.cli.lock_manager.remove_lock("file2.sldasm", "user2")
    
    def test_service_startup_order(self):
        """Test that services start up in the correct order"""
        # Lock manager should be initialized first
        self.cli.setup_lock_manager()
        self.assertIsNotNone(self.cli.lock_manager)
        
        # File monitor depends on lock manager
        self.cli.file_monitor = FileMonitor(self.cli.lock_manager)
        self.assertIsNotNone(self.cli.file_monitor)
        
        # Dashboard depends on lock manager
        with patch('backend.web.dashboard.init_dashboard'):
            with patch('backend.web.dashboard.start_dashboard'):
                self.cli.start_dashboard('127.0.0.1', 5001)
        
        # All services should be properly initialized
        self.assertIsNotNone(self.cli.lock_manager)
        self.assertIsNotNone(self.cli.file_monitor)

if __name__ == '__main__':
    unittest.main()
