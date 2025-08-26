# Nova ⭐

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, open-source CAD file locking system for team collaboration. Prevent conflicts when multiple engineers work with CAD files simultaneously.

## 🎯 What is Nova?

Nova is a lightweight file locking system designed specifically for CAD files (SolidWorks, Inventor, AutoCAD, etc.). It prevents file conflicts by automatically creating locks when files are opened and removing them when closed.

### Key Features

- **🔒 Automatic Locking**: Monitors CAD processes and automatically locks/unlocks files
- **🌐 Web Dashboard**: Real-time web interface to monitor all locks across the network
- **⚡ Lightweight**: No complex setup or expensive licensing
- **🛡️ Secure**: User-based permissions and stale lock cleanup
- **📱 Modern UI**: Beautiful, responsive web dashboard with real-time updates
- **🔧 Flexible**: Support for multiple CAD applications and file formats

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/nova.git
cd nova

# Install dependencies
pip install -e .

# Or install from PyPI (when available)
pip install nova
```

### Basic Usage

#### 1. Start the Dashboard (Server)

```bash
# Start the web dashboard
nova dashboard --lock-dir ./locks --host 0.0.0.0 --port 5000
```

Open your browser to `http://localhost:5000` to view the dashboard.

#### 2. Start File Monitoring (Each CAD Computer)

```bash
# Start automatic file monitoring
nova monitor --lock-dir ./locks

# The monitor will automatically:
# - Lock files when opened in CAD software
# - Unlock files when closed
# - Clean up stale locks
```

#### 3. Manual Operations

```bash
# Manually lock a file
nova lock "path/to/file.sldprt" --lock-dir ./locks

# Check if a file is locked
nova check "path/to/file.sldprt" --lock-dir ./locks

# Unlock a file
nova unlock "path/to/file.sldprt" --lock-dir ./locks

# Unlock all files for current user
nova unlock-all --lock-dir ./locks

# List all active locks
nova list --lock-dir ./locks

# Clean up stale locks
nova cleanup --lock-dir ./locks --max-age 24
```

## 🏗️ Architecture

```
Nova System
├── Core Lock Manager
│   ├── Lock creation/removal
│   ├── Stale lock cleanup
│   └── File validation
├── File Monitor
│   ├── Process monitoring
│   ├── Automatic lock/unlock
│   └── CAD process detection
├── Web Dashboard
│   ├── Real-time monitoring
│   ├── Lock management
│   └── Statistics
└── CLI Interface
    ├── Manual operations
    ├── Monitoring control
    └── System management
```

## 📋 Supported CAD Applications

- **SolidWorks** (.sldprt, .sldasm, .slddrw)
- **Inventor** (.ipt, .iam, .idw)
- **AutoCAD** (.dwg, .dxf)
- **Pro/Engineer & Creo** (.prt, .asm, .drw)
- **Fusion 360** (.f3d, .f3z)
- **Siemens NX** (.prt, .asm)
- **CATIA** (.CATPart, .CATProduct)
- **Neutral Formats** (.step, .stp, .iges, .igs)

## 🌐 Network Setup

### Single Network Share

For small teams, use a shared network folder:

```bash
# On server computer
nova dashboard --lock-dir "\\\\server\\shared\\nova\\locks"

# On each CAD computer
nova monitor --lock-dir "\\\\server\\shared\\nova\\locks"
```

### Multiple Locations

For distributed teams, use cloud storage (Google Drive, Dropbox, etc.):

```bash
# All computers use the same cloud-synced folder
nova monitor --lock-dir "C:\\GoogleDrive\\Nova\\locks"
```

## 🔧 Configuration

### Environment Variables

```bash
# Dashboard secret key (optional)
export NOVA_SECRET_KEY="your-secret-key"

# Logging level
export NOVA_LOG_LEVEL="INFO"
```

### Custom CAD Processes

You can customize which processes to monitor:

```python
from nova.monitor import FileMonitor
from nova.core import LockManager

lock_manager = LockManager("./locks")
monitor = FileMonitor(
    lock_manager,
    cad_processes=[
        'SLDWORKS.exe',      # SolidWorks
        'Inventor.exe',      # Inventor
        'acad.exe',          # AutoCAD
        'my-custom-cad.exe'  # Custom CAD application
    ]
)
```

## 📊 Web Dashboard Features

- **Real-time Updates**: Live lock status with WebSocket connections
- **Statistics**: Total locks, active users, computers, file types
- **Filtering**: Filter by user, computer, or search file paths
- **Lock Management**: Remove locks directly from the dashboard
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Development

### Project Structure

```
nova/
├── core/           # Core locking functionality
├── monitor/        # File monitoring system
├── web/           # Web dashboard
├── cli/           # Command-line interface
└── tests/         # Test suite
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=nova
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔒 Security Considerations

- **User Permissions**: Only the user who created a lock can remove it
- **Stale Lock Cleanup**: Automatic removal of locks older than 24 hours
- **Process Validation**: Locks are tied to specific process IDs
- **Network Security**: Dashboard can be secured with authentication

## 📈 Performance

- **Lightweight**: Minimal CPU and memory usage
- **Efficient**: File system-based locking with JSON metadata
- **Scalable**: Supports hundreds of concurrent users
- **Fast**: Sub-second lock creation and removal


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the original [CADLock project](https://github.com/Cosmic-Robotics/CADLock)
- Built with modern Python technologies
- Uses Flask and Socket.IO for real-time web interface

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/nova/issues)
- **Documentation**: [Read the Docs](https://nova.readthedocs.io/)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/nova/discussions)

---

**Nova** - Making CAD collaboration simple and conflict-free! ⭐✨
