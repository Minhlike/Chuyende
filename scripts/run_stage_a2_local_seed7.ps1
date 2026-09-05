# scripts/run_stage_a2_local_seed7.ps1
# Launch Canonical Seed 7 (Stage A2 HDFS Empirical)

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed7.stdout.log"
$stderrLog = "$logDir\seed7.stderr.log"
$pidFile = "$logDir\seed7.pid"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "7",
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "$baseDir\durable\stage-a2\HDFS",
    "--plan", "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "$baseDir\experiments\evidence\stage-a2\preexecution\SEED7-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING CANONICAL SEED 7 (STAGE A2)                  " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsArray `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "Stdout Log: $stdoutLog"
Write-Host "Stderr Log: $stderrLog"
Write-Host "PID File:   $pidFile"
