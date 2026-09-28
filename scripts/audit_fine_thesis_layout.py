"""Read-only PDF/OOXML inventory for the fine pagination review."""
import argparse,json,re,sys,zipfile
from pathlib import Path
from lxml import etree
import pypdfium2 as pdfium
from PIL import Image,ImageDraw
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M='{http://schemas.openxmlformats.org/officeDocument/2006/math}'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('docx',type=Path);ap.add_argument('pdf',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.docx) as z:root=etree.fromstring(z.read('word/document.xml'))
    body=root.find(W+'body');inventory=[]
    for i,p in enumerate(body):
        text=''.join(n.text or '' for n in p.iter() if n.tag in {W+'t',M+'t'})
        pr=p.find(W+'pPr');style=pr.find(W+'pStyle') if pr is not None else None
        inventory.append({'index':i,'kind':etree.QName(p).localname,'style':style.get(W+'val') if style is not None else '',
            'text':text,'pPr':etree.tostring(pr,encoding='unicode') if pr is not None else '',
            'math':len(list(p.iter(M+'oMath'))),'drawing':len(list(p.iter(W+'drawing'))),
            'section': [etree.tostring(s,encoding='unicode') for s in p.iter(W+'sectPr')],
            'breaks':[n.get(W+'type') for n in p.iter(W+'br')],
            'rows':[{'header':r.find(W+'trPr/'+W+'tblHeader') is not None,'cant_split':r.find(W+'trPr/'+W+'cantSplit') is not None} for r in p.findall(W+'tr')]})
    (a.out/'xml-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
    pdf=pdfium.PdfDocument(str(a.pdf));pages=[];thumbs=[]
    for i in range(len(pdf)):
        p=pdf[i];tp=p.get_textpage();raw=tp.get_text_range();boxes=[];outside=[]
        width,height=p.get_size()
        for j in range(tp.count_chars()):
            char=tp.get_text_range(j,1)
            if not char.strip():continue
            box=tp.get_charbox(j);boxes.append(box)
            if box[0]<0 or box[2]>width+1 or box[1]<0 or box[3]>height+1:outside.append([j,char,list(box)])
        content=[b for b in boxes if b[3]<height-55 and b[1]>45]
        pages.append({'page':i+1,'text':raw,'characters':len(raw.strip()),'outside':outside,
            'content_top':round(height-max((b[3] for b in content),default=0),1),
            'content_bottom':round(min((b[1] for b in content),default=height),1)})
        im=p.render(scale=1.5).to_pil().convert('RGB');im.save(a.out/f'page-{i+1:03}.png')
        im.thumbnail((490,695));thumbs.append(im.copy());tp.close();p.close()
    pdf.close()
    for start in range(0,len(thumbs),9):
        sheet=Image.new('RGB',(1530,2190),'#ddd');draw=ImageDraw.Draw(sheet)
        for j,im in enumerate(thumbs[start:start+9]):
            x=(j%3)*510+10;y=(j//3)*730+30;sheet.paste(im,(x,y));draw.text((x,y-22),f'PDF {start+j+1}',fill='black')
        sheet.save(a.out/f'sheet-{start+1:03}-{min(start+9,len(thumbs)):03}.png')
    (a.out/'pdf-inventory.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'pages':len(pages),'blank':[p['page'] for p in pages if p['characters']<20],
        'sparse':[p['page'] for p in pages if p['content_bottom']>220],'overflow':[p['page'] for p in pages if p['outside']]}))
if __name__=='__main__':main()
