"""
Hình Trình quản lý siêu dữ liệu & xuất xứ (Nhắc 6 Phần 60)
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from research_agent.schemas.verification import FigureSpecification


class FigureMetadataManager:
    """
    Tạo và kiểm tra các tệp siêu dữ liệu mà máy có thể đọc được đồng hành với các số liệu khoa học.
    """

    def generate_metadata_file(
        self,
        fig_spec: FigureSpecification,
        metadata_path: Path | str,
    ) -> str:
        """Ghi hình-metadata.json liên kết hình ảnh với mã và băm dữ liệu."""
        p = Path(metadata_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        meta = {
            "figure_id": fig_spec.figure_id,
            "figure_type": fig_spec.figure_type.value if hasattr(fig_spec.figure_type, "value") else str(fig_spec.figure_type),
            "title": fig_spec.title,
            "caption": fig_spec.caption,
            "plot_script_path": fig_spec.plot_script_path,
            "output_file_rel_path": fig_spec.output_file_rel_path,
            "companion_data_csv_rel_path": fig_spec.companion_data_csv_rel_path,
            "output_sha256": fig_spec.output_sha256,
            "companion_data_sha256": fig_spec.companion_data_sha256,
            "manually_edited": fig_spec.manually_edited,
            "manual_edit_reason": fig_spec.manual_edit_reason,
            "created_at": fig_spec.created_at.isoformat(),
        }

        with open(p, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return str(p)
