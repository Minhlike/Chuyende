# scripts/monitor_stage_a2_live.ps1
# Universal Realtime Live Monitor & Progress Bar for Stage A2 Canonical Five-Seed Execution
# Accurate, honest, calibrated against Epoch 1 baseline (~10,900s / 182 mins)

$baseDir = "D:\Research"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"
$logFile = "$baseDir\logs\stage-a2\seed42.stdout.log"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\best_val_loss.pt"
$ckptLast = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\last_checkpoint.pt"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\TRAIN-LOG.jsonl"

# Benchmark baseline: Epoch 1 took 10,934s total (Train 10,386s + Val 545s)
$benchmarkEpochSeconds = 10800.0
$totalEpochs = 20

try {
    [Console]::CursorVisible = $false
} catch {}

Clear-Host

try {
    while ($true) {
        # 1. Discover Active Process
        $proc = Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%run_stage_a2_five_seed_empirical.py%'" | 
                Where-Object { $_.ProcessId -ne $PID } | 
                Sort-Object -Property UserModeTime -Descending | 
                Select-Object -First 1

        $isAlive = ($proc -ne $null)

        # 2. Read State & Logs
        $stateData = $null
        if (Test-Path $stateFile) {
            try {
                $stateData = Get-Content $stateFile -Raw | ConvertFrom-Json
            } catch {}
        }

        $logRecords = @()
        if (Test-Path $trainLog) {
            try {
                $rawLogs = Get-Content $trainLog
                foreach ($rl in $rawLogs) {
                    if ($rl -and $rl.Trim().Length -gt 0) {
                        $logRecords += ($rl | ConvertFrom-Json)
                    }
                }
            } catch {}
        }

        # 3. Determine Console Width (Split Screen Friendly)
        $rawWidth = 80
        try {
            $rawWidth = $host.UI.RawUI.WindowSize.Width
        } catch {}
        $width = [math]::Max(50, [math]::Min($rawWidth - 2, 80))
        $sep = "=" * $width

        $lines = [System.Collections.Generic.List[string]]::new()
        $lines.Add($sep)
        $lines.Add(" STAGE A2 CANONICAL SEED 42 -- UNIVERSAL TRAINING MONITOR")
        $lines.Add($sep)

        $completedEpochs = $logRecords.Count
        if ($stateData -ne $null -and $stateData.completed_epoch -gt $completedEpochs) {
            $completedEpochs = [int]$stateData.completed_epoch
        }

        # 4. Hardware Metrics
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

        if ($isAlive) {
            $userSec = [double]$proc.UserModeTime / 10000000.0
            $kernSec = [double]$proc.KernelModeTime / 10000000.0
            $ramMB = [math]::Round($proc.WorkingSetSize / 1MB, 1)

            $activeEpoch = $completedEpochs + 1
            if ($activeEpoch -gt $totalEpochs) { $activeEpoch = $totalEpochs }

            # Accurate progress based on real 10,800s benchmark
            $rawEpochPct = ($userSec / $benchmarkEpochSeconds) * 100.0
            $epochPct = [math]::Min(99.0, [math]::Max(1.0, $rawEpochPct))
            $campaignPct = [math]::Min(100.0, [math]::Round((($completedEpochs + ($epochPct / 100.0)) / [double]$totalEpochs) * 100.0, 1))

            $elapsedMin = [math]::Round($userSec / 60.0, 1)
            $remainingSec = [math]::Max(60.0, $benchmarkEpochSeconds - $userSec)
            $remainingMin = [math]::Round($remainingSec / 60.0, 1)

            $statusDesc = ""
            if ($userSec -lt 120.0) {
                $statusDesc = "DATASET MATERIALIZATION (HDFS Splits)"
            } elseif ($epochPct -lt 85.0) {
                $stepStart = $completedEpochs * 573
                $stepEnd = $stepStart + 573
                $statusDesc = "TRAINING PHASE (Steps $stepStart -> $stepEnd)"
            } elseif ($epochPct -lt 98.0) {
                $statusDesc = "VALIDATION PHASE (119,531 events | 467 Windows)"
            } else {
                $statusDesc = "SAVING CHECKPOINT & SYNCHRONIZING DURABLE ROOT"
            }

            # Progress Bars
            $barWidth = [math]::Max(18, $width - 32)
            
            # Overall Campaign Bar
            $cFilled = [int][math]::Round(($campaignPct / 100.0) * $barWidth)
            if ($cFilled -gt $barWidth) { $cFilled = $barWidth }
            $cEmpty = [int]($barWidth - $cFilled)
            $cBarStr = ("#" * $cFilled) + ("-" * $cEmpty)

            # Current Epoch Bar
            $eFilled = [int][math]::Round(($epochPct / 100.0) * $barWidth)
            if ($eFilled -gt $barWidth) { $eFilled = $barWidth }
            $eEmpty = [int]($barWidth - $eFilled)
            $eBarStr = ("#" * $eFilled) + ("-" * $eEmpty)

            $lines.Add(" STATUS:         RUNNING (PID: $($proc.ProcessId))")
            $lines.Add(" ACTIVE EPOCH:   Epoch $activeEpoch / $totalEpochs (Completed: $completedEpochs)")
            $lines.Add(" CURRENT PHASE:  $statusDesc")
            $lines.Add("")
            $lines.Add(" CAMPAIGN TOTAL: [$cBarStr] $campaignPct%")
            $lines.Add(" EPOCH $activeEpoch PROGRESS: [$eBarStr] $([math]::Round($epochPct, 1))%")
            $lines.Add("")

            $lines.Add(" [COMPUTE TIME & HARDWARE]")
            $lines.Add("   - Epoch Compute:  $elapsedMin mins / ~180 mins expected")
            $lines.Add("   - Est. Remaining: ~$remainingMin mins")
            $lines.Add("   - GPU Active:     $gpuUtil | VRAM: $gpuMem | Temp: $gpuTemp")
            $lines.Add("   - Process RAM:    $ramMB MB")
            $lines.Add("")

        } else {
            $campaignPct = [math]::Min(100.0, [math]::Round(($completedEpochs / [double]$totalEpochs) * 100.0, 1))
            $barWidth = [math]::Max(18, $width - 32)
            $cFilled = [int][math]::Round(($campaignPct / 100.0) * $barWidth)
            if ($cFilled -gt $barWidth) { $cFilled = $barWidth }
            $cEmpty = [int]($barWidth - $cFilled)
            $cBarStr = ("#" * $cFilled) + ("-" * $cEmpty)

            $lines.Add(" STATUS:         PAUSED / STANDBY")
            $lines.Add(" COMPLETED:      $completedEpochs / $totalEpochs Epochs")
            $lines.Add(" CAMPAIGN TOTAL: [$cBarStr] $campaignPct%")
            $lines.Add("")
            $lines.Add(" [SYSTEM & HARDWARE]")
            $lines.Add("   - GPU VRAM:   $gpuMem | Temp: $gpuTemp")
            $lines.Add("")
        }

        # 5. Completed Epochs History Table
        $lines.Add(" [EPOCH HISTORY]")
        if ($logRecords.Count -gt 0) {
            foreach ($rec in $logRecords) {
                $eNum = $rec.epoch
                $tLoss = [math]::Round([double]$rec.train_L_graph, 4)
                $vLoss = [math]::Round([double]$rec.val_L_graph, 4)
                $gStep = $rec.global_step
                $star = ""
                if ($stateData -ne $null -and $eNum -eq $stateData.best_epoch) {
                    $star = " (*BEST*)"
                }
                $lines.Add("   - Epoch $eNum : Train=$tLoss | Val=$vLoss | Step $gStep$star")
            }
        } else {
            $lines.Add("   - (No completed epochs recorded yet)")
        }
        $lines.Add("")

        # 6. Best Checkpoint State
        $lines.Add(" [BEST CHECKPOINT]")
        if ($stateData -ne $null -and $stateData.best_val_loss -ne $null -and $stateData.best_val_loss -ne [double]::PositiveInfinity) {
            $bestLossStr = [math]::Round([double]$stateData.best_val_loss, 4)
            $lines.Add("   - Best Val Loss: $bestLossStr (Achieved at Epoch $($stateData.best_epoch))")
        }
        if (Test-Path $ckptBest) {
            $ckptInfo = Get-Item $ckptBest
            $lines.Add("   - File: best_val_loss.pt ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
        }

        $lines.Add($sep)
        $lines.Add(" Live smooth refresh (every 1s). Press Ctrl+C to exit.")

        # 7. Render Frame Safely
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
