# Qt Platform Plugin Troubleshooting Guide

## Problem: "no Qt platform plugin could be initialized"

This error occurs when PyQt5 cannot find or load the required Qt platform plugins, specifically the XCB (X11) plugin on Linux systems.

## Quick Fix (Most Common Solution)

For **local Linux machines with a display**, run:

```bash
# Navigate to project directory
cd 16824_RGB_LIDAR_Fusion

# Run the fix script
sudo bash scripts/fix_qt_dependencies.sh

# Activate conda environment
conda activate rgb-fusion

# Test the fix
python scripts/test_qt.py
```

## Diagnostic Steps

### 1. Run Diagnostic Script

```bash
bash scripts/diagnose_qt.sh
```

This will check:
- Display configuration
- Qt plugin paths
- Missing system libraries
- Package installation status

### 2. Manual Diagnosis

Check if DISPLAY is set:
```bash
echo $DISPLAY
# Should output something like ":0" or ":1"
```

Check Qt plugin paths:
```bash
conda activate rgb-fusion
python -c "from PyQt5.QtCore import QCoreApplication; print(QCoreApplication.libraryPaths())"
```

Check for XCB plugin:
```bash
find ~/anaconda3/envs/rgb-fusion -name "libqxcb.so" 2>/dev/null
```

## Solutions by Environment Type

### Local Linux Machine (Desktop/Laptop)

**Install missing Qt dependencies:**

```bash
sudo apt-get update
sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxkbcommon-x11-0 \
    libxcb-xkb1 \
    libxcb-xfixes0 \
    libxcb-util1
```

### Remote Server / Headless System

**Option 1: Use offscreen rendering**
```bash
export QT_QPA_PLATFORM=offscreen
python your_script.py
```

**Option 2: Use Xvfb (virtual framebuffer)**
```bash
sudo apt-get install xvfb
xvfb-run -a python your_script.py
```

**Option 3: Modify matplotlib backend**
```python
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
```

### SSH Session

**Enable X11 forwarding:**
```bash
# Connect with X11 forwarding
ssh -X user@remote-host

# Or set DISPLAY
export DISPLAY=:0
```

### WSL2 (Windows Subsystem for Linux)

**Install VcXsrv or X410:**
1. Install VcXsrv on Windows
2. Launch XLaunch with "Disable access control" checked
3. In WSL2:
```bash
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
export LIBGL_ALWAYS_INDIRECT=1
```

## Common Error Messages and Solutions

### Error: "Could not load the Qt platform plugin 'xcb'"

**Cause:** Missing XCB libraries

**Solution:**
```bash
sudo apt-get install libxcb-xinerama0 libxcb-cursor0
```

### Error: "qt.qpa.plugin: Could not find the Qt platform plugin 'xcb' in ''"

**Cause:** Qt plugin path not set correctly

**Solution:**
```bash
export QT_PLUGIN_PATH=$CONDA_PREFIX/plugins
```

### Error: "This application failed to start because no Qt platform plugin could be initialized"

**Cause:** Multiple possible causes

**Solutions:**
1. Install missing dependencies (see above)
2. Check DISPLAY variable
3. Verify Qt installation in conda environment
4. Try offscreen rendering

### Error: "qt.qpa.xcb: could not connect to display"

**Cause:** No X server running or DISPLAY not set

**Solutions:**
```bash
# Check if X server is running
ps aux | grep X

# Set DISPLAY
export DISPLAY=:0

# Or use offscreen mode
export QT_QPA_PLATFORM=offscreen
```

## Debugging Tips

### Enable Qt Debug Output

```bash
export QT_DEBUG_PLUGINS=1
python your_script.py
```

This will show detailed information about which plugins Qt is trying to load and why they're failing.

### Check Library Dependencies

```bash
# Find the XCB plugin
XCB_PLUGIN=$(find $CONDA_PREFIX -name "libqxcb.so" | head -1)

# Check its dependencies
ldd $XCB_PLUGIN
```

Look for any libraries marked as "not found".

### Verify Conda Environment

```bash
conda activate rgb-fusion
conda list | grep -E "pyqt|qt"
```

Should show:
- pyqt=5.12.3
- qt=5.12.9
- pyqt5-sip
- pyqtgraph

## Alternative Visualization Methods

If Qt issues persist, consider these alternatives:

### 1. Save Visualizations to Files

Instead of displaying windows, save to image files:

```python
import matplotlib.pyplot as plt
matplotlib.use('Agg')  # Set before importing pyplot

# Your plotting code
plt.savefig('output.png')
# Don't use plt.show()
```

### 2. Use Jupyter Notebook

Jupyter notebooks handle visualization differently:

```bash
conda activate rgb-fusion
pip install jupyter
jupyter notebook
```

### 3. Use Web-Based Visualization

Tools like Plotly or Bokeh create web-based visualizations:

```bash
pip install plotly
```

## Testing Your Fix

After applying any solution, test with:

```bash
# Basic Qt test
python scripts/test_qt.py

# Test with actual viewer
python -c "from utils.kitti_viewer import show_lidar_with_boxes; print('Import successful')"
```

## Environment-Specific Setup Scripts

### Add to ~/.bashrc for Persistent Configuration

```bash
# For local machine
export QT_QPA_PLATFORM=xcb

# For headless server
export QT_QPA_PLATFORM=offscreen

# For WSL2
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
export LIBGL_ALWAYS_INDIRECT=1
```

## Still Having Issues?

1. **Check system logs:**
   ```bash
   dmesg | grep -i qt
   journalctl -xe | grep -i qt
   ```

2. **Reinstall PyQt5 in conda environment:**
   ```bash
   conda activate rgb-fusion
   conda remove pyqt qt
   conda install pyqt=5.12.3 qt=5.12.9
   ```

3. **Try a minimal test:**
   ```python
   from PyQt5.QtWidgets import QApplication
   import sys
   app = QApplication(sys.argv)
   print("Success!")
   ```

4. **Check for conflicting Qt installations:**
   ```bash
   which qmake
   qmake -version
   ```

## Additional Resources

- [Qt Platform Plugin Documentation](https://doc.qt.io/qt-5/qpa.html)
- [PyQt5 Installation Guide](https://www.riverbankcomputing.com/static/Docs/PyQt5/installation.html)
- [Conda Qt Packages](https://anaconda.org/conda-forge/qt)

## Summary of Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `diagnose_qt.sh` | Identify missing dependencies | `bash scripts/diagnose_qt.sh` |
| `fix_qt_dependencies.sh` | Install required packages | `sudo bash scripts/fix_qt_dependencies.sh` |
| `test_qt.py` | Verify Qt is working | `python scripts/test_qt.py` |

---

**Last Updated:** 2026-04-16  
**Tested On:** Ubuntu 18.04, 20.04, 22.04