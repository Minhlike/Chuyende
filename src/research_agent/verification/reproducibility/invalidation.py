"""
Cascader vô hiệu hóa và tính toán lại artifact (Nhắc 6 Mục 88)
"""

from typing import Dict, List, Set, Tuple
from research_agent.verification.reproducibility.lineage_dag import ScientificLineageDAG


class InvalidationManager:
    """
    Quản lý việc rút lại, vô hiệu hóa và đánh dấu xếp tầng trên biểu đồ khoa học.
    Khi phát hiện lỗi hoặc dữ liệu bị ô nhiễm, hãy theo dõi và vô hiệu hóa tất cả các kết quả phụ thuộc.
    """

    def __init__(self, dag: ScientificLineageDAG):
        self.dag = dag
        self._invalidated_entities: Dict[str, str] = {}  # entity_id -> lý do

    def invalidate_entity(self, entity_id: str, reason: str) -> Set[str]:
        """
        Vô hiệu hóa entity_id và vô hiệu hóa tầng đối với tất cả những người phụ thuộc ở hạ nguồn.
        Trả về tập hợp tất cả các ID thực thể bị ảnh hưởng.
        """
        self._invalidated_entities[entity_id] = reason
        dependents = self.dag.get_downstream_dependents(entity_id)

        for dep in dependents:
            self._invalidated_entities[dep] = f"Cascaded invalidation from parent {entity_id}: {reason}"

        return {entity_id}.union(dependents)

    def is_invalidated(self, entity_id: str) -> Tuple[bool, str]:
        """Kiểm tra xem một thực thể có bị vô hiệu hay không, trả về (is_invalid, lý do)."""
        if entity_id in self._invalidated_entities:
            return True, self._invalidated_entities[entity_id]
        return False, ""

    def list_invalidated_entities(self) -> Dict[str, str]:
        return dict(self._invalidated_entities)
