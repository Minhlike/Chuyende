"""
Stable Identifier Strategy and Sequence Generator (ADR-0002)
"""

import re
from enum import Enum
from typing import Optional


class EntityPrefix(str, Enum):
    """Canonical Entity ID Prefixes."""
    PROJECT = "PRJ-"
    ROADMAP = "ROD-"
    NODE = "NOD-"
    RESEARCH_QUESTION = "RQ-"
    HYPOTHESIS = "HYP-"
    SOURCE = "SRC-"
    SOURCE_VERSION = "SRV-"
    SOURCE_ARTIFACT = "SRA-"
    EVIDENCE = "EVD-"
    CLAIM = "CLM-"
    ARGUMENT_NODE = "ARG-"
    ARGUMENT_EDGE = "ARE-"
    EQUATION = "EQ-"
    SYMBOL = "SYM-"
    DATASET = "DATA-"
    DATASET_VERSION = "DSV-"
    EXPERIMENT = "EXP-"
    EXPERIMENT_RUN = "RUN-"
    TABLE = "TBL-"
    FIGURE = "FIG-"
    DECISION = "DEC-"
    CONTRADICTION = "CTR-"
    MEMORY = "MEM-"
    SKILL = "SKL-"
    VERIFICATION = "VRF-"


_ID_REGEX = re.compile(r"^([A-Z]+-)(\d{6})$")


def format_stable_id(prefix: EntityPrefix | str, sequence_number: int) -> str:
    """Format a prefix and sequence integer into a standard 6-digit stable ID."""
    p_str = prefix.value if isinstance(prefix, EntityPrefix) else prefix
    if not p_str.endswith("-"):
        p_str = f"{p_str}-"
    return f"{p_str}{sequence_number:06d}"


def validate_stable_id(entity_id: str, expected_prefix: Optional[EntityPrefix | str] = None) -> bool:
    """Validate that an ID conforms to the standard pattern and optionally expected prefix."""
    if not entity_id or not isinstance(entity_id, str):
        return False
    match = _ID_REGEX.match(entity_id)
    if not match:
        return False
    if expected_prefix:
        p_str = expected_prefix.value if isinstance(expected_prefix, EntityPrefix) else expected_prefix
        if not p_str.endswith("-"):
            p_str = f"{p_str}-"
        return match.group(1) == p_str
    return True
