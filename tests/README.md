# 🧪 Nova Test Suite

This directory contains tests and demonstrations for the Nova CAD lock system.

## Test Files

### **Unit Tests**
- `test_lock_manager.py` - Unit tests for the LockManager class with NovaLocks directory
- `test_file_monitor.py` - Unit tests for file monitoring and CAD process detection
- `test_dashboard.py` - Unit tests for web dashboard API endpoints
- `test_cli_commands.py` - Unit tests for CLI commands and interface
- `test_service_management.py` - Unit tests for service lifecycle and management

### **Integration Tests**
- `test_integration.py` - Comprehensive system integration tests
- `test_background_monitor.py` - Tests for nova start/stop commands

### **Demonstrations**
- `demo_lock_conflict.py` - Interactive demo showing what happens when users try to open locked files

## Running Tests

### **Run All Unit Tests**
```bash
# From the nova root directory
python -m pytest tests/

# Or run individual test files
python tests/test_lock_manager.py
```

### **Run Demonstrations**
```bash
# Show lock conflict behavior
python tests/demo_lock_conflict.py
```

### **Test Coverage**
```bash
# Generate test coverage report
pip install pytest-cov
python -m pytest tests/ --cov=backend --cov-report=html
```

## Test Scenarios Covered

### **Lock Manager Tests**
- ✅ Successful lock creation in NovaLocks directory
- ✅ Lock conflict detection
- ✅ Lock removal by owner
- ✅ Prevention of removal by wrong user
- ✅ CAD file type detection
- ✅ Multiple lock management
- ✅ NovaLocks directory structure creation

### **File Monitor Tests**
- ✅ CAD process detection (SolidWorks, AutoCAD, Inventor)
- ✅ CAD file type identification
- ✅ Automatic lock creation when files are opened
- ✅ Automatic lock removal when files are closed
- ✅ Multiple CAD processes monitoring
- ✅ NovaLocks directory integration
- ✅ Error handling during monitoring

### **Dashboard API Tests**
- ✅ `/api/locks` endpoint returns all locks
- ✅ `/api/stats` endpoint returns lock statistics
- ✅ `/api/cleanup` endpoint removes stale locks
- ✅ `/api/remove_lock` endpoint removes specific locks
- ✅ `/api/search` endpoint filters locks by criteria
- ✅ Dashboard home page loads correctly
- ✅ NovaLocks directory integration
- ✅ Error handling and CORS headers

### **CLI Commands Tests**
- ✅ Command-line interface initialization
- ✅ Lock file/unlock file commands
- ✅ Check lock status command
- ✅ List all locks command
- ✅ Cleanup stale locks command
- ✅ Show analytics dashboard command
- ✅ Start web dashboard command
- ✅ Environment variable configuration
- ✅ Default directory path handling
- ✅ Permission error handling

### **Service Management Tests**
- ✅ Service initialization and setup
- ✅ File monitor startup and shutdown
- ✅ Dashboard service startup
- ✅ Service restart capability
- ✅ Dependency management
- ✅ Error handling and recovery
- ✅ Graceful shutdown on signals
- ✅ Performance characteristics
- ✅ Memory usage management
- ✅ Service coordination and integration

### **Integration Tests**
- ✅ End-to-end lock workflow
- ✅ Multi-user collaboration scenarios
- ✅ Lock conflict resolution
- ✅ Automatic monitoring integration
- ✅ NovaLocks directory system integration
- ✅ Concurrent access handling
- ✅ Error recovery scenarios
- ✅ Performance under load (100+ locks)

### **Lock Conflict Demo**
- ✅ First user opens file successfully
- ✅ Second user gets lock conflict error
- ✅ Clear error message with user/computer info
- ✅ Lock release and subsequent access
- ✅ Read-only mode explanation
- ✅ NovaLocks directory structure display

## Test Environment Setup

The tests use temporary directories and don't require actual network storage or CAD software. This makes them safe to run on any development machine.

**Test Structure:**
```
tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This file
├── test_lock_manager.py        # Lock manager unit tests with NovaLocks
├── test_file_monitor.py        # File monitor unit tests
├── test_dashboard.py           # Dashboard API unit tests
├── test_integration.py         # System integration tests
├── test_background_monitor.py  # Background monitoring tests
├── demo_lock_conflict.py       # Interactive lock conflict demo
└── run_all_tests.py            # Test runner script
```

## Manual Testing Checklist

For full system testing, manually verify:

- [ ] Network storage accessibility (NovaLocks directory)
- [ ] CAD software integration (SolidWorks, AutoCAD, Inventor, etc.)
- [ ] Dashboard web interface (http://localhost:5000)
- [ ] Multi-workstation coordination
- [ ] Lock cleanup on process termination
- [ ] Stale lock detection and cleanup
- [ ] Windows/Linux cross-platform compatibility
- [ ] Nova start/stop commands work correctly
- [ ] Background monitoring functionality
- [ ] NovaLocks directory creation and permissions

## Contributing

When adding new features:

1. Write unit tests first (TDD approach)
2. Add integration tests for complex scenarios
3. Update this README with new test descriptions
4. Ensure all tests pass before submitting changes

Run `python -m pytest tests/ -v` to verify all tests pass.