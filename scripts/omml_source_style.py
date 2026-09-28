"""Reuse the original thesis' OMML symbol shapes, scripts and typography."""
from __future__ import annotations

import copy
from collections import defaultdict
from lxml import etree

M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SCRIPT_TAGS = {M + name for name in ('sSub', 'sSup', 'sSubSup')}


def surface(node):
    return ''.join(t.text or '' for t in node.iter(M + 't'))


def key(value):
    return ''.join(value.split()).replace('ϕ', 'φ').replace('ϵ', 'ε').replace('⟂', '⊥').replace('−', '-')


class SourceMathStyle:
    def __init__(self, body):
        self.symbols = defaultdict(list)
        self.runs = defaultdict(list)
        self.matches = []
        for index, paragraph in enumerate(body):
            for node in paragraph.iter():
                if node.tag in SCRIPT_TAGS:
                    base = node.find(M + 'e')
                    # Atomic symbols only; do not mistake a whole formula or
                    # a norm for a reusable symbol.
                    if base is not None and not any(n.tag in SCRIPT_TAGS for n in base.iter()):
                        text = surface(base).strip()
                        if any(c.isalpha() for c in text) and all(c.isalnum() or c in 'Δϕφψθσλγερτπ' for c in text):
                            self.symbols[key(surface(node))].append((index, copy.deepcopy(node)))
                elif node.tag == M + 'r':
                    text = surface(node).strip()
                    if (any(c.isalpha() for c in text) or text in ('⊥','⟂')) and all(c.isalnum() or c in 'Δϕφψθσλγερτπ⊥⟂' for c in text):
                        self.runs[key(text)].append((index, copy.deepcopy(node)))

    @staticmethod
    def nearest(candidates, anchor):
        return min(candidates, key=lambda item: (abs(item[0] - anchor), item[0] > anchor, item[0]))

    def apply(self, omml, anchor):
        result = copy.deepcopy(omml)

        def walk(node):
            for child in list(node):
                candidates = self.symbols.get(key(surface(child))) if child.tag in SCRIPT_TAGS else None
                if candidates:
                    index, original = self.nearest(candidates, anchor)
                    node.replace(child, copy.deepcopy(original))
                    self.matches.append({'anchor': anchor, 'symbol': surface(original),
                                         'source_body_index': index, 'kind': 'whole_symbol',
                                         'source_structure': etree.QName(original).localname})
                    continue
                if child.tag == M + 'r':
                    candidates = self.runs.get(key(surface(child).strip()))
                    if candidates:
                        index, original = self.nearest(candidates, anchor)
                        # Keep new numbers and operators; copy the symbol's
                        # original math alphabet, bold/italic/normal style,
                        # font and other run properties exactly.
                        for tag in (M + 'rPr', W + 'rPr'):
                            current = child.find(tag)
                            if current is not None:
                                child.remove(current)
                        props = [copy.deepcopy(p) for p in original if p.tag in (M + 'rPr', W + 'rPr')]
                        for position, prop in enumerate(props):
                            child.insert(position, prop)
                        # Variants of phi/epsilon/bottom must match the source.
                        old_text = original.find(M + 't')
                        new_text = child.find(M + 't')
                        if old_text is not None and new_text is not None:
                            new_text.text = old_text.text
                        self.matches.append({'anchor': anchor, 'symbol': surface(original),
                                             'source_body_index': index, 'kind': 'run_style'})
                walk(child)

        walk(result)
        return result
