#!/bin/bash
# Qt Platform Plugin Diagnostic Script
# This script checks for Qt dependencies and identifies missing packages

echo "=========================================="
echo "Qt Platform Plugin Diagnostic Tool"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running with display
echo "1. Checking Display Configuration..."
if [ -z "$DISPLAY" ]; then
    echo -e "${RED}✗ DISPLAY variable not set${NC}"
    echo "  Solution: export DISPLAY=:0"
else
    echo -e "${GREEN}✓ DISPLAY is set to: $DISPLAY${NC}"
fi
echo ""

# Check Qt plugin paths
echo "2. Checking Qt Plugin Paths..."
if command -v python3 &> /dev/null; then
    python3 << 'EOF'
import sys
import os

try:
    from PyQt5.QtCore import QCoreApplication, QLibraryInfo
    
    # Get Qt plugin paths
    plugin_paths = QCoreApplication.libraryPaths()
    print(f"Qt Plugin Paths:")
    for path in plugin_paths:
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {exists} {path}")
        if os.path.exists(path):
            platforms_dir = os.path.join(path, "platforms")
            if os.path.exists(platforms_dir):
                plugins = os.listdir(platforms_dir)
                print(f"    Platform plugins: {', '.join(plugins)}")
    
    # Check for xcb plugin specifically
    xcb_found = False
    for path in plugin_paths:
        xcb_path = os.path.join(path, "platforms", "libqxcb.so")
        if os.path.exists(xcb_path):
            xcb_found = True
            print(f"\n✓ XCB plugin found at: {xcb_path}")
            break
    
    if not xcb_found:
        print("\n✗ XCB plugin NOT found - this is likely the issue!")
        
except ImportError as e:
    print(f"✗ Error importing PyQt5: {e}")
    sys.exit(1)
EOF
else
    echo -e "${RED}✗ Python3 not found${NC}"
fi
echo ""

# Check for required system libraries
echo "3. Checking Required System Libraries..."
REQUIRED_LIBS=(
    "libxcb-xinerama.so.0"
    "libxcb-cursor.so.0"
    "libxcb-icccm.so.4"
    "libxcb-image.so.0"
    "libxcb-keysyms.so.1"
    "libxcb-randr.so.0"
    "libxcb-render-util.so.0"
    "libxcb-shape.so.0"
    "libxkbcommon-x11.so.0"
    "libxcb-xkb.so.1"
    "libxcb-xfixes.so.0"
    "libxcb-util.so.1"
)

MISSING_LIBS=()
for lib in "${REQUIRED_LIBS[@]}"; do
    if ldconfig -p | grep -q "$lib"; then
        echo -e "${GREEN}✓${NC} $lib"
    else
        echo -e "${RED}✗${NC} $lib ${YELLOW}(MISSING)${NC}"
        MISSING_LIBS+=("$lib")
    fi
done
echo ""

# Check for required packages
echo "4. Checking Required Debian/Ubuntu Packages..."
REQUIRED_PACKAGES=(
    "libxcb-xinerama0"
    "libxcb-cursor0"
    "libxcb-icccm4"
    "libxcb-image0"
    "libxcb-keysyms1"
    "libxcb-randr0"
    "libxcb-render-util0"
    "libxcb-shape0"
    "libxkbcommon-x11-0"
    "libxcb-xkb1"
    "libxcb-xfixes0"
    "libxcb-util1"
)

MISSING_PACKAGES=()
for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo -e "${GREEN}✓${NC} $pkg"
    else
        echo -e "${RED}✗${NC} $pkg ${YELLOW}(NOT INSTALLED)${NC}"
        MISSING_PACKAGES+=("$pkg")
    fi
done
echo ""

# Summary and recommendations
echo "=========================================="
echo "DIAGNOSTIC SUMMARY"
echo "=========================================="

if [ ${#MISSING_PACKAGES[@]} -eq 0 ] && [ ${#MISSING_LIBS[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All required packages and libraries are installed!${NC}"
    echo ""
    echo "If you're still experiencing issues, try:"
    echo "  1. export QT_DEBUG_PLUGINS=1"
    echo "  2. Run your application again to see detailed Qt plugin loading info"
    echo "  3. Check if your conda environment has conflicting Qt installations"
else
    echo -e "${RED}✗ Missing dependencies detected!${NC}"
    echo ""
    
    if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
        echo "Missing packages:"
        for pkg in "${MISSING_PACKAGES[@]}"; do
            echo "  - $pkg"
        done
        echo ""
        echo "To install missing packages, run:"
        echo -e "${YELLOW}sudo apt-get update && sudo apt-get install -y ${MISSING_PACKAGES[*]}${NC}"
        echo ""
        echo "Or use the provided fix script:"
        echo -e "${YELLOW}bash scripts/fix_qt_dependencies.sh${NC}"
    fi
fi

echo ""
echo "For more information, see: docs/QT_TROUBLESHOOTING.md"
echo "=========================================="

# Made with Bob
