# Inference: How to Predict Labels from Model Outputs

This guide explains the complete process of converting raw model outputs into predicted object labels during inference for the RGB-LiDAR Fusion 3D object detection model.

## Overview

The model uses a YOLO-style detection approach that outputs predictions on a spatial grid. Each grid cell can contain object predictions with confidence scores and bounding box parameters.

## Model Output Format

### Raw Output Shape
```python
outputs: torch.Tensor  # Shape: (Batch, box_length, grid_height, grid_width)
# box_length = 9 (default)
# grid_height, grid_width depend on the point cloud voxelization
```

### YOLO Output Format (per grid cell)
Each grid cell contains 9 values representing:

| Index | Parameter | Description |
|-------|-----------|-------------|
| 0 | `conf` | Confidence score (0-1) indicating object presence |
| 1 | `x` | X-coordinate offset within grid cell (normalized) |
| 2 | `y` | Y-coordinate offset within grid cell (normalized) |
| 3 | `z` | Z-coordinate (height) in velodyne frame (normalized) |
| 4 | `h` | Object height (normalized relative to anchor) |
| 5 | `w` | Object width (normalized relative to anchor) |
| 6 | `l` | Object length (normalized relative to anchor) |
| 7 | `yaw_r` | Real part of yaw angle (cos(yaw)) |
| 8 | `yaw_i` | Imaginary part of yaw angle (sin(yaw)) |

**Note**: The yaw angle is encoded as complex number components to avoid discontinuity issues.

## Complete Inference Pipeline

### Step 1: Load Model and Data

```python
import torch
from model.model import RgbLidarFusion
from model.loss import YoloLoss
from data_loader.data_loader_inference import get_data_loaders

# Initialize model
model = RgbLidarFusion(args).to(args.device)
checkpoint = torch.load(args.checkpoint_path, weights_only=False)
model.load_state_dict(checkpoint['state_dict'])
model.eval()

# Initialize loss function (contains conversion utilities)
criterion = YoloLoss(
    args, 
    args.pc_range, 
    args.pc_voxel_size, 
    args.yolo_num_box_per_cell, 
    args.yolo_box_length, 
    args.yolo_anchors
)

# Load test data
test_loader = get_data_loaders(args)
```

### Step 2: Run Model Inference

```python
with torch.no_grad():
    for batch_idx, batch_data in enumerate(test_loader):
        # Extract batch data
        images = batch_data['image'].to(args.device)
        lidars = batch_data['lidar']
        calibs = batch_data['calib']
        
        # Forward pass
        outputs = model(images, lidars)
        # outputs shape: (batch_size, 9, grid_height, grid_width)
```

### Step 3: Convert YOLO Output to KITTI Labels

For each example in the batch:

```python
for example_idx in range(outputs.shape[0]):
    output = outputs[example_idx]  # Shape: (9, grid_height, grid_width)
    calib = calibs[example_idx]
    
    # Convert to KITTI format with confidence threshold
    output_kitti = criterion.convert_yolo_output_to_kitti_labels(
        output, 
        calib, 
        conf_th=args.inference_conf_threshold  # e.g., 0.5
    )
```

## Detailed Conversion Process

The [`convert_yolo_output_to_kitti_labels()`](../model/loss.py:213) method performs the following steps:

### 3.1 Iterate Through Grid Cells

```python
for y_idx in range(output.shape[1]):  # grid height
    for x_idx in range(output.shape[2]):  # grid width
        # Get confidence for this grid cell
        conf = output[0, y_idx, x_idx]  # YOLOLABEL_IDX["conf"] = 0
        
        # Skip low-confidence predictions
        if conf < conf_th:
            continue
```

### 3.2 Denormalize Spatial Coordinates

Convert normalized grid coordinates back to real-world velodyne coordinates:

```python
# Calculate grid cell size in meters
output_grid_len_m = (
    z_range,  # Full Z range
    y_range / output.shape[1],  # Y cell size
    x_range / output.shape[2]   # X cell size
)

# Denormalize X coordinate
x_velo = (
    yolo_label[1] * output_grid_len_m[2] +  # Offset within cell
    x_offset +                                # Point cloud range offset
    x_idx * output_grid_len_m[2]             # Grid cell position
)

# Denormalize Y coordinate
y_velo = (
    yolo_label[2] * output_grid_len_m[1] +  # Offset within cell
    y_offset +                                # Point cloud range offset
    y_idx * output_grid_len_m[1]             # Grid cell position
)

# Denormalize Z coordinate
z_velo = (
    yolo_label[3] * output_grid_len_m[0] +  # Normalized height
    z_offset                                  # Point cloud range offset
)
```

### 3.3 Denormalize Object Dimensions

Convert normalized dimensions back to real sizes using anchors:

```python
# Anchors: [h, w, l] = [1.56, 1.6, 3.9] (typical car dimensions)
h = yolo_label[4] * anchors[0] + anchors[0]  # Height
w = yolo_label[5] * anchors[1] + anchors[1]  # Width
l = yolo_label[6] * anchors[2] + anchors[2]  # Length
```

### 3.4 Recover Yaw Angle

Convert complex representation back to angle:

```python
yaw = torch.atan2(
    yolo_label[8],  # yaw_i (imaginary/sin component)
    yolo_label[7]   # yaw_r (real/cos component)
)
```

### 3.5 Transform to Camera Coordinate Frame

Convert from velodyne (LiDAR) frame to camera rectified frame:

```python
# Stack all XYZ coordinates
xyz_velo = kitti_labels[:, [x_idx, y_idx, z_idx]]

# Use calibration to transform
xyz_rect = calib.project_velo_to_rect(xyz_velo.numpy())

# Update labels with camera coordinates
kitti_labels[:, [x_idx, y_idx, z_idx]] = torch.from_numpy(xyz_rect)
```

## KITTI Label Format

The final output is in KITTI format with 16 values per detection:

| Index | Field | Description |
|-------|-------|-------------|
| 0 | `class` | Object class (0=Car, 1=Pedestrian, 2=Cyclist) |
| 1 | `truncated` | Truncation level (not used in this model) |
| 2 | `occluded` | Occlusion level (not used in this model) |
| 3 | `alpha` | Observation angle (not used in this model) |
| 4-7 | `bbox` | 2D bounding box [left, top, right, bottom] (not used) |
| 8 | `h` | 3D object height (meters) |
| 9 | `w` | 3D object width (meters) |
| 10 | `l` | 3D object length (meters) |
| 11 | `x` | 3D object center X in camera coordinates (meters) |
| 12 | `y` | 3D object center Y in camera coordinates (meters) |
| 13 | `z` | 3D object center Z in camera coordinates (meters) |
| 14 | `yaw` | Rotation around Y-axis (radians) |
| 15 | `conf` | Detection confidence score |

## Post-Processing Steps

### 4.1 Confidence Thresholding

Filter predictions based on confidence:

```python
# Set threshold (e.g., 0.5)
conf_threshold = args.inference_conf_threshold

# Only predictions with conf >= threshold are kept
# This is done inside convert_yolo_output_to_kitti_labels()
```

### 4.2 Non-Maximum Suppression (NMS)

Remove duplicate detections for the same object:

```python
def apply_nms(predictions, iou_threshold=0.5):
    """
    Apply Non-Maximum Suppression to remove overlapping boxes
    
    Args:
        predictions: List of KITTI format predictions
        iou_threshold: IoU threshold for suppression
    
    Returns:
        Filtered predictions after NMS
    """
    # Sort by confidence (descending)
    predictions = sorted(predictions, key=lambda x: x[15], reverse=True)
    
    keep = []
    while len(predictions) > 0:
        # Keep highest confidence prediction
        keep.append(predictions[0])
        predictions = predictions[1:]
        
        # Remove overlapping predictions
        predictions = [
            pred for pred in predictions 
            if calculate_3d_iou(keep[-1], pred) < iou_threshold
        ]
    
    return keep
```

### 4.3 Coordinate System Notes

**Velodyne (LiDAR) Frame:**
- X: Forward (vehicle direction)
- Y: Left
- Z: Up

**Camera Rectified Frame:**
- X: Right
- Y: Down
- Z: Forward

The calibration matrices handle the transformation between these frames.

## Complete Inference Example

```python
def run_inference(args):
    # Setup
    model = RgbLidarFusion(args).to(args.device)
    checkpoint = torch.load(args.checkpoint_path, weights_only=False)
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    
    criterion = YoloLoss(args, args.pc_range, args.pc_voxel_size, 
                        args.yolo_num_box_per_cell, args.yolo_box_length, 
                        args.yolo_anchors)
    
    test_loader = get_data_loaders(args)
    
    all_predictions = []
    
    with torch.no_grad():
        for batch_idx, batch_data in enumerate(test_loader):
            images = batch_data['image'].to(args.device)
            lidars = batch_data['lidar']
            calibs = batch_data['calib']
            
            # Forward pass
            outputs = model(images, lidars)
            
            # Process each example
            for example_idx in range(outputs.shape[0]):
                output = outputs[example_idx]
                calib = calibs[example_idx]
                
                # Convert to KITTI labels
                predictions = criterion.convert_yolo_output_to_kitti_labels(
                    output, 
                    calib, 
                    conf_th=args.inference_conf_threshold
                )
                
                if predictions is not None:
                    # Apply NMS if needed
                    predictions = apply_nms(
                        predictions, 
                        iou_threshold=args.NMS_overlap_threshold
                    )
                    all_predictions.append(predictions)
    
    return all_predictions
```

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `inference_conf_threshold` | 0.5 | Minimum confidence to keep prediction |
| `NMS_overlap_threshold` | 0.5 | IoU threshold for NMS |
| `pc_range` | [0, -60, -3, 120, 60, 1] | Point cloud range [x_min, y_min, z_min, x_max, y_max, z_max] |
| `pc_voxel_size` | [0.32, 0.32, 4] | Voxel size [x, y, z] in meters |
| `yolo_anchors` | [1.56, 1.6, 3.9] | Anchor dimensions [h, w, l] for cars |

## Troubleshooting

### Issue: No predictions returned
- **Cause**: Confidence threshold too high
- **Solution**: Lower `inference_conf_threshold` (try 0.3 or 0.2)

### Issue: Too many overlapping predictions
- **Cause**: NMS not applied or threshold too high
- **Solution**: Apply NMS with lower `NMS_overlap_threshold` (try 0.3)

### Issue: Predictions in wrong coordinate frame
- **Cause**: Missing coordinate transformation
- **Solution**: Ensure calibration is passed to `convert_yolo_output_to_kitti_labels()`

## References

- YOLO Output Format: [`model/loss.py`](../model/loss.py:30-40)
- Conversion Function: [`model/loss.py:convert_yolo_output_to_kitti_labels()`](../model/loss.py:213)
- Validation Example: [`trainer/trainer.py:val_epoch()`](../trainer/trainer.py:99)
- Inference Script: [`inference.py`](../inference.py)