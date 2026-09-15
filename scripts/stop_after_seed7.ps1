# scripts/stop_after_seed7.ps1
# Monitors Seed 7 Multi-View run:
# 1. If RUN-MANIFEST.json appears naturally (early stopping), stops process so Seed 999 is skipped.
# 2. If clock passes 17:00:00, waits for the current in-progress epoch to finish its checkpoint,
#    then stops training, runs finalize_multiview_checkpoint.py, and leaves PC awake.

$targetDir = "D:\Research\experiments\nineplus\confirmatory\CONF_MULTI_VIEW_ALIGNED_seed7_1789452137"
$manifest = "$targetDir\RUN-MANIFEST.json"
$logFile = "$targetDir\STOP_AFTER_SEED7.log"

function Log-Msg ($msg) {
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log-Msg "Watcher active. Monitoring Seed 7 (Natural Early Stop or 17:00:00 Deadline Cutoff)..."

while ($true) {
    # 1. Check natural completion
    if (Test-Path $manifest) {
        $item = Get-Item $manifest -ErrorAction SilentlyContinue
        if ($item -and $item.Length -gt 100) {
            Log-Msg "Seed 7 RUN-MANIFEST.json verified ($($item.Length) bytes). Waiting 5 seconds for complete flush..."
            Start-Sleep -Seconds 5
            
            $procs = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
                try {
                    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
                    $cmd -like "*run_nineplus_confirmatory*"
                } catch { $false }
            }
            
            foreach ($p in $procs) {
                Log-Msg "Stopping Python PID $($p.Id) to prevent Seed 999 from executing..."
                Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
            }
            
            Log-Msg "Seed 7 completed 100%. Seed 999 suppressed per user order. PC kept active."
            break
        }
    }

    # 2. Check 17:00:00 deadline cutoff
    $now = Get-Date
    if ($now.Hour -ge 17) {
        Log-Msg "DEADLINE REACHED: Current time is $($now.ToString('HH:mm:ss')) >= 17:00:00."
        
        $ckpts = Get-ChildItem -Path $targetDir -Filter "checkpoint_epoch*.pt" -ErrorAction SilentlyContinue
        $countInitial = if ($ckpts) { $ckpts.Count } else { 0 }
        Log-Msg "Currently completed checkpoints: $countInitial. Waiting for in-progress epoch to finish naturally and save checkpoint..."
        
        while ($true) {
            $ckptsNow = Get-ChildItem -Path $targetDir -Filter "checkpoint_epoch*.pt" -ErrorAction SilentlyContinue
            if ($ckptsNow -and ($ckptsNow.Count -gt $countInitial)) {
                $newest = $ckptsNow | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                Log-Msg "In-progress epoch finished! New checkpoint detected: $($newest.Name) ($([math]::Round($newest.Length / 1MB, 2)) MB)."
                Start-Sleep -Seconds 10
                break
            }
            Start-Sleep -Seconds 5
        }
        
        # Stop training runner
        $procs = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
            try {
                $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
                $cmd -like "*run_nineplus_confirmatory*"
            } catch { $false }
        }
        foreach ($p in $procs) {
            Log-Msg "Stopping Python training process PID $($p.Id) after completed epoch..."
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        }
        
        Log-Msg "Executing finalize_multiview_checkpoint.py to extract representations and compute Linear Probe on best checkpoint..."
        & "D:\Research\.venv-stage-a2-cuda\Scripts\python.exe" "D:\Research\scripts\finalize_multiview_checkpoint.py" --run-dir "$targetDir" --seed 7 --device cuda
        
        Log-Msg "Seed 7 safely finalized at 17:00 deadline. RUN-MANIFEST.json created. PC active."
        break
    }

    Start-Sleep -Seconds 5
}
