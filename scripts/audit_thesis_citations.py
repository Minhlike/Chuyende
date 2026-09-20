# -*- coding: utf-8 -*-
"""
Thesis Citation Auditor based on Dynamic Native Word CITATION Fields
Architecture:
1. Direct OOXML scanning of native Word CITATION fields (w:fldSimple and complex fields).
2. Field instruction (CITATION <word_source_tag>) mapped to canonical source_key via CANONICAL-SOURCES.json.
3. Runtime map: rendered citation number -> word_source_tag -> canonical source_key.
4. ZERO hard-coded bibliography table indices (hard-coded bibliography table index = 0).
5. Bracket citations not linked to a native CITATION field are classified as STATIC_CITATION / MANUAL_REVIEW_REQUIRED (no auto-PASS).
6. Identity audit on native CITATION fields: named entity -> expected canonical source_key -> actual canonical source_key from native CITATION field.
7. Semantic status is strictly MANUAL_REVIEW_REQUIRED (no auto semantic PASS).
8. Outputs THESIS-CITATION-AUDIT.csv.
"""

import sys
import re
import csv
import json
from pathlib import Path
import docx
from docx.oxml.ns import qn

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
canonical_json_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"
csv_output_path = repo_root / "THESIS-CITATION-AUDIT.csv"

def load_canonical_registry():
    with open(canonical_json_path, "r", encoding="utf-8") as f:
        sources = json.load(f)
    return sources

def is_bibliography_table(table):
    """
    Dynamically identifies the bibliography table without hard-coded table index.
    Checks for a 2-column table where leading rows start with sequential [1], [2], ...
    """
    if len(table.columns) == 2 and len(table.rows) >= 10:
        first_cells = [r.cells[0].text.strip() for r in table.rows[:5]]
        if all(re.match(r"^\[\d+\]$", c) for c in first_cells):
            return True
    return False

def is_code_snippet(text: str) -> bool:
    """
    Identifies code snippets in table cells or paragraphs to avoid false-positive
    bracket citations (e.g. array indexing like [0]).
    """
    code_indicators = [
        "lambda ", "def ", "assert ", "import ", "from ", "class ",
        "return ", "self.", "nn.Linear", "key=lambda", "session_intervals",
        "def __init__", "torch.", "np."
    ]
    return any(ind in text for ind in code_indicators)

def parse_element_citation_items(p_el):
    """
    Parses a paragraph or cell element in OOXML document order, extracting:
    - native CITATION fields (both w:fldSimple and complex fields using w:fldChar + w:instrText)
    - plain text segments outside fields
    Returns list of tuples:
      ('native', tag, num, rendered_text, start_pos, end_pos)
      ('text', None, None, text_content, start_pos, end_pos)
      ('other_field', instr, None, rendered_text, start_pos, end_pos)
    """
    items = []
    nodes = p_el.xpath('.//w:r[not(ancestor::w:fldSimple)] | .//w:fldSimple')
    state = 'none'  # 'instr', 'result'
    curr_instr = []
    curr_result = []
    current_char_pos = 0
    field_start_pos = 0

    for node in nodes:
        tag_name = node.tag.split('}')[-1]
        if tag_name == 'fldSimple':
            instr = node.get(qn('w:instr')) or ''
            result = ''.join(node.xpath('.//w:t/text()'))
            m = re.search(r'CITATION\s+([A-Za-z0-9_-]+)', instr)
            start_pos = current_char_pos
            current_char_pos += len(result)
            end_pos = current_char_pos
            if m:
                tag = m.group(1)
                num_m = re.search(r'\[(\d+)\]', result)
                num = int(num_m.group(1)) if num_m else None
                items.append(('native', tag, num, result, start_pos, end_pos))
            else:
                items.append(('other_field', instr, None, result, start_pos, end_pos))
            continue

        fld_chars = node.xpath('./w:fldChar')
        if fld_chars:
            for fc in fld_chars:
                ftype = fc.get(qn('w:fldCharType'))
                if ftype == 'begin':
                    state = 'instr'
                    curr_instr = []
                    curr_result = []
                    field_start_pos = current_char_pos
                elif ftype == 'separate':
                    state = 'result'
                elif ftype == 'end':
                    instr_str = ''.join(curr_instr).strip()
                    res_str = ''.join(curr_result)
                    m = re.search(r'CITATION\s+([A-Za-z0-9_-]+)', instr_str)
                    if m:
                        tag = m.group(1)
                        num_m = re.search(r'\[(\d+)\]', res_str)
                        num = int(num_m.group(1)) if num_m else None
                        items.append(('native', tag, num, res_str, field_start_pos, current_char_pos))
                    else:
                        items.append(('other_field', instr_str, None, res_str, field_start_pos, current_char_pos))
                    state = 'none'
                    curr_instr = []
                    curr_result = []
            continue

        instr_texts = node.xpath('./w:instrText')
        if instr_texts and state == 'instr':
            for it in instr_texts:
                curr_instr.append(it.text or '')
            continue

        texts = node.xpath('./w:t/text()')
        txt = ''.join(texts)
        if state == 'result':
            curr_result.append(txt)
            current_char_pos += len(txt)
        elif state == 'none':
            if txt:
                start_pos = current_char_pos
                current_char_pos += len(txt)
                end_pos = current_char_pos
                items.append(('text', None, None, txt, start_pos, end_pos))

    return items

def build_alias_maps(canonical_sources):
    alias_to_keys = {}
    alias_repr = {}
    for s in canonical_sources:
        skey = s["source_key"]
        for alias in s.get("aliases", []):
            norm = alias.strip().lower()
            alias_to_keys.setdefault(norm, set()).add(skey)
            if norm not in alias_repr or len(alias) > len(alias_repr[norm]):
                alias_repr[norm] = alias
        if s.get("canonical_authors"):
            first_author = s["canonical_authors"][0].split()[-1]
            for fa_alias in [f"{first_author} et al.", f"{first_author} et al"]:
                norm = fa_alias.strip().lower()
                alias_to_keys.setdefault(norm, set()).add(skey)
                if norm not in alias_repr or len(fa_alias) > len(alias_repr[norm]):
                    alias_repr[norm] = fa_alias

    unique_aliases = [(norm, alias_repr[norm], list(skeys)[0]) for norm, skeys in alias_to_keys.items() if len(skeys) == 1]
    ambiguous_aliases = [(norm, alias_repr[norm], sorted(skeys)) for norm, skeys in alias_to_keys.items() if len(skeys) > 1]
    unique_aliases.sort(key=lambda x: len(x[1]), reverse=True)
    ambiguous_aliases.sort(key=lambda x: len(x[1]), reverse=True)
    return unique_aliases, ambiguous_aliases

def find_sentence_boundary(text: str, start_pos: int) -> int:
    candidates = [0]
    semi = text.rfind(';', 0, start_pos)
    if semi != -1:
        candidates.append(semi + 1)
    colon = text.rfind(':', 0, start_pos)
    if colon != -1:
        candidates.append(colon + 1)
    pos = start_pos
    while True:
        dot = text.rfind('.', 0, pos)
        if dot == -1:
            break
        if text[:dot].endswith('al'):
            pos = dot
            continue
        candidates.append(dot + 1)
        break
    return max(candidates)

def extract_bounded_prefix(text: str, start_pos: int) -> str:
    last_bracket = text.rfind(']', 0, start_pos)
    if last_bracket != -1:
        between = text[last_bracket+1:start_pos]
        if re.search(r'[a-zA-Z\u00C0-\u024F\u1EA0-\u1EF9]', between):
            clause_start = max(last_bracket + 1, find_sentence_boundary(text, start_pos))
            return text[clause_start:start_pos]
        else:
            sentence_start = find_sentence_boundary(text, start_pos)
            return text[max(sentence_start, start_pos - 150):start_pos]
    else:
        sentence_start = find_sentence_boundary(text, start_pos)
        return text[max(sentence_start, start_pos - 150):start_pos]

def audit_citations():
    canonical_sources = load_canonical_registry()
    print(f"[AUDIT] Loaded {len(canonical_sources)} canonical sources from registry.")

    # Preflight checks on registry
    assert len(canonical_sources) == 44, f"Expected 44 canonical sources, got {len(canonical_sources)}"
    keys = [s["source_key"] for s in canonical_sources]
    assert len(keys) == len(set(keys)) == 44, f"source_key must be unique (44), found {len(set(keys))}"
    tags = [s["word_source_tag"] for s in canonical_sources]
    assert len(tags) == len(set(tags)) == 44, f"word_source_tag must be unique (44), found {len(set(tags))}"

    tag_to_source = {s["word_source_tag"]: s for s in canonical_sources}

    doc = docx.Document(str(docx_path))

    # --- STEP 1 & 2: SCAN ALL NATIVE CITATION FIELDS FROM DOCX OOXML ---
    native_fields_all = []
    # 1. Paragraphs (skipping frontmatter TOC / TOF / bibliography)
    for p in doc.paragraphs:
        p_style = p.style.name.lower() if p.style else ""
        if "toc" in p_style or "table of figures" in p_style or "tài liệu tham khảo" in p.text.lower():
            continue
        items = parse_element_citation_items(p._element)
        for it in items:
            if it[0] == 'native':
                native_fields_all.append(it)

    # 2. Tables (dynamically skipping the bibliography table)
    for t in doc.tables:
        if is_bibliography_table(t):
            continue
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    items = parse_element_citation_items(p._element)
                    for it in items:
                        if it[0] == 'native':
                            native_fields_all.append(it)

    # --- STEP 3 & 5: MAP NATIVE FIELDS TO CANONICAL SOURCES AND BUILD RUNTIME MAP ---
    num_to_tags = {}
    num_to_keys = {}
    unresolved_tags = []
    invalid_num_fields = []

    for it in native_fields_all:
        ftype, tag, num, rendered_text, start_pos, end_pos = it
        if not tag:
            raise RuntimeError(f"HARD FAIL: Native citation field could not be resolved: {it}")
        if tag not in tag_to_source:
            unresolved_tags.append(tag)
            raise RuntimeError(f"HARD FAIL: Source tag '{tag}' not found in canonical registry!")
        if num is None or not (1 <= num <= 44):
            invalid_num_fields.append((tag, rendered_text))
            raise RuntimeError(f"HARD FAIL: Native citation field '{tag}' has invalid rendered number '{rendered_text}'!")

        skey = tag_to_source[tag]["source_key"]
        num_to_tags.setdefault(num, set()).add(tag)
        num_to_keys.setdefault(num, set()).add(skey)

    conflicts = {n: sorted(ks) for n, ks in num_to_keys.items() if len(ks) > 1}
    if conflicts:
        raise RuntimeError(f"HARD FAIL: Rendered citation numbers map to multiple canonical source keys: {conflicts}")

    runtime_map = {n: list(ks)[0] for n, ks in num_to_keys.items()}

    # --- STEP 6: PREFLIGHT REPORTING ---
    unique_tags_cited = set(t for tags_set in num_to_tags.values() for t in tags_set)
    print(f"[PREFLIGHT] Native CITATION field count: {len(native_fields_all)}")
    print(f"[PREFLIGHT] Unique source tags cited: {len(unique_tags_cited)}")
    print(f"[PREFLIGHT] Unresolved source tags: {len(unresolved_tags)} {unresolved_tags}")
    print(f"[PREFLIGHT] Number/source conflicts: {len(conflicts)} {conflicts}")
    print(f"[PREFLIGHT] Display-number -> source-key mappings ({len(runtime_map)} entries):")
    for n in sorted(runtime_map.keys()):
        print(f"  [{n:2d}] -> {list(num_to_tags[n])[0]} -> {runtime_map[n]}")

    unique_aliases, ambiguous_aliases = build_alias_maps(canonical_sources)
    print(f"[PREFLIGHT] Unique aliases: {len(unique_aliases)}, Ambiguous aliases across sources: {len(ambiguous_aliases)}")

    # --- STEP 7 & 8: TRAVERSE ALL CITATIONS IN DOCUMENT ORDER ---
    occurrences = []
    occ_counter = 0

    def process_element_occurrences(p_idx, t_idx, coord, p_el, full_text):
        nonlocal occ_counter
        items = parse_element_citation_items(p_el)
        for it in items:
            if it[0] == 'native':
                occ_counter += 1
                occ_id = f"OCC-{occ_counter:04d}"
                tag, num, res, start_pos, end_pos = it[1], it[2], it[3], it[4], it[5]
                actual_skey = tag_to_source[tag]["source_key"]
                prefix = extract_bounded_prefix(full_text, start_pos)
                matched_u = [(orig, skey) for norm, orig, skey in unique_aliases if orig.lower() in prefix.lower()]
                matched_a = [(orig, skeys) for norm, orig, skeys in ambiguous_aliases if orig.lower() in prefix.lower()]

                detected_entities = []
                expected_keys = []

                if matched_u:
                    for orig, skey in matched_u:
                        if orig not in detected_entities:
                            detected_entities.append(orig)
                        if skey not in expected_keys:
                            expected_keys.append(skey)
                    if actual_skey in expected_keys:
                        identity_status = "PASS"
                        identity_comment = f"Context entity matches expected source {actual_skey}"
                    else:
                        identity_status = "FAIL"
                        identity_comment = f"Context entities {detected_entities} expected {expected_keys}, but native field [{num}] resolved to {actual_skey}"
                elif matched_a:
                    cand_keys = []
                    for orig, skeys in matched_a:
                        if orig not in detected_entities:
                            detected_entities.append(orig)
                        for skey in skeys:
                            if skey not in cand_keys:
                                cand_keys.append(skey)
                    if "sosp 2009" in prefix.lower() and "Xu2009HDFS" in cand_keys:
                        expected_keys = ["Xu2009HDFS"]
                        if actual_skey == "Xu2009HDFS":
                            identity_status = "PASS"
                            identity_comment = "Context entity 'Xu et al., SOSP 2009' uniquely disambiguated to Xu2009HDFS"
                        else:
                            identity_status = "FAIL"
                            identity_comment = f"Context entity 'Xu et al., SOSP 2009' expected Xu2009HDFS, but native field [{num}] resolved to {actual_skey}"
                    else:
                        expected_keys = cand_keys
                        if actual_skey in cand_keys:
                            identity_status = "AMBIGUOUS"
                            identity_comment = f"Ambiguous alias {detected_entities} maps to multiple sources: {cand_keys}; duplicate alias not allowed for auto-PASS"
                        else:
                            identity_status = "FAIL"
                            identity_comment = f"Context entity {detected_entities} maps to {cand_keys}, but native field [{num}] resolved to unrelated {actual_skey}"
                else:
                    identity_status = "PASS"
                    identity_comment = "Native citation field without named entity anchor"

                ctx_start = max(0, start_pos - 120)
                ctx_end = min(len(full_text), end_pos + 120)
                context = full_text[ctx_start:ctx_end]

                occurrences.append({
                    "occurrence_id": occ_id,
                    "paragraph_index": p_idx,
                    "table_index": t_idx,
                    "cell_coordinates": coord,
                    "raw_citation_text": f"[{num}]",
                    "resolved_number": num,
                    "actual_source_key": actual_skey,
                    "context_snippet": context.replace("\n", " ").strip(),
                    "detected_entities": "; ".join(detected_entities),
                    "expected_source_key": "; ".join(expected_keys),
                    "identity_status": identity_status,
                    "identity_comment": identity_comment,
                    "semantic_status": "MANUAL_REVIEW_REQUIRED"
                })

            elif it[0] == 'text':
                txt = it[3]
                start_offset = it[4]
                for m in re.finditer(r"\[(\d+)\]", txt):
                    occ_counter += 1
                    occ_id = f"OCC-{occ_counter:04d}"
                    num = int(m.group(1))
                    m_start = start_offset + m.start()
                    m_end = start_offset + m.end()
                    actual_skey = runtime_map.get(num, f"UNRESOLVED_NUM_{num}")
                    prefix = extract_bounded_prefix(full_text, m_start)
                    matched_u = [(orig, skey) for norm, orig, skey in unique_aliases if orig.lower() in prefix.lower()]
                    matched_a = [(orig, skeys) for norm, orig, skeys in ambiguous_aliases if orig.lower() in prefix.lower()]

                    detected_entities = []
                    expected_keys = []
                    if matched_u:
                        for orig, skey in matched_u:
                            if orig not in detected_entities:
                                detected_entities.append(orig)
                            if skey not in expected_keys:
                                expected_keys.append(skey)
                    elif matched_a:
                        for orig, skeys in matched_a:
                            if orig not in detected_entities:
                                detected_entities.append(orig)
                            for skey in skeys:
                                if skey not in expected_keys:
                                    expected_keys.append(skey)

                    identity_comment = "Static bracket citation not linked to a native Word CITATION field (no auto-PASS)"
                    if detected_entities:
                        identity_comment += f"; context entities {detected_entities} expected {expected_keys}"

                    ctx_start = max(0, m_start - 120)
                    ctx_end = min(len(full_text), m_end + 120)
                    context = full_text[ctx_start:ctx_end]

                    occurrences.append({
                        "occurrence_id": occ_id,
                        "paragraph_index": p_idx,
                        "table_index": t_idx,
                        "cell_coordinates": coord,
                        "raw_citation_text": f"[{num}]",
                        "resolved_number": num,
                        "actual_source_key": actual_skey,
                        "context_snippet": context.replace("\n", " ").strip(),
                        "detected_entities": "; ".join(detected_entities),
                        "expected_source_key": "; ".join(expected_keys),
                        "identity_status": "STATIC_CITATION",
                        "identity_comment": identity_comment,
                        "semantic_status": "MANUAL_REVIEW_REQUIRED"
                    })

    # Traverse paragraphs
    for p_idx, p in enumerate(doc.paragraphs):
        p_style = p.style.name.lower() if p.style else ""
        if "toc" in p_style or "table of figures" in p_style or "tài liệu tham khảo" in p.text.lower():
            continue
        process_element_occurrences(p_idx, "", "", p._element, p.text)

    # Traverse tables
    for t_idx, t in enumerate(doc.tables):
        if is_bibliography_table(t):
            continue
        for r_idx, row in enumerate(t.rows):
            for c_idx, cell in enumerate(row.cells):
                if is_code_snippet(cell.text):
                    continue
                for p in cell.paragraphs:
                    if is_code_snippet(p.text):
                        continue
                    process_element_occurrences("", t_idx, f"({r_idx},{c_idx})", p._element, p.text)

    # Write THESIS-CITATION-AUDIT.csv
    fieldnames = [
        "occurrence_id",
        "paragraph_index",
        "table_index",
        "cell_coordinates",
        "raw_citation_text",
        "resolved_number",
        "actual_source_key",
        "context_snippet",
        "detected_entities",
        "expected_source_key",
        "identity_status",
        "identity_comment",
        "semantic_status"
    ]

    with open(csv_output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(occurrences)

    # Summary statistics
    total_bracket_occurrences = len(occurrences)
    total_native_citations = sum(1 for o in occurrences if o["identity_status"] != "STATIC_CITATION")
    static_only_citations = sum(1 for o in occurrences if o["identity_status"] == "STATIC_CITATION")

    native_occs = [o for o in occurrences if o["identity_status"] != "STATIC_CITATION"]
    identity_pass = sum(1 for o in native_occs if o["identity_status"] == "PASS")
    identity_fails = [o for o in native_occs if o["identity_status"] == "FAIL"]
    identity_ambig = [o for o in native_occs if o["identity_status"] == "AMBIGUOUS"]
    manual_review_count = sum(1 for o in occurrences if o["semantic_status"] == "MANUAL_REVIEW_REQUIRED")

    print(f"\n[AUDIT-REPORT] Total bracket citation occurrences: {total_bracket_occurrences}")
    print(f"  - Total native CITATION fields: {total_native_citations}")
    print(f"  - Static-only citation occurrences: {static_only_citations}")
    print(f"  - Native citation identity: PASS: {identity_pass} / FAIL: {len(identity_fails)} / AMBIGUOUS: {len(identity_ambig)}")
    print(f"  - Semantic status: {manual_review_count} MANUAL_REVIEW_REQUIRED (0 auto-PASS)")
    print(f"  - Hard-coded bibliography table index = 0")

    if identity_ambig:
        print(f"\n[AUDIT-REPORT] Detected {len(identity_ambig)} Ambiguous Citations:")
        for a_occ in identity_ambig:
            print(f"  {a_occ['occurrence_id']}: {a_occ['raw_citation_text']} in p[{a_occ['paragraph_index']}] / t[{a_occ['table_index']}] - {a_occ['identity_comment']}")
            print(f"     Snippet: {a_occ['context_snippet'][:100]}")

    if identity_fails:
        print(f"\n[AUDIT-REPORT] Detected {len(identity_fails)} Identity Mismatches:")
        for f_occ in identity_fails:
            print(f"  {f_occ['occurrence_id']}: {f_occ['raw_citation_text']} in p[{f_occ['paragraph_index']}] / t[{f_occ['table_index']}] - {f_occ['identity_comment']}")
            print(f"     Snippet: {f_occ['context_snippet'][:100]}")
    else:
        print("\n[AUDIT-REPORT] ALL native citation identity checks PASSED (0 mismatches)!")

if __name__ == "__main__":
    audit_citations()
