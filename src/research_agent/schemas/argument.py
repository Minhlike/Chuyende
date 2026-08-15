"""
Argument Graph Schemas (Section 11, Section 8)
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import ArgumentRelationType


class ArgumentNode(BaseModel):
    """Node in the Formal Argument Graph."""
    node_id: str = Field(description="Stable ID: ARG-000001")
    claim_id: str = Field(description="Associated Claim ID: CLM-000001")
    role: str = Field(default="PREMISE", description="PREMISE, INFERENCE, CONCLUSION, COUNTERARGUMENT, REBUTTAL")
    summary: str = Field(min_length=3)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArgumentEdge(BaseModel):
    """Directed Logical Edge in Argument Graph."""
    edge_id: str = Field(description="Stable ID: ARE-000001")
    from_node_id: str = Field(description="Origin Argument Node ID")
    to_node_id: str = Field(description="Target Argument Node ID")
    relation_type: ArgumentRelationType = Field(description="Canonical relation type (Section 11)")
    weight: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    rationale: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
