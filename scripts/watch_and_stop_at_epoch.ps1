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
            break
        }
    }
}
