import torch
import json
from pathlib import Path

run_dir = Path("experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed999_1789541331")
pause_file = run_dir / "ADMINISTRATIVE_PAUSE.json"
manifest_file = run_dir / "RUN-MANIFEST.json"

print("=== PAUSE FILE ===")
if pause_file.exists():
    print(pause_file.read_text(encoding="utf-8"))

print("=== MANIFEST FILE ===")
if manifest_file.exists():
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    for k, v in manifest.items():
        if k != "epoch_history":
            print(f"{k}: {v}")
        else:
            print(f"epoch_history ({len(v)} epochs):")
            for ep in v:
                print(" ", ep)

print("=== CHECKPOINT AUDIT ===")
for ep in range(1, 8):
    p = run_dir / f"checkpoint_epoch{ep}.pt"
    if p.exists():
        c = torch.load(p, map_location="cpu", weights_only=False)
        print(f"Ep {ep}: keys={list(c.keys())}")
        print(f"   epoch={c.get('epoch')}, step={c.get('global_step')}, best_loss={c.get('best_val_loss')}, best_epoch={c.get('best_epoch')}, patience={c.get('patience_counter')}")
        print(f"   has_opt={'optimizer_state_dict' in c}, has_sched={'scheduler_state_dict' in c}, has_rng={'rng_state' in c}")
