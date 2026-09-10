# Stage A2 Five-Seed Chronological Provenance & Protocol Audit Report

**Audit Date:** 2026-09-10  
**Branch:** `fix/stage-a2-forensic-final`  
**Base Commit:** `3864ea64eea490bf316edeaa733677a48e14df22`  
**Auditor:** Senior Research Reproducibility Engineer + Scientific Auditor  

---

## 1. Executive Summary & Forensic Seed Classifications

| Seed | Classification | Status | Epochs | Steps | Best Epoch | Best Val Loss | Final Train Loss | Execution Commit | Git Provenance & Protocol Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Seed 42** | `CANONICAL` | EARLY_STOPPED | 4 / 12 | 2,292 | 1 | `6.081352` | `0.308279` | `33269cbe...` | Adhered to Amendment 13 (20-epoch schedule, warmup 573); stopped early at epoch 4 by protocol rule. |
| **Seed 7** | `PROTOCOL_DEVIATION` | COMPLETED | 12 / 12 | 6,876 | 12 | `0.550259` | `0.160910` | `e4d53b82...` | Ran 12 epochs without prospective protocol amendment; authorization committed ~34h post-start. |
| **Seed 999** | `PROTOCOL_DEVIATION` | COMPLETED | 12 / 12 | 6,876 | 12 | `0.609500` | `0.159004` | `e4d53b82...` | Ran 12 epochs without prospective protocol amendment in PROTOCOL-AMENDMENTS.md. |
| **Seed 1337** | `NONCANONICAL` | INCOMPLETE | 12 / 20 | 6,876 | 10 | `0.917827` | `0.184784` | `33269cbe...` | Incomplete 20-epoch schedule, halted at epoch 12 (`lr=0.000195`), missing run-level artifacts. |
| **Seed 2024** | `NONCANONICAL` | FLAWED | 12 / 12 | 6,876 | 12 | `0.553257` | `0.167085` | `e4d53b82...` | Phantom commit `00ce524e`, retroactive authorization, mid-run schedule alteration. |

---

## 2. Chronological Git Provenance Timeline

An exhaustive git history audit using commit timestamps reveals:

1. **Protocol Amendments (2026-08-28 10:24:59 +0700, commit `33269cbe`):**
   - Amendment 12 locked `max_epochs = 20`, `warmup_steps = 573`, `total_steps = 11,460`.
   - Amendment 13 moved execution to `LOCAL_WINDOWS_GPU` while explicitly maintaining all scientific parameters invariant.
   - **No prospective protocol amendment for 12 epochs was ever recorded in `PROTOCOL-AMENDMENTS.md`.**
2. **Seed 42 Launch (2026-08-28 10:25:53 +0700):**
   - Authorization committed in `c8879181` prior to run launch (`10:26:33 +0700`). Compliant with protocol.
3. **Seed 1337 Launch (2026-08-29 23:20:24 +0700):**
   - Authorization committed in `84d1aa95` for 20 epochs. Halted at epoch 12.
4. **Seed 2024 Launch (2026-09-02 21:02:35 +0700):**
   - Started on 20-epoch schedule. Plan modified mid-run to 12 epochs in commit `68cdcbf` on 2026-09-03.
5. **Seed 7 Launch (2026-09-05 22:17:43 +0700):**
   - Began training on 2026-09-05. Its launch authorization was committed to Git on 2026-09-07 in `b53b7264` (~34 hours later).
6. **Seed 999 Launch (2026-09-08 23:12:43 +0700):**
   - Authorization committed on 2026-09-08 23:11:15 (`244e81a5`), but 12-epoch ceiling has no scientific amendment.

---

## 3. Strict Machine-Readable Aggregates

- **Canonical Subset ($N=1$, Seed 42):**
  - Best Val Loss: `6.081352`
  - Final Train Loss: `0.308279`
  - Standard deviation is undefined for $N=1$.
- **Protocol Deviation Subset ($N=2$, Seed 7 & Seed 999):**
  - Mean Best Val Loss: `0.579880`
  - Sample Std Best Val Loss: `0.041890`
  - Mean Final Train Loss: `0.159957`
  - Kept strictly distinct from the Canonical aggregate.
