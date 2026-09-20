import sys
import zipfile
import io
import xml.etree.ElementTree as ET
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
canonical_json_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"

def inspect_fields():
    with open(canonical_json_path, "r", encoding="utf-8") as f:
        canonical = json.load(f)
    tag_to_skey = {c["word_source_tag"]: c["source_key"] for c in canonical}

    with open(docx_path, "rb") as f:
        z = zipfile.ZipFile(io.BytesIO(f.read()))

    doc_xml = z.read("word/document.xml")
    root = ET.fromstring(doc_xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

    # Count fields by type
    field_counts = {
        "CITATION": 0,
        "BIBLIOGRAPHY": 0,
        "TOC": 0,
        "PAGEREF": 0,
        "REF": 0,
        "SEQ": 0,
        "other": 0
    }

    citation_details = []

    # Iterate paragraphs to capture complex fields and simple fields
    for p_idx, p in enumerate(root.findall(".//w:p", ns)):
        # Check fldSimple
        for fs in p.findall(".//w:fldSimple", ns):
            instr = fs.attrib.get(f"{{{ns['w']}}}instr", "").strip()
            first_word = instr.split()[0] if instr else "other"
            if first_word in field_counts:
                field_counts[first_word] += 1
            else:
                field_counts["other"] += 1

            if first_word == "CITATION":
                tag = instr.replace("CITATION", "").replace(r"\l 1033", "").strip()
                rendered = "".join(fs.itertext()).strip()
                skey = tag_to_skey.get(tag, "UNRESOLVED_TAG")
                citation_details.append({
                    "paragraph_index": p_idx,
                    "source_tag": tag,
                    "rendered_number": rendered,
                    "canonical_source_key": skey
                })

        # Check complex fields
        runs = p.findall(".//w:r", ns)
        i = 0
        while i < len(runs):
            r = runs[i]
            fld_char = r.find(".//w:fldChar", ns)
            if fld_char is not None and fld_char.attrib.get(f"{{{ns['w']}}}fldCharType") == "begin":
                # Collect instrText until separate or end
                instr_parts = []
                j = i + 1
                while j < len(runs):
                    r_next = runs[j]
                    it = r_next.find(".//w:instrText", ns)
                    if it is not None and it.text:
                        instr_parts.append(it.text)
                    fc_next = r_next.find(".//w:fldChar", ns)
                    if fc_next is not None and fc_next.attrib.get(f"{{{ns['w']}}}fldCharType") in ["separate", "end"]:
                        break
                    j += 1

                instr_str = "".join(instr_parts).strip()
                first_word = instr_str.split()[0] if instr_str else "other"
                if first_word in field_counts:
                    field_counts[first_word] += 1
                else:
                    field_counts["other"] += 1

                # If separate, collect rendered text until end
                rendered_parts = []
                if j < len(runs) and runs[j].find(".//w:fldChar", ns).attrib.get(f"{{{ns['w']}}}fldCharType") == "separate":
                    k = j + 1
                    while k < len(runs):
                        r_k = runs[k]
                        fc_k = r_k.find(".//w:fldChar", ns)
                        if fc_k is not None and fc_k.attrib.get(f"{{{ns['w']}}}fldCharType") == "end":
                            break
                        rendered_parts.extend(r_k.itertext())
                        k += 1
                    i = k
                else:
                    i = j

                rendered_str = "".join(rendered_parts).strip()

                if first_word == "CITATION":
                    tag = instr_str.replace("CITATION", "").replace(r"\l 1033", "").strip()
                    skey = tag_to_skey.get(tag, "UNRESOLVED_TAG")
                    citation_details.append({
                        "paragraph_index": p_idx,
                        "source_tag": tag,
                        "rendered_number": rendered_str,
                        "canonical_source_key": skey
                    })
            i += 1

    print("[FIELD-INSPECTION] Summary of Word Fields:")
    for k, v in field_counts.items():
        print(f"  - {k}: {v}")

    unresolved = [c for c in citation_details if c["canonical_source_key"] == "UNRESOLVED_TAG"]
    print(f"\nTotal CITATION fields: {len(citation_details)}")
    print(f"Unresolved CITATION tags: {len(unresolved)}")

    return field_counts, citation_details

if __name__ == "__main__":
    inspect_fields()
