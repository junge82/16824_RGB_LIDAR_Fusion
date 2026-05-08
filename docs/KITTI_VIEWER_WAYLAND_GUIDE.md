# KITTI Viewer Guide for Ubuntu 22.04 Wayland

Complete guide for visualizing KITTI dataset 3D point clouds and bounding boxes on Ubuntu 22.04 with Wayland display server.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Wayland Configuration](#wayland-configuration)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## Prerequisites

### System Requirements
- Ubuntu 22.04 LTS (or compatible)
- Wayland display server (default on Ubuntu 22.04)
- Python 3.8 or higher
- OpenGL support

### Check Your Display Server
```bash
# Check if you're running Wayland
echo $XDG_SESSION_TYPE
# Should output: wayland
```

---

## Installation

### 1. Install System Dependencies

```bash
# Update package list
sudo apt-get update

# Install Qt5 and OpenGL dependencies
sudo apt-get install -y \
    python3-pyqt5 \
    python3-opengl \
    qtwayland5 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libgl1-mesa-glx \
    libglu1-mesa

# For NVIDIA GPU users (optional but recommended)
sudo apt-get install -y nvidia-utils-XXX  # Replace XXX with your driver version
```

### 2. Install Python Dependencies

```bash
# Using pip
pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5

# Or using conda
conda install numpy opencv pyqtgraph pyopengl pyqt
```

### 3. Verify Installation

```bash
# Test PyQt5 with Wayland
python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('PyQt5 OK')"

# Test OpenGL
python3 -c "from OpenGL.GL import *; print('OpenGL OK')"

# Test pyqtgraph
python3 -c "import pyqtgraph as pg; print('pyqtgraph OK')"
```

---

## Wayland Configuration

### Environment Variables

For optimal Wayland compatibility, set these environment variables:

```bash
# Add to ~/.bashrc or ~/.profile for permanent configuration
export QT_QPA_PLATFORM=wayland
export QT_AUTO_SCREEN_SCALE_FACTOR=1
export QT_WAYLAND_DISABLE_WINDOWDECORATION=0
export QT_XCB_GL_INTEGRATION=xcb_egl

# Apply changes
source ~/.bashrc
```

### Alternative: X11 Fallback

If you encounter issues with Wayland, you can force X11 mode:

```bash
# Temporary (for current session)
export QT_QPA_PLATFORM=xcb

# Or run with the environment variable
QT_QPA_PLATFORM=xcb python3 example_kitti_viewer_wayland.py
```

---

## Quick Start

### 1. Download KITTI Dataset

```bash
# Create directory structure
mkdir -p kitti_object/training/{velodyne,label_2,calib,image_2}
mkdir -p kitti_object/testing/{velodyne,calib,image_2}

# Download from KITTI website:
# http://www.cvlibs.net/datasets/kitti/eval_object.php
# 
# Required files:
# - data_object_velodyne.zip (29 GB) - Velodyne point clouds
# - data_object_label_2.zip (5 MB) - Training labels
# - data_object_calib.zip (16 MB) - Calibration files
# - data_object_image_2.zip (12 GB) - Left color images

# Extract to kitti_object directory
```

### 2. Run the Example Script

```bash
# Make the script executable
chmod +x example_kitti_viewer_wayland.py

# Run with default settings (visualizes sample 0)
python3 example_kitti_viewer_wayland.py

# Verify data without visualization
python3 example_kitti_viewer_wayland.py --verify-only

# Visualize a specific sample
python3 example_kitti_viewer_wayland.py --idx 5

# Use custom KITTI directory
python3 example_kitti_viewer_wayland.py --root /path/to/kitti --idx 10
```

---

## Usage Examples

### Example 1: Basic Visualization

```python
#!/usr/bin/env python3
import os
import sys

# Configure for Wayland
os.environ['QT_QPA_PLATFORM'] = 'wayland'

# Add project to path
sys.path.insert(0, '16824_RGB_LIDAR_Fusion')

from utils.kitti_viewer import (
    load_velo_scan,
    read_label,
    Calibration,
    show_lidar_with_boxes
)

# Load data
idx = 0
root = './kitti_object/training'

pc_velo = load_velo_scan(f'{root}/velodyne/{idx:06d}.bin')
objects = read_label(f'{root}/label_2/{idx:06d}.txt')
calib = Calibration(f'{root}/calib/{idx:06d}.txt')

# Visualize
show_lidar_with_boxes(pc_velo, objects, calib)
```

### Example 2: Visualize with Predictions

```python
from utils.kitti_viewer import show_lidar_with_boxes, Object3d

# Load ground truth
objects_gt = read_label('path/to/label.txt')

# Create prediction objects (example)
pred_data = [
    [0, 0, 0, 0, 100, 100, 200, 200, 1.5, 1.8, 4.0, 0, 0, 10, 0],  # Car
]
objects_pred = [Object3d(pred, from_file=False) for pred in pred_data]

# Visualize: GT in red, predictions in green
show_lidar_with_boxes(pc_velo, objects_gt, calib, preds=objects_pred)
```

### Example 3: Batch Processing

```python
import glob

# Process multiple samples
kitti_root = './kitti_object/training'
velodyne_files = sorted(glob.glob(f'{kitti_root}/velodyne/*.bin'))

for velo_file in velodyne_files[:10]:  # First 10 samples
    idx = int(os.path.basename(velo_file).split('.')[0])
    
    pc_velo = load_velo_scan(velo_file)
    objects = read_label(f'{kitti_root}/label_2/{idx:06d}.txt')
    calib = Calibration(f'{kitti_root}/calib/{idx:06d}.txt')
    
    print(f"Visualizing sample {idx:06d}")
    show_lidar_with_boxes(pc_velo, objects, calib)
```

### Example 4: Custom Visualization with Training Data

```python
from utils.kitti_viewer import draw_3d_output, draw_2d_output

# From PyTorch training loop
for batch_idx, (images, lidar, labels, calib) in enumerate(dataloader):
    # Visualize 3D point cloud with boxes
    draw_3d_output(
        lidar[0].cpu().numpy(),
        labels[0].numpy().tolist(),
        calib[0]
    )
    
    # Visualize 2D image with projected boxes
    draw_2d_output(
        images[0].cpu().permute(1, 2, 0).numpy(),
        labels[0].numpy().tolist(),
        calib[0]
    )
```

---

## Troubleshooting

### Issue 1: "Could not connect to display"

**Solution:**
```bash
# Check Wayland is running
echo $WAYLAND_DISPLAY
# Should output something like: wayland-0

# If empty, restart your session or try X11
export QT_QPA_PLATFORM=xcb
```

### Issue 2: Black/Empty Window

**Symptoms:** Window opens but shows nothing or is black.

**Solutions:**
```bash
# 1. Check OpenGL support
glxinfo | grep "OpenGL version"

# 2. Try software rendering
export LIBGL_ALWAYS_SOFTWARE=1
python3 example_kitti_viewer_wayland.py

# 3. Update graphics drivers
sudo ubuntu-drivers autoinstall
```

### Issue 3: "ImportError: No module named 'OpenGL'"

**Solution:**
```bash
# Install PyOpenGL
pip install PyOpenGL PyOpenGL-accelerate

# Or with conda
conda install pyopengl
```

### Issue 4: Slow Performance

**Solutions:**
```bash
# 1. Enable hardware acceleration
export LIBGL_ALWAYS_SOFTWARE=0

# 2. For NVIDIA GPUs
nvidia-smi  # Check GPU is detected
export __GLX_VENDOR_LIBRARY_NAME=nvidia

# 3. Reduce point cloud density
# In your code, subsample the point cloud:
pc_velo = pc_velo[::2]  # Use every 2nd point
```

### Issue 5: "xcb plugin error"

**Solution:**
```bash
# Install missing xcb libraries
sudo apt-get install -y \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0
```

### Issue 6: Window Decorations Missing

**Solution:**
```bash
# Enable window decorations
export QT_WAYLAND_DISABLE_WINDOWDECORATION=0

# Or use a different compositor
# For GNOME users:
gsettings set org.gnome.mutter experimental-features "['scale-monitor-framebuffer']"
```

---

## Advanced Usage

### Custom Point Cloud Colors

```python
from utils.kitti_viewer import plot3d, inte_to_rgb

p3d = plot3d()

# Color by intensity
pc_color = inte_to_rgb(pc_velo[:, 3])
p3d.add_points(pc_velo[:, 0:3], pc_color)

# Or custom colors (RGBA)
custom_colors = np.ones((len(pc_velo), 4))
custom_colors[:, 0] = 1.0  # Red channel
custom_colors[:, 1] = 0.5  # Green channel
custom_colors[:, 2] = 0.0  # Blue channel
p3d.add_points(pc_velo[:, 0:3], custom_colors)

p3d.show()
```

### Interactive Controls

When the 3D viewer window is open:

- **Left Mouse Button + Drag**: Rotate view
- **Right Mouse Button + Drag**: Pan view
- **Mouse Wheel**: Zoom in/out
- **Middle Mouse Button**: Reset view
- **ESC or Close Window**: Exit

### Keyboard Shortcuts (if implemented)

- `R`: Reset view
- `S`: Save screenshot
- `H`: Toggle help
- `Q`: Quit

### Performance Optimization

```python
# Subsample point cloud for faster rendering
def subsample_pointcloud(pc, factor=2):
    """Keep every 'factor' points"""
    return pc[::factor]

# Filter by distance
def filter_by_distance(pc, max_dist=50.0):
    """Keep only points within max_dist meters"""
    distances = np.sqrt(np.sum(pc[:, :3]**2, axis=1))
    return pc[distances < max_dist]

# Apply filters
pc_velo = subsample_pointcloud(pc_velo, factor=2)
pc_velo = filter_by_distance(pc_velo, max_dist=50.0)
```

---

## Additional Resources

### KITTI Dataset
- Official website: http://www.cvlibs.net/datasets/kitti/
- Paper: http://www.cvlibs.net/publications/Geiger2013IJRR.pdf
- Development kit: https://github.com/bostondiditeam/kitti

### PyQtGraph Documentation
- Official docs: https://pyqtgraph.readthedocs.io/
- OpenGL examples: https://pyqtgraph.readthedocs.io/en/latest/3dgraphics/

### Wayland Resources
- Wayland documentation: https://wayland.freedesktop.org/
- Qt Wayland: https://doc.qt.io/qt-5/qpa.html

---

## Common Command Reference

```bash
# Check system info
uname -a
echo $XDG_SESSION_TYPE
glxinfo | grep "OpenGL"

# Install dependencies
sudo apt-get install qtwayland5 python3-pyqt5 python3-opengl

# Run with different backends
QT_QPA_PLATFORM=wayland python3 script.py  # Wayland
QT_QPA_PLATFORM=xcb python3 script.py      # X11
QT_QPA_PLATFORM=offscreen python3 script.py # Headless

# Debug Qt platform
export QT_DEBUG_PLUGINS=1
python3 script.py

# Check Qt platform plugins
ls /usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/
```

---

## License

This guide is provided as-is for educational purposes. KITTI dataset has its own license terms.

## Contributing

Feel free to submit issues or improvements to this guide.

---

**Last Updated:** 2026-04-16
**Tested On:** Ubuntu 22.04 LTS with Wayland