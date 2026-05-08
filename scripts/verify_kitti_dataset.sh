#!/bin/bash
# verify_kitti_dataset.sh

KITTI_DIR=/mnt/fastDisk/kitti3d/kitti_object

echo "Verifying KITTI dataset..."

# Check training data
echo "Training data:"
echo "  Images: $(ls $KITTI_DIR/training/image_2/*.png 2>/dev/null | wc -l) / 7481"
echo "  Velodyne: $(ls $KITTI_DIR/training/velodyne/*.bin 2>/dev/null | wc -l) / 7481"
echo "  Calib: $(ls $KITTI_DIR/training/calib/*.txt 2>/dev/null | wc -l) / 7481"
echo "  Labels: $(ls $KITTI_DIR/training/label_2/*.txt 2>/dev/null | wc -l) / 7481"

# Check testing data
echo "Testing data:"
echo "  Images: $(ls $KITTI_DIR/testing/image_2/*.png 2>/dev/null | wc -l) / 7518"
echo "  Velodyne: $(ls $KITTI_DIR/testing/velodyne/*.bin 2>/dev/null | wc -l) / 7518"
echo "  Calib: $(ls $KITTI_DIR/testing/calib/*.txt 2>/dev/null | wc -l) / 7518"

echo "Verification complete!"