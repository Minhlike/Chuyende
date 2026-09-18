# -*- coding: utf-8 -*-
"""
Hợp đồng thử nghiệm Canonical H1: Độ chuẩn xác ngữ nghĩa (semantic fidelity) của tham số
Đánh giá xem liệu biểu diễn tham số động nhận biết bảo mật có bảo toàn thông tin lẫn nhau hay không
I(z; Y_sec) so với trừu tượng hóa chỉ dựa trên mẫu (template-only abstraction) trong kiến trúc, phân tách, thăm dò và ngân sách giống hệt nhau.
"""

from typing import Dict, Any, Optional
import numpy as np

def evaluate_h1_parameter_fidelity_contract(
    cluster_ids: np.ndarray,
    y_true: np.ndarray,
    parameter_repr_scores: np.ndarray,
    template_only_scores: np.ndarray,
    b_resamples: int = 2000,
    seed: int = 10007
) -> Dict[str, Any]:
    """
    Thực hiện kiểm tra giả thuyết H1 đã đăng ký trước bằng cách sử dụng Độ chính xác trung bình (AP).
    """
    from research_agent.experiments.protocols.paired_cluster_bootstrap import (
        paired_cluster_bootstrap_recompute,
        compute_average_precision
    )
    
    bootstrap_result = paired_cluster_bootstrap_recompute(
        cluster_ids=cluster_ids,
        y_true=y_true,
        y_pred_proposed=parameter_repr_scores,
        y_pred_baseline=template_only_scores,
        metric_fn=compute_average_precision,
        b_resamples=b_resamples,
        random_seed=seed,
        alpha=0.05,
        correction_family="bonferroni_h1"
    )

    verdict = bootstrap_result["verdict"]

    return {
        "hypothesis_id": "H1_Parameter_Semantic_Fidelity",
        "description": "Security-aware parameter representation vs Template-only abstraction",
        "primary_metric": "Average Precision (AP) Difference over Clusters",
        "bootstrap_results": bootstrap_result,
        "falsification_status": "FALSIFIED" if verdict == "FALSIFIED" else ("NOT_FALSIFIED" if verdict == "SUPPORTED" else "INCONCLUSIVE"),
        "verdict": verdict
    }
