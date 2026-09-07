# STAGE-A2 HARDWARE TRAINING PROFILE: THE SWEET SPOT SPECIFICATION

## 1. Context & The Windows Performance Choke Root Cause
During nocturnal training on the Acer laptop with discrete NVIDIA RTX 3050 Laptop GPU:
- **User Constraint:** The laptop must remain **physically OPEN** with the display set to turn off automatically after **20 seconds** of inactivity (VIDEOIDLE = 20s). The training noise must remain virtually silent and temperatures cool (~52°C) so the user can rest.
- **The Windows Choke Mechanism:** When the screen turned off, default Windows power policies applied:
  1. SUB_PCIEXPRESS ASPM = 2 (Maximum Link State Power Savings): throttled the PCIe bus between system RAM and GPU VRAM.
  2. SUB_PROCESSOR PROCTHROTTLEMIN = 5%: aggressively downclocked the CPU to ~800 MHz when display was inactive.
  3. The PCIe latency created high wait times for graph batch transfer. The GPU went idle between steps, triggering NVIDIA Optimus to force the GPU into P8 power state (210 MHz / 6.7W).
  4. **Consequence:** An epoch took **~4 hours (240+ minutes)** instead of ~95 minutes!

---

## 2. The Proven Sweet Spot Configuration (Under 100 Mins / Silent)
Empirically proven in Seed 7 Epochs 6 & 7:
- **Epoch 6 Runtime:** 94.5 minutes (Val loss: 3.0235)
- **Epoch 7 Runtime:** 94.3 minutes (Val loss: 1.9751 ⭐ Sub-2.0 record)
- **GPU Stats:** 795 MHz (P5 steady state), 9.69W - 10.39W, 52°C, silent fan noise.

### Power & Hardware Directives:
`powershell
# 1. Acer Power Scheme (Active)
powercfg /setactive 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13

# 2. Display auto-off after 20s
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_VIDEO VIDEOIDLE 20

# 3. Disable PCIe ASPM (NO PCIe throttling)
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_PCIEXPRESS ASPM 0

# 4. Disable Disk Idle
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_DISK DISKIDLE 0

# 5. Floor CPU Minimum at 60% (~2.2 GHz base clock)
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_PROCESSOR PROCTHROTTLEMIN 60

# 6. Cap CPU Maximum at 99% (Prevents aggressive Turbo Boost fan whine & overheating)
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_PROCESSOR PROCTHROTTLEMAX 99

# 7. Disable Sleep & Lid action
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_SLEEP STANDBYIDLE 0
powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_BUTTONS LIDACTION 0

# 8. Set Process Priority
# The Python training worker process MUST have PriorityClass = AboveNormal.
`

---

## 3. Automation Scripts
- **Activate Sweet Spot:** D:\Research\scripts\set_training_sweetspot.ps1
- **Restore Normal Mode:** D:\Research\scripts\restore_normal_profile.ps1
- **Resume Seed 7 Epoch 8:** D:\Research\scripts\resume_stage_a2_local_seed7_epoch8.ps1
  - Last Checkpoint: D:\Research\.artifacts\stage-a2\HDFS\seed-7\last_checkpoint.pt
  - SHA-256: 529b6c8230a42f083dd611ea2cf58b9eb9e183a212f7611d0db0223070e3a850
