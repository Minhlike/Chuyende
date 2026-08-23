import sys
import platform
try:
    import torch
    torch_ver = torch.__version__
    cuda_ver = torch.version.cuda
    device_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
except ImportError:
    torch_ver = "NotInstalled"
    cuda_ver = "None"
    device_name = "None"

print(f"PYTHON: {sys.version.split()[0]}")
print(f"TORCH: {torch_ver}")
print(f"CUDA: {cuda_ver}")
print(f"DEVICE: {device_name}")
print(f"PLATFORM: {platform.platform()}")
