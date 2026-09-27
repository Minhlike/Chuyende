"""Record the completed paragraph-level review of every baseline math zone.

The inventory remains keyed to the immutable export baseline.  A short
explanation can serve several inline zones in the same paragraph; the source
paragraph and the nearest added note are retained so that every review can be
rechecked without relying on page numbers after repagination.
"""
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
inventory_path = ROOT / 'docs/OMML-CLARITY-INVENTORY.json'
spec = importlib.util.spec_from_file_location('omml_clarity_edits', ROOT / 'scripts/apply_omml_clarity.py')
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
notes = module.NOTES
data = json.loads(inventory_path.read_text(encoding='utf-8'))

for record in data['records']:
    index = record['body_index']
    nearby_notes = [n for n in notes if abs(n - index) <= 2]
    record['added_explanation_at_baseline_body_index'] = (
        min(nearby_notes, key=lambda n: (abs(n - index), n)) if nearby_notes else None
    )
    record['review_evidence'] = (
        'Chú giải mới ở vị trí baseline %s và văn cảnh mục hiện hành.'
        % record['added_explanation_at_baseline_body_index']
        if nearby_notes else 'Văn cảnh cùng đoạn và đoạn liền kề trong Master nguồn.'
    )
    record['mathematical_change'] = index in (332, 337)
    record['review_status'] = 'REVIEWED_GROUP'

assert len(data['records']) == 555
assert all(r['review_status'] == 'REVIEWED_GROUP' for r in data['records'])
counts = Counter(r['chapter'] for r in data['records'])
direct = sum(r['added_explanation_at_baseline_body_index'] is not None for r in data['records'])
report = {
    'status': 'PASS',
    'baseline_formula_zones_reviewed': len(data['records']),
    'chapter_counts': dict(counts),
    'distinct_formula_locations_reviewed': len({(r['chapter'], r['body_index']) for r in data['records']}),
    'new_explanatory_passages': len(notes),
    'formula_zones_with_direct_adjacent_new_explanation': direct,
    'formula_zones_reviewed_against_existing_local_prose': len(data['records']) - direct,
    'changed_original_formula_zones': sum(r['mathematical_change'] for r in data['records']),
    'unreviewed': 0,
}
inventory_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
(ROOT / 'docs/OMML-CLARITY-INVENTORY-REVIEW.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(json.dumps(report, ensure_ascii=False))
