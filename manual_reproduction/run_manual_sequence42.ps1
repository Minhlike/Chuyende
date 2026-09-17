# =====================================================================
# KỊCH BẢN TÁI LẬP THỰC NGHIỆM ĐỘC LẬP: SEQUENCE_ONLY SEED 42
# Dự án: Chuyên đề chuyên sâu - Học biểu diễn đặc trưng log an ninh
# =====================================================================
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# 1. Tự động xác định thư mục gốc của repository (không hard-code)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
Set-Location $RepoRoot

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  KỊCH BẢN TÁI LẬP THỰC NGHIỆM: SEQUENCE_ONLY (SEED 42)" -ForegroundColor Cyan
Write-Host "  Repository Root: $RepoRoot" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# 2. Tìm kiếm Python thực thi (ưu tiên virtual environment, sau đó tới python hệ thống)
$PythonCandidates = @(
    (Join-Path $RepoRoot ".venv-stage-a2-cuda\Scripts\python.exe"),
    (Join-Path $RepoRoot ".venv\Scripts\python.exe"),
    "python"
)

$PythonExe = $null
foreach ($cand in $PythonCandidates) {
    if (Test-Path $cand) {
        $PythonExe = $cand
        break
    } elseif ($cand -eq "python") {
        $cmd = Get-Command "python" -ErrorAction SilentlyContinue
        if ($cmd) {
            $PythonExe = "python"
            break
        }
    }
}

if (-not $PythonExe) {
    Write-Error "[FAIL-FAST] Không tìm thấy Python thực thi hợp lệ. Vui lòng cài đặt môi trường ảo theo requirements-lock.txt."
    exit 1
}

Write-Host "[CHECK 1/5] Python executable: $PythonExe" -ForegroundColor Green

# 3. Kiểm tra GPU CUDA khả dụng
$CudaCheckCmd = '& "' + $PythonExe + '" -c "import torch; assert torch.cuda.is_available(), ''CUDA_UNAVAILABLE''; print(torch.cuda.get_device_name(0))"'
$CudaDevice = & $PythonExe -c "import torch; assert torch.cuda.is_available(), 'CUDA_UNAVAILABLE'; print(torch.cuda.get_device_name(0))" 2>&1
if ($LASTEXITCODE -ne 0 -or $CudaDevice -match "CUDA_UNAVAILABLE") {
    Write-Error "[FAIL-FAST] CUDA không khả dụng trên môi trường Python hiện tại: $CudaDevice. Bắt buộc có GPU NVIDIA và PyTorch CUDA."
    exit 1
}
Write-Host "[CHECK 2/5] CUDA Device: $CudaDevice" -ForegroundColor Green

# 4. Kiểm tra dung lượng đĩa trống (tối thiểu 2GB)
$Drive = (Get-Item $RepoRoot).PSDrive
if ($Drive -and $Drive.Free) {
    $FreeGB = [math]::Round($Drive.Free / 1GB, 2)
    if ($FreeGB -lt 2.0) {
        Write-Error "[FAIL-FAST] Dung lượng đĩa trống không đủ ($FreeGB GB < 2.0 GB yêu cầu)."
        exit 1
    }
    Write-Host "[CHECK 3/5] Dung lượng đĩa trống: $FreeGB GB (Đạt chuẩn > 2GB)" -ForegroundColor Green
} else {
    Write-Host "[CHECK 3/5] Bỏ qua kiểm tra đĩa (không thể đọc PSDrive.Free)" -ForegroundColor Yellow
}

# 5. Kiểm tra tệp dữ liệu bắt buộc và đối soát mã băm SHA-256
$RequiredDataFiles = @(
    @{
        Path = (Join-Path $RepoRoot "experiments\runs\data\hdfs\hdfs_ssl_train.pt")
        ExpectedSha = "0422677f5357494fbc587cac4b6de2004781e71d9b8087b4c8f9f0cd160f3363"
        Name = "hdfs_ssl_train.pt"
    },
    @{
        Path = (Join-Path $RepoRoot "experiments\runs\data\hdfs\hdfs_ssl_val.pt")
        ExpectedSha = "96bdab531c3545f4a0f0ed7f87e47cba985c2bc4cac7a3e6c04245b5c712fbe9"
        Name = "hdfs_ssl_val.pt"
    },
    @{
        Path = (Join-Path $RepoRoot "experiments\runs\data\hdfs\hdfs_vocab.json")
        ExpectedSha = "7631ce3beb6861845a043c7e49e156fe79b011b6d85228a060708d03fecb0f73"
        Name = "hdfs_vocab.json"
    },
    @{
        Path = (Join-Path $RepoRoot "experiments\runs\data\vault\hdfs_probe_labels_val.pt")
        ExpectedSha = "3364428ddbdf8d48744fc8a9492988a9467a88a4de3bf01ae8c9d106df460b1a"
        Name = "hdfs_probe_labels_val.pt"
    }
)

Write-Host "[CHECK 4/5] Kiểm tra tính sẵn sàng và mã băm toàn vẹn SHA-256 của tập dữ liệu..." -ForegroundColor Green
$DataHashes = @{}
foreach ($item in $RequiredDataFiles) {
    if (-not (Test-Path $item.Path)) {
        Write-Error "[FAIL-FAST] Thiếu tệp dữ liệu bắt buộc: $($item.Path). Vui lòng nạp artifact từ kho ngoại vi theo ARTIFACT-MANIFEST.json."
        exit 1
    }
    $actualHash = (Get-FileHash -Path $item.Path -Algorithm SHA256).Hash.ToLower()
    $DataHashes[$item.Name] = $actualHash
    if ($actualHash -ne $item.ExpectedSha.ToLower()) {
        Write-Error "[FAIL-FAST] Sai lệch mã băm SHA-256 cho tệp $($item.Name)! Thực tế: $actualHash | Kỳ vọng: $($item.ExpectedSha)"
        exit 1
    }
    Write-Host "  - $($item.Name): SHA-256 khớp chuẩn ($actualHash)" -ForegroundColor Gray
}

# 6. Khởi tạo thư mục chạy riêng biệt theo timestamp (không ghi đè lịch sử)
$Timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$RunDir = Join-Path $RepoRoot "manual_reproduction\runs\$Timestamp"
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
Write-Host "[CHECK 5/5] Khởi tạo thư mục phiên chạy: $RunDir" -ForegroundColor Green

# 7. Bắt đầu ghi nhật ký toàn diện (Transcript)
$TranscriptPath = Join-Path $RunDir "transcript.log"
Start-Transcript -Path $TranscriptPath -Append

$GitCommit = git rev-parse HEAD 2>&1
$GitStatus = git status --porcelain 2>&1

Write-Host "---------------------------------------------------------------------"
Write-Host "THÔNG TIN PHIÊN CHẠY (AUDIT METADATA):"
Write-Host "  Timestamp UTC: $([DateTime]::UtcNow.ToString('o'))"
Write-Host "  Git Commit:    $GitCommit"
Write-Host "  Python:        $PythonExe"
Write-Host "  CUDA Device:   $CudaDevice"
Write-Host "---------------------------------------------------------------------"

# 8. Snapshot danh sách các thư mục confirmatory trước khi chạy
$ConfDir = Join-Path $RepoRoot "experiments\nineplus\confirmatory"
if (-not (Test-Path $ConfDir)) {
    New-Item -ItemType Directory -Path $ConfDir -Force | Out-Null
}
$PreExistingDirs = @(Get-ChildItem -Directory -Path $ConfDir -Filter "CONF_SEQUENCE_ONLY_seed42_*" | Select-Object -ExpandProperty Name)

# 9. Thiết lập biến môi trường xác định và kích hoạt chạy huấn luyện
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"

Write-Host "`n>>> BẮT ĐẦU HUẤN LUYỆN: python scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda" -ForegroundColor Yellow
$RunnerScript = Join-Path $RepoRoot "scripts\run_nineplus_confirmatory.py"

& $PythonExe $RunnerScript --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda --base-dir $RepoRoot
$RunExitCode = $LASTEXITCODE

Write-Host ">>> TIẾN TRÌNH HUẤN LUYỆN KẾT THÚC VỚI EXIT CODE: $RunExitCode" -ForegroundColor Yellow

# 10. Nhận diện chính xác thư mục vừa sinh ra bằng cách so sánh danh sách trước/sau
$PostExistingDirs = @(Get-ChildItem -Directory -Path $ConfDir -Filter "CONF_SEQUENCE_ONLY_seed42_*" | Select-Object -ExpandProperty Name)
$NewRuns = @($PostExistingDirs | Where-Object { $_ -notin $PreExistingDirs })

$GeneratedRunDir = $null
$ManifestData = $null
$BestCkptSha = $null

if ($NewRuns.Count -eq 1) {
    $NewRunId = $NewRuns[0]
    $GeneratedRunDir = Join-Path $ConfDir $NewRunId
    Write-Host "`n[KẾT QUẢ] Đã nhận diện đúng thư mục chạy mới: $GeneratedRunDir" -ForegroundColor Green

    $ManifestFile = Join-Path $GeneratedRunDir "RUN-MANIFEST.json"
    $TrainLogFile = Join-Path $GeneratedRunDir "TRAIN-LOG.jsonl"
    $BestCkptFile = Join-Path $GeneratedRunDir "best_checkpoint.pt"

    if (Test-Path $ManifestFile) {
        $ManifestData = Get-Content $ManifestFile -Raw | ConvertFrom-Json
    }
    if (Test-Path $BestCkptFile) {
        $BestCkptSha = (Get-FileHash -Path $BestCkptFile -Algorithm SHA256).Hash.ToLower()
    }
} elseif ($NewRuns.Count -gt 1) {
    $JoinedNewRuns = $NewRuns -join ', '
    Write-Warning "Phát hiện nhiều hơn 1 thư mục mới sinh ra trong confirmatory: $JoinedNewRuns"
} else {
    Write-Warning "Không phát hiện thư mục mới nào trong confirmatory (có thể huấn luyện gặp lỗi hoặc bị ngắt sớm)."
}

# 11. Tạo báo cáo tóm tắt phiên chạy: MANUAL_RUN_SUMMARY.txt
$SummaryFile = Join-Path $RunDir "MANUAL_RUN_SUMMARY.txt"
$NowUtcStr = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$TrainHash = $DataHashes["hdfs_ssl_train.pt"]
$ValHash = $DataHashes["hdfs_ssl_val.pt"]
$VocabHash = $DataHashes["hdfs_vocab.json"]
$ProbeHash = $DataHashes["hdfs_probe_labels_val.pt"]

$SummaryLines = @(
    "=====================================================================",
    "BÁO CÁO TÁI LẬP THỰC NGHIỆM ĐỘC LẬP (MANUAL RUN SUMMARY)",
    "=====================================================================",
    "Thời gian thực hiện (UTC): $NowUtcStr",
    "Thư mục lưu trữ phiên chạy:  $RunDir",
    "Git Commit SHA:            $GitCommit",
    "Môi trường Python:          $PythonExe",
    "Thiết bị CUDA:              $CudaDevice",
    "Trạng thái Exit Code:      $RunExitCode",
    "",
    "THÔNG TIN ĐẦU VÀO VÀ MÃ BĂM DỮ LIỆU:",
    "  - hdfs_ssl_train.pt:       $TrainHash",
    "  - hdfs_ssl_val.pt:         $ValHash",
    "  - hdfs_vocab.json:         $VocabHash",
    "  - hdfs_probe_labels_val.pt: $ProbeHash",
    "",
    "KẾT QUẢ THỰC NGHIỆM ĐẠT ĐƯỢC:",
    "  - Thư mục Confirmatory:    $GeneratedRunDir",
    "  - Mã đợt chạy (run_id):     $($ManifestData.run_id)",
    "  - Số Epochs thực tế:        $($ManifestData.total_epochs_trained)",
    "  - Best Epoch:              $($ManifestData.best_epoch) (Kỳ vọng: 3)",
    "  - Best Val Loss:           $($ManifestData.best_val_loss) (Kỳ vọng xấp xỉ 1.1577)",
    "  - Early Stopping:          $($ManifestData.early_stopped) (Dừng sớm tại Epoch 6 với patience=3)",
    "  - Probe Average Precision: $($ManifestData.probe_ap) (Kỳ vọng xấp xỉ 1.0000)",
    "  - Probe ROC-AUC:           $($ManifestData.probe_roc_auc) (Kỳ vọng xấp xỉ 1.0000)",
    "  - Peak VRAM ghi nhận:      $($ManifestData.peak_vram_mb) MB",
    "  - SHA-256 Checkpoint mới:  $BestCkptSha",
    "====================================================================="
)

$SummaryLines | Out-File -FilePath $SummaryFile -Encoding utf8
Write-Host "`nĐã lưu báo cáo đối soát tại: $SummaryFile" -ForegroundColor Cyan

# 12. Kết thúc Transcript
Stop-Transcript

Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "  HOÀN TẤT PHIÊN TÁI LẬP THỰC NGHIỆM ĐỘC LẬP!" -ForegroundColor Green
Write-Host "  Vui lòng xem chi tiết tại: $SummaryFile" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
