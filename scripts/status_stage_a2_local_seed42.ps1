# scripts/status_stage_a2_local_seed42.ps1
$baseDir = "D:\Research"
$logDir = "D:\Research\logs\stage-a2"
$stdoutLog = "$logDir\seed42.stdout.log"
$stderrLog = "$logDir\seed42.stderr.log"
$pidFile = "$logDir\seed42.pid"
$stateFile = "D:\Research\experiments\runs\stage-a2\HDFS\seed-42\RUN-STATE.json"

Write-Host "=========================================================="
Write-Host "   STAGE A2 LOCAL SEED 42 TRAINING STATUS                "
Write-Host "=========================================================="

if (-not (Test-Path $pidFile)) {
    Write-Host "No PID file found at $pidFile. Training process not launched."
    exit 0
}

$pidVal = Get-Content $pidFile -Raw
$pidVal = $pidVal.Trim()
Write-Host "Recorded PID: $pidVal"

$proc = Get-Process -Id $pidVal -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "Process State: RUNNING (Alive)"
    Write-Host "Process Name:  $($proc.ProcessName)"
    Write-Host "CPU Time:      $($proc.TotalProcessorTime)"
    Write-Host "Working Set:   $([math]::Round($proc.WorkingSet64 / 1MB, 2)) MB"
} else {
    Write-Host "Process State: TERMINATED / NOT RUNNING"
}

if (Test-Path $stateFile) {
    Write-Host "`n--- RUN-STATE.json ---"
    Get-Content $stateFile
}

if (Test-Path $stdoutLog) {
    Write-Host "`n--- Last 20 lines of STDOUT ---"
    Get-Content $stdoutLog -Tail 20
}

if (Test-Path $stderrLog) {
    $errContent = Get-Content $stderrLog -Tail 10
    if ($errContent) {
        Write-Host "`n--- Last 10 lines of STDERR ---"
        $errContent
    }
}
Write-Host "=========================================================="
