# scripts/sleep_after_training.ps1
# Passively waits for Python PID 15308 to exit naturally,
# verifies checkpoints, restores Sweet Spot, and safely suspends the PC.

$targetPid = 15308
$pilotDir = "D:\Research\experiments\nineplus\pilots\PILOT_GRAPH_ONLY_seed42_1789315134"
$logFile = "$pilotDir\SLEEP_TRIGGER.log"

function Log-Message ($msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$timestamp] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log-Message "Watcher started. Passively waiting for PID $targetPid to finish naturally..."

# Wait for target process to exit
try {
    Wait-Process -Id $targetPid -ErrorAction Stop
} catch {
    Log-Message "Process $targetPid not found or already exited: $_"
}

Log-Message "Process $targetPid has exited naturally. Waiting 10 seconds for disk sync..."
Start-Sleep -Seconds 10

# Check files
$ckpt2 = "$pilotDir\checkpoint_epoch2.pt"
$manifest = "$pilotDir\RUN-MANIFEST.json"

if (Test-Path $ckpt2) {
    $size = (Get-Item $ckpt2).Length / 1MB
    Log-Message "VERIFIED: checkpoint_epoch2.pt exists ($([math]::Round($size, 2)) MB)."
} else {
    Log-Message "WARNING: checkpoint_epoch2.pt not found on disk!"
}

if (Test-Path $manifest) {
    Log-Message "VERIFIED: RUN-MANIFEST.json exists."
} else {
    Log-Message "WARNING: RUN-MANIFEST.json not found on disk!"
}

# Restore Sweet Spot power profile
Log-Message "Restoring Sweet Spot power profile..."
try {
    & "D:\Research\scripts\set_training_sweetspot.ps1"
    Log-Message "Sweet Spot profile applied successfully."
} catch {
    Log-Message "Error applying sweet spot profile: $_"
}

Log-Message "Preparing to suspend machine in 15 seconds. Good night!"
Start-Sleep -Seconds 15

# Put PC to sleep cleanly
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)
