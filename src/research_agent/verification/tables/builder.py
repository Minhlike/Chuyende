"""
Deterministic Scientific Table Builder (Prompt 6 Sections 53..56, RC-09)
"""

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd
from research_agent.core.enums import TableType
from research_agent.schemas.verification import TableSpecification


class TableBuilder:
    """
    Builds publication-ready scientific tables deterministically from structured DataFrames.
    Exports aligned CSV, Markdown, and LaTeX representations with SHA-256 hash and cell provenance.
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
        """Constructs a verified TableSpecification with multiple formats."""
        columns = [str(c) for c in df.columns]
        rows_data = df.values.tolist()

        # Generate CSV
        csv_str = df.to_csv(index=False)

        # Generate Markdown deterministically
        headers = [str(c) for c in df.columns]
        md_lines = ["| " + " | ".join(headers) + " |"]
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for _, row in df.iterrows():
            md_lines.append("| " + " | ".join(str(val) for val in row) + " |")
        md_str = "\n".join(md_lines)

        # Generate LaTeX tabular deterministically (Booktabs style)
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

        # Hash combined content
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
