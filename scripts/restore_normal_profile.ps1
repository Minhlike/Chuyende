# scripts/restore_normal_profile.ps1
# Restores Windows Hardware & Power to Normal Everyday Usage Profile

$ErrorActionPreference = "Stop"

$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13" # Acer Scheme

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " RESTORING HARDWARE PROFILE TO NORMAL EVERYDAY DEFAULTS " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Display auto-off to 5 minutes (AC) and 3 minutes (DC)
powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 300
powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 180

# 2. Restore PCIe ASPM to Maximum power savings (Windows default)
powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2
powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2

# 3. Restore Disk Idle to default (20 mins = 1200s)
powercfg /setacvalueindex $schemeGuid SUB_DISK DISKIDLE 1200
powercfg /setdcvalueindex $schemeGuid SUB_DISK DISKIDLE 1200

# 4. Restore CPU Minimum state to 5% (Allows CPU to idle down and run cool on light tasks)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5

# 5. Restore CPU Maximum state to 99% (keeps fans quiet on idle)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99

# 6. Re-apply active scheme
powercfg /setactive $schemeGuid

Write-Host "Hardware profile restored to normal defaults:" -ForegroundColor Green
Write-Host " - Power Scheme: Acer ($schemeGuid)"
Write-Host " - Screen Off: 5 minutes (AC) / 3 minutes (DC)"
Write-Host " - PCIe ASPM: 2 (Default power savings)"
Write-Host " - CPU Min: 5% (Normal idle)"
Write-Host " - CPU Max: 99% (Silent fans)"
Write-Host "==========================================================" -ForegroundColor Cyan
