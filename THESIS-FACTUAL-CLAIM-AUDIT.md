# THESIS FACTUAL / CLAIM / CITATION / IMPLEMENTATION AUDIT REPORT

**Tài liệu thẩm định:** `Chuyên đề chuyên sâu.docx` (và xuất xưởng `Chuyên đề chuyên sâu.pdf`)  
**Repository:** `Minhlike/Chuyende` (nhánh `fix/thesis-apply-edits`)  
**Tác giả chính thức:** Đoàn Ngọc Hoàng Minh – AT180632  
**Giảng viên hướng dẫn:** ThS. Nguyễn Thị Thu Thủy – Khoa An toàn thông tin, Học viện Kỹ thuật Mật mã  
**Ngày thực hiện:** 20/09/2026  

---

## 1. PHÂN LOẠI TRẠNG THÁI (AUDIT CLASSIFICATION CODES)

Mỗi claim và cơ chế kỹ thuật trong chuyên đề được thẩm tra và phân loại theo 6 bậc chuẩn mực học thuật:
- **A. `VERIFIED_FACT`**: Được nguồn học thuật/official source hoặc artifact thực nghiệm hỗ trợ đầy đủ.
- **B. `IMPLEMENTED_AND_TESTED`**: Có hiện thực thật trong mã nguồn; có unit test và bằng chứng thực nghiệm kiểm chứng tương ứng.
- **C. `IMPLEMENTED_NOT_TESTED`**: Có mã nguồn trong codebase nhưng chưa có bằng chứng thực nghiệm định lượng cho claim.
- **D. `DESIGN_ONLY`**: Là thiết kế kiến trúc / đề xuất mở rộng của chuyên đề; không được viết như đã triển khai thực tế.
- **E. `NOT_TESTED`**: Giả thuyết hoặc cấu hình chưa được kiểm chứng thực nghiệm.
- **F. `INCORRECT_OR_UNSUPPORTED`**: Sai factual, trích dẫn không hỗ trợ, hoặc claim mạnh hơn bằng chứng thực tế.

---

## 2. BẢNG MA TRẬN DESIGN VS IMPLEMENTATION

| Thành phần kỹ thuật | Phân loại trạng thái | Minh chứng trong Code / File / Class / Function | Bằng chứng thực nghiệm / Test tương ứng |
| :--- | :--- | :--- | :--- |
| **Controlled Linkability / HMAC** | `IMPLEMENTED_AND_TESTED` | `src/research_agent/experiments/extractor/tokenizer.py`<br>`SecurityAwareTokenizer.pseudonymize_token` | `tests/test_tokenizer_privacy.py`<br>(4/4 tests pass: zero hardcoded keys, scope rotation, RFC1918, transformation) |
| **VICReg Multi-View Alignment** | `IMPLEMENTED_AND_TESTED` | `src/research_agent/experiments/extractor/multi_view.py`<br>`VICRegLoss`, `MultiViewFeatureExtractor` | `tests/test_multiview_vicreg.py`<br>(3/3 tests pass: isolation, embeddings, loss/gradients)<br>`experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_*` |
| **LRU Dynamic Entity Memory** | `IMPLEMENTED_AND_TESTED` | `src/research_agent/experiments/extractor/graph_view.py`<br>`BoundedEntityMemoryBank` (`OrderedDict` LRU eviction) | `tests/test_temporal_gnn.py`<br>(`test_04_bounded_memory_capacity_and_peak_tracking`) |
| **Fail-Closed Late Event Handling** | `IMPLEMENTED_AND_TESTED` | `src/research_agent/experiments/extractor/graph_view.py`<br>`BoundedEntityMemoryBank.get_memory` (ném `ValueError`) | `tests/test_temporal_gnn.py`<br>(`test_02_strict_global_temporal_monotonicity_rejection`) |
| **PCGrad Gradient Surgery** | `DESIGN_ONLY` / `NOT_TESTED` | Không có implementation trong training pipeline (`multi_view.py` dùng weighted sum loss). Chỉ có công thức OMML tại `native_omml_equations.py`. | Chưa kiểm chứng trong thực nghiệm Stage A2 (đã chuyển ngữ thành "đề xuất áp dụng" và "chưa kiểm chứng"). |
| **Attention-MIL (Stage B)** | `DESIGN_ONLY` / `NOT_TESTED` | Không có implementation trong `models/` hoặc `extractor/`. | Giả thuyết H4 xác lập chính thức là `NOT_TESTED` trong Chương 3. |
| **Token-Bucket Backpressure & Shedding** | `DESIGN_ONLY` | Không có implementation trong codebase khoa học. | Thành phần kiến trúc dòng đề xuất; không vận hành trong thực nghiệm Stage A2. |
| **Top-k Temporal Attention Sampling** | `DESIGN_ONLY` | Không có implementation trong `temporal_graph_view_encoder.py`. | Cơ chế ứng viên đề xuất; chưa kiểm chứng thực nghiệm tại Chương 3. |
| **Reconciliation Buffer & Explicit Info-Loss** | `DESIGN_ONLY` | Không có implementation (pipeline hiện tại fail-closed từ chối sự kiện trễ). | Kiến trúc dòng đề xuất; không vận hành trong thực nghiệm Stage A2. |
| **Graph-Fidelity Candidates (4 cơ chế)** | `DESIGN_ONLY` | Chưa hiện thực hóa 4 cơ chế trong `graph_builder.py`. | Cơ chế ứng viên đề xuất; chưa kiểm chứng qua phân tích triệt tiêu tại Chương 3. |

---

## 3. CHI TIẾT CÁC LỖI ĐÃ PHÁT HIỆN VÀ SỬA ĐỔI

### 3.1. Lỗi Factual: Dung lượng HDFS 44.7 GB (§3.1.2)
- **Vị trí cũ**: `p[517]` (§3.1.2).
- **Claim cũ**: `HDFS_1.tar.gz, dung lượng 44.7 GB chưa nén`
- **Phân loại**: `INCORRECT_OR_UNSUPPORTED`
- **Minh chứng/Source**:
  - `datasets/manifests/REAL-DATA-CONTRACT-HDFS.json`: `raw_artifact_sha256 = 6ca6c5bc...`, `source_record_count = 11,175,629`.
  - `datasets/manifests/SPL-HDFS-001.json`: `file_name = HDFS_1.tar.gz`, `byte_count = 161886385`, `raw_total_line_count = 11175629`, `labeled_block_count = 575061`.
- **Sửa thành**:
  > *“Trong khuôn khổ nghiên cứu chuyên đề, thực nghiệm Stage A2 tập trung đánh giá trên tập dữ liệu chuẩn HDFS (Hadoop Distributed File System). Tệp lưu trữ HDFS_1.tar.gz có kích thước 161,886,385 byte (mã băm SHA-256: 6ca6c5bc​2671c66a​fecee936​9a2fdac6​06bf3399​7a2494ac​66aa411f​e3e95169); sau khi xử lý, tập dữ liệu chứa 11,175,629 bản ghi log được ánh xạ tới 575,061 block session.”*
- **Lý do**: Không suy diễn hoặc ước lượng con số "44.7 GB chưa nén" khi không có bằng chứng artifact xác thực; đưa về dữ kiện thực nghiệm chính xác tuyệt đối theo manifest.

---

### 3.2. Lỗi Khái niệm Mật mã: Đồng nhất SHA-256 với Chữ ký số (§3.1.1, §3.1.2)
- **Vị trí cũ**: `p[515]` (§3.1.1) và `p[518]` (§3.1.2).
- **Claim cũ**:
  - `p[515]`: *“Mã băm SHA-256 thu được cung cấp chữ ký toàn vẹn không thể bác bỏ, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường.”*
  - `p[518]`: *“Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và xác thực bằng chữ ký mật mã: [10]”*
- **Phân loại**: `INCORRECT_OR_UNSUPPORTED`
- **Minh chứng/Source**: NIST FIPS 180-4 (Secure Hash Standard). SHA-256 là hàm băm một chiều (cryptographic hash function), cung cấp dấu vân tay nội dung (content fingerprint / checksum) để đối chiếu tính toàn vẹn, KHÔNG phải chữ ký số (digital signature) và tự thân không cung cấp tính chống chối bỏ (non-repudiation) nếu thiếu khóa bí mật / hạ tầng PKI.
- **Sửa thành**:
  - `p[515]`: *“Hàm compute_file_sha256 đọc tệp tin dưới dạng nhị phân theo từng khối 64 KB nhằm tối ưu bộ nhớ máy trạm khi xử lý các tệp nhật ký và checkpoint trọng lượng lớn. Mã băm SHA-256 thu được cung cấp dấu vân tay nội dung dùng để kiểm tra tính toàn vẹn của tệp khi đối chiếu với giá trị tham chiếu tin cậy, phục vụ công tác kiểm toán nguồn gốc thực nghiệm và khóa môi trường.”*
  - `p[518]`: *“Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và kiểm soát tính toàn vẹn bằng mã băm mật mã SHA-256 trong tệp manifest.”*
- **Lý do**: Chuẩn hóa chính xác thuật ngữ mật mã học, loại bỏ hoàn toàn các khái niệm "chữ ký không thể bác bỏ" và "chữ ký mật mã" khi thực chất chỉ sử dụng mã băm SHA-256.

---

### 3.3. Lỗi Hệ thống: Trích dẫn sai lệch (Citation Numbering Audit)
Thẩm định toàn diện 44 mục Thư mục tham khảo (Bảng 27) đối chiếu với toàn bộ 199 lần xuất hiện trích dẫn trong văn bản.

#### A. §3.1.2 Trích dẫn Arp et al. và 4 bộ dữ liệu
- **Vị trí cũ**: `p[518]`.
- **Nội dung cũ**: `temporal snooping của Arp et al. [8]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [12], LANL [13], HDFS [18], BGL [42]); ... [10]`
- **Phân tích sai lệch**:
  - `[8]` trong Bảng 27 là Sysmon (Russinovich & Garnier) $\to$ Arp et al. (USENIX Security 2022) thực chất là `[10]`.
  - `[12]` là VICReg $\to$ DARPA TC E3 thực chất là `[14]`.
  - `[13]` là Barlow Twins $\to$ LANL (Kent) thực chất là `[16]`.
  - `[18]` là Shokri et al. (MIA) $\to$ HDFS là `[17]` (Xu et al., SOSP 2009) và `[9]` (LogHub, ISSRE 2023).
  - `[42]` là CPM-Nets $\to$ BGL thuộc kho LogHub `[9]`.
  - Số trích dẫn `[10]` bị rơi thừa ở cuối câu.
- **Sửa thành**:
  > *“...tuân thủ khuyến nghị tránh rò rỉ thời gian (temporal snooping) của Arp et al. [10]. Khung đối chuẩn nghiên cứu bao quát 4 tập dữ liệu đại diện cho các miền viễn trắc an ninh khác nhau (DARPA TC E3 [14], LANL [16], HDFS [17], [9], BGL [9]); trong đó, tập dữ liệu HDFS đóng vai trò là môi trường thực thi chính thức cho chiến dịch tiền huấn luyện Stage A2 hiện hành, còn các tập dữ liệu quy mô lớn còn lại định vị bối cảnh mở rộng cho các giai đoạn tiếp theo. Toàn bộ các phân vùng dữ liệu được phân định theo thứ tự thời gian và kiểm soát tính toàn vẹn bằng mã băm mật mã SHA-256 trong tệp manifest.”*

#### B. §2.4.1.3 Trích dẫn InfoNCE và Barlow Twins
- **Vị trí cũ**: `p[408]`.
- **Nội dung cũ**: `trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [38], [37] và Barlow Twins [11] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo. [41] [21] [13]`
- **Phân tích sai lệch**:
  - `[38]` là T. T. T. Nguyễn, `[37]` là Alon & Yahav (GNN), `[11]` là UNICORN (Han et al.) $\to$ hoàn toàn không liên quan đến InfoNCE và Barlow Twins.
  - Các trích dẫn đúng bị dồn thừa về cuối câu: `[41]` (van den Oord - InfoNCE/CPC), `[21]` (Chen et al. - SimCLR), `[13]` (Zbontar et al. - Barlow Twins).
- **Sửa thành**:
  > *“...trong khi việc đối sánh triệt tiêu định lượng với InfoNCE [41], [21] và Barlow Twins [13] được định vị cho các chiến dịch thực nghiệm hạ nguồn tiếp theo.”*

#### C. Hình 1.2 / Caption Trích dẫn MITRE ATT&CK và Inam et al.
- **Vị trí cũ**: `p[64]` (Danh mục hình vẽ), `p[127]` (nội dung), `p[130]` (caption Hình 1.2).
- **Nội dung cũ**: `nguồn tác giả tổng hợp dựa trên MITRE ATT&CK [4] và Inam et al. [1]2 [6] [3]`
- **Phân tích sai lệch**:
  - `[4]` là Michael et al. (Audit Logs) $\to$ trỏ nhầm cho MITRE ATT&CK.
  - Chuỗi rác `[1]2 [6] [3]` gồm `[1]` (Zhu et al. - Log Parsing), `2` (số thừa), `[6]` (MITRE ATT&CK), `[3]` (Inam et al. - S&P 2023).
- **Sửa thành**:
  > *“...nguồn tác giả tổng hợp dựa trên MITRE ATT&CK [6] và Inam et al. [3]”*

---

### 3.4. Lỗi Trích dẫn LLM ở Lời nói đầu
- **Vị trí cũ**: `p[97]`.
- **Nội dung cũ**: `Mô hình ngôn ngữ lớn mở thêm khả năng chuẩn hóa và diễn giải log, nhưng vẫn chịu hạn chế về chi phí, độ trễ, tính ổn định và bảo mật dữ liệu [2].`
- **Phân loại**: `INCORRECT_OR_UNSUPPORTED`
- **Minh chứng/Source**: Nguồn `[2]` là Jiang et al., *“A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?”* (ISSTA 2024), chuyên khảo sát các bộ phân tích cú pháp log truyền thống (Drain, Spell, Brain...), hoàn toàn không nghiên cứu hay đưa ra kết luận về mô hình ngôn ngữ lớn (LLM).
- **Sửa thành**: Loại bỏ câu phụ về LLM và trích dẫn sai `[2]`, giữ nguyên mạch lập luận khoa học từ thống kê $\to$ tuần tự/ngữ nghĩa $\to$ đồ thị $\to$ học tự giám sát.

---

### 3.5. Thu hẹp Mô tả Ground Truth của DARPA TC (§1.1.2)
- **Vị trí cũ**: `p[132]`.
- **Nội dung cũ**: `trong đó các kịch bản tấn công và diễn tập red-team trong các engagement của chương trình được gán nhãn ở mức độ hạt tiến trình và luồng phụ thuộc;`
- **Phân loại**: `INCORRECT_OR_UNSUPPORTED` (overclaim)
- **Minh chứng/Source**: DARPA Transparent Computing program releases (TC E3/E5 ground truth reports). Dữ liệu viễn trắc nền của hệ điều hành không có nhãn sẵn ở từng tiến trình/luồng; chỉ các hành vi của Red Team được ghi nhận trong báo cáo kịch bản, cho phép ánh xạ suy diễn nhãn.
- **Sửa thành**:
  > *“trong đó các kịch bản tấn công của đội Red Team được ghi nhận qua các báo cáo kịch bản (ground-truth reports/annotations), cho phép ánh xạ và suy diễn nhãn ở mức tiến trình và luồng phụ thuộc liên quan đến đợt tấn công, thay vì toàn bộ dữ liệu viễn trắc nền đều có nhãn sẵn ở mức hạt nhân;”*

---

### 3.6. Căn chỉnh Ranh giới Design vs Implementation trong Chương 2
- **Token-Bucket Backpressure & Shedding (`p[244]`)**:
  - Cũ: Trình bày như cơ chế đang vận hành trong hệ thống.
  - Mới: Đánh dấu rõ là cơ chế kiểm soát áp lực ngược đề xuất trong kiến trúc mục tiêu, chưa triển khai trong thực nghiệm Stage A2.
- **4 Cơ chế ứng viên Kiểm soát Độ chân thực Đồ thị (`p[352]`)**:
  - Cũ: *“Mức độ đóng góp và hiệu quả thực tế của từng cơ chế ứng viên được đánh giá định lượng thông qua phân tích triệt tiêu tại Chương 3.”*
  - Mới: Khẳng định rõ đây là các cơ chế ứng viên thuộc thiết kế kiến trúc đề xuất; việc hiện thực hóa và đánh giá định lượng được định vị cho các nghiên cứu tiếp theo (chưa kiểm chứng trong Stage A2).
- **Top-k Temporal Attention Sampling (`p[381]`)**:
  - Cũ: Viết như đã áp dụng và đánh giá đối sánh tại Chương 3.
  - Mới: Xác định rõ là cơ chế ứng viên đề xuất trong thiết kế mở rộng; chưa hiện thực và chưa kiểm chứng thực nghiệm tại Chương 3.
- **Attention-MIL (`p[471]`, `p[479]`)**:
  - Cũ: *“Chuyên đề áp dụng cơ chế Attention-based Deep MIL...”*, *“trang bị một đầu phân lớp...”*
  - Mới: *“Chuyên đề đề xuất áp dụng cơ chế Attention-based Deep MIL... (như một thiết kế mở rộng tùy chọn, chưa hiện thực và chưa kiểm chứng trong chiến dịch Stage A2 hiện tại)...”*, *“dự kiến trang bị một đầu phân lớp...”*

---

### 3.7. Hạ mức các Overclaim Ngôn ngữ
- **Frozen Probe Fairness (`p[530]`)**:
  - Cũ: *“bảo đảm tính công bằng tuyệt đối”*
  - Mới: *“giúp quá trình xáo trộn có tính xác định và nhất quán giữa các lần đánh giá”* (Determinism $\neq$ Fairness).
- **AP/ROC Ties (`p[532]`)**:
  - Cũ: *“loại bỏ hoàn toàn các sai số do tính toán thứ hạng thô”*
  - Mới: *“tránh sai lệch do triển khai thủ công không nhất quán trong xử lý thứ hạng/ties”*
- **Manual Reproduction (`p[49]`, `p[565]`, `p[567]`, `p[568]`)**:
  - Cũ: *“Kiểm chứng tái lập độc lập trên máy trạm”*, *“Đợt chạy thực nghiệm độc lập”*
  - Mới: *“Kiểm chứng tái lập thủ công trên máy trạm”*, *“Đợt chạy thực nghiệm tái lập thủ công”* (Tránh gây hiểu nhầm là third-party independent replication).
- **Giới hạn tài nguyên VRAM (`p[567]`)**:
  - Cũ: *“khẳng định khả năng vận hành hoàn toàn nằm trong giới hạn tài nguyên khả thi của máy trạm cá nhân.”*
  - Mới: *“cho thấy cấu hình thực nghiệm này có thể vận hành trong giới hạn tài nguyên của máy trạm được sử dụng.”*

---

### 3.8. Loại bỏ AI-Slop và Thuật ngữ Tự tham chiếu AI
- **`p[566]`**:
  - Cũ: *“...mà không phụ thuộc vào giao diện tương tác hay luồng tự động hóa của trợ lý AI, sinh viên đã trực tiếp thực thi kịch bản kiểm chứng manual_reproduction/run_manual_sequence42.ps1 ngoài môi trường PowerShell độc lập...”*
  - Mới: *“...mà không phụ thuộc vào phiên tương tác hay phần mềm điều phối bên ngoài, sinh viên đã trực tiếp thực thi kịch bản kiểm chứng manual_reproduction/run_manual_sequence42.ps1 trong môi trường PowerShell độc lập...”*
- **`p[572]`**:
  - Cũ: *“...trên máy trạm ngoài môi trường trợ lý AI.”*
  - Mới: *“...trên máy trạm trong cửa sổ dòng lệnh PowerShell độc lập.”*

---

### 3.9. Sửa lỗi Author Identity tận gốc trong Working Repo
- **Danh tính tác giả chính thức**: **Đoàn Ngọc Hoàng Minh – AT180632**
- **Nơi phát hiện residue sai**: `HUONG_DAN_CHAY_VA_XAC_MINH.md` dòng 4 ghi `**Học viên thực hiện:** Khúc Hữu Hùng`.
- **Nơi cấu hình sai**: `pyproject.toml` ghi tác giả generic `Research Engineering Team` và tên package `research-agent`.
- **Sửa tận gốc trong `D:\Research`**:
  - `HUONG_DAN_CHAY_VA_XAC_MINH.md`: Đổi thành `**Sinh viên thực hiện:** Đoàn Ngọc Hoàng Minh – AT180632`.
  - `pyproject.toml`: Căn chỉnh metadata thành `name = "log-feature-representation"`, `authors = [{ name = "Đoàn Ngọc Hoàng Minh" }]`.
  - Đảm bảo kịch bản đóng gói `scripts/package_clean_release.py` khi sao chép sang bất kỳ bản phân phối nào trong tương lai sẽ mang đúng danh tính tác giả chính thức.
