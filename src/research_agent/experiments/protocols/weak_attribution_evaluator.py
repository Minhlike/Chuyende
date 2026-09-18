# -*- coding: utf-8 -*-
"""
Công cụ đánh giá thuộc tính bằng chứng yếu (RQ4)
Đánh giá phân bổ Attention trong Học tập nhiều phiên bản (MIL attention attribution) mà không tạo nhãn sự kiện giả mạo.
Quy tắc:
  - Nghiêm cấm các nhãn heuristic tổng hợp (e.g., giả sử 3 sự kiện cuối cùng là bất thường).
  - Trên HDFS: Trả về rõ ràng NOT_EVALUABLE_ON_HDFS khi chỉ tồn tại các nhãn cấp khối thô.
  - Trên Provenance / DARPA: Yêu cầu đối sánh chính xác IOC / cấp độ sự kiện từ bản đồ nhãn chuẩn (verified ground truth map) đã được xác minh.
"""

from typing import Dict, Any, List, Optional, Set
import numpy as np

def evaluate_weak_attribution_accuracy(
    bag_attention_weights: List[np.ndarray],
    ground_truth_event_indices: List[Optional[Set[int]]],
    dataset_name: str
) -> Dict[str, Any]:
    """
    Chỉ đánh giá tỷ lệ trúng sự kiện nguyên nhân gốc Top-1, Top-3, Top-5 dựa trên nhãn chuẩn (verified ground truth) đã được xác minh.
    """
    if dataset_name.upper() == "HDFS":
        # HDFS chỉ cung cấp nhãn bất thường ở cấp độ khối, không cung cấp nhãn nguyên nhân gốc trên mỗi nhật ký
        has_real_event_annotations = any(gt is not None for gt in ground_truth_event_indices)
        if not has_real_event_annotations:
            return {
                "dataset": "HDFS",
                "evaluation_status": "NOT_EVALUABLE_ON_HDFS",
                "reason": "HDFS standard distribution provides only coarse block-level labels. Per-event attribution cannot be evaluated without independent event annotations.",
                "top1_hit_rate": None,
                "top3_hit_rate": None,
                "top5_hit_rate": None
            }

    top1_hits = 0
    top3_hits = 0
    top5_hits = 0
    total_evaluable = 0
    entropies = []

    for weights, gt_indices in zip(bag_attention_weights, ground_truth_event_indices):
        if gt_indices is None or len(gt_indices) == 0:
            continue

        total_evaluable += 1
        seq_len = len(weights)
        top_k_indices = np.argsort(weights)[::-1]

        # Top-1
        if top_k_indices[0] in gt_indices:
            top1_hits += 1
        # Top 3
        if any(idx in gt_indices for idx in top_k_indices[:min(3, seq_len)]):
            top3_hits += 1
        # Top 5
        if any(idx in gt_indices for idx in top_k_indices[:min(5, seq_len)]):
            top5_hits += 1

        # Entropy chú ý
        p = np.clip(weights, 1e-12, 1.0)
        p = p / np.sum(p)
        entropy = -float(np.sum(p * np.log(p)))
        entropies.append(entropy)

    if total_evaluable == 0:
        return {
            "dataset": dataset_name,
            "evaluation_status": "NO_EVALUABLE_INSTANCES",
            "total_evaluable": 0
        }

    return {
        "dataset": dataset_name,
        "evaluation_status": "COMPLETED",
        "total_evaluable_bags": total_evaluable,
        "top1_hit_rate": float(top1_hits / total_evaluable),
        "top3_hit_rate": float(top3_hits / total_evaluable),
        "top5_hit_rate": float(top5_hits / total_evaluable),
        "mean_attention_entropy": float(np.mean(entropies))
    }
