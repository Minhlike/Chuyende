# scripts/watchdog_training_guard.ps1
# Continuous Hardware Thermal Guard & Training Progress Monitor for Seed 7

param (
    [int]$TargetEpoch = 12,
    [int]$Seed = 7,
    [int]$MaxGpuTemp = 70,
    [int]$PollIntervalSeconds = 30
)

$baseDir = "D:\Research"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\TRAIN-LOG.jsonl"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\RUN-STATE.json"
$pidFile = "$baseDir\logs\stage-a2\seed$Seed.pid"
$logDir = "$baseDir\logs\stage-a2"
$watchdogLog = "$logDir\watchdog_seed${Seed}_guard.log"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$startMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Watchdog active. Target: Epoch $TargetEpoch. Max Temp: ${MaxGpuTemp}C. Poll: ${PollIntervalSeconds}s"
Write-Host $startMsg -ForegroundColor Cyan
Add-Content -Path $watchdogLog -Value $startMsg

$lastLoggedEpoch = -1

while ($true) {
    Start-Sleep -Seconds $PollIntervalSeconds
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    $pythonProc = Get-Process -Name python -ErrorAction SilentlyContinue | 
                  Sort-Object -Property CPU -Descending | 
                  Select-Object -First 1

    if (-not $pythonProc) {
        $msg = "[$now] ALERT: No active python training process detected!"
        Write-Host $msg -ForegroundColor Red
        Add-Content -Path $watchdogLog -Value $msg
        break
    }

    $gpuTemp = 0
    $gpuUtil = 0
    $gpuPower = 0.0
    try {
        $smiOut = & nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,power.draw --format=csv,noheader,nounits 2>$null
        if ($smiOut) {
            $parts = $smiOut.Split(',')
            if ($parts.Count -ge 3) {
                $gpuTemp = [int]$parts[0].Trim()
                $gpuUtil = [int]$parts[1].Trim()
                $gpuPower = [double]$parts[2].Trim()
            }
        }
    } catch {}

    if ($gpuTemp -ge $MaxGpuTemp) {
        $alertMsg = "[$now] THERMAL WARNING: GPU Temp reached ${gpuTemp}C >= ${MaxGpuTemp}C! Engaging cooldown..."
        Write-Host $alertMsg -ForegroundColor Red
        Add-Content -Path $watchdogLog -Value $alertMsg
        powercfg /setacvalueindex 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13 SUB_PROCESSOR PROCTHROTTLEMAX 80
        powercfg /setactive 0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13
    }

    $completedCount = 0
    if (Test-Path $trainLog) {
        $lines = @(Get-Content -Path $trainLog | Where-Object { $_.Trim().Length -gt 0 })
        $completedCount = $lines.Count
        if ($completedCount -ne $lastLoggedEpoch) {
            $lastLoggedEpoch = $completedCount
            $epochMsg = "[$now] PROGRESS: $completedCount epochs completed so far."
            Write-Host $epochMsg -ForegroundColor Green
            Add-Content -Path $watchdogLog -Value $epochMsg
        }
    }

    $logLine = "[$now] PID: $($pythonProc.Id) | CPU Time: $([math]::Round($pythonProc.CPU, 1))s | GPU: ${gpuTemp}C, ${gpuUtil}%, ${gpuPower}W | Completed Epochs: $completedCount"
    Add-Content -Path $watchdogLog -Value $logLine

    if ($completedCount -ge $TargetEpoch) {
        $finishMsg = "[$now] SUCCESS: Target Epoch $TargetEpoch completed!"
        Write-Host $finishMsg -ForegroundColor Green
        Add-Content -Path $watchdogLog -Value $finishMsg
        break
    }
}
