"""
Equation Registry Schemas (Section 12, RC-08)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from research_agent.core.enums import (
    EquationType,
    IntellectualOwnership,
    VerificationStatus,
)
from research_agent.core.exceptions import ProvenanceError


class SymbolDefinition(BaseModel):
    """Canonical mathematical symbol definition with explicit scope (Section 12)."""
    symbol_id: str = Field(description="Stable ID: SYM-000001")
    symbol_latex: str = Field(description="LaTeX string, e.g. '\\mathbf{z}', '\\lambda'")
    name: str
    dimension: Optional[str] = Field(default=None, description="e.g. '\\mathbb{R}^d', '\\mathbb{N}'")
    domain: Optional[str] = Field(default=None, description="e.g. 'Continuous latent representation'")
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EquationDerivation(BaseModel):
    """Mathematical proof / derivation lineage."""
    parent_equation_ids: List[str] = Field(default_factory=list, description="IDs of prerequisite equations")
    derivation_steps: List[str] = Field(default_factory=list, description="Ordered derivation steps in LaTeX/text")
    assumptions_applied: List[str] = Field(default_factory=list)
    proof_notes: Optional[str] = None


class Equation(BaseModel):
    """Canonical Equation Entity (RC-08)."""
    equation_id: str = Field(description="Stable ID: EQ-000001")
    latex: str = Field(min_length=1, description="Raw LaTeX representation")
    normalized_representation: Optional[str] = None
    equation_type: EquationType = Field(description="SOURCE_EQUATION, DERIVED_EQUATION, PROPOSED_EQUATION")
    source_id: Optional[str] = Field(default=None, description="Required for SOURCE_EQUATION (RC-08)")
    source_locator: Optional[str] = Field(default=None, description="Page / Section in external source")
    ownership: IntellectualOwnership = Field(default=IntellectualOwnership.OURS)
    symbols: List[SymbolDefinition] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    derivation: Optional[EquationDerivation] = None
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_method: str = "MANUAL_CHECK"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_provenance_invariants(self) -> "Equation":
        # RC-08 / TEST 3 Invariant: SOURCE_EQUATION must have source_id
        if self.equation_type == EquationType.SOURCE_EQUATION:
            if not self.source_id or not self.source_id.strip():
                raise ProvenanceError(
                    rule_id="RC-08",
                    message=f"Equation '{self.equation_id}' of type SOURCE_EQUATION must specify a valid source_id."
                )

        if self.equation_type == EquationType.DERIVED_EQUATION and not self.derivation:
            raise ValueError(f"Equation '{self.equation_id}' of type DERIVED_EQUATION must have a derivation record.")

        return self
