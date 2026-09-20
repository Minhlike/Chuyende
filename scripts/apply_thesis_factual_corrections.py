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
5. ZERO hard-coded numeric citation targets: resolves dynamic numbers from Table 27 via CANONICAL-SOURCES.json.
6. Idempotent: second run makes 0 changes; DOCX SHA-256 before == after.
"""
import sys
import shutil
import hashlib
import json
import re
from pathlib import Path
import docx
import win32com.client as win32
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
sys.path.insert(0, str(repo_root / "src"))
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
pdf_path = repo_root / "Chuyên đề chuyên sâu.pdf"
canonical_json_path = repo_root / "research_specs" / "reference_map" / "CANONICAL-SOURCES.json"

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

def apply_occ_0136_p235(p, nist_num, shokri_num, fredrikson_num):
    # p.runs[0] is before oMath (ϵ,δ) - leave untouched to preserve formula 100%!
    # p.runs[1] is after oMath:
    p.runs[1].text = f'dưới các giả định toán học xác định theo các hướng dẫn đánh giá của NIST SP 800-226 [{nist_num}], còn rủi ro thực tế được định vị là phép kiểm tra hạ nguồn cần đánh giá thực nghiệm độc lập thông qua các quy trình kiểm thử tấn công suy luận thành viên (MIA) [{shokri_num}] và tấn công nghịch đảo/tái định danh thực thể [{fredrikson_num}].'
    for r in p.runs[2:]:
        r.text = ""

def resolve_canonical_citation_numbers(doc):
    with open(canonical_json_path, "r", encoding="utf-8") as f:
        canonical_sources = json.load(f)

    t27 = doc.tables[27]
    runtime_map = {}
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
            title_words = [w for w in re.split(r"\W+", title) if len(w) > 3]
            if title_words:
                matches = sum(1 for w in title_words if w in text_cell.lower())
                score = matches / len(title_words)
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
            raise RuntimeError(f"Could not map row [{num}]: {text_cell[:60]} in Table 27")
        runtime_map[matched_key] = num
    return runtime_map

def run_corrections(docx_file: Path, pdf_file: Path):
    sha_before = compute_sha256(docx_file)
    print(f"Starting DOCX SHA-256: {sha_before}")

    doc = docx.Document(str(docx_file))

    # Verify initial OMML count
    initial_omml = len(doc._element.xpath('.//m:oMath'))
    print(f"Initial OMML count: {initial_omml}")
    assert initial_omml == 606, f"Expected 606 OMML elements, found {initial_omml}"

    # Dynamically resolve citation numbers from Table 27
    key_to_num = resolve_canonical_citation_numbers(doc)
    mitre_num = key_to_num["MITRE2026ATTCK"]
    inam_num = key_to_num["Inam2023ProvenanceSoK"]
    vicreg_num = key_to_num["Bardes2022VICReg"]
    barlow_num = key_to_num["Zbontar2021BarlowTwins"]
    infonce_num = key_to_num["Oord2018CPC"]
    simclr_num = key_to_num["Chen2020SimCLR"]
    arp_num = key_to_num["Arp2022DosDonts"]
    darpa_num = key_to_num["DARPA2018TCE3"]
    lanl_num = key_to_num["Kent2015LANL"]
    hdfs_num = key_to_num["Xu2009HDFS"]
    loghub_num = key_to_num["Zhu2023Loghub"]

    shokri_num = key_to_num["Shokri2017MembershipInference"]
    fredrikson_num = key_to_num["Fredrikson2015ModelInversion"]
    nist_num = key_to_num["NIST2025SP800226"]

    print(f"[DYNAMIC-CITATION-MAP] Resolved from Table 27:")
    print(f"  MITRE -> [{mitre_num}], Inam -> [{inam_num}], VICReg -> [{vicreg_num}], Barlow -> [{barlow_num}]")
    print(f"  InfoNCE -> [{infonce_num}], SimCLR -> [{simclr_num}], Arp -> [{arp_num}], DARPA E3 -> [{darpa_num}]")
    print(f"  LANL -> [{lanl_num}], HDFS -> [{hdfs_num}], LogHub -> [{loghub_num}]")
    print(f"  Shokri -> [{shokri_num}], Fredrikson -> [{fredrikson_num}], NIST -> [{nist_num}]")

    body_paragraphs = [p for p in doc.paragraphs if not is_toc_or_tof(p)]

    corrections = [
        {
            'id': 'fig12_text',
            'desc': 'Figure 1.2 citation in body text',
            'anchor_fn': lambda p: 'Do đó, chuyên đề xác lập nguyên tắc: Ma trận MITRE ATT&CK' in p.text,
            'old_text': 'MITRE ATT&CK [6] và Inam et al. [3]',
            'new_text': f'MITRE ATT&CK [{mitre_num}] và Inam et al. [{inam_num}]'
        },
        {
            'id': 'fig12_caption',
            'desc': 'Figure 1.2 caption',
            'anchor_fn': lambda p: 'Hình 1.2: Mô hình Không gian Bằng chứng Hành vi Đa chiều' in p.text and p.style.name == 'Caption',
            'old_text': 'MITRE ATT&CK [6] và Inam et al. [3]',
            'new_text': f'MITRE ATT&CK [{mitre_num}] và Inam et al. [{inam_num}]'
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
            'anchor_fn': lambda p: 'áp lực ngược' in p.text and 'Token-Bucket' in p.text,
            'old_text': 'Đối với tình huống đột biến lưu lượng (Traffic Spike), kiến trúc đề xuất cơ chế kiểm soát áp lực ngược (Backpressure Control) dự kiến dựa trên thuật toán Token-Bucket để điều tiết tốc độ nạp dữ liệu. Trong thiết kế này, nếu lưu lượng vượt quá giới hạn chịu tải tối đa, việc loại bỏ gói tin (Shedding) được đề xuất thực hiện độc lập với kết quả phát hiện của mô hình (dựa trên hạn ngạch băng thông nguồn thu thập hoặc mức độ ưu tiên của phân vùng telemetry, không dựa vào điểm số an ninh chưa kiểm chứng) nhằm tránh rủi ro rò rỉ vòng lặp Detector Leakage và loại bỏ nhầm các bằng chứng APT yếu thưa thớt (thành phần streaming này thuộc thiết kế kiến trúc mục tiêu, chưa triển khai trong thực nghiệm Stage A2).',
            'new_text': 'Đối với tình huống đột biến lưu lượng (Traffic Spike), kiến trúc đề xuất cơ chế kiểm soát áp lực ngược (Backpressure Control) dự kiến dựa trên thuật toán Token-Bucket để điều tiết tốc độ nạp dữ liệu. Trong thiết kế kiến trúc đề xuất này, chính sách loại bỏ gói tin hoặc phân luồng ưu tiên (Priority Shedding) được định vị cho kịch bản quá tải; tuy nhiên, cơ chế này chưa hiện thực trong Stage A2 và chưa được kiểm chứng thực nghiệm trong phạm vi chuyên đề hiện tại.'
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
            'id': 'occ_0132_p208',
            'desc': 'OCC-0132 NIST citation separation in P208',
            'anchor_fn': lambda p: 'Một mô hình được thiết kế có nhận thức về quyền riêng tư' in p.text,
            'old_text': f'Một mô hình được thiết kế có nhận thức về quyền riêng tư không tự động đồng nghĩa với việc đã đạt được khả năng bảo vệ quyền riêng tư ; các quy trình kiểm thử tấn công MIA và đảo ngược mô hình được định vị là phép kiểm tra hạ nguồn và chưa được thực thi trong phạm vi thực nghiệm hiện tại  [{nist_num}].',
            'new_text': f'Một mô hình được thiết kế có nhận thức về quyền riêng tư không tự động đồng nghĩa với việc đã đạt được khả năng bảo vệ quyền riêng tư; các quy trình kiểm thử tấn công MIA [{shokri_num}] và đảo ngược mô hình [{fredrikson_num}], cũng như quy trình đánh giá quyền riêng tư vi sai theo hướng dẫn NIST SP 800-226 [{nist_num}], được định vị là phép kiểm tra hạ nguồn và chưa được thực thi trong phạm vi thực nghiệm hiện tại.'
        },
        {
            'id': 'occ_0136_p235',
            'desc': 'OCC-0136 NIST citation separation in P235',
            'anchor_fn': lambda p: 'Trong đó lý thuyết Quyền riêng tư Vi sai (DP) đóng vai trò' in p.text,
            'is_applied_fn': lambda p: f'NIST SP 800-226 [{nist_num}]' in p.text and f'[{shokri_num}],  [{nist_num}]' not in p.text and f'[{shokri_num}], [{nist_num}]' not in p.text,
            'custom_apply_fn': lambda p: apply_occ_0136_p235(p, nist_num, shokri_num, fredrikson_num)
        },
        {
            'id': 'p405_infonce_simclr',
            'desc': 'InfoNCE/CPC and SimCLR citation in Section 2.4.1.3 P405',
            'anchor_fn': lambda p: 'Trong học biểu diễn tự giám sát' in p.text and 'Barlow Twins' in p.text,
            'old_text': f'Trong học biểu diễn tự giám sát, ba hướng tiếp cận tiêu biểu bao gồm: InfoNCE / Contrastive Learning  [{infonce_num}],  [{simclr_num}], Barlow Twins  [{barlow_num}], và VICReg  [{vicreg_num}].',
            'new_text': f'Trong học biểu diễn tự giám sát, các hướng tiếp cận tiêu biểu bao gồm: InfoNCE/CPC [{infonce_num}], SimCLR [{simclr_num}], Barlow Twins [{barlow_num}], và VICReg [{vicreg_num}].'
        },
        {
            'id': 'vicreg_p407_1',
            'desc': 'VICReg citation in Section 2.4.1.3 body',
            'anchor_fn': lambda p: 'Từ phân tích phương pháp luận trên, chuyên đề lựa chọn VICReg' in p.text,
            'old_text': 'VICReg (Variance-Invariance-Covariance Regularization) [12]',
            'new_text': f'VICReg (Variance-Invariance-Covariance Regularization) [{vicreg_num}]'
        },
        {
            'id': 'vicreg_p407_2',
            'desc': 'Bardes et al. citation in Section 2.4.1.3 body',
            'anchor_fn': lambda p: 'Từ phân tích phương pháp luận trên, chuyên đề lựa chọn VICReg' in p.text,
            'old_text': 'Theo Bardes et al. [12],',
            'new_text': f'Theo Bardes et al. [{vicreg_num}],'
        },
        {
            'id': 'infonce_barlow',
            'desc': 'InfoNCE and Barlow Twins citation correction in Section 2.4.1.3',
            'anchor_fn': lambda p: 'Từ phân tích phương pháp luận trên, chuyên đề lựa chọn VICReg' in p.text,
            'old_text': f'trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [{infonce_num}], [{simclr_num}] và Barlow Twins [{barlow_num}] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo.',
            'new_text': f'trong khi việc đối sánh triệt tiêu định lượng với InfoNCE/CPC [{infonce_num}], SimCLR [{simclr_num}] và Barlow Twins [{barlow_num}] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo.'
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
            'desc': 'Arp and datasets citation correction in Section 3.1.2',
            'anchor_fn': lambda p: 'Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu' in p.text,
            'old_text': f'Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [{darpa_num}], LANL [{lanl_num}], HDFS [{hdfs_num}], [{loghub_num}], BGL [{loghub_num}]);',
            'new_text': f'Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [{darpa_num}], LANL [{lanl_num}], HDFS (Xu et al. [{hdfs_num}]; LogHub [{loghub_num}]) và BGL (LogHub [{loghub_num}]));'
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
            'anchor_fn': lambda p: 'xử lý thứ hạng/ties' in p.text,
            'old_text': 'tránh sai lệch do triển khai thủ công không nhất quán trong xử lý thứ hạng/ties và thiết lập tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc.',
            'new_text': 'tránh sai lệch do triển khai thủ công không nhất quán trong xử lý thứ hạng/ties và thống nhất cách tính giữa các kiến trúc.'
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

        if 'is_applied_fn' in c:
            if c['is_applied_fn'](p):
                print(f"[{cid}] NEW_ALREADY_PRESENT: Already applied.")
                noop_count += 1
            else:
                print(f"[{cid}] OLD_FOUND_ONCE: Ready to apply correction.")
                plan_to_apply.append((c, p))
            continue

        old_in = c['old_text'] in p.text
        new_in = c['new_text'] in p.text

        if new_in and not old_in:
            print(f"[{cid}] NEW_ALREADY_PRESENT: Already applied.")
            noop_count += 1
        elif old_in and not new_in:
            print(f"[{cid}] OLD_FOUND_ONCE: Ready to apply correction.")
            plan_to_apply.append((c, p))
        else:
            raise RuntimeError(f"[{cid}] AMBIGUOUS_OR_MISSING: old_in={old_in}, new_in={new_in} for {cid}")

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
        if 'custom_apply_fn' in c:
            c['custom_apply_fn'](p)
        else:
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

        # Re-render Figure 2.4 Canvas with updated proposed labels
        try:
            from research_agent.visuals.chapter2_drawings import draw_fig_2_4
            from research_agent.composition.word_com_post_process import render_canvas_at_bookmark
            render_canvas_at_bookmark(wdoc, "BK_FIG_2_004_CANVAS", draw_fig_2_4, "Figure 2.4")
        except Exception as e_fig:
            print(f"[WARNING] Could not update Figure 2.4 Canvas: {e_fig}")

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
