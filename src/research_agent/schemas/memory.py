"""
Research Memory Hierarchy Schemas (Section 7, Section 8, ADR-0004)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from research_agent.core.enums import MemoryTier
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class SkillRecord(BaseModel):
    """M5 Procedural Memory Skill / Protocol / Rubric."""
    skill_id: str = Field(description="Stable ID: SKL-000001")
    name: str = Field(min_length=3)
    category: str = Field(description="e.g. 'EVALUATION_PROTOCOL', 'FEATURE_EXTRACTION_RUBRIC'")
    protocol_markdown_rel_path: str = Field(description="Path within memory/procedural/")
    description: str
    checklist: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryRecord(BaseModel):
    """Canonical Persistent Research Memory Record (Tiers M0..M5)."""
    memory_id: str = Field(description="Stable ID: MEM-000001")
    tier: MemoryTier = Field(description="M0_WORKING, M1_SOURCE, M2_SEMANTIC, M3_EPISODIC, M4_ARGUMENT, M5_PROCEDURAL")
    topic: str = Field(min_length=2)
    content: str = Field(min_length=5)
    associated_entity_ids: List[str] = Field(default_factory=list, description="Linked CLM, EVD, EXP, SRC IDs")
    tags: List[str] = Field(default_factory=list)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
