"""
Word Native Cross-Reference Manager (Rule 5)
Provides native Microsoft Word REF field cross-references linking narrative text to Figure/Table bookmarks.
Enforces:
- No hardcoded plaintext references like 'xem Hình 2.3'
- Generates native <w:fldSimple w:instr="REF BK_xxx \\h "> elements
- Updates dynamically when Word updates fields (Ctrl+A -> F9).
"""

from typing import Optional, Union
import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls


class WordCrossReferenceManager:
    """
    Manages native Word REF dynamic cross-reference fields.
    """

    @staticmethod
    def create_ref_element(
        bookmark_name: str,
        fallback_text: str = "Hình",
        font_name: str = "Times New Roman",
        font_size_pt: float = 14.0,
    ):
        r"""
        Creates an XML element for a native Word REF field with hyperlink switch (\h).
        """
        sz_val = int(font_size_pt * 2)
        ref_xml = (
            f'<w:fldSimple {nsdecls("w")} w:instr="REF {bookmark_name} \\h ">\n'
            '  <w:r>\n'
            '    <w:rPr>\n'
            f'      <w:rFonts w:ascii="{font_name}" w:hAnsi="{font_name}"/>\n'
            f'      <w:sz w:val="{sz_val}"/>\n'
            '    </w:rPr>\n'
            f'    <w:t>{fallback_text}</w:t>\n'
            '  </w:r>\n'
            '</w:fldSimple>'
        )
        return parse_xml(ref_xml)

    @classmethod
    def append_cross_reference_to_paragraph(
        cls,
        paragraph: docx.text.paragraph.Paragraph,
        prefix_text: str,
        bookmark_name: str,
        fallback_target_text: str,
        suffix_text: str = "",
        font_size_pt: float = 14.0,
    ):
        """
        Appends text with an embedded native cross-reference field into a paragraph.
        Example: prefix_text="kết quả được trình bày trong ", bookmark_name="BK_TBL_001", fallback="Bảng 1.1", suffix_text="."
        """
        if prefix_text:
            r_pre = paragraph.add_run(prefix_text)
            r_pre.font.name = "Times New Roman"
            r_pre.font.size = docx.shared.Pt(font_size_pt)

        ref_elem = cls.create_ref_element(
            bookmark_name=bookmark_name,
            fallback_text=fallback_target_text,
            font_size_pt=font_size_pt,
        )
        paragraph._p.append(ref_elem)

        if suffix_text:
            r_post = paragraph.add_run(suffix_text)
            r_post.font.name = "Times New Roman"
            r_post.font.size = docx.shared.Pt(font_size_pt)
