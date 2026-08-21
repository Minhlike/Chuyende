# -*- coding: utf-8 -*-
"""
H3 Canonical Test Contract & Executable Perturbation Suite (P01..P12)
Implements Chapter 2 & Chapter 3 Frozen Robustness Protocol:
  - Strict PR-AUC Chance Baseline: Defined by positive sample prevalence (positive_count / total_count), NOT fixed 0.50.
  - 12 Fully Executable Semantic-Preserving Perturbation Operators (P01..P12):
      * P01: Token Deletion
      * P02: Token Insertion Noise
      * P03: Parameter Obfuscation
      * P04: Event Order Jitter
      * P05: IP Subnet Translation
      * P06: Path Aliasing
      * P07: Burst Interleaving
      * P08: Unseen Template Shift
      * P09: Host Reassignment
      * P10: Entity Pseudonym Rotation
      * P11: Timestamp Skew
      * P12: Composite Perturbation
  - Benjamini-Hochberg False Discovery Rate (BH-FDR) Multiplicity Correction.
"""

import re
import random
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

# -----------------------------------------------------------------------------
# EXECUTABLE PERTURBATION OPERATORS (P01 .. P12)
# -----------------------------------------------------------------------------

def apply_p01_token_deletion(lines: List[str], seed: int = 42, budget: float = 0.1) -> List[str]:
    """P01: Randomly drops budget fraction of non-critical tokens."""
    rng = random.Random(seed)
    perturbed = []
    for line in lines:
        tokens = line.split()
        if len(tokens) <= 3:
            perturbed.append(line)
            continue
        kept = [t for t in tokens if rng.random() > budget or t.startswith("blk_")]
        perturbed.append(" ".join(kept) if kept else line)
    return perturbed

def apply_p02_token_insertion_noise(lines: List[str], seed: int = 42, budget: float = 0.1) -> List[str]:
    """P02: Injects benign background noise log lines."""
    rng = random.Random(seed)
    noise_templates = [
        "org.apache.hadoop.hdfs.server.datanode.DataNode: Periodic Block Pool Scanner complete",
        "org.apache.hadoop.hdfs.StateChange: BLOCK* ask 10.0.0.1:50010 to delete block",
        "INFO dfs.DataBlockScanner: Verification succeeded for block"
    ]
    perturbed = []
    for line in lines:
        perturbed.append(line)
        if rng.random() < budget:
            perturbed.append(rng.choice(noise_templates))
    return perturbed

def apply_p03_parameter_obfuscation(lines: List[str], seed: int = 42, budget: float = 0.2) -> List[str]:
    """P03: Obfuscates numerical / hex parameter representations."""
    perturbed = []
    for line in lines:
        # Convert hex to dec or vice versa
        def hex_to_dec(m):
            return str(int(m.group(0), 16))
        new_line = re.sub(r"0x[0-9a-fA-F]+", hex_to_dec, line)
        perturbed.append(new_line)
    return perturbed

def apply_p04_event_order_jitter(lines: List[str], seed: int = 42, window_size: int = 3) -> List[str]:
    """P04: Shuffles concurrent event order within sliding window."""
    rng = random.Random(seed)
    perturbed = list(lines)
    for i in range(0, len(perturbed) - window_size, window_size):
        chunk = perturbed[i:i + window_size]
        rng.shuffle(chunk)
        perturbed[i:i + window_size] = chunk
    return perturbed

def apply_p05_ip_subnet_translation(lines: List[str], seed: int = 42) -> List[str]:
    """P05: Translates IP subnets preserving internal/external topology."""
    perturbed = []
    for line in lines:
        # Translate 10.x.x.x -> 192.168.x.x
        new_line = re.sub(r"\b10\.(\d+)\.(\d+)\.(\d+)\b", r"192.168.\2.\3", line)
        perturbed.append(new_line)
    return perturbed

def apply_p06_path_aliasing(lines: List[str], seed: int = 42) -> List[str]:
    """P06: Replaces path separators with redundant relative aliases."""
    perturbed = []
    for line in lines:
        new_line = line.replace("/etc/", "/etc/./").replace("/tmp/", "/tmp/../tmp/")
        perturbed.append(new_line)
    return perturbed

def apply_p07_burst_interleaving(lines: List[str], seed: int = 42, burst_count: int = 5) -> List[str]:
    """P07: Interleaves high-volume repetitive logging bursts."""
    burst_line = "INFO datanode.DataNode: Heartbeat received from namenode"
    perturbed = []
    for idx, line in enumerate(lines):
        perturbed.append(line)
        if idx == len(lines) // 2:
            perturbed.extend([burst_line] * burst_count)
    return perturbed

def apply_p08_unseen_template_shift(lines: List[str], seed: int = 42) -> List[str]:
    """P08: Replaces verbs with semantic synonyms."""
    synonyms = {"Received": "Accepted", "Served": "Delivered", "Terminated": "Ended", "Starting": "Initiating"}
    perturbed = []
    for line in lines:
        for k, v in synonyms.items():
            line = line.replace(k, v)
        perturbed.append(line)
    return perturbed

def apply_p09_host_reassignment(lines: List[str], seed: int = 42) -> List[str]:
    """P09: Replaces hostname identifiers with unseen host domain."""
    perturbed = []
    for line in lines:
        new_line = re.sub(r"host-\d+", "worker-node-alt", line)
        perturbed.append(new_line)
    return perturbed

def apply_p10_entity_pseudonym_rotation(lines: List[str], seed: int = 42) -> List[str]:
    """P10: Rotates entity pseudonym markers."""
    perturbed = []
    for line in lines:
        new_line = re.sub(r"<PSEUDO:([0-9a-f]+)>", r"<PSEUDO_ROTATED:\1>", line)
        perturbed.append(new_line)
    return perturbed

def apply_p11_timestamp_skew(lines: List[str], seed: int = 42, jitter_sec: float = 2.0) -> List[str]:
    """P11: Adds Gaussian time jitter to event timestamps."""
    rng = random.Random(seed)
    perturbed = []
    for line in lines:
        # Match epoch timestamp
        def jitter_ts(m):
            ts = float(m.group(0)) + rng.gauss(0, jitter_sec)
            return str(int(max(0, ts)))
        new_line = re.sub(r"\b1[1-7]\d{8}\b", jitter_ts, line)
        perturbed.append(new_line)
    return perturbed

def apply_p12_composite_perturbation(lines: List[str], seed: int = 42) -> List[str]:
    """P12: Composite perturbation applying P01 + P03 + P05 + P11."""
    out = apply_p01_token_deletion(lines, seed=seed, budget=0.05)
    out = apply_p03_parameter_obfuscation(out, seed=seed)
    out = apply_p05_ip_subnet_translation(out, seed=seed)
    out = apply_p11_timestamp_skew(out, seed=seed)
    return out

PERTURBATION_DISPATCHER: Dict[str, Callable[[List[str], int], List[str]]] = {
    "P01_Token_Deletion": lambda l, s: apply_p01_token_deletion(l, seed=s),
    "P02_Token_Insertion_Noise": lambda l, s: apply_p02_token_insertion_noise(l, seed=s),
    "P03_Parameter_Obfuscation": lambda l, s: apply_p03_parameter_obfuscation(l, seed=s),
    "P04_Event_Order_Jitter": lambda l, s: apply_p04_event_order_jitter(l, seed=s),
    "P05_IP_Subnet_Translation": lambda l, s: apply_p05_ip_subnet_translation(l, seed=s),
    "P06_Path_Aliasing": lambda l, s: apply_p06_path_aliasing(l, seed=s),
    "P07_Burst_Interleaving": lambda l, s: apply_p07_burst_interleaving(l, seed=s),
    "P08_Unseen_Template_Shift": lambda l, s: apply_p08_unseen_template_shift(l, seed=s),
    "P09_Host_Reassignment": lambda l, s: apply_p09_host_reassignment(l, seed=s),
    "P10_Entity_Pseudonym_Rotation": lambda l, s: apply_p10_entity_pseudonym_rotation(l, seed=s),
    "P11_Timestamp_Skew": lambda l, s: apply_p11_timestamp_skew(l, seed=s),
    "P12_Composite_Perturbation": lambda l, s: apply_p12_composite_perturbation(l, seed=s),
}

# -----------------------------------------------------------------------------
# H3 EVALUATION CONTRACT
# -----------------------------------------------------------------------------

def evaluate_h3_robustness_contract(
    y_true: np.ndarray,
    clean_scores: np.ndarray,
    perturbed_scores_dict: Dict[str, np.ndarray],
    cluster_ids: np.ndarray,
    b_resamples: int = 2000,
    seed: int = 10007,
    q_fdr: float = 0.05
) -> Dict[str, Any]:
    """
    Evaluates representation invariance across all 12 perturbation operators using BH-FDR.
    Chance baseline is dynamically derived from positive prevalence.
    """
    from research_agent.experiments.protocols.paired_cluster_bootstrap import (
        paired_cluster_bootstrap_recompute,
        apply_benjamini_hochberg_fdr,
        compute_pr_auc
    )

    y_true_arr = np.asarray(y_true)
    positive_count = int(np.sum(y_true_arr))
    total_count = len(y_true_arr)
    positive_prevalence = float(positive_count / max(1, total_count))
    chance_level = positive_prevalence

    clean_pr_auc = compute_pr_auc(y_true_arr, clean_scores)

    raw_p_values = {}
    perturbation_reports = {}
    collapsed_to_chance_flags = []

    for p_id, p_func in PERTURBATION_DISPATCHER.items():
        if p_id not in perturbed_scores_dict:
            perturbation_reports[p_id] = {"status": "PENDING"}
            continue

        p_scores = perturbed_scores_dict[p_id]
        p_pr_auc = compute_pr_auc(y_true_arr, p_scores)

        # Bootstrap comparison: Clean vs Perturbed
        boot_res = paired_cluster_bootstrap_recompute(
            cluster_ids=cluster_ids,
            y_true=y_true_arr,
            y_pred_proposed=p_scores,
            y_pred_baseline=clean_scores,
            metric_fn=compute_pr_auc,
            b_resamples=b_resamples,
            random_seed=seed
        )

        raw_p_values[p_id] = boot_res["p_value"]

        # Falsification check: Falsified if PR-AUC drops to chance level (positive prevalence + 0.02 margin)
        collapsed_to_chance = bool(p_pr_auc <= (chance_level + 0.02))
        collapsed_to_chance_flags.append(collapsed_to_chance)

        perturbation_reports[p_id] = {
            "pr_auc_under_perturbation": p_pr_auc,
            "pr_auc_clean": clean_pr_auc,
            "delta_pr_auc": boot_res["observed_delta"],
            "ci_95": boot_res["ci_95"],
            "raw_p_value": boot_res["p_value"],
            "positive_prevalence_chance": positive_prevalence,
            "collapsed_to_chance": collapsed_to_chance
        }

    # Apply BH-FDR correction across all tested perturbations
    bh_decisions = apply_benjamini_hochberg_fdr(raw_p_values, q_threshold=q_fdr)
    for p_id, bh in bh_decisions.items():
        if p_id in perturbation_reports:
            perturbation_reports[p_id]["bh_fdr_rank"] = bh["rank"]
            perturbation_reports[p_id]["bh_critical_value"] = bh["bh_critical_value"]
            perturbation_reports[p_id]["bh_rejected_null"] = bh["rejected_null"]

    overall_falsified = any(collapsed_to_chance_flags) if collapsed_to_chance_flags else True

    return {
        "hypothesis_id": "H3_Robustness_Shortcut_Invariance",
        "description": "Invariance under 12 Executable Perturbations (P01..P12)",
        "positive_prevalence": positive_prevalence,
        "chance_level_pr_auc": chance_level,
        "clean_pr_auc": clean_pr_auc,
        "perturbation_evaluations": perturbation_reports,
        "falsification_status": "FALSIFIED" if overall_falsified else "NOT_FALSIFIED"
    }
