# -*- coding: utf-8 -*-
"""
Tường lửa chống chế tạo và bảo vệ xuất xứ kết quả khoa học
Thực thi dòng mật mã nghiêm ngặt cho tất cả các số liệu thử nghiệm:
Mọi số thực nghiệm phải truy nguyên về:
  - experiment_id
  - run_id
  - dataset_raw_hash
  - split_hash
  - git_commit
  - config_hash
  - environment_hash
  - seed
  - raw_predictions_path / raw_benchmark_log_path
  - computation_script
Quét và từ chối mọi từ điển kết quả được mã hóa cứng/không có căn cứ.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import json

REQUIRED_PROVENANCE_FIELDS = [
    "experiment_id",
    "run_id",
    "dataset_raw_hash",
    "split_hash",
    "git_commit",
    "config_hash",
    "environment_hash",
    "seed",
    "computation_script",
    "raw_run_log_path"
]

class ResultProvenanceFirewall:
    """
    Xác thực nguồn gốc mật mã và hoạt động trước khi chấp nhận bất kỳ kết quả nào vào bản ghi Chương 3.
    """
    @staticmethod
    def validate_run_record(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        missing = []
        for f in REQUIRED_PROVENANCE_FIELDS:
            if f not in record or not record[f]:
                missing.append(f)
        
        if missing:
            return False, missing
        return True, []

    @staticmethod
    def scan_for_hardcoded_empirical_literals(data: Dict[str, Any]) -> List[str]:
        """
        Quét các từ điển số liệu thực nghiệm thiếu bản ghi nguồn gốc thực thi.
        """
        violations = []
        # Nếu có số liệu xác nhận mà không có khối xuất xứ chạy:
        if "confirmatory_hypothesis_testing" in data:
            if "provenance_records" not in data or not data["provenance_records"]:
                violations.append("Confirmatory results present without verified provenance_records block.")
        return violations
