from __future__ import annotations

import argparse
import copy
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree
import pythoncom
import win32com.client as win32

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from research_agent.visuals.chapter2_drawings import draw_fig_2_2, draw_fig_2_3, draw_fig_2_4

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def text_of(paragraph: etree._Element) -> str:
    return "".join(paragraph.xpath(".//w:t/text()", namespaces=NS))


def field_paragraph(instruction: str) -> etree._Element:
    paragraph = etree.Element(qn("p"))
    field = etree.SubElement(paragraph, qn("fldSimple"))
    field.set(qn("instr"), instruction)
    run = etree.SubElement(field, qn("r"))
    etree.SubElement(run, qn("t")).text = ""
    return paragraph


def heading_paragraph(text: str) -> etree._Element:
    paragraph = etree.Element(qn("p"))
    ppr = etree.SubElement(paragraph, qn("pPr"))
    etree.SubElement(ppr, qn("pStyle")).set(qn("val"), "UH1")
    run = etree.SubElement(paragraph, qn("r"))
    etree.SubElement(run, qn("t")).text = text
    return paragraph


def drawing_from_temp(draw_fn) -> etree._Element:
    temp_dir = Path(tempfile.mkdtemp(prefix="recovery_shapes_"))
    temp_docx = temp_dir / "shape.docx"
    pythoncom.CoInitialize()
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Add()
        anchor = doc.Paragraphs(1).Range
        canvas = doc.Shapes.AddCanvas(0, 0, 450, 160, anchor)
        draw_fn(canvas)
        canvas.ConvertToInlineShape()
        doc.SaveAs2(str(temp_docx))
        doc.Close(False)
    finally:
        word.Quit()
        pythoncom.CoUninitialize()
    with zipfile.ZipFile(temp_docx) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
    drawing = root.xpath(".//w:drawing", namespaces=NS)[0]
    return copy.deepcopy(drawing)


def replace_zip_member(docx: Path, document_xml: bytes) -> None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=docx.parent) as tmp:
        temp_path = Path(tmp.name)
    try:
        with zipfile.ZipFile(docx, "r") as source:
            with zipfile.ZipFile(temp_path, "w", zipfile.ZIP_DEFLATED) as target:
                for info in source.infolist():
                    target.writestr(info, document_xml if info.filename == "word/document.xml" else source.read(info.filename))
        temp_path.replace(docx)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    args = parser.parse_args()
    with zipfile.ZipFile(args.docx) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))

    body = root.find("w:body", NS)
    labels = {
        "MỤC LỤC": 'TOC \\o "1-3" \\h \\z \\u',
        "DANH MỤC HÌNH VẼ": 'TOF \\h \\c "Hình"',
        "DANH MỤC BẢNG": 'TOF \\h \\c "Bảng"',
    }
    for paragraph in list(body.findall("w:p", NS)):
        label = text_of(paragraph).strip()
        if label in labels:
            body.insert(body.index(paragraph) + 1, field_paragraph(labels[label]))

    body.append(heading_paragraph("TÀI LIỆU THAM KHẢO"))
    body.append(field_paragraph("BIBLIOGRAPHY \\l 1033"))

    drawings = {
        "BK_FIG_2_002_CANVAS": drawing_from_temp(draw_fig_2_2),
        "BK_FIG_2_003_CANVAS": drawing_from_temp(draw_fig_2_3),
        "BK_FIG_2_004_CANVAS": drawing_from_temp(draw_fig_2_4),
    }
    for name, drawing in drawings.items():
        marker = root.xpath(f'.//w:bookmarkStart[@w:name="{name}"]', namespaces=NS)
        if len(marker) != 1:
            raise RuntimeError(f"Expected one canvas bookmark for {name}, found {len(marker)}")
        paragraph = marker[0].getparent()
        run = etree.Element(qn("r"))
        run.append(drawing)
        paragraph.append(run)

    replace_zip_member(args.docx, etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True))
    print("Inserted native TOC/TOF/BIBLIOGRAPHY field codes and 3 native vector drawings.")


if __name__ == "__main__":
    main()
