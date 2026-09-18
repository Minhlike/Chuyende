# tập lệnh/resume_stage_a2_local_seed999_epoch12.ps1
# Tiếp tục Canonical Seed 999 từ checkpoint epoch 11 -> Thực thi epoch cuối cùng 12
# Được định cấu hình cho Chế độ bình thường ban ngày (Ưu tiên: Bình thường, Mối quan hệ: Lõi P 0-7, Quạt im lặng <= 54C, Hoàn thành <= 3 giờ)

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

# 1. Đảm bảo Cấu hình bình thường ban ngày đang hoạt động (Quạt im lặng, Thời gian chờ màn hình 10 phút, CPU tối thiểu 50%, CPU tối đa 99%, ASPM 0)
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

# 2. Định cấu hình Mức độ ưu tiên của quy trình thành Bình thường & Mối quan hệ với lõi P (0-7)
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

# 3. Vô hiệu hóa Windows Power Throttling (EcoQoS) qua Win32 API
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
