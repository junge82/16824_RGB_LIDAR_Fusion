# RGB LiDAR Fusion Installation Guide for NVIDIA GeForce RTX 4060

This guide provides installation instructions specifically adapted for **NVIDIA GeForce RTX 4060** (Compute Capability sm_89).

## Hardware Requirements

- **GPU**: NVIDIA GeForce RTX 4060 (sm_89 architecture)
- **RAM**: 16GB+ recommended
- **Storage**: 20GB+ free space

## System Requirements

- **OS**: Ubuntu 20.04/22.04 (tested) or compatible Linux distribution
- **CUDA**: 11.8 or 12.x (RTX 4060 requires CUDA 11.8+)
- **Python**: 3.9 or 3.10
- **Conda**: Anaconda or Miniconda

## Pre-Installation Steps

### 1. Verify GPU and CUDA Compatibility

Check your GPU:
```bash
nvidia-smi
```

You should see your RTX 4060 listed. Note the CUDA version shown in the top right.

### 2. Install NVIDIA Drivers

If not already installed:
```bash
# Ubuntu 22.04
sudo ubuntu-drivers autoinstall
sudo reboot
```

Or install specific driver version:
```bash
sudo apt update
sudo apt install nvidia-driver-535  # or newer
sudo reboot
```

## Installation Methods

### Method 1: Conda Environment (Recommended for RTX 4060)

#### Step 1: Create Conda Environment

```bash
conda create -n rgb-fusion-rtx4060 python=3.10 -y
conda activate rgb-fusion-rtx4060
```

#### Step 2: Install PyTorch with CUDA 12.1 Support

For RTX 4060, use PyTorch with CUDA 12.1 or 11.8:

```bash
# Option A: CUDA 12.1 (Recommended for RTX 4060)
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Option B: CUDA 11.8 (Alternative)
# conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

#### Step 3: Install Core Dependencies

```bash
conda install scikit-image scipy numba pillow matplotlib flask pyqtgraph pyopengl -c conda-forge
```

#### Step 4: Install Python Packages

```bash
pip install fire tensorboardX protobuf opencv-python tqdm wandb scikit-learn
```

#### Step 5: Install spconv for RTX 4060

The original `spconv-cu113` is not compatible with RTX 4060. Use the newer version:

```bash
# For CUDA 12.1
pip install spconv-cu120

# For CUDA 11.8 (if you chose Option B above)
# pip install spconv-cu118
```

**Note**: If `spconv-cu120` is not available, you may need to build from source:

```bash
git clone https://github.com/traveller59/spconv.git --recursive
cd spconv
python setup.py bdist_wheel
pip install dist/spconv*.whl
cd ..
```

### Method 2: Quick Install Script for RTX 4060

Create and run this installation script:

```bash
#!/bin/bash
# install_rtx4060.sh

echo "Installing RGB LiDAR Fusion for RTX 4060..."

# Create environment
conda create -n rgb-fusion-rtx4060 python=3.10 -y
conda activate rgb-fusion-rtx4060

# Install PyTorch with CUDA 12.1
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install conda packages
conda install scikit-image scipy numba pillow matplotlib flask pyqtgraph pyopengl -c conda-forge -y

# Install pip packages
pip install fire tensorboardX protobuf opencv-python tqdm wandb scikit-learn

# Install spconv for CUDA 12.x
pip install spconv-cu120

echo "Installation complete! Activate with: conda activate rgb-fusion-rtx4060"
```

Make it executable and run:
```bash
chmod +x install_rtx4060.sh
./install_rtx4060.sh
```

## Verification

### Test PyTorch CUDA Support

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Compute Capability: {torch.cuda.get_device_capability(0)}")
```

Expected output should show:
- CUDA available: True
- GPU: NVIDIA GeForce RTX 4060
- Compute Capability: (8, 9)

### Test spconv Installation

```python
import spconv.pytorch as spconv
print(f"spconv version: {spconv.__version__}")
```

## Troubleshooting

### Issue 1: CUDA Version Mismatch

**Error**: `RuntimeError: CUDA error: no kernel image is available for execution on the device`

**Solution**: This means PyTorch was compiled for older architectures. Reinstall PyTorch with CUDA 12.1:
```bash
pip uninstall torch torchvision torchaudio
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### Issue 2: spconv Compatibility

**Error**: `ImportError: cannot import name 'spconv'` or CUDA errors with spconv

**Solution**: Build spconv from source with sm_89 support:
```bash
git clone https://github.com/traveller59/spconv.git --recursive
cd spconv
export TORCH_CUDA_ARCH_LIST="8.9"
python setup.py bdist_wheel
pip install dist/spconv*.whl
```

### Issue 3: Out of Memory Errors

**Error**: `CUDA out of memory`

**Solution**: RTX 4060 has 8GB VRAM. Reduce batch size in training:
```python
# In your training config
batch_size = 2  # Reduce from default
```

### Issue 4: Driver Version Too Old

**Error**: `CUDA driver version is insufficient for CUDA runtime version`

**Solution**: Update NVIDIA drivers:
```bash
sudo apt update
sudo apt install nvidia-driver-535  # or newer
sudo reboot
```

## Performance Optimization for RTX 4060

### 1. Enable TF32 (Tensor Float 32)

Add to your training script:
```python
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

### 2. Mixed Precision Training

Use automatic mixed precision to save memory:
```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

# In training loop
with autocast():
    output = model(input)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### 3. Gradient Checkpointing

For large models, enable gradient checkpointing to reduce memory:
```python
model.gradient_checkpointing_enable()
```

## Architecture-Specific Notes

### RTX 4060 (sm_89) Specifications

- **Compute Capability**: 8.9
- **CUDA Cores**: 3072
- **Tensor Cores**: 96 (4th Gen)
- **Memory**: 8GB GDDR6
- **Memory Bandwidth**: 272 GB/s
- **TDP**: 115W

### Recommended Settings

For optimal performance on RTX 4060:

```python
# Training configuration
config = {
    'batch_size': 2,           # Adjust based on model size
    'num_workers': 4,          # For data loading
    'pin_memory': True,        # Faster data transfer
    'mixed_precision': True,   # Enable AMP
    'gradient_accumulation': 4 # Simulate larger batch size
}
```

## Comparison with Original Setup

| Component | Original (CUDA 11.3) | RTX 4060 (CUDA 12.1) |
|-----------|---------------------|----------------------|
| PyTorch | 1.11.0 | 2.0+ |
| CUDA Toolkit | 11.3 | 12.1 |
| spconv | spconv-cu113 | spconv-cu120 |
| Compute Capability | sm_75, sm_80, sm_86 | sm_89 |
| Python | 3.9 | 3.10 |

## Additional Resources

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [spconv GitHub](https://github.com/traveller59/spconv)
- [RTX 4060 Specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4060-4060ti/)

## Running the Model

After installation, activate the environment and run:

```bash
conda activate rgb-fusion-rtx4060

# Test installation
python -c "import torch; print(torch.cuda.is_available())"

# Run training (adjust batch size for 8GB VRAM)
python main.py --batch_size 2 --mixed_precision
```

## Support

If you encounter issues specific to RTX 4060:

1. Check CUDA compatibility: `nvidia-smi`
2. Verify PyTorch sees GPU: `python -c "import torch; print(torch.cuda.get_device_name(0))"`
3. Check compute capability: Should be (8, 9)
4. Ensure driver version ≥ 525.60.13 for CUDA 12.1

## License

Same as original RGB LiDAR Fusion project.

## Acknowledgments

- Original project: [RGB LiDAR Fusion](https://kangkelvin.github.io/16824_RGB_LIDAR_Fusion/)
- Adapted for NVIDIA GeForce RTX 4060 (sm_89)