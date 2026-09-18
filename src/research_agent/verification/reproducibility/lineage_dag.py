"""
Dòng khoa học DAG & Biểu đồ truy xuất nguồn gốc (Nhắc 6 Phần 85)
"""

from typing import Dict, List, Set


class ScientificLineageDAG:
    """
    Theo dõi sự phụ thuộc trong toàn bộ vòng đời khoa học:
    DatasetVersion -> SplitManifest -> ExperimentRun -> Số liệu -> StatisticalResult -> Bảng/Hình -> NumericalClaim.
    """

    def __init__(self):
        self._forward_edges: Dict[str, Set[str]] = {}
        self._backward_edges: Dict[str, Set[str]] = {}

    def add_dependency(self, parent_id: str, child_id: str):
        """Ghi lại rằng child_id phụ thuộc vào parent_id."""
        if parent_id not in self._forward_edges:
            self._forward_edges[parent_id] = set()
        self._forward_edges[parent_id].add(child_id)

        if child_id not in self._backward_edges:
            self._backward_edges[child_id] = set()
        self._backward_edges[child_id].add(parent_id)

    def get_downstream_dependents(self, entity_id: str) -> Set[str]:
        """Trả về tất cả các artifact hạ nguồn (downstream) bắc cầu phụ thuộc vào entity_id."""
        visited: Set[str] = set()
        queue = [entity_id]

        while queue:
            curr = queue.pop(0)
            for child in self._forward_edges.get(curr, set()):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)

        return visited

    def get_upstream_provenance(self, entity_id: str) -> Set[str]:
        """Trả về tất cả các đầu vào thượng nguồn (upstream) bắc cầu đã tạo ra entity_id."""
        visited: Set[str] = set()
        queue = [entity_id]

        while queue:
            curr = queue.pop(0)
            for parent in self._backward_edges.get(curr, set()):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)

        return visited
