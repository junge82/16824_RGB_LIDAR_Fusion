#!/bin/bash
# Qt Dependencies Fix Script
# Installs all required Qt platform plugins and dependencies

echo "=========================================="
echo "Qt Dependencies Installation Script"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}This script requires sudo privileges to install packages.${NC}"
    echo "Please run with: sudo bash scripts/fix_qt_dependencies.sh"
    echo "Or the script will prompt for your password when needed."
    echo ""
fi

# Update package list
echo -e "${BLUE}Step 1: Updating package list...${NC}"
sudo apt-get update
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Package list updated successfully${NC}"
else
    echo -e "${RED}✗ Failed to update package list${NC}"
    exit 1
fi
echo ""

# Install required Qt/XCB packages
echo -e "${BLUE}Step 2: Installing Qt platform plugins and dependencies...${NC}"
PACKAGES=(
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
    "libxcb1"
    "libx11-xcb1"
    "libglib2.0-0"
    "libdbus-1-3"
)

echo "Installing packages: ${PACKAGES[*]}"
echo ""

sudo apt-get install -y "${PACKAGES[@]}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All packages installed successfully${NC}"
else
    echo ""
    echo -e "${RED}✗ Some packages failed to install${NC}"
    echo "Please check the error messages above and try again."
    exit 1
fi
echo ""

# Verify installation
echo -e "${BLUE}Step 3: Verifying installation...${NC}"
MISSING=0
for pkg in "${PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo -e "${GREEN}✓${NC} $pkg"
    else
        echo -e "${RED}✗${NC} $pkg (still missing)"
        MISSING=$((MISSING + 1))
    fi
done
echo ""

if [ $MISSING -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "✓ Installation Complete!"
    echo "==========================================${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Activate your conda environment:"
    echo "     conda activate rgb-fusion"
    echo ""
    echo "  2. Test the fix with:"
    echo "     python scripts/test_qt.py"
    echo ""
    echo "  3. If issues persist, run diagnostics:"
    echo "     bash scripts/diagnose_qt.sh"
    echo ""
    echo "  4. Try running your viewer script again"
    echo ""
else
    echo -e "${YELLOW}=========================================="
    echo "⚠ Installation completed with warnings"
    echo "==========================================${NC}"
    echo ""
    echo "$MISSING package(s) could not be installed."
    echo "Please check your system's package repositories."
    echo ""
fi

# Optional: Clear font cache (sometimes helps with Qt issues)
echo -e "${BLUE}Step 4: Clearing font cache (optional)...${NC}"
if command -v fc-cache &> /dev/null; then
    fc-cache -f -v > /dev/null 2>&1
    echo -e "${GREEN}✓ Font cache cleared${NC}"
else
    echo -e "${YELLOW}⚠ fc-cache not found, skipping${NC}"
fi
echo ""

echo "=========================================="
echo "Installation script completed!"
echo "=========================================="

# Made with Bob
