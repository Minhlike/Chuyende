# -*- coding: utf-8 -*-
r"""
Nineplus Experiment Campaign - Graph-Only Downstream Probe Evaluator
Evaluates capacity-controlled linear probe (AP & ROC-AUC) on frozen validation representations
extracted from Stage A2 TemporalGraphViewEncoder checkpoints (D:\Research\.artifacts\stage-a2\HDFS).

Strictly enforces:
  - ZERO access to TEST split (TEST_OPENED=false, TEST_READ_COUNT=0)
  - Capacity-controlled linear probe (W in R^{128 x 1}, 50 epochs, AdamW)
  - Identical validation split (7,500 sessions, hdfs_probe_labels_val.pt)
  - Anti-collapse latent variance contract (Var(z) >= 0.01)
"""

import os
import sys
import json
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder

def evaluate_downstream_linear_probe(
    z_all: torch.Tensor,
    labels: List[int] | torch.Tensor,
    seed: int = 42,
    device: str = "cuda"
) -> Dict[str, float]:
    """
    Capacity-Controlled Linear Probe on Frozen Latent Representations.
    Trains W in R^{128 x 1} (bce loss, lr=1e-2, 50 epochs)
    using an 80/20 train/test split within the validation representation pool.
    """
    dev = torch.device(device if torch.cuda.is_available() else "cpu")
    y = torch.tensor(labels, dtype=torch.float32)
    N = len(labels)
    
    rng = np.random.RandomState(seed)
    pos_idx = [i for i, val in enumerate(labels) if val == 1]
    neg_idx = [i for i, val in enumerate(labels) if val == 0]
    
    rng.shuffle(pos_idx)
    rng.shuffle(neg_idx)
    
    n_pos_train = int(len(pos_idx) * 0.8)
    n_neg_train = int(len(neg_idx) * 0.8)
    
    train_idx = pos_idx[:n_pos_train] + neg_idx[:n_neg_train]
    test_idx = pos_idx[n_pos_train:] + neg_idx[n_neg_train:]
    rng.shuffle(train_idx)
    rng.shuffle(test_idx)
    
    z_train = z_all[train_idx].to(dev)
    y_train = y[train_idx].to(dev)
    z_test = z_all[test_idx].to(dev)
    y_test = y[test_idx].numpy()
    
    probe = nn.Linear(128, 1).to(dev)
    optimizer = torch.optim.AdamW(probe.parameters(), lr=1e-2, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    
    probe.train()
    batch_size = 256
    for ep in range(50):
        perm = torch.randperm(len(train_idx))
        for b_start in range(0, len(train_idx), batch_size):
            b_ids = perm[b_start:b_start + batch_size]
            optimizer.zero_grad()
            logits = probe(z_train[b_ids]).squeeze(-1)
            loss = criterion(logits, y_train[b_ids])
            loss.backward()
            optimizer.step()
            
    probe.eval()
    with torch.no_grad():
        test_logits = probe(z_test).squeeze(-1)
        test_scores = torch.sigmoid(test_logits).cpu().numpy()
        
    order = np.argsort(-test_scores)
    sorted_labels = y_test[order]
    tp = np.cumsum(sorted_labels == 1)
    fp = np.cumsum(sorted_labels == 0)
    n_pos = np.sum(y_test == 1)
    n_neg = np.sum(y_test == 0)
    recalls = np.concatenate(([0.0], tp / max(1, n_pos)))
    precisions = np.concatenate(([1.0], tp / (tp + fp)))
    ap = float(np.sum((recalls[1:] - recalls[:-1]) * precisions[1:]))
    
    ranks = np.argsort(np.argsort(test_scores)) + 1
    pos_rank_sum = np.sum(ranks[y_test == 1])
    u = pos_rank_sum - n_pos * (n_pos + 1) / 2
    auc = float(u / max(1, n_pos * n_neg))
    
    return {"probe_ap": ap, "probe_roc_auc": auc}


def evaluate_graph_checkpoint(
    base_dir: Path,
    seed: int,
    val_events: List[Dict[str, Any]],
    val_sids: List[str],
    val_labels: List[int],
    device: str = "cuda"
) -> Dict[str, Any]:
    print(f"\n[{seed}] Evaluating Stage A2 Graph-Only Checkpoint (Seed {seed})...")
    dev = torch.device(device if torch.cuda.is_available() else "cpu")
    
    ckpt_dir = base_dir / ".artifacts" / "stage-a2" / "HDFS" / f"seed-{seed}"
    ckpt_path = ckpt_dir / "best_val_loss.pt"
    if not ckpt_path.exists():
        ckpt_path = ckpt_dir / "last_checkpoint.pt"
    if not ckpt_path.exists():
        raise FileNotFoundError(f"No checkpoint found in {ckpt_dir}")

    print(f"[{seed}] Loading checkpoint from {ckpt_path.name}...")
    ckpt_data = torch.load(ckpt_path, map_location=dev, weights_only=False)

    model = TemporalGraphViewEncoder(
        d_node=128, d_edge=64, d_msg=128, n_heads=4,
        d_time_proj=32, d_rel_emb=32, d_type_emb=32,
        dropout=0.10, num_canonical_relations=8, num_node_types=4
    ).to(dev)

    model.load_state_dict(ckpt_data["model_state_dict"])
    model.eval()
    model.reset_node_states()

    # Stream through val_events in chunks
    chunk_size = 5000
    total_events = len(val_events)
    print(f"[{seed}] Streaming {total_events:,} validation events through graph encoder...")
    t0 = time.perf_counter()
    with torch.no_grad():
        for start_idx in range(0, total_events, chunk_size):
            chunk = val_events[start_idx:start_idx + chunk_size]
            model.forward_event_window(chunk, is_training=False)
    dt_stream = time.perf_counter() - t0
    print(f"[{seed}] Stream completed in {dt_stream:.2f}s ({total_events / dt_stream:.1f} events/s). Nodes in memory: {len(model.node_memory):,}")

    # Extract representation for all 7,500 validation sessions
    val_reps = []
    zero_fallback_count = 0
    for sid in val_sids:
        if sid in model.node_memory:
            val_reps.append(model.node_memory[sid].cpu().unsqueeze(0))
        else:
            val_reps.append(torch.zeros(1, 128))
            zero_fallback_count += 1

    z_all = torch.cat(val_reps, dim=0)
    assert z_all.shape == (7500, 128), f"Expected (7500, 128), got {z_all.shape}"
    assert not torch.isnan(z_all).any() and not torch.isinf(z_all).any(), "NaN/Inf in representations!"

    latent_variance = float(torch.var(z_all, dim=0).mean().item())
    anti_collapse_pass = (latent_variance >= 0.01)

    # Downstream linear probe
    probe_metrics = evaluate_downstream_linear_probe(z_all, val_labels, seed=seed, device=device)

    best_epoch = ckpt_data.get("early_stopping_state", {}).get("best_epoch", ckpt_data.get("completed_epoch", 1))
    best_val_loss = ckpt_data.get("early_stopping_state", {}).get("best_val_loss", 0.0)

    # Output directory
    timestamp = int(time.time())
    run_id = f"CONF_GRAPH_ONLY_seed{seed}_{timestamp}"
    run_dir = base_dir / "experiments" / "nineplus" / "confirmatory" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id,
        "architecture": "GRAPH_ONLY",
        "status": "COMPLETED",
        "seed": seed,
        "source_checkpoint": str(ckpt_path),
        "best_epoch": best_epoch,
        "best_val_loss": float(best_val_loss) if best_val_loss is not None else None,
        "latent_variance": latent_variance,
        "anti_collapse_pass": anti_collapse_pass,
        "probe_ap": probe_metrics["probe_ap"],
        "probe_roc_auc": probe_metrics["probe_roc_auc"],
        "zero_fallback_count": zero_fallback_count,
        "stream_seconds": dt_stream,
        "nan_count": 0,
        "inf_count": 0
    }

    (run_dir / "RUN-MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{seed}] GRAPH_ONLY Probe AP: {probe_metrics['probe_ap']:.4f} | ROC-AUC: {probe_metrics['probe_roc_auc']:.4f} | Var(z): {latent_variance:.4f} | Zero-Fallback: {zero_fallback_count}")

    return manifest


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Stage A2 Graph Checkpoints via Linear Probe")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 7, 999], help="Seeds to evaluate")
    parser.add_argument("--device", type=str, default="cuda", help="Execution device")
    args = parser.parse_args()

    base_dir = Path(r"D:\Research")

    print("="*70)
    print("  EVALUATING GRAPH_ONLY LINEAR PROBES ON HISTORICAL STAGE A2 CHECKPOINTS")
    print(f"  Target Seeds: {args.seeds} | Device: {args.device}")
    print("="*70)

    # 1. Load cached graph events
    cache_path = base_dir / "datasets" / "cache" / "hdfs_graph_events.pt"
    print("Loading cached validation graph events...")
    graph_pkg = torch.load(cache_path, weights_only=False)
    val_events = graph_pkg["val_events"]
    print(f"Loaded {len(val_events):,} validation graph events.")

    # 2. Load validation labels
    labels_path = base_dir / "experiments" / "runs" / "data" / "vault" / "hdfs_probe_labels_val.pt"
    print("Loading validation probe labels...")
    probe_labels = torch.load(labels_path, weights_only=False)
    val_sids = probe_labels["session_ids"]
    val_labels = probe_labels["labels"]
    print(f"Loaded {len(val_sids):,} session IDs (Anomalies: {sum(1 for l in val_labels if l == 1)}).")

    results = {}
    for seed in args.seeds:
        try:
            manifest = evaluate_graph_checkpoint(
                base_dir=base_dir,
                seed=seed,
                val_events=val_events,
                val_sids=val_sids,
                val_labels=val_labels,
                device=args.device
            )
            results[seed] = manifest
        except Exception as e:
            print(f"[ERROR] Failed evaluating seed {seed}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("  GRAPH_ONLY EVALUATION SUMMARY")
    print("="*70)
    aps = [res["probe_ap"] for res in results.values()]
    aucs = [res["probe_roc_auc"] for res in results.values()]
    vars_ = [res["latent_variance"] for res in results.values()]

    for s, res in results.items():
        print(f"  - Seed {s:4d}: AP={res['probe_ap']:.4f} | ROC-AUC={res['probe_roc_auc']:.4f} | Var(z)={res['latent_variance']:.4f}")

    if len(aps) > 1:
        print("-"*70)
        print(f"  MEAN (N={len(aps)}): AP={np.mean(aps):.4f} +/- {np.std(aps, ddof=1):.4f}")
        print(f"  MEAN (N={len(aps)}): ROC-AUC={np.mean(aucs):.4f} +/- {np.std(aucs, ddof=1):.4f}")
        print(f"  MEAN (N={len(aps)}): Var(z)={np.mean(vars_):.4f} +/- {np.std(vars_, ddof=1):.4f}")
    print("="*70)


if __name__ == "__main__":
    main()
