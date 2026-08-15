"""
Artifact Invalidation & Recomputation Cascader (Prompt 6 Section 88)
"""

from typing import Dict, List, Set, Tuple
from research_agent.verification.reproducibility.lineage_dag import ScientificLineageDAG


class InvalidationManager:
    """
    Manages retraction, invalidation, and cascading marks across the scientific graph.
    When a bug or contaminated data is detected, traces and invalidates all dependent outcomes.
    """

    def __init__(self, dag: ScientificLineageDAG):
        self.dag = dag
        self._invalidated_entities: Dict[str, str] = {}  # entity_id -> reason

    def invalidate_entity(self, entity_id: str, reason: str) -> Set[str]:
        """
        Invalidates entity_id and cascades invalidation to all downstream dependents.
        Returns the set of all affected entity IDs.
        """
        self._invalidated_entities[entity_id] = reason
        dependents = self.dag.get_downstream_dependents(entity_id)

        for dep in dependents:
            self._invalidated_entities[dep] = f"Cascaded invalidation from parent {entity_id}: {reason}"

        return {entity_id}.union(dependents)

    def is_invalidated(self, entity_id: str) -> Tuple[bool, str]:
        """Checks if an entity is invalidated, returning (is_invalid, reason)."""
        if entity_id in self._invalidated_entities:
            return True, self._invalidated_entities[entity_id]
        return False, ""

    def list_invalidated_entities(self) -> Dict[str, str]:
        return dict(self._invalidated_entities)
