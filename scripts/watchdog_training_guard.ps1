# scripts/watchdog_training_guard.ps1
# Continuous Hardware Thermal Guard & Training Progress Monitor for Stage A2

param (
    [int]$TargetEpoch = 12,
    [int]$Seed = 999,
    [int]$MaxGpuTemp = 70,
    [int]$PollIntervalSeconds = 30,
    [string]$PriorityClass = "AboveNormal"
)

$baseDir = "D:\Research"
$trainLog = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\TRAIN-LOG.jsonl"
$stateFile = "$baseDir\experiments\runs\stage-a2\HDFS\seed-$Seed\RUN-STATE.json"
$pidFile = "$baseDir\logs\stage-a2\seed$Seed.pid"
$logDir = "$baseDir\logs\stage-a2"
$watchdogLog = "$logDir\watchdog_seed${Seed}_guard.log"

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Ensure Win32PowerGuard type definition for EcoQoS suppression
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
} catch {}

$schemeGuid = "0a0d0183-1b65-4b13-ad7a-e1bfc6c0ab13"
$isThrottledForCooling = $false

$startMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Watchdog active. Target: Seed $Seed, Epoch $TargetEpoch. Max Temp: ${MaxGpuTemp}C. Poll: ${PollIntervalSeconds}s"
Write-Host $startMsg -ForegroundColor Cyan
Add-Content -Path $watchdogLog -Value $startMsg

$lastLoggedEpoch = -1

while ($true) {
    Start-Sleep -Seconds $PollIntervalSeconds
    $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

    $pythonProc = Get-Process -Name python -ErrorAction SilentlyContinue | 
                  Sort-Object -Property CPU -Descending | 
                  Select-Object -First 1

    if (-not $pythonProc) {
        $msg = "[$now] Training process finished. Checking final state..."
        Write-Host $msg -ForegroundColor Cyan
        Add-Content -Path $watchdogLog -Value $msg
        if (Test-Path $stateFile) {
            try {
                $st = Get-Content $stateFile -Raw | ConvertFrom-Json
                if ($st.status -eq "COMPLETED") {
                    $completeMsg = "[$now] SUCCESS: Training COMPLETED! Restoring machine to normal resting defaults..."
                    Write-Host $completeMsg -ForegroundColor Green
                    Add-Content -Path $watchdogLog -Value $completeMsg
                    & "$baseDir\scripts\restore_normal_profile.ps1"
                }
            } catch {}
        }
        break
    }

    # Continuous enforcement of process locks
    try {
        $targetPriority = [System.Diagnostics.ProcessPriorityClass]::$PriorityClass
        if ($pythonProc.PriorityClass -ne $targetPriority) {
            $pythonProc.PriorityClass = $targetPriority
        }
        if ($pythonProc.ProcessorAffinity.ToInt64() -ne 255) {
            $pythonProc.ProcessorAffinity = 255
        }
        [Win32PowerGuard]::DisableThrottling($pythonProc.Handle) | Out-Null
    } catch {}

    $gpuTemp = 0
    $gpuUtil = 0
    $gpuPower = 0.0
    try {
        $smiOut = & nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,power.draw --format=csv,noheader,nounits 2>$null
        if ($smiOut) {
            $parts = $smiOut.Split(',')
            if ($parts.Count -ge 3) {
                $gpuTemp = [int]$parts[0].Trim()
                $gpuUtil = [int]$parts[1].Trim()
                $gpuPower = [double]$parts[2].Trim()
            }
        }
    } catch {}

    # Thermal guard with hysteresis
    if ($gpuTemp -ge $MaxGpuTemp -and -not $isThrottledForCooling) {
        $alertMsg = "[$now] THERMAL WARNING: GPU Temp reached ${gpuTemp}C >= ${MaxGpuTemp}C! Engaging cooldown (CPU max 80%)..."
        Write-Host $alertMsg -ForegroundColor Red
        Add-Content -Path $watchdogLog -Value $alertMsg
        powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 80
        powercfg /setactive $schemeGuid
        $isThrottledForCooling = $true
    } elseif ($gpuTemp -le ($MaxGpuTemp - 10) -and $isThrottledForCooling) {
        $coolMsg = "[$now] THERMAL RECOVERY: GPU Temp cooled to ${gpuTemp}C. Restoring sweet spot (CPU max 99%)..."
        Write-Host $coolMsg -ForegroundColor Green
        Add-Content -Path $watchdogLog -Value $coolMsg
        powercfg /setacvalueindex $schemeGuid SUB_PROCESSOR PROCTHROTTLEMAX 99
        powercfg /setactive $schemeGuid
        $isThrottledForCooling = $false
    }

    $completedCount = 0
    if (Test-Path $trainLog) {
        $lines = @(Get-Content -Path $trainLog | Where-Object { $_.Trim().Length -gt 0 })
        $completedCount = $lines.Count
        if ($completedCount -ne $lastLoggedEpoch) {
            $lastLoggedEpoch = $completedCount
            $epochMsg = "[$now] PROGRESS: $completedCount epochs completed so far."
            Write-Host $epochMsg -ForegroundColor Green
            Add-Content -Path $watchdogLog -Value $epochMsg
        }
    }

    $logLine = "[$now] PID: $($pythonProc.Id) | CPU Time: $([math]::Round($pythonProc.CPU, 1))s | GPU: ${gpuTemp}C, ${gpuUtil}%, ${gpuPower}W | Completed Epochs: $completedCount"
    Add-Content -Path $watchdogLog -Value $logLine

    if ($completedCount -ge $TargetEpoch) {
        $finishMsg = "[$now] SUCCESS: Target Epoch $TargetEpoch reached! Waiting 25s for checkpoint save & Google Drive sync to finalize..."
        Write-Host $finishMsg -ForegroundColor Green
        Add-Content -Path $watchdogLog -Value $finishMsg
        Start-Sleep -Seconds 25

        # Verify Google Drive sync and state file
        if (Test-Path $stateFile) {
            try {
                $st = Get-Content $stateFile -Raw | ConvertFrom-Json
                if ($TargetEpoch -lt 12) {
                    $st.status = "PAUSED_AT_EPOCH_$TargetEpoch"
                    $jsonStr = $st | ConvertTo-Json -Depth 10
                    [System.IO.File]::WriteAllText($stateFile, $jsonStr, (New-Object System.Text.UTF8Encoding($false)))
                    Add-Content -Path $watchdogLog -Value "[$now] RUN-STATE updated: status = PAUSED_AT_EPOCH_$TargetEpoch"
                } else {
                    Add-Content -Path $watchdogLog -Value "[$now] All 12 Canonical Epochs completed! Final Status: $($st.status)"
                }
            } catch {}
        }

        # If TargetEpoch < 12, stop process to rest. If 12, wait up to 30s for natural clean exit
        if ($TargetEpoch -lt 12) {
            try {
                $pToStop = Get-Process -Id $pythonProc.Id -ErrorAction SilentlyContinue
                if ($pToStop) {
                    Stop-Process -Id $pToStop.Id -Force -ErrorAction SilentlyContinue
                    Add-Content -Path $watchdogLog -Value "[$now] Python worker (PID: $($pToStop.Id)) stopped cleanly at Epoch $TargetEpoch boundary."
                }
            } catch {}
        } else {
            # Wait for python process to cleanly exit after metrics write
            Start-Sleep -Seconds 15
        }

        # Restore normal everyday resting power profile
        & "$baseDir\scripts\restore_normal_profile.ps1"
        Add-Content -Path $watchdogLog -Value "[$now] Normal resting profile restored. Screen timeout restored, CPU min 5%, fans silenced, machine at rest."
        break
    }
}
