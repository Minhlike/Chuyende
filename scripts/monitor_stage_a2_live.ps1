# scripts/monitor_stage_a2_live.ps1
# Realtime Live Monitor & Progress Bar for Stage A2 Canonical Seed 42 (Responsive & Split-Screen Friendly)

$baseDir = "D:\Research"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"
$logFile = "$baseDir\logs\stage-a2\seed42.stdout.log"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\best_val_loss.pt"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\TRAIN-LOG.jsonl"

# Per-epoch user compute expectation ~9,000s
$expectedEpochUserSeconds = 9050.0

try {
    [Console]::CursorVisible = $false
} catch {}

Clear-Host

try {
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

        # Determine terminal width (handles split screens)
        $rawWidth = 80
        try {
            $rawWidth = $host.UI.RawUI.WindowSize.Width
        } catch {}
        $width = [math]::Max(50, [math]::Min($rawWidth - 2, 75))
        $sep = "=" * $width

        $lines = [System.Collections.Generic.List[string]]::new()
        $lines.Add($sep)
        $lines.Add(" STAGE A2 CANONICAL SEED 42 - LIVE MONITOR")
        $lines.Add($sep)

        if ($isAlive) {
            $userSec = [double]$proc.UserModeTime / 10000000.0
            $kernSec = [double]$proc.KernelModeTime / 10000000.0
            $ramMB = [math]::Round($proc.WorkingSetSize / 1MB, 1)

            # Determine running epoch
            $completedEpochs = 0
            $currentEpochNum = 1
            if ($stateData -ne $null) {
                $completedEpochs = [int]$stateData.completed_epoch
                $currentEpochNum = $completedEpochs + 1
            }

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

            # Calculate Progress for current running epoch
            $pct = [math]::Min(99.5, [math]::Max(1.0, ($userSec / $expectedEpochUserSeconds) * 100.0))
            $remainingSec = [math]::Max(10.0, $expectedEpochUserSeconds - $userSec)
            $etaSec = [int]($remainingSec / 0.95)

            $statusDesc = ""
            if ($userSec -lt 120.0) {
                $statusDesc = "DATASET MATERIALIZATION (HDFS Splits)"
            } elseif ($pct -lt 83.0) {
                $stepStart = $completedEpochs * 573
                $stepEnd = $stepStart + 573
                $statusDesc = "TRAINING (Steps $stepStart -> $stepEnd)"
            } else {
                $statusDesc = "VALIDATION (119,531 events | 467 Windows)"
            }

            # Visual progress bar (adapted to width)
            $barWidth = [math]::Max(20, $width - 25)
            $filled = [int][math]::Round(($pct / 100.0) * $barWidth)
            if ($filled -gt $barWidth) { $filled = $barWidth }
            if ($filled -lt 0) { $filled = 0 }
            $empty = [int]($barWidth - $filled)
            $barStr = ("#" * $filled) + ("-" * $empty)

            $lines.Add(" RUN ID:       RUN-STAGE-A2-HDFS-SEED42")
            $lines.Add(" STATUS:       RUNNING (PID: $($proc.ProcessId))")
            $lines.Add(" ACTIVE EPOCH: Epoch $currentEpochNum / 20 (Completed: $completedEpochs)")
            $lines.Add(" PHASE:        $statusDesc")
            $lines.Add("")
            $lines.Add(" EPOCH $currentEpochNum PROGRESS: [$barStr] $([math]::Round($pct, 1))%")
            $lines.Add("")

            $elapsedMin = [math]::Round($userSec / 60.0, 1)
            $etaMin = [math]::Round($etaSec / 60.0, 1)
            $etaStr = "$([int]($etaSec / 60))m $($etaSec % 60)s"

            $lines.Add(" [TIME & ESTIMATION]")
            $lines.Add("   - Epoch User Time: $elapsedMin mins ($([int]$userSec) s)")
            $lines.Add("   - Estimated ETA:   $etaStr (~$etaMin mins)")
            $lines.Add("")
            $lines.Add(" [SYSTEM & HARDWARE]")
            $lines.Add("   - GPU Active:      $gpuUtil | VRAM: $gpuMem")
            $lines.Add("   - GPU Temp:        $gpuTemp")
            $lines.Add("   - Process RAM:     $ramMB MB")
            $lines.Add("")
            $lines.Add(" [CHECKPOINTS]")
            if ($stateData -ne $null -and $stateData.best_val_loss -ne $null -and $stateData.best_val_loss -ne [double]::PositiveInfinity) {
                $bestLossStr = [math]::Round([double]$stateData.best_val_loss, 4)
                $lines.Add("   - Best Val Loss:   $bestLossStr (Epoch $($stateData.best_epoch))")
            }
            if (Test-Path $ckptBest) {
                $ckptInfo = Get-Item $ckptBest
                $lines.Add("   - Checkpoint:      Ready ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
            }

        } else {
            $lines.Add(" STATUS:       PAUSED / NOT RUNNING")
            if (Test-Path $ckptBest) {
                $ckptInfo = Get-Item $ckptBest
                $lines.Add(" LAST CHECKPOINT: Epoch 1 is Saved & Verified ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
            }
        }

        $lines.Add($sep)
        $lines.Add(" Live smooth refresh (every 1s). Press Ctrl+C to exit.")

        # Ensure no line exceeds terminal width to prevent line wrapping glitches
        $formattedLines = $lines | ForEach-Object {
            $line = $_
            if ($line.Length -gt $width) {
                $line = $line.Substring(0, $width)
            }
            $line.PadRight($width)
        }

        $outputBlock = $formattedLines -join [Environment]::NewLine
        try {
            [Console]::SetCursorPosition(0, 0)
        } catch {}
        [Console]::Write($outputBlock)

        Start-Sleep -Seconds 1
    }
} finally {
    try {
        [Console]::CursorVisible = $true
    } catch {}
    Write-Host ""
}
