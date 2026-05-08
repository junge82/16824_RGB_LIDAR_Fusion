# KITTI Dataset Download Guide for RGB LiDAR Fusion

This guide provides detailed instructions for downloading and preparing the KITTI 3D Object Detection dataset for training and validation.

## Table of Contents

- [Overview](#overview)
- [Dataset Requirements](#dataset-requirements)
- [Download Methods](#download-methods)
- [Dataset Structure](#dataset-structure)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Overview

The RGB LiDAR Fusion model requires the **KITTI 3D Object Detection Dataset**, which includes:
- RGB camera images
- LiDAR point clouds (Velodyne)
- Calibration files
- 3D object annotations

**Dataset Size**: ~29 GB (training) + ~12 GB (testing)

## Dataset Requirements

### Training Data
- **Left color images**: 7,481 images
- **Velodyne point clouds**: 7,481 files
- **Camera calibration**: 7,481 files
- **Training labels**: 7,481 files

### Validation/Testing Data
- **Left color images**: 7,518 images
- **Velodyne point clouds**: 7,518 files
- **Camera calibration**: 7,518 files
- **No labels** (for testing/validation)

## Download Methods

### Method 1: Official KITTI Website (Recommended)

#### Step 1: Register on KITTI Website

1. Visit [KITTI Vision Benchmark Suite](http://www.cvlibs.net/datasets/kitti/)
2. Navigate to **3D Object Detection Evaluation 2017**
3. Register for an account if you don't have one

#### Step 2: Download Required Files

Download the following files from the [KITTI 3D Object Detection page](http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d):

**For Training:**
```bash
# Create directory structure
mkdir -p ~/kitti_object/training/{image_2,velodyne,calib,label_2}

# Download training data (manual download from website)
# - Left color images of object data set (12 GB)
# - Velodyne point clouds (29 GB)
# - Camera calibration matrices (16 MB)
# - Training labels of object data set (5 MB)
```

**For Testing/Validation:**
```bash
# Create directory structure
mkdir -p ~/kitti_object/testing/{image_2,velodyne,calib}

# Download testing data (manual download from website)
# - Left color images of object data set (12 GB)
# - Velodyne point clouds (29 GB)
# - Camera calibration matrices (16 MB)
```

#### Step 3: Extract Downloaded Files

```bash
# Navigate to download directory
cd ~/Downloads

# Extract training data
unzip data_object_image_2.zip -d ~/kitti_object/training/
unzip data_object_velodyne.zip -d ~/kitti_object/training/
unzip data_object_calib.zip -d ~/kitti_object/training/
unzip data_object_label_2.zip -d ~/kitti_object/training/

# Extract testing data
unzip data_object_image_2.zip -d ~/kitti_object/testing/
unzip data_object_velodyne.zip -d ~/kitti_object/testing/
unzip data_object_calib.zip -d ~/kitti_object/testing/
```

### Method 2: Using wget (Alternative)

If direct download links are available, you can use wget:

```bash
#!/bin/bash
# download_kitti_object.sh

# Set download directory
KITTI_DIR=~/kitti_object
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
```

Make executable and run:
```bash
chmod +x download_kitti_object.sh
./download_kitti_object.sh
```

### Method 3: Using Kaggle Dataset

The KITTI dataset is also available on Kaggle:

```bash
# Install Kaggle CLI
pip install kaggle

# Configure Kaggle API (requires API token from kaggle.com/account)
mkdir -p ~/.kaggle
# Place your kaggle.json in ~/.kaggle/

# Download dataset
kaggle datasets download -d klemenko/kitti-dataset
unzip kitti-dataset.zip -d ~/kitti_object/
```

## Dataset Structure

After downloading and extracting, your directory structure should look like this:

```
~/kitti_object/
├── training/
│   ├── image_2/          # Left color camera images
│   │   ├── 000000.png
│   │   ├── 000001.png
│   │   └── ... (7,481 files)
│   ├── velodyne/         # LiDAR point clouds
│   │   ├── 000000.bin
│   │   ├── 000001.bin
│   │   └── ... (7,481 files)
│   ├── calib/            # Calibration files
│   │   ├── 000000.txt
│   │   ├── 000001.txt
│   │   └── ... (7,481 files)
│   └── label_2/          # 3D object annotations
│       ├── 000000.txt
│       ├── 000001.txt
│       └── ... (7,481 files)
└── testing/
    ├── image_2/          # Left color camera images
    │   ├── 000000.png
    │   ├── 000001.png
    │   └── ... (7,518 files)
    ├── velodyne/         # LiDAR point clouds
    │   ├── 000000.bin
    │   ├── 000001.bin
    │   └── ... (7,518 files)
    └── calib/            # Calibration files
        ├── 000000.txt
        ├── 000001.txt
        └── ... (7,518 files)
```

## Configuring the Model

After downloading the dataset, update the paths in your training script:

### Option 1: Command Line Arguments

```bash
python main.py \
  --train_dir ~/kitti_object/training \
  --val_dir ~/kitti_object/testing \
  --batch_size 2
```

### Option 2: Modify main.py

Edit [`main.py`](main.py:24-25):

```python
parser.add_argument('--train_dir', type=str, default="~/kitti_object/training")
parser.add_argument('--val_dir', type=str, default="~/kitti_object/testing")
```

### Option 3: Create Symbolic Links

```bash
# Create links in the project directory
cd 16824_RGB_LIDAR_Fusion/data/
ln -s ~/kitti_object/training train
ln -s ~/kitti_object/testing val
```

Then use:
```bash
python main.py \
  --train_dir ./data/train \
  --val_dir ./data/val
```

## Verification

### Verify Download Completeness

```bash
#!/bin/bash
# verify_kitti_dataset.sh

KITTI_DIR=~/kitti_object

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
```

### Test Data Loading

```python
# test_data_loading.py
import sys
sys.path.append('16824_RGB_LIDAR_Fusion')

from data_loader.data_loader import KittiDataset
from main import get_args
import torch

# Configure paths
args = get_args([
    '--train_dir', '~/kitti_object/training',
    '--val_dir', '~/kitti_object/testing'
])

# Test loading
print("Testing data loading...")
train_dataset = KittiDataset(args, args.train_dir, None, training=True)
print(f"Training samples: {len(train_dataset)}")

# Load one sample
sample = train_dataset[0]
print(f"Sample keys: {sample.keys()}")
print(f"Image shape: {sample['image'].shape}")
print(f"LiDAR shape: {sample['lidar'].shape}")
print("Data loading successful!")
```

Run verification:
```bash
python test_data_loading.py
```

## Dataset Split Recommendations

For training and validation, you can split the training set:

### Option 1: Use Official Split

KITTI provides official train/val splits. Create split files:

```bash
# Create train.txt with indices 0-6000
seq 0 6000 > train_split.txt

# Create val.txt with indices 6001-7480
seq 6001 7480 > val_split.txt
```

### Option 2: Random Split (80/20)

```python
# create_split.py
import random

indices = list(range(7481))
random.shuffle(indices)

train_size = int(0.8 * len(indices))
train_indices = indices[:train_size]
val_indices = indices[train_size:]

with open('train_split.txt', 'w') as f:
    f.write('\n'.join(map(str, train_indices)))

with open('val_split.txt', 'w') as f:
    f.write('\n'.join(map(str, val_indices)))

print(f"Train: {len(train_indices)}, Val: {len(val_indices)}")
```

## Data Preprocessing (Optional)

### Generate Reduced Point Clouds

To speed up training, you can pre-process point clouds:

```python
# preprocess_pointclouds.py
import numpy as np
from pathlib import Path

def reduce_pointcloud(pc_path, output_path, max_points=16384):
    """Reduce point cloud to fixed number of points"""
    pc = np.fromfile(pc_path, dtype=np.float32).reshape(-1, 4)
    
    if len(pc) > max_points:
        indices = np.random.choice(len(pc), max_points, replace=False)
        pc = pc[indices]
    
    pc.tofile(output_path)

# Process all point clouds
kitti_dir = Path('~/kitti_object').expanduser()
for split in ['training', 'testing']:
    input_dir = kitti_dir / split / 'velodyne'
    output_dir = kitti_dir / split / 'velodyne_reduced'
    output_dir.mkdir(exist_ok=True)
    
    for pc_file in input_dir.glob('*.bin'):
        output_file = output_dir / pc_file.name
        reduce_pointcloud(pc_file, output_file)
        print(f"Processed {pc_file.name}")
```

## Troubleshooting

### Issue 1: Download Interrupted

**Solution**: Resume download using wget with `-c` flag:
```bash
wget -c https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_velodyne.zip
```

### Issue 2: Insufficient Disk Space

**Error**: `No space left on device`

**Solution**: 
- Ensure you have at least 80 GB free space
- Use external drive or cloud storage
- Download only training data initially (~41 GB)

### Issue 3: Corrupted Downloads

**Solution**: Verify file integrity with checksums:
```bash
# Check file size
ls -lh data_object_velodyne.zip

# Expected sizes:
# data_object_image_2.zip: ~12 GB
# data_object_velodyne.zip: ~29 GB
# data_object_calib.zip: ~16 MB
# data_object_label_2.zip: ~5 MB
```

### Issue 4: Permission Denied

**Solution**: 
```bash
chmod -R 755 ~/kitti_object
```

### Issue 5: Data Loading Errors

**Error**: `FileNotFoundError` or `IndexError`

**Solution**: 
1. Verify dataset structure matches expected format
2. Check file counts match expected numbers
3. Ensure file naming is sequential (000000.png, 000001.png, etc.)

## Quick Start Script

Complete script to download, extract, and verify:

```bash
#!/bin/bash
# setup_kitti_dataset.sh

set -e

KITTI_DIR=~/kitti_object
PROJECT_DIR=16824_RGB_LIDAR_Fusion

echo "=========================================="
echo "KITTI Dataset Setup for RGB LiDAR Fusion"
echo "=========================================="

# Create directory structure
echo "Creating directory structure..."
mkdir -p $KITTI_DIR/training/{image_2,velodyne,calib,label_2}
mkdir -p $KITTI_DIR/testing/{image_2,velodyne,calib}

echo ""
echo "Please download the following files from:"
echo "http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d"
echo ""
echo "Required files:"
echo "  1. Left color images (training + testing)"
echo "  2. Velodyne point clouds (training + testing)"
echo "  3. Camera calibration (training + testing)"
echo "  4. Training labels"
echo ""
echo "After downloading, place them in ~/Downloads and press Enter..."
read

# Extract files
echo "Extracting files..."
cd ~/Downloads

if [ -f "data_object_image_2.zip" ]; then
    echo "Extracting images..."
    unzip -q data_object_image_2.zip -d $KITTI_DIR/
fi

if [ -f "data_object_velodyne.zip" ]; then
    echo "Extracting velodyne..."
    unzip -q data_object_velodyne.zip -d $KITTI_DIR/
fi

if [ -f "data_object_calib.zip" ]; then
    echo "Extracting calibration..."
    unzip -q data_object_calib.zip -d $KITTI_DIR/
fi

if [ -f "data_object_label_2.zip" ]; then
    echo "Extracting labels..."
    unzip -q data_object_label_2.zip -d $KITTI_DIR/
fi

# Verify
echo ""
echo "Verifying dataset..."
echo "Training images: $(ls $KITTI_DIR/training/image_2/*.png 2>/dev/null | wc -l)"
echo "Training velodyne: $(ls $KITTI_DIR/training/velodyne/*.bin 2>/dev/null | wc -l)"
echo "Training calib: $(ls $KITTI_DIR/training/calib/*.txt 2>/dev/null | wc -l)"
echo "Training labels: $(ls $KITTI_DIR/training/label_2/*.txt 2>/dev/null | wc -l)"

echo ""
echo "Setup complete!"
echo "Dataset location: $KITTI_DIR"
echo ""
echo "To train the model, run:"
echo "  cd $PROJECT_DIR"
echo "  python main.py --train_dir $KITTI_DIR/training --val_dir $KITTI_DIR/testing"
```

## Additional Resources

- [KITTI Dataset Paper](http://www.cvlibs.net/publications/Geiger2012CVPR.pdf)
- [KITTI 3D Object Detection Benchmark](http://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d)
- [KITTI DevKit](https://github.com/bostondiditeam/kitti/tree/master/resources/devkit_object)
- [PyKITTI Library](https://github.com/utiasSTARS/pykitti)

## Citation

If you use the KITTI dataset, please cite:

```bibtex
@inproceedings{Geiger2012CVPR,
  author = {Andreas Geiger and Philip Lenz and Raquel Urtasun},
  title = {Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite},
  booktitle = {Conference on Computer Vision and Pattern Recognition (CVPR)},
  year = {2012}
}
```

## Next Steps

After downloading the dataset:

1. **Verify installation**: Run verification script
2. **Test data loading**: Use test script to ensure data loads correctly
3. **Configure paths**: Update training script with correct paths
4. **Start training**: Follow [RTX4060_QUICK_START.md](RTX4060_QUICK_START.md) for training

For RTX 4060-specific setup, see [INSTALL_RTX4060.md](INSTALL_RTX4060.md).