# scripts/resume_stage_a2_local_seed7_epoch8.ps1
# Resume Canonical Seed 7 from Epoch 7 Checkpoint -> Execute Epoch 8

Continue = Stop

 = D:\Research
 = \.venv-stage-a2-cuda\Scripts\python.exe
 = \logs\stage-a2
 = \.artifacts\stage-a2\HDFS\seed-7\last_checkpoint.pt
 = 529b6c8230a42f083dd611ea2cf58b9eb9e183a212f7611d0db0223070e3a850

# 1. Ensure Hardware Sweet Spot is applied
& \scripts\set_training_sweetspot.ps1

if (-not (Test-Path )) {
    New-Item -ItemType Directory -Path  -Force | Out-Null
}

 = \seed7.stdout.log
 = \seed7.stderr.log
 = \seed7.pid

 = :4096:8
 = 1

 = @(
    -u,
    scripts\run_stage_a2_five_seed_empirical.py,
    --seed, 7,
    --resume, ,
    --resume-sha256, ,
    --authorize-real-empirical-execution,
    --base-dir, ,
    --dataset-path, \datasets\raw\hdfs\HDFS_1.tar.gz,
    --durable-root, \durable\stage-a2\HDFS,
    --plan, \experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json,
    --environment-lock, \experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json,
    --authorization, \experiments\evidence\stage-a2\preexecution\SEED7-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json
)

Write-Host ========================================================== -ForegroundColor Cyan
Write-Host  RESUMING CANONICAL SEED 7 (EPOCH 8)  -ForegroundColor Yellow
Write-Host ========================================================== -ForegroundColor Cyan
Write-Host Checkpoint: 
Write-Host SHA-256: 

 = Start-Process -FilePath  
    -ArgumentList  
    -WorkingDirectory  
    -RedirectStandardOutput  
    -RedirectStandardError  
    -PassThru

# Elevate priority to AboveNormal to guarantee CPU scheduling
Start-Sleep -Seconds 1
try {
     = Get-Process -Id .Id -ErrorAction SilentlyContinue
    if () {
        .PriorityClass = [System.Diagnostics.ProcessPriorityClass]::AboveNormal
        Write-Host Set process priority to:  -ForegroundColor Green
    }
} catch {
    Write-Warning Could not elevate priority class: 
}

.Id | Set-Content -Path  -Encoding ascii
Write-Host Spawned Resume Process PID:  -ForegroundColor Green
Write-Host PID saved to 
Write-Host ========================================================== -ForegroundColor Cyan
