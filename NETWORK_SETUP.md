# Nova Shared Lock Directory (CADLock Style)

Nova uses a shared network directory for storing CAD file locks, similar to CADLock's approach. This ensures proper team collaboration with rich analytics and activity tracking.

## Lock Directory Detection

Nova automatically detects shared network locations in this order:

**Windows:**
1. `NOVA_LOCKS_DIR` environment variable
2. `\\server\shared\Nova\Locks`
3. `G:\Shared drives\Engineering\Nova\Locks`
4. `C:\Shared\Nova\Locks`
5. `Z:\Nova\Locks`

**Linux/Mac:**
1. `NOVA_LOCKS_DIR` environment variable
2. `/mnt/shared/nova/locks`
3. `/shared/nova/locks`
4. `/network/nova/locks`

## Why Shared Network Directory?

Like CADLock, Nova uses shared storage for:
- ✅ All team members see the same locks instantly
- ✅ Real-time conflict prevention across the network
- ✅ Rich analytics and activity tracking
- ✅ Cloud/network drive compatibility
- ✅ Centralized team collaboration

## Automatic Directory Creation

Nova automatically:
1. Creates the lock directory if it doesn't exist
2. Verifies write permissions
3. Exits with error if directory cannot be created/accessed

No setup required - Nova handles everything automatically.

## Requirements

For proper team collaboration:
- ✅ All team members must have **read/write access** to the fixed directory
- ✅ Directory must be **accessible from all workstations**
- ⚠️  May require administrator privileges to create system directories

## Installation

### Team Setup (Recommended)
1. **Set shared directory**: `export NOVA_LOCKS_DIR="\\server\shared\Nova\Locks"`
2. **Ensure permissions**: All team members need read/write access
3. **Test**: Run `nova list` on each machine to verify access

### Auto-Detection Setup
1. Create one of the standard paths (Windows: `G:\Shared drives\Engineering\Nova\Locks`)
2. Nova will auto-detect and use it
3. All team members must have access to the same path

## Testing Your Setup

```bash
# Check if Nova can access the shared directory
nova list

# View rich analytics
nova analytics

# Test from different machines
nova lock "/path/to/test/file.sldprt"
nova list  # Should show detailed lock info on all machines
nova unlock "/path/to/test/file.sldprt"
```

## Troubleshooting

### "Cannot initialize Nova lock directory" Error
- **Windows**: Run as administrator to create `C:\NovaLocks`
- **Linux/Mac**: Run with sudo: `sudo nova monitor`

### "Permission denied" Errors
- Ensure all users have read/write access to the lock directory
- May need to adjust folder permissions after creation

---

*Nova automatically handles lock directory creation and management - no manual configuration needed.*