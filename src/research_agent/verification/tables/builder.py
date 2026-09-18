"""
Trình tạo bảng khoa học xác định (Nhắc 6 Phần 53..56, RC-09)
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd
from research_agent.core.enums import TableType
from research_agent.schemas.verification import TableSpecification


class TableBuilder:
    """
    Xây dựng các bảng khoa học sẵn sàng xuất bản một cách xác định từ các DataFrames có cấu trúc.
    Xuất các biểu diễn CSV, Markdown và LaTeX được căn chỉnh với hàm băm SHA-256 và nguồn gốc ô.
    """

    def build_table(
        self,
        table_id: str,
        title: str,
        caption: str,
        df: pd.DataFrame,
        table_type: TableType = TableType.COMPUTED_TABLE,
        cell_provenance: Optional[Dict[str, str]] = None,
        dataset_ids: Optional[List[str]] = None,
        experiment_run_ids: Optional[List[str]] = None,
        is_comparable: bool = True,
        incomparability_reason: Optional[str] = None,
        generation_script: Optional[str] = None,
    ) -> TableSpecification:
        """Xây dựng một TableSpecification đã được xác minh với nhiều định dạng."""
        columns = [str(c) for c in df.columns]
        rows_data = df.values.tolist()

        # Tạo CSV
        csv_str = df.to_csv(index=False)

        # Tạo Markdown một cách xác định
        headers = [str(c) for c in df.columns]
        md_lines = ["| " + " | ".join(headers) + " |"]
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in df.iterrows():
            md_lines.append("| " + " | ".join(str(val) for val in row) + " |")
        md_str = "\n".join(md_lines)

        # Tạo bảng LaTeX một cách xác định (kiểu Booktabs)
        col_spec = "l" * len(headers)
        latex_lines = [
            r"\begin{table}[htbp]",
            r"\centering",
            f"\\begin{{tabular}}{{{col_spec}}}",
            r"\toprule",
            " & ".join(headers) + r" \\",
            r"\midrule",
        ]
        for _, row in df.iterrows():
            latex_lines.append(" & ".join(str(val) for val in row) + r" \\")
        latex_lines.extend([
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
        ])
        latex_str = "\n".join(latex_lines)

        # Nội dung kết hợp băm
        hasher = hashlib.sha256()
        hasher.update(csv_str.encode("utf-8"))
        output_sha256 = hasher.hexdigest()

        return TableSpecification(
            table_id=table_id,
            table_type=table_type,
            title=title,
            caption=caption,
            columns=columns,
            rows_data=rows_data,
            cell_provenance=cell_provenance or {},
            is_directly_comparable=is_comparable,
            incomparability_reason=incomparability_reason,
            output_csv=csv_str,
            output_markdown=md_str,
            output_latex=latex_str,
            output_sha256=output_sha256,
            dataset_ids=dataset_ids or [],
            experiment_run_ids=experiment_run_ids or [],
            generation_script=generation_script,
            created_at=datetime.now(timezone.utc),
        )
