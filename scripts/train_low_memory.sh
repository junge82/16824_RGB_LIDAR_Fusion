#!/bin/bash
# train_low_memory.sh - Memory-optimized training script for GPUs with limited VRAM

echo "=========================================="
echo "RGB LiDAR Fusion - Low Memory Training"
echo "=========================================="

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo "GPU Information:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
else
    echo "Warning: nvidia-smi not found. Make sure CUDA is installed."
fi

# Memory-optimized settings for 8GB VRAM
python main.py \
  --data_dir /mnt/fastDisk/kitti3d/kitti_object/training \
  --batch_size 2 \
  --image_size 384 \
  --pc_max_num_voxels 8000 \
  --pc_max_num_points_per_voxel 75 \




echo ""
echo "=========================================="
echo "Training Complete!"
echo "=========================================="

# Made with Bob
