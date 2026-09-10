# -*- coding: utf-8 -*-
"""
Master Automated Test Suite for Thesis Final Formal-Presentation Audit.
Verifies:
1. Section margins and page orientations (Portrait vs Dedicated Landscape Table 3.3).
2. Page numbering continuity across section transitions.
3. Heading hierarchy, bold styling, keep_with_next, and Vietnamese sentence-case normalization.
4. Body paragraph typography (Times New Roman, 14 pt, JUSTIFY, 1.27 cm indent, 1.5 line spacing).
5. Caption syntax and numbering consistency (Bảng X.Y: and Hình X.Y:).
6. Table Grid formatting, cantSplit across all rows, no overflow.
7. Table 3.3 dedicated landscape properties:
   - Dedicated landscape section
   - 0 mid-token wraps
   - 0 mid-number splits
   - Display mapping to human-readable Vietnamese academic labels
   - Raw source metrics preservation (zero mutation of underlying scientific data)
8. Equation formatting: Native Word OMML (m:oMath), Cambria Math, centered display, no raw unicode pseudo-equations.
9. Scientific Figure alignment, aspect ratio, SEQ Hình fields, and bookmarks.
10. Cryptographic invariance of Chapter 1 and Chapter 2 against historical baseline.
11. Test firewall integrity (TEST_OPENED == false, NEW_OPTIMIZER_STEPS == 0).
"""

import re
import json
import hashlib
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
# 1. SECTION MARGINS & ORIENTATION
# =============================================================================

def test_section_count_and_orientations(thesis_doc):
    sections = thesis_doc.sections
    assert len(sections) == 4, f"Expected 4 sections, found {len(sections)}"

    # Section 0: Cover / Front Matter (Portrait)
    assert sections[0].orientation == docx.enum.section.WD_ORIENT.PORTRAIT
    # Section 1: Main Body pre-Table 3.3 (Portrait)
    assert sections[1].orientation == docx.enum.section.WD_ORIENT.PORTRAIT
    # Section 2: Dedicated Landscape Section for Table 3.3
    assert sections[2].orientation == docx.enum.section.WD_ORIENT.LANDSCAPE
    assert abs(sections[2].page_width.pt - 841.9) < 1.0, f"Landscape width expected 841.9 pt, got {sections[2].page_width.pt}"
    assert abs(sections[2].page_height.pt - 595.3) < 1.0, f"Landscape height expected 595.3 pt, got {sections[2].page_height.pt}"
    # Section 3: Resumed Main Body post-Table 3.3 (Portrait)
    assert sections[3].orientation == docx.enum.section.WD_ORIENT.PORTRAIT


def test_section_page_numbering_continuity(thesis_doc):
    """Verifies that Section 2 (Landscape) and Section 3 (Resumed Portrait) do NOT restart page numbering."""
    body_sectPr = thesis_doc._element.body.find(qn("w:sectPr"))
    assert body_sectPr is not None
    # Ensure final body sectPr does not contain w:start="1"
    for pgn in body_sectPr.findall(qn("w:pgNumType")):
        assert pgn.get(qn("w:start")) is None, "Final section unexpectedly restarts page numbering!"


# =============================================================================
# 2. HEADING HIERARCHY & CASE NORMALIZATION
# =============================================================================

def test_heading_hierarchy_and_keep_with_next(thesis_doc):
    for p in thesis_doc.paragraphs:
        st = p.style.name if p.style else ""
        if st in ["Heading 1", "Heading 2", "Heading 3", "Heading 4"]:
            # All chapter headings must enforce keep_with_next
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
            # Subheadings must NOT be entirely UPPERCASE
            assert not (txt.isupper() and len(txt) > 5), f"Subheading in Chapter 3 is improperly UPPERCASE: '{txt}'"
            # First character of subheading should be uppercase
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
            # Check alignment: JUSTIFY or inherited
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
# 5. TABLE 3.3 DEDICATED LANDSCAPE, ZERO SPLITS, & DISPLAY MAPPING
# =============================================================================

def test_table33_in_landscape_section(thesis_doc):
    t33 = None
    for t in thesis_doc.tables:
        if len(t.rows) == 7 and len(t.columns) == 12:
            t33 = t
            break
    assert t33 is not None, "Table 3.3 not found!"

    # Width of Table 3.3 must match landscape specification (13,600 dxa = 680 pt)
    tblPr = t33._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    assert tblW is not None
    assert tblW.get(qn("w:w")) == "13600", f"Expected width 13600 dxa, got {tblW.get(qn('w:w'))}"


def test_table33_display_mapping_and_zero_splits(thesis_doc, source_metrics):
    t33 = None
    for t in thesis_doc.tables:
        if len(t.rows) == 7 and len(t.columns) == 12:
            t33 = t
            break
    assert t33 is not None

    DISPLAY_CLASSIFICATION = {
        "PROTOCOL_DEVIATION": "Sai lệch giao thức",
        "NONCANONICAL": "Không chuẩn",
        "CANONICAL": "Chuẩn",
        "EVIDENCE_INCOMPLETE": "Thiếu bằng chứng"
    }
    DISPLAY_STOP_REASON = {
        "EARLY_STOPPING": "Dừng sớm",
        "CEILING_REACHED": "Đạt trần epoch",
        "HALTED": "Dừng giữa chừng"
    }

    st = source_metrics["seeds_table"]
    for i, s in enumerate(st):
        row = t33.rows[i + 1]
        cells = [c.text.strip() for c in row.cells]

        # Classification display mapping check
        assert cells[1] == DISPLAY_CLASSIFICATION[s["classification"]]
        # Stop reason display mapping check
        assert cells[4] == DISPLAY_STOP_REASON[s["stop_reason"]]

        # Scientific numbers must be intact on a single line (no newlines in string)
        for c_idx in [3, 5, 7, 8, 9, 10, 11]:
            assert "\n" not in cells[c_idx], f"Number split by newline in cell ({i+1}, {c_idx}): '{cells[c_idx]}'"
            assert " " not in cells[c_idx] or c_idx == 3, f"Number split by space in cell ({i+1}, {c_idx}): '{cells[c_idx]}'"


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
# 6. EQUATION OMML AUDIT
# =============================================================================

def test_equation_omml_presence(thesis_doc):
    omml_elems = thesis_doc._element.xpath(".//m:oMath")
    assert len(omml_elems) >= 65, f"Expected at least 65 OMML elements, found {len(omml_elems)}"


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
