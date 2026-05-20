# Fix: Cannot Load libqpdf.so - Missing libQt5Pdf.so.5

## The Problem

You're seeing this error:
```
Cannot load library /home/gergo/anaconda3/envs/kitti_env/lib/python3.11/site-packages/PyQt5/Qt5/plugins/imageformats/libqpdf.so: 
(libQt5Pdf.so.5: cannot open shared object file: No such file or directory)
```

**Root Cause:** PyQt5's PDF image format plugin requires the Qt5Pdf library, which is not included in the standard PyQt5 package. This is typically a non-critical warning that can be safely ignored unless you specifically need PDF image loading in Qt.

## Quick Fix Options

### Option 1: Ignore the Warning (Recommended if you don't need PDF support)

This warning is usually harmless and won't affect most applications. Simply ignore it if your application works fine otherwise.

To suppress the warning, set this environment variable:

```bash
export QT_LOGGING_RULES="*.debug=false;qt.qpa.plugin=false"
```

Or add to your Python script before importing PyQt5:

```python
import os
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.plugin=false'

from PyQt5.QtWidgets import QApplication
# ... rest of your imports
```

### Option 2: Remove the PDF Plugin (Clean Solution)

Simply remove the problematic plugin file:

```bash
rm ~/anaconda3/envs/kitti_env/lib/python3.11/site-packages/PyQt5/Qt5/plugins/imageformats/libqpdf.so
```

This removes the plugin that's causing the error. You won't be able to load PDF files as images in Qt, but most applications don't need this functionality.

### Option 3: Install Qt5Pdf Library (If you need PDF support)

Install the missing Qt5Pdf library from your system package manager:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libqt5pdf5
```

**Fedora/RHEL:**
```bash
sudo dnf install qt5-qtwebengine
```

**Arch Linux:**
```bash
sudo pacman -S qt5-webengine
```

Then create a symlink so PyQt5 can find it:

```bash
# Find where libQt5Pdf.so.5 is installed
find /usr -name "libQt5Pdf.so.5" 2>/dev/null

# Create symlink (adjust path based on find results)
ln -s /usr/lib/x86_64-linux-gnu/libQt5Pdf.so.5 \
      ~/anaconda3/envs/kitti_env/lib/python3.11/site-packages/PyQt5/Qt5/lib/
```

### Option 4: Reinstall PyQt5 with Proper Dependencies

```bash
# Uninstall current PyQt5
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip

# Install from conda-forge (better dependency management)
conda install -c conda-forge pyqt

# Or reinstall with pip
pip install PyQt5
```

## Permanent Solution

Add to your conda environment activation script:

```bash
# Create activation script directory
mkdir -p ~/anaconda3/envs/kitti_env/etc/conda/activate.d

# Create the fix script
cat > ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_pdf_fix.sh << 'EOF'
#!/bin/bash
# Suppress Qt PDF plugin warnings
export QT_LOGGING_RULES="*.debug=false;qt.qpa.plugin=false"
EOF

chmod +x ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_pdf_fix.sh
```

Now every time you activate the environment, the warning will be suppressed.

## Verification

Test that PyQt5 works correctly:

```bash
# Test PyQt5 import
python3 -c "from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('✓ PyQt5 OK')"

# Test with OpenCV if you use it
python3 -c "from PyQt5.QtWidgets import QApplication; import cv2; import sys; app = QApplication(sys.argv); print('✓ PyQt5 + OpenCV OK')"
```

## Understanding the Issue

The issue occurs because:

1. **PyQt5** includes various image format plugins in `Qt5/plugins/imageformats/`
2. The **libqpdf.so** plugin is for loading PDF files as images
3. This plugin depends on **libQt5Pdf.so.5**, which is part of Qt WebEngine
4. Standard PyQt5 pip packages don't include Qt WebEngine libraries
5. The plugin tries to load but fails, generating a warning

**Important:** This is just a warning, not an error. Your application will still work unless you specifically need to load PDF files as images in Qt.

## When You Actually Need PDF Support

You only need to fix this if:
- You're loading PDF files using Qt's image loading functions
- You're using QImage or QPixmap to display PDFs
- Your application explicitly requires PDF rendering in Qt

Most applications (including KITTI viewers, computer vision tools, etc.) don't need this functionality.

## Combined Fix with OpenCV Conflict

If you also have the OpenCV/Qt conflict (see `QT_OPENCV_CONFLICT_FIX.md`), combine both fixes:

```bash
# Create combined activation script
mkdir -p ~/anaconda3/envs/kitti_env/etc/conda/activate.d

cat > ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_fixes.sh << 'EOF'
#!/bin/bash
# Fix OpenCV Qt conflict
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins
export QT_QPA_PLATFORM=xcb
export QT_PLUGIN_PATH=$(echo $QT_PLUGIN_PATH | sed 's|[^:]*cv2[^:]*:||g')

# Suppress Qt PDF plugin warnings
export QT_LOGGING_RULES="*.debug=false;qt.qpa.plugin=false"
EOF

chmod +x ~/anaconda3/envs/kitti_env/etc/conda/activate.d/qt_fixes.sh

# Reactivate environment
conda deactivate
conda activate kitti_env
```

## Summary

**Fastest Fix (Recommended):**
```bash
# Just suppress the warning
export QT_LOGGING_RULES="*.debug=false;qt.qpa.plugin=false"
python3 your_script.py
```

**Cleanest Fix:**
```bash
# Remove the problematic plugin
rm ~/anaconda3/envs/kitti_env/lib/python3.11/site-packages/PyQt5/Qt5/plugins/imageformats/libqpdf.so
```

**If you need PDF support:**
```bash
# Install system Qt5Pdf library
sudo apt-get install libqt5pdf5
```

Choose the solution that best fits your needs! 🎉