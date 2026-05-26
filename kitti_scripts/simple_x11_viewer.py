#!/usr/bin/env python3
import os
import sys

# Force X11 backend
#os.environ['QT_QPA_PLATFORM'] = 'xcb'

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
root = '/mnt/fastDisk/kitti3d/kitti_object/training'

# Load data
pc_velo = load_velo_scan(f'{root}/velodyne/{idx:06d}.bin')
objects = read_label(f'{root}/labels_2/{idx:06d}.txt')
calib = Calibration(f'{root}/calib/{idx:06d}.txt')

# Visualize (opens 3D window)
show_lidar_with_boxes(pc_velo, objects, calib)
