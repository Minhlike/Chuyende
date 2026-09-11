# Báo cáo Kiểm toán Văn phong Khoa học & Chống AI-Slop (ATTT Scientific Prose Auditor v2.2)

- **Cơ sở phương pháp luận**: Bài báo *"AI slop hay rác AI: Từ hiện tượng ngôn ngữ đến rủi ro an ninh mạng"* (Khúc Hữu Hùng, *Tạp chí An toàn thông tin*, 19/08/2026).
- **Văn bản thẩm định**: `Chuyên đề chuyên sâu.docx` (97 trang A4 Portrait, 555 đoạn văn, 14 bảng biểu).
- **Thời điểm kiểm toán (UTC)**: `2026-09-11T11:49:05.797698+00:00`
- **Trạng thái tổng thể**: `AUDIT_COMPLETE_PATCH_PREPARED`

---

## 1. Tóm tắt Điều hành & Kết quả Cổng Kiểm soát (Hard Gates)

Theo định nghĩa của *Tạp chí An toàn thông tin*, AI-slop trong nghiên cứu khoa học không đồng nghĩa với văn bản do AI sinh ra, mà là **nội dung trôi chảy nhưng rỗng, lặp khuôn, vắng chủ thể chịu trách nhiệm và chuyển gánh nặng kiểm chứng sang người đọc**.

| Mã Cổng | Tên Cổng Kiểm soát | Kết quả Thẩm định | Đánh giá Pháp chứng |
|---|---|---|---|
| **GATE-1** | `REFERENCE_INTEGRITY` | **PASS** | 43/43 tài liệu tham khảo được xác minh từ nguồn xuất bản chính thống (IEEE, ACM, USENIX, NDSS, NIST, LANL). 0 nguồn giả mạo. |
| **GATE-2** | `HYPOTHESIS_ID_CONSISTENCY` | **REQUIRES_ACTION** | Phát hiện sự lệch pha ngữ nghĩa giữa định nghĩa H1–H5 ở Chương 2 và diễn giải tại Mục 3.3.2. Cần điều chỉnh câu chữ diễn giải thực nghiệm theo Phương án A. |
| **GATE-3** | `CLAIM_EVIDENCE_PROPORTIONALITY` | **PASS** | Kết luận tương xứng với dữ liệu thực nghiệm; câu caveat bảo vệ ranh giới tại P533 (VRAM < 550 MB chỉ gợi ý tiềm năng bộ nhớ, chưa đủ kết luận triển khai SOC) và P534 (Seed 42 dừng sớm) được bảo toàn nguyên vẹn. |
| **GATE-4** | `EPISTEMIC_ACCOUNTABILITY` | **PASS** | 100% mệnh đề khoa học quan trọng đều có chủ thể tri thức xác định (`CITED_LITERATURE`, `AUTHOR_PROPOSAL`, `OBSERVED_RESULT`). 2 vị trí chứa mệnh đề vô chủ nhẹ (P194, P374) được rà soát. |
| **GATE-5** | `SPECIFICITY` | **PASS** | Dữ liệu định lượng rõ ràng: seed, epochs (12), loss values (0.550259), GPU hardware UUID, không dùng văn phong rỗng để che giấu thiếu sót. |
| **GATE-6** | `NO_NEW_CLAIMS` | **PASS** | Không phát sinh dữ kiện mới trong quá trình kiểm toán. |
| **GATE-7** | `CITATION_PRESERVATION` | **PASS** | Toàn bộ 67 citation-bearing claims giữ nguyên liên kết trích dẫn [1]–[43]. |
| **GATE-8** | `OMML_INTEGRITY` | **PASS** | **202 công thức toán học OMML** được nhận diện và khóa bảo vệ 100%. |

---

## 2. Kiểm toán Chi tiết Lớp Rhetorical Auditor (Chống AI-Slop Bề mặt)

### 2.1. Phân bố Từ mở đầu & Phát hiện Cụm Dập khuôn (Template Clustering)
- **Tổng số đoạn văn mở đầu bằng stock opener**: 26 / 555 đoạn văn.
  - `Để`: 12 đoạn
  - `Về mặt`: 6 đoạn
  - `Nhằm`: 6 đoạn
  - `Cần nhấn mạnh rằng`: 1 đoạn
  - `Đồng thời`: 1 đoạn
- **Phát hiện Cụm Dập khuôn (Template Cluster)**:  
  Khảo sát cho thấy toàn bộ thân bài không bị nợ mẫu toàn cục. **Duy nhất một cụm vi phạm nghiêm trọng nằm tại Phần Kết luận (P547–P549)**:
  - `P547`: *1. Về mặt khảo sát và xác lập bài toán (Chương 1)...*
  - `P548`: *2. Về mặt phương pháp luận và thiết kế kiến trúc (Chương 2)...*
  - `P549`: *3. Về mặt thực nghiệm và kiểm toán khoa học (Chương 3)...*
  Đây chính là mẫu dập khuôn 3 ngăn kéo được *deep-research-report.md* chỉ rõ. Giải pháp: Tái cấu trúc logic toàn bộ phần Kết luận mà không đổi bất kỳ số liệu hay dữ kiện nào.

### 2.2. Kiểm toán Tính từ Kỹ thuật Khoa trương (Inflated Technical Prose)
- Các từ xuất hiện: `tuyệt đối` (18), `cốt lõi` (15), `tường minh` (12), `chặt chẽ` (11), `nghiêm ngặt` (10), `toàn diện` (7), `vững chắc` (4), `then chốt` (3).
- **Phân loại**:
  - *Nhóm thuật ngữ kỹ thuật hợp lệ (BẢO LƯU)*: "độc lập tuyệt đối", "không cập nhật ngược lại", "phân rã tường minh", "phân vùng thời gian nghiêm ngặt", "tuân thủ nghiêm ngặt ranh giới Extractor-Detector".
  - *Nhóm tính từ đệm sáo rỗng (CẦN TINH GỌN)*:
    - `P200`: "Để thiết lập nền tảng lý thuyết vững chắc và giải quyết căn bản các khoảng trống phương pháp luận..." -> Sửa thành phát biểu kỹ thuật trực tiếp.
    - `P426`: "Nhằm bảo đảm tính chặt chẽ phương pháp luận và kiểm toán hoàn toàn các tham số có gradient..." -> Tinh gọn thành mệnh đề mô tả mục tiêu kiểm toán tham số.

### 2.3. Mệnh đề Vô chủ (Ownerless Claims)
- Xuất hiện 2 vị trí chứa cụm từ "được xem là":
  - `P194`: "việc lưu giữ khả năng liên kết này... được xem là..." -> Cần làm rõ ranh giới phân tích nguy cơ rò rỉ thông tin định danh.
  - `P374`: "Một cặp biểu diễn đa góc nhìn được xem là một cặp tương ứng hợp lệ..." -> Định nghĩa điều kiện toán học, hợp lệ theo ngữ cảnh định nghĩa khái niệm.

---

## 3. Kiểm toán Lớp Khoa học: Vấn đề Hypothesis Drift (H1–H5)

### 3.1. Hiện trạng Đối chiếu
| ID | Định nghĩa Ban đầu (Chương 2, P208–P220) | Diễn giải Đánh giá Thực nghiệm (Mục 3.3.2, P530–P534) | Trạng thái Ngữ nghĩa |
|---|---|---|---|
| **H1** | **Parameter Semantic Fidelity**: Bảo tồn thông tin tương hỗ ngữ nghĩa an ninh tiềm ẩn \(I(z; Y_{\text{sec}}) > I(z_{\text{template}}; Y_{\text{sec}})\). | Năng lực Biểu diễn Quan hệ Cấu trúc: Giảm mất mát cạnh quan hệ \(L_{\text{rel}}\) từ 4.0927 xuống 0.5052–0.5367. | **Lệch nghĩa**: Đánh giá \(L_{\text{rel}}\) của đồ thị thay vì bảo tồn tham số động. |
| **H2** | **Multi-View Alignment & Negative Transfer Prevention**: Gióng hàng có kiểm soát chuỗi và đồ thị nguồn gốc. | Độ nhạy Thời gian Liên tục: Mất mát hồi quy thời gian \(L_{\text{time}}\) giảm về 0.0857–0.0887. | **Lệch nghĩa**: Đánh giá \(L_{\text{time}}\) thay vì gióng hàng đa góc nhìn. |
| **H3** | **Anti-Drift & Shortcut Invariance Robustness**: Ổn định trước shortcut và phân phối biến động. | Gióng hàng Đa góc nhìn: Thừa nhận chưa kiểm chứng ở Stage A2, định vị cho tương lai. | **Đảo vị trí**: Chuyển nội dung H2 ban đầu sang H3; bỏ qua Anti-Drift. |
| **H4** | **Bounded Operational Budget Feasibility**: Ràng buộc độ trễ và ngân sách bộ nhớ. | Hiệu năng Tính toán Luồng: VRAM < 550 MB dưới kích thước lô 1,024 sự kiện. | **Tương thích một phần**: Khớp về dung lượng bộ nhớ GPU, giữ đúng caveat về độ trễ streaming. |
| **H5** | **Controlled Linkability & Utility–Privacy Frontier**: Cân bằng Pareto giữa an ninh và quyền riêng tư vi sai. | Độ bất định Khởi tạo Trọng số: Phân kỳ quỹ đạo huấn luyện giữa Seed 42 và các seed khác. | **Lệch nghĩa**: Đánh giá tính nhạy cảm khởi tạo ngẫu nhiên thay vì bài toán quyền riêng tư. |

### 3.2. Phương án Khuyến nghị (Phương án A)
Giữ nguyên định nghĩa H1–H5 khoa học chuẩn ở Chương 2. Tại Mục 3.3.2 (P530–P534), điều chỉnh lời dẫn để làm rõ:
- Stage A2 là pha tiền huấn luyện tự giám sát trên nhánh đồ thị thời gian độc lập; do đó các kết quả đo đạc (\(L_{\text{rel}}\), \(L_{\text{time}}\), VRAM < 550 MB, độ phân kỳ Seed 42) cung cấp **bằng chứng thực nghiệm bước đầu cho các tiền đề kỹ thuật thành phần** (năng lực biểu diễn quan hệ và thời gian), trong khi việc kiểm chứng đầy đủ H1, H2, H3, H5 toàn phần được bảo lưu minh bạch cho các giai đoạn thực nghiệm hạ nguồn (Downstream & Multi-View Stages).

---

## 4. Kiểm toán Lớp DOCX/OMML Safety (Bảo tồn Cấu trúc)

- **Tổng số đoạn văn**: 555
- **Đoạn văn PLAIN_TEXT thuần túy**: 206
- **Đoạn văn MIXED_PROTECTED (chứa OMML text)**: 137
- **Đoạn văn PROTECTED_ONLY (chỉ có OMML)**: 65
- **Đoạn văn FIELD_OR_DRAWING (chứa bảng mục lục, field, hình vẽ)**: 147
- **Đoạn văn HEADING**: 85
- **Bảng biểu**: 14
- **Cơ chế can thiệp**: Mọi bản vá văn phong chỉ tác động vào các đoạn `PLAIN_TEXT` hoặc run-level text an toàn, bảo đảm **202 công thức toán OMML không bị chạm vào**.