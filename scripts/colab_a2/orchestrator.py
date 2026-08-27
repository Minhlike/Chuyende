# -*- coding: utf-8 -*-
"""
Stage A2 Local Orchestrator via Google Colab CLI.
Manages persistent named sessions, remote preparation, deterministic qualification,
single-seed execution, log streaming, failure recovery, and permanent archival.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List

from scripts.colab_a2.wsl_bridge import ColabCLIBridge
from scripts.colab_a2.remote_prepare import run_remote_prepare, FROZEN_EXECUTION_COMMIT
from scripts.colab_a2.remote_qualify import run_remote_qualify
from scripts.colab_a2.remote_train import CANONICAL_SEEDS, run_seed_dry_run, authorize_and_launch_seed
from scripts.colab_a2.archive_run import archive_completed_seed

def query_drive_seed_status(bridge: ColabCLIBridge, seed: int) -> Dict[str, Any]:
    """Inspects remote Google Drive state for a given seed."""
    check_code = f"""
import json
from pathlib import Path

durable_root = Path('/content/drive/MyDrive/Chuyende-stage-a2')
run_dir_1 = durable_root / 'runs' / 'stage-a2' / 'HDFS' / 'seed-{seed}'
run_dir_2 = durable_root / 'runs' / 'HDFS' / 'seed-{seed}'
run_dir = run_dir_1 if run_dir_1.exists() else run_dir_2

state_info = {{
    "seed": {seed},
    "exists": run_dir.exists(),
    "status": "NOT_STARTED",
    "completed_epoch": 0,
    "next_epoch": 0,
    "global_step": 0,
    "best_val_loss": None,
    "last_checkpoint_sha": None,
    "checkpoint_inventory_count": 0
}}

if run_dir.exists():
    state_p = run_dir / 'RUN-STATE.json'
    if state_p.exists():
        data = json.loads(state_p.read_text(encoding='utf-8'))
        state_info["status"] = data.get("status", "UNKNOWN")
        state_info["completed_epoch"] = data.get("completed_epoch", 0)
        state_info["next_epoch"] = data.get("next_epoch_to_run", 0)
        state_info["global_step"] = data.get("global_step", 0)
        state_info["best_val_loss"] = data.get("best_val_loss")
        state_info["last_checkpoint_sha"] = data.get("last_checkpoint_sha256")
    
    inv_p = run_dir / 'CHECKPOINT-INVENTORY.json'
    if inv_p.exists():
        inv_data = json.loads(inv_p.read_text(encoding='utf-8'))
        state_info["checkpoint_inventory_count"] = len(inv_data.get("checkpoints", []))

print("__JSON_STATE__:" + json.dumps(state_info))
"""
    rc, out, err = bridge.exec_code(check_code.strip())
    if rc == 0:
        for line in out.splitlines():
            if line.startswith("__JSON_STATE__:"):
                return json.loads(line.replace("__JSON_STATE__:", "").strip())
    return {"seed": seed, "exists": False, "status": "UNKNOWN_OR_UNREACHABLE"}

def get_next_canonical_seed(seed_statuses: Dict[int, Dict[str, Any]]) -> Optional[int]:
    """Determines the next canonical seed to execute."""
    for s in CANONICAL_SEEDS:
        info = seed_statuses.get(s, {})
        if info.get("status") != "COMPLETED":
            return s
    return None

def main():
    parser = argparse.ArgumentParser(description="Stage A2 Local Orchestrator via Google Colab CLI")
    parser.add_argument("command", choices=["status", "prepare", "qualify", "run-next", "resume", "archive", "stop", "auto"],
                        help="Orchestrator action")
    parser.add_argument("--session", type=str, default="stage-a2", help="Colab CLI session name")
    parser.add_argument("--gpu", type=str, default=None, help="GPU type (T4, L4, A100)")
    parser.add_argument("--seed", type=int, default=None, help="Specific canonical seed (42, 1337, 2024, 7, 999)")
    parser.add_argument("--all", action="store_true", default=False, help="Prohibited for real training")
    
    args = parser.parse_args()
    
    if args.all and args.command in ["run-next", "resume", "auto"]:
        print("FATAL ERROR: Flag --all is strictly PROHIBITED for real empirical execution!")
        sys.exit(1)
        
    bridge = ColabCLIBridge(session_name=args.session, gpu_type=args.gpu or "T4")
    
    if args.command == "status":
        print(f"=== Stage A2 Orchestrator Status (Session: {args.session}) ===")
        sess_status = bridge.get_session_status()
        print(f"Colab Session Active: {sess_status['exists']}")
        if not sess_status['exists']:
            print("Session status: STOPPED / NOT ALLOCATED")
            return
        
        print("\n--- Durable Google Drive Seed Statuses ---")
        seed_statuses = {}
        for s in CANONICAL_SEEDS:
            st = query_drive_seed_status(bridge, s)
            seed_statuses[s] = st
            print(f"Seed {s:4d}: Status={st.get('status'):12s} | Completed Epoch={st.get('completed_epoch', 0):2d} | Step={st.get('global_step', 0):5d} | Best Val L_graph={st.get('best_val_loss')}")
        
        next_s = get_next_canonical_seed(seed_statuses)
        print(f"\nNext Pending Canonical Seed: {next_s if next_s is not None else 'ALL_5_SEEDS_COMPLETED'}")
        
    elif args.command == "prepare":
        bridge.mount_drive()
        ok, msg = run_remote_prepare(bridge)
        if not ok:
            sys.exit(1)
            
    elif args.command == "qualify":
        ok, msg = run_remote_qualify(bridge)
        if not ok:
            sys.exit(1)
            
    elif args.command == "run-next":
        bridge.mount_drive()
        seed_statuses = {s: query_drive_seed_status(bridge, s) for s in CANONICAL_SEEDS}
        target_seed = args.seed or get_next_canonical_seed(seed_statuses)
        if target_seed is None:
            print("All 5 canonical seeds are already COMPLETED!")
            return
        
        if seed_statuses[target_seed].get("status") == "COMPLETED":
            print(f"FATAL: Seed {target_seed} is already COMPLETED! Overwrite protection active.")
            sys.exit(1)
            
        if target_seed == 42 and seed_statuses[42].get("status") == "RUNNING":
            print("FATAL: Seed 42 is currently RUNNING (browser runtime protected). Do not disrupt.")
            sys.exit(1)
            
        # 1. Dry run
        dry_ok, _ = run_seed_dry_run(bridge, target_seed)
        if not dry_ok:
            print(f"Dry run failed for Seed {target_seed}!")
            sys.exit(1)
            
        # 2. Authorize and launch
        train_ok, _ = authorize_and_launch_seed(bridge, target_seed)
        if not train_ok:
            print(f"Training failed for Seed {target_seed}!")
            sys.exit(1)
            
    elif args.command == "archive":
        target_seed = args.seed or 42
        ok, msg = archive_completed_seed(bridge, target_seed)
        if not ok:
            sys.exit(1)
            
    elif args.command == "stop":
        bridge.stop_session()
        
    elif args.command == "auto":
        print("=== STAGE A2 AUTO-ORCHESTRATION PIPELINE ===")
        # Fail closed auto loop
        if not bridge.get_session_status()['exists']:
            print("Allocating new session...")
            if not bridge.create_session():
                sys.exit(1)
        bridge.mount_drive()
        
        seed_statuses = {s: query_drive_seed_status(bridge, s) for s in CANONICAL_SEEDS}
        next_s = get_next_canonical_seed(seed_statuses)
        if next_s is None:
            print("All canonical seeds COMPLETED!")
            return
            
        if next_s == 42 and seed_statuses[42].get("status") == "RUNNING":
            print("Seed 42 is currently running in manual browser session. Waiting for completion.")
            return
            
        # Prepare & Qualify
        run_remote_prepare(bridge)
        run_remote_qualify(bridge)
        
        while next_s is not None:
            print(f"\n>>> Executing Canonical Seed {next_s} <<<")
            run_seed_dry_run(bridge, next_s)
            ok, _ = authorize_and_launch_seed(bridge, next_s)
            if not ok:
                print(f"FATAL: Execution failed on Seed {next_s}!")
                sys.exit(1)
            archive_completed_seed(bridge, next_s)
            seed_statuses = {s: query_drive_seed_status(bridge, s) for s in CANONICAL_SEEDS}
            next_s = get_next_canonical_seed(seed_statuses)
            
        print("All 5 Canonical Seeds Finished & Archived Successfully.")

if __name__ == "__main__":
    main()
