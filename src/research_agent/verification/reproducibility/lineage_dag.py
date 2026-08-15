"""
Scientific Lineage DAG & Traceability Graph (Prompt 6 Section 85)
"""

from typing import Dict, List, Set


class ScientificLineageDAG:
    """
    Tracks dependencies across the entire scientific lifecycle:
    DatasetVersion -> SplitManifest -> ExperimentRun -> Metric -> StatisticalResult -> Table/Figure -> NumericalClaim.
    """

    def __init__(self):
        self._forward_edges: Dict[str, Set[str]] = {}
        self._backward_edges: Dict[str, Set[str]] = {}

    def add_dependency(self, parent_id: str, child_id: str):
        """Records that child_id depends on parent_id."""
        if parent_id not in self._forward_edges:
            self._forward_edges[parent_id] = set()
        self._forward_edges[parent_id].add(child_id)

        if child_id not in self._backward_edges:
            self._backward_edges[child_id] = set()
        self._backward_edges[child_id].add(parent_id)

    def get_downstream_dependents(self, entity_id: str) -> Set[str]:
        """Returns all transitive downstream artifacts that depend on entity_id."""
        visited: Set[str] = set()
        queue = [entity_id]

        while queue:
            curr = queue.pop(0)
            for child in self._forward_edges.get(curr, set()):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)

        return visited

    def get_upstream_provenance(self, entity_id: str) -> Set[str]:
        """Returns all transitive upstream inputs that produced entity_id."""
        visited: Set[str] = set()
        queue = [entity_id]

        while queue:
            curr = queue.pop(0)
            for parent in self._backward_edges.get(curr, set()):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)

        return visited
