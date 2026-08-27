# STAGE A2 GOOGLE COLAB CLI AUTOMATION GUIDE

## 1. Overview
This automation framework enables complete, unattended, fail-closed orchestration of Stage A2 pretraining across the 5 canonical seeds (42, 1337, 2024, 7, 999) using the official `google-colab-cli` via WSL2.

## 2. Architecture
```
Host (Windows 11) / WSL2 Orchestrator
        ↓ (colab new / exec / drivemount / status)
Google Colab GPU VM (Linux T4/L4/A100)
        ↓ (git checkout d89f09b4039bd368cef60b30ae4b8ad9ba6c5e67)
Repository & PyTorch 2.6.0+cu124 Environment Lock
        ↓ (scripts/run_stage_a2_five_seed_empirical.py)
Google Drive Durable Storage (/content/drive/MyDrive/Chuyende-stage-a2)
```

## 3. CLI Commands
- `python scripts/colab_a2/orchestrator.py status` : Inspect session and Drive progress.
- `python scripts/colab_a2/orchestrator.py prepare` : Clean checkout of frozen commit & dataset copy.
- `python scripts/colab_a2/orchestrator.py qualify` : Run deterministic qualification & mirror evidence.
- `python scripts/colab_a2/orchestrator.py run-next` : Dry-run, authorize, and train the next pending seed.
- `python scripts/colab_a2/orchestrator.py archive --seed <int>` : Create immutable ZIP archive + SHA-256.
- `python scripts/colab_a2/orchestrator.py stop` : Stop the remote Colab session.
- `python scripts/colab_a2/orchestrator.py auto` : Run automated end-to-end multi-seed pipeline.

## 4. Invariants
- Frozen execution commit: `d89f09b4039bd368cef60b30ae4b8ad9ba6c5e67`
- Flag `--all` is strictly prohibited for real empirical training.
- Test firewall remains locked (`TEST_OPENED=false`).
- Completed seeds are never overwritten.
