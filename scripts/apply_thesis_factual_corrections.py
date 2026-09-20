# -*- coding: utf-8 -*-
"""
Anchor-based, Idempotent Factual, Citation, and Implementation Boundary Corrections
for Chuyên đề chuyên sâu.docx and PDF export.

Guarantees:
1. Anchor-based paragraph resolution (no hard-coded paragraph indices).
2. 3-state check per correction:
   - OLD_FOUND_ONCE: apply correction.
   - NEW_ALREADY_PRESENT: pass / no-op.
   - AMBIGUOUS_OR_MISSING: raise exception and fail.
3. Update TOC and List of Figures strictly via Word COM (Fields.Update, TablesOfContents.Update, TablesOfFigures.Update).
4. Strictly preserves all 606 OMML equations.
5. Idempotent: second run makes 0 changes; DOCX SHA-256 before == after.
"""
import sys
import shutil
import hashlib
from pathlib import Path
import docx
import win32com.client as win32
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
pdf_path = repo_root / "Chuyên đề chuyên sâu.pdf"

backup_path = repo_root / "Chuyên đề chuyên sâu.pre_audit_backup.docx"
if not backup_path.exists():
    shutil.copy2(docx_path, backup_path)
    print(f"Created pre-audit backup at {backup_path}")

def compute_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def is_toc_or_tof(p) -> bool:
    s = p.style.name.lower()
    return 'toc' in s or 'table of figures' in s

def replace_in_paragraph_runs(p, old_text: str, new_text: str):
    full_text = p.text
    if old_text not in full_text:
        raise ValueError(f"Target text not found in paragraph:\nExpected: {old_text}\nActual: {full_text}")

    # Check if old_text is contained entirely within a single run:
    for r in p.runs:
        if old_text in r.text:
            r.text = r.text.replace(old_text, new_text)
            return

    # If it spans multiple runs:
    has_omml = len(p._p.xpath('.//m:oMath')) > 0
    if not has_omml:
        first_run = p.runs[0] if p.runs else p.add_run()
        first_run.text = full_text.replace(old_text, new_text)
        for r in p.runs[1:]:
            r.text = ""
    else:
        for r in p.runs:
            if old_text in r.text:
                r.text = r.text.replace(old_text, new_text)
                return
        raise ValueError("Could not surgically replace text across OMML runs without risking formula damage.")

def run_corrections(docx_file: Path, pdf_file: Path):
    sha_before = compute_sha256(docx_file)
    print(f"Starting DOCX SHA-256: {sha_before}")

    doc = docx.Document(str(docx_file))

    # Verify initial OMML count
    initial_omml = len(doc._element.xpath('.//m:oMath'))
    print(f"Initial OMML count: {initial_omml}")
    assert initial_omml == 606, f"Expected 606 OMML elements, found {initial_omml}"

    body_paragraphs = [p for p in doc.paragraphs if not is_toc_or_tof(p)]

    corrections = [
        {
            'id': 'fig12_text',
            'desc': 'Figure 1.2 citation in body text',
            'anchor_fn': lambda p: 'Do đó, chuyên đề xác lập nguyên tắc: Ma trận MITRE ATT&CK' in p.text,
            'old_text': 'MITRE ATT&CK [4] và Inam et al. [1]2',
            'new_text': 'MITRE ATT&CK [6] và Inam et al. [3]'
        },
        {
            'id': 'fig12_caption',
            'desc': 'Figure 1.2 caption',
            'anchor_fn': lambda p: 'Hình 1.2: Mô hình Không gian Bằng chứng Hành vi Đa chiều' in p.text and p.style.name == 'Caption',
            'old_text': 'MITRE ATT&CK [4] và Inam et al. [1]2 [6] [3]',
            'new_text': 'MITRE ATT&CK [6] và Inam et al. [3]'
        },
        {
            'id': 'llm_preface',
            'desc': 'Unsupported LLM claim removal in preface',
            'anchor_fn': lambda p: 'Mô hình ngôn ngữ lớn mở thêm khả năng' in p.text,
            'old_text': 'Mô hình ngôn ngữ lớn mở thêm khả năng chuẩn hóa và diễn giải log, nhưng vẫn chịu hạn chế về chi phí, độ trễ, tính ổn định và bảo mật dữ liệu [2]. ',
            'new_text': ''
        },
        {
            'id': 'darpa_gt',
            'desc': 'DARPA TC ground truth description narrowing',
            'anchor_fn': lambda p: 'Xét theo dữ liệu thực nghiệm, việc mô hình hóa hành vi tấn công' in p.text,
            'old_text': 'trong đó các kịch bản tấn công và diễn tập red-team trong các engagement của chương trình được gán nhãn ở mức độ hạt tiến trình và luồng phụ thuộc;',
            'new_text': 'trong đó các kịch bản tấn công của đội Red Team được ghi nhận qua các báo cáo kịch bản (ground-truth reports/annotations), cho phép ánh xạ và suy diễn nhãn ở mức tiến trình và luồng phụ thuộc liên quan đến đợt tấn công, thay vì toàn bộ dữ liệu viễn trắc nền đều có nhãn sẵn ở mức hạt nhân;'
        },
        {
            'id': 'token_bucket',
            'desc': 'Token-Bucket Backpressure marked design-only',
            'anchor_fn': lambda p: 'Detector Leakage' in p.text,
            'old_text': 'Khi hệ thống gặp hiện tượng đột biến lưu lượng Traffic Spike, cơ chế kiểm soát áp lực ngược Backpressure Control dựa trên thuật toán Token-Bucket điều tiết tốc độ nạp dữ liệu. Nếu lưu lượng vượt quá giới hạn chịu tải tối đa, việc loại bỏ gói tin (Shedding) được thực hiện hoàn toàn độc lập với kết quả phát hiện của mô hình (dựa trên hạn ngạch băng thông nguồn thu thập hoặc mức độ ưu tiên của phân vùng telemetry, tuyệt đối không dựa vào điểm số an ninh chưa kiểm chứng) nhằm tránh rủi ro rò rỉ vòng lặp Detector Leakage và loại bỏ nhầm các bằng chứng APT yếu thưa thớt.',
            'new_text': 'Đối với tình huống đột biến lưu lượng (Traffic Spike), kiến trúc đề xuất cơ chế kiểm soát áp lực ngược (Backpressure Control) dự kiến dựa trên thuật toán Token-Bucket để điều tiết tốc độ nạp dữ liệu. Trong thiết kế này, nếu lưu lượng vượt quá giới hạn chịu tải tối đa, việc loại bỏ gói tin (Shedding) được đề xuất thực hiện độc lập với kết quả phát hiện của mô hình (dựa trên hạn ngạch băng thông nguồn thu thập hoặc mức độ ưu tiên của phân vùng telemetry, không dựa vào điểm số an ninh chưa kiểm chứng) nhằm tránh rủi ro rò rỉ vòng lặp Detector Leakage và loại bỏ nhầm các bằng chứng APT yếu thưa thớt (thành phần streaming này thuộc thiết kế kiến trúc mục tiêu, chưa triển khai trong thực nghiệm Stage A2).'
        },
        {
            'id': 'graph_fidelity',
            'desc': 'Graph fidelity mechanisms marked design-only',
            'anchor_fn': lambda p: 'Tính độc lập và đánh giá thực nghiệm: các cơ chế trên' in p.text,
            'old_text': 'Mức độ đóng góp và hiệu quả thực tế của từng cơ chế ứng viên được đánh giá định lượng thông qua phân tích triệt tiêu tại Chương 3.',
            'new_text': 'Các cơ chế ứng viên này thuộc thiết kế kiến trúc đề xuất nhằm kiểm soát độ chân thực đồ thị; việc hiện thực hóa và đánh giá định lượng thông qua phân tích triệt tiêu được định vị cho các nghiên cứu tiếp theo (chưa được kiểm chứng trong chiến dịch thực nghiệm Stage A2 hiện tại).'
        },
        {
            'id': 'topk_sampling',
            'desc': 'Top-k temporal sampling marked design-only',
            'anchor_fn': lambda p: 'Top-k Temporal Attention Sampling' in p.text,
            'old_text': 'áp dụng cơ chế lấy mẫu lân cận có chọn lọc theo trọng số thời gian Top-k Temporal Attention Sampling, ưu tiên tổng hợp thông điệp từ các đỉnh lân cận có hoạt động gần nhất thay vì mở rộng toàn bộ cây phụ thuộc nhiều bước. Cơ chế này được thiết kế để đánh giá đối sánh với các chính sách lấy mẫu toàn bộ lân cận Full Neighborhood và lấy mẫu theo độ mới Recency Sampling tại Chương 3, nhằm kiểm tra thực nghiệm liệu chính sách sampling có gây mất mát các bằng chứng APT dài hạn hay không.',
            'new_text': 'chuyên đề đề xuất cơ chế ứng viên lấy mẫu lân cận có chọn lọc theo trọng số thời gian Top-k Temporal Attention Sampling, ưu tiên tổng hợp thông điệp từ các đỉnh lân cận có hoạt động gần nhất thay vì mở rộng toàn bộ cây phụ thuộc nhiều bước. Đây là thiết kế mở rộng dự kiến phục vụ đối sánh với các chính sách lấy mẫu toàn bộ lân cận (Full Neighborhood) và lấy mẫu theo độ mới (Recency Sampling) trong các nghiên cứu tương lai; thành phần này chưa được hiện thực và chưa kiểm chứng thực nghiệm trong chiến dịch Stage A2 hiện tại.'
        },
        {
            'id': 'infonce_barlow',
            'desc': 'InfoNCE and Barlow Twins citation correction',
            'anchor_fn': lambda p: 'Từ phân tích phương pháp luận trên, chuyên đề lựa chọn VICReg' in p.text,
            'old_text': 'trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [38], [37] và Barlow Twins [11] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo. [41] [21] [13]',
            'new_text': 'trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [41], [21] và Barlow Twins [13] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo.'
        },
        {
            'id': 'mil_proposed',
            'desc': 'Attention-MIL marked proposed/optional',
            'anchor_fn': lambda p: 'Cybersecurity Bag-Instance Mapping, Đề xuất của đề tài / Ours' in p.text,
            'old_text': 'Chuyên đề áp dụng cơ chế Attention-based Deep MIL của Ilse et al.  [44], nhưng thiết kế cơ chế ánh xạ Túi, Thực thể đặc thù cho bài toán an ninh mạng (Cybersecurity Bag-Instance Mapping, Đề xuất của đề tài / Ours):',
            'new_text': 'Chuyên đề đề xuất áp dụng cơ chế Attention-based Deep MIL của Ilse et al.  [44] (như một thiết kế mở rộng tùy chọn, chưa hiện thực và chưa kiểm chứng trong chiến dịch Stage A2 hiện tại), kết hợp thiết kế cơ chế ánh xạ Túi – Thực thể đặc thù cho bài toán an ninh mạng (Cybersecurity Bag-Instance Mapping, Đề xuất của đề tài / Ours):'
        },
        {
            'id': 'mil_classifier',
            'desc': 'Attention-MIL classifier boundary (OMML paragraph)',
            'anchor_fn': lambda p: 'Phân định ranh giới giữa Khung trích xuất chuẩn tắc và Đầu phân lớp phụ trợ MIL:' in p.text,
            'old_text': 'Cơ chế Gated Attention-MIL trang bị một đầu phân lớp túi phụ trợ ',
            'new_text': 'Cơ chế Gated Attention-MIL dự kiến trang bị một đầu phân lớp túi phụ trợ '
        },
        {
            'id': 'sha256_fp',
            'desc': 'SHA-256 content fingerprint terminology',
            'anchor_fn': lambda p: 'Hàm compute_file_sha256 đọc tệp tin dưới dạng nhị phân' in p.text,
            'old_text': 'Mã băm SHA-256 thu được cung cấp chữ ký toàn vẹn không thể bác bỏ, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường.',
            'new_text': 'Mã băm SHA-256 thu được cung cấp dấu vân tay nội dung dùng để kiểm tra tính toàn vẹn của tệp khi đối chiếu với giá trị tham chiếu tin cậy, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường.'
        },
        {
            'id': 'hdfs_size',
            'desc': 'HDFS dataset size from manifest',
            'anchor_fn': lambda p: '6ca6c5bc' in p.text and 'HDFS_1.tar.gz' in p.text,
            'old_text': 'Tệp dữ liệu gốc HDFS_1.tar.gz, dung lượng 44.7 GB chưa nén, chứa tổng cộng 11,175,629 sự kiện log hệ thống được phân nhóm thành 575,061 phiên khối Block Session ID, có mã băm toàn vẹn SHA-256: 6ca6c5bc​2671c66a​fecee936​9a2fdac6​06bf3399​7a2494ac​66aa411f​e3e95169.',
            'new_text': 'Tệp lưu trữ HDFS_1.tar.gz có kích thước 161,886,385 byte (mã băm SHA-256: 6ca6c5bc​2671c66a​fecee936​9a2fdac6​06bf3399​7a2494ac​66aa411f​e3e95169); sau khi xử lý, tập dữ liệu chứa 11,175,629 bản ghi log được ánh xạ tới 575,061 block session.'
        },
        {
            'id': 'split_arp_data',
            'desc': 'Arp [10] and datasets [14], [16], [17], [9] citation correction',
            'anchor_fn': lambda p: 'temporal snooping' in p.text,
            'old_text': 'tuân thủ khuyến nghị tránh rò rỉ thời gian (temporal snooping) của Arp et al. [8]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [12], LANL [13], HDFS [18], BGL [42]); trong đó, tập dữ liệu HDFS đóng vai trò là môi trường thực thi chính thức cho chiến dịch tiền huấn luyện Stage A2 hiện hành, còn các tập dữ liệu quy mô lớn còn lại định vị bối cảnh mở rộng cho các giai đoạn tiếp theo. Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và xác thực bằng chữ ký mật mã: [10]',
            'new_text': 'tuân thủ khuyến nghị tránh rò rỉ thời gian (temporal snooping) của Arp et al. [10]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [14], LANL [16], HDFS [17], [9], BGL [9]); trong đó, tập dữ liệu HDFS đóng vai trò là môi trường thực thi chính thức cho chiến dịch tiền huấn luyện Stage A2 hiện hành, còn các tập dữ liệu quy mô lớn còn lại định vị bối cảnh mở rộng cho các giai đoạn tiếp theo. Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và kiểm soát tính toàn vẹn bằng mã băm mật mã SHA-256 trong tệp manifest.'
        },
        {
            'id': 'frozen_probe_fairness',
            'desc': 'Frozen probe determinism overclaim lowering',
            'anchor_fn': lambda p: 'Quy trình huấn luyện bộ dò tuyến tính sử dụng tầng tuyến tính duy nhất nn.Linear(128, 1)' in p.text,
            'old_text': 'bảo đảm tính công bằng tuyệt đối khi đo lường khả năng tách biệt thông tin an ninh của biểu diễn tự giám sát.',
            'new_text': 'giúp quá trình xáo trộn có tính xác định và nhất quán giữa các lần đánh giá khi đo lường khả năng tách biệt thông tin an ninh của biểu diễn tự giám sát.'
        },
        {
            'id': 'ap_roc_ties',
            'desc': 'AP/ROC ties handling overclaim lowering',
            'anchor_fn': lambda p: 'tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc' in p.text,
            'old_text': 'loại bỏ hoàn toàn các sai số do tính toán thứ hạng thô và thiết lập tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc.',
            'new_text': 'tránh sai lệch do triển khai thủ công không nhất quán trong xử lý thứ hạng/ties và thiết lập tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc.'
        },
        {
            'id': 'heading_324',
            'desc': 'Heading 3.2.4 manual reproduction wording',
            'anchor_fn': lambda p: 'Kiểm chứng tái lập' in p.text and p.style.name == 'Heading 3',
            'old_text': 'Kiểm chứng tái lập độc lập trên máy trạm',
            'new_text': 'Kiểm chứng tái lập thủ công trên máy trạm'
        },
        {
            'id': 'manual_324_intro',
            'desc': 'Section 3.2.4 manual reproduction intro narrowing',
            'anchor_fn': lambda p: 'manual_reproduction/run_manual_sequence42.ps1' in p.text,
            'old_text': 'Nhằm xác thực tính độc lập, khách quan và năng lực tái lập thực tế của hệ thống mã nguồn mà không phụ thuộc vào phiên tương tác hay phần mềm điều phối bên ngoài, sinh viên đã trực tiếp thực thi',
            'new_text': 'Nhằm kiểm tra khả năng tái lập thủ công của pipeline trong môi trường thực thi đã ghi nhận, sinh viên trực tiếp thực thi'
        },
        {
            'id': 'manual_324_vram',
            'desc': 'Section 3.2.4 VRAM claim lowering',
            'anchor_fn': lambda p: '170.45 MB VRAM' in p.text,
            'old_text': 'khẳng định khả năng vận hành hoàn toàn nằm trong giới hạn tài nguyên khả thi của máy trạm cá nhân.',
            'new_text': 'cho thấy cấu hình thực nghiệm này có thể vận hành trong giới hạn tài nguyên của máy trạm được sử dụng.'
        },
        {
            'id': 'manual_324_run_title',
            'desc': 'Section 3.2.4 run title manual reproduction',
            'anchor_fn': lambda p: '170.45 MB VRAM' in p.text,
            'old_text': 'Đợt chạy thực nghiệm độc lập (với định danh Run ID CONF_SEQUENCE_ONLY_seed42_1789724929',
            'new_text': 'Đợt chạy thực nghiệm tái lập thủ công (với định danh Run ID CONF_SEQUENCE_ONLY_seed42_1789724929'
        },
        {
            'id': 'manual_324_conclusion',
            'desc': 'Section 3.2.4 conclusion reproduction narrowing',
            'anchor_fn': lambda p: 'POST_TRAINING_INTERNAL_VAL_80_20_PROBE' in p.text,
            'old_text': 'Đợt chạy tái lập thủ công này đã tái hiện chính xác quỹ đạo hội tụ, cơ chế dừng sớm và các chỉ số kiểm toán của đợt chạy xác nhận Seed 42, cho thấy tính xác định và độ tin cậy thực nghiệm của pipeline nghiên cứu.',
            'new_text': 'kết quả cho thấy phiên chạy có thể tái lập các chỉ số kiểm toán và hành vi dừng sớm đã ghi nhận trong điều kiện môi trường và artifact tương ứng.'
        },
        {
            'id': 'table_37b_caption',
            'desc': 'Table 3.7b caption manual reproduction',
            'anchor_fn': lambda p: 'Bảng 3.7b:' in p.text and p.style.name == 'Caption',
            'old_text': 'Bảng 3.7b: Thông số kỹ thuật và kết quả đo đạc từ đợt chạy kiểm chứng độc lập Sequence-Only (Seed 42)',
            'new_text': 'Bảng 3.7b: Thông số kỹ thuật và kết quả đo đạc từ đợt chạy kiểm chứng tái lập thủ công Sequence-Only (Seed 42)'
        },
        {
            'id': 'fig_31_caption',
            'desc': 'Figure 3.1 caption manual reproduction',
            'anchor_fn': lambda p: 'Hình 3.1: Giao diện PowerShell' in p.text and p.style.name == 'Caption',
            'old_text': 'Hình 3.1: Giao diện PowerShell khi chạy kiểm chứng độc lập Sequence-Only (Seed 42), thể hiện tiến trình 6 epoch, kích hoạt early stopping tại epoch 6 (checkpoint tối ưu tại epoch 3) và hoàn tất lưu vết thực nghiệm.',
            'new_text': 'Hình 3.1: Giao diện PowerShell khi chạy kiểm chứng tái lập thủ công Sequence-Only (Seed 42), thể hiện tiến trình 6 epoch, kích hoạt early stopping tại epoch 6 (checkpoint tối ưu tại epoch 3) và hoàn tất lưu vết thực nghiệm.'
        },
        {
            'id': 'fig_31_desc',
            'desc': 'Figure 3.1 description removed AI wording',
            'anchor_fn': lambda p: 'Hình 3.1 ghi nhận nhật ký console' in p.text,
            'old_text': 'trên máy trạm ngoài môi trường trợ lý AI.',
            'new_text': 'trên máy trạm trong cửa sổ dòng lệnh PowerShell độc lập.'
        }
    ]

    applied_count = 0
    noop_count = 0
    plan_to_apply = []

    for c in corrections:
        cid = c['id']
        if cid == 'llm_preface':
            has_llm = any('Mô hình ngôn ngữ lớn' in p.text for p in doc.paragraphs)
            if not has_llm:
                print(f"[{cid}] NEW_ALREADY_PRESENT: LLM preface sentence already removed.")
                noop_count += 1
            else:
                matched_p = [p for p in doc.paragraphs if c['anchor_fn'](p)]
                if len(matched_p) != 1:
                    raise RuntimeError(f"[{cid}] AMBIGUOUS_OR_MISSING: matched {len(matched_p)} paragraphs")
                plan_to_apply.append((c, matched_p[0]))
            continue

        matched_p = [p for p in body_paragraphs if c['anchor_fn'](p)]
        if len(matched_p) != 1:
            raise RuntimeError(f"[{cid}] AMBIGUOUS_OR_MISSING: matched {len(matched_p)} paragraphs (expected 1)")

        p = matched_p[0]
        old_in = c['old_text'] in p.text
        new_in = c['new_text'] in p.text

        if new_in and not old_in:
            print(f"[{cid}] NEW_ALREADY_PRESENT: Already applied.")
            noop_count += 1
        elif old_in and not new_in:
            print(f"[{cid}] OLD_FOUND_ONCE: Ready to apply correction.")
            plan_to_apply.append((c, p))
        else:
            raise RuntimeError(f"[{cid}] AMBIGUOUS_OR_MISSING: old_in={old_in}, new_in={new_in}")

    if not plan_to_apply:
        print(f"\n[IDEMPOTENCE-PASS] All {noop_count} corrections already present. No modifications needed.")
        sha_after = compute_sha256(docx_file)
        print(f"DOCX SHA-256 before: {sha_before}")
        print(f"DOCX SHA-256 after:  {sha_after}")
        assert sha_before == sha_after, "DOCX SHA changed even with 0 corrections applied!"
        return True

    # Apply planned corrections
    for c, p in plan_to_apply:
        cid = c['id']
        old_txt = c['old_text']
        new_txt = c['new_text']
        replace_in_paragraph_runs(p, old_txt, new_txt)
        applied_count += 1
        print(f"[{cid}] APPLIED: {c['desc']}")

    # Save DOCX
    doc.save(str(docx_file))
    print(f"\nSaved updated DOCX with {applied_count} applied corrections ({noop_count} were already present).")

    # Verify OMML count after python-docx save
    doc_check = docx.Document(str(docx_file))
    check_omml = len(doc_check._element.xpath('.//m:oMath'))
    print(f"OMML count after python-docx edit: {check_omml}")
    assert check_omml == 606, f"OMML count mismatch! Expected 606, found {check_omml}"

    # Update TOC and List of Figures / Tables and Export PDF via Word COM
    print("\nUpdating Word fields, TOC, List of Figures and exporting PDF via Word COM...")
    pythoncom.CoInitialize()
    try:
        word = win32.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = 0
        wdoc = word.Documents.Open(str(docx_file.resolve()))

        # Update all fields (covers citations, page refs, etc.)
        wdoc.Fields.Update()

        # Update Table of Contents
        for toc in wdoc.TablesOfContents:
            toc.Update()

        # Update Tables of Figures / Tables
        for tof in wdoc.TablesOfFigures:
            tof.Update()

        # Save the updated DOCX with recomputed fields and TOC
        wdoc.Save()

        # Export PDF
        wdoc.ExportAsFixedFormat(
            OutputFileName=str(pdf_file.resolve()),
            ExportFormat=17,  # wdExportFormatPDF
            OpenAfterExport=False,
            OptimizeFor=0,  # wdExportOptimizeForPrint
            CreateBookmarks=1,  # wdExportCreateHeadingBookmarks
            DocStructureTags=True
        )
        wdoc.Close(False)
        word.Quit()
        print(f"Successfully updated fields, TOC, and exported PDF to {pdf_file}")
    except Exception as e:
        print(f"Word COM error: {e}")
        raise
    finally:
        pythoncom.CoUninitialize()

    # Final OMML verification
    doc_final = docx.Document(str(docx_file))
    final_omml = len(doc_final._element.xpath('.//m:oMath'))
    print(f"Final OMML count after Word COM: {final_omml}")
    assert final_omml == 606, f"Final OMML count mismatch! Expected 606, found {final_omml}"

    sha_final = compute_sha256(docx_file)
    print(f"Final DOCX SHA-256: {sha_final}")
    return True

if __name__ == "__main__":
    run_corrections(docx_path, pdf_path)
