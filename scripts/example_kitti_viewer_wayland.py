#!/usr/bin/env python3
"""
KITTI Viewer Example for Ubuntu 22.04 with Wayland
===================================================

This script demonstrates how to use the kitti_viewer utility to visualize
KITTI dataset point clouds and 3D bounding boxes on Ubuntu 22.04 with Wayland.

Prerequisites:
--------------
1. Install required packages:
   sudo apt-get update
   sudo apt-get install python3-pyqt5 python3-opengl libxcb-xinerama0

2. Install Python dependencies:
   pip install numpy opencv-python pyqtgraph PyOpenGL PyQt5

3. For Wayland compatibility, set environment variables:
   export QT_QPA_PLATFORM=wayland
   export QT_AUTO_SCREEN_SCALE_FACTOR=1
   export QT_WAYLAND_DISABLE_WINDOWDECORATION=0

Usage:
------
Basic usage:
    python example_kitti_viewer_wayland.py

With specific data index:
    python example_kitti_viewer_wayland.py --idx 5

With custom KITTI root directory:
    python example_kitti_viewer_wayland.py --root /path/to/kitti --idx 10

Troubleshooting Wayland Issues:
--------------------------------
If you encounter display issues on Wayland:

1. Force X11 backend (fallback):
   export QT_QPA_PLATFORM=xcb
   python example_kitti_viewer_wayland.py

2. Check if Wayland is running:
   echo $XDG_SESSION_TYPE

3. Install additional Wayland support:
   sudo apt-get install qtwayland5

4. For NVIDIA GPUs, ensure proper drivers:
   sudo apt-get install nvidia-driver-XXX
"""

import os
import sys
import argparse
import numpy as np

# Configure Qt for Wayland before importing PyQt5
# This is crucial for Ubuntu 22.04 Wayland compatibility
def configure_qt_for_wayland():
    """Configure Qt environment variables for Wayland compatibility"""
    
    # Check if running on Wayland
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    
    if session_type == 'wayland':
        print("🌊 Detected Wayland session")
        
        # Set Qt platform to Wayland
        if 'QT_QPA_PLATFORM' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'wayland'
            print("   ✓ Set QT_QPA_PLATFORM=wayland")
        
        # Enable automatic screen scaling
        if 'QT_AUTO_SCREEN_SCALE_FACTOR' not in os.environ:
            os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
            print("   ✓ Enabled auto screen scaling")
        
        # Enable window decorations
        if 'QT_WAYLAND_DISABLE_WINDOWDECORATION' not in os.environ:
            os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '0'
            print("   ✓ Enabled window decorations")
        
        # Force OpenGL backend (important for 3D rendering)
        if 'QT_XCB_GL_INTEGRATION' not in os.environ:
            os.environ['QT_XCB_GL_INTEGRATION'] = 'xcb_egl'
            print("   ✓ Set OpenGL integration")
            
    elif session_type == 'x11':
        print("🖥️  Detected X11 session")
        # X11 usually works out of the box
        if 'QT_QPA_PLATFORM' not in os.environ:
            os.environ['QT_QPA_PLATFORM'] = 'xcb'
    else:
        print(f"⚠️  Unknown session type: {session_type}")
        print("   Attempting auto-detection...")

# Configure Qt BEFORE importing any Qt modules
configure_qt_for_wayland()

# Now import the kitti_viewer utilities
# Adjust the import path based on your project structure
try:
    # Try importing from the 16824_RGB_LIDAR_Fusion project
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '16824_RGB_LIDAR_Fusion'))
    from utils.kitti_viewer import (
        kitti_object, 
        show_lidar_with_boxes,
        Calibration,
        Object3d,
        load_velo_scan,
        read_label
    )
    print("✓ Successfully imported kitti_viewer from 16824_RGB_LIDAR_Fusion")
except ImportError as e:
    print(f"❌ Failed to import kitti_viewer: {e}")
    print("\nPlease ensure the kitti_viewer.py is in the correct location:")
    print("  - 16824_RGB_LIDAR_Fusion/utils/kitti_viewer.py")
    sys.exit(1)


def verify_kitti_data(root_dir, split='training', idx=0):
    """Verify that KITTI data exists and is accessible"""
    
    print(f"\n📁 Verifying KITTI data at: {root_dir}")
    
    split_dir = os.path.join(root_dir, split)
    
    # Check directories
    velodyne_dir = os.path.join(split_dir, 'velodyne')
    label_dir = os.path.join(split_dir, 'label_2')
    calib_dir = os.path.join(split_dir, 'calib')
    image_dir = os.path.join(split_dir, 'image_2')
    
    dirs_to_check = [
        ('Velodyne (LiDAR)', velodyne_dir),
        ('Labels', label_dir),
        ('Calibration', calib_dir),
        ('Images', image_dir)
    ]
    
    all_exist = True
    for name, path in dirs_to_check:
        exists = os.path.exists(path)
        status = "✓" if exists else "❌"
        print(f"   {status} {name}: {path}")
        if not exists:
            all_exist = False
    
    # Check specific files for the given index
    if all_exist:
        print(f"\n📄 Checking files for index {idx:06d}:")
        
        files_to_check = [
            ('LiDAR', os.path.join(velodyne_dir, f'{idx:06d}.bin')),
            ('Label', os.path.join(label_dir, f'{idx:06d}.txt')),
            ('Calib', os.path.join(calib_dir, f'{idx:06d}.txt')),
            ('Image', os.path.join(image_dir, f'{idx:06d}.png'))
        ]
        
        for name, path in files_to_check:
            exists = os.path.exists(path)
            status = "✓" if exists else "❌"
            print(f"   {status} {name}: {os.path.basename(path)}")
    
    return all_exist


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
    print("\n🖼️  Opening 3D visualization...")
    print("   Controls:")
    print("   - Left mouse: Rotate view")
    print("   - Right mouse: Pan view")
    print("   - Scroll wheel: Zoom in/out")
    print("   - Close window to exit")
    print("\n" + "=" * 60)
    
    try:
        show_lidar_with_boxes(pc_velo, objects, calib)
        print("\n✓ Visualization completed successfully")
    except Exception as e:
        print(f"\n❌ Error during visualization: {e}")
        print("\nTroubleshooting tips:")
        print("1. Try running with X11 backend:")
        print("   export QT_QPA_PLATFORM=xcb")
        print("   python example_kitti_viewer_wayland.py")
        print("\n2. Install missing dependencies:")
        print("   sudo apt-get install qtwayland5 libxcb-xinerama0")
        print("\n3. Check OpenGL support:")
        print("   glxinfo | grep OpenGL")
        raise


def main():
    """Main function with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description='KITTI Viewer Example for Ubuntu 22.04 Wayland',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--root',
        type=str,
        default='./kitti_object',
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
    
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify data existence without visualization'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("KITTI Viewer - Ubuntu 22.04 Wayland Example")
    print("=" * 60)
    
    # Verify data exists
    data_exists = verify_kitti_data(args.root, args.split, args.idx)
    
    if not data_exists:
        print("\n❌ KITTI data not found or incomplete!")
        print("\nTo download KITTI dataset:")
        print("1. Visit: http://www.cvlibs.net/datasets/kitti/eval_object.php")
        print("2. Download:")
        print("   - Left color images of object data set (12 GB)")
        print("   - Velodyne point clouds (29 GB)")
        print("   - Camera calibration matrices (16 MB)")
        print("   - Training labels (5 MB)")
        print("3. Extract to:", args.root)
        return 1
    
    if args.verify_only:
        print("\n✓ Data verification complete!")
        return 0
    
    # Visualize the sample
    try:
        visualize_kitti_sample(args.root, args.split, args.idx)
        return 0
    except Exception as e:
        print(f"\n❌ Visualization failed: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

# Made with Bob
