# -*- coding: utf-8 -*-
"""
Automated Test Suite for Table 3.3 & Table 3.4 Layout & Formatting Verification.
Verifies:
1. Bookmark-based location of Table 3.3 (BK_TBL_3_003) and Table 3.4 (BK_TBL_3_004).
2. Structural shape:
   - Table 3.3: 7 rows x 10 columns (Metric table)
   - Table 3.4: 7 rows x 3 columns (Provenance / Status table)
3. Style: "Table Grid".
4. Table alignment: CENTER (<w:jc w:val="center"/>).
5. Table layout: FIXED (<w:tblLayout w:type="fixed"/>).
6. Row properties: cantSplit enabled across all rows.
7. Cell vertical alignment: CENTER (<w:vAlign w:val="center"/>) across all cells.
8. Cell paragraph formatting:
   - horizontal alignment according to semantic specifications
   - space_before: 0 pt
   - space_after: 0 pt
   - first_line_indent: 0 cm
9. Non-empty cell content (accounting for OMML elements).
10. Exact parity between displayed scientific metrics/labels and CHAPTER3-SOURCE-METRICS.json.
"""

import json
from pathlib import Path
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import pytest

DOCX_PATH = Path(r"D:\Research\Chuyên đề chuyên sâu.docx")
SOURCE_METRICS_PATH = Path(r"D:\Research\experiments\evidence\stage-a2\reconciliation\CHAPTER3-SOURCE-METRICS.json")

DISPLAY_CLASSIFICATION = {
    "CANONICAL": "Đạt chuẩn",
    "PROTOCOL_DEVIATION": "Có sai lệch thủ tục",
    "NONCANONICAL": "Ngoài tập chuẩn",
    "EVIDENCE_INCOMPLETE": "Hồ sơ chưa đầy đủ"
}
DISPLAY_STOP_REASON = {
    "EARLY_STOPPING": "Dừng sớm",
    "CEILING_REACHED": "Đạt trần epoch",
    "HALTED": "Dừng giữa chừng"
}

EXPECTED_T33_BODY_ALIGNMENTS = [
    WD_ALIGN_PARAGRAPH.CENTER,  # 0: Hạt giống
    WD_ALIGN_PARAGRAPH.CENTER,  # 1: Epoch
    WD_ALIGN_PARAGRAPH.RIGHT,   # 2: Số bước
    WD_ALIGN_PARAGRAPH.RIGHT,   # 3: Train loss
    WD_ALIGN_PARAGRAPH.CENTER,  # 4: Best epoch
    WD_ALIGN_PARAGRAPH.RIGHT,   # 5: Best val loss
    WD_ALIGN_PARAGRAPH.RIGHT,   # 6: Val loss cuối
    WD_ALIGN_PARAGRAPH.RIGHT,   # 7: L_rel
    WD_ALIGN_PARAGRAPH.RIGHT,   # 8: L_node
    WD_ALIGN_PARAGRAPH.RIGHT    # 9: L_time
]

EXPECTED_T34_BODY_ALIGNMENTS = [
    WD_ALIGN_PARAGRAPH.CENTER,  # 0: Hạt giống
    WD_ALIGN_PARAGRAPH.CENTER,  # 1: Trạng thái hồ sơ
    WD_ALIGN_PARAGRAPH.CENTER   # 2: Lý do kết thúc
]


def find_table_by_bookmark(doc, bookmark_name):
    body = doc._body._element
    target_tbl = None
    for bm in body.iter(qn("w:bookmarkStart")):
        if bm.get(qn("w:name")) == bookmark_name:
            curr = bm.getparent()
            while curr is not None:
                curr = curr.getnext()
                if curr is not None and curr.tag.endswith("tbl"):
                    target_tbl = curr
                    break
            break
    if target_tbl is None:
        return None, None

    for t in doc.tables:
        if t._tbl == target_tbl:
            return t, target_tbl
    return None, None


@pytest.fixture(scope="module")
def doc_and_metrics():
    assert DOCX_PATH.exists(), f"Master DOCX not found at: {DOCX_PATH}"
    assert SOURCE_METRICS_PATH.exists(), f"Source metrics not found at: {SOURCE_METRICS_PATH}"

    doc = docx.Document(str(DOCX_PATH))
    with open(SOURCE_METRICS_PATH, "r", encoding="utf-8") as f:
        source_metrics = json.load(f)

    return doc, source_metrics


def test_table33_structure_and_style(doc_and_metrics):
    doc, _ = doc_and_metrics
    table, tbl_elem = find_table_by_bookmark(doc, "BK_TBL_3_003")
    assert table is not None, "Table 3.3 not found following bookmark BK_TBL_3_003!"
    assert len(table.rows) == 7, f"Expected 7 rows, found {len(table.rows)}"
    assert len(table.columns) == 10, f"Expected 10 columns, found {len(table.columns)}"
    assert table.style.name == "Table Grid", f"Expected style 'Table Grid', found '{table.style.name}'"


def test_table34_structure_and_style(doc_and_metrics):
    doc, _ = doc_and_metrics
    table, tbl_elem = find_table_by_bookmark(doc, "BK_TBL_3_004")
    assert table is not None, "Table 3.4 not found following bookmark BK_TBL_3_004!"
    assert len(table.rows) == 7, f"Expected 7 rows, found {len(table.rows)}"
    assert len(table.columns) == 3, f"Expected 3 columns, found {len(table.columns)}"
    assert table.style.name == "Table Grid", f"Expected style 'Table Grid', found '{table.style.name}'"


def test_table33_alignment_and_fixed_layout(doc_and_metrics):
    doc, _ = doc_and_metrics
    table, tbl_elem = find_table_by_bookmark(doc, "BK_TBL_3_003")
    tblPr = tbl_elem.tblPr
    assert tblPr is not None, "Table 3.3 missing tblPr!"

    tblLayout = tblPr.find(qn("w:tblLayout"))
    assert tblLayout is not None, "Table 3.3 missing <w:tblLayout> element!"
    assert tblLayout.get(qn("w:type")) == "fixed", f"Expected fixed layout, got {tblLayout.get(qn('w:type'))}"

    jc = tblPr.find(qn("w:jc"))
    assert jc is not None, "Table 3.3 missing <w:jc> element in tblPr!"
    assert jc.get(qn("w:val")) == "center", f"Expected center table alignment, got {jc.get(qn('w:val'))}"
    assert table.alignment == WD_TABLE_ALIGNMENT.CENTER


def test_table33_and_34_row_cant_split(doc_and_metrics):
    doc, _ = doc_and_metrics
    for bm in ["BK_TBL_3_003", "BK_TBL_3_004"]:
        table, _ = find_table_by_bookmark(doc, bm)
        assert table is not None, f"Table for {bm} not found!"
        for r_idx, row in enumerate(table.rows):
            trPr = row._tr.get_or_add_trPr()
            cantSplit = trPr.find(qn("w:cantSplit"))
            assert cantSplit is not None, f"{bm} Row {r_idx} missing <w:cantSplit/>!"


def test_table33_cell_alignments(doc_and_metrics):
    doc, _ = doc_and_metrics
    table, _ = find_table_by_bookmark(doc, "BK_TBL_3_003")
    assert table is not None

    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.get_or_add_tcPr()
            vAlign = tcPr.find(qn("w:vAlign"))
            assert vAlign is not None, f"Cell ({r_idx}, {c_idx}) missing <w:vAlign/>!"
            assert vAlign.get(qn("w:val")) == "center"

            expected_align = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 else EXPECTED_T33_BODY_ALIGNMENTS[c_idx]
            for p in cell.paragraphs:
                has_content = len(p.text.strip()) > 0 or len(p._p.findall(".//" + qn("m:oMath"))) > 0
                if has_content:
                    assert p.alignment == expected_align, (
                        f"Cell ({r_idx}, {c_idx}) alignment is {p.alignment}, expected {expected_align}"
                    )
                    assert (p.paragraph_format.first_line_indent or 0) == 0
                    assert (p.paragraph_format.space_before or 0) == 0
                    assert (p.paragraph_format.space_after or 0) == 0


def test_table34_cell_alignments(doc_and_metrics):
    doc, _ = doc_and_metrics
    table, _ = find_table_by_bookmark(doc, "BK_TBL_3_004")
    assert table is not None

    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            tcPr = cell._tc.get_or_add_tcPr()
            vAlign = tcPr.find(qn("w:vAlign"))
            assert vAlign is not None, f"Cell ({r_idx}, {c_idx}) missing <w:vAlign/>!"
            assert vAlign.get(qn("w:val")) == "center"

            expected_align = WD_ALIGN_PARAGRAPH.CENTER if r_idx == 0 else EXPECTED_T34_BODY_ALIGNMENTS[c_idx]
            for p in cell.paragraphs:
                if len(p.text.strip()) > 0:
                    assert p.alignment == expected_align
                    assert (p.paragraph_format.first_line_indent or 0) == 0
                    assert (p.paragraph_format.space_before or 0) == 0
                    assert (p.paragraph_format.space_after or 0) == 0


def test_table33_and_34_no_empty_cells(doc_and_metrics):
    doc, _ = doc_and_metrics
    for bm in ["BK_TBL_3_003", "BK_TBL_3_004"]:
        table, _ = find_table_by_bookmark(doc, bm)
        assert table is not None
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                txt = cell.text.strip()
                has_omml = len(cell._tc.findall(".//" + qn("m:oMath"))) > 0
                assert len(txt) > 0 or has_omml, f"{bm} Cell ({r_idx}, {c_idx}) is unexpectedly empty!"


def test_table33_source_metrics_parity(doc_and_metrics):
    doc, source_metrics = doc_and_metrics
    table, _ = find_table_by_bookmark(doc, "BK_TBL_3_003")
    assert table is not None
    st = source_metrics["seeds_table"]
    ag_dev = source_metrics["aggregates"]["protocol_deviation"]

    # Check 5 seeds (rows 1..5)
    for i, s in enumerate(st):
        row = table.rows[i + 1]
        cells = [c.text.strip() for c in row.cells]
        assert cells[0] == s["seed_name"]
        assert cells[1] == str(s["epochs_completed"])
        assert cells[2] == f"{s['steps']:,}"
        assert cells[3] == f"{s['train_loss']:.4f}"
        assert cells[4] == str(s["best_epoch"])
        assert cells[5] == f"{s['best_val_loss']:.6f}"
        assert cells[6] == f"{s['final_val_loss']:.6f}"
        assert cells[7] == f"{s['l_rel']:.4f}"
        assert cells[8] == f"{s['l_node']:.4f}"
        assert cells[9] == f"{s['l_time']:.4f}"

    # Check aggregate row (row 6)
    agg_row = table.rows[6]
    agg_cells = [c.text.strip() for c in agg_row.cells]
    assert agg_cells[0] == "TB lệch thủ tục (3 seed)"
    assert agg_cells[1] == "-"
    assert agg_cells[2] == "-"
    assert agg_cells[3] == f"{ag_dev['mean_final_train_loss']:.4f}"
    assert agg_cells[4] == "-"
    assert agg_cells[5] == f"{ag_dev['mean_best_val_loss']:.6f}"
    assert agg_cells[6] == f"{ag_dev['mean_final_val_loss']:.6f}"
    assert agg_cells[7] == f"{ag_dev['mean_l_rel']:.4f}"
    assert agg_cells[8] == f"{ag_dev['mean_l_node']:.4f}"
    assert agg_cells[9] == f"{ag_dev['mean_l_time']:.4f}"


def test_table34_source_metrics_parity(doc_and_metrics):
    doc, source_metrics = doc_and_metrics
    table, _ = find_table_by_bookmark(doc, "BK_TBL_3_004")
    assert table is not None
    st = source_metrics["seeds_table"]

    # Header check
    hdr_cells = [c.text.strip() for c in table.rows[0].cells]
    assert hdr_cells[0] == "Hạt giống"
    assert "Trạng thái hồ sơ" in hdr_cells[1] or "Trạng thái" in hdr_cells[1]
    assert hdr_cells[2] == "Lý do kết thúc"

    # Check 5 seeds
    for i, s in enumerate(st):
        row = table.rows[i + 1]
        cells = [c.text.strip() for c in row.cells]
        assert cells[0] == s["seed_name"]
        assert cells[1] == DISPLAY_CLASSIFICATION[s["classification"]]
        assert cells[2] == DISPLAY_STOP_REASON[s["stop_reason"]]

    # Check aggregate row
    agg_row = table.rows[6]
    agg_cells = [c.text.strip() for c in agg_row.cells]
    assert agg_cells[0] == "TB lệch thủ tục (3 seed)"
    assert agg_cells[1] == DISPLAY_CLASSIFICATION["PROTOCOL_DEVIATION"]
    assert agg_cells[2] == "-"


def test_table33_and_34_display_mapping_is_presentation_only(doc_and_metrics):
    """Verifies that machine-readable source JSON retains raw enum strings."""
    _, source_metrics = doc_and_metrics
    st = source_metrics["seeds_table"]
    raw_classifications = {s["classification"] for s in st}
    assert "PROTOCOL_DEVIATION" in raw_classifications
    assert "NONCANONICAL" in raw_classifications
    raw_stop_reasons = {s["stop_reason"] for s in st}
    assert "CEILING_REACHED" in raw_stop_reasons
    assert "EARLY_STOPPING" in raw_stop_reasons
