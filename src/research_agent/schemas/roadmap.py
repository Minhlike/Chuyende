"""
Research Roadmap, Nodes, Questions, and Hypotheses Schemas (Section 8, Section 21)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class ResearchQuestion(BaseModel):
    """Canonical Research Question (RQ1..RQ5)."""
    rq_id: str = Field(description="Stable ID: RQ-000001..RQ-000005")
    code: str = Field(description="Human label e.g., 'RQ1', 'RQ2'")
    title: str
    description: str
    target_representation_aspect: str = Field(description="Aspect of feature representation z addressed")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Hypothesis(BaseModel):
    """Canonical Scientific Hypothesis (H1..H5)."""
    hyp_id: str = Field(description="Stable ID: HYP-000001..HYP-000005")
    code: str = Field(description="Human label e.g., 'H1', 'H2'")
    rq_id: str = Field(description="Associated Research Question ID")
    statement: str
    falsification_criteria: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResearchNode(BaseModel):
    """Hierarchical node in Research Roadmap (Chapter / Section / Subsection / Topic)."""
    node_id: str = Field(description="Stable ID: NOD-000001")
    parent_node_id: Optional[str] = None
    level: int = Field(ge=1, le=5, description="1=Chapter, 2=Section, 3=Subsection, 4=Paragraph/Topic")
    order_index: int = Field(ge=0, description="Strict ordering within parent")
    code: str = Field(description="e.g. '1.1', '2.3.1'")
    title: str
    description: Optional[str] = None
    expected_outputs: List[str] = Field(default_factory=list)
    rq_ids: List[str] = Field(default_factory=list)
    hyp_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchRoadmap(BaseModel):
    """Canonical Versioned Research Specification Roadmap (Prompt 2 target)."""
    roadmap_id: str = Field(default_factory=lambda: format_stable_id(EntityPrefix.ROADMAP, 1))
    version: str = "1.0.0"
    title: str
    summary: str
    sha256_hash: Optional[str] = None
    nodes: List[ResearchNode] = Field(default_factory=list)
    questions: List[ResearchQuestion] = Field(default_factory=list)
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
