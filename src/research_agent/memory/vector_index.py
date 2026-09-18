"""
Công cụ lưu trữ và xây dựng lại chỉ mục vectơ có nguồn gốc (Dấu Prompt 4, Phần 23, Phần 42, Bất biến 9)
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from research_agent.memory.embeddings import EmbeddingProvider, LocalBM25TFIDFEmbeddingProvider, EmbeddingVector
from research_agent.storage.repository import ResearchRepository


class DerivedVectorIndex:
    """
    Chỉ số vectơ dẫn xuất, dùng một lần để xếp hạng độ tương tự cosin ngữ nghĩa nhanh.
    Tuân thủ nghiêm ngặt Bất biến 9: Chỉ mục phái sinh có thể dùng một lần và có thể xây dựng lại.
    """

    def __init__(
        self,
        index_path: Path | str = "runtime/indexes/derived_vectors.json",
        provider: Optional[EmbeddingProvider] = None,
    ):
        self.index_path = Path(index_path)
        self.provider = provider or LocalBM25TFIDFEmbeddingProvider()
        self.vectors: Dict[str, EmbeddingVector] = {}
        self.index_version: str = "1.0.0"
        self._load()

    def _load(self) -> None:
        if self.index_path.exists():
            try:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.index_version = data.get("index_version", "1.0.0")
                    model_id = data.get("model_id", "")
                    # Vô hiệu nếu mô hình không khớp
                    if model_id != self.provider.model_id:
                        self.vectors = {}
                        return
                    for item in data.get("vectors", []):
                        vec = EmbeddingVector(**item)
                        self.vectors[vec.entity_id] = vec
            except Exception:
                self.vectors = {}
        else:
            self.vectors = {}

    def save(self) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "index_version": self.index_version,
            "model_id": self.provider.model_id,
            "model_version": self.provider.model_version,
            "dimensions": self.provider.dimensions,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "vectors": [v.model_dump(mode="json") for v in self.vectors.values()],
        }
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_or_update(self, entity_id: str, entity_type: str, text: str) -> None:
        vec_vals = self.provider.embed_text(text)
        self.vectors[entity_id] = EmbeddingVector(
            entity_id=entity_id,
            entity_type=entity_type,
            model_id=self.provider.model_id,
            model_version=self.provider.model_version,
            dimensions=self.provider.dimensions,
            vector=vec_vals,
        )

    def remove(self, entity_id: str) -> None:
        if entity_id in self.vectors:
            del self.vectors[entity_id]

    def clear(self) -> None:
        self.vectors.clear()
        if self.index_path.exists():
            self.index_path.unlink()

    def search(self, query: str, top_k: int = 10, entity_type: Optional[str] = None) -> List[Tuple[str, str, float]]:
        """
        Tìm kiếm chỉ mục vectơ theo độ tương tự cosin.
        Trả về: Danh sách (entity_id, entity_type, similarity_score).
        """
        query_vec = self.provider.embed_text(query)
        q_norm = math.sqrt(sum(x * x for x in query_vec))
        if q_norm < 1e-9:
            return []

        scored: List[Tuple[str, str, float]] = []
        for v in self.vectors.values():
            if entity_type and v.entity_type != entity_type:
                continue
            # Độ tương tự cosine giữa các vectơ chuẩn hóa L2 là tích số chấm
            dot = sum(a * b for a, b in zip(query_vec, v.vector))
            scored.append((v.entity_id, v.entity_type, dot))

        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:top_k]

    def rebuild_from_repository(self, repo: ResearchRepository) -> int:
        """Xây dựng lại hoàn toàn chỉ mục vectơ từ các thực thể kho lưu trữ chuẩn."""
        self.vectors.clear()
        count = 0

        # Nguồn
        for s in repo.list_sources():
            text = f"{s.title} {s.venue} {s.notes or ''} {' '.join(s.keywords)}"
            self.add_or_update(s.source_id, "SOURCE", text)
            count += 1

        # Khiếu nại
        for c in repo.list_claims():
            text = f"{c.statement} {c.scope or ''} {' '.join(c.assumptions)}"
            self.add_or_update(c.claim_id, "CLAIM", text)
            count += 1

        # Nút lộ trình
        for n in repo.list_roadmap_nodes():
            text = f"{n.code} {n.title} {n.canonical_text or ''}"
            self.add_or_update(n.node_id, "ROADMAP_NODE", text)
            count += 1

        # Câu hỏi & Giả thuyết
        for q in repo.list_research_questions():
            text = f"{q.code} {q.title} {q.canonical_wording_en}"
            self.add_or_update(q.rq_id, "RESEARCH_QUESTION", text)
            count += 1

        for h in repo.list_hypotheses():
            text = f"{h.code} {h.title} {h.statement} {h.falsification_criteria}"
            self.add_or_update(h.hyp_id, "HYPOTHESIS", text)
            count += 1

        # Quyết định
        for d in repo.list_decisions():
            text = f"{d.title} {d.decision} {d.rationale} {d.context}"
            self.add_or_update(d.decision_id, "DECISION", text)
            count += 1

        # tập phim
        for e in repo.list_episodes():
            text = f"{e.action} {e.outcome} {e.failure_reason or ''}"
            self.add_or_update(e.episode_id, "EPISODE", text)
            count += 1

        # Bài học
        for l in repo.list_lessons_learned():
            text = f"{l.title} {l.statement} {' '.join(l.actionable_recommendations)}"
            self.add_or_update(l.lesson_id, "LESSON", text)
            count += 1

        # Câu hỏi mở
        for o in repo.list_open_questions():
            text = f"{o.question} {o.why_open} {o.required_evidence}"
            self.add_or_update(o.question_id, "OPEN_QUESTION", text)
            count += 1

        # Bản ghi bộ nhớ
        for m in repo.list_memories():
            text = f"{m.topic} {m.summary} {m.content or ''}"
            self.add_or_update(m.memory_id, "MEMORY", text)
            count += 1

        self.save()
        return count
