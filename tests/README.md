# 🧪 Nova Test Suite

This directory contains tests and demonstrations for the Nova CAD lock system.

## Test Files

### **Unit Tests**
- `test_lock_manager.py` - Unit tests for the LockManager class
- `test_file_monitor.py` - Unit tests for file monitoring (TODO)
- `test_dashboard.py` - Unit tests for web dashboard (TODO)

### **Demonstrations**
- `demo_lock_conflict.py` - Interactive demo showing what happens when users try to open locked files

### **Integration Tests**
- `test_multi_user.py` - Multi-user scenarios (TODO)
- `test_network_storage.py` - Network storage integration (TODO)

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
- ✅ Successful lock creation
- ✅ Lock conflict detection
- ✅ Lock removal by owner
- ✅ Prevention of removal by wrong user
- ✅ CAD file type detection
- ✅ Multiple lock management

### **Lock Conflict Demo**
- ✅ First user opens file successfully
- ✅ Second user gets lock conflict error
- ✅ Clear error message with user/computer info
- ✅ Lock release and subsequent access
- ✅ Read-only mode explanation

### **Planned Tests (TODO)**
- File monitoring automation
- Dashboard API endpoints
- WebSocket real-time updates
- Network storage scenarios
- Performance under load
- Error recovery scenarios

## Test Environment Setup

The tests use temporary directories and don't require actual network storage or CAD software. This makes them safe to run on any development machine.

**Test Structure:**
```
tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This file
├── test_lock_manager.py        # Lock manager unit tests
├── demo_lock_conflict.py       # Interactive lock conflict demo
└── fixtures/                   # Test data files (if needed)
```

## Manual Testing Checklist

For full system testing, manually verify:

- [ ] Network storage accessibility
- [ ] CAD software integration (SolidWorks, AutoCAD, etc.)
- [ ] Dashboard web interface
- [ ] Multi-workstation coordination
- [ ] Lock cleanup on process termination
- [ ] Stale lock detection and cleanup
- [ ] Windows/Linux cross-platform compatibility

## Contributing

When adding new features:

1. Write unit tests first (TDD approach)
2. Add integration tests for complex scenarios
3. Update this README with new test descriptions
4. Ensure all tests pass before submitting changes

Run `python -m pytest tests/ -v` to verify all tests pass.