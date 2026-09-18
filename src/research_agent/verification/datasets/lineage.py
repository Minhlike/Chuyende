"""
Biểu đồ nguồn gốc và dòng dữ liệu (Nhắc 6 Phần 27)
"""

from typing import Dict, List, Optional
from research_agent.schemas.verification import PreprocessingTransformation


class DatasetLineageTracker:
    """
    Xây dựng và truy vấn biểu đồ dòng từ các tập dữ liệu thô đến các đầu vào đặc trưng.
    Đảm bảo mọi tập dữ liệu dẫn xuất đều có một phép chuyển đổi rõ ràng, có thể lặp lại.
    """

    def __init__(self):
        self._transformations: Dict[str, PreprocessingTransformation] = {}

    def record_transformation(self, trf: PreprocessingTransformation):
        self._transformations[trf.transformation_id] = trf

    def get_ancestors(self, dataset_version_id: str) -> List[str]:
        """Theo dõi tất cả các phiên bản tập dữ liệu gốc dẫn đến dataset_version_id."""
        ancestors = []
        current = dataset_version_id
        while True:
            parent = None
            for trf in self._transformations.values():
                if trf.output_dataset_version_id == current:
                    parent = trf.input_dataset_version_id
                    break
            if parent and parent != current:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def get_lineage_trail(self, dataset_version_id: str) -> List[PreprocessingTransformation]:
        """Trả về danh sách các phép biến đổi có thứ tự được áp dụng để tạo ra dataset_version_id."""
        trail = []
        current = dataset_version_id
        while True:
            step = None
            for trf in self._transformations.values():
                if trf.output_dataset_version_id == current:
                    step = trf
                    break
            if step:
                trail.append(step)
                current = step.input_dataset_version_id
            else:
                break
        return list(reversed(trail))
