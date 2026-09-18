# =====================================================================
# KỊCH BẢN TÁI LẬP THỰC NGHIỆM ĐỘC LẬP: SEQUENCE_ONLY SEED 42
# Dự án: Chuyên đề chuyên sâu - Học biểu diễn đặc trưng log an ninh
# =====================================================================
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# 1. Thiết lập biến môi trường xác định TRƯỚC MỌI CHECK PYTHON/CUDA
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"

# 2. Tự động xác định thư mục gốc của repository (không hard-code)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path
Set-Location $RepoRoot

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  KỊCH BẢN TÁI LẬP THỰC NGHIỆM: SEQUENCE_ONLY (SEED 42)" -ForegroundColor Cyan
Write-Host "  Repository Root: $RepoRoot" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

# 3. Tìm kiếm Python thực thi (ưu tiên virtual environment, sau đó tới python hệ thống)
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

# 4. Chạy gpu_smoke_test.py - Dừng ngay lập tức nếu exit code != 0
Write-Host "`n>>> [BƯỚC 1/6] CHẠY GPU SMOKE TEST KIỂM SOÁT ĐIỀU KIỆN TIÊN QUYẾT..." -ForegroundColor Yellow
$SmokeScript = Join-Path $RepoRoot "scripts\gpu_smoke_test.py"
& $PythonExe $SmokeScript
$SmokeExitCode = $LASTEXITCODE
if ($SmokeExitCode -ne 0) {
    Write-Error "[FAIL-FAST] gpu_smoke_test.py thất bại (Exit code: $SmokeExitCode). Dừng kịch bản ngay lập tức."
    exit 1
}

# 5. Đọc ARTIFACT-MANIFEST.json để lấy expected hashes cho dữ liệu bắt buộc
Write-Host "`n>>> [BƯỚC 2/6] ĐỐI SOÁT MÃ BĂM DỮ LIỆU TỪ ARTIFACT-MANIFEST.json..." -ForegroundColor Yellow
$ManifestPath = Join-Path $RepoRoot "experiments\nineplus\ARTIFACT-MANIFEST.json"
if (-not (Test-Path $ManifestPath)) {
    Write-Error "[FAIL-FAST] Không tìm thấy ARTIFACT-MANIFEST.json tại: $ManifestPath"
    exit 1
}

$ArtifactManifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$ArtifactMap = @{}
foreach ($art in $ArtifactManifest.artifacts) {
    $normPath = $art.relative_path.Replace("/", "\")
    $ArtifactMap[$normPath] = $art
}

$RequiredFiles = @(
    "experiments\runs\data\hdfs\hdfs_ssl_train.pt",
    "experiments\runs\data\hdfs\hdfs_ssl_val.pt",
    "experiments\runs\data\hdfs\hdfs_vocab.json",
    "experiments\runs\data\vault\hdfs_probe_labels_val.pt"
)

$DataHashes = @{}
foreach ($relPath in $RequiredFiles) {
    $fullPath = Join-Path $RepoRoot $relPath
    $fileName = Split-Path -Leaf $relPath

    if (-not (Test-Path $fullPath)) {
        Write-Error "[FAIL-FAST] Tệp dữ liệu bắt buộc không tồn tại: $relPath"
        exit 1
    }

    if (-not $ArtifactMap.ContainsKey($relPath)) {
        Write-Error "[FAIL-FAST] Tệp $relPath không được kê khai trong ARTIFACT-MANIFEST.json"
        exit 1
    }

    $artMeta = $ArtifactMap[$relPath]
    if ($artMeta.availability -eq "UNVERIFIED_LOCAL_ONLY") {
        Write-Error "[FAIL-FAST] Tệp $relPath có trạng thái UNVERIFIED_LOCAL_ONLY trong manifest"
        exit 1
    }

    if (-not $artMeta.sha256) {
        Write-Error "[FAIL-FAST] Tệp $relPath thiếu mã băm sha256 trong ARTIFACT-MANIFEST.json"
        exit 1
    }

    $actualHash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash.ToLower()
    $expectedHash = $artMeta.sha256.ToLower()

    if ($actualHash -ne $expectedHash) {
        Write-Error "[FAIL-FAST] Sai lệch mã băm SHA-256 cho $fileName! Thực tế: $actualHash | Kỳ vọng: $expectedHash"
        exit 1
    }

    $DataHashes[$fileName] = $actualHash
    Write-Host "  [OK] $fileName : $actualHash" -ForegroundColor Green
}

# 6. Khởi tạo thư mục phiên chạy
$Timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$RunDir = Join-Path $RepoRoot "manual_reproduction\runs\$Timestamp"
New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
$SummaryFile = Join-Path $RunDir "MANUAL_RUN_SUMMARY.txt"
$TranscriptPath = Join-Path $RunDir "transcript.log"

$RunSucceeded = $false
try {
    Start-Transcript -Path $TranscriptPath -Append

    $GitCommit = (git rev-parse HEAD 2>&1).Trim()
    $GitStatus = (git status --porcelain 2>&1)
    $GitDirty = if ($GitStatus) { "DIRTY ($($GitStatus.Count) modified/untracked files)" } else { "CLEAN" }

    $PkgInfo = & $PythonExe -c "import sys, torch; print(f'Python: {sys.version.split()[0]} | PyTorch: {torch.__version__} | CUDA: {torch.version.cuda} | Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"

    Write-Host "`n---------------------------------------------------------------------"
    Write-Host "THÔNG TIN PHIÊN CHẠY (AUDIT METADATA):"
    Write-Host "  Timestamp UTC: $([DateTime]::UtcNow.ToString('o'))"
    Write-Host "  Git Commit:    $GitCommit"
    Write-Host "  Git Status:    $GitDirty"
    Write-Host "  Runtime:       $PkgInfo"
    Write-Host "---------------------------------------------------------------------"

    $ConfDir = Join-Path $RepoRoot "experiments\nineplus\confirmatory"
    if (-not (Test-Path $ConfDir)) {
        New-Item -ItemType Directory -Path $ConfDir -Force | Out-Null
    }
    $PreExistingDirs = @(Get-ChildItem -Directory -Path $ConfDir -Filter "CONF_SEQUENCE_ONLY_seed42_*" | Select-Object -ExpandProperty Name)

    # 7. Kích hoạt huấn luyện
    Write-Host "`n>>> [BƯỚC 3/6] BẮT ĐẦU HUẤN LUYỆN: python scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda" -ForegroundColor Yellow
    $RunnerScript = Join-Path $RepoRoot "scripts\run_nineplus_confirmatory.py"
    & $PythonExe $RunnerScript --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda --base-dir $RepoRoot
    $TrainExitCode = $LASTEXITCODE

    if ($TrainExitCode -ne 0) {
        throw "[FAIL-FAST] Tiến trình huấn luyện kết thúc với mã lỗi $TrainExitCode (khác 0)."
    }

    # 8. Nhận diện chính xác 1 thư mục mới
    Write-Host "`n>>> [BƯỚC 4/6] NHẬN DIỆN THƯ MỤC KẾT QUẢ MỚI..." -ForegroundColor Yellow
    $PostExistingDirs = @(Get-ChildItem -Directory -Path $ConfDir -Filter "CONF_SEQUENCE_ONLY_seed42_*" | Select-Object -ExpandProperty Name)
    $NewRuns = @($PostExistingDirs | Where-Object { $_ -notin $PreExistingDirs })

    if ($NewRuns.Count -ne 1) {
        throw "[FAIL-FAST] Yêu cầu chính xác 1 thư mục kết quả mới sinh ra, nhưng phát hiện: $($NewRuns.Count) thư mục ($($NewRuns -join ', '))"
    }

    $GeneratedRunDir = Join-Path $ConfDir $NewRuns[0]
    Write-Host "  Thư mục mới: $GeneratedRunDir" -ForegroundColor Green

    # 9. Kiểm tra 3 tệp bắt buộc
    $ManifestFile = Join-Path $GeneratedRunDir "RUN-MANIFEST.json"
    $TrainLogFile = Join-Path $GeneratedRunDir "TRAIN-LOG.jsonl"
    $BestCkptFile = Join-Path $GeneratedRunDir "best_checkpoint.pt"

    if (-not (Test-Path $ManifestFile)) { throw "[FAIL-FAST] Thiếu tệp RUN-MANIFEST.json tại $GeneratedRunDir" }
    if (-not (Test-Path $TrainLogFile)) { throw "[FAIL-FAST] Thiếu tệp TRAIN-LOG.jsonl tại $GeneratedRunDir" }
    if (-not (Test-Path $BestCkptFile)) { throw "[FAIL-FAST] Thiếu tệp best_checkpoint.pt tại $GeneratedRunDir" }

    # 10. Kiểm tra tính hợp lệ của manifest mới
    Write-Host "`n>>> [BƯỚC 5/6] KIỂM ĐỊNH BẰNG CHỨNG RUN-MANIFEST MỚI..." -ForegroundColor Yellow
    $ManifestData = Get-Content $ManifestFile -Raw | ConvertFrom-Json

    if ($ManifestData.status -ne "COMPLETED") {
        throw "[FAIL-FAST] Manifest status='$($ManifestData.status)' (yêu cầu COMPLETED)"
    }
    if ($ManifestData.architecture -ne "SEQUENCE_ONLY") {
        throw "[FAIL-FAST] Manifest architecture='$($ManifestData.architecture)' (yêu cầu SEQUENCE_ONLY)"
    }
    if ([int]$ManifestData.seed -ne 42) {
        throw "[FAIL-FAST] Manifest seed=$($ManifestData.seed) (yêu cầu 42)"
    }
    $epochsTrained = [int]$ManifestData.total_epochs_trained
    if ($epochsTrained -lt 1 -or $epochsTrained -gt 12) {
        throw "[FAIL-FAST] total_epochs_trained=$epochsTrained không nằm trong khoảng 1..12"
    }
    $bestEp = [int]$ManifestData.best_epoch
    if ($bestEp -lt 1 -or $bestEp -gt $epochsTrained) {
        throw "[FAIL-FAST] best_epoch=$bestEp không hợp lệ đối với $epochsTrained epochs"
    }
    if ([int]$ManifestData.nan_count -ne 0) {
        throw "[FAIL-FAST] nan_count=$($ManifestData.nan_count) > 0"
    }
    if ([int]$ManifestData.inf_count -ne 0) {
        throw "[FAIL-FAST] inf_count=$($ManifestData.inf_count) > 0"
    }

    $BestCkptSha = (Get-FileHash -Path $BestCkptFile -Algorithm SHA256).Hash.ToLower()

    # 11. Ghi MANUAL_RUN_SUMMARY.txt với số liệu THỰC TẾ ĐO ĐƯỢC
    Write-Host "`n>>> [BƯỚC 6/6] GHI BÁO CÁO TÓM TẮT MANUAL_RUN_SUMMARY.txt..." -ForegroundColor Yellow
    $SummaryLines = @(
        "=====================================================================",
        "BÁO CÁO TÁI LẬP THỰC NGHIỆM ĐỘC LẬP (MANUAL RUN SUMMARY)",
        "=====================================================================",
        "Thời gian ghi nhận (UTC): $([DateTime]::UtcNow.ToString('o'))",
        "Thư mục lưu trữ phiên chạy: $RunDir",
        "Git Commit SHA:           $GitCommit",
        "Git Status:               $GitDirty",
        "Môi trường thực thi:      $PkgInfo",
        "Exit Status:              PASS (All Gating Conditions Met)",
        "",
        "THÔNG TIN ĐẦU VÀO VÀ MÃ BĂM DỮ LIỆU ĐÃ KIỂM CHỨNG:",
        "  - hdfs_ssl_train.pt:       $($DataHashes['hdfs_ssl_train.pt'])",
        "  - hdfs_ssl_val.pt:         $($DataHashes['hdfs_ssl_val.pt'])",
        "  - hdfs_vocab.json:         $($DataHashes['hdfs_vocab.json'])",
        "  - hdfs_probe_labels_val.pt: $($DataHashes['hdfs_probe_labels_val.pt'])",
        "",
        "KẾT QUẢ THỰC TẾ QUAN SÁT TỪ ĐỢT CHẠY MỚI (OBSERVED RUN METRICS):",
        "  - Run ID:                  $($ManifestData.run_id)",
        "  - Thư mục Confirmatory:    $GeneratedRunDir",
        "  - Architecture:            $($ManifestData.architecture)",
        "  - Seed:                    $($ManifestData.seed)",
        "  - Status:                  $($ManifestData.status)",
        "  - Total Epochs Trained:    $($ManifestData.total_epochs_trained)",
        "  - Early Stopped:           $($ManifestData.early_stopped)",
        "  - Best Epoch:              $($ManifestData.best_epoch)",
        "  - Best Val Loss (Observed):$($ManifestData.best_val_loss)",
        "  - Latent Variance Var(z):  $($ManifestData.latent_variance)",
        "  - Peak VRAM:               $($ManifestData.peak_vram_mb) MB",
        "  - Training Internal Probe AP:      $($ManifestData.probe_ap)",
        "  - Training Internal Probe ROC-AUC: $($ManifestData.probe_roc_auc)",
        "  - Ghi chú phân định Protocol:     Các chỉ số AP/ROC-AUC ở trên là của đầu dò nội bộ (training internal probe), không nhầm lẫn với frozen-probe V3 được đánh giá độc lập sau đó.",
        "  - Checkpoint SHA-256 mới:  $BestCkptSha",
        "====================================================================="
    )
    $SummaryLines | Out-File -FilePath $SummaryFile -Encoding utf8
    Write-Host "  Đã ghi tóm tắt: $SummaryFile" -ForegroundColor Cyan

    $RunSucceeded = $true

} catch {
    Write-Error $_.Exception.Message
    $RunSucceeded = $false
} finally {
    Stop-Transcript
}

if ($RunSucceeded) {
    Write-Host "`n=====================================================================" -ForegroundColor Green
    Write-Host "  HOÀN TẤT PHIÊN TÁI LẬP THỰC NGHIỆM ĐỘC LẬP!" -ForegroundColor Green
    Write-Host "  Vui lòng xem chi tiết tại: $SummaryFile" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n=====================================================================" -ForegroundColor Red
    Write-Host "  THẤT BẠI: PHIÊN TÁI LẬP THỰC NGHIỆM GẶP LỖI HOẶC BỊ HỦY." -ForegroundColor Red
    Write-Host "  Vui lòng kiểm tra nhật ký tại: $TranscriptPath" -ForegroundColor Red
    Write-Host "=====================================================================" -ForegroundColor Red
    exit 1
}
