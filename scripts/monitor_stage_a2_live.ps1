# scripts/monitor_stage_a2_live.ps1
# Realtime Live Monitor & Progress Bar for Stage A2 Canonical Seed 42

$baseDir = "D:\Research"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"
$logFile = "$baseDir\logs\stage-a2\seed42.stdout.log"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\best_val_loss.pt"
$ckptLast = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\last_checkpoint.pt"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\TRAIN-LOG.jsonl"

# Baseline target constants for Epoch 1:
# Total expected user compute seconds ~ 9,000s (Train 586k events + Val 120k events = 706k events)
$expectedTotalUserSeconds = 9050.0

Write-Host "Starting Live Stage A2 Training Monitor... (Press Ctrl+C to exit)" -ForegroundColor Cyan
Start-Sleep -Milliseconds 500

while ($true) {
    # 1. Discover Process
    $proc = Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%run_stage_a2_five_seed_empirical.py%'" | 
            Where-Object { $_.ProcessId -ne $PID } | 
            Sort-Object -Property UserModeTime -Descending | 
            Select-Object -First 1

    $isAlive = ($proc -ne $null)
    $stateData = $null
    if (Test-Path $stateFile) {
        try {
            $stateData = Get-Content $stateFile -Raw | ConvertFrom-Json
        } catch {}
    }

    $ckptExists = (Test-Path $ckptBest)

    Clear-Host
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host "        STAGE A2 CANONICAL SEED 42 — REALTIME TRAINING MONITOR                  " -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan

    if ($isAlive) {
        $userSec = [double]$proc.UserModeTime / 10000000.0
        $kernSec = [double]$proc.KernelModeTime / 10000000.0
        $ramMB = [math]::Round($proc.WorkingSetSize / 1MB, 1)

        # GPU metrics
        $gpuUtil = "N/A"
        $gpuMem = "N/A"
        $gpuTemp = "N/A"
        try {
            $smiOut = & nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>$null
            if ($smiOut) {
                $parts = $smiOut.Split(',')
                if ($parts.Count -ge 4) {
                    $gpuUtil = "$($parts[0].Trim())%"
                    $gpuMem = "$($parts[1].Trim()) / $($parts[2].Trim()) MB"
                    $gpuTemp = "$($parts[3].Trim()) C"
                }
            }
        } catch {}

        # Calculate Progress
        $pct = 0.0
        $statusDesc = ""
        $etaSec = 0

        if ($ckptExists -or ($stateData -ne $null -and $stateData.completed_epoch -ge 1)) {
            $pct = 100.0
            $statusDesc = "EPOCH 1 COMPLETED! (Checkpoint Saved)"
            $etaSec = 0
        } else {
            # Train is 586k events (~83%), Val is 120k events (~17%)
            $pct = [math]::Min(99.5, [math]::Max(5.0, ($userSec / $expectedTotalUserSeconds) * 100.0))
            $remainingSec = [math]::Max(10.0, $expectedTotalUserSeconds - $userSec)
            $etaSec = [int]($remainingSec / 0.95) # duty cycle adjustment

            if ($pct -lt 83.0) {
                $statusDesc = "TRAINING PHASE (586,577 events | 573 Optimizer Steps)"
            } else {
                $statusDesc = "VALIDATION PHASE (119,531 events | 467 Windows) — Final Steps"
            }
        }

        # Format visual progress bar
        $barWidth = 40
        $filled = [math]::Round(($pct / 100.0) * $barWidth)
        if ($filled -gt $barWidth) { $filled = $barWidth }
        $empty = $barWidth - $filled
        $barStr = ("#" * $filled) + ("-" * $empty)

        # Output UI
        Write-Host " RUN ID:          " -NoNewline; Write-Host "RUN-STAGE-A2-HDFS-SEED42" -ForegroundColor Green
        Write-Host " PROCESS STATUS:  " -NoNewline; Write-Host "RUNNING (PID: $($proc.ProcessId))" -ForegroundColor Green
        Write-Host " CURRENT EPOCH:   " -NoNewline; Write-Host "Epoch 1 / 20" -ForegroundColor White
        Write-Host " CURRENT PHASE:   " -NoNewline; Write-Host "$statusDesc" -ForegroundColor Magenta
        Write-Host ""
        
        Write-Host " PROGRESS:        [$barStr] $([math]::Round($pct, 1))%" -ForegroundColor Yellow
        Write-Host ""

        $elapsedUserMin = [math]::Round($userSec / 60.0, 1)
        $etaMin = [math]::Round($etaSec / 60.0, 1)
        $etaStr = if ($pct -ge 100.0) { "00:00 (DONE)" } else { "$([int]($etaSec / 60))m $($etaSec % 60)s" }

        Write-Host " [TIME & ESTIMATION]" -ForegroundColor White
        Write-Host "   - User Compute Time: $elapsedUserMin mins ($([int]$userSec) s)"
        Write-Host "   - Estimated ETA:     $etaStr (~$etaMin mins remaining)" -ForegroundColor Yellow
        Write-Host ""

        Write-Host " [SYSTEM & HARDWARE]" -ForegroundColor White
        Write-Host "   - GPU Active Util:   $gpuUtil"
        Write-Host "   - GPU VRAM:          $gpuMem"
        Write-Host "   - GPU Temperature:   $gpuTemp"
        Write-Host "   - Process RAM:       $ramMB MB"
        Write-Host ""

        Write-Host " [CHECKPOINT & ARTIFACTS]" -ForegroundColor White
        if ($ckptExists) {
            $ckptInfo = Get-Item $ckptBest
            Write-Host "   - best_val_loss.pt:  EXISTS! ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)" -ForegroundColor Green
            Write-Host "   - Saved At:          $($ckptInfo.LastWriteTime)" -ForegroundColor Green
        } else {
            Write-Host "   - Checkpoint Status: Pending Epoch 1 validation completion..." -ForegroundColor DarkYellow
        }

    } else {
        Write-Host " PROCESS STATUS:  " -NoNewline; Write-Host "NOT RUNNING / TERMINATED" -ForegroundColor Red
        if ($ckptExists) {
            Write-Host " STATUS:          " -NoNewline; Write-Host "EPOCH 1 CHECKPOINT IS READY!" -ForegroundColor Green
            $ckptInfo = Get-Item $ckptBest
            Write-Host " Checkpoint File: $ckptBest ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)" -ForegroundColor Green
        }
    }

    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host " Refreshes every 2 seconds. Press Ctrl+C to stop monitor." -ForegroundColor DarkGray

    Start-Sleep -Seconds 2
}
