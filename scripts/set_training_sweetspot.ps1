# scripts/set_training_sweetspot.ps1
# Định cấu hình phần cứng và nguồn điện Windows cho Sweet Spot huấn luyện
# Mục tiêu: Thời gian chạy Epoch <= 100 phút, GPU không bị thiếu dữ liệu đầu vào (zero GPU starvation), quạt im lặng (52C), màn hình tắt sau 20 giây.

$ErrorActionPreference = "Stop"

$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13" # Acer Scheme

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CONFIGURING HARDWARE SWEET SPOT PROFILE FOR TRAINING " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Kích hoạt sơ đồ Acer
powercfg /setactive $schemeGuid

# 2. Tắt tính năng tự động tắt màn hình (Người dùng sử dụng nút bật tắt đèn nền phần cứng Fn + F6)
powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 0
powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 0

# 3. CRITICAL: Vô hiệu hóa PCIe ASPM (Ngăn chặn độ trễ truyền hàng loạt RAM->VRAM)
powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0
powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0

# 4. CRITICAL: Tắt Disk Idle (Ngăn chặn chế độ ngủ SSD/HDD)
powercfg /setacvalueindex $schemeGuid SUB_DISK DISKIDLE 0
powercfg /setdcvalueindex $schemeGuid SUB_DISK DISKIDLE 0

# 5. CRITICAL: Tầng CPU Trạng thái tối thiểu ở mức 60% (xung nhịp cơ bản ~2,2 GHz)
# (Ngăn Windows hạ xung CPU xuống 800 MHz khi màn hình tắt)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 60
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 60

# 6. CRITICAL: Giới hạn CPU Trạng thái tối đa ở mức 99%
# (Vô hiệu hóa các xung điện áp Intel/AMD Turbo Boost mạnh mẽ -> quạt im lặng, không quá nóng, trạng thái ổn định 52C)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99

# 7. Chính sách ngủ và đóng nắp máy (sleep and lid policy)
powercfg /setacvalueindex $schemeGuid SUB_SLEEP STANDBYIDLE 0
powercfg /setdcvalueindex $schemeGuid SUB_SLEEP STANDBYIDLE 0
powercfg /setacvalueindex $schemeGuid SUB_BUTTONS LIDACTION 0
powercfg /setdcvalueindex $schemeGuid SUB_BUTTONS LIDACTION 0

# 8. Áp dụng lại chương trình đang hoạt động
powercfg /setactive $schemeGuid

# 9. Đảm bảo tùy chọn GPU hiệu suất cao DirectX cho Python
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
Write-Host " - Screen Off: 0 (Always ON, hardware Fn+F6 for backlight)"
Write-Host " - PCIe ASPM: 0 (OFF - No GPU starvation)"
Write-Host " - CPU Min: 60% (Base ~2.2 GHz - No downclock)"
Write-Host " - CPU Max: 99% (Turbo disabled - Silent fans & 52C)"
Write-Host " - GPU Pref: High Performance (DirectX GpuPreference=2)"
Write-Host "==========================================================" -ForegroundColor Cyan
