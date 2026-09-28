"""Apply only the preclassified local FIX pagination settings."""
import argparse,hashlib,json,sys
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.patch_ch3_limited_clarifications import load,replace_member,canonical,pageref_slots,W
from scripts.patch_controlled_thesis_formatting import roman
SHA='a8d225253a83965050a0efd5843b20b0ebecea5df3954d9ecad12d9274e48d71'
def prop(p,name,value=None):
    pr=p.find(W+'pPr')
    if pr is None:pr=etree.Element(W+'pPr');p.insert(0,pr)
    node=pr.find(W+name)
    if node is None:
        node=etree.Element(W+name)
        # keepNext/keepLines/pageBreakBefore precede spacing and indentation.
        order=['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr','spacing','ind','jc','sectPr','rPr']
        at=next((i for i,n in enumerate(pr) if etree.QName(n).localname in order and order.index(etree.QName(n).localname)>order.index(name)),len(pr));pr.insert(at,node)
    if value is not None:node.set(W+'val',value)
    else:node.attrib.pop(W+'val',None)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('baseline',type=Path);ap.add_argument('target',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--refresh',type=Path);a=ap.parse_args()
    assert hashlib.sha256(a.baseline.read_bytes()).hexdigest()==SHA
    if a.refresh:
        root=load(a.target);slots=pageref_slots(root);record=json.loads(a.refresh.read_text(encoding='utf-8'));changes=[]
        for key,ts in slots.items():
            old=''.join(t.text or '' for t in ts);value=record['pageref_results'][key]
            if old and all(c in 'ivxlcdm' for c in old):value=roman(int(value))
            if old!=value:
                changes.append({'bookmark':key,'before':old,'after':value});ts[0].text=value
                for t in ts[1:]:t.text=''
        replace_member(a.target,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
        a.out.write_text(json.dumps({'pageref_cache_changes':changes,'count':len(changes)},ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'pageref_cache_changes':len(changes)}));return
    ledger=json.loads((ROOT/'docs/FINE-LAYOUT-CANDIDATES.json').read_text(encoding='utf-8'))
    root=load(a.baseline);b=root.find(W+'body');old=[canonical(n) for n in b]
    prop(b[1],'pageBreakBefore','0');prop(b[1],'keepNext','0')
    prop(b[276],'pageBreakBefore','0')
    for i in [142,176,249,268,291,292,373,374,451,452,512,513,521,522,538,539,540,541,558]:prop(b[i],'keepNext')
    a.target.write_bytes(a.baseline.read_bytes());replace_member(a.target,etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True))
    changed=[i for i,p in enumerate(b) if canonical(p)!=old[i]]
    assert changed==[1,142,176,249,268,276,291,292,373,374,451,452,512,513,521,522,538,539,540,541,558]
    a.out.write_text(json.dumps({'classification':'FIX only','changed_body_indices':changed,'candidate_ids':[x['id'] for x in ledger['FIX']]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'changed_paragraphs':len(changed),'candidate_groups':len(ledger['FIX'])}))
if __name__=='__main__':main()
