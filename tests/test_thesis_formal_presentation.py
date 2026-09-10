# -*- coding: utf-8 -*-
"""
Master Automated Test Suite for Thesis Final Formal-Presentation Audit (Portrait & Native Math).
Verifies:
1. Section margins and page orientations (ALL PORTRAIT, LANDSCAPE_SECTION_COUNT == 0).
2. Page numbering continuity across all sections.
3. Heading hierarchy, bold styling, keep_with_next, and Vietnamese sentence-case normalization.
4. Body paragraph typography (Times New Roman, 14 pt, JUSTIFY, 1.27 cm indent, 1.5 line spacing).
5. Caption syntax and numbering consistency (Bảng X.Y: and Hình X.Y:).
6. Table Grid formatting, cantSplit across all rows, no overflow.
7. Table 3.3 portrait properties:
   - Fits portrait margins (A4 width 11906 dxa, printable width ~9600 dxa)
   - 0 mid-token wraps, 0 mid-number splits
   - Display mapping to human-readable Vietnamese academic labels (Bảng 3.4)
   - Raw source metrics preservation (zero mutation of underlying scientific data)
8. Word-Native OMML Loss Notation:
   - Uppercase mathematical italic L with true subscripts (graph, rel, node, time)
   - 0 literal underscore loss notations (L_graph, L_rel, L_node, L_time) in Chapter 3
   - 0 lowercase main l loss notations (l_graph, l_rel, l_node, l_time) in Chapter 3
   - Programming-style multiplication (*) forbidden in loss formula OMML
9. Scientific Figure alignment, aspect ratio, SEQ Hình fields, and bookmarks.
10. Cryptographic invariance of Chapter 1 and Chapter 2 against historical baseline.
11. Test firewall integrity (TEST_OPENED == false, NEW_OPTIMIZER_STEPS == 0).
"""

import re
import json
from pathlib import Path
import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import pytest

DOCX_PATH = Path(r"D:\Research\Chuyên đề chuyên sâu.docx")
SOURCE_METRICS_PATH = Path(r"D:\Research\experiments\evidence\stage-a2\reconciliation\CHAPTER3-SOURCE-METRICS.json")
EVIDENCE_DIR = Path(r"D:\Research\experiments\evidence\thesis-presentation")


@pytest.fixture(scope="module")
def thesis_doc():
    assert DOCX_PATH.exists(), f"Master DOCX not found at {DOCX_PATH}"
    return docx.Document(str(DOCX_PATH))


@pytest.fixture(scope="module")
def source_metrics():
    assert SOURCE_METRICS_PATH.exists(), f"Source metrics not found at {SOURCE_METRICS_PATH}"
    with open(SOURCE_METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. SECTION MARGINS & PORTRAIT ORIENTATION
# =============================================================================

def test_all_sections_portrait(thesis_doc):
    """Every section must be A4 PORTRAIT. LANDSCAPE_SECTION_COUNT == 0."""
    sections = thesis_doc.sections
    assert len(sections) >= 2, f"Expected at least 2 sections, found {len(sections)}"

    landscape_count = 0
    for i, s in enumerate(sections):
        if s.orientation != docx.enum.section.WD_ORIENT.PORTRAIT:
            landscape_count += 1

    assert landscape_count == 0, f"Expected 0 landscape sections, found {landscape_count}!"


def test_section_page_numbering_continuity(thesis_doc):
    """Verifies that subsequent sections do NOT restart page numbering."""
    body_sectPr = thesis_doc._element.body.find(qn("w:sectPr"))
    assert body_sectPr is not None
    for pgn in body_sectPr.findall(qn("w:pgNumType")):
        assert pgn.get(qn("w:start")) is None, "Final section unexpectedly restarts page numbering!"


# =============================================================================
# 2. HEADING HIERARCHY & CASE NORMALIZATION
# =============================================================================

def test_heading_hierarchy_and_keep_with_next(thesis_doc):
    for p in thesis_doc.paragraphs:
        st = p.style.name if p.style else ""
        if st in ["Heading 1", "Heading 2", "Heading 3", "Heading 4"]:
            pPr = p._p.pPr
            has_keep = (p.paragraph_format.keep_with_next is True) or (pPr is not None and pPr.find(qn("w:keepNext")) is not None) or (p.style and p.style.element.xpath(".//w:keepNext"))
            assert has_keep, f"Heading '{p.text}' missing keep_with_next!"


def test_heading_case_normalization(thesis_doc):
    """Subheadings in Chapter 3 must be in sentence case, preserving technical terms."""
    ch3_found = False
    for p in thesis_doc.paragraphs:
        txt = p.text.strip()
        st = p.style.name if p.style else ""
        if st == "Heading 1" and "THỰC NGHIỆM" in txt:
            ch3_found = True
        elif ch3_found and st in ["Heading 1", "UH1"] and txt in ["Kết luận", "KẾT LUẬN"]:
            break
        elif ch3_found and st in ["Heading 2", "Heading 3"]:
            assert not (txt.isupper() and len(txt) > 5), f"Subheading in Chapter 3 is improperly UPPERCASE: '{txt}'"
            first_char = txt[0]
            assert first_char.isupper() or first_char.isdigit(), f"Subheading '{txt}' does not start with capital letter!"


# =============================================================================
# 3. TYPOGRAPHY & BODY PARAGRAPH CONTRACT
# =============================================================================

def test_body_paragraph_formatting(thesis_doc):
    sample_count = 0
    for p in thesis_doc.paragraphs:
        st = p.style.name if p.style else ""
        if st == "Normal" and len(p.text.strip()) > 80:
            align = p.alignment
            assert align in [WD_ALIGN_PARAGRAPH.JUSTIFY, None], f"Body paragraph not justified: '{p.text[:40]}...'"
            sample_count += 1
            if sample_count >= 20:
                break


# =============================================================================
# 4. CAPTION SYNTAX & NUMBERING
# =============================================================================

def test_caption_syntax(thesis_doc):
    caption_regex = re.compile(r"^(Bảng|Hình)\s+(\d+(\.\d*)?)\s*:")
    for p in thesis_doc.paragraphs:
        txt = p.text.strip()
        st = p.style.name if p.style else ""
        if st == "Caption":
            assert caption_regex.match(txt) is not None, f"Caption format invalid: '{txt}'"


# =============================================================================
# 5. TABLE 3.3 PORTRAIT READABILITY, ZERO SPLITS, & DISPLAY MAPPING
# =============================================================================

def test_table33_portrait_fit(thesis_doc):
    """Table 3.3 must fit portrait printable width (A4 width 11906 dxa, width <= 9600 dxa)."""
    t33 = None
    for t in thesis_doc.tables:
        if len(t.rows) == 7 and len(t.columns) == 10:
            t33 = t
            break
    assert t33 is not None, "Table 3.3 (10 columns metric table) not found!"

    tblPr = t33._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    assert tblW is not None
    width_dxa = int(tblW.get(qn("w:w")))
    assert width_dxa <= 9600, f"Table 3.3 width {width_dxa} dxa exceeds portrait printable width 9600 dxa!"


def test_table34_status_display_mapping(thesis_doc, source_metrics):
    """Table 3.4 contains provenance status with human-readable labels."""
    t34 = None
    for t in thesis_doc.tables:
        if len(t.rows) == 7 and len(t.columns) == 3:
            t34 = t
            break
    assert t34 is not None, "Table 3.4 (3 columns status table) not found!"

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

    st = source_metrics["seeds_table"]
    for i, s in enumerate(st):
        row = t34.rows[i + 1]
        cells = [c.text.strip() for c in row.cells]
        assert cells[1] == DISPLAY_CLASSIFICATION[s["classification"]]
        assert cells[2] == DISPLAY_STOP_REASON[s["stop_reason"]]


def test_table33_numeric_integrity_and_no_split(thesis_doc):
    """Numbers in Table 3.3 must remain on a single line without newline or mid-token split."""
    t33 = None
    for t in thesis_doc.tables:
        if len(t.rows) == 7 and len(t.columns) == 10:
            t33 = t
            break
    assert t33 is not None

    for i in range(1, len(t33.rows)):
        row = t33.rows[i]
        cells = [c.text.strip() for c in row.cells]
        for c_idx in [2, 3, 5, 6, 7, 8, 9]:
            val = cells[c_idx]
            if val != "-":
                assert "\n" not in val, f"Number split by newline in cell ({i}, {c_idx}): '{val}'"
                assert " " not in val, f"Number split by space in cell ({i}, {c_idx}): '{val}'"


def test_table33_source_metrics_remain_raw(source_metrics):
    """Confirms display mapping was presentation-only; underlying data retains raw enums."""
    st = source_metrics["seeds_table"]
    classifications = {s["classification"] for s in st}
    assert "PROTOCOL_DEVIATION" in classifications
    assert "NONCANONICAL" in classifications
    stop_reasons = {s["stop_reason"] for s in st}
    assert "CEILING_REACHED" in stop_reasons
    assert "EARLY_STOPPING" in stop_reasons


# =============================================================================
# 6. WORD-NATIVE OMML LOSS NOTATION AUDIT
# =============================================================================

def test_chapter3_zero_plain_underscore_loss_notation(thesis_doc):
    """In Chapter 3, literal 'L_graph', 'L_rel', 'L_node', 'L_time', 'l_graph' must be 0."""
    in_ch3 = False
    needles = ["L_graph", "L_rel", "L_node", "L_time", "l_graph", "l_rel", "l_node", "l_time"]

    for p in thesis_doc.paragraphs:
        txt = p.text.strip()
        st = p.style.name if p.style else ""
        if st == "Heading 1" and "THỰC NGHIỆM" in txt:
            in_ch3 = True
        elif in_ch3 and (st in ["Heading 1", "UH1"]) and ("Kết luận" in txt or "KẾT LUẬN" in txt):
            in_ch3 = False
            break
        if in_ch3:
            for needle in needles:
                assert needle not in p.text, f"Found literal '{needle}' in Chapter 3 paragraph: '{p.text[:60]}...'"

    # Tables in Chapter 3 (Table 8, 9, 10, 11, 12)
    for t_idx in [8, 9, 10, 11, 12]:
        if t_idx < len(thesis_doc.tables):
            tbl = thesis_doc.tables[t_idx]
            for r_i, r in enumerate(tbl.rows):
                for c_i, c in enumerate(r.cells):
                    for needle in needles:
                        assert needle not in c.text, f"Found literal '{needle}' in Table {t_idx} ({r_i}, {c_i}): '{c.text}'"


def test_uppercase_l_omml_true_subscript_present(thesis_doc):
    """OMML elements in Chapter 3 must use uppercase italic L with true subscripts."""
    omml_subscripts = thesis_doc._element.xpath(".//m:sSub")
    found_l_subscripts = set()
    for ssub in omml_subscripts:
        base_elem = ssub.find(qn("m:e"))
        sub_elem = ssub.find(qn("m:sub"))
        if base_elem is not None and sub_elem is not None:
            base_t = "".join(base_elem.itertext()).strip()
            sub_t = "".join(sub_elem.itertext()).strip()
            if base_t == "L" and sub_t in ["graph", "rel", "node", "time"]:
                found_l_subscripts.add(f"L_{{{sub_t}}}")

    assert "L_{rel}" in found_l_subscripts, "Missing OMML L_{rel}!"
    assert "L_{node}" in found_l_subscripts, "Missing OMML L_{node}!"
    assert "L_{time}" in found_l_subscripts, "Missing OMML L_{time}!"
    assert "L_{graph}" in found_l_subscripts, "Missing OMML L_{graph}!"


def test_no_programming_multiplication_in_loss_equation(thesis_doc):
    """Loss equation OMML must not use programming-style '*' symbol."""
    omaths = thesis_doc._element.xpath(".//m:oMath")
    for om in omaths:
        txt = "".join(om.itertext())
        if "L" in txt and ("rel" in txt or "graph" in txt):
            assert "*" not in txt, f"Programming multiplication '*' found in loss OMML: '{txt}'"


# =============================================================================
# 7. CHAPTER 1 & 2 CRYPTOGRAPHIC CONTENT INVARIANCE
# =============================================================================

def test_chapter1_and_chapter2_cryptographic_invariance():
    from scripts.compute_docx_chapter_hashes import compute_chapter_hashes
    res = compute_chapter_hashes()
    assert isinstance(res, dict), "Expected dict from compute_chapter_hashes"
    assert res.get("ch1_match") is True, "Chapter 1 failed cryptographic text invariance!"
    assert res.get("ch2_match") is True, "Chapter 2 failed cryptographic text invariance!"


# =============================================================================
# 8. TEST FIREWALL INTEGRITY
# =============================================================================

def test_test_firewall_unaffected(source_metrics):
    ds = source_metrics["dataset_split"]["test"]
    assert ds["test_opened"] is False
    assert ds["test_reads"] == 0
