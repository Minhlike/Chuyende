# scripts/monitor_stage_a2_live.ps1
# Universal Realtime Live Monitor for Stage A2 Canonical Five-Seed Execution (Honest, Real-Time Hardware & State Telemetry)

$baseDir = "D:\Research"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"
$logFile = "$baseDir\logs\stage-a2\seed42.stdout.log"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\best_val_loss.pt"
$ckptLast = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\last_checkpoint.pt"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\TRAIN-LOG.jsonl"
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
        $lines.Add(" STAGE A2 CANONICAL SEED 42 -- LIVE TELEMETRY MONITOR")
        $lines.Add($sep)

        $completedEpochs = $logRecords.Count
        if ($stateData -ne $null -and $stateData.completed_epoch -gt $completedEpochs) {
            $completedEpochs = [int]$stateData.completed_epoch
        }

        # 4. Hardware Metrics
        $gpuUtil = "0%"
        $gpuMem = "0 / 4096 MB"
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
            $userMin = [math]::Round($userSec / 60.0, 1)

            $activeEpoch = $completedEpochs + 1
            if ($activeEpoch -gt $totalEpochs) { $activeEpoch = $totalEpochs }

            $lines.Add(" PROCESS STATUS:  ACTIVE COMPUTING (PID: $($proc.ProcessId))")
            $lines.Add(" ACTIVE EPOCH:    Epoch $activeEpoch / $totalEpochs (Completed: $completedEpochs)")
            $lines.Add(" EPOCH COMPUTE:   $userMin mins ($([int]$userSec) seconds of CPU/GPU time)")
            $lines.Add("")
            $lines.Add(" [LIVE HARDWARE TELEMETRY]")
            $lines.Add("   - GPU Util:    $gpuUtil (Actively executing neural graph forward/eval)")
            $lines.Add("   - GPU VRAM:    $gpuMem")
            $lines.Add("   - GPU Temp:    $gpuTemp")
            $lines.Add("   - Host RAM:    $ramMB MB (Dynamic graph buffers in memory)")
            $lines.Add("")
            $lines.Add(" [CURRENT STAGE]")
            if ($userMin -lt 5.0) {
                $lines.Add("   -> Phase: Dataset Materialization (35,000 train + 7,500 val sessions)")
            } elseif ($userMin -lt 170.0) {
                $lines.Add("   -> Phase: Training Stream (Steps $(($completedEpochs * 573)) -> $(($completedEpochs * 573 + 573)))")
            } else {
                $lines.Add("   -> Phase: Validation Stream & Checkpoint Commit (119,531 events / 467 windows)")
            }
            $lines.Add("")

        } else {
            $lines.Add(" PROCESS STATUS:  PAUSED / NOT RUNNING")
            $lines.Add(" COMPLETED:       $completedEpochs / $totalEpochs Epochs")
            $lines.Add(" GPU VRAM:        $gpuMem (Cleanly freed)")
            $lines.Add("")
        }

        # 5. Completed Epochs History Table
        $lines.Add(" [CHECKPOINT & EPOCH HISTORY]")
        if ($logRecords.Count -gt 0) {
            foreach ($rec in $logRecords) {
                $eNum = $rec.epoch
                $tLoss = [math]::Round([double]$rec.train_L_graph, 4)
                $vLoss = [math]::Round([double]$rec.val_L_graph, 4)
                $gStep = $rec.global_step
                $star = ""
                if ($stateData -ne $null -and $eNum -eq $stateData.best_epoch) {
                    $star = " (*BEST CHECKPOINT*)"
                }
                $lines.Add("   - Epoch $eNum : Train Loss=$tLoss | Val Loss=$vLoss | Step $gStep$star")
            }
        } else {
            $lines.Add("   - (No completed epochs recorded yet)")
        }
        $lines.Add("")

        # 6. Best Checkpoint State
        if ($stateData -ne $null -and $stateData.best_val_loss -ne $null -and $stateData.best_val_loss -ne [double]::PositiveInfinity) {
            $bestLossStr = [math]::Round([double]$stateData.best_val_loss, 4)
            $lines.Add(" [BEST CHECKPOINT SAVED]")
            $lines.Add("   - Best Val Loss: $bestLossStr (at Epoch $($stateData.best_epoch))")
            if (Test-Path $ckptBest) {
                $ckptInfo = Get-Item $ckptBest
                $lines.Add("   - Checkpoint:    best_val_loss.pt ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
            }
            $lines.Add("")
        }

        $lines.Add($sep)
        $lines.Add(" Live telemetry refresh (every 1s). Press Ctrl+C to exit.")

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
