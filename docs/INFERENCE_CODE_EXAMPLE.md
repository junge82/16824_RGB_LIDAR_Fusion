# Corrected Inference Code Example

This document provides a complete, corrected implementation of the inference pipeline for predicting labels from model outputs.

## Complete Corrected Inference Script

```python
"""
Corrected Inference Script for RGB-LiDAR Fusion 3D Object Detection

This script demonstrates the proper way to predict labels from model outputs
during inference.
"""

import argparse
import multiprocessing
import torch
from data_loader.data_loader_inference import get_data_loaders
from model.model import RgbLidarFusion
from model.loss import YoloLoss
import numpy as np
from logging import getLogger, basicConfig, INFO
from tqdm import tqdm
import os

# Enable TF32 for faster computation with less memory
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Enable memory efficient attention
torch.backends.cuda.enable_mem_efficient_sdp(True)

# Set memory fraction (use 90% of available VRAM)
torch.cuda.set_per_process_memory_fraction(0.9, 0)

print("Memory optimizations enabled for RTX 4060")

SEED = 10
# Set the random seed manually for reproducibility
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)


def get_args(arg_list=None):
    parser = argparse.ArgumentParser(description='RGB-LiDAR Fusion Inference')
    
    # Setup params
    parser.add_argument('--data_dir', type=str, 
                       default="/mnt/fastDisk/kitti3d/kitti_object/testing")
    parser.add_argument('--device', default=torch.device("cuda"))
    parser.add_argument('--num_data_loader_workers', type=int, 
                       default=multiprocessing.cpu_count())
    
    # Model checkpoint
    parser.add_argument('--checkpoint_path', type=str, 
                       default="results/checkpoint_epoch40.pth")
    
    # Data params
    parser.add_argument('--image_size', type=int, default=384)
    parser.add_argument('--batch_size', type=int, default=2)
    
    # Pointcloud encoder params
    parser.add_argument('--pc_num_input_features', type=int, default=4)
    parser.add_argument('--pc_use_norm', type=bool, default=True)
    parser.add_argument('--pc_num_filters', type=list[int], 
                       default=[48, 96, 96])
    parser.add_argument('--pc_with_distance', type=bool, default=False)
    parser.add_argument('--pc_voxel_size', type=list[float], 
                       default=[0.32, 0.32, 4])
    parser.add_argument('--pc_range', type=list[float], 
                       default=[0, -60, -3, 120, 60, 1])
    parser.add_argument('--pc_max_num_voxels', type=int, default=8000)
    parser.add_argument('--pc_max_num_points_per_voxel', type=int, default=75)
    parser.add_argument('--pc_grid_size', type=list[int])
    
    # YOLO params
    parser.add_argument('--yolo_anchors', type=list[float], 
                       default=[1.56, 1.6, 3.9])  # h, w, l
    parser.add_argument('--yolo_num_box_per_cell', type=int, default=1)
    parser.add_argument('--yolo_box_length', type=int, default=9)
    
    # Inference params
    parser.add_argument('--inference_conf_threshold', type=float, default=0.5)
    parser.add_argument('--NMS_overlap_threshold', type=float, default=0.5)
    
    # Output params
    parser.add_argument('--output_dir', type=str, default="inference_results")
    parser.add_argument('--save_predictions', type=bool, default=True)
    
    args = parser.parse_args() if arg_list is None else parser.parse_args(arg_list)
    return args


def save_predictions_to_file(predictions, output_path):
    """
    Save predictions in KITTI format to a text file
    
    Args:
        predictions: Tensor of shape (N, 16) with KITTI format labels
        output_path: Path to save the predictions
    """
    if predictions is None or len(predictions) == 0:
        # Create empty file if no predictions
        with open(output_path, 'w') as f:
            pass
        return
    
    with open(output_path, 'w') as f:
        for pred in predictions:
            # KITTI format: class truncated occluded alpha bbox_2d h w l x y z yaw score
            # We only have 3D info, so we use placeholder values for 2D bbox
            class_name = "Car"  # Assuming all predictions are cars
            truncated = 0.0
            occluded = 0
            alpha = -10  # Placeholder
            bbox_2d = "0 0 0 0"  # Placeholder
            
            h, w, l = pred[8].item(), pred[9].item(), pred[10].item()
            x, y, z = pred[11].item(), pred[12].item(), pred[13].item()
            yaw = pred[14].item()
            score = pred[15].item()
            
            line = f"{class_name} {truncated} {occluded} {alpha} {bbox_2d} "
            line += f"{h:.2f} {w:.2f} {l:.2f} {x:.2f} {y:.2f} {z:.2f} {yaw:.2f} {score:.4f}\n"
            f.write(line)


def main(args):
    # Setup logging
    basicConfig(level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = getLogger(__name__)
    
    logger.info("Starting inference pipeline")
    logger.info(f"Using checkpoint: {args.checkpoint_path}")
    logger.info(f"Data directory: {args.data_dir}")
    logger.info(f"Confidence threshold: {args.inference_conf_threshold}")
    
    # Create output directory
    if args.save_predictions:
        os.makedirs(args.output_dir, exist_ok=True)
        logger.info(f"Predictions will be saved to: {args.output_dir}")
    
    # Load data
    logger.info("Loading test data...")
    test_loader = get_data_loaders(args)
    logger.info(f"Loaded {len(test_loader.dataset)} test samples")
    
    # Initialize model
    logger.info("Initializing model...")
    model = RgbLidarFusion(args).to(args.device)
    
    # Load checkpoint
    logger.info("Loading model checkpoint...")
    checkpoint = torch.load(args.checkpoint_path, weights_only=False)
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    logger.info("Model loaded successfully")
    
    # Initialize loss function (contains conversion utilities)
    criterion = YoloLoss(
        args, 
        args.pc_range, 
        args.pc_voxel_size, 
        args.yolo_num_box_per_cell, 
        args.yolo_box_length, 
        args.yolo_anchors
    )
    
    # Storage for all predictions
    all_predictions = []
    sample_idx = 0
    
    # Disable gradient computation for inference
    with torch.no_grad():
        logger.info("Starting inference...")
        
        for batch_idx, batch_data in enumerate(tqdm(test_loader, desc="Processing batches")):
            # Extract batch data
            images = batch_data['image'].to(args.device)
            lidars = batch_data['lidar']
            calibs = batch_data['calib']
            
            # Forward pass through the model
            # Output shape: (batch_size, box_length, grid_height, grid_width)
            outputs = model(images, lidars)
            
            # Process each example in the batch
            for example_idx in range(outputs.shape[0]):
                output = outputs[example_idx]  # Shape: (9, H, W)
                calib = calibs[example_idx]
                
                # Convert YOLO output to KITTI labels
                # This function:
                # 1. Iterates through all grid cells
                # 2. Filters by confidence threshold
                # 3. Denormalizes coordinates and dimensions
                # 4. Converts from velodyne to camera frame
                # Returns: Tensor of shape (N, 16) or None if no detections
                predictions = criterion.convert_yolo_output_to_kitti_labels(
                    output, 
                    calib, 
                    conf_th=args.inference_conf_threshold
                )
                
                # Store predictions
                all_predictions.append(predictions)
                
                # Save predictions to file if requested
                if args.save_predictions:
                    output_file = os.path.join(
                        args.output_dir, 
                        f"{sample_idx:06d}.txt"
                    )
                    save_predictions_to_file(predictions, output_file)
                
                # Log statistics for this sample
                if predictions is not None:
                    num_detections = predictions.shape[0]
                    avg_conf = predictions[:, 15].mean().item()
                    logger.debug(
                        f"Sample {sample_idx}: {num_detections} detections, "
                        f"avg confidence: {avg_conf:.3f}"
                    )
                else:
                    logger.debug(f"Sample {sample_idx}: No detections")
                
                sample_idx += 1
    
    # Summary statistics
    total_samples = len(all_predictions)
    samples_with_detections = sum(1 for p in all_predictions if p is not None)
    total_detections = sum(
        p.shape[0] for p in all_predictions if p is not None
    )
    
    logger.info("=" * 60)
    logger.info("Inference completed!")
    logger.info(f"Total samples processed: {total_samples}")
    logger.info(f"Samples with detections: {samples_with_detections}")
    logger.info(f"Total detections: {total_detections}")
    logger.info(f"Average detections per sample: {total_detections / total_samples:.2f}")
    logger.info("=" * 60)
    
    if args.save_predictions:
        logger.info(f"Predictions saved to: {args.output_dir}")
    
    return all_predictions


if __name__ == '__main__':
    args = get_args()
    predictions = main(args)
```

## Key Differences from Original Code

### 1. Proper Model Output Processing

**Original (Incorrect):**
```python
outputs = self.model(images, lidars)  # Wrong: self.model doesn't exist
```

**Corrected:**
```python
outputs = model(images, lidars)  # Correct: use the model variable
```

### 2. Correct Conversion Function Call

**Original (Incorrect):**
```python
output_kitti = self.criterion.convert_yolo_output_to_kitti_labels(output, calib, 0.0)
# Wrong: self.criterion doesn't exist, and hardcoded threshold
```

**Corrected:**
```python
predictions = criterion.convert_yolo_output_to_kitti_labels(
    output, 
    calib, 
    conf_th=args.inference_conf_threshold  # Use configurable threshold
)
```

### 3. Proper Variable Naming

**Original (Incorrect):**
```python
for example_idx in range(outputs.shape[0]):
    output = outputs[example_idx]
    target = labels[example_idx]  # Wrong: labels doesn't exist in inference
```

**Corrected:**
```python
for example_idx in range(outputs.shape[0]):
    output = outputs[example_idx]
    calib = calibs[example_idx]
    # No target/labels in inference mode
```

### 4. Added Prediction Saving

The corrected version includes functionality to save predictions in KITTI format:

```python
def save_predictions_to_file(predictions, output_path):
    """Save predictions in KITTI format"""
    if predictions is None or len(predictions) == 0:
        with open(output_path, 'w') as f:
            pass
        return
    
    with open(output_path, 'w') as f:
        for pred in predictions:
            # Format: class truncated occluded alpha bbox h w l x y z yaw score
            # ... (see full implementation above)
```

## Usage Examples

### Basic Inference

```bash
python inference_corrected.py \
    --data_dir /path/to/kitti/testing \
    --checkpoint_path results/checkpoint_epoch40.pth \
    --inference_conf_threshold 0.5
```

### Inference with Custom Parameters

```bash
python inference_corrected.py \
    --data_dir /path/to/kitti/testing \
    --checkpoint_path results/checkpoint_best.pth \
    --inference_conf_threshold 0.3 \
    --batch_size 4 \
    --output_dir my_predictions \
    --save_predictions True
```

### Low Confidence Detection

```bash
python inference_corrected.py \
    --checkpoint_path results/checkpoint_epoch40.pth \
    --inference_conf_threshold 0.2  # Lower threshold to detect more objects
```

## Understanding the Output

### Prediction Format

Each prediction file (`000000.txt`, `000001.txt`, etc.) contains one line per detected object:

```
Car 0.0 0 -10 0 0 0 0 1.56 1.60 3.90 2.45 1.50 8.30 -1.57 0.9234
```

Fields:
1. `Car` - Object class
2. `0.0` - Truncation (placeholder)
3. `0` - Occlusion (placeholder)
4. `-10` - Alpha angle (placeholder)
5-8. `0 0 0 0` - 2D bbox (placeholder)
9. `1.56` - Height (meters)
10. `1.60` - Width (meters)
11. `3.90` - Length (meters)
12. `2.45` - X position in camera frame (meters)
13. `1.50` - Y position in camera frame (meters)
14. `8.30` - Z position in camera frame (meters)
15. `-1.57` - Yaw angle (radians)
16. `0.9234` - Confidence score

### Interpreting Confidence Scores

- **0.9 - 1.0**: Very high confidence, likely correct detection
- **0.7 - 0.9**: High confidence, probably correct
- **0.5 - 0.7**: Medium confidence, may have some false positives
- **0.3 - 0.5**: Low confidence, many false positives expected
- **< 0.3**: Very low confidence, mostly false positives

## Post-Processing Options

### Option 1: Apply NMS in Post-Processing

```python
def apply_nms(predictions, iou_threshold=0.5):
    """Apply Non-Maximum Suppression"""
    if predictions is None or len(predictions) == 0:
        return predictions
    
    # Sort by confidence
    sorted_indices = torch.argsort(predictions[:, 15], descending=True)
    predictions = predictions[sorted_indices]
    
    keep_indices = []
    while len(predictions) > 0:
        keep_indices.append(0)
        if len(predictions) == 1:
            break
        
        # Calculate IoU with remaining boxes
        ious = calculate_3d_iou_batch(predictions[0:1], predictions[1:])
        
        # Keep boxes with IoU below threshold
        keep_mask = ious < iou_threshold
        predictions = predictions[1:][keep_mask]
    
    return predictions[keep_indices]

# Use in inference loop:
predictions = criterion.convert_yolo_output_to_kitti_labels(
    output, calib, conf_th=args.inference_conf_threshold
)
if predictions is not None:
    predictions = apply_nms(predictions, args.NMS_overlap_threshold)
```

### Option 2: Filter by Distance

```python
def filter_by_distance(predictions, max_distance=50.0):
    """Keep only predictions within a certain distance"""
    if predictions is None:
        return None
    
    # Calculate distance from camera
    distances = torch.sqrt(
        predictions[:, 11]**2 +  # x
        predictions[:, 12]**2 +  # y
        predictions[:, 13]**2    # z
    )
    
    mask = distances <= max_distance
    return predictions[mask] if mask.any() else None
```

## Troubleshooting Guide

### Problem: RuntimeError: CUDA out of memory

**Solution:**
```python
# Reduce batch size
--batch_size 1

# Or process on CPU
--device cpu
```

### Problem: No predictions generated

**Solutions:**
1. Lower confidence threshold: `--inference_conf_threshold 0.2`
2. Check if model is loaded correctly
3. Verify input data format matches training data

### Problem: Too many false positives

**Solutions:**
1. Increase confidence threshold: `--inference_conf_threshold 0.7`
2. Apply NMS with lower threshold
3. Use a better trained model checkpoint

### Problem: Predictions in wrong location

**Cause:** Calibration issue or coordinate frame mismatch

**Solution:** Verify calibration files are correct and match the test images

## Performance Tips

1. **Batch Processing**: Use larger batch sizes if GPU memory allows
2. **Mixed Precision**: Enable for faster inference (already enabled in script)
3. **Data Loading**: Increase `num_data_loader_workers` for faster data loading
4. **Caching**: Process predictions once and save to disk

## Next Steps

After running inference, you can:

1. **Visualize Results**: Use the visualization tools in `utils/kitti_viewer.py`
2. **Evaluate Performance**: Compare predictions with ground truth using mAP
3. **Analyze Errors**: Identify common failure cases
4. **Fine-tune Thresholds**: Adjust confidence and NMS thresholds based on results

## Related Documentation

- [Main Inference Guide](INFERENCE_LABEL_PREDICTION.md)
- [Model Architecture](../model/model.py)
- [Loss and Conversion Functions](../model/loss.py)
- [Data Loading](../data_loader/data_loader_inference.py)