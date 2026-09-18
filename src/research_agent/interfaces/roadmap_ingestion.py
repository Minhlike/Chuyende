"""
Hợp đồng đặc tả và giao diện nhập lộ trình (Phần 21, Mục tiêu nhắc 2)
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from research_agent.schemas.roadmap import (
    ResearchRoadmap,
    ResearchNode,
    ResearchQuestion,
    Hypothesis,
    ResearchAxis,
    RepresentationContract,
    NegativeControl,
    ResearchBoundary,
    DefensibilityQuestion,
    TraceabilityEntry,
)
from research_agent.core.hash_utils import compute_string_sha256
from research_agent.core.exceptions import InvariantViolationError
from research_agent.storage.repository import ResearchRepository


class RoadmapIngestionService:
    """Nhập và xác thực các thông số kỹ thuật của Lộ trình nghiên cứu chính thức gồm 3 chương mà không bị đột biến văn bản (RC-15)."""

    def __init__(self, repository: ResearchRepository):
        self.repo = repository

    def validate_roadmap_structure(self, roadmap: ResearchRoadmap, strict_canonical: bool = False) -> None:
        """Thực hiện xác thực toàn diện về cấu trúc và ngữ nghĩa (TEST-RM-01..16)."""
        if not roadmap.title or not roadmap.title.strip():
            raise InvariantViolationError("Roadmap must possess a non-empty canonical title.")

        if not roadmap.nodes:
            raise InvariantViolationError("Roadmap must contain hierarchical research nodes.")

        # 1. ID duy nhất & Mã Canonical
        node_ids: Set[str] = set()
        node_codes: Set[str] = set()
        for node in roadmap.nodes:
            if node.node_id in node_ids:
                raise InvariantViolationError(f"Duplicate node_id detected: '{node.node_id}' (TEST-RM-02).")
            if node.code in node_codes:
                raise InvariantViolationError(f"Duplicate canonical section code detected: '{node.code}' (TEST-RM-02).")
            node_ids.add(node.node_id)
            node_codes.add(node.code)

        # 2. Xác thực hệ thống phân cấp: cha mẹ phải tồn tại nếu được chỉ định
        for node in roadmap.nodes:
            if node.parent_node_id:
                if node.parent_node_id not in node_ids:
                    raise InvariantViolationError(
                        f"Node '{node.code}' ({node.node_id}) references non-existent parent_node_id '{node.parent_node_id}' (TEST-RM-01)."
                    )

        # 3. RQ & giả thuyết độc đáo
        rq_codes = [q.code for q in roadmap.questions]
        if len(rq_codes) != len(set(rq_codes)):
            raise InvariantViolationError(f"Duplicate Research Question code detected (TEST-RM-03).")

        h_codes = [h.code for h in roadmap.hypotheses]
        if len(h_codes) != len(set(h_codes)):
            raise InvariantViolationError(f"Duplicate Hypothesis code detected (TEST-RM-04).")

        # 4. Kiểm tra Canonical nghiêm ngặt (Thông số kỹ thuật đầy đủ của Lộ trình 1.0.0)
        if strict_canonical or len(roadmap.nodes) > 10:
            expected_rqs = {"RQ1", "RQ2", "RQ3", "RQ4", "RQ5"}
            if len(roadmap.questions) != 5 or set(rq_codes) != expected_rqs:
                raise InvariantViolationError(
                    f"Canonical roadmap must contain exactly RQ1..RQ5. Found: {rq_codes} (TEST-RM-03)."
                )

            expected_hs = {"H1", "H2", "H3", "H4", "H5"}
            if len(roadmap.hypotheses) != 5 or set(h_codes) != expected_hs:
                raise InvariantViolationError(
                    f"Canonical roadmap must contain exactly H1..H5. Found: {h_codes} (TEST-RM-04)."
                )

        # 5. Xác nhận hợp đồng đại diện
        if roadmap.representation_contract:
            rc = roadmap.representation_contract
            if not rc.preserve or not rc.invariant or not rc.exclude:
                raise InvariantViolationError(
                    "Representation Contract must specify all three categories: PRESERVE, INVARIANT, EXCLUDE (TEST-RM-07)."
                )

        # 6. Xác thực đối tượng trung tâm
        if "feature representation z" not in (roadmap.central_object or ""):
            raise InvariantViolationError(
                "Central object must explicitly declare 'feature representation z' (TEST-RM-08)."
            )

    def ingest_roadmap_dict(self, data: Dict[str, Any], raw_text: Optional[str] = None) -> ResearchRoadmap:
        """Phân tích cú pháp, xác thực, băm và duy trì thông số kỹ thuật của Lộ trình nghiên cứu một cách bình thường."""
        # Tính toán tổng kiểm tra xác định
        sha256 = compute_string_sha256(raw_text or json.dumps(data, sort_keys=True))

        nodes = [ResearchNode(**n) for n in data.get("nodes", [])]
        questions = [ResearchQuestion(**q) for q in data.get("questions", [])]
        hypotheses = [Hypothesis(**h) for h in data.get("hypotheses", [])]
        axes = [ResearchAxis(**a) for a in data.get("axes", [])]
        rep_contract = RepresentationContract(**data["representation_contract"]) if "representation_contract" in data and data["representation_contract"] else None
        controls = [NegativeControl(**c) for c in data.get("controls", [])]
        boundaries = [ResearchBoundary(**b) for b in data.get("boundaries", [])]
        dqs = [DefensibilityQuestion(**dq) for dq in data.get("defensibility_questions", [])]
        traceability = [TraceabilityEntry(**tr) for tr in data.get("traceability_matrix", [])]

        roadmap = ResearchRoadmap(
            roadmap_id=data.get("roadmap_id") or "ROD-000001",
            version=data.get("version", "1.0.0"),
            title=data.get("title", "Nghiên cứu phương pháp trích xuất đặc trưng đối với dữ liệu log trong phát hiện tấn công"),
            summary=data.get("summary", ""),
            central_object=data.get("central_object", "feature representation z (f_theta: L_{1:t} -> z_t)"),
            sha256_hash=sha256,
            nodes=nodes,
            questions=questions,
            hypotheses=hypotheses,
            axes=axes,
            representation_contract=rep_contract,
            controls=controls,
            boundaries=boundaries,
            defensibility_questions=dqs,
            traceability_matrix=traceability,
        )

        # Xác thực
        self.validate_roadmap_structure(roadmap)

        # Kiên trì một cách bình thường
        self.repo.save_roadmap(roadmap)
        return roadmap
