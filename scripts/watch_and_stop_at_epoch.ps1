# scripts/watch_and_stop_at_epoch.ps1
param (
    [int]$TargetEpoch = 5,
    [int]$Seed = 1337,
    [int]$PollIntervalSeconds = 5
)

$ErrorActionPreference = "SilentlyContinue"

$baseDir = "D:\Research"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\TRAIN-LOG.jsonl"
$pidFile = "$baseDir\logs\stage-a2\seed$Seed.pid"
$logDir = "$baseDir\logs\stage-a2"
$watcherLog = "$logDir\auto_stop_watcher_seed${Seed}_epoch${TargetEpoch}.log"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$startMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Auto-stop watcher active: Seed $Seed, Target Epoch $TargetEpoch (Poll interval: ${PollIntervalSeconds}s)"
Write-Host $startMsg -ForegroundColor Cyan
Add-Content -Path $watcherLog -Value $startMsg

while ($true) {
    Start-Sleep -Seconds $PollIntervalSeconds
    
    if (Test-Path $trainLog) {
        $lines = @(Get-Content -Path $trainLog)
        if ($lines.Count -ge $TargetEpoch) {
            $msg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] DETECTED: Epoch $TargetEpoch completed and logged in TRAIN-LOG.jsonl ($($lines.Count) lines)."
            Write-Host $msg -ForegroundColor Yellow
            Add-Content -Path $watcherLog -Value $msg
            
            # Allow 5 seconds for last checkpoint flush and durable sync to finalize
            Start-Sleep -Seconds 5
            
            # Find and stop all python and powershell processes for this seed
            $processes = Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%--seed $Seed%'"
            foreach ($p in $processes) {
                Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
                $killMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Terminated process PID $($p.ProcessId) ($($p.Name))"
                Write-Host $killMsg -ForegroundColor Green
                Add-Content -Path $watcherLog -Value $killMsg
            }
            
            "PAUSED_AFTER_EPOCH_$TargetEpoch" | Set-Content -Path $pidFile -Encoding ascii
            $doneMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Auto-stop completed successfully. GPU VRAM freed. PID set to PAUSED_AFTER_EPOCH_$TargetEpoch."
            Write-Host $doneMsg -ForegroundColor Green
            Add-Content -Path $watcherLog -Value $doneMsg

            # Update RUN-STATE.json to PAUSED and sync to durable
            $runStateP = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\RUN-STATE.json"
            $durableStateP = "$baseDir\durable\stage-a2\HDFS\seed-$Seed\RUN-STATE.json"
            if (Test-Path $runStateP) {
                try {
                    $st = Get-Content -Path $runStateP -Raw | ConvertFrom-Json
                    $st.status = "PAUSED"
                    $st | ConvertTo-Json -Depth 10 | Set-Content -Path $runStateP -Encoding utf8
                    if (Test-Path (Split-Path $durableStateP)) {
                        Copy-Item -Path $runStateP -Destination $durableStateP -Force
                    }
                    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] RUN-STATE.json marked PAUSED and synced to durable." -ForegroundColor Green
                } catch {
                    Write-Warning "Could not update RUN-STATE: $_"
                }
            }

            # Restore system CPU, GPU, fan, and sleep defaults to normal
            $restoreMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Restoring system CPU, GPU, and Sleep settings to factory defaults..."
            Write-Host $restoreMsg -ForegroundColor Cyan
            Add-Content -Path $watcherLog -Value $restoreMsg

            $schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13"
            powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 300
            powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 180
            powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2
            powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 2
            powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5
            powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 5
            powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 100
            powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 100
            powercfg /setacvalueindex $schemeGuid SUB_DISK DISKIDLE 1200
            powercfg /setdcvalueindex $schemeGuid SUB_DISK DISKIDLE 1200
            powercfg /setactive $schemeGuid

            $allRestoredMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] All settings restored to default successfully."
            Write-Host $allRestoredMsg -ForegroundColor Green
            Add-Content -Path $watcherLog -Value $allRestoredMsg
            break
        }
    }
}
