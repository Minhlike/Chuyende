"""
Canonical Visual Registry (Rule 7)
Maintains full provenance, metadata, bookmarks, and verification status for every figure, diagram, and table.
"""

import json
from typing import Any, Dict, List, Optional
from research_agent.storage.db import DatabaseManager
from research_agent.visuals.schemas import VisualRecord, VisualType, CreationMethod, VisualNecessityEvaluation


class VisualRegistry:
    """
    Central repository for scientific visuals (Diagrams, Figures, Tables).
    Guarantees stable IDs (FIG-xxxxxx, TBL-xxxxxx), bookmarks, and data provenance.
    """

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self._ensure_table()

    def _ensure_table(self):
        with self.db.session() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS visual_records (
                visual_id TEXT PRIMARY KEY,
                node_code TEXT NOT NULL,
                purpose TEXT NOT NULL,
                visual_type TEXT NOT NULL,
                creation_method TEXT NOT NULL,
                caption TEXT NOT NULL,
                source_provenance TEXT NOT NULL,
                script_path TEXT,
                output_file_path TEXT,
                companion_data_path TEXT,
                output_sha256 TEXT NOT NULL,
                bookmark_name TEXT NOT NULL,
                seq_number INTEGER NOT NULL DEFAULT 1,
                chapter_number INTEGER DEFAULT 1,
                is_verified INTEGER NOT NULL DEFAULT 1,
                necessity_json TEXT,
                created_at TEXT NOT NULL
            )
            """)

    def register_visual(self, record: VisualRecord) -> VisualRecord:
        """Registers a visual record in the database."""
        with self.db.session() as conn:
            conn.execute("""
            INSERT OR REPLACE INTO visual_records (
                visual_id, node_code, purpose, visual_type, creation_method,
                caption, source_provenance, script_path, output_file_path,
                companion_data_path, output_sha256, bookmark_name, seq_number,
                chapter_number, is_verified, necessity_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.visual_id,
                record.node_code,
                record.purpose,
                record.visual_type.value,
                record.creation_method.value,
                record.caption,
                record.source_provenance,
                record.script_path,
                record.output_file_path,
                record.companion_data_path,
                record.output_sha256,
                record.bookmark_name,
                record.seq_number,
                record.chapter_number,
                1 if record.is_verified else 0,
                record.necessity_evaluation.model_dump_json() if record.necessity_evaluation else None,
                record.created_at.isoformat(),
            ))
        return record

    def get_visual(self, visual_id: str) -> Optional[VisualRecord]:
        """Retrieves a visual record by its stable ID."""
        with self.db.session() as conn:
            row = conn.execute("SELECT * FROM visual_records WHERE visual_id = ?", (visual_id,)).fetchone()
            if not row:
                return None
            return self._row_to_record(row)

    def list_visuals(self, visual_type: Optional[VisualType] = None) -> List[VisualRecord]:
        """Lists all registered visuals, optionally filtered by type."""
        with self.db.session() as conn:
            if visual_type:
                rows = conn.execute("SELECT * FROM visual_records WHERE visual_type = ? ORDER BY seq_number", (visual_type.value,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM visual_records ORDER BY seq_number").fetchall()
            return [self._row_to_record(r) for r in rows]

    def _row_to_record(self, row: Any) -> VisualRecord:
        keys = ["visual_id", "node_code", "purpose", "visual_type", "creation_method",
                "caption", "source_provenance", "script_path", "output_file_path",
                "companion_data_path", "output_sha256", "bookmark_name", "seq_number",
                "chapter_number", "is_verified", "necessity_json", "created_at"]
        d = dict(zip(keys, row))
        nec = json.loads(d["necessity_json"]) if d.get("necessity_json") else None
        return VisualRecord(
            visual_id=d["visual_id"],
            node_code=d["node_code"],
            purpose=d["purpose"],
            visual_type=VisualType(d["visual_type"]),
            creation_method=CreationMethod(d["creation_method"]),
            caption=d["caption"],
            source_provenance=d["source_provenance"],
            script_path=d["script_path"],
            output_file_path=d["output_file_path"],
            companion_data_path=d["companion_data_path"],
            output_sha256=d["output_sha256"],
            bookmark_name=d["bookmark_name"],
            seq_number=d["seq_number"],
            chapter_number=d["chapter_number"],
            is_verified=bool(d["is_verified"]),
            necessity_evaluation=VisualNecessityEvaluation(**nec) if nec else None,
            created_at=d["created_at"],
        )
