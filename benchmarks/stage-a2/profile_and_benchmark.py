# -*- coding: utf-8 -*-
"""
Stage A2 Baseline Profiler and Benchmark Harness.
Measures reference implementation throughput, latency, GPU/CPU utilization,
and profiles hotpaths with cProfile and PyTorch profiler.
"""

import os
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
os.environ["PYTHONUNBUFFERED"] = "1"

import sys
import time
import json
import psutil
import pstats
import cProfile
from pathlib import Path
from typing import Dict, Any, List

import torch

from research_agent.experiments.models.temporal_graph_view_encoder import TemporalGraphViewEncoder
from research_agent.experiments.training.stage_a2_trainer import StageA2Trainer

def chunk_windows(events: List[Dict[str, Any]], window_size: int = 256) -> List[List[Dict[str, Any]]]:
    return [events[i:i+window_size] for i in range(0, len(events), window_size)]

def run_benchmark(fixture_path: Path):
    print("==========================================================")
    print("   STAGE A2 BASELINE PERFORMANCE PROFILING & BENCHMARK    ")
    print("==========================================================")

    # 1. Enforce determinism
    torch.use_deterministic_algorithms(True)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device} ({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'})")

    # 2. Load fixture
    raw_data = json.loads(fixture_path.read_text(encoding="utf-8"))
    print(f"Loaded {len(raw_data)} fixture events from {fixture_path.name}")

    warmup_events = raw_data[:1024]
    timed_events = raw_data[:8192]
    profile_events = raw_data[:2048]

    warmup_windows = chunk_windows(warmup_events, 256)
    timed_windows = chunk_windows(timed_events, 256)
    profile_windows = chunk_windows(profile_events, 256)

    # 3. Model & Trainer setup
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    model = TemporalGraphViewEncoder(
        d_node=128,
        d_edge=64,
        d_msg=128,
        n_heads=4,
        d_time_proj=32,
        d_rel_emb=32,
        d_type_emb=32,
        dropout=0.10,
        num_canonical_relations=8,
        num_node_types=4
    )

    trainer = StageA2Trainer(
        model=model,
        learning_rate=5e-4,
        weight_decay=0.01,
        min_lr=1e-5,
        warmup_ratio=0.05,
        temporal_window_size=256,
        gradient_accumulation_steps=4,
        clip_norm=1.0,
        max_epochs=20,
        early_stopping_patience=3,
        seed=42,
        execution_device="cuda",
        execution_mode="FIXTURE_TEST",
        empirical_authorized=True,
        total_steps_override=573 * 20
    )

    # 4. Warmup
    print(f"Running Warmup ({len(warmup_events)} events, {len(warmup_windows)} windows)...")
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    trainer.train_one_epoch(warmup_windows)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    print("Warmup complete.")

    # 5. Timed Baseline
    print(f"\nRunning Timed Baseline ({len(timed_events)} events, {len(timed_windows)} windows)...")
    trainer.model.reset_node_states()
    trainer.mask_generator.manual_seed(42)
    trainer.stream_cursor = 0
    trainer.global_step = 0
    trainer.grad_accum_position = 0

    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

    t_start = time.perf_counter()
    stats = trainer.train_one_epoch(timed_windows)

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t_end = time.perf_counter()

    elapsed = t_end - t_start
    events_per_sec = len(timed_events) / elapsed
    windows_per_sec = len(timed_windows) / elapsed
    opt_steps = stats["optimizer_steps"]
    steps_per_sec = opt_steps / elapsed

    vram_alloc_mb = (torch.cuda.max_memory_allocated() / (1024**2)) if torch.cuda.is_available() else 0
    vram_res_mb = (torch.cuda.max_memory_reserved() / (1024**2)) if torch.cuda.is_available() else 0

    print(f"Timed Baseline Elapsed: {elapsed:.3f} s")
    print(f"Throughput: {events_per_sec:.1f} events/s | {windows_per_sec:.2f} windows/s | {steps_per_sec:.2f} opt_steps/s")
    print(f"VRAM Peak: {vram_alloc_mb:.1f} MB allocated | {vram_res_mb:.1f} MB reserved")

    # Projections (ESTIMATE)
    train_total_events = 586577
    val_total_events = 119531
    est_train_time_sec = train_total_events / events_per_sec
    est_val_time_sec = (val_total_events / events_per_sec) * 0.75
    est_total_epoch_sec = est_train_time_sec + est_val_time_sec

    print("\n--- PERFORMANCE ESTIMATES (ESTIMATE) ---")
    print(f"ESTIMATE Train Time (586,577 events): {est_train_time_sec / 60.0:.2f} min ({est_train_time_sec:.1f} s)")
    print(f"ESTIMATE Val Time (119,531 events):   {est_val_time_sec / 60.0:.2f} min ({est_val_time_sec:.1f} s)")
    print(f"ESTIMATE Total Epoch Time:             {est_total_epoch_sec / 60.0:.2f} min ({est_total_epoch_sec:.1f} s)")

    # 6. Detailed Profiling
    print(f"\nProfiling Hotpath ({len(profile_events)} events)...")
    trainer.model.reset_node_states()
    trainer.mask_generator.manual_seed(42)
    trainer.stream_cursor = 0
    trainer.global_step = 0
    trainer.grad_accum_position = 0

    profiler = cProfile.Profile()
    profiler.enable()
    trainer.train_one_epoch(profile_windows)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    profiler.disable()

    stats_obj = pstats.Stats(profiler).sort_stats("cumulative")
    print("\n--- TOP 25 CUMULATIVE HOTSPOTS (cProfile) ---")
    stats_obj.print_stats(25)

    stats_tottime = pstats.Stats(profiler).sort_stats("tottime")
    print("\n--- TOP 25 SELF-TIME (tottime) HOTSPOTS (cProfile) ---")
    stats_tottime.print_stats(25)

    results = {
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None",
        "timed_events": len(timed_events),
        "elapsed_sec": elapsed,
        "events_per_sec": events_per_sec,
        "windows_per_sec": windows_per_sec,
        "steps_per_sec": steps_per_sec,
        "vram_alloc_mb": vram_alloc_mb,
        "vram_res_mb": vram_res_mb,
        "est_train_time_sec": est_train_time_sec,
        "est_val_time_sec": est_val_time_sec,
        "est_total_epoch_sec": est_total_epoch_sec
    }

    out_file = Path("D:/Research/benchmarks/stage-a2/baseline_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved baseline benchmark results to {out_file}")

if __name__ == "__main__":
    fixture_p = Path("D:/Research/benchmarks/stage-a2/fixtures/train_events_10240.json")
    run_benchmark(fixture_p)
