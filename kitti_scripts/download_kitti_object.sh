#!/bin/bash
# download_kitti_object.sh

# Set download directory
KITTI_DIR=/mnt/fastDisk/kitti3d/kitti_object
mkdir -p $KITTI_DIR

cd $KITTI_DIR

# Training data
echo "Downloading training data..."
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_image_2.zip
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_velodyne.zip
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_calib.zip
wget https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip

# Extract training data
echo "Extracting training data..."
unzip -q data_object_image_2.zip
unzip -q data_object_velodyne.zip
unzip -q data_object_calib.zip
unzip -q data_object_label_2.zip

# Clean up zip files
rm *.zip

echo "Download complete!"