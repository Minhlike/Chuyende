# scripts/resume_stage_a2_local_seed999_epoch12.ps1
# Resume Canonical Seed 999 from Epoch 11 Checkpoint -> Execute Final Epoch 12
# Configured for Daytime Normal Mode (Priority: Normal, Affinity: P-cores 0-7, Silent fans <= 54C, Finish <= 3 hours)

$ErrorActionPreference = "Stop"

$baseDir = "D:\Research"
$pythonExe = "$baseDir\.venv-stage-a2-cuda\Scripts\python.exe"
$logDir = "$baseDir\logs\stage-a2"
$lastCkpt = "$baseDir\.artifacts\stage-a2\HDFS\seed-999\last_checkpoint.pt"
$ckptSha = "3ed0daed768a88f5c18c4610fe820358d915e075bbad5caba5aa1033e21a8793"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

$stdoutLog = "$logDir\seed999.stdout.log"
$stderrLog = "$logDir\seed999.stderr.log"
$pidFile = "$logDir\seed999.pid"

# 1. Ensure Daytime Normal Profile is active (Silent fans, Screen timeout 10m, CPU min 50%, CPU max 99%, ASPM 0)
$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13"
powercfg /setactive $schemeGuid
powercfg /setacvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 600
powercfg /setdcvalueindex $schemeGuid SUB_VIDEO VIDEOIDLE 300
powercfg /setacvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0
powercfg /setdcvalueindex $schemeGuid SUB_PCIEXPRESS ASPM 0
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 50
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMIN 50
powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setdcvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
powercfg /setactive $schemeGuid

$env:CUBLAS_WORKSPACE_CONFIG = ":4096:8"
$env:PYTHONUNBUFFERED = "1"

$argsArray = @(
    "-u",
    "scripts\run_stage_a2_five_seed_empirical.py",
    "--seed", "999",
    "--resume", $lastCkpt,
    "--resume-sha256", $ckptSha,
    "--authorize-real-empirical-execution",
    "--base-dir", $baseDir,
    "--dataset-path", "$baseDir\datasets\raw\hdfs\HDFS_1.tar.gz",
    "--durable-root", "$baseDir\durable\stage-a2\HDFS",
    "--plan", "$baseDir\experiments\plans\STAGE-A2-FIVE-SEED-EXECUTION-PLAN-V1.5.json",
    "--environment-lock", "$baseDir\experiments\evidence\stage-a2\preexecution\STAGE-A2-LOCAL-EXECUTION-ENVIRONMENT-V1.5.json",
    "--authorization", "$baseDir\experiments\evidence\stage-a2\preexecution\SEED999-LOCAL-LAUNCH-AUTHORIZATION-V1.5.json"
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   RESUMING CANONICAL SEED 999 (FINAL EPOCH 12 - DAYTIME) " -ForegroundColor Yellow
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

Start-Sleep -Seconds 2

# 2. Configure Process Priority to Normal & Affinity to P-cores (0-7)
try {
    $procObj = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
    if ($procObj) {
        $procObj.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::Normal
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
Write-Host "Spawned Resume Process PID: $($process.Id)" -ForegroundColor Green
Write-Host "PID saved to $pidFile"
