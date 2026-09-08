# scripts/run_stage_a2_local_seed999.ps1
# Launch Canonical Seed 999 (Stage A2 HDFS Empirical - FINAL SEED)

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed999.stdout.log"
$stderrLog = "$logDir\seed999.stderr.log"
$pidFile = "$logDir\seed999.pid"

# 1. Apply Hardware Sweet Spot Profile
& "$baseDir\scripts\set_training_sweetspot.ps1"

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "999",
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "$baseDir\durable\stage-a2\HDFS",
    "--plan", "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "$baseDir\experiments\evidence\stage-a2\preexecution\SEED999-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LAUNCHING CANONICAL SEED 999 (FINAL SEED - STAGE A2)   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$process = Start-Process -FilePath $pythonExe `
    -ArgumentList $argsArray `
    -WorkingDirectory $baseDir `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -PassThru

Start-Sleep -Seconds 2

# 2. Lock PriorityClass to AboveNormal and Affinity to P-cores
try {
    $procObj = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    if ($procObj) {
        $procObj.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::AboveNormal
        Write-Host "Set process priority to: $($procObj.PriorityClass)" -ForegroundColor Green
        $procObj.ProcessorAffinity = 255
        Write-Host "Locked processor affinity to P-cores: $($procObj.ProcessorAffinity)" -ForegroundColor Green
    }
} catch {
    Write-Warning "Could not adjust process priority/affinity: $_"
}

# 3. Disable Windows Power Throttling (EcoQoS) via Win32 API
try {
    $code = @"
using System;
using System.Runtime.InteropServices;

public class Win32PowerGuard {
    [StructLayout(LayoutKind.Sequential)]
    public struct PROCESS_POWER_THROTTLING_STATE {
        public uint Version;
        public uint ControlMask;
        public uint StateMask;
    }

    private const int ProcessPowerThrottling = 4;
    private const uint PROCESS_POWER_THROTTLING_CURRENT_VERSION = 1;
    private const uint PROCESS_POWER_THROTTLING_EXECUTION_SPEED = 0x1;
    private const uint PROCESS_POWER_THROTTLING_IGNORE_TIMER_RESOLUTION = 0x4;

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern bool SetProcessInformation(
        IntPtr hProcess,
        int ProcessInformationClass,
        ref PROCESS_POWER_THROTTLING_STATE ProcessInformation,
        uint ProcessInformationSize
    );

    public static bool DisableThrottling(IntPtr hProcess) {
        PROCESS_POWER_THROTTLING_STATE state = new PROCESS_POWER_THROTTLING_STATE();
        state.Version = PROCESS_POWER_THROTTLING_CURRENT_VERSION;
        state.ControlMask = PROCESS_POWER_THROTTLING_EXECUTION_SPEED | PROCESS_POWER_THROTTLING_IGNORE_TIMER_RESOLUTION;
        state.StateMask = 0;
        return SetProcessInformation(hProcess, ProcessPowerThrottling, ref state, (uint)Marshal.SizeOf(state));
    }
}
"@
    if (-not ([System.Management.Automation.PSTypeName]'Win32PowerGuard').Type) {
        Add-Type -TypeDefinition $code -Language CSharp
    }
    $p = [System.Diagnostics.Process]::GetProcessById($process.Id)
    $res = [Win32PowerGuard]::DisableThrottling($p.Handle)
    Write-Host "Windows Power Throttling Disabled (EcoQoS Blocked): $res" -ForegroundColor Green
} catch {
    Write-Warning "Could not disable power throttling: $_"
}

$process.Id | Set-Content -Path $pidFile -Encoding ascii
Write-Host "Spawned Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
