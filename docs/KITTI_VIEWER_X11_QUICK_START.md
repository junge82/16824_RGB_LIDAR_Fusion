# KITTI Viewer Quick Start for X11 (Ubuntu 22.04)

Simple guide for using kitti_viewer with X11 display server on Ubuntu 22.04.

## Quick Setup for X11

### 1. Check Your Display Server

```bash
# Check if you're using X11
echo $XDG_SESSION_TYPE
# Should output: x11

# Check DISPLAY variable
echo $DISPLAY
# Should output something like: :0 or :1
```

### 2. Install Dependencies (One Command)

```bash
# Install everything needed for X11
sudo apt-get update && sudo apt-get install -y \
    python3-pyqt5 \
    python3-opengl \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libgl1-mesa-glx

# Install Python packages
pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5
```

### 3. Set Environment Variable (X11)

```bash
# For X11, use xcb platform
export QT_QPA_PLATFORM=xcb

# Add to ~/.bashrc for permanent setting
echo 'export QT_QPA_PLATFORM=xcb' >> ~/.bashrc
source ~/.bashrc
```

## Running the Viewer

### Option 1: Use the X11-specific script

```bash
# Simple - just run it
python3 example_kitti_viewer_x11.py

# Visualize specific sample
python3 example_kitti_viewer_x11.py --idx 5

# Custom KITTI directory
python3 example_kitti_viewer_x11.py --root /path/to/kitti --idx 10
```

### Option 2: Use the universal script (auto-detects X11)

```bash
# The Wayland script also works with X11 - it auto-detects!
python3 example_kitti_viewer_wayland.py --idx 0
```

### Option 3: Force X11 mode inline

```bash
# Set environment variable inline
QT_QPA_PLATFORM=xcb python3 your_script.py
```

## Simple Python Example for X11

```python
#!/usr/bin/env python3
import os
import sys

# Force X11 backend
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Add project to path
sys.path.insert(0, '16824_RGB_LIDAR_Fusion')

from utils.kitti_viewer import (
    load_velo_scan,
    read_label,
    Calibration,
    show_lidar_with_boxes
)

# Set your paths
idx = 0
root = './kitti_object/training'

# Load data
pc_velo = load_velo_scan(f'{root}/velodyne/{idx:06d}.bin')
objects = read_label(f'{root}/label_2/{idx:06d}.txt')
calib = Calibration(f'{root}/calib/{idx:06d}.txt')

# Visualize (opens 3D window)
show_lidar_with_boxes(pc_velo, objects, calib)
```

Save as `simple_x11_viewer.py` and run:
```bash
python3 simple_x11_viewer.py
```

## X11-Specific Troubleshooting

### Issue: "Could not connect to display"

```bash
# Check DISPLAY is set
echo $DISPLAY

# If empty, set it
export DISPLAY=:0

# Check X11 is running
ps aux | grep X
```

### Issue: "xcb plugin not found"

```bash
# Install XCB libraries
sudo apt-get install -y \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0
```

### Issue: Permission denied

```bash
# Allow local connections
xhost +local:

# Or for specific user
xhost +SI:localuser:$(whoami)
```

### Issue: Black/empty window

```bash
# Check OpenGL
glxinfo | grep "OpenGL version"

# If not installed
sudo apt-get install mesa-utils

# Test with simple OpenGL app
glxgears
```

## Differences: X11 vs Wayland

| Feature | X11 | Wayland |
|---------|-----|---------|
| Environment Variable | `QT_QPA_PLATFORM=xcb` | `QT_QPA_PLATFORM=wayland` |
| Stability | More stable, older | Newer, some issues |
| Performance | Good | Better (in theory) |
| Compatibility | Excellent | Good |
| Remote Display | Easy (X forwarding) | Limited |

## When to Use X11 Instead of Wayland

Use X11 if you experience:
- ❌ Black or empty windows with Wayland
- ❌ Crashes or freezes
- ❌ Missing window decorations
- ❌ Need remote display (SSH X forwarding)
- ❌ Using older NVIDIA drivers

## Switching Between X11 and Wayland

### Temporary (current session only)

```bash
# Switch to X11
export QT_QPA_PLATFORM=xcb

# Switch to Wayland
export QT_QPA_PLATFORM=wayland
```

### Permanent (login session)

```bash
# At login screen, click gear icon
# Select "Ubuntu on Xorg" for X11
# Or "Ubuntu" for Wayland
```

## Complete Working Example

```bash
# 1. Install dependencies
sudo apt-get install -y python3-pyqt5 python3-opengl libxcb-xinerama0
pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5

# 2. Set X11 mode
export QT_QPA_PLATFORM=xcb

# 3. Download KITTI data (if not already done)
# Visit: http://www.cvlibs.net/datasets/kitti/eval_object.php

# 4. Run viewer
python3 example_kitti_viewer_x11.py --idx 0

# 5. Interact with 3D view
# - Left mouse: rotate
# - Right mouse: pan
# - Scroll: zoom
```

## Remote Display via SSH (X11 Only)

```bash
# On remote machine
ssh -X user@remote-host

# Set X11 mode
export QT_QPA_PLATFORM=xcb

# Run viewer (display shows on local machine)
python3 example_kitti_viewer_x11.py
```

Note: Wayland doesn't support X forwarding easily!

## Performance Tips for X11

```bash
# 1. Disable compositing (if using a compositor)
# For GNOME: Alt+F2, type 'r', press Enter

# 2. Use hardware acceleration
export LIBGL_ALWAYS_SOFTWARE=0

# 3. For NVIDIA GPUs
export __GLX_VENDOR_LIBRARY_NAME=nvidia
```

## Verification Commands

```bash
# Verify X11 setup
echo "Display: $DISPLAY"
echo "Session: $XDG_SESSION_TYPE"
echo "Qt Platform: $QT_QPA_PLATFORM"

# Test X11 works
xclock &  # Should show a clock window

# Test OpenGL
glxgears  # Should show rotating gears

# Test Qt
python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('Qt OK')"
```

## Summary Commands

```bash
# Complete one-liner setup for X11
export QT_QPA_PLATFORM=xcb && \
pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5 && \
python3 example_kitti_viewer_x11.py --idx 0
```

---

**TL;DR for X11 users:**
1. `export QT_QPA_PLATFORM=xcb`
2. `pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5`
3. `python3 example_kitti_viewer_x11.py`

That's it! 🎉