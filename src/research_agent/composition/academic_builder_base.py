"""
Bậc thầy xây dựng tài liệu Word học thuật - Chương 1 & Chương 2 Phần 2.1
Biên soạn tài liệu luận án khoa học nguyên sơ trực tiếp vào Microsoft Word 2016 (.docx)
với Trích dẫn Từ gốc, Phương trình OMML, Hình ảnh Vector, Chú thích và Tự động hóa COM.
"""

import os
import shutil
import zipfile
import uuid
import json
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Iterable
import win32com.client as win32
import pythoncom
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn


CANONICAL_SOURCES_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "research_specs"
    / "reference_map"
    / "CANONICAL-SOURCES.json"
)


@dataclass
class CanonicalSource:
    source_key: str
    canonical_title: str
    canonical_authors: List[str]
    year: int
    venue: Optional[str]
    publication_type: str
    doi: Optional[str]
    url: Optional[str]
    word_source_tag: str
    aliases: Optional[List[str]] = None

    # Properties for compatibility with legacy source consumers
    @property
    def source_id(self) -> str:
        return self.word_source_tag

    @property
    def title(self) -> str:
        return self.canonical_title

    @property
    def authors(self) -> List[str]:
        return self.canonical_authors


_CANONICAL_SOURCES: Optional[List[CanonicalSource]] = None
_CANONICAL_SOURCE_MAP: Optional[Dict[str, CanonicalSource]] = None
_CANONICAL_TAG_MAP: Optional[Dict[str, CanonicalSource]] = None


def load_canonical_sources(json_path: Optional[Path] = None) -> List[CanonicalSource]:
    """
    Tải danh mục 44 nguồn chuẩn hóa từ CANONICAL-SOURCES.json.
    HARD FAIL nếu:
    - số lượng != 44
    - thiếu source_key hoặc word_source_tag
    - trùng lặp source_key hoặc word_source_tag
    """
    target_path = json_path if json_path is not None else CANONICAL_SOURCES_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"HARD FAIL: Canonical sources file not found at: {target_path}")

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if len(data) != 44:
        raise ValueError(f"HARD FAIL: Expected exactly 44 canonical sources, found {len(data)}")

    sources: List[CanonicalSource] = []
    seen_keys = set()
    seen_tags = set()

    for entry in data:
        skey = entry.get("source_key")
        stag = entry.get("word_source_tag")

        if not skey:
            raise ValueError(f"HARD FAIL: Entry missing 'source_key': {entry}")
        if not stag:
            raise ValueError(f"HARD FAIL: Entry missing 'word_source_tag': {entry}")

        if skey in seen_keys:
            raise ValueError(f"HARD FAIL: Duplicate source_key '{skey}' in canonical sources")
        if stag in seen_tags:
            raise ValueError(f"HARD FAIL: Duplicate word_source_tag '{stag}' in canonical sources")

        seen_keys.add(skey)
        seen_tags.add(stag)

        sources.append(
            CanonicalSource(
                source_key=skey,
                canonical_title=entry.get("canonical_title", ""),
                canonical_authors=entry.get("canonical_authors", []),
                year=int(entry.get("year", 0)),
                venue=entry.get("venue"),
                publication_type=entry.get("publication_type", ""),
                doi=entry.get("doi"),
                url=entry.get("url"),
                word_source_tag=stag,
                aliases=entry.get("aliases", []),
            )
        )

    return sources


def get_canonical_source_map() -> Dict[str, CanonicalSource]:
    """Trả về từ điển tra cứu nhanh: source_key -> CanonicalSource."""
    global _CANONICAL_SOURCE_MAP
    if _CANONICAL_SOURCE_MAP is None:
        sources = load_canonical_sources()
        _CANONICAL_SOURCE_MAP = {s.source_key: s for s in sources}
    return _CANONICAL_SOURCE_MAP


def get_canonical_tag_map() -> Dict[str, CanonicalSource]:
    """Trả về từ điển tra cứu nhanh: word_source_tag -> CanonicalSource."""
    global _CANONICAL_TAG_MAP
    if _CANONICAL_TAG_MAP is None:
        sources = load_canonical_sources()
        _CANONICAL_TAG_MAP = {s.word_source_tag: s for s in sources}
    return _CANONICAL_TAG_MAP


def latex_to_clean_omml(latex_code: str) -> OxmlElement:
    """Chuyển đổi biểu thức LaTeX thành phần tử Office Math (w:oMath) sạch."""
    clean_code = (
        latex_code.replace(r"\mathbf", "")
        .replace(r"\mathcal", "")
        .replace(r"\mathbb", "")
        .replace(r"\text", "")
        .replace(r"\quad", " ")
        .replace(r"\qquad", "  ")
        .replace(r"\top", "T")
        .replace(r"\mid", "|")
        .replace(r"\_", "_")
        .replace("{", "")
        .replace("}", "")
    )
    omml_xml = (
        f'<m:oMath {nsdecls("m")}>\n'
        '  <m:r>\n'
        '    <m:rPr>\n'
        '      <m:scr m:val="roman"/>\n'
        '      <m:sty m:val="p"/>\n'
        '    </m:rPr>\n'
        f'    <m:t>{escape(clean_code)}</m:t>\n'
        '  </m:r>\n'
        '</m:oMath>'
    )
    return parse_xml(omml_xml)


def make_citation_element(items):
    """
    Tạo các thành phần trường Trích dẫn Word gốc (native Word CITATION fields)
    từ canonical source_key (string).

    CẤM:
    - số nguyên (int)
    - word_source_tag (SRC0000xx) trực tiếp trong builder domain code
    - source_key không tồn tại trong CANONICAL-SOURCES.json
    """
    if isinstance(items, str):
        items = [items]
    elif not isinstance(items, (list, tuple, set)):
        raise TypeError(f"HARD FAIL: make_citation_element expected iterable of str, got {type(items)}")

    s_map = get_canonical_source_map()
    elems = []

    for i, item in enumerate(items):
        if isinstance(item, int):
            raise TypeError(
                f"HARD FAIL: make_citation_element received integer '{item}'. "
                f"Numeric indices are strictly forbidden. Only canonical source_key strings "
                f"(e.g. 'Cheng2024KAIROS') are permitted."
            )
        if not isinstance(item, str):
            raise TypeError(
                f"HARD FAIL: make_citation_element expected str source_key, got {type(item)}: '{item}'"
            )
        if item.startswith("SRC") and re.match(r"^SRC\d+$", item):
            raise ValueError(
                f"HARD FAIL: make_citation_element received word_source_tag '{item}'. "
                f"Direct use of word_source_tag in builder domain code is strictly forbidden. "
                f"Use canonical source_key (e.g. 'Cheng2024KAIROS') instead."
            )
        if item not in s_map:
            raise KeyError(
                f"HARD FAIL: Unknown source_key '{item}' not found in canonical registry CANONICAL-SOURCES.json!"
            )

        src = s_map[item]
        tag = src.word_source_tag
        num_str = str(int(tag.replace("SRC", "")))

        if i > 0:
            sep_xml = (
                f'<w:r {nsdecls("w")}>\n'
                '  <w:rPr>\n'
                '    <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>\n'
                '    <w:sz w:val="28"/>\n'
                '  </w:rPr>\n'
                '  <w:t xml:space="preserve">, </w:t>\n'
                '</w:r>'
            )
            elems.append(parse_xml(sep_xml))

        fld_xml = (
            f'<w:fldSimple {nsdecls("w")} w:instr="CITATION {tag} \\l 1033 ">\n'
            '  <w:r>\n'
            '    <w:rPr>\n'
            '      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>\n'
            '      <w:sz w:val="28"/>\n'
            '    </w:rPr>\n'
            f'    <w:t>[{num_str}]</w:t>\n'
            '  </w:r>\n'
            '</w:fldSimple>'
        )
        elems.append(parse_xml(fld_xml))
    return elems


def make_ref_element(bookmark_name: str, fallback_text: str, font_size_pt: float = 14.0):
    """Tạo phần tử trường tham chiếu chéo động Word REF gốc."""
    sz_val = int(font_size_pt * 2)
    ref_xml = (
        f'<w:fldSimple {nsdecls("w")} w:instr="REF {bookmark_name} \\h ">\n'
        '  <w:r>\n'
        '    <w:rPr>\n'
        '      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>\n'
        f'      <w:sz w:val="{sz_val}"/>\n'
        '    </w:rPr>\n'
        f'    <w:t>{fallback_text}</w:t>\n'
        '  </w:r>\n'
        '</w:fldSimple>'
    )
    return parse_xml(ref_xml)


def add_table_caption(doc, target_p, seq_num: int, title_content, bookmark_name: str = None):
    """Inserts a native Word Caption paragraph with SEQ Bảng field and keepWithNext."""
    cap_p = doc.add_paragraph(style="Caption") if target_p is None else target_p.insert_paragraph_before(style="Caption")
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.space_before = Pt(12)
    cap_p.paragraph_format.space_after = Pt(4)
    cap_p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    cap_p.paragraph_format.keep_with_next = True

    cap_xml = (
        f'<w:pPr {nsdecls("w")}>\n'
        '  <w:pStyle w:val="Caption"/>\n'
        '  <w:jc w:val="center"/>\n'
        '  <w:spacing w:before="240" w:after="80" w:line="360" w:lineRule="auto"/>\n'
        '  <w:keepNext/>\n'
        '</w:pPr>'
    )
    cap_p._p.remove(cap_p._p.pPr)
    cap_p._p.append(parse_xml(cap_xml))

    if bookmark_name:
        cap_p._p.append(parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="20{seq_num}" w:name="{bookmark_name}"/>'))

    r1 = cap_p.add_run(f"Bảng {seq_num//10 if seq_num >= 10 else 1}.")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(14)
    r1.bold = True

    seq_xml = (
        f'<w:fldSimple {nsdecls("w")} w:instr="SEQ Bảng \\* ARABIC ">\n'
        '  <w:r>\n'
        '    <w:rPr>\n'
        '      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>\n'
        '      <w:b/>\n'
        '      <w:sz w:val="28"/>\n'
        '    </w:rPr>\n'
        f'    <w:t>{seq_num % 10 if seq_num >= 10 else seq_num}</w:t>\n'
        '  </w:r>\n'
        '</w:fldSimple>'
    )
    cap_p._p.append(parse_xml(seq_xml))

    if bookmark_name:
        cap_p._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="20{seq_num}"/>'))

    colon_r = cap_p.add_run(": ")
    colon_r.font.name = "Times New Roman"
    colon_r.font.size = Pt(14)
    colon_r.bold = True

    items = [title_content] if isinstance(title_content, str) else title_content
    for item in items:
        if isinstance(item, str):
            r = cap_p.add_run(item)
            r.font.name = "Times New Roman"
            r.font.size = Pt(14)
            r.bold = True
        elif isinstance(item, list):
            for sub in item:
                cap_p._p.append(sub)
        else:
            cap_p._p.append(item)

    return cap_p


def add_figure_caption(doc, target_p, seq_label: str, title_content, bookmark_name: str = None, seq_id: int = 1):
    """Inserts a native Word Caption paragraph with SEQ Hình field placed below the figure."""
    cap_p = doc.add_paragraph(style="Caption") if target_p is None else target_p.insert_paragraph_before(style="Caption")
    cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_p.paragraph_format.space_before = Pt(6)
    cap_p.paragraph_format.space_after = Pt(12)
    cap_p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    cap_xml = (
        f'<w:pPr {nsdecls("w")}>\n'
        '  <w:pStyle w:val="Caption"/>\n'
        '  <w:jc w:val="center"/>\n'
        '  <w:spacing w:before="120" w:after="240" w:line="360" w:lineRule="auto"/>\n'
        '</w:pPr>'
    )
    cap_p._p.remove(cap_p._p.pPr)
    cap_p._p.append(parse_xml(cap_xml))

    if bookmark_name:
        cap_p._p.append(parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="10{seq_id}" w:name="{bookmark_name}"/>'))

    r1 = cap_p.add_run(f"Hình {seq_label.split('.')[0]}.")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(14)
    r1.bold = True

    seq_num = seq_label.split('.')[1] if '.' in seq_label else str(seq_id)
    seq_xml = (
        f'<w:fldSimple {nsdecls("w")} w:instr="SEQ Hình \\* ARABIC ">\n'
        '  <w:r>\n'
        '    <w:rPr>\n'
        '      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>\n'
        '      <w:b/>\n'
        '      <w:sz w:val="28"/>\n'
        '    </w:rPr>\n'
        f'    <w:t>{seq_num}</w:t>\n'
        '  </w:r>\n'
        '</w:fldSimple>'
    )
    cap_p._p.append(parse_xml(seq_xml))

    if bookmark_name:
        cap_p._p.append(parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="10{seq_id}"/>'))

    colon_r = cap_p.add_run(": ")
    colon_r.font.name = "Times New Roman"
    colon_r.font.size = Pt(14)
    colon_r.bold = True

    items = [title_content] if isinstance(title_content, str) else title_content
    for item in items:
        if isinstance(item, str):
            r = cap_p.add_run(item)
            r.font.name = "Times New Roman"
            r.font.size = Pt(14)
            r.bold = True
        elif isinstance(item, list):
            for sub in item:
                cap_p._p.append(sub)
        else:
            cap_p._p.append(item)

    return cap_p


def format_table_cell(cell, width_dxa: int, align=WD_ALIGN_PARAGRAPH.LEFT, bold=False, font_size_pt=14):
    """Đặt các thuộc tính ô tiêu chuẩn: chiều rộng chính xác, căn giữa theo chiều dọc, đường viền, phần đệm và khoảng cách dòng nhỏ gọn."""
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


def insert_clean_table(doc, target_p, headers, rows_data, col_widths, font_size_pt=13):
    """Tạo một bảng có đường viền rõ ràng được chèn trước target_p."""
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers)) if target_p is None else target_p.insert_paragraph_before()._p.addprevious(parse_xml(f'<w:tbl {nsdecls("w")}/>'))
    if target_p is not None:
        tbl = docx.table.Table(tbl, doc)

    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_pr = tbl._tbl.tblPr
    tbl_pr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="0" w:type="auto"/>'))
    tbl_pr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}>\n  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n  <w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n  <w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n  <w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n</w:tblBorders>'))

    hdr_row = tbl.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

    for c_i, h in enumerate(headers):
        cell = hdr_row.cells[c_i]
        cell.text = h
        format_table_cell(cell, col_widths[c_i], align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, font_size_pt=font_size_pt)

    for r_i, row in enumerate(rows_data):
        b_row = tbl.rows[r_i + 1]
        b_trPr = b_row._tr.get_or_add_trPr()
        b_trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

        for c_i, val in enumerate(row):
            cell = b_row.cells[c_i]
            cell.text = val
            cell_align = WD_ALIGN_PARAGRAPH.CENTER if (c_i == 0 and len(headers) >= 4) else WD_ALIGN_PARAGRAPH.LEFT
            format_table_cell(cell, col_widths[c_i], align=cell_align, bold=(c_i == 0 and len(headers) == 3), font_size_pt=font_size_pt)


def generate_perfect_sources_xml(sources=None):
    """Tạo các Nguồn thư mục Microsoft Word hợp lệ CustomXML với kiểu Tác giả doanh nghiệp & IEEE."""
    if sources is None:
        sources = load_canonical_sources()

    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>']
    lines.append('<b:Sources SelectedStyle="\\IEEE.XSL" StyleName="IEEE" xmlns:b="http://schemas.openxmlformats.org/officeDocument/2006/bibliography" xmlns="http://schemas.openxmlformats.org/officeDocument/2006/bibliography">')

    corporate_map = {
        "SRC000001": "MITRE ATT&CK",
        "SRC000027": "National Institute of Standards and Technology (NIST)",
        "SRC000028": "Defense Advanced Research Projects Agency (DARPA)",
        "SRC-000001": "MITRE ATT&CK",
        "SRC-000027": "National Institute of Standards and Technology (NIST)",
        "SRC-000028": "Defense Advanced Research Projects Agency (DARPA)",
    }

    for s in sources:
        tag = getattr(s, "word_source_tag", None) or getattr(s, "source_id", "")
        clean_tag = tag.replace("-", "")
        venue = getattr(s, "venue", "") or ""
        title = getattr(s, "canonical_title", None) or getattr(s, "title", "")
        year = getattr(s, "year", "")
        authors = getattr(s, "canonical_authors", None) or getattr(s, "authors", [])

        if any(w in venue for w in ["Proceedings", "Conference", "Symposium", "NDSS", "S&P", "CCS", "ICLR", "ICML", "ACSAC", "ISSTA", "ISSRE", "ASE", "IJCNN", "KDD", "IJCAI", "ICDM", "SOSP", "ATC", "USENIX"]):
            stype = "ConferenceProceedings"
        elif any(w in venue for w in ["Journal", "Surveys", "IEEE Transactions", "ACM"]):
            stype = "ArticleInAPeriodical"
        elif "Standard" in venue or "NIST" in venue or "DARPA" in venue or "LANL" in venue:
            stype = "Report"
        elif "arxiv" in venue.lower():
            stype = "InternetSite"
        else:
            stype = "Report"

        guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"thesis.sources.{clean_tag}")).upper()

        lines.append("  <b:Source>")
        lines.append(f"    <b:Tag>{clean_tag}</b:Tag>")
        lines.append(f"    <b:SourceType>{stype}</b:SourceType>")
        lines.append(f"    <b:Guid>{{{guid}}}</b:Guid>")
        lines.append(f"    <b:Title>{escape(title)}</b:Title>")
        lines.append(f"    <b:Year>{year}</b:Year>")
        if stype == "ConferenceProceedings":
            lines.append(f"    <b:ConferenceName>{escape(venue)}</b:ConferenceName>")
        elif stype == "ArticleInAPeriodical":
            lines.append(f"    <b:JournalName>{escape(venue)}</b:JournalName>")
        elif stype == "InternetSite":
            lines.append(f"    <b:InternetSiteTitle>{escape(venue)}</b:InternetSiteTitle>")
        else:
            lines.append(f"    <b:Institution>{escape(venue)}</b:Institution>")

        if tag in corporate_map or clean_tag in corporate_map:
            corp_name = corporate_map.get(tag) or corporate_map.get(clean_tag)
            lines.append("    <b:Author>")
            lines.append("      <b:Author>")
            lines.append(f"        <b:Corporate>{escape(corp_name)}</b:Corporate>")
            lines.append("      </b:Author>")
            lines.append("    </b:Author>")
        elif tag in ["SRC000029", "SRC-000029"] or clean_tag == "SRC000029":
            lines.append("    <b:Author>")
            lines.append("      <b:Author>")
            lines.append("        <b:NameList>")
            lines.append("          <b:Person><b:Last>Kent</b:Last><b:First>Alexander D.</b:First></b:Person>")
            lines.append("        </b:NameList>")
            lines.append("      </b:Author>")
            lines.append("    </b:Author>")
            lines.append("    <b:Institution>Los Alamos National Laboratory</b:Institution>")
        else:
            lines.append("    <b:Author>")
            lines.append("      <b:Author>")
            lines.append("        <b:NameList>")
            for author_name in authors:
                parts = author_name.strip().split()
                if len(parts) > 1:
                    first = " ".join(parts[:-1])
                    last = parts[-1]
                    lines.append(f"          <b:Person><b:Last>{escape(last)}</b:Last><b:First>{escape(first)}</b:First></b:Person>")
                else:
                    lines.append(f"          <b:Person><b:Last>{escape(author_name)}</b:Last></b:Person>")
            lines.append("        </b:NameList>")
            lines.append("      </b:Author>")
            lines.append("    </b:Author>")

        lines.append("  </b:Source>")

    lines.append("</b:Sources>")
    return "\n".join(lines)
