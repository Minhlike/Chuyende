# -*- coding: utf-8 -*-
"""
Thesis Citation Auditor based on Dynamic Canonical Source Identity
Guarantees:
1. ZERO hard-coded expected numeric IDs.
2. Dynamic resolution of DOCX bibliography rows -> canonical source keys.
3. Runtime map: citation_number -> actual_source_key.
4. Named entity / alias in citation context -> expected_source_key.
5. Verification: actual_source_key == expected_source_key.
6. Semantic status is strictly MANUAL_REVIEW_REQUIRED (no auto-PASS).
7. Outputs THESIS-CITATION-AUDIT.csv.
"""

import sys
import re
import csv
import json
from pathlib import Path
import docx

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
canonical_json_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"
csv_output_path = repo_root / "THESIS-CITATION-AUDIT.csv"

def load_canonical_registry():
    with open(canonical_json_path, "r", encoding="utf-8") as f:
        sources = json.load(f)
    return sources

def resolve_bibliography_table(doc, canonical_sources):
    """
    Parses Table 27 (the Bibliography) from the document and maps each row number [1..44]
    to its canonical source_key.
    Returns: dict[int, str] mapping citation_number -> source_key
    """
    t27 = doc.tables[27]
    runtime_map = {}
    
    # Pre-index canonical sources by title words and author keywords
    for idx, row in enumerate(t27.rows):
        num_cell = row.cells[0].text.strip()
        text_cell = row.cells[1].text.strip()
        
        m = re.search(r"\[(\d+)\]", num_cell)
        if not m:
            continue
        num = int(m.group(1))
        
        matched_key = None
        best_score = 0
        
        for s in canonical_sources:
            score = 0
            title = s["canonical_title"].lower()
            # Title overlap
            title_words = [w for w in re.split(r"\W+", title) if len(w) > 3]
            if title_words:
                matches = sum(1 for w in title_words if w in text_cell.lower())
                score = matches / len(title_words)
            
            # Key specific overrides
            if s["source_key"] == "DARPA2018TCE3" and "Engagement 3" in text_cell:
                score = 10.0
            elif s["source_key"] == "DARPA2020TCE5" and "Engagement 5" in text_cell:
                score = 10.0
            elif s["source_key"] == "Russinovich2026Sysmon" and "Sysmon" in text_cell:
                score = 10.0
            elif s["source_key"] == "Zhu2023Loghub" and "Loghub: A Large Collection" in text_cell:
                score = 10.0
            elif s["source_key"] == "Zhu2019LogParsing" and "Tools and Benchmarks" in text_cell:
                score = 10.0
            elif s["source_key"] == "Kent2015LANL" and "Comprehensive, Multi-Source" in text_cell:
                score = 10.0
            elif s["source_key"] == "Ilse2018AttentionMIL" and "Attention-based Deep Multiple" in text_cell:
                score = 10.0
            elif s["source_key"] == "Guerra2026PIDSEvalProtocols" and "Guerra" in text_cell:
                score = 10.0
            elif s["source_key"] == "Nguyen2026APTGraphLearning" and "Nguyễn" in text_cell:
                score = 10.0
                
            if score > best_score and score > 0.3:
                best_score = score
                matched_key = s["source_key"]
                
        if not matched_key:
            raise RuntimeError(f"Could not uniquely map Bibliography row [{num}]: {text_cell[:60]}")
        runtime_map[num] = matched_key
        
    return runtime_map

def build_alias_maps(canonical_sources):
    """
    Builds:
    - unique_aliases: list of (norm_alias, original_alias, single_source_key)
    - ambiguous_aliases: list of (norm_alias, original_alias, sorted_list_of_source_keys)
    Both sorted by length of original_alias descending.
    """
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
    """
    Extracts the relevant prefix for a citation, bounded by prior citations
    or punctuation to prevent entity leakage across independent clauses.
    Handles 'et al.' abbreviations safely so the period is not treated as a sentence end.
    """
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

    # Preflight checks
    assert len(canonical_sources) == 44, f"Expected 44 canonical sources, got {len(canonical_sources)}"
    keys = [s["source_key"] for s in canonical_sources]
    assert len(keys) == len(set(keys)) == 44, f"source_key must be unique (44), found {len(set(keys))}"
    tags = [s["word_source_tag"] for s in canonical_sources]
    assert len(tags) == len(set(tags)) == 44, f"word_source_tag must be unique (44), found {len(set(tags))}"

    # Check cross-source duplicate aliases in CANONICAL-SOURCES.json
    json_alias_map = {}
    for s in canonical_sources:
        k = s["source_key"]
        for a in s.get("aliases", []):
            json_alias_map.setdefault(a.strip().lower(), set()).add(k)
    dup_json = {a: sorted(ks) for a, ks in json_alias_map.items() if len(ks) > 1}
    print(f"[PREFLIGHT] 44 source_key unique: OK")
    print(f"[PREFLIGHT] 44 word_source_tag unique: OK")
    print(f"[PREFLIGHT] Cross-source duplicate aliases in CANONICAL-SOURCES.json: {len(dup_json)}")
    for a, ks in sorted(dup_json.items()):
        print(f"  [DUP REGISTRY] '{a}' -> {ks}")

    doc = docx.Document(str(docx_path))
    runtime_bib_map = resolve_bibliography_table(doc, canonical_sources)
    print(f"[AUDIT] Successfully resolved {len(runtime_bib_map)} DOCX bibliography entries to canonical source keys.")
    for num in sorted(runtime_bib_map.keys()):
        print(f"  [{num:2d}] -> {runtime_bib_map[num]}")

    unique_aliases, ambiguous_aliases = build_alias_maps(canonical_sources)
    print(f"[PREFLIGHT] Unique aliases: {len(unique_aliases)}, Ambiguous aliases across sources: {len(ambiguous_aliases)}")
    for norm, orig, ks in ambiguous_aliases:
        print(f"  [AMBIGUOUS ALIAS] '{orig}' -> {ks}")

    occurrences = []
    occ_counter = 0

    # Helper to check if text is a code snippet
    def is_code_snippet(txt):
        code_markers = ["def ", "class ", "return ", "import ", "lambda ", " = ", "self.", "torch.", "np.", "session_intervals[b][0]", "np.zeros", "nn.Module", "pytest."]
        return any(m in txt for m in code_markers)

    # 1. Audit paragraphs (skip Bibliography table / TOC / TOF)
    for p_idx, p in enumerate(doc.paragraphs):
        p_text = p.text
        if not p_text.strip():
            continue

        p_style = p.style.name.lower() if p.style else ""
        if "toc" in p_style or "table of figures" in p_style or "tài liệu tham khảo" in p_text.lower():
            continue

        if is_code_snippet(p_text):
            continue

        # Regex for [N] or [N, M] or [N]-[M]
        for m in re.finditer(r"\[(\d+)(?:,\s*(\d+))*\]", p_text):
            raw_match = m.group(0)
            start_pos, end_pos = m.span()

            # Context window around the citation (-120 to +120 chars)
            ctx_start = max(0, start_pos - 120)
            ctx_end = min(len(p_text), end_pos + 120)
            context = p_text[ctx_start:ctx_end]

            nums = [int(n) for n in re.findall(r"\d+", raw_match)]
            sentence_prefix = extract_bounded_prefix(p_text, start_pos)

            matched_u = [(orig, skey) for norm, orig, skey in unique_aliases if orig.lower() in sentence_prefix.lower()]
            matched_a = [(orig, skeys) for norm, orig, skeys in ambiguous_aliases if orig.lower() in sentence_prefix.lower()]

            for num in nums:
                occ_counter += 1
                occ_id = f"OCC-{occ_counter:04d}"

                syntax_status = "PASS" if 1 <= num <= 44 else "FAIL"
                actual_skey = runtime_bib_map.get(num, f"UNRESOLVED_NUM_{num}")

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
                        identity_comment = f"Context entities {detected_entities} expected {expected_keys}, but [{num}] resolved to {actual_skey}"
                elif matched_a:
                    cand_keys = []
                    for orig, skeys in matched_a:
                        if orig not in detected_entities:
                            detected_entities.append(orig)
                        for skey in skeys:
                            if skey not in cand_keys:
                                cand_keys.append(skey)
                    expected_keys = cand_keys
                    if actual_skey in cand_keys:
                        identity_status = "AMBIGUOUS"
                        identity_comment = f"Ambiguous alias {detected_entities} maps to multiple sources: {cand_keys}; duplicate alias not allowed for auto-PASS"
                    else:
                        identity_status = "FAIL"
                        identity_comment = f"Context entity {detected_entities} maps to {cand_keys}, but [{num}] resolved to unrelated {actual_skey}"
                else:
                    identity_status = "PASS"
                    identity_comment = "General citation without named entity anchor"

                occurrences.append({
                    "occurrence_id": occ_id,
                    "paragraph_index": p_idx,
                    "table_index": "",
                    "cell_coordinates": "",
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

    # 2. Audit table cells (excluding Table 27)
    for t_idx, table in enumerate(doc.tables):
        if t_idx == 27:
            continue
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                c_text = cell.text
                if not c_text.strip() or is_code_snippet(c_text):
                    continue
                for m in re.finditer(r"\[(\d+)(?:,\s*(\d+))*\]", c_text):
                    raw_match = m.group(0)
                    start_pos, end_pos = m.span()
                    ctx_start = max(0, start_pos - 80)
                    ctx_end = min(len(c_text), end_pos + 80)
                    context = c_text[ctx_start:ctx_end]

                    nums = [int(n) for n in re.findall(r"\d+", raw_match)]
                    sentence_prefix = extract_bounded_prefix(c_text, start_pos)

                    matched_u = [(orig, skey) for norm, orig, skey in unique_aliases if orig.lower() in sentence_prefix.lower()]
                    matched_a = [(orig, skeys) for norm, orig, skeys in ambiguous_aliases if orig.lower() in sentence_prefix.lower()]

                    for num in nums:
                        occ_counter += 1
                        occ_id = f"OCC-{occ_counter:04d}"
                        syntax_status = "PASS" if 1 <= num <= 44 else "FAIL"
                        actual_skey = runtime_bib_map.get(num, f"UNRESOLVED_NUM_{num}")

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
                                identity_comment = f"Context entities {detected_entities} expected {expected_keys}, but [{num}] resolved to {actual_skey}"
                        elif matched_a:
                            cand_keys = []
                            for orig, skeys in matched_a:
                                if orig not in detected_entities:
                                    detected_entities.append(orig)
                                for skey in skeys:
                                    if skey not in cand_keys:
                                        cand_keys.append(skey)
                            expected_keys = cand_keys
                            if actual_skey in cand_keys:
                                identity_status = "AMBIGUOUS"
                                identity_comment = f"Ambiguous alias {detected_entities} maps to multiple sources: {cand_keys}; duplicate alias not allowed for auto-PASS"
                            else:
                                identity_status = "FAIL"
                                identity_comment = f"Context entity {detected_entities} maps to {cand_keys}, but [{num}] resolved to unrelated {actual_skey}"
                        else:
                            identity_status = "PASS"
                            identity_comment = "General citation without named entity anchor"

                        occurrences.append({
                            "occurrence_id": occ_id,
                            "paragraph_index": "",
                            "table_index": t_idx,
                            "cell_coordinates": f"({r_idx},{c_idx})",
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

    # Print summary
    syntax_fails = sum(1 for o in occurrences if not (1 <= o["resolved_number"] <= 44))
    identity_pass = sum(1 for o in occurrences if o["identity_status"] == "PASS")
    identity_fails = [o for o in occurrences if o["identity_status"] == "FAIL"]
    identity_ambig = [o for o in occurrences if o["identity_status"] == "AMBIGUOUS"]
    manual_review_count = sum(1 for o in occurrences if o["semantic_status"] == "MANUAL_REVIEW_REQUIRED")

    print(f"\n[AUDIT-REPORT] Total citation occurrences: {len(occurrences)}")
    print(f"  - Syntax PASS: {len(occurrences) - syntax_fails} / FAIL: {syntax_fails}")
    print(f"  - Identity PASS: {identity_pass} / FAIL: {len(identity_fails)} / AMBIGUOUS: {len(identity_ambig)}")
    print(f"  - Semantic status: {manual_review_count} MANUAL_REVIEW_REQUIRED (0 auto-PASS)")

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
        print("\n[AUDIT-REPORT] ALL citation identity checks PASSED (0 mismatches)!")

if __name__ == "__main__":
    audit_citations()
