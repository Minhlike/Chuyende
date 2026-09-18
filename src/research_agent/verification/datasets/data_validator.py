"""
Trình xác thực chất lượng và tính toàn vẹn của tập dữ liệu (Lời nhắc 6 Phần 22)
"""

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd


class DataValidator:
    """
    Xác thực các tệp dữ liệu, lược đồ, phân tích cú pháp dấu thời gian và tính toàn vẹn của bản ghi.
    Không bao giờ âm thầm thay đổi hoặc tự động xóa bản ghi; tạo báo cáo chất lượng dữ liệu rõ ràng.
    """

    def calculate_file_sha256(self, file_path: Path | str) -> str:
        """Tính hàm băm SHA-256 của một tệp trên đĩa."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Dataset file '{file_path}' does not exist.")
        hasher = hashlib.sha256()
        with open(p, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def validate_file_hash(self, file_path: Path | str, expected_sha256: str) -> Tuple[bool, str]:
        """So sánh tệp thực tế SHA256 với hàm băm của tệp kê khai dự kiến."""
        actual_hash = self.calculate_file_sha256(file_path)
        if actual_hash.lower() == expected_sha256.lower():
            return True, f"SHA-256 matches: {actual_hash}"
        return False, f"HASH_MISMATCH: expected {expected_sha256}, got {actual_hash}"

    def validate_dataframe_schema(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
        timestamp_col: Optional[str] = None,
        label_col: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Xác thực lược đồ khung dữ liệu, cột bị thiếu, trùng lặp và độ chính xác của dấu thời gian."""
        issues: List[str] = []

        # Kiểm tra các cột bị thiếu
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            issues.append(f"Missing required columns: {missing}")

        # Kiểm tra trùng lặp
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append(f"Dataset contains {duplicate_count} duplicate rows ({duplicate_count / len(df):.2%}).")

        # Kiểm tra phân tích cú pháp dấu thời gian và độ tỉnh táo
        if timestamp_col and timestamp_col in df.columns:
            try:
                ts = pd.to_datetime(df[timestamp_col], errors="coerce")
                null_ts = ts.isna().sum()
                if null_ts > 0:
                    issues.append(f"{null_ts} rows have unparseable timestamps in column '{timestamp_col}'.")
                else:
                    min_ts = ts.min()
                    max_ts = ts.max()
                    if min_ts.year < 1990 or max_ts.year > 2035:
                        issues.append(f"Impossible timestamp range detected: [{min_ts}, {max_ts}].")
            except Exception as e:
                issues.append(f"Timestamp parsing failed for column '{timestamp_col}': {str(e)}")

        # Kiểm tra cột nhãn
        if label_col and label_col in df.columns:
            missing_labels = df[label_col].isna().sum()
            if missing_labels > 0:
                issues.append(f"{missing_labels} rows have missing ground truth labels in '{label_col}'.")

        return len(issues) == 0, issues
