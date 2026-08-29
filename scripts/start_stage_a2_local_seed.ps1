# scripts/start_stage_a2_local_seed.ps1
# Generic Canonical Stage A2 Launcher for Local Execution (Fresh Start without Checkpoint Resume)

param (
    [Parameter(Mandatory = $true)]
    [int]$Seed
)

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"
$authFile = "$baseDir\experiments\evidence\stage-a2\preexecution\SEED$Seed-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
$envLock = "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json"
$planFile = "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json"
$datasetPath = "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz"
$durableRoot = "$baseDir\durable\stage-a2\HDFS"

if (-not (Test-Path $authFile)) {
    Write-Error "FATAL: Launch authorization file does not exist: $authFile"
}

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed$Seed.stdout.log"
$stderrLog = "$logDir\seed$Seed.stderr.log"
$pidFile = "$logDir\seed$Seed.pid"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "$Seed",
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", $datasetPath,
    "--durable-root", $durableRoot,
    "--plan", $planFile,
    "--environment-lock", $envLock,
    "--authorization", $authFile
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING CANONICAL SEED $Seed (FRESH START)           " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Seed:          $Seed"
Write-Host "Authorization: $authFile"
Write-Host "Logs:          $stdoutLog"

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsArray `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
Write-Host "Run 'powershell -ExecutionPolicy Bypass -File scripts\status_stage_a2_local_seed.ps1 -Seed $Seed' to check status." -ForegroundColor Yellow
