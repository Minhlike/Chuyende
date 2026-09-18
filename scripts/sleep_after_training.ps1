param (
    [int]$TargetPid = 0,
    [string]$RunDir = "D:\Research\experiments\nineplus\confirmatory"
)

if ($TargetPid -eq 0) {
    $proc = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
        try {
            $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
            $cmd -like "*run_nineplus_confirmatory*"
        } catch { $false }
    } | Select-Object -First 1
    if ($proc) {
        $TargetPid = $proc.Id
    }
}

$logFile = "$RunDir\SLEEP_TRIGGER.log"

function Log-Message ($msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$timestamp] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

if ($TargetPid -eq 0) {
    Log-Message "ERROR: No target Python process found to wait for."
    exit 1
}

Log-Message "Watcher started. Passively waiting for PID $TargetPid to finish naturally..."

# Đợi quá trình đích thoát ra
try {
    Wait-Process -Id $TargetPid -ErrorAction Stop
} catch {
    Log-Message "Process $TargetPid not found or already exited: $_"
}

Log-Message "Process $TargetPid has exited naturally. Waiting 15 seconds for disk sync..."
Start-Sleep -Seconds 15

# Kiểm tra tập tin
$manifests = Get-ChildItem -Path $RunDir -Recurse -Filter "RUN-MANIFEST.json"
Log-Message "VERIFIED: Found $($manifests.Count) RUN-MANIFEST.json files across confirmatory runs."
foreach ($m in $manifests) {
    Log-Message "  - $($m.FullName)"
}

# Khôi phục hồ sơ sức mạnh Sweet Spot
Log-Message "Restoring Sweet Spot power profile..."
try {
    & "D:\Research\scripts\set_training_sweetspot.ps1"
    Log-Message "Sweet Spot profile applied successfully."
} catch {
    Log-Message "Error applying sweet spot profile: $_"
}

Log-Message "Preparing to suspend machine in 15 seconds. Training complete!"
Start-Sleep -Seconds 15

# Đặt PC vào chế độ ngủ sạch sẽ
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)
