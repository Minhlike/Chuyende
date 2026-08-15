"""
System Exception Hierarchy for Research Engineering System
"""


class ResearchSystemError(Exception):
    """Base exception for all research system operations."""
    pass


class ConstitutionViolationError(ResearchSystemError):
    """Raised when an action violates a fundamental Research Constitution invariant."""
    def __init__(self, rule_id: str, message: str):
        self.rule_id = rule_id
        super().__init__(f"[{rule_id}] Constitution Violation: {message}")


class InvariantViolationError(ResearchSystemError):
    """Raised when an internal data invariant or contract is breached."""
    pass


class SecurityPathViolationError(ResearchSystemError):
    """Raised when an I/O operation attempts to breach workspace boundaries."""
    pass


class EntityNotFoundError(ResearchSystemError):
    """Raised when a referenced entity ID does not exist."""
    pass


class DuplicateEntityError(ResearchSystemError):
    """Raised when an entity with existing ID or unique constraint is added."""
    pass


class EpistemicStateError(ResearchSystemError):
    """Raised on invalid epistemic status transitions."""
    pass


class ProvenanceError(ConstitutionViolationError):
    """Raised when provenance requirement (RC-02, RC-08, RC-09, RC-10) is violated."""
    def __init__(self, rule_id: str, message: str):
        super().__init__(rule_id=rule_id, message=message)
