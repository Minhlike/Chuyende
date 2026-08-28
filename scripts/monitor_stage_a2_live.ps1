# scripts/monitor_stage_a2_live.ps1
# Realtime Live Monitor & Progress Bar for Stage A2 Canonical Seed 42

$baseDir = "D:\Research"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"
$logFile = "$baseDir\logs\stage-a2\seed42.stdout.log"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\best_val_loss.pt"
$ckptLast = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\last_checkpoint.pt"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-42\TRAIN-LOG.jsonl"

$expectedTotalUserSeconds = 9050.0

try {
    [Console]::CursorVisible = $false
} catch {}

Clear-Host

try {
    while ($true) {
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

        $lines = [System.Collections.Generic.List[string]]::new()
        $width = 80
        $sep = "=" * $width

        $lines.Add($sep)
        $lines.Add("        STAGE A2 CANONICAL SEED 42 -- REALTIME TRAINING MONITOR         ")
        $lines.Add($sep)

        if ($isAlive) {
            $userSec = [double]$proc.UserModeTime / 10000000.0
            $kernSec = [double]$proc.KernelModeTime / 10000000.0
            $ramMB = [math]::Round($proc.WorkingSetSize / 1MB, 1)

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

            $pct = 0.0
            $statusDesc = ""
            $etaSec = 0

            if ($ckptExists -or ($stateData -ne $null -and $stateData.completed_epoch -ge 1)) {
                $pct = 100.0
                $statusDesc = "EPOCH 1 COMPLETED! (Checkpoint Saved)"
                $etaSec = 0
            } else {
                $pct = [math]::Min(99.5, [math]::Max(5.0, ($userSec / $expectedTotalUserSeconds) * 100.0))
                $remainingSec = [math]::Max(10.0, $expectedTotalUserSeconds - $userSec)
                $etaSec = [int]($remainingSec / 0.95)

                if ($pct -lt 83.0) {
                    $statusDesc = "TRAINING PHASE (586,577 events | 573 Optimizer Steps)"
                } else {
                    $statusDesc = "VALIDATION PHASE (119,531 events | 467 Windows) - Final Steps"
                }
            }

            $barWidth = 40
            $filled = [int][math]::Round(($pct / 100.0) * $barWidth)
            if ($filled -gt $barWidth) { $filled = $barWidth }
            if ($filled -lt 0) { $filled = 0 }
            $empty = [int]($barWidth - $filled)
            $barStr = ("#" * $filled) + ("-" * $empty)

            $lines.Add(" RUN ID:          RUN-STAGE-A2-HDFS-SEED42")
            $lines.Add(" PROCESS STATUS:  RUNNING (PID: $($proc.ProcessId))")
            $lines.Add(" CURRENT EPOCH:   Epoch 1 / 20")
            $lines.Add(" CURRENT PHASE:   $statusDesc")
            $lines.Add("")
            $lines.Add(" PROGRESS:        [$barStr] $([math]::Round($pct, 1))%")
            $lines.Add("")

            $elapsedUserMin = [math]::Round($userSec / 60.0, 1)
            $etaMin = [math]::Round($etaSec / 60.0, 1)
            $etaStr = if ($pct -ge 100.0) { "00:00 (DONE)" } else { "$([int]($etaSec / 60))m $($etaSec % 60)s" }

            $lines.Add(" [TIME & ESTIMATION]")
            $lines.Add("   - User Compute Time: $elapsedUserMin mins ($([int]$userSec) s)")
            $lines.Add("   - Estimated ETA:     $etaStr (~$etaMin mins remaining)")
            $lines.Add("")
            $lines.Add(" [SYSTEM & HARDWARE]")
            $lines.Add("   - GPU Active Util:   $gpuUtil")
            $lines.Add("   - GPU VRAM:          $gpuMem")
            $lines.Add("   - GPU Temperature:   $gpuTemp")
            $lines.Add("   - Process RAM:       $ramMB MB")
            $lines.Add("")
            $lines.Add(" [CHECKPOINT & ARTIFACTS]")
            if ($ckptExists) {
                $ckptInfo = Get-Item $ckptBest
                $lines.Add("   - best_val_loss.pt:  EXISTS! ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
                $lines.Add("   - Saved At:          $($ckptInfo.LastWriteTime)")
            } else {
                $lines.Add("   - Checkpoint Status: Pending Epoch 1 validation completion...")
            }

        } else {
            $lines.Add(" PROCESS STATUS:  NOT RUNNING / TERMINATED")
            if ($ckptExists) {
                $lines.Add(" STATUS:          EPOCH 1 CHECKPOINT IS READY!")
                $ckptInfo = Get-Item $ckptBest
                $lines.Add(" Checkpoint File: $ckptBest ($([math]::Round($ckptInfo.Length / 1MB, 2)) MB)")
            }
        }

        $lines.Add($sep)
        $lines.Add(" Live smooth refresh (every 1s). Press Ctrl+C to stop monitor.")

        $outputBlock = ($lines | ForEach-Object { $_.PadRight($width) }) -join [Environment]::NewLine
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
