# -*- coding: utf-8 -*-
"""
Synchronize Word customXml/item1.xml in Chuyên đề chuyên sâu.docx from CANONICAL-SOURCES.json
Preserving exact Word GUIDs, SourceTypes, RefOrders, and schema-compliant Author structures.
"""
import sys
import json
import zipfile
import io
from pathlib import Path
from xml.sax.saxutils import escape

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
canonical_json_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"
backup_info_path = repo_root / "scripts" / "backup_sources_info.json"

def generate_sources_xml(canonical_sources, backup_info):
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<b:Sources SelectedStyle="\\IEEE.XSL" xmlns:b="http://schemas.openxmlformats.org/officeDocument/2006/bibliography" xmlns="http://schemas.openxmlformats.org/officeDocument/2006/bibliography">')

    for s in canonical_sources:
        tag = s["word_source_tag"]
        title = s["canonical_title"]
        year = s["year"]
        venue = s.get("venue", "")
        doi = s.get("doi")
        url = s.get("url")
        authors = s["canonical_authors"]

        b_entry = backup_info.get(tag, {})
        stype = b_entry.get("sourcetype") or "ConferenceProceedings"
        guid = b_entry.get("guid") or "{00000000-0000-0000-0000-000000000000}"
        ref_order = b_entry.get("reforder")
        institution = b_entry.get("institution") or venue

        lines.append("  <b:Source>")
        lines.append(f"    <b:Tag>{tag}</b:Tag>")
        lines.append(f"    <b:SourceType>{stype}</b:SourceType>")
        lines.append(f"    <b:Guid>{guid}</b:Guid>")
        lines.append(f"    <b:Title>{escape(title)}</b:Title>")
        lines.append(f"    <b:Year>{year}</b:Year>")

        if stype == "ConferenceProceedings":
            lines.append(f"    <b:ConferenceName>{escape(venue)}</b:ConferenceName>")
        elif stype == "ArticleInAPeriodical":
            lines.append(f"    <b:JournalName>{escape(venue)}</b:JournalName>")
        elif stype == "InternetSite":
            lines.append(f"    <b:InternetSiteTitle>{escape(venue)}</b:InternetSiteTitle>")
        elif stype == "Report":
            lines.append(f"    <b:Institution>{escape(institution)}</b:Institution>")
        else:
            lines.append(f"    <b:Institution>{escape(venue)}</b:Institution>")

        if url:
            lines.append(f"    <b:URL>{escape(url)}</b:URL>")
        if doi:
            lines.append(f"    <b:DOI>{escape(doi)}</b:DOI>")

        # Authors
        lines.append("    <b:Author>")
        lines.append("      <b:Author>")
        lines.append("        <b:NameList>")
        for author_name in authors:
            if author_name == "MITRE Corporation":
                lines.append(f"          <b:Person><b:Last>MITRE Corporation</b:Last></b:Person>")
            elif "DARPA" in author_name:
                lines.append(f"          <b:Person><b:Last>DARPA/I2O</b:Last><b:First>Defense Advanced Research Projects Agency</b:First></b:Person>")
            else:
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

        if ref_order:
            lines.append(f"    <b:RefOrder>{ref_order}</b:RefOrder>")

        lines.append("  </b:Source>")

    lines.append("</b:Sources>")
    return "\n".join(lines)

def sync_docx_customxml():
    with open(canonical_json_path, "r", encoding="utf-8") as f:
        canonical_sources = json.load(f)
    with open(backup_info_path, "r", encoding="utf-8") as f:
        backup_info = json.load(f)

    new_xml_str = generate_sources_xml(canonical_sources, backup_info)
    new_xml_bytes = new_xml_str.encode("utf-8")

    # Read existing docx zip
    with open(docx_path, "rb") as f:
        in_mem = io.BytesIO(f.read())

    in_zip = zipfile.ZipFile(in_mem, "r")
    out_mem = io.BytesIO()
    out_zip = zipfile.ZipFile(out_mem, "w", zipfile.ZIP_DEFLATED)

    for item in in_zip.infolist():
        if item.filename == "customXml/item1.xml":
            out_zip.writestr(item, new_xml_bytes)
        else:
            out_zip.writestr(item, in_zip.read(item.filename))

    in_zip.close()
    out_zip.close()

    # Overwrite docx
    with open(docx_path, "wb") as f:
        f.write(out_mem.getvalue())

    print(f"Successfully synchronized customXml/item1.xml in {docx_path} with {len(canonical_sources)} canonical sources.")

if __name__ == "__main__":
    sync_docx_customxml()
