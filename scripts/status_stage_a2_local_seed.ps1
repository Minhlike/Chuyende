# scripts/status_stage_a2_local_seed.ps1
# Status checker for Local Stage A2 Seed Execution

param (
    [Parameter(Mandatory = $true)]
    [int]$Seed
)

$baseDir = "D:\Research"
$pidFile = "$baseDir\logs\stage-a2\seed$Seed.pid"
$stdoutLog = "$baseDir\logs\stage-a2\seed$Seed.stdout.log"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\RUN-STATE.json"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\TRAIN-LOG.jsonl"
$ckptBest = "$baseDir\.artifacts\stage-a2\HDFS\seed-$Seed\best_val_loss.pt"
$ckptLast = "$baseDir\.artifacts\stage-a2\HDFS\seed-$Seed\last_checkpoint.pt"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   STATUS CHECK: CANONICAL SEED $Seed                     " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Process Check
$proc = Get-CimInstance Win32_Process -Filter "CommandLine LIKE '%--seed $Seed%'" | 
        Where-Object { $_.ProcessId -ne $PID -and $_.Name -like "*python*" } | 
        Select-Object -Last 1

if ($proc) {
    $userSec = [double]$proc.UserModeTime / 10000000.0
    $ramMB = [math]::Round($proc.WorkingSetSize / 1MB, 1)
    Write-Host "Process PID:       $($proc.ProcessId)" -ForegroundColor Green
    Write-Host "Process Status:    ALIVE & RUNNING" -ForegroundColor Green
    Write-Host "Compute Time:      $([math]::Round($userSec / 60.0, 1)) mins ($([int]$userSec) s)"
    Write-Host "Host RAM:          $ramMB MB"
} else {
    $recPid = if (Test-Path $pidFile) { (Get-Content $pidFile -Raw).Trim() } else { "N/A" }
    Write-Host "Process Status:    NOT RUNNING (Last PID: $recPid)" -ForegroundColor Gray
}

# 2. GPU Telemetry
try {
    $smiOut = & nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>$null
    if ($smiOut) {
        $parts = $smiOut.Split(',')
        if ($parts.Count -ge 4) {
            Write-Host "GPU Telemetry:     Util $($parts[0].Trim())% | VRAM $($parts[1].Trim()) / $($parts[2].Trim()) MB | Temp $($parts[3].Trim()) C"
        }
    }
} catch {}

# 3. RUN-STATE Data
if (Test-Path $stateFile) {
    try {
        $state = Get-Content $stateFile -Raw | ConvertFrom-Json
        Write-Host "Run State Status:  $($state.status)"
        Write-Host "Completed Epochs:  $($state.completed_epoch)"
        Write-Host "Global Step:       $($state.global_step)"
        if ($state.best_val_loss -ne $null -and $state.best_val_loss -ne [double]::PositiveInfinity) {
            Write-Host "Best Val Loss:     $([math]::Round([double]$state.best_val_loss, 6)) (Epoch $($state.best_epoch))"
        }
    } catch {}
} else {
    Write-Host "Run State:         (Not started yet / RUN-STATE.json not present)"
}

# 4. Checkpoints
if (Test-Path $ckptBest) {
    $bInfo = Get-Item $ckptBest
    Write-Host "Best Checkpoint:   Ready ($([math]::Round($bInfo.Length / 1MB, 2)) MB)"
}
if (Test-Path $ckptLast) {
    $lInfo = Get-Item $ckptLast
    Write-Host "Last Checkpoint:   Ready ($([math]::Round($lInfo.Length / 1MB, 2)) MB)"
}

# 5. Recent Logs
if (Test-Path $stdoutLog) {
    Write-Host "`n--- Recent Stdout (Last 10 lines) ---" -ForegroundColor Cyan
    Get-Content $stdoutLog -Tail 10 | ForEach-Object { Write-Host "  $_" }
}

Write-Host "==========================================================" -ForegroundColor Cyan
