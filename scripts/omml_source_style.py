"""Copy symbols using reviewed object-specific baseline XML selectors."""
from __future__ import annotations
import copy,hashlib,json
from pathlib import Path
from lxml import etree
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
ROOT=Path(__file__).resolve().parents[1]
SCRIPT_TAGS={M+name for name in ('sSub','sSup','sSubSup')}

def surface(node):return ''.join(t.text or '' for t in node.iter(M+'t'))
def key(value):return ''.join(value.split()).replace('−','-')
def canonical(node):return etree.tostring(node,method='c14n',exclusive=True)
def at(root,path):
    for index in path:root=root[index]
    return root

class SourceMathStyle:
    def __init__(self,body):
        self.body=copy.deepcopy(body)
        data=json.loads((ROOT/'docs/OMML-OBJECT-SYMBOL-BINDINGS.json').read_text(encoding='utf-8'))
        self.baseline_sha256=data['baseline_sha256']
        if data['mixed_candidates_to_review']:raise ValueError('Unreviewed object ambiguity')
        self.bindings={(r['anchor'],r['expression']):r for r in data['bindings']}
        self.matches=[]

    def source(self,record):
        source=at(self.body[record['source_body_index']],record['source_path'])
        if hashlib.sha256(canonical(source)).hexdigest()!=record['source_sha256']:
            raise ValueError('Original object XML changed: '+str(record))
        result=copy.deepcopy(source)
        if record['kind']=='run_span':
            lo,hi=record['span']
            result.find(M+'t').text=surface(source)[lo:hi]
        if record['kind']=='indexed_example':
            change=record['substitution'];slot=result.find(M+change['slot'])
            if surface(slot)!=change['old']:raise ValueError('Indexed example source changed')
            texts=list(slot.iter(M+'t'))
            if len(texts)!=1:raise ValueError('Indexed example source must be atomic')
            texts[0].text=change['new']
        return result

    def apply(self,omml,anchor,raw):
        record=self.bindings.get((anchor,raw))
        if record is None:raise ValueError(f'Unbound mathematical object: {anchor}, {raw}')
        if hashlib.sha256(canonical(omml)).hexdigest()!=record['input_omml_sha256']:
            raise ValueError(f'Unreviewed input expression: {anchor}, {raw}')
        result=copy.deepcopy(omml)
        # Reverse index order preserves frozen paths when a run is split.
        for operation in sorted(record['operations'],key=lambda r:r['target_path'],reverse=True):
            target=at(result,operation['target_path']);parent=target.getparent();index=parent.index(target)
            if operation['kind']=='split_run':
                value=surface(target);replacement=[];last=0
                for part in operation['segments']:
                    lo,hi=part['target_span']
                    if lo>last:
                        plain=copy.deepcopy(target);plain.find(M+'t').text=value[last:lo];replacement.append(plain)
                    replacement.append(self.source(part));last=hi
                    self.matches.append({'anchor':anchor,'expression':raw,'object_context':record['object_context'],
                        **{k:v for k,v in part.items() if not k.startswith('target_')}})
                if last<len(value):
                    plain=copy.deepcopy(target);plain.find(M+'t').text=value[last:];replacement.append(plain)
                parent.remove(target)
                for offset,node in enumerate(replacement):parent.insert(index+offset,node)
            else:
                parent.replace(target,self.source(operation))
                self.matches.append({'anchor':anchor,'expression':raw,'object_context':record['object_context'],
                    **{k:v for k,v in operation.items() if not k.startswith('target_')}})
        return result
