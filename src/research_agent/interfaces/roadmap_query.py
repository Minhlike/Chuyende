"""
Roadmap Query API and Research Specification Inspection Service (Section 24)
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
    """Provides high-level programmatic and CLI queries against the canonical Research Roadmap."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def get_roadmap(self) -> Optional[ResearchRoadmap]:
        """Retrieve full roadmap."""
        return self.repo.get_roadmap()

    def get_rq(self, code_or_id: str) -> Optional[ResearchQuestion]:
        """Query Research Question by code (e.g. 'RQ3') or ID (e.g. 'RQ-000003')."""
        return self.repo.get_research_question(code_or_id)

    def get_hypothesis(self, code_or_id: str) -> Optional[Hypothesis]:
        """Query Hypothesis by code (e.g. 'H2') or ID (e.g. 'HYP-000002')."""
        return self.repo.get_hypothesis(code_or_id)

    def get_node(self, code_or_id: str) -> Optional[ResearchNode]:
        """Query a roadmap node by canonical code (e.g. '1.3.1', '2.3.2') or node_id."""
        node = self.repo.get_roadmap_node_by_code(code_or_id)
        if not node:
            for n in self.repo.list_roadmap_nodes():
                if n.node_id == code_or_id:
                    return n
        return node

    def get_nodes_by_axis(self, axis_code: str) -> List[ResearchNode]:
        """Retrieve all roadmap nodes associated with a Research Axis (e.g. 'A1', 'A5')."""
        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if axis_code in n.research_axes or axis_code in n.code]

    def get_nodes_testing_hypothesis(self, hyp_code_or_id: str) -> List[ResearchNode]:
        """Find all roadmap nodes testing or evaluating a given hypothesis."""
        hyp = self.get_hypothesis(hyp_code_or_id)
        target_ids = {hyp_code_or_id}
        if hyp:
            target_ids.add(hyp.hyp_id)
            target_ids.add(hyp.code)

        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if any(h in target_ids for h in n.hyp_ids)]

    def get_traceability_for_rq(self, rq_code_or_id: str) -> Optional[TraceabilityEntry]:
        """Retrieve full gap -> mechanism -> evaluation traceability path for an RQ."""
        for tr in self.repo.get_traceability_matrix():
            if tr.rq_id == rq_code_or_id or tr.code == rq_code_or_id:
                return tr
        return None

    def get_controls_by_category(self, category: str) -> List[NegativeControl]:
        """Retrieve negative controls in a category (e.g. 'LEAKAGE', 'SHORTCUT', 'PRIVACY')."""
        cat_upper = category.upper()
        return [c for c in self.repo.list_negative_controls() if c.category.upper() == cat_upper]

    def get_privacy_evaluation_nodes(self) -> List[ResearchNode]:
        """Retrieve all sections requiring privacy or linkability evaluation."""
        all_nodes = self.repo.list_roadmap_nodes()
        return [n for n in all_nodes if "A5" in n.research_axes or "privacy" in n.title.lower()]

    def get_boundary_constraints(self, topic: Optional[str] = None) -> List[ResearchBoundary]:
        """Retrieve claim boundaries optionally filtered by topic."""
        boundaries = self.repo.list_research_boundaries()
        if not topic:
            return boundaries
        t_low = topic.lower()
        return [b for b in boundaries if t_low in b.title.lower() or t_low in b.statement.lower()]
