# -*- coding: utf-8 -*-
"""
Surgical Factual, Citation, and Implementation Boundary Corrections for Chuyên đề chuyên sâu.docx
"""
import sys
import shutil
import hashlib
from pathlib import Path
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
import win32com.client as win32
import pythoncom

sys.stdout.reconfigure(encoding='utf-8')

repo_root = Path(r"D:\Research")
docx_path = repo_root / "Chuyên đề chuyên sâu.docx"
pdf_path = repo_root / "Chuyên đề chuyên sâu.pdf"

backup_path = repo_root / "Chuyên đề chuyên sâu.pre_audit_backup.docx"
if not backup_path.exists():
    shutil.copy2(docx_path, backup_path)
    print(f"Created backup at {backup_path}")

doc = docx.Document(str(docx_path))

# Check initial OMML count
initial_omml = len(doc._element.xpath('.//m:oMath'))
print(f"Initial OMML count: {initial_omml}")
assert initial_omml == 606, f"Expected 606 OMML elements, found {initial_omml}"

# Helper function to replace text across runs in a paragraph while preserving run formatting
def replace_in_paragraph_runs(p, old_text, new_text):
    full_text = p.text
    if old_text not in full_text:
        raise ValueError(f"Target text not found in paragraph:\nExpected: {old_text}\nActual: {full_text}")
    
    # If there's only one run or old_text is completely within one run:
    for r in p.runs:
        if old_text in r.text:
            r.text = r.text.replace(old_text, new_text)
            return
            
    # If old_text spans across multiple runs, we consolidate text into the first matching run
    # while preserving other runs (e.g. if there's an oMath or formatting boundary)
    # Check if this paragraph has oMath
    has_omml = len(p._p.xpath('.//m:oMath')) > 0
    if not has_omml:
        # We can safely put new_text into first run and empty the rest, preserving first run's font/size
        first_run = p.runs[0] if p.runs else p.add_run()
        first_run.text = full_text.replace(old_text, new_text)
        for r in p.runs[1:]:
            r.text = ""
    else:
        # With OMML, do surgical replacement across non-OMML text runs
        # Find which runs contain parts of old_text
        for r in p.runs:
            for part in old_text.split():
                if part in r.text:
                    r.text = r.text.replace(part, "")
        # Put new_text in first run
        p.runs[0].text = full_text.replace(old_text, new_text)

# 1. p[49] (TOC: Heading 3.2.4)
p49 = doc.paragraphs[49]
assert "Kiểm chứng tái lập độc lập trên máy trạm" in p49.text
p49.text = p49.text.replace("Kiểm chứng tái lập độc lập trên máy trạm", "Kiểm chứng tái lập thủ công trên máy trạm")
print("Updated p[49] (TOC 3.2.4)")

# 2. p[64] (TOC: Figure 1.2 caption)
p64 = doc.paragraphs[64]
assert "Inam et al. [1]2 [6] [3]" in p64.text or "MITRE ATT&CK [4]" in p64.text
p64.text = p64.text.replace("MITRE ATT&CK [4] và Inam et al. [1]2 [6] [3]", "MITRE ATT&CK [6] và Inam et al. [3]")
print("Updated p[64] (TOC Figure 1.2)")

# 3. p[97] (Lời nói đầu - LLM claim removal)
p97 = doc.paragraphs[97]
llm_sentence = "Mô hình ngôn ngữ lớn mở thêm khả năng chuẩn hóa và diễn giải log, nhưng vẫn chịu hạn chế về chi phí, độ trễ, tính ổn định và bảo mật dữ liệu  [2]. "
assert llm_sentence in p97.text or "Mô hình ngôn ngữ lớn mở thêm khả năng" in p97.text
if llm_sentence in p97.text:
    replace_in_paragraph_runs(p97, llm_sentence, "")
else:
    # try without double space
    llm_sentence_single = "Mô hình ngôn ngữ lớn mở thêm khả năng chuẩn hóa và diễn giải log, nhưng vẫn chịu hạn chế về chi phí, độ trễ, tính ổn định và bảo mật dữ liệu [2]. "
    replace_in_paragraph_runs(p97, llm_sentence_single, "")
print("Updated p[97] (Removed unsupported LLM claim)")

# 4. p[127] (Text referencing Figure 1.2)
p127 = doc.paragraphs[127]
assert "MITRE ATT&CK [4] và Inam et al. [1]2" in p127.text
replace_in_paragraph_runs(p127, "MITRE ATT&CK [4] và Inam et al. [1]2", "MITRE ATT&CK [6] và Inam et al. [3]")
print("Updated p[127] (Figure 1.2 reference)")

# 5. p[130] (Figure 1.2 Caption)
p130 = doc.paragraphs[130]
assert "MITRE ATT&CK [4] và Inam et al. [1]2 [6] [3]" in p130.text
replace_in_paragraph_runs(p130, "MITRE ATT&CK [4] và Inam et al. [1]2 [6] [3]", "MITRE ATT&CK [6] và Inam et al. [3]")
print("Updated p[130] (Figure 1.2 caption)")

# 6. p[132] (DARPA TC Ground Truth)
p132 = doc.paragraphs[132]
old_darpa = "trong đó các kịch bản tấn công và diễn tập red-team trong các engagement của chương trình được gán nhãn ở mức độ hạt tiến trình và luồng phụ thuộc;"
new_darpa = "trong đó các kịch bản tấn công của đội Red Team được ghi nhận qua các báo cáo kịch bản (ground-truth reports/annotations), cho phép ánh xạ và suy diễn nhãn ở mức tiến trình và luồng phụ thuộc liên quan đến đợt tấn công, thay vì toàn bộ dữ liệu viễn trắc nền đều có nhãn sẵn ở mức hạt nhân;"
assert old_darpa in p132.text
replace_in_paragraph_runs(p132, old_darpa, new_darpa)
print("Updated p[132] (DARPA TC ground truth description)")

# 7. p[244] (Token-Bucket Backpressure & Shedding)
p244 = doc.paragraphs[244]
old_tb = "Khi hệ thống gặp hiện tượng đột biến lưu lượng Traffic Spike, cơ chế kiểm soát áp lực ngược Backpressure Control dựa trên thuật toán Token-Bucket điều tiết tốc độ nạp dữ liệu. Nếu lưu lượng vượt quá giới hạn chịu tải tối đa, việc loại bỏ gói tin (Shedding) được thực hiện hoàn toàn độc lập với kết quả phát hiện của mô hình (dựa trên hạn ngạch băng thông nguồn thu thập hoặc mức độ ưu tiên của phân vùng telemetry, tuyệt đối không dựa vào điểm số an ninh chưa kiểm chứng) nhằm tránh rủi ro rò rỉ vòng lặp Detector Leakage và loại bỏ nhầm các bằng chứng APT yếu thưa thớt."
new_tb = "Đối với tình huống đột biến lưu lượng (Traffic Spike), kiến trúc đề xuất cơ chế kiểm soát áp lực ngược (Backpressure Control) dự kiến dựa trên thuật toán Token-Bucket để điều tiết tốc độ nạp dữ liệu. Trong thiết kế này, nếu lưu lượng vượt quá giới hạn chịu tải tối đa, việc loại bỏ gói tin (Shedding) được đề xuất thực hiện độc lập với kết quả phát hiện của mô hình (dựa trên hạn ngạch băng thông nguồn thu thập hoặc mức độ ưu tiên của phân vùng telemetry, không dựa vào điểm số an ninh chưa kiểm chứng) nhằm tránh rủi ro rò rỉ vòng lặp Detector Leakage và loại bỏ nhầm các bằng chứng APT yếu thưa thớt (thành phần streaming này thuộc thiết kế kiến trúc mục tiêu, chưa triển khai trong thực nghiệm Stage A2)."
assert old_tb in p244.text
replace_in_paragraph_runs(p244, old_tb, new_tb)
print("Updated p[244] (Token-Bucket Backpressure design-only)")

# 8. p[352] (Graph-Fidelity Candidates)
p352 = doc.paragraphs[352]
old_gf = "Mức độ đóng góp và hiệu quả thực tế của từng cơ chế ứng viên được đánh giá định lượng thông qua phân tích triệt tiêu tại Chương 3."
new_gf = "Các cơ chế ứng viên này thuộc thiết kế kiến trúc đề xuất nhằm kiểm soát độ chân thực đồ thị; việc hiện thực hóa và đánh giá định lượng thông qua phân tích triệt tiêu được định vị cho các nghiên cứu tiếp theo (chưa được kiểm chứng trong chiến dịch thực nghiệm Stage A2 hiện tại)."
assert old_gf in p352.text
replace_in_paragraph_runs(p352, old_gf, new_gf)
print("Updated p[352] (Graph-fidelity candidates design-only)")

# 9. p[381] (Top-k Temporal Attention Sampling)
p381 = doc.paragraphs[381]
old_topk = "áp dụng cơ chế lấy mẫu lân cận có chọn lọc theo trọng số thời gian Top-k Temporal Attention Sampling, ưu tiên tổng hợp thông điệp từ các đỉnh lân cận có hoạt động gần nhất thay vì mở rộng toàn bộ cây phụ thuộc nhiều bước. Cơ chế này được thiết kế để đánh giá đối sánh với các chính sách lấy mẫu toàn bộ lân cận Full Neighborhood và lấy mẫu theo độ mới Recency Sampling tại Chương 3, nhằm kiểm tra thực nghiệm liệu chính sách sampling có gây mất mát các bằng chứng APT dài hạn hay không."
new_topk = "chuyên đề đề xuất cơ chế ứng viên lấy mẫu lân cận có chọn lọc theo trọng số thời gian Top-k Temporal Attention Sampling, ưu tiên tổng hợp thông điệp từ các đỉnh lân cận có hoạt động gần nhất thay vì mở rộng toàn bộ cây phụ thuộc nhiều bước. Đây là thiết kế mở rộng dự kiến phục vụ đối sánh với các chính sách lấy mẫu toàn bộ lân cận (Full Neighborhood) và lấy mẫu theo độ mới (Recency Sampling) trong các nghiên cứu tương lai; thành phần này chưa được hiện thực và chưa kiểm chứng thực nghiệm trong chiến dịch Stage A2 hiện tại."
assert old_topk in p381.text
replace_in_paragraph_runs(p381, old_topk, new_topk)
print("Updated p[381] (Top-k sampling design-only)")

# 10. p[408] (InfoNCE & Barlow Twins citation mismatch)
p408 = doc.paragraphs[408]
old_infonce = "trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [38], [37] và Barlow Twins [11] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo. [41] [21] [13]"
new_infonce = "trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [41], [21] và Barlow Twins [13] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo."
assert old_infonce in p408.text
replace_in_paragraph_runs(p408, old_infonce, new_infonce)
print("Updated p[408] (InfoNCE & Barlow Twins citations)")

# 11. p[471] (Attention-MIL proposed)
p471 = doc.paragraphs[471]
old_mil1 = "Chuyên đề áp dụng cơ chế Attention-based Deep MIL của Ilse et al.  [44], nhưng thiết kế cơ chế ánh xạ Túi, Thực thể đặc thù cho bài toán an ninh mạng (Cybersecurity Bag-Instance Mapping, Đề xuất của đề tài / Ours):"
new_mil1 = "Chuyên đề đề xuất áp dụng cơ chế Attention-based Deep MIL của Ilse et al.  [44] (như một thiết kế mở rộng tùy chọn, chưa hiện thực và chưa kiểm chứng trong chiến dịch Stage A2 hiện tại), kết hợp thiết kế cơ chế ánh xạ Túi – Thực thể đặc thù cho bài toán an ninh mạng (Cybersecurity Bag-Instance Mapping, Đề xuất của đề tài / Ours):"
assert old_mil1 in p471.text
replace_in_paragraph_runs(p471, old_mil1, new_mil1)
print("Updated p[471] (Attention-MIL proposed)")

# 12. p[479] (Attention-MIL classifier boundary)
p479 = doc.paragraphs[479]
# Note: p[479] contains an oMath element! We update only the text in the first run
old_mil2 = "Cơ chế Gated Attention-MIL trang bị một đầu phân lớp túi phụ trợ "
new_mil2 = "Cơ chế Gated Attention-MIL dự kiến trang bị một đầu phân lớp túi phụ trợ "
assert old_mil2 in p479.runs[0].text
p479.runs[0].text = p479.runs[0].text.replace(old_mil2, new_mil2)
print("Updated p[479] (Attention-MIL classifier boundary while preserving OMML)")

# 13. p[515] (SHA-256 digital signature claim)
p515 = doc.paragraphs[515]
old_sha = "Mã băm SHA-256 thu được cung cấp chữ ký toàn vẹn không thể bác bỏ, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường."
new_sha = "Mã băm SHA-256 thu được cung cấp dấu vân tay nội dung dùng để kiểm tra tính toàn vẹn của tệp khi đối chiếu với giá trị tham chiếu tin cậy, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường."
assert old_sha in p515.text
replace_in_paragraph_runs(p515, old_sha, new_sha)
print("Updated p[515] (SHA-256 content fingerprint)")

# 14. p[517] (HDFS 44.7 GB)
p517 = doc.paragraphs[517]
old_hdfs = "Tệp dữ liệu gốc HDFS_1.tar.gz, dung lượng 44.7 GB chưa nén, chứa tổng cộng 11,175,629 sự kiện log hệ thống được phân nhóm thành 575,061 phiên khối Block Session ID, có mã băm toàn vẹn SHA-256: 6ca6c5bc​2671c66a​fecee936​9a2fdac6​06bf3399​7a2494ac​66aa411f​e3e95169."
new_hdfs = "Tệp lưu trữ HDFS_1.tar.gz có kích thước 161,886,385 byte (mã băm SHA-256: 6ca6c5bc​2671c66a​fecee936​9a2fdac6​06bf3399​7a2494ac​66aa411f​e3e95169); sau khi xử lý, tập dữ liệu chứa 11,175,629 bản ghi log được ánh xạ tới 575,061 block session."
assert old_hdfs in p517.text
replace_in_paragraph_runs(p517, old_hdfs, new_hdfs)
print("Updated p[517] (HDFS archive size from manifest)")

# 15. p[518] (Arp et al. [10] & Datasets [14], [16], [17], [9] & Manifest hash)
p518 = doc.paragraphs[518]
old_split = "tuân thủ khuyến nghị tránh rò rỉ thời gian (temporal snooping) của Arp et al. [8]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [12], LANL [13], HDFS [18], BGL [42]); trong đó, tập dữ liệu HDFS đóng vai trò là môi trường thực thi chính thức cho chiến dịch tiền huấn luyện Stage A2 hiện hành, còn các tập dữ liệu quy mô lớn còn lại định vị bối cảnh mở rộng cho các giai đoạn tiếp theo. Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và xác thực bằng chữ ký mật mã: [10]"
new_split = "tuân thủ khuyến nghị tránh rò rỉ thời gian (temporal snooping) của Arp et al. [10]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [14], LANL [16], HDFS [17], [9], BGL [9]); trong đó, tập dữ liệu HDFS đóng vai trò là môi trường thực thi chính thức cho chiến dịch tiền huấn luyện Stage A2 hiện hành, còn các tập dữ liệu quy mô lớn còn lại định vị bối cảnh mở rộng cho các giai đoạn tiếp theo. Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và kiểm soát tính toàn vẹn bằng mã băm mật mã SHA-256 trong tệp manifest."
assert old_split in p518.text
replace_in_paragraph_runs(p518, old_split, new_split)
print("Updated p[518] (Arp [10], Datasets [14],[16],[17],[9], Manifest hash)")

# 16. p[530] (Frozen probe fairness overclaim)
p530 = doc.paragraphs[530]
old_fairness = "bảo đảm tính công bằng tuyệt đối khi đo lường khả năng tách biệt thông tin an ninh của biểu diễn tự giám sát."
new_fairness = "giúp quá trình xáo trộn có tính xác định và nhất quán giữa các lần đánh giá khi đo lường khả năng tách biệt thông tin an ninh của biểu diễn tự giám sát."
assert old_fairness in p530.text
replace_in_paragraph_runs(p530, old_fairness, new_fairness)
print("Updated p[530] (Frozen probe determinism)")

# 17. p[532] (AP/ROC ties overclaim)
p532 = doc.paragraphs[532]
old_ties = "loại bỏ hoàn toàn các sai số do tính toán thứ hạng thô và thiết lập tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc."
new_ties = "tránh sai lệch do triển khai thủ công không nhất quán trong xử lý thứ hạng/ties và thiết lập tiêu chuẩn đối chuẩn khách quan giữa các kiến trúc."
assert old_ties in p532.text
replace_in_paragraph_runs(p532, old_ties, new_ties)
print("Updated p[532] (AP/ROC ties handling)")

# 18. p[565] (Heading 3.2.4)
p565 = doc.paragraphs[565]
assert "Kiểm chứng tái lập độc lập trên máy trạm" in p565.text
replace_in_paragraph_runs(p565, "Kiểm chứng tái lập độc lập trên máy trạm", "Kiểm chứng tái lập thủ công trên máy trạm")
print("Updated p[565] (Heading 3.2.4)")

# 19. p[566] (AI self-referential wording)
p566 = doc.paragraphs[566]
old_ai1 = "Nhằm xác thực tính độc lập, khách quan và năng lực tái lập thực tế của hệ thống mã nguồn mà không phụ thuộc vào giao diện tương tác hay luồng tự động hóa của trợ lý AI, sinh viên đã trực tiếp thực thi kịch bản kiểm chứng manual_reproduction/run_manual_sequence42.ps1 ngoài môi trường PowerShell độc lập (với cờ lệnh -ExecutionPolicy Bypass)."
new_ai1 = "Nhằm xác thực tính độc lập, khách quan và năng lực tái lập thực tế của hệ thống mã nguồn mà không phụ thuộc vào phiên tương tác hay phần mềm điều phối bên ngoài, sinh viên đã trực tiếp thực thi kịch bản kiểm chứng manual_reproduction/run_manual_sequence42.ps1 trong môi trường PowerShell độc lập (với cờ lệnh -ExecutionPolicy Bypass)."
assert old_ai1 in p566.text
replace_in_paragraph_runs(p566, old_ai1, new_ai1)
print("Updated p[566] (Removed AI self-referential wording)")

# 20. p[567] (VRAM overclaim & manual run)
p567 = doc.paragraphs[567]
old_vram = "khẳng định khả năng vận hành hoàn toàn nằm trong giới hạn tài nguyên khả thi của máy trạm cá nhân."
new_vram = "cho thấy cấu hình thực nghiệm này có thể vận hành trong giới hạn tài nguyên của máy trạm được sử dụng."
assert old_vram in p567.text
replace_in_paragraph_runs(p567, old_vram, new_vram)
replace_in_paragraph_runs(p567, "Đợt chạy thực nghiệm độc lập (với định danh Run ID CONF_SEQUENCE_ONLY_seed42_1789724929", "Đợt chạy thực nghiệm tái lập thủ công (với định danh Run ID CONF_SEQUENCE_ONLY_seed42_1789724929")
print("Updated p[567] (VRAM and manual reproduction)")

# 21. p[568] (Manual reproduction)
p568 = doc.paragraphs[568]
old_rep = "Đợt chạy tái lập độc lập này đã tái hiện chính xác quỹ đạo hội tụ, cơ chế dừng sớm và các chỉ số kiểm toán của đợt chạy xác nhận Seed 42, khẳng định tính xác định và độ tin cậy thực nghiệm của pipeline nghiên cứu."
new_rep = "Đợt chạy tái lập thủ công này đã tái hiện chính xác quỹ đạo hội tụ, cơ chế dừng sớm và các chỉ số kiểm toán của đợt chạy xác nhận Seed 42, cho thấy tính xác định và độ tin cậy thực nghiệm của pipeline nghiên cứu."
assert old_rep in p568.text
replace_in_paragraph_runs(p568, old_rep, new_rep)
print("Updated p[568] (Manual reproduction wording)")

# 22. p[572] (AI self-referential in Figure 3.1)
p572 = doc.paragraphs[572]
old_ai2 = "trên máy trạm ngoài môi trường trợ lý AI."
new_ai2 = "trên máy trạm trong cửa sổ dòng lệnh PowerShell độc lập."
assert old_ai2 in p572.text
replace_in_paragraph_runs(p572, old_ai2, new_ai2)
print("Updated p[572] (Removed AI wording in Figure 3.1 description)")

# Save modified document
doc.save(str(docx_path))
print(f"Successfully saved modified DOCX to {docx_path}")

# Verify OMML count after modification
doc_after = docx.Document(str(docx_path))
after_omml = len(doc_after._element.xpath('.//m:oMath'))
print(f"Final OMML count: {after_omml}")
assert after_omml == 606, f"OMML count mismatch! Expected 606, got {after_omml}"

# Export PDF via Word COM
print("Exporting PDF via Word COM...")
pythoncom.CoInitialize()
try:
    word = win32.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    wdoc = word.Documents.Open(str(docx_path.resolve()))
    # 17 = wdExportFormatPDF
    wdoc.ExportAsFixedFormat(
        OutputFileName=str(pdf_path.resolve()),
        ExportFormat=17,
        OpenAfterExport=False,
        OptimizeFor=0, # wdExportOptimizeForPrint
        CreateBookmarks=1, # wdExportCreateHeadingBookmarks
        DocStructureTags=True
    )
    wdoc.Close(False)
    word.Quit()
    print(f"Successfully exported PDF to {pdf_path}")
except Exception as e:
    print(f"Word COM PDF export error: {e}")
    raise
finally:
    pythoncom.CoUninitialize()
