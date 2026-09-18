"""
Khung cơ bản cho các kỹ năng nghiên cứu quy trình (Nhắc 5 phần 75..92)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Siêu dữ liệu mô tả kỹ năng nghiên cứu quy trình."""
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
    """Kết quả thực hiện của một kỹ năng nghiên cứu."""
    skill_id: str
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseResearchSkill(ABC):
    """Lớp cơ sở trừu tượng cho tất cả các kỹ năng nghiên cứu kinh điển."""

    def __init__(self, metadata: SkillMetadata):
        self.metadata = metadata

    @abstractmethod
    def execute(self, payload: Dict[str, Any], engine: Any) -> SkillResult:
        """Thực thi kỹ năng dựa trên tải trọng được cung cấp bằng ScientificReasoningEngine."""
        pass
