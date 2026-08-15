"""
Roadmap Ingestion Interface and Specification Contract (Section 21, Prompt 2 Target)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from research_agent.schemas.roadmap import (
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
)
from research_agent.core.hash_utils import compute_string_sha256
from research_agent.core.exceptions import InvariantViolationError
from research_agent.storage.repository import ResearchRepository


class RoadmapIngestionService:
    """Ingests and validates formal 3-chapter Research Roadmap specifications without text mutation (RC-15)."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def ingest_roadmap_dict(self, data: Dict[str, Any], raw_text: Optional[str] = None) -> ResearchRoadmap:
        """Parse, validate, hash, and persist a Research Roadmap specification."""
        if not data.get("title"):
            raise InvariantViolationError("Roadmap specification must have a non-empty title.")
        if not data.get("nodes"):
            raise InvariantViolationError("Roadmap specification must contain hierarchical nodes.")

        # Compute deterministic checksum
        sha256 = compute_string_sha256(raw_text or json.dumps(data, sort_keys=True))

        roadmap = ResearchRoadmap(
            roadmap_id=data.get("roadmap_id") or "ROD-000001",
            version=data.get("version", "1.0.0"),
            title=data["title"],
            summary=data.get("summary", ""),
            sha256_hash=sha256,
            nodes=[ResearchNode(**n) for n in data["nodes"]],
            questions=[ResearchQuestion(**q) for q in data.get("questions", [])],
            hypotheses=[Hypothesis(**h) for h in data.get("hypotheses", [])],
        )

        # Store in relational database
        with self.repo.db.session() as conn:
            conn.execute(
                """
                INSERT INTO roadmaps (roadmap_id, version, title, summary, sha256_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(roadmap_id) DO UPDATE SET
                    version=excluded.version,
                    title=excluded.title,
                    summary=excluded.summary,
                    sha256_hash=excluded.sha256_hash,
                    updated_at=excluded.updated_at
                """,
                (
                    roadmap.roadmap_id,
                    roadmap.version,
                    roadmap.title,
                    roadmap.summary,
                    roadmap.sha256_hash,
                    roadmap.created_at.isoformat(),
                    roadmap.updated_at.isoformat(),
                )
            )

            # Insert nodes
            for node in roadmap.nodes:
                conn.execute(
                    """
                    INSERT INTO roadmap_nodes (node_id, roadmap_id, parent_node_id, level, order_index, code, title, description, expected_outputs_json, rq_ids_json, hyp_ids_json, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        parent_node_id=excluded.parent_node_id,
                        level=excluded.level,
                        order_index=excluded.order_index,
                        code=excluded.code,
                        title=excluded.title,
                        description=excluded.description,
                        expected_outputs_json=excluded.expected_outputs_json,
                        rq_ids_json=excluded.rq_ids_json,
                        hyp_ids_json=excluded.hyp_ids_json,
                        metadata_json=excluded.metadata_json
                    """,
                    (
                        node.node_id,
                        roadmap.roadmap_id,
                        node.parent_node_id,
                        node.level,
                        node.order_index,
                        node.code,
                        node.title,
                        node.description,
                        json.dumps(node.expected_outputs),
                        json.dumps(node.rq_ids),
                        json.dumps(node.hyp_ids),
                        json.dumps(node.metadata),
                    )
                )

            # Insert RQs
            for rq in roadmap.questions:
                conn.execute(
                    """
                    INSERT INTO research_questions (rq_id, code, title, description, target_aspect, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(rq_id) DO UPDATE SET
                        code=excluded.code,
                        title=excluded.title,
                        description=excluded.description,
                        target_aspect=excluded.target_aspect
                    """,
                    (rq.rq_id, rq.code, rq.title, rq.description, rq.target_representation_aspect, rq.created_at.isoformat())
                )

            # Insert Hypotheses
            for hyp in roadmap.hypotheses:
                conn.execute(
                    """
                    INSERT INTO hypotheses (hyp_id, code, rq_id, statement, falsification_criteria, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(hyp_id) DO UPDATE SET
                        code=excluded.code,
                        rq_id=excluded.rq_id,
                        statement=excluded.statement,
                        falsification_criteria=excluded.falsification_criteria
                    """,
                    (hyp.hyp_id, hyp.code, hyp.rq_id, hyp.statement, hyp.falsification_criteria, hyp.created_at.isoformat())
                )

        return roadmap
