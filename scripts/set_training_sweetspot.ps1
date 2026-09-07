# scripts/set_training_sweetspot.ps1
# Configures Windows Hardware & Power for Training Sweet Spot
# Target: Epoch runtime <= 100 minutes, zero GPU starvation, silent fans (52C), screen turns off after 20s.

$ErrorActionPreference = "Stop"

$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13" # Acer Scheme

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CONFIGURING HARDWARE SWEET SPOT PROFILE FOR TRAINING " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Activate Acer Scheme
powercfg /setactive $schemeGuid

# 2. Display auto-off after 20 seconds (user constraint: laptop OPEN, screen off)
powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 20
powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 20

# 3. CRITICAL: Disable PCIe ASPM (Prevents RAM->VRAM batch transfer latency choke)
powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0
powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0

# 4. CRITICAL: Disable Disk Idle (Prevents SSD/HDD sleep)
powercfg /setacvalueindex $schemeGuid SUB_DISK DISKIDLE 0
powercfg /setdcvalueindex $schemeGuid SUB_DISK DISKIDLE 0

# 5. CRITICAL: Floor CPU Minimum state at 60% (~2.2 GHz base clock)
# (Prevents Windows from downclocking CPU to 800MHz when screen turns off)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 60
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 60

# 6. CRITICAL: Cap CPU Maximum state at 99%
# (Disables aggressive Intel/AMD Turbo Boost voltage spikes -> silent fans, no overheating, 52C steady state)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99

# 7. Sleep & Lid Policies
powercfg /setacvalueindex $schemeGuid SUB_SLEEP STANDBYIDLE 0
powercfg /setdcvalueindex $schemeGuid SUB_SLEEP STANDBYIDLE 0
powercfg /setacvalueindex $schemeGuid SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex $schemeGuid SUB_BUTTONS LIDACTION 0

# 8. Re-apply active scheme
powercfg /setactive $schemeGuid

# 9. Ensure DirectX High Performance GPU preference for Python
$regKey = "HKCU:\Software\Microsoft\DirectX\UserGpuPreferences"
if (-not (Test-Path $regKey)) {
    New-Item -Path $regKey -Force | Out-Null
}
$pythonExe1 = "D:\Research\.venv-stage-a2-cuda\Scripts\python.exe"
$pythonExe2 = "C:\Users\Acer\AppData\Local\Programs\Python\Python310\python.exe"
if (Test-Path $pythonExe1) {
    Set-ItemProperty -Path $regKey -Name $pythonExe1 -Value "GpuPreference=2;"
}
if (Test-Path $pythonExe2) {
    Set-ItemProperty -Path $regKey -Name $pythonExe2 -Value "GpuPreference=2;"
}

Write-Host "Hardware profile configured successfully:" -ForegroundColor Green
Write-Host " - Power Scheme: Acer ($schemeGuid)"
Write-Host " - Screen Off: 20 seconds"
Write-Host " - PCIe ASPM: 0 (OFF - No GPU starvation)"
Write-Host " - CPU Min: 60% (Base ~2.2 GHz - No downclock)"
Write-Host " - CPU Max: 99% (Turbo disabled - Silent fans & 52C)"
Write-Host " - GPU Pref: High Performance (DirectX GpuPreference=2)"
Write-Host "==========================================================" -ForegroundColor Cyan
