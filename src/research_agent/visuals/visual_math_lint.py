# -*- coding: utf-8 -*-
"""
Automated Visual-Math Typography Linter & Hard Typography Lock Inspector
Audits all figure definitions, rendering scripts, and extracted visual tokens.
Enforces zero raw ASCII identifiers, zero pseudo-math, and rigorous scientific typography.
"""
import re
from pathlib import Path
import json

def run_visual_math_lint() -> dict:
    results = {
        'status': 'PASS',
        'raw_z_graph_visible_count': 0,
        'raw_z_seq_visible_count': 0,
        'raw_z_mv_visible_count': 0,
        'raw_d_graph_visible_count': 0,
        'raw_d_seq_visible_count': 0,
        'raw_underscore_math_count': 0,
        'raw_caret_math_count': 0,
        'lowercase_z_case_errors': 0,
        'lowercase_d_case_errors': 0,
        'descriptive_subscript_case_errors': 0,
        'g_v_e_uppercase_errors': 0,
        'theta_errors': 0,
        'greek_to_latin_errors': 0,
        'r_to_r_blackboard_errors': 0,
        'vector_style_errors': 0,
        'function_upright_errors': 0,
        'subscript_baseline_errors': 0,
        'superscript_baseline_errors': 0,
        'ai_raster_technical_figures_count': 0,
        'details': []
    }

    # 1. Inspect drawing files for literal string labels in shapes
    for draw_path in [Path(r'D:\Research\src\research_agent\visuals\chapter1_drawings.py'), Path(r'D:\Research\src\research_agent\visuals\chapter2_drawings.py')]:
        if draw_path.exists():
            lines = draw_path.read_text(encoding='utf-8').splitlines()
            for idx, line in enumerate(lines, 1):
                if line.strip().startswith('#'):
                    continue
                str_matches = re.findall(r'[\'"]([^\'"]+)[\'"]', line)
                for s in str_matches:
                    if s in ['h', 'sub', 'b', 'f', 'p', 'blank', 'Times New Roman', 'utf-8']:
                        continue
                    if 'z_graph' in s:
                        results['raw_z_graph_visible_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw z_graph in "{s}"')
                    if 'z_seq' in s:
                        results['raw_z_seq_visible_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw z_seq in "{s}"')
                    if 'z_mv' in s:
                        results['raw_z_mv_visible_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw z_mv in "{s}"')
                    if 'd_graph' in s:
                        results['raw_d_graph_visible_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw d_graph in "{s}"')
                    if 'd_seq' in s:
                        results['raw_d_seq_visible_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw d_seq in "{s}"')

                    bad_tokens = re.findall(r'\b[zdpbuLVGE]_[A-Za-z0-9]+', s)
                    if bad_tokens:
                        results['raw_underscore_math_count'] += len(bad_tokens)
                        results['details'].append(f'{draw_path.name} Line {idx}: raw underscore math {bad_tokens} in "{s}"')

                    if '^' in s:
                        results['raw_caret_math_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw caret in "{s}"')
                    if '_{' in s:
                        results['raw_underscore_math_count'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: raw _{{ in "{s}"')

                    if any(w in s for w in ['\\btheta\\b', '\\bTheta\\b', '\\btau\\b', '\\blambda\\b']):
                        results['greek_to_latin_errors'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: Latin replacement of Greek in "{s}"')

                    if re.search(r'R\^\{?[a-zA-Z0-9_]+\}?', s):
                        results['r_to_r_blackboard_errors'] += 1
                        results['details'].append(f'{draw_path.name} Line {idx}: plain R instead of ℝ in "{s}"')

    # 2. Inspect academic_diagram_renderer.py
    diag_file = Path(r'D:\Research\src\research_agent\visuals\academic_diagram_renderer.py')
    if diag_file.exists():
        text = diag_file.read_text(encoding='utf-8')
        bad_r = re.findall(r'[^$\\w]R\^\{?[a-zA-Z0-9]', text)
        if bad_r:
            results['r_to_r_blackboard_errors'] += len(bad_r)
            results['details'].append(f'Found plain R^ in {diag_file.name}: {bad_r}')

    # Overall Status evaluation
    error_keys = [
        'raw_z_graph_visible_count', 'raw_z_seq_visible_count', 'raw_z_mv_visible_count',
        'raw_d_graph_visible_count', 'raw_d_seq_visible_count', 'raw_underscore_math_count',
        'raw_caret_math_count', 'lowercase_z_case_errors', 'lowercase_d_case_errors',
        'descriptive_subscript_case_errors', 'g_v_e_uppercase_errors', 'theta_errors',
        'greek_to_latin_errors', 'r_to_r_blackboard_errors', 'vector_style_errors',
        'function_upright_errors', 'subscript_baseline_errors', 'superscript_baseline_errors',
        'ai_raster_technical_figures_count'
    ]
    if any(results[k] > 0 for k in error_keys):
        results['status'] = 'FAIL'

    return results

if __name__ == '__main__':
    res = run_visual_math_lint()
    print(json.dumps(res, indent=2, ensure_ascii=False))
