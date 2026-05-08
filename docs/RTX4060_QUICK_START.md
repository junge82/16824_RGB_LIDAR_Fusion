# RTX 4060 Quick Start Guide

Quick reference for installing and running RGB LiDAR Fusion on NVIDIA GeForce RTX 4060.

## Prerequisites

- NVIDIA GeForce RTX 4060
- Ubuntu 20.04/22.04
- NVIDIA Driver ≥ 525.60.13
- Conda installed

## Quick Install (3 Steps)

### 1. Make script executable and run
```bash
cd 16824_RGB_LIDAR_Fusion
chmod +x install_rtx4060.sh
./install_rtx4060.sh
```

### 2. Activate environment
```bash
conda activate rgb-fusion-rtx4060
```

### 3. Verify installation
```bash
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}, Compute: {torch.cuda.get_device_capability(0)}')"
```

Expected output: `GPU: NVIDIA GeForce RTX 4060, Compute: (8, 9)`

## Key Differences from Original Setup

| Component | Original | RTX 4060 |
|-----------|----------|----------|
| CUDA | 11.3 | 12.1 |
| PyTorch | 1.11.0 | 2.0+ |
| spconv | cu113 | cu120 |
| Python | 3.9 | 3.10 |
| Compute Cap | sm_75/80/86 | sm_89 |

## Memory Optimization (8GB VRAM)

RTX 4060 has 8GB VRAM. Use these settings:

```python
# Reduce batch size
batch_size = 2  # or 1 for large models

# Enable mixed precision
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Use gradient accumulation
gradient_accumulation_steps = 4
```

## Common Issues

### Issue: "no kernel image available"
**Fix**: Reinstall PyTorch with CUDA 12.1
```bash
pip uninstall torch torchvision torchaudio
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
```

### Issue: Out of memory
**Fix**: Reduce batch size to 1 or 2
```python
batch_size = 1
```

### Issue: spconv not found
**Fix**: Build from source
```bash
git clone https://github.com/traveller59/spconv.git --recursive
cd spconv
export TORCH_CUDA_ARCH_LIST="8.9"
python setup.py bdist_wheel
pip install dist/spconv*.whl
```

## Performance Tips

1. **Enable TF32**: Faster computation on RTX 4060
   ```python
   torch.backends.cuda.matmul.allow_tf32 = True
   ```

2. **Use AMP**: Automatic Mixed Precision saves memory
   ```python
   from torch.cuda.amp import autocast, GradScaler
   scaler = GradScaler()
   ```

3. **Pin Memory**: Faster data loading
   ```python
   DataLoader(..., pin_memory=True)
   ```

## Running the Model

```bash
# Activate environment
conda activate rgb-fusion-rtx4060

# Run with optimized settings for RTX 4060
python main.py \
  --batch_size 2 \
  --mixed_precision \
  --gradient_accumulation 4
```

## Full Documentation

See [`INSTALL_RTX4060.md`](INSTALL_RTX4060.md) for complete installation guide and troubleshooting.

## Verification Checklist

- [ ] NVIDIA driver ≥ 525.60.13 installed
- [ ] `nvidia-smi` shows RTX 4060
- [ ] Conda environment created
- [ ] PyTorch with CUDA 12.1 installed
- [ ] `torch.cuda.is_available()` returns `True`
- [ ] Compute capability is (8, 9)
- [ ] spconv imports successfully

## Support

For RTX 4060-specific issues, check:
1. Driver version: `nvidia-smi`
2. CUDA version: `python -c "import torch; print(torch.version.cuda)"`
3. Compute capability: `python -c "import torch; print(torch.cuda.get_device_capability(0))"`

Expected: Driver ≥ 525, CUDA 12.1, Compute (8, 9)