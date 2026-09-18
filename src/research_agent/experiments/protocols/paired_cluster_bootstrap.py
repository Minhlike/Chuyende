# -*- coding: utf-8 -*-
"""
Công cụ Bootstrap cụm được ghép nối với tính toán lại số liệu đầy đủ
Triển khai Chương 3 Giao thức thống kê được đăng ký trước:
  - Chính xác B = 2000 mẫu lại, seed chính xác = 10007
  - Chỉ số chính: Độ chính xác trung bình (AP), khớp với sklearn.metrics.average_precision_score
  - Hệ mét phụ: Hình thang PR-AUC
  - Tái tạo lại toàn bộ nhóm quan sát mẫu trên mỗi mẫu lại cụm
  - Nhiều điều chỉnh thử nghiệm:
      * H1: Họ Bonferroni gồm 4 người (alpha = 0,0125)
      * H2: Họ Bonferroni gồm 3 người (alpha = 0,0167)
      * H3: Stewamini-Hochberg FDR trên P01..P12
      * H5: Holm-Bonferroni hạ bệ qua các bài kiểm tra đối thủ
  - Trạng thái quyết định thống kê: SUPPORTED, INCONCLUSIVE, FALSIFIED (Zero ACCEPT_H0)
"""

from typing import Dict, Any, List, Tuple, Optional, Callable
import numpy as np

def compute_average_precision(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Tính toán Độ chính xác trung bình (AP) dưới dạng tích phân từng bước trên đường cong thu hồi độ chính xác.
    Định nghĩa toán học chính xác: AP = sum_n (R_n - R_{n-1}) * P_n
    Phù hợp với sklearn.metrics.average_precision_score.
    """
    y_true = np.asarray(y_true, dtype=np.int32)
    y_score = np.asarray(y_score, dtype=np.float64)

    pos_count = int(np.sum(y_true))
    if pos_count == 0 or len(y_true) == 0:
        return 0.0

    # Sắp xếp giảm dần theo điểm
    sort_idx = np.argsort(-y_score)
    sorted_true = y_true[sort_idx]

    cum_tp = np.cumsum(sorted_true)
    cum_fp = np.cumsum(1 - sorted_true)
    recalls = cum_tp / pos_count
    precisions = cum_tp / (cum_tp + cum_fp)

    # Trả trước thu hồi=0, độ chính xác=1
    recalls_with_zero = np.insert(recalls, 0, 0.0)
    precisions_with_one = np.insert(precisions, 0, 1.0)
    
    # Bước tích phân
    ap = float(np.sum((recalls_with_zero[1:] - recalls_with_zero[:-1]) * precisions_with_one[1:]))
    return max(0.0, min(1.0, ap))

def compute_trapezoidal_pr_auc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Tính diện tích hình thang theo đường cong thu hồi chính xác.
    """
    y_true = np.asarray(y_true, dtype=np.int32)
    y_score = np.asarray(y_score, dtype=np.float64)

    pos_count = int(np.sum(y_true))
    if pos_count == 0 or len(y_true) == 0:
        return 0.0

    sort_idx = np.argsort(-y_score)
    sorted_true = y_true[sort_idx]

    cum_tp = np.cumsum(sorted_true)
    cum_fp = np.cumsum(1 - sorted_true)
    recalls = cum_tp / pos_count
    precisions = cum_tp / (cum_tp + cum_fp)

    recalls_padded = np.insert(recalls, 0, 0.0)
    precisions_padded = np.insert(precisions, 0, precisions[0] if len(precisions) > 0 else 1.0)

    # Quy tắc hình thang: (r_i - r_{i-1}) * (p_i + p_{i-1}) / 2
    dr = recalls_padded[1:] - recalls_padded[:-1]
    avg_p = 0.5 * (precisions_padded[1:] + precisions_padded[:-1])
    pr_auc = float(np.sum(dr * avg_p))
    return max(0.0, min(1.0, pr_auc))

# Bí danh cho khả năng tương thích ngược
compute_pr_auc = compute_average_precision

def compute_f1_score(y_true: np.ndarray, y_score: np.ndarray, threshold: float = 0.5) -> float:
    y_true = np.asarray(y_true, dtype=np.int32)
    y_pred = (np.asarray(y_score, dtype=np.float64) >= threshold).astype(np.int32)

    tp = int(np.sum((y_pred == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    fn = int(np.sum((y_pred == 0) & (y_true == 1)))

    if tp == 0:
        return 0.0
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    return float(2.0 * (prec * rec) / (prec + rec))

def paired_cluster_bootstrap_recompute(
    cluster_ids: np.ndarray,
    y_true: np.ndarray,
    y_pred_proposed: np.ndarray,
    y_pred_baseline: np.ndarray,
    metric_fn: Callable[[np.ndarray, np.ndarray], float] = compute_average_precision,
    b_resamples: int = 2000,
    random_seed: int = 10007,
    alpha: float = 0.05,
    correction_family: str = "none"
) -> Dict[str, Any]:
    """
    Thực thi Bootstrap theo cụm được ghép nối bằng cách lấy mẫu lại các cụm và tính toán lại toàn bộ số liệu chính xác.
    """
    if b_resamples != 2000:
        raise ValueError(f"Confirmatory protocol requires exact B=2000, got B={b_resamples}")
    if random_seed != 10007:
        raise ValueError(f"Confirmatory protocol requires exact seed=10007, got seed={random_seed}")

    cluster_ids = np.asarray(cluster_ids)
    y_true = np.asarray(y_true)
    y_prop = np.asarray(y_pred_proposed)
    y_base = np.asarray(y_pred_baseline)

    n_obs = len(y_true)
    if len(cluster_ids) != n_obs or len(y_prop) != n_obs or len(y_base) != n_obs:
        raise ValueError("All input arrays must have identical length")

    unique_clusters = np.unique(cluster_ids)
    n_clusters = len(unique_clusters)

    if n_clusters < 30:
        raise ValueError(
            f"Cluster count ({n_clusters}) is too low for Paired Cluster Bootstrap. "
            "Evaluation clusters must represent independent sessions/blocks, not seed arrays."
        )

    cluster_to_indices = {}
    for idx, c_id in enumerate(cluster_ids):
        cluster_to_indices.setdefault(c_id, []).append(idx)

    obs_metric_prop = metric_fn(y_true, y_prop)
    obs_metric_base = metric_fn(y_true, y_base)
    obs_delta = float(obs_metric_prop - obs_metric_base)

    rng = np.random.default_rng(random_seed)
    boot_cluster_choices = rng.choice(unique_clusters, size=(b_resamples, n_clusters), replace=True)

    delta_bootstrap = []

    for b in range(b_resamples):
        sampled_c_ids = boot_cluster_choices[b]
        sampled_indices = []
        for c_id in sampled_c_ids:
            sampled_indices.extend(cluster_to_indices[c_id])
        
        sampled_idx_arr = np.array(sampled_indices, dtype=np.int64)

        b_y_true = y_true[sampled_idx_arr]
        b_y_prop = y_prop[sampled_idx_arr]
        b_y_base = y_base[sampled_idx_arr]

        m_prop_b = metric_fn(b_y_true, b_y_prop)
        m_base_b = metric_fn(b_y_true, b_y_base)
        delta_b = m_prop_b - m_base_b
        delta_bootstrap.append(delta_b)

    delta_boot_arr = np.array(delta_bootstrap, dtype=np.float64)

    ci_lower = float(np.percentile(delta_boot_arr, 2.5))
    ci_upper = float(np.percentile(delta_boot_arr, 97.5))

    centered_deltas = delta_boot_arr - obs_delta
    p_val = float(np.mean(np.abs(centered_deltas) >= np.abs(obs_delta)))

    adjusted_alpha = alpha
    if correction_family == "bonferroni_h1":
        adjusted_alpha = alpha / 4.0
    elif correction_family == "bonferroni_h2":
        adjusted_alpha = alpha / 3.0

    # Ngữ nghĩa quyết định: SUPPORTED, INCONCLUSIVE, FALSIFIED
    is_supported = bool(p_val <= adjusted_alpha and ci_lower > 0.0)
    is_falsified = bool(obs_delta < 0.0 and p_val <= adjusted_alpha and ci_upper < 0.0)
    
    if is_supported:
        decision_verdict = "SUPPORTED"
    elif is_falsified:
        decision_verdict = "FALSIFIED"
    else:
        decision_verdict = "INCONCLUSIVE"

    return {
        "n_clusters": n_clusters,
        "n_observations": n_obs,
        "b_resamples": b_resamples,
        "seed": random_seed,
        "observed_metric_proposed": float(obs_metric_prop),
        "observed_metric_baseline": float(obs_metric_base),
        "observed_delta": obs_delta,
        "ci_95": [ci_lower, ci_upper],
        "p_value": p_val,
        "alpha_nominal": alpha,
        "alpha_adjusted": adjusted_alpha,
        "correction_family": correction_family,
        "verdict": decision_verdict,
        "is_significant": is_supported
    }

def apply_benjamini_hochberg_fdr(p_values: Dict[str, float], q_threshold: float = 0.05) -> Dict[str, Any]:
    m = len(p_values)
    if m == 0:
        return {}

    sorted_p = sorted(p_values.items(), key=lambda x: x[1])
    decisions = {}
    max_k = -1

    for rank, (name, p_val) in enumerate(sorted_p, start=1):
        crit_val = (rank / m) * q_threshold
        if p_val <= crit_val:
            max_k = rank

    for rank, (name, p_val) in enumerate(sorted_p, start=1):
        crit_val = (rank / m) * q_threshold
        is_sig = (rank <= max_k)
        decisions[name] = {
            "rank": rank,
            "raw_p": p_val,
            "bh_critical_value": crit_val,
            "rejected_null": is_sig,
            "verdict": "SUPPORTED" if is_sig else "INCONCLUSIVE"
        }

    return decisions

def apply_holm_bonferroni_stepdown(p_values: Dict[str, float], alpha: float = 0.05) -> Dict[str, Any]:
    m = len(p_values)
    if m == 0:
        return {}

    sorted_p = sorted(p_values.items(), key=lambda x: x[1])
    decisions = {}
    stopped = False

    for rank, (name, p_val) in enumerate(sorted_p, start=1):
        crit_alpha = alpha / (m - rank + 1)
        if not stopped and p_val <= crit_alpha:
            decisions[name] = {"rank": rank, "raw_p": p_val, "critical_alpha": crit_alpha, "rejected_null": True, "verdict": "SUPPORTED"}
        else:
            stopped = True
            decisions[name] = {"rank": rank, "raw_p": p_val, "critical_alpha": crit_alpha, "rejected_null": False, "verdict": "INCONCLUSIVE"}

    return decisions
