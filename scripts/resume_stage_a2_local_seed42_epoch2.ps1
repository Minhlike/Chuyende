# scripts/resume_stage_a2_local_seed42_epoch2.ps1
# Resume Canonical Seed 42 from Epoch 1 Checkpoint -> Execute Epoch 2

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"
$lastCkpt = "$baseDir\.artifacts\stage-a2\HDFS\seed-42\last_checkpoint.pt"
$ckptSha = "cca63e780d2fc91bc57260cacace37fc5bb1581d0206e4341ccbb26ed10f2a9f"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed42.stdout.log"
$stderrLog = "$logDir\seed42.stderr.log"
$pidFile = "$logDir\seed42.pid"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argString = "-u scripts\run_stage_a2_five_seed_empirical.py --seed 42 --resume `"$lastCkpt`" --resume-sha256 `"$ckptSha`" --authorize-real-empirical-execution --base-dir `"$baseDir`" --dataset-path `"$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz`" --durable-root `"$baseDir\durable\stage-a2\HDFS`" --plan `"$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json`" --environment-lock `"$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json`" --authorization `"$baseDir\experiments\evidence\stage-a2\preexecution\SEED42-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json`""

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   RESUMING STAGE A2 LOCAL CANONICAL SEED 42 (EPOCH 2)    " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Checkpoint: $lastCkpt"
Write-Host "SHA-256:    $ckptSha"
Write-Host "Logs:       $stdoutLog"

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argString `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Resume Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
Write-Host "You can now run 'powershell -ExecutionPolicy Bypass -File scripts\monitor_stage_a2_live.ps1' to watch progress!" -ForegroundColor Yellow
