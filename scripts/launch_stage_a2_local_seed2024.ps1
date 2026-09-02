# scripts/launch_stage_a2_local_seed2024.ps1
# Launch Canonical Seed 2024 Execution on Local CUDA GPU under Protocol V1.5

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed2024.stdout.log"
$stderrLog = "$logDir\seed2024.stderr.log"
$pidFile = "$logDir\seed2024.pid"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "2024",
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "$baseDir\durable\stage-a2\HDFS",
    "--plan", "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "$baseDir\experiments\evidence\stage-a2\preexecution\SEED2024-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING CANONICAL SEED 2024 REAL EMPIRICAL RUN       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Python:     $pythonExe"
Write-Host "Seed:       2024"
Write-Host "Logs:       $stdoutLog"

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsArray `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
Write-Host "You can monitor status with: powershell -ExecutionPolicy Bypass -File scripts\status_stage_a2_local_seed.ps1 -Seed 2024" -ForegroundColor Yellow
