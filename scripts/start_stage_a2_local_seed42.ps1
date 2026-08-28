# scripts/start_stage_a2_local_seed42.ps1
$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "D:\Research\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "D:\Research\logs\stage-a2"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed42.stdout.log"
$stderrLog = "$logDir\seed42.stderr.log"
$pidFile = "$logDir\seed42.pid"

# Set deterministic environment variables in the session
$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsList = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "42",
    "--authorize-real-empirical-execution",
    "--base-dir", "D:\Research",
    "--dataset-path", "D:\Research\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "D:\Research\durable\stage-a2\HDFS",
    "--plan", "experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "experiments\evidence\stage-a2\preexecution\SEED42-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "Starting Stage A2 Local Canonical Seed 42 Training..."
Write-Host "Python: $pythonExe"
Write-Host "Logs:   $stdoutLog"

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsList `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Process PID: $($process.Id)"
Write-Host "PID saved to $pidFile"
