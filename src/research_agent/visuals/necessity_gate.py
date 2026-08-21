"""
Visual Necessity Gate (Rule 8)
Guarantees that no decorative fluff or gratuitous visuals are introduced into the scientific report.
"""

from typing import Optional
from research_agent.visuals.schemas import (
    VisualNecessityEvaluation,
    VisualNecessityReason,
    VisualType,
    CreationMethod,
)


class VisualNecessityGate:
    """
    Validates whether a proposed visual satisfies scientific necessity criteria before inclusion.
    """

    @staticmethod
    def evaluate(
        visual_id: str,
        visual_type: VisualType,
        purpose: str,
        clarity_statement: str,
        alternative_prose_deficiency: str,
        primary_reason: Optional[VisualNecessityReason] = None,
    ) -> VisualNecessityEvaluation:
        """
        Evaluates visual necessity.
        Requires non-empty purpose, explicit clarity statement, and concrete explanation
        of why text/prose alone cannot adequately convey the structure or quantitative data.
        """
        if not purpose or len(purpose.strip()) < 10:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement or "",
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Purpose is empty or too vague (< 10 chars).",
            )

        if not clarity_statement or len(clarity_statement.strip()) < 15:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement or "",
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Clarity statement is too brief; must explain the single clear idea conveyed.",
            )

        if not alternative_prose_deficiency or len(alternative_prose_deficiency.strip()) < 15:
            return VisualNecessityEvaluation(
                is_necessary=False,
                clarity_statement=clarity_statement,
                alternative_prose_deficiency=alternative_prose_deficiency or "",
                rejection_reason="Alternative prose deficiency statement required (< 15 chars). Must justify why prose is deficient.",
            )

        # Map type to default reason if not provided
        if not primary_reason:
            if visual_type == VisualType.CONCEPTUAL_DIAGRAM:
                primary_reason = VisualNecessityReason.ARCHITECTURE
            elif visual_type in (VisualType.DATA_FIGURE, VisualType.STATISTICAL_CHART):
                primary_reason = VisualNecessityReason.QUANTITATIVE_COMPARISON
            elif visual_type == VisualType.NATIVE_TABLE:
                primary_reason = VisualNecessityReason.QUANTITATIVE_COMPARISON

        return VisualNecessityEvaluation(
            is_necessary=True,
            primary_reason=primary_reason,
            clarity_statement=clarity_statement.strip(),
            alternative_prose_deficiency=alternative_prose_deficiency.strip(),
            rejection_reason=None,
        )
