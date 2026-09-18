"""
Á hậu tái tạo khoa học nhiều tầng (Nhắc 6 phần 80..82)
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from research_agent.core.enums import ReproducibilityLevel


class ReproductionRunner:
    """
    Thực hiện quy trình sao chép trên 5 tầng tiêu chuẩn:
    - Cấp độ 1: Tính toàn vẹn băm của các tạo phẩm hiện có.
    - Cấp độ 2: Tính toán lại số liệu từ các tệp dự đoán đã lưu.
    - Cấp độ 3: Phân tích thống kê & tái tạo bảng/hình từ nhật ký số liệu.
    - Cấp độ 4: Chạy lại suy luận mô hình trên test Split với checkpoint bị khóa.
    - Cấp độ 5: Đào tạo lại và đánh giá từ đầu đến cuối từ nhật ký thô.
    """

    def verify_level_1_integrity(
        self,
        artifact_path: Path | str,
        expected_sha256: str,
    ) -> Tuple[bool, str]:
        """Cấp độ 1: Kiểm tra hàm băm mật mã trên tạo phẩm tệp."""
        p = Path(artifact_path)
        if not p.exists():
            return False, f"Artifact not found: {artifact_path}"

        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        actual = hasher.hexdigest()

        if actual.lower() == expected_sha256.lower():
            return True, f"LEVEL 1 PASS: SHA-256 matches {actual}"
        return False, f"LEVEL 1 FAIL: Expected {expected_sha256}, got {actual}"

    def verify_level_2_metrics(
        self,
        recomputed_metrics: Dict[str, float],
        original_metrics: Dict[str, float],
        tolerance: float = 1e-5,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Cấp độ 2: Kiểm tra tính bằng số giữa số liệu gốc và số liệu được tính toán lại."""
        divergences = {}
        passed = True

        for k, orig_v in original_metrics.items():
            if k not in recomputed_metrics:
                divergences[k] = {"error": "Missing from recomputation", "original": orig_v}
                passed = False
                continue

            recomp_v = recomputed_metrics[k]
            diff = abs(orig_v - recomp_v)
            if diff > tolerance:
                divergences[k] = {
                    "original": orig_v,
                    "recomputed": recomp_v,
                    "diff": diff,
                    "tolerance": tolerance,
                }
                passed = False

        return passed, {
            "level": ReproducibilityLevel.LEVEL_2_METRIC.value,
            "passed": passed,
            "divergences": divergences,
            "metrics_evaluated": len(original_metrics),
        }
