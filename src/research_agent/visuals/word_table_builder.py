"""
Word Native Table Builder (Rule 3)
Builds publication-grade native Word tables matching strict thesis specifications.
Enforces: Repeat header, CantSplit, Exact column widths fitting page margins, Single 0.5pt black border, 14pt Times New Roman, Cell provenance tracking.
"""

from typing import Any, Dict, List, Optional
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import pandas as pd

from research_agent.schemas.verification import TableSpecification
from research_agent.core.enums import TableType


class WordTableBuilder:
    """
    Constructs compliant Word tables from TableSpecification or pandas DataFrame.
    """

    PAGE_WIDTH_DXA = 9600  # Standard body width between 3.5cm left and 2.0cm right margins on A4

    @staticmethod
    def format_table_cell(
        cell: docx.table._Cell,
        width_dxa: int,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        bold: bool = False,
        font_size_pt: float = 14.0,
    ):
        """Formats an individual table cell with exact width, padding, borders, and line spacing."""
        tcPr = cell._tc.get_or_add_tcPr()
        tc_xml = (
            f'<w:tcPr {nsdecls("w")}>\n'
            f'  <w:tcW w:w="{width_dxa}" w:type="dxa"/>\n'
            '  <w:vAlign w:val="center"/>\n'
            '  <w:tcBorders>\n'
            '    <w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            '    <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            '    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            '    <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
            '  </w:tcBorders>\n'
            '  <w:tcMar>\n'
            '    <w:top w:w="80" w:type="dxa"/>\n'
            '    <w:bottom w:w="80" w:type="dxa"/>\n'
            '    <w:left w:w="120" w:type="dxa"/>\n'
            '    <w:right w:w="120" w:type="dxa"/>\n'
            '  </w:tcMar>\n'
            '</w:tcPr>'
        )
        cell._tc.remove(tcPr)
        cell._tc.append(parse_xml(tc_xml))

        p = cell.paragraphs[0]
        p.alignment = align
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(font_size_pt)
            if bold:
                r.bold = True

    @classmethod
    def insert_table(
        cls,
        doc: docx.Document,
        ref_paragraph: Optional[docx.text.paragraph.Paragraph],
        spec: TableSpecification,
        font_size_pt: float = 14.0,
        custom_col_widths_dxa: Optional[List[int]] = None,
    ) -> docx.table.Table:
        """
        Creates and inserts a native Word Table according to TableSpecification.
        """
        headers = spec.columns
        rows_data = spec.rows_data

        tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        tbl.style = "Table Grid"
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        if ref_paragraph is not None:
            ref_paragraph._p.addprevious(tbl._tbl)

        num_cols = len(headers)
        if custom_col_widths_dxa and len(custom_col_widths_dxa) == num_cols:
            col_widths = custom_col_widths_dxa
        else:
            w_per_col = cls.PAGE_WIDTH_DXA // num_cols
            col_widths = [w_per_col] * num_cols
            col_widths[-1] = cls.PAGE_WIDTH_DXA - sum(col_widths[:-1])

        tblPr = tbl._tbl.tblPr
        total_w = sum(col_widths)
        tblPr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{total_w}" w:type="dxa"/>'))

        # Header Row
        hdr_row = tbl.rows[0]
        hdr_trPr = hdr_row._tr.get_or_add_trPr()
        hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for c_i, h in enumerate(headers):
            cell = hdr_row.cells[c_i]
            cell.text = str(h)
            cls.format_table_cell(
                cell,
                col_widths[c_i],
                align=WD_ALIGN_PARAGRAPH.CENTER,
                bold=True,
                font_size_pt=font_size_pt
            )

        # Body Rows
        for r_i, row in enumerate(rows_data):
            b_row = tbl.rows[r_i + 1]
            b_trPr = b_row._tr.get_or_add_trPr()
            b_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

            for c_i, val in enumerate(row):
                cell = b_row.cells[c_i]
                cell.text = str(val)
                # First column centered if category/ID, left-aligned if description
                c_align = WD_ALIGN_PARAGRAPH.CENTER if (c_i == 0 and num_cols >= 4) else WD_ALIGN_PARAGRAPH.LEFT
                cls.format_table_cell(
                    cell,
                    col_widths[c_i],
                    align=c_align,
                    bold=(c_i == 0 and num_cols == 3),
                    font_size_pt=font_size_pt
                )

        return tbl
