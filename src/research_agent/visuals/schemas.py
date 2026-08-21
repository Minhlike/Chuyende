"""
Schemas and Data Contracts for Microsoft Word 2016 Scientific Visuals Engine
(Diagrams, Data Figures, Statistical Charts, Native Tables, Captions, Cross-References & Visual Registry)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field


class VisualType(str, Enum):
    CONCEPTUAL_DIAGRAM = "CONCEPTUAL_DIAGRAM"
    DATA_FIGURE = "DATA_FIGURE"
    STATISTICAL_CHART = "STATISTICAL_CHART"
    NATIVE_TABLE = "NATIVE_TABLE"


class CreationMethod(str, Enum):
    WORD_NATIVE_SHAPES = "WORD_NATIVE_SHAPES"
    WORD_DRAWING_CANVAS = "WORD_DRAWING_CANVAS"
    MATPLOTLIB_IMAGE = "MATPLOTLIB_IMAGE"
    WORD_NATIVE_TABLE = "WORD_NATIVE_TABLE"


class VisualNecessityReason(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    PIPELINE = "PIPELINE"
    TAXONOMY = "TAXONOMY"
    CONCEPT_RELATIONSHIPS = "CONCEPT_RELATIONSHIPS"
    QUANTITATIVE_COMPARISON = "QUANTITATIVE_COMPARISON"


class VisualNecessityEvaluation(BaseModel):
    """Evaluation result for Visual Necessity Gate."""
    is_necessary: bool
    primary_reason: Optional[VisualNecessityReason] = None
    clarity_statement: str = Field(description="Clear explanation of the concept/data this visual conveys.")
    alternative_prose_deficiency: str = Field(description="Why prose alone is insufficient.")
    rejection_reason: Optional[str] = None


class ShapeNodeSpec(BaseModel):
    """Specification for a single shape in a Word diagram."""
    shape_id: str
    shape_type: str = Field(default="ROUNDED_RECTANGLE", description="RECTANGLE, ROUNDED_RECTANGLE, OVAL, DIAMOND, PROCESS_BOX")
    label: str
    sub_label: Optional[str] = None
    left_pt: float
    top_pt: float
    width_pt: float
    height_pt: float
    font_size_pt: float = 11.0
    is_bold: bool = False
    fill_color_rgb: int = 0xFFFFFF  # White
    line_color_rgb: int = 0x000000  # Black
    line_weight_pt: float = 1.0


class ConnectorSpec(BaseModel):
    """Specification for a directional connector arrow between shapes."""
    connector_id: str
    source_shape_id: str
    target_shape_id: str
    connector_type: str = Field(default="ELBOW", description="STRAIGHT, ELBOW, CURVED")
    start_connection_site: int = 3  # Right side usually
    end_connection_site: int = 1    # Left side usually
    arrow_head: bool = True
    label: Optional[str] = None
    line_color_rgb: int = 0x000000
    line_weight_pt: float = 1.0
    dash_style: str = "SOLID"  # SOLID, DASHED


class DiagramSpecification(BaseModel):
    """Complete specification for a Word Native Diagram."""
    diagram_id: str = Field(description="FIG-000001 or similar")
    title: str
    caption: str
    use_canvas: bool = True
    canvas_width_pt: float = 460.0   # ~16.2 cm (fits within page margins)
    canvas_height_pt: float = 220.0
    nodes: List[ShapeNodeSpec] = Field(default_factory=list)
    connectors: List[ConnectorSpec] = Field(default_factory=list)
    group_shapes: bool = True
    bookmark_name: str = ""
    chapter_num: Optional[int] = 1


class VisualRecord(BaseModel):
    """Canonical registry entry for a scientific visual (FIG-ID / TBL-ID)."""
    visual_id: str = Field(description="Stable ID: FIG-000001, TBL-000001")
    node_code: str = Field(description="Associated Roadmap ResearchNode code, e.g. '1.1.1'")
    purpose: str = Field(description="Methodological purpose of the visual")
    visual_type: VisualType
    creation_method: CreationMethod
    caption: str
    source_provenance: str = Field(description="Data provenance / source locator / algorithm script")
    script_path: Optional[str] = None
    output_file_path: Optional[str] = None
    companion_data_path: Optional[str] = None
    output_sha256: str = Field(default="")
    bookmark_name: str = Field(description="Word native bookmark for cross-referencing")
    seq_number: int = Field(default=1)
    chapter_number: Optional[int] = Field(default=1)
    is_verified: bool = Field(default=True)
    necessity_evaluation: Optional[VisualNecessityEvaluation] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
