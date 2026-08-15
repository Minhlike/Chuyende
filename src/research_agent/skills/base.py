"""
Base Framework for Procedural Research Skills (Prompt 5 Sections 75..92)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata describing a procedural research skill."""
    skill_id: str
    name: str
    version: str = "1.0.0"
    category: str
    description: str
    inputs: List[str]
    outputs: List[str]
    preconditions: List[str] = Field(default_factory=list)
    invariants: List[str] = Field(default_factory=list)


class SkillResult(BaseModel):
    """Execution outcome of a research skill."""
    skill_id: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseResearchSkill(ABC):
    """Abstract base class for all canonical research skills."""

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata

    @abstractmethod
    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        """Executes the skill against the provided payload using ScientificReasoningEngine."""
        pass
