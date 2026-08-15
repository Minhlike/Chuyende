"""
Research Project Schema
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from research_agent.core.identifiers import EntityPrefix, format_stable_id


class ResearchProject(BaseModel):
    """Canonical Root Research Project Model."""
    project_id: str = Field(default_factory=lambda: format_stable_id(EntityPrefix.PROJECT, 1))
    title: str = "Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công"
    central_object: str = "feature representation z"
    description: str = "Research Engineering System for log representation, evaluation, and provable claims."
    authors: List[str] = Field(default_factory=lambda: ["Research Engineering Team"])
    constitution_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
