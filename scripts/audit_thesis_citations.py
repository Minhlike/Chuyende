# -*- coding: utf-8 -*-
"""
Auditor for Thesis Citations in Chuyên đề chuyên sâu.docx
Generates machine-readable THESIS-CITATION-AUDIT.csv
"""
import sys
import re
import csv
from pathlib import Path
import docx

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
csv_path = repo_root / "THESIS-CITATION-AUDIT.csv"

doc = docx.Document(str(docx_path))
bib_table = doc.tables[27]

# Parse Table 27
bib_entries = {}
for i, r in enumerate(bib_table.rows):
    num_txt = r.cells[0].text.strip()
    c_txt = r.cells[1].text.strip() if len(r.cells) > 1 else ''
    m = re.match(r'\[(\d+)\]', num_txt)
    num = int(m.group(1)) if m else i + 1
    
    author_part = c_txt.split('"')[0].strip().rstrip(',')
    title_match = re.search(r'"([^"]+)"', c_txt)
    title_part = title_match.group(1) if title_match else c_txt
    bib_entries[num] = {
        'full': c_txt,
        'author': author_part,
        'title': title_part
    }

# Specific entity associations that bind directly before a citation token
# Mapping pattern directly preceding [n] -> valid citation numbers
DIRECT_ENTITY_BINDINGS = [
    (re.compile(r'arp\s+et\s+al\.?\s*$', re.I), 'Arp et al.', [10]),
    (re.compile(r'inam\s+et\s+al\.?\s*$', re.I), 'Inam et al.', [3]),
    (re.compile(r'michael\s+et\s+al\.?\s*$', re.I), 'Michael et al.', [4]),
    (re.compile(r'liu\s+et\s+al\.?\s*$', re.I), 'Liu et al.', [5]),
    (re.compile(r'mitre\s*(?:att&ck)?(?:\s*enterprise)?(?:\s*matrix)?(?:\s*\(v19\.1\))?\s*$', re.I), 'MITRE ATT&CK', [6]),
    (re.compile(r'zipperle\s+et\s+al\.?\s*$', re.I), 'Zipperle et al.', [7]),
    (re.compile(r'sysmon(?:\s*\(system\s*monitor\))?\s*$', re.I), 'Sysmon', [8]),
    (re.compile(r'loghub\s*$', re.I), 'Loghub', [9]),
    (re.compile(r'unicorn(?:\s*\(han\s+et\s+al\.[^)]*\))?\s*$', re.I), 'UNICORN', [11]),
    (re.compile(r'vicreg(?:\s*\([^)]*\))?\s*$', re.I), 'VICReg', [12]),
    (re.compile(r'barlow\s+twins\s*$', re.I), 'Barlow Twins', [13]),
    (re.compile(r'darpa(?:\s*tc)?(?:\s*e3|\s*engagement\s*#?3)?\s*$', re.I), 'DARPA TC E3', [14]),
    (re.compile(r'darpa(?:\s*tc)?(?:\s*e5|\s*engagement\s*#?5)?\s*$', re.I), 'DARPA TC E5', [15]),
    (re.compile(r'lanl(?:\s*unified\s*host\s*and\s*network\s*dataset)?\s*$', re.I), 'LANL', [16]),
    (re.compile(r'kent\s*$', re.I), 'Kent', [16]),
    (re.compile(r'hdfs(?:\s*của\s*xu\s+et\s+al\.?)?\s*$', re.I), 'HDFS', [17, 9]),
    (re.compile(r'xu\s+et\s+al\.?\s*$', re.I), 'Xu et al.', [17, 39]),
    (re.compile(r'shokri\s+et\s+al\.?\s*$', re.I), 'Shokri et al.', [18]),
    (re.compile(r'fredrikson\s+et\s+al\.?\s*$', re.I), 'Fredrikson et al.', [19]),
    (re.compile(r'nist(?:\s*sp\s*800-226)?\s*$', re.I), 'NIST SP 800-226', [20]),
    (re.compile(r'simclr\s*$', re.I), 'SimCLR', [21]),
    (re.compile(r'chen\s+et\s+al\.?\s*$', re.I), 'Chen et al.', [21]),
    (re.compile(r'lou\s+et\s+al\.?\s*$', re.I), 'Lou et al.', [22]),
    (re.compile(r'deeplog(?:\s*\(du\s+et\s+al\.[^)]*\))?\s*$', re.I), 'DeepLog', [23]),
    (re.compile(r'logbert(?:\s*\(guo\s+et\s+al\.[^)]*\))?\s*$', re.I), 'LogBERT', [24]),
    (re.compile(r'neurallog\s*$', re.I), 'NeuralLog', [25]),
    (re.compile(r'loganomaly\s*$', re.I), 'LogAnomaly', [26]),
    (re.compile(r'nedelkoski\s+et\s+al\.?\s*$', re.I), 'Nedelkoski et al.', [27]),
    (re.compile(r'vaswani\s+et\s+al\.?\s*$', re.I), 'Vaswani et al.', [28]),
    (re.compile(r'kairos(?:\s*\(cheng\s+et\s+al\.[^)]*\))?\s*$', re.I), 'KAIROS', [29]),
    (re.compile(r'nodlink(?:\s*\(she\s+et\s+al\.[^)]*\)|\s*\(li\s+et\s+al\.[^)]*\))?\s*$', re.I), 'NODLINK', [30]),
    (re.compile(r'magic(?:\s*\(jia\s+et\s+al\.[^)]*\))?\s*$', re.I), 'MAGIC', [31]),
    (re.compile(r'orthrus(?:\s*\(jiang\s+et\s+al\.[^)]*\)|\s*\(wang\s+et\s+al\.[^)]*\))?\s*$', re.I), 'ORTHRUS', [32]),
    (re.compile(r'palant[íi]r(?:\s*\(zeng\s+et\s+al\.[^)]*\)|\s*\(gao\s+et\s+al\.[^)]*\))?\s*$', re.I), 'PalanTír', [33]),
    (re.compile(r'bilot\s+et\s+al\.?\s*$', re.I), 'Bilot et al.', [34]),
    (re.compile(r'guerra\s+et\s+al\.?\s*$', re.I), 'Guerra et al.', [35]),
    (re.compile(r'oono\s*&\s*suzuki\s*$', re.I), 'Oono & Suzuki', [36]),
    (re.compile(r'alon\s*&\s*yahav\s*$', re.I), 'Alon & Yahav', [37]),
    (re.compile(r'nguyễn(?:\s*thị\s*thu\s*thủy)?\s*$', re.I), 'Nguyễn', [38]),
    (re.compile(r'rossi\s+et\s+al\.?\s*$', re.I), 'Rossi et al.', [40]),
    (re.compile(r'infonce(?:\s*/\s*contrastive\s*learning)?\s*$', re.I), 'InfoNCE', [41, 21]),
    (re.compile(r'cpm-nets\s*$', re.I), 'CPM-Nets', [42]),
    (re.compile(r'pcgrad\s*$', re.I), 'PCGrad', [43]),
    (re.compile(r'attention-(?:based\s+deep\s+)?mil(?:\s*của\s*ilse\s+et\s+al\.?)?\s*$', re.I), 'Attention-MIL', [44]),
    (re.compile(r'bgl\s*$', re.I), 'BGL', [9])
]

# Regex to find citation tokens
cit_token_regex = re.compile(r'\[(\d+(?:\s*,\s*\d+)*)\](\d*)')

# Check if text is a code block
def is_code_block(text, location_desc):
    # If the text contains python code constructs like 'def ', 'import ', 'class ', 'lambda b:', 'raise ValueError'
    code_indicators = ['def ', 'import ', 'class ', 'lambda ', 'raise ValueError', 'return ', 'torch.', 'np.']
    return any(ci in text for ci in code_indicators)

occurrences = []
occ_counter = 0

def process_text_block(text, location_desc, section_name):
    global occ_counter
    if is_code_block(text, location_desc):
        # Skip pure code blocks from citation audit
        return

    for m in cit_token_regex.finditer(text):
        raw_token = m.group(0)
        cits_str = m.group(1)
        trailing_digit = m.group(2)
        
        start_idx = max(0, m.start() - 70)
        end_idx = min(len(text), m.end() + 70)
        excerpt = text[start_idx:end_idx].replace('\n', ' ').strip()
        
        cits = [int(x.strip()) for x in cits_str.split(',')]
        
        # Text immediately preceding this citation token
        preceding_text = text[max(0, m.start() - 50):m.start()].strip()
        
        for c in cits:
            occ_counter += 1
            syntax_status = "PASS"
            notes = []
            if trailing_digit:
                syntax_status = "FAIL"
                notes.append(f"Corrupted trailing digit '{trailing_digit}'")
            if c < 1 or c > 44:
                syntax_status = "FAIL"
                notes.append(f"Citation [{c}] out of bibliography range [1..44]")
                
            identity_status = "PASS"
            resolved_key = f"REF-{c:02d}"
            resolved_author = bib_entries.get(c, {}).get('author', 'UNKNOWN')
            resolved_title = bib_entries.get(c, {}).get('title', 'UNKNOWN')
            
            if resolved_author == 'UNKNOWN':
                identity_status = "FAIL"
                notes.append(f"Unresolved reference [{c}]")
                
            # Check direct binding
            bound_entity = "NONE"
            for pat, ent_name, expected_nums in DIRECT_ENTITY_BINDINGS:
                if pat.search(preceding_text):
                    bound_entity = ent_name
                    if c not in expected_nums:
                        identity_status = "FAIL"
                        notes.append(f"Named entity '{ent_name}' bound to [{c}], expected {expected_nums}")
                    break
            
            # Semantic status: MANUAL_REVIEW_REQUIRED
            semantic_status = "MANUAL_REVIEW_REQUIRED"
            
            occurrences.append({
                'occurrence_id': f"OCC-{occ_counter:04d}",
                'section': section_name,
                'paragraph_excerpt': excerpt,
                'citation_number': c,
                'resolved_reference_key': resolved_key,
                'resolved_author': resolved_author,
                'resolved_title': resolved_title,
                'named_entity_in_text': bound_entity,
                'syntax_status': syntax_status,
                'identity_status': identity_status,
                'semantic_status': semantic_status,
                'notes': "; ".join(notes) if notes else "OK"
            })

current_section = "Lời nói đầu"
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if p.style and p.style.name.startswith("Heading"):
        current_section = txt
    if '[' in txt and ']' in txt:
        process_text_block(txt, f"p[{i}]", current_section)

for tidx, table in enumerate(doc.tables):
    if tidx == 27:
        continue
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            txt = cell.text.strip()
            if '[' in txt and ']' in txt:
                process_text_block(txt, f"table[{tidx}][{r_idx},{c_idx}]", current_section)

fieldnames = [
    'occurrence_id', 'section', 'paragraph_excerpt', 'citation_number',
    'resolved_reference_key', 'resolved_author', 'resolved_title',
    'named_entity_in_text', 'syntax_status', 'identity_status',
    'semantic_status', 'notes'
]

with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in occurrences:
        writer.writerow(row)

print(f"Total citation occurrences audited: {len(occurrences)}")
syntax_fails = [o for o in occurrences if o['syntax_status'] == 'FAIL']
identity_fails = [o for o in occurrences if o['identity_status'] == 'FAIL']
manual_review = [o for o in occurrences if o['semantic_status'] == 'MANUAL_REVIEW_REQUIRED']

print(f"Syntax PASS: {len(occurrences) - len(syntax_fails)} / FAIL: {len(syntax_fails)}")
print(f"Identity PASS: {len(occurrences) - len(identity_fails)} / FAIL: {len(identity_fails)}")
print(f"Manual review count: {len(manual_review)}")
if syntax_fails:
    print("Syntax failures count:", len(syntax_fails))
if identity_fails:
    print("Identity failures count:", len(identity_fails))
    for f in identity_fails:
        print(" ", f['occurrence_id'], f['paragraph_excerpt'], f['notes'])
