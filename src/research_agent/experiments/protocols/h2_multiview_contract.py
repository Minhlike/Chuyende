# -*- coding: utf-8 -*-
"""
Hợp đồng thử nghiệm Canonical H2: Căn chỉnh xem chéo & không thu gọn
Đánh giá xem các biểu diễn nhiều chế độ xem có được căn chỉnh z_mv Chế độ xem đơn chiếm ưu thế Pareto hay không
baseline (Chỉ chuỗi, chỉ đồ thị) và phản ứng tổng hợp không được căn chỉnh mà không thu gọn biểu diễn.
Loại bỏ các baseline tiên tri ở cấp độ quan sát và thực hiện 3 phép so sánh Bonferroni riêng biệt.
"""

from typing import Dict, Any
import numpy as np

def evaluate_h2_multiview_alignment_contract(
    cluster_ids: np.ndarray,
    y_true: np.ndarray,
    aligned_mv_scores: np.ndarray,
    seq_only_scores: np.ndarray,
    graph_only_scores: np.ndarray,
    unaligned_mv_scores: np.ndarray,
    latent_variance: float,
    b_resamples: int = 2000,
    seed: int = 10007,
    margin_epsilon: float = 0.02
) -> Dict[str, Any]:
    """
    Thực hiện kiểm tra giả thuyết H2 đã đăng ký trước bằng cách sử dụng Độ chính xác trung bình (AP) trên 3 phép so sánh riêng biệt.
    """
    from research_agent.experiments.protocols.paired_cluster_bootstrap import (
        paired_cluster_bootstrap_recompute,
        compute_average_precision
    )
    
    # So sánh 1: Chế độ xem nhiều chế độ được căn chỉnh và chỉ theo trình tự
    boot_vs_seq = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=seq_only_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    # So sánh 2: Nhiều chế độ xem được căn chỉnh so với chỉ đồ thị
    boot_vs_graph = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=graph_only_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    # So sánh 3: Multi-View được căn chỉnh và Fusion không được căn chỉnh
    boot_vs_unaligned = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=aligned_mv_scores,
        y_pred_baseline=unaligned_mv_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h2"
    )

    variance_collapsed = bool(latent_variance < 0.01)

    # Tất cả các so sánh một lượt xem không được đánh bại căn chỉnh đáng kể
    # Căn chỉnh phải được hỗ trợ ít nhất là không được căn chỉnh và không tệ hơn các chế độ xem đơn lẻ
    is_falsified = (
        boot_vs_seq["verdict"] == "FALSIFIED" or
        boot_vs_graph["verdict"] == "FALSIFIED" or
        variance_collapsed
    )
    is_supported = (
        (boot_vs_seq["verdict"] == "SUPPORTED" or boot_vs_seq["observed_delta"] >= -margin_epsilon) and
        (boot_vs_graph["verdict"] == "SUPPORTED" or boot_vs_graph["observed_delta"] >= -margin_epsilon) and
        (boot_vs_unaligned["verdict"] == "SUPPORTED") and
        not variance_collapsed
    )

    if is_falsified:
        final_verdict = "FALSIFIED"
    elif is_supported:
        final_verdict = "SUPPORTED"
    else:
        final_verdict = "INCONCLUSIVE"

    return {
        "hypothesis_id": "H2_Multi_View_Alignment",
        "description": "Aligned Multi-View vs Sequence-Only, Graph-Only, and Unaligned Fusion",
        "latent_representation_variance": latent_variance,
        "variance_collapse_detected": variance_collapsed,
        "comparisons": {
            "vs_sequence_only": boot_vs_seq,
            "vs_graph_only": boot_vs_graph,
            "vs_unaligned_fusion": boot_vs_unaligned
        },
        "falsification_status": "FALSIFIED" if final_verdict == "FALSIFIED" else ("NOT_FALSIFIED" if final_verdict == "SUPPORTED" else "INCONCLUSIVE"),
        "verdict": final_verdict
    }
