from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'docs/OMML-CLARITY-INVENTORY.json'
parser=argparse.ArgumentParser()
parser.add_argument('baseline',type=Path,help='The exact export baseline DOCX, SHA-256 locked below')
args=parser.parse_args()
expected='9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033'
if hashlib.sha256(args.baseline.read_bytes()).hexdigest()!=expected:
    raise SystemExit('Not the locked export baseline')
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
# Inventory positions are locked to the export baseline, not the edited copy.
with ZipFile(args.baseline) as z:
    root=etree.fromstring(z.read('word/document.xml'))
body=root.find(f'{{{W}}}body')
def surface(x):
    return ''.join(n.text or '' for n in x.iter() if n.tag in (f'{{{W}}}t',f'{{{M}}}t')).strip()
texts=[surface(x) for x in body]
data=json.loads(P.read_text(encoding='utf-8'))

def topic(ch,i):
    if ch==1:
        if i<=127:return 'cửa sổ sự kiện và các dạng trôi dạt'
        if i<=132:return 'không gian nhãn ATT&CK'
        if i<=157:return 'Hợp đồng Biểu diễn và ranh giới bộ mã hóa/bộ dò'
        if i<=166:return 'đếm sự kiện, TF-IDF và entropy'
        if i<=170:return 'PCA, phần dư và bất biến tuyến tính'
        if i<=175:return 'xác suất chuỗi và tập dự đoán top-g'
        return 'đồ thị nguồn gốc và kiểu đỉnh/cạnh'
    if i<=242:return 'luồng sự kiện, ánh xạ biểu diễn và giả thuyết H1–H5'
    if i<=257:return 'trạng thái dòng, watermark và ngân sách tài nguyên'
    if i<=285:return 'bộ sáu sự kiện, chuẩn hóa và phân chia dữ liệu'
    if i<=303:return 'giả danh hóa và liên kết có kiểm soát'
    if i<=318:return 'đồng bộ thời gian và cửa sổ đa tỷ lệ'
    if i<=345:return 'mã hóa chuỗi Transformer và hàm mất mát tự giám sát'
    if i<=401:return 'đồ thị nguồn gốc, Temporal GNN và hàm mất mát đồ thị'
    if i<=441:return 'đầu chiếu và ba thành phần VICReg'
    if i<=473:return 'đồ thị tối ưu và hàm mất mát Stage A'
    if i<=483:return 'cổng độ tin cậy và PCGrad'
    if i<=498:return 'Attention-MIL và nhãn túi'
    return 'dung hợp đa góc nhìn và độ phức tạp'

def next_text(i,step):
    k=i+step
    while 0<=k<len(texts):
        if texts[k] and len(texts[k])>15:return texts[k][:1100]
        k+=step
    return ''

for rec in data['records']:
    s=rec['formula_surface']; i=rec['body_index']; t=topic(rec['chapter'],i)
    eq=('=' in s or '←' in s); bound=any(x in s for x in ('≤','≥','≠','<','>'))
    operator=any(x in s for x in ('∑','log','exp','softmax','Var','‖','O(', 'σ','cos','⊙'))
    atomic=len(s)<22 and not (eq or bound or operator)
    if atomic:
        rec['purpose']=f'Đặt tên cho đại lượng hoặc thành phần của {t}; vai trò cụ thể nằm trong đoạn văn nguyên văn đi kèm.'
    elif bound:
        rec['purpose']=f'Phát biểu điều kiện hoặc giới hạn của {t}; cần đọc cùng các giả định trong đoạn văn đi kèm.'
    elif eq:
        rec['purpose']=f'Định nghĩa phép tính hoặc quan hệ cấu thành {t}; vế trái là đại lượng được xác định từ vế phải.'
    else:
        rec['purpose']=f'Ký hiệu hóa cấu trúc hoặc phép toán thuộc {t}; không tự thân là kết quả thực nghiệm.'
    rec['nearby_before']=next_text(i,-1)
    rec['nearby_after']=next_text(i,1)
    rec['symbols']=list(dict.fromkeys(rec.pop('symbol_tokens_surface', rec.get('symbols', []))))
    # Conservative triage: a local prose definition is not yet proof that every symbol is explained.
    local=rec['paragraph_context']
    explicit=any(w in local.lower() for w in ('trong đó',' là ',' biểu thị',' gồm ','định nghĩa','ký hiệu','đại diện','tức '))
    rec['symbol_explanations_current']='Có diễn giải tại cùng đoạn; cần đối chiếu từng ký hiệu' if explicit else 'Chưa thấy diễn giải đầy đủ ngay cùng đoạn; đối chiếu đoạn liền kề'
    rec['missing_domain_unit_or_intuition']='Kiểm tra miền giá trị/đơn vị khi có thời gian, xác suất hoặc kích thước; thiếu ví dụ trực tiếp' if not atomic else 'Ký hiệu ngắn; kiểm tra phạm vi định nghĩa trong cùng mục'
    rec['numeric_example_feasible']=bool((eq or bound or operator) and not any(w in s for w in ('Ttactics','Process','Utility(','PrivacyLoss(','I(z;','ΘPCGrad')))
    rec['conceptual_example_if_not_numeric']=f'Minh họa bằng một cửa sổ log hoặc hai thực thể quan sát được trong chủ đề {t}.' if not rec['numeric_example_feasible'] else None
    if atomic: rec['difficulty']='CƠ BẢN'
    elif i in (166,168,170,175,231,234,237,239,241,325,330,332,337,374,376,378,383,385,387,395,426,428,430,432,434,469,472,478,482,490,493,509,520): rec['difficulty']='CỐT LÕI'
    elif len(s)>75 or operator: rec['difficulty']='KHÓ'
    else: rec['difficulty']='TRUNG BÌNH'
    if 423<=i<=435 or i in (154,330,332,337,381,383,385,387,466,469,472): risk='Mất mát nhỏ hoặc vector khớp không tự chứng minh hiểu ngữ nghĩa an ninh.'
    elif i in (167,168,170,174,175,490,491,492,493,497,498): risk='Điểm bất thường/trọng số chú ý không tự suy ra tấn công hay quan hệ nhân quả.'
    elif 286<=i<=303 or i in (241,242): risk='Giả danh hóa không tương đương bảo đảm riêng tư; số minh họa không là đo lường thực nghiệm.'
    elif 230<=i<=242: risk='Đây là giả thuyết/điều kiện kiểm định, không phải kết quả đã được chứng minh.'
    elif 244<=i<=257 or 516<=i<=521: risk='Độ phức tạp phụ thuộc giả định kiến trúc và không chứng minh ngân sách đầu-cuối.'
    elif 350<=i<=401: risk='Cạnh phụ thuộc quan sát được không chứng minh tác động nhân quả.'
    else: risk='Không biến ví dụ giả định thành kết quả thực nghiệm; giữ nguyên miền và giả định của ký hiệu.'
    rec['simplification_risk']=risk
    rec['review_status']='INITIAL_TRIAGE'
P.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Enriched {len(data['records'])} records; numerical candidates={sum(r['numeric_example_feasible'] for r in data['records'])}")
