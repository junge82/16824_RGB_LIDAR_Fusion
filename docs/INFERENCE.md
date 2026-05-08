Based on my analysis of the repository, **this repo currently only supports training, NOT inference**. Here's what I found:

## Current State

The [`main.py`](16824_RGB_LIDAR_Fusion/main.py:1) file only has training functionality:
- Line 95: `trainer.train()` - runs training loop
- Line 93: `trainer.visualize_sample()` - only visualizes samples during training/validation

The [`trainer.py`](16824_RGB_LIDAR_Fusion/trainer/trainer.py:1) has:
- `train()` method (line 48) - training loop
- `val_epoch()` method (line 99) - validation during training
- `visualize_sample()` method (line 180) - visualization helper
- **NO dedicated inference method**

## How to Add Inference

To run inference on new data, you need to create an inference script. Here's what you'd need:

1. **Load a trained model checkpoint**:
```python
checkpoint = torch.load('results/checkpoint_best.pth')
model.load_state_dict(checkpoint['state_dict'])
model.eval()
```

2. **Process input data** (image + LiDAR point cloud)

3. **Run forward pass**:
```python
with torch.no_grad():
    outputs = model(images, lidars)
    predictions = criterion.convert_yolo_output_to_kitti_labels(
        outputs[0], calib, inference_conf_threshold
    )
```

4. **Post-process and visualize results** using the existing utilities in [`utils/kitti_viewer.py`](16824_RGB_LIDAR_Fusion/utils/kitti_viewer.py:1)

The repository provides the building blocks (model loading, output conversion, visualization) but lacks a standalone inference script for running predictions on new test data.


## Why Testing Label Data is Missing

The **KITTI testing dataset intentionally does NOT include labels** (label_2 folder). This is by design:

### KITTI Dataset Structure

**Training Set** (7,481 samples):
- ✅ Images (`image_2/`)
- ✅ LiDAR point clouds (`velodyne/`)
- ✅ Calibration files (`calib/`)
- ✅ **Labels** (`label_2/`) - Ground truth annotations

**Testing Set** (7,518 samples):
- ✅ Images (`image_2/`)
- ✅ LiDAR point clouds (`velodyne/`)
- ✅ Calibration files (`calib/`)
- ❌ **NO Labels** - Withheld for benchmark evaluation

### Why No Testing Labels?

1. **Benchmark Integrity**: KITTI maintains a public leaderboard. Test labels are kept private to prevent overfitting to the test set.

2. **Fair Evaluation**: To get test set results, you must submit predictions to the KITTI evaluation server, which computes metrics using the private labels.

3. **Standard Practice**: This is common in computer vision benchmarks (ImageNet, COCO, etc.)

### How to Use This Repo

**For Training/Validation:**
- Split the **training set** (7,481 samples) into train/val
- Example: 6,000 for training, 1,481 for validation
- Both have labels for supervised learning

**For Testing/Inference:**
- Use the testing set (7,518 samples) for inference only
- Generate predictions and submit to KITTI server for evaluation
- Or use it for qualitative visualization

### Current Error Fix

The error occurs because [`data_loader.py:80`](16824_RGB_LIDAR_Fusion/data_loader/data_loader.py:80) expects labels for validation. You have two options:

**Option 1**: Use training data for both train and val (split internally)
```bash
python main.py \
  --train_dir /mnt/fastDisk/kitti3d/kitti_object/training \
  --val_dir /mnt/fastDisk/kitti3d/kitti_object/training
```

**Option 2**: Modify the code to support inference without labels (requires creating an inference script)

The repo currently **only supports training**, not inference on unlabeled test data.