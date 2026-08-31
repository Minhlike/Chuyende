# scripts/resume_stage_a2_local_seed1337_epoch4.ps1
# Resume Canonical Seed 1337 from Epoch 3 Checkpoint -> Execute Epoch 4

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"
$lastCkpt = "$baseDir\.artifacts\stage-a2\HDFS\seed-1337\last_checkpoint.pt"
$ckptSha = "4a28940348db263f376d51380ec85419ae71b6cdbc3b84d871d4ad98eb0cd17a"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed1337.stdout.log"
$stderrLog = "$logDir\seed1337.stderr.log"
$pidFile = "$logDir\seed1337.pid"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "1337",
    "--resume", $lastCkpt,
    "--resume-sha256", $ckptSha,
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "$baseDir\durable\stage-a2\HDFS",
    "--plan", "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "$baseDir\experiments\evidence\stage-a2\preexecution\SEED1337-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   RESUMING CANONICAL SEED 1337 (EPOCH 4)                 " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Checkpoint: $lastCkpt"
Write-Host "SHA-256:    $ckptSha"
Write-Host "Logs:       $stdoutLog"

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsArray `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Resume Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
Write-Host "You can now run 'powershell -ExecutionPolicy Bypass -File scripts\status_stage_a2_local_seed.ps1 -Seed 1337' to check status." -ForegroundColor Yellow
