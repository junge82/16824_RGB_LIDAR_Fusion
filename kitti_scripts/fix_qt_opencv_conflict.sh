#!/bin/bash
# Fix Qt platform plugin conflict between OpenCV and PyQt5
# This resolves: "Could not load the Qt platform plugin 'xcb'"

echo "=========================================="
echo "Qt/OpenCV Plugin Conflict Fix"
echo "=========================================="
echo ""

# Detect conda environment
if [ -n "$CONDA_PREFIX" ]; then
    echo "✓ Detected conda environment: $CONDA_PREFIX"
    CONDA_ENV=$CONDA_PREFIX
else
    echo "⚠️  No conda environment detected"
    echo "   Please activate your conda environment first:"
    echo "   conda activate kitti_env"
    exit 1
fi

echo ""
echo "Problem: OpenCV's bundled Qt plugins conflict with system Qt"
echo "Solution: Remove OpenCV's Qt plugins to use system Qt instead"
echo ""

# Find OpenCV Qt plugins directory
CV2_QT_PLUGINS="$CONDA_ENV/lib/python*/site-packages/cv2/qt/plugins"

if [ -d "$CV2_QT_PLUGINS" ]; then
    echo "Found OpenCV Qt plugins at:"
    echo "  $CV2_QT_PLUGINS"
    echo ""
    
    # Backup first
    BACKUP_DIR="$CONDA_ENV/cv2_qt_backup_$(date +%Y%m%d_%H%M%S)"
    echo "Creating backup at: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    cp -r $CV2_QT_PLUGINS "$BACKUP_DIR/"
    echo "✓ Backup created"
    echo ""
    
    # Remove the conflicting plugins
    echo "Removing OpenCV Qt plugins..."
    rm -rf $CV2_QT_PLUGINS
    echo "✓ OpenCV Qt plugins removed"
    echo ""
else
    echo "OpenCV Qt plugins directory not found"
    echo "Checking alternative locations..."
    
    # Try to find cv2 installation
    CV2_PATH=$(python -c "import cv2; import os; print(os.path.dirname(cv2.__file__))" 2>/dev/null)
    if [ -n "$CV2_PATH" ]; then
        echo "Found cv2 at: $CV2_PATH"
        CV2_QT_DIR="$CV2_PATH/qt"
        if [ -d "$CV2_QT_DIR" ]; then
            echo "Found Qt directory, removing..."
            mv "$CV2_QT_DIR" "${CV2_QT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
            echo "✓ Moved to backup"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "Additional Fixes"
echo "=========================================="
echo ""

# Set environment variables
echo "Setting Qt environment variables..."

# Create/update conda env activation script
ACTIVATE_DIR="$CONDA_ENV/etc/conda/activate.d"
mkdir -p "$ACTIVATE_DIR"

cat > "$ACTIVATE_DIR/qt_fix.sh" << 'EOF'
#!/bin/bash
# Qt environment fixes for kitti_viewer

# Remove OpenCV's Qt plugin path from QT_PLUGIN_PATH
export QT_PLUGIN_PATH=$(echo $QT_PLUGIN_PATH | sed 's|[^:]*cv2[^:]*:||g' | sed 's|:$||')

# Use system Qt plugins
export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins

# Set platform based on display server
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    export QT_QPA_PLATFORM=wayland
else
    export QT_QPA_PLATFORM=xcb
fi

# Debug (uncomment to see Qt plugin loading)
# export QT_DEBUG_PLUGINS=1

echo "Qt environment configured for kitti_viewer"
EOF

chmod +x "$ACTIVATE_DIR/qt_fix.sh"
echo "✓ Created conda activation script: $ACTIVATE_DIR/qt_fix.sh"

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""

# Reactivate environment to apply changes
echo "Please run these commands:"
echo ""
echo "  conda deactivate"
echo "  conda activate kitti_env"
echo ""
echo "Then test with:"
echo "  python3 -c 'from PyQt5.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print(\"Qt OK\")'"
echo ""

echo "=========================================="
echo "Alternative Solutions"
echo "=========================================="
echo ""
echo "If the above doesn't work, try:"
echo ""
echo "1. Reinstall OpenCV without Qt:"
echo "   pip uninstall opencv-python opencv-contrib-python"
echo "   pip install opencv-python-headless"
echo ""
echo "2. Use system PyQt5 instead of conda:"
echo "   conda remove pyqt"
echo "   pip install PyQt5"
echo ""
echo "3. Set QT_QPA_PLATFORM_PLUGIN_PATH manually:"
echo "   export QT_QPA_PLATFORM_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/qt5/plugins"
echo ""

echo "Fix script completed!"

# Made with Bob
