# tập lệnh/restore_normal_profile.ps1
# Khôi phục phần cứng và nguồn Windows về cấu hình sử dụng bình thường hàng ngày

$ErrorActionPreference = "Stop"

$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13" # Acer Scheme

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " RESTORING HARDWARE PROFILE TO NORMAL EVERYDAY DEFAULTS " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Hiển thị tự động tắt đến 5 phút (AC) và 3 phút (DC)
powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 300
powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 180

# 2. Khôi phục PCIe ASPM về mức tiết kiệm điện năng tối đa (mặc định của Windows)
powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2
powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2

# 3. Khôi phục Disk Idle về mặc định (20 phút = 1200 giây)
powercfg /setacvalueindex $schemeGuid SUB_DISK DISKIDLE 1200
powercfg /setdcvalueindex $schemeGuid SUB_DISK DISKIDLE 1200

# 4. Khôi phục trạng thái Tối thiểu của CPU về 5% (Cho phép CPU chạy không tải và chạy mát đối với các tác vụ nhẹ)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5

# 5. Khôi phục trạng thái Tối đa của CPU về 99% (giữ cho quạt yên tĩnh khi không hoạt động)
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99

# 6. Áp dụng lại chương trình đang hoạt động
powercfg /setactive $schemeGuid

Write-Host "Hardware profile restored to normal defaults:" -ForegroundColor Green
Write-Host " - Power Scheme: Acer ($schemeGuid)"
Write-Host " - Screen Off: 5 minutes (AC) / 3 minutes (DC)"
Write-Host " - PCIe ASPM: 2 (Default power savings)"
Write-Host " - CPU Min: 5% (Normal idle)"
Write-Host " - CPU Max: 99% (Silent fans)"
Write-Host "==========================================================" -ForegroundColor Cyan
