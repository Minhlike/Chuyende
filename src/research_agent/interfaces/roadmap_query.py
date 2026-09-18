"""
Truy vấn lộ trình API và Dịch vụ kiểm tra thông số nghiên cứu (Phần 24)
"""

from typing import Any, Dict, List, Optional
from research_agent.schemas.roadmap import (
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
    ResearchAxis,
    NegativeControl,
    ResearchBoundary,
    DefensibilityQuestion,
    TraceabilityEntry,
)
from research_agent.storage.repository import ResearchRepository


class RoadmapQueryService:
    """Cung cấp các truy vấn có lập trình cấp cao và CLI dựa trên Lộ trình nghiên cứu chuẩn."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def get_roadmap(self) -> Optional[ResearchRoadmap]:
        """Truy xuất lộ trình đầy đủ."""
        return self.repo.get_roadmap()

    def get_rq(self, code_or_id: str) -> Optional[ResearchQuestion]:
        """Câu hỏi nghiên cứu truy vấn theo mã (e.g. 'RQ3') hoặc ID (e.g. 'RQ-000003')."""
        return self.repo.get_research_question(code_or_id)

    def get_hypothesis(self, code_or_id: str) -> Optional[Hypothesis]:
        """Giả thuyết truy vấn theo mã (e.g. 'H2') hoặc ID (e.g. 'HYP-000002')."""
        return self.repo.get_hypothesis(code_or_id)

    def get_node(self, code_or_id: str) -> Optional[ResearchNode]:
        """Truy vấn nút lộ trình theo mã chuẩn (e.g. '1.3.1', '2.3.2') hoặc node_id."""
        node = self.repo.get_roadmap_node_by_code(code_or_id)
        if not node:
            for n in self.repo.list_roadmap_nodes():
                if n.node_id == code_or_id:
                    return n
        return node

    def get_nodes_by_axis(self, axis_code: str) -> List[ResearchNode]:
        """Truy xuất tất cả các nút lộ trình được liên kết với Trục nghiên cứu (e.g. 'A1', 'A5')."""
        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if axis_code in n.research_axes or axis_code in n.code]

    def get_nodes_testing_hypothesis(self, hyp_code_or_id: str) -> List[ResearchNode]:
        """Tìm tất cả các nút lộ trình đang kiểm tra hoặc đánh giá một giả thuyết nhất định."""
        hyp = self.get_hypothesis(hyp_code_or_id)
        target_ids = {hyp_code_or_id}
        if hyp:
            target_ids.add(hyp.hyp_id)
            target_ids.add(hyp.code)

        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if any(h in target_ids for h in n.hyp_ids)]

    def get_traceability_for_rq(self, rq_code_or_id: str) -> Optional[TraceabilityEntry]:
        """Truy xuất toàn bộ khoảng trống -> cơ chế -> đường dẫn truy xuất nguồn gốc đánh giá cho RQ."""
        for tr in self.repo.get_traceability_matrix():
            if tr.rq_id == rq_code_or_id or tr.code == rq_code_or_id:
                return tr
        return None

    def get_controls_by_category(self, category: str) -> List[NegativeControl]:
        """Truy xuất các điều khiển phủ định trong một danh mục (e.g. 'LEAKAGE', 'SHORTCUT', 'PRIVACY')."""
        cat_upper = category.upper()
        return [c for c in self.repo.list_negative_controls() if c.category.upper() == cat_upper]

    def get_privacy_evaluation_nodes(self) -> List[ResearchNode]:
        """Truy xuất tất cả các phần yêu cầu đánh giá quyền riêng tư hoặc khả năng liên kết."""
        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if "A5" in n.research_axes or "privacy" in n.title.lower()]

    def get_boundary_constraints(self, topic: Optional[str] = None) -> List[ResearchBoundary]:
        """Truy xuất ranh giới yêu cầu tùy chọn được lọc theo chủ đề."""
        boundaries = self.repo.list_research_boundaries()
        if not topic:
            return boundaries
        t_low = topic.lower()
        return [b for b in boundaries if t_low in b.title.lower() or t_low in b.statement.lower()]
