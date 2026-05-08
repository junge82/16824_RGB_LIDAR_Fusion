# Memory Optimization Guide for RGB LiDAR Fusion

This guide provides strategies to reduce GPU memory usage during training, especially useful for GPUs with limited VRAM (8GB or less).

## Quick Start - Low Memory Configuration

Run training with these optimized settings:

```bash
python main.py \
  --batch_size 1 \
  --num_data_loader_workers 2 \
  --image_size 384 \
  --pc_max_num_voxels 8000 \
  --pc_num_filters 32 64 64 \
  --gradient_accumulation_steps 4
```

## Memory Optimization Strategies

### 1. Reduce Batch Size (Most Effective)

**Default**: `batch_size=3` (~6-8GB VRAM)
**Recommended**: `batch_size=1` (~2-3GB VRAM)

```bash
python main.py --batch_size 1
```

### 2. Use Gradient Accumulation

Simulate larger batch sizes without memory overhead:

```python
# Effective batch size = batch_size × gradient_accumulation_steps
# Example: 1 × 4 = 4 effective batch size
--gradient_accumulation_steps 4
```

### 3. Reduce Image Resolution

**Default**: `image_size=448`
**Options**: 384 (saves ~20%), 320 (saves ~40%)

```bash
python main.py --image_size 384
```

### 4. Reduce Point Cloud Complexity

**Reduce max voxels**:
```bash
--pc_max_num_voxels 8000  # Default: 12000
```

**Reduce points per voxel**:
```bash
--pc_max_num_points_per_voxel 50  # Default: 100
```

**Reduce filter sizes**:
```bash
--pc_num_filters 32 64 64  # Default: [64, 128, 128]
```

### 5. Reduce Data Loader Workers

```bash
--num_data_loader_workers 2  # Default: CPU count
```

### 6. Enable Mixed Precision Training (PyTorch AMP)

Reduces memory by ~40% and speeds up training:

```python
# Add to trainer.py
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

# In training loop:
with autocast():
    outputs = model(images, lidars)
    loss = criterion(...)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### 7. Clear Cache Periodically

```python
# Add to training loop
if batch_idx % 100 == 0:
    torch.cuda.empty_cache()
```

## Memory Usage Comparison

| Configuration | Batch Size | Image Size | Voxels | Est. VRAM |
|--------------|------------|------------|--------|-----------|
| Default | 3 | 448 | 12000 | 8-10 GB |
| Optimized | 2 | 448 | 10000 | 5-6 GB |
| Low Memory | 1 | 384 | 8000 | 2-3 GB |
| Ultra Low | 1 | 320 | 6000 | 1.5-2 GB |

## Recommended Configurations

### For 8GB VRAM (RTX 4060, RTX 3060)

```bash
python main.py \
  --batch_size 1 \
  --image_size 384 \
  --pc_max_num_voxels 8000 \
  --pc_max_num_points_per_voxel 75 \
  --pc_num_filters 48 96 96 \
  --num_data_loader_workers 4 \
  --gradient_accumulation_steps 3
```

### For 6GB VRAM (GTX 1060, RTX 2060)

```bash
python main.py \
  --batch_size 1 \
  --image_size 320 \
  --pc_max_num_voxels 6000 \
  --pc_max_num_points_per_voxel 50 \
  --pc_num_filters 32 64 64 \
  --num_data_loader_workers 2 \
  --gradient_accumulation_steps 4
```

### For 4GB VRAM (GTX 1050 Ti, GTX 1650)

```bash
python main.py \
  --batch_size 1 \
  --image_size 256 \
  --pc_max_num_voxels 4000 \
  --pc_max_num_points_per_voxel 40 \
  --pc_num_filters 32 48 48 \
  --num_data_loader_workers 2 \
  --gradient_accumulation_steps 6
```

## Monitoring Memory Usage

### Check GPU Memory

```bash
# Real-time monitoring
watch -n 1 nvidia-smi

# Or use Python
python -c "import torch; print(f'Allocated: {torch.cuda.memory_allocated()/1e9:.2f}GB')"
```

### Add Memory Logging to Training

```python
# Add to trainer.py
if batch_idx % 10 == 0:
    allocated = torch.cuda.memory_allocated() / 1e9
    reserved = torch.cuda.memory_reserved() / 1e9
    print(f"GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
```

## Performance vs Memory Trade-offs

| Optimization | Memory Saved | Training Speed | Accuracy Impact |
|-------------|--------------|----------------|-----------------|
| Batch size 3→1 | ~60% | -40% | None (with grad accum) |
| Image 448→384 | ~20% | +15% | Minimal (~1-2%) |
| Voxels 12k→8k | ~15% | +10% | Minimal (~1%) |
| Mixed precision | ~40% | +30% | Minimal (<1%) |
| Filters reduced | ~25% | +20% | Moderate (~3-5%) |

## Troubleshooting

### Out of Memory Error

```
RuntimeError: CUDA out of memory
```

**Solutions** (try in order):
1. Reduce batch size to 1
2. Reduce image size to 384 or 320
3. Reduce pc_max_num_voxels to 8000 or 6000
4. Reduce num_data_loader_workers to 2
5. Enable gradient checkpointing (advanced)

### Slow Training

If training is too slow after optimization:
1. Use gradient accumulation to simulate larger batches
2. Enable mixed precision training
3. Reduce validation frequency (`--val_period 2000`)
4. Use fewer data loader workers if CPU is bottleneck

### Memory Leak

If memory usage grows over time:
```python
# Add to training loop
torch.cuda.empty_cache()
gc.collect()
```

## Advanced Optimizations

### 1. Gradient Checkpointing

Trade computation for memory:
```python
from torch.utils.checkpoint import checkpoint

# In model forward pass
output = checkpoint(self.layer, input)
```

### 2. CPU Offloading

Move some tensors to CPU:
```python
# Keep labels on CPU until needed
labels = batch_data['label']  # Don't move to GPU immediately
```

### 3. Reduce Validation Frequency

```bash
--val_period 2000  # Validate every 2000 epochs instead of 1000
```

### 4. Disable Visualization During Training

```bash
--visualize_sample False
```

## Example Training Script

```bash
#!/bin/bash
# train_low_memory.sh

python main.py \
  --train_dir /mnt/fastDisk/kitti3d/kitti_object/training \
  --val_dir /mnt/fastDisk/kitti3d/kitti_object/training \
  --batch_size 1 \
  --image_size 384 \
  --pc_max_num_voxels 8000 \
  --pc_max_num_points_per_voxel 75 \
  --pc_num_filters 48 96 96 \
  --num_data_loader_workers 4 \
  --num_epochs 60 \
  --lr 1e-2 \
  --save_period 10 \
  --val_period 2000 \
  --use_wandb False
```

Make executable and run:
```bash
chmod +x train_low_memory.sh
./train_low_memory.sh
```

## Verification

Check if optimizations work:

```python
import torch
from main import get_args, main

# Test with low memory config
args = get_args([
    '--batch_size', '1',
    '--image_size', '384',
    '--pc_max_num_voxels', '8000'
])

print(f"GPU Available: {torch.cuda.is_available()}")
print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB")

# Run one iteration to check memory
# main(args)
```

## Summary

**Minimum Requirements**:
- GPU: 4GB VRAM (with heavy optimization)
- Recommended: 8GB VRAM
- Optimal: 12GB+ VRAM

**Best Practice**:
1. Start with batch_size=1
2. Use gradient accumulation for effective larger batches
3. Monitor memory with nvidia-smi
4. Adjust image_size and voxels based on available memory
5. Enable mixed precision if supported