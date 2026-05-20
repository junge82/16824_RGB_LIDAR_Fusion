# Fix: Qt Platform Plugin "xcb" Could Not Be Loaded

## The Problem

You're seeing this error:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in 
"/home/gergo/anaconda3/envs/kitti_env/lib/python3.11/site-packages/cv2/qt/plugins" 
even though it was found.
```

**Root Cause:** OpenCV (cv2) bundles its own Qt plugins that conflict with PyQt5's plugins in conda environments.

## Quick Fix (Recommended)

### Option 1: Automated Fix Script

```bash
# Make the script executable
chmod +x fix_qt_opencv_conflict.sh

# Run the fix
./fix_qt_opencv_conflict.sh

# Reactivate your conda environment
conda deactivate
conda activate kitti_env

# Test it works
python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('Qt OK')"
```

### Option 2: Manual Fix (3 Steps)

```bash
# 1. Remove OpenCV's Qt plugins
rm -rf ~/anaconda3/envs/kitti_env/lib/python*/site-packages/cv2/qt/plugins

# 2. Set Qt plugin path to system location
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins

# 3. Run your script
python3 example_kitti_viewer_x11.py
```

### Option 3: Use OpenCV Headless (Best for Production)

```bash
# Uninstall regular OpenCV
pip uninstall opencv-python opencv-contrib-python

# Install headless version (no Qt bundled)
pip install opencv-python-headless

# Install PyQt5 separately
pip install PyQt5

# Now run your script
python3 example_kitti_viewer_x11.py
```

## Permanent Solution

Add these lines to your conda environment activation script:

```bash
# Create activation script directory
mkdir -p ~/anaconda3/envs/kitti_env/etc/conda/activate.d

# Create the fix script
cat > ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_fix.sh << 'EOF'
#!/bin/bash
# Remove OpenCV Qt plugins from path
export QT_PLUGIN_PATH=$(echo $QT_PLUGIN_PATH | sed 's|[^:]*cv2[^:]*:||g')
# Use system Qt plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
# Set platform
export QT_QPA_PLATFORM=xcb
EOF

chmod +x ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_fix.sh
```

Now every time you activate the environment, Qt will be configured correctly!

## Alternative Workarounds

### Workaround 1: Set Environment Variables Before Running

```bash
# Create a wrapper script
cat > run_kitti_viewer.sh << 'EOF'
#!/bin/bash
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
export QT_QPA_PLATFORM=xcb
unset QT_PLUGIN_PATH
python3 "$@"
EOF

chmod +x run_kitti_viewer.sh

# Use it
./run_kitti_viewer.sh example_kitti_viewer_x11.py --idx 0
```

### Workaround 2: Modify Python Script

Add this at the very beginning of your Python script (before any imports):

```python
import os
import sys

# Fix Qt plugin conflict
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/usr/lib/x86_64-linux-gnu/qt5/plugins'
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Remove cv2 from Qt plugin path if present
qt_plugin_path = os.environ.get('QT_PLUGIN_PATH', '')
if 'cv2' in qt_plugin_path:
    paths = [p for p in qt_plugin_path.split(':') if 'cv2' not in p]
    os.environ['QT_PLUGIN_PATH'] = ':'.join(paths)

# Now import Qt and other modules
from PyQt5.QtWidgets import QApplication
import cv2
# ... rest of your imports
```

### Workaround 3: Use System Python Instead of Conda

```bash
# Deactivate conda
conda deactivate

# Use system Python with venv
python3 -m venv kitti_venv
source kitti_venv/bin/activate

# Install packages
pip install numpy opencv-python-headless pyqtgraph PyOpenGL PyQt5

# Run script
python3 example_kitti_viewer_x11.py
```

## Verification Steps

After applying any fix, verify it works:

```bash
# Test 1: Check Qt can be imported
python3 -c "from PyQt5.QtWidgets import QApplication; print('✓ PyQt5 OK')"

# Test 2: Check OpenCV works
python3 -c "import cv2; print('✓ OpenCV OK')"

# Test 3: Check both together
python3 -c "from PyQt5.QtWidgets import QApplication; import cv2; import sys; app = QApplication(sys.argv); print('✓ Both OK')"

# Test 4: Check OpenGL
python3 -c "from OpenGL.GL import *; print('✓ OpenGL OK')"

# Test 5: Check pyqtgraph
python3 -c "import pyqtgraph as pg; print('✓ pyqtgraph OK')"
```

## Debug Mode

If you still have issues, enable Qt debug mode:

```bash
export QT_DEBUG_PLUGINS=1
python3 example_kitti_viewer_x11.py
```

This will show detailed information about which plugins Qt is trying to load.

## Understanding the Issue

The problem occurs because:

1. **OpenCV** (cv2) includes its own Qt libraries and plugins
2. **PyQt5** also has Qt libraries and plugins
3. When both are installed in conda, they conflict
4. The cv2 Qt plugins are incompatible with PyQt5

The solution is to either:
- Remove cv2's Qt plugins (use system Qt)
- Use opencv-python-headless (no Qt bundled)
- Properly configure QT_PLUGIN_PATH to exclude cv2

## System-Specific Paths

Your Qt plugins might be in different locations:

```bash
# Find system Qt plugins
find /usr -name "libqxcb.so" 2>/dev/null

# Common locations:
# Ubuntu/Debian: /usr/lib/x86_64-linux-gnu/qt5/plugins
# Fedora/RHEL: /usr/lib64/qt5/plugins
# Arch: /usr/lib/qt/plugins
```

Use the correct path for your system in `QT_QPA_PLATFORM_PLUGIN_PATH`.

## Still Not Working?

If none of the above works, try this nuclear option:

```bash
# 1. Create fresh conda environment
conda create -n kitti_clean python=3.11
conda activate kitti_clean

# 2. Install packages in specific order
pip install numpy
pip install opencv-python-headless  # Headless version!
pip install PyQt5
pip install pyqtgraph PyOpenGL

# 3. Test
python3 example_kitti_viewer_x11.py
```

## Summary

**Fastest Fix:**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
python3 example_kitti_viewer_x11.py
```

**Most Reliable Fix:**
```bash
./fix_qt_opencv_conflict.sh
conda deactivate && conda activate kitti_env
python3 example_kitti_viewer_x11.py
```

Choose the one that works best for your setup! 🎉