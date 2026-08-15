"""
Argument Graph Interface (Section 11, Section 8)
"""

import json
from typing import List, Optional
from research_agent.schemas.argument import ArgumentNode, ArgumentEdge
from research_agent.core.enums import ArgumentRelationType
from research_agent.core.identifiers import EntityPrefix
from research_agent.core.exceptions import EntityNotFoundError
from research_agent.storage.repository import ResearchRepository


class ArgumentGraph:
    """Manages the formal argument graph connecting premises, inferences, and conclusions."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def add_node(self, claim_id: str, role: str = "PREMISE", summary: str = "") -> ArgumentNode:
        """Add an argument node associated with a canonical claim."""
        claim = self.repo.get_claim(claim_id)
        if not claim:
            raise EntityNotFoundError(f"Claim '{claim_id}' does not exist.")

        node_id = self.repo.next_id(EntityPrefix.ARGUMENT_NODE)
        node = ArgumentNode(
            node_id=node_id,
            claim_id=claim_id,
            role=role,
            summary=summary or claim.statement[:100],
        )
        with self.repo.db.session() as conn:
            conn.execute(
                """
                INSERT INTO argument_nodes (node_id, claim_id, role, summary, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (node.node_id, node.claim_id, node.role, node.summary, json.dumps(node.metadata), node.created_at.isoformat())
            )
        return node

    def add_edge(
        self,
        from_node_id: str,
        to_node_id: str,
        relation_type: ArgumentRelationType,
        weight: float = 1.0,
        rationale: Optional[str] = None,
    ) -> ArgumentEdge:
        """Add a directed typed edge between two argument nodes."""
        edge_id = self.repo.next_id(EntityPrefix.ARGUMENT_EDGE)
        edge = ArgumentEdge(
            edge_id=edge_id,
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relation_type=relation_type,
            weight=weight,
            rationale=rationale,
        )
        with self.repo.db.session() as conn:
            conn.execute(
                """
                INSERT INTO argument_edges (edge_id, from_node_id, to_node_id, relation_type, weight, rationale, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    edge.edge_id,
                    edge.from_node_id,
                    edge.to_node_id,
                    edge.relation_type.value,
                    edge.weight,
                    edge.rationale,
                    json.dumps(edge.metadata),
                    edge.created_at.isoformat(),
                )
            )
        return edge
