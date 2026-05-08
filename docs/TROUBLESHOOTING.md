# Troubleshooting Guide

## Common Issues and Solutions

### 1. CUDA Version Mismatch Error

**Error:**
```
RuntimeError: Detected that PyTorch and torchvision were compiled with different CUDA major versions.
```

**Solution:**
Run the fix script to reinstall PyTorch packages with matching CUDA versions:

```bash
cd 16824_RGB_LIDAR_Fusion
chmod +x fix_cuda_mismatch.sh
./fix_cuda_mismatch.sh
```

**Manual Fix:**
```bash
conda activate rgb-fusion-rtx4060  # or your environment name
pip uninstall torch torchvision torchaudio -y
conda uninstall pytorch torchvision torchaudio pytorch-cuda -y --force
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

---

### 2. Weights & Biases (wandb) Permission Error

**Error:**
```
wandb.errors.errors.CommError: Error uploading run: returned error 403
{"message":"permission denied","path":["upsertBucket"],"extensions":{"code":"PERMISSION_ERROR"}}
```

**Cause:** The code tries to use entity "16824_rgb_lidar_fusion" which you don't have access to.

**Solution 1: Disable wandb (Recommended for quick testing)**
```bash
python main.py --use_wandb False [other arguments]
```

**Solution 2: Use your personal wandb account**

The code has been updated to use your personal wandb account. Just make sure you're logged in:
```bash
wandb login
```
Then enter your API key from https://wandb.ai/authorize

**Solution 3: Run in offline mode**
```bash
export WANDB_MODE=offline
python main.py [arguments]
```

---

### 3. Running the Training

**Basic command (without wandb):**
```bash
python main.py --use_wandb False
```

**With wandb (using your personal account):**
```bash
wandb login  # First time only
python main.py
```

**Full example with custom parameters:**
```bash
python main.py \
  --use_wandb False \
  --batch_size 4 \
  --num_epochs 50 \
  --lr 0.001 \
  --device cuda
```

---

### 4. Environment Issues

**If conda environment doesn't exist:**
```bash
cd 16824_RGB_LIDAR_Fusion
chmod +x install_rtx4060.sh
./install_rtx4060.sh
```

**If using a different environment name:**
Edit the fix script and replace `rgb-fusion-rtx4060` with your environment name.

---

### 5. GPU Not Detected

**Check NVIDIA driver:**
```bash
nvidia-smi
```

**Check PyTorch CUDA availability:**
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

**If CUDA is not available:**
- Verify NVIDIA drivers are installed
- Ensure PyTorch was installed with CUDA support
- Check that your GPU is compatible (RTX 4060 requires compute capability 8.9)

---

## Quick Reference

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--use_wandb` | True | Enable/disable Weights & Biases logging |
| `--batch_size` | 4 | Training batch size |
| `--num_epochs` | 50 | Number of training epochs |
| `--lr` | 0.001 | Learning rate |
| `--device` | cuda | Device to use (cuda/cpu) |

### File Locations

- Main training script: `main.py`
- Installation script: `install_rtx4060.sh`
- CUDA fix script: `fix_cuda_mismatch.sh`
- Quick start guide: `RTX4060_QUICK_START.md`

---

## Getting Help

If you encounter other issues:

1. Check the error message carefully
2. Verify your environment is activated: `conda activate rgb-fusion-rtx4060`
3. Check GPU status: `nvidia-smi`
4. Verify PyTorch installation: `python -c "import torch; print(torch.__version__)"`
5. Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`

---

*Last updated: 2026-04-10*