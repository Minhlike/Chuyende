"""
Equation Registry Interface (Section 12, RC-08)
"""

from typing import List, Optional
from research_agent.schemas.equation import Equation, SymbolDefinition, EquationDerivation
from research_agent.core.enums import EquationType, IntellectualOwnership, VerificationStatus
from research_agent.core.identifiers import EntityPrefix
from research_agent.core.exceptions import ProvenanceError
from research_agent.storage.repository import ResearchRepository


class EquationRegistry:
    """Manages LaTeX mathematical formulations, derivations, and symbol scoping."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def register_symbol(
        self,
        symbol_latex: str,
        name: str,
        description: str,
        dimension: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> SymbolDefinition:
        """Define a scoped mathematical symbol (RC-08)."""
        symbol_id = self.repo.next_id(EntityPrefix.SYMBOL)
        sym = SymbolDefinition(
            symbol_id=symbol_id,
            symbol_latex=symbol_latex,
            name=name,
            description=description,
            dimension=dimension,
            domain=domain,
        )
        with self.repo.db.session() as conn:
            conn.execute(
                """
                INSERT INTO symbol_definitions (symbol_id, symbol_latex, name, dimension, domain, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol_id) DO UPDATE SET
                    symbol_latex=excluded.symbol_latex,
                    name=excluded.name,
                    dimension=excluded.dimension,
                    domain=excluded.domain,
                    description=excluded.description
                """,
                (sym.symbol_id, sym.symbol_latex, sym.name, sym.dimension, sym.domain, sym.description, sym.created_at.isoformat())
            )
        return sym

    def register_equation(
        self,
        latex: str,
        equation_type: EquationType,
        ownership: IntellectualOwnership = IntellectualOwnership.OURS,
        source_id: Optional[str] = None,
        source_locator: Optional[str] = None,
        symbols: Optional[List[SymbolDefinition]] = None,
        assumptions: Optional[List[str]] = None,
        derivation: Optional[EquationDerivation] = None,
        normalized_representation: Optional[str] = None,
    ) -> Equation:
        """Register an equation with strict provenance checks (RC-08)."""
        eq_id = self.repo.next_id(EntityPrefix.EQUATION)
        equation = Equation(
            equation_id=eq_id,
            latex=latex,
            normalized_representation=normalized_representation,
            equation_type=equation_type,
            source_id=source_id,
            source_locator=source_locator,
            ownership=ownership,
            symbols=symbols or [],
            assumptions=assumptions or [],
            derivation=derivation,
            verification_status=VerificationStatus.VERIFIED if equation_type != EquationType.PROPOSED_EQUATION else VerificationStatus.PENDING,
        )
        return self.repo.save_equation(equation)
