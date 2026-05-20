#!/usr/bin/env python3
"""
KITTI Viewer Example for Ubuntu 22.04 with X11
===============================================

This script demonstrates how to use the kitti_viewer utility to visualize
KITTI dataset point clouds and 3D bounding boxes on Ubuntu 22.04 with X11.

Prerequisites:
--------------
1. Install required packages:
   sudo apt-get update
   sudo apt-get install python3-pyqt5 python3-opengl libxcb-xinerama0

2. Install Python dependencies:
   pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5

3. For X11 (explicitly set):
   export QT_QPA_PLATFORM=xcb

Usage:
------
Basic usage:
    python example_kitti_viewer_x11.py

With specific data index:
    python example_kitti_viewer_x11.py --idx 5

With custom KITTI root directory:
    python example_kitti_viewer_x11.py --root /path/to/kitti --idx 10

Force X11 mode:
    QT_QPA_PLATFORM=xcb python example_kitti_viewer_x11.py
"""

import os
import sys
import argparse
import numpy as np

# Force X11/XCB backend for Qt
# This ensures compatibility with X11 display server
#os.environ['QT_QPA_PLATFORM'] = 'xcb'
#os.environ['QT_XCB_GL_INTEGRATION'] = 'xcb_egl'

print("🖥️  Configured for X11 display server")
print(f"   QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM')}")

# Import kitti_viewer utilities
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'my/16824_RGB_LIDAR_Fusion'))
    from utils.kitti_viewer import (
        kitti_object, 
        show_lidar_with_boxes,
        Calibration,
        Object3d,
        load_velo_scan,
        read_label
    )
    print("✓ Successfully imported kitti_viewer")
except ImportError as e:
    print(f"❌ Failed to import kitti_viewer: {e}")
    print("\nPlease ensure the kitti_viewer.py is in the correct location:")
    print("  - 16824_RGB_LIDAR_Fusion/utils/kitti_viewer.py")
    sys.exit(1)


def verify_x11_display():
    """Verify X11 display is available"""
    display = os.environ.get('DISPLAY')
    if not display:
        print("⚠️  Warning: DISPLAY environment variable not set")
        print("   X11 display may not be available")
        return False
    
    print(f"✓ X11 DISPLAY: {display}")
    return True


def visualize_kitti_sample(root_dir, split='training', idx=0):
    """
    Visualize a KITTI sample with 3D point cloud and bounding boxes
    
    Args:
        root_dir: Path to KITTI dataset root directory
        split: 'training' or 'testing'
        idx: Sample index to visualize
    """
    
    print(f"\n🎨 Visualizing KITTI sample {idx:06d}")
    print("=" * 60)
    
    # Construct file paths
    split_dir = os.path.join(root_dir, split)
    velodyne_file = os.path.join(split_dir, 'velodyne', f'{idx:06d}.bin')
    label_file = os.path.join(split_dir, 'label_2', f'{idx:06d}.txt')
    calib_file = os.path.join(split_dir, 'calib', f'{idx:06d}.txt')
    
    # Verify files exist
    if not os.path.exists(velodyne_file):
        print(f"❌ LiDAR file not found: {velodyne_file}")
        return False
    
    if not os.path.exists(calib_file):
        print(f"❌ Calibration file not found: {calib_file}")
        return False
    
    # Load data
    print("\n📊 Loading data...")
    
    # Load LiDAR point cloud
    print(f"   Loading LiDAR: {velodyne_file}")
    pc_velo = load_velo_scan(velodyne_file)
    print(f"   ✓ Loaded {pc_velo.shape[0]} points")
    
    # Load calibration
    print(f"   Loading calibration: {calib_file}")
    calib = Calibration(calib_file)
    print(f"   ✓ Calibration loaded")
    
    # Load labels (if available)
    objects = []
    if os.path.exists(label_file):
        print(f"   Loading labels: {label_file}")
        objects = read_label(label_file)
        print(f"   ✓ Loaded {len(objects)} objects")
        
        # Print object information
        print("\n📦 Detected objects:")
        for i, obj in enumerate(objects):
            if obj.type != 'DontCare':
                print(f"   {i+1}. {obj.type}: "
                      f"location=({obj.t[0]:.2f}, {obj.t[1]:.2f}, {obj.t[2]:.2f}), "
                      f"size=({obj.l:.2f}×{obj.w:.2f}×{obj.h:.2f})")
    else:
        print(f"   ⚠️  No label file found (testing set)")
    
    # Visualize
    print("\n🖼️  Opening 3D visualization (X11)...")
    print("   Controls:")
    print("   - Left mouse: Rotate view")
    print("   - Right mouse: Pan view")
    print("   - Scroll wheel: Zoom in/out")
    print("   - Close window to exit")
    print("\n" + "=" * 60)
    
    try:
        show_lidar_with_boxes(pc_velo, objects, calib)
        print("\n✓ Visualization completed successfully")
        return True
    except Exception as e:
        print(f"\n❌ Error during visualization: {e}")
        print("\nTroubleshooting tips for X11:")
        print("1. Verify X11 is running:")
        print("   echo $DISPLAY")
        print("\n2. Check X11 permissions:")
        print("   xhost +local:")
        print("\n3. Install missing X11 libraries:")
        print("   sudo apt-get install libxcb-xinerama0 libxcb-cursor0")
        print("\n4. Test X11 with simple app:")
        print("   xclock")
        raise


def main():
    """Main function with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description='KITTI Viewer Example for Ubuntu 22.04 X11',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--root',
        type=str,
        default='/mnt/fastDisk/kitti3d/kitti_object',
        help='Path to KITTI dataset root directory (default: ./kitti_object)'
    )
    
    parser.add_argument(
        '--split',
        type=str,
        default='training',
        choices=['training', 'testing'],
        help='Dataset split to use (default: training)'
    )
    
    parser.add_argument(
        '--idx',
        type=int,
        default=0,
        help='Sample index to visualize (default: 0)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("KITTI Viewer - Ubuntu 22.04 X11 Example")
    print("=" * 60)
    
    # Verify X11 display
    if not verify_x11_display():
        print("\n⚠️  X11 display may not be available")
        print("   Attempting to continue anyway...")
    
    # Visualize the sample
    try:
        success = visualize_kitti_sample(args.root, args.split, args.idx)
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Visualization failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
