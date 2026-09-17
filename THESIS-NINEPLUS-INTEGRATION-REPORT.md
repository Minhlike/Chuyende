# BÁO CÁO TỔNG KẾT TÍCH HỢP BẰNG CHỨNG THỰC NGHIỆM NINEPLUS VÀO LUẬN VĂN THẠC SĨ
**Mã báo cáo:** THESIS-NINEPLUS-INTEGRATION-REPORT  
**Ngày hoàn thành:** 2026-09-18  
**Trạng thái nghiệm thu:** COMPLETED_WITH_ZERO_VIOLATION  

---

## 1. THÔNG TIN QUẢN TRỊ VÀ ĐỐI CHUẨN MẬT MÃ

- **Workspace:** `D:\Research`
- **Nhánh Git (Branch):** `fix/thesis-apply-edits`
- **Commit bằng chứng khởi điểm (START_EVIDENCE_COMMIT):** `878a3dbdd7d9baa5f10728250b396f3759b8f790`
- **Tài liệu nguồn chuyên sâu (Authoritative Source):** `D:\Research\deep-research-report-v4.md`
- **Báo cáo bằng chứng thực nghiệm căn cứ:** `experiments/nineplus/reports/NINEPLUS-COST-OPTIMIZED-FINAL-EVIDENCE-REPORT.md`
- **Tài liệu Master đầu ra:**
  - `D:\Research\Chuyên đề chuyên sâu.docx`
  - `D:\Research\Chuyên đề chuyên sâu.pdf`

---

## 2. KIỂM TOÁN TÍNH BẤT BIẾN (INVARIANTS AUDIT)

| Tiêu chí kiểm định | Yêu cầu chuẩn mực | Trạng thái thực tế | Kết luận |
| :--- | :--- | :--- | :--- |
| **Niêm phong tập Kiểm thử (Test split)** | `TEST_OPENED = false`, `TEST_READ_COUNT = 0` | `test_opened = false`, 0 lượt truy cập | **TUÂN THỦ TUYỆT ĐỐI** |
| **Độ nguyên vẹn mô hình nền tảng** | `NEW_BACKBONE_OPTIMIZER_STEPS = 0` | 0 bước huấn luyện backbone mới | **TUÂN THỦ TUYỆT ĐỐI** |
| **Kế toán tối ưu hóa đầu dò (Probe)** | Minh bạch chính xác số bước probe | 82.200 bước tối ưu probe độc lập | **KHỚP 100% BÁO CÁO** |
| **Quy chuẩn ký tự gạch ngang dài** | Tuyệt đối không chứa ký tự em-dash `—` | 0 ký tự `—` trên toàn văn bản | **TUÂN THỦ TUYỆT ĐỐI** |
| **Phát ngôn suy diễn thống kê** | Không tuyên bố ý nghĩa thống kê cho N=3 | Sử dụng phương sai mẫu mô tả định lượng | **TUÂN THỦ TUYỆT ĐỐI** |
| **Tuyên bố quan hệ nhân quả** | Không khẳng định nhân quả về VICReg/Fusion | Đặt dưới 3 giả thuyết cơ chế mở đường | **TUÂN THỦ TUYỆT ĐỐI** |
| **Mô hình Đơn đồ thị lịch sử** | Phải định danh đúng vai trò tham khảo | `HISTORICAL_EXPLORATORY_REFERENCE_ONLY` | **ĐỊNH DANH MINH BẠCH** |
| **Chính sách công thức toán học (OMML)** | 100% công thức dùng Office Math bản địa | **600 nút OMML** (535 đoạn, 65 bảng) | **TUÂN THỦ TUYỆT ĐỐI** |

---

## 3. CHÍNH SÁCH CÔNG THỨC TOÁN HỌC BẢN ĐỊA (MATHEMATICAL EQUATION POLICY AUDIT)

Toàn bộ các biểu thức toán học trong Master DOCX được xây dựng bằng cấu trúc **Microsoft Word Office Math (OMML)** bản địa, sử dụng bộ chuyển đổi chính thức của Microsoft Office (`MML2OMML.XSL`) kết hợp các cây phần tử XML chuẩn:

1. **Công thức chỉ số dưới / chỉ số trên thực sự:**
   - Các hàm mất mát đồ thị Stage A2: L_{graph}, L_{rel}, L_{node}, L_{time} được bảo toàn 100% nguyên vẹn dưới dạng `<m:sSub>`, không bị làm phẳng thành văn bản thô.
   - Vector tần suất, không gian bằng chứng và chỉ số kích thước: d_{mem} = 128, lr = 5 × 10^{-4}, ε = 10^{-8}, min_lr = 10^{-5}, 10^{-2}, 10^{-4}.
2. **Không gian biểu diễn và ma trận:**
   - Vector phiên: z_{session} ∈ ℝ^{128} và z ∈ ℝ^{128} với ký tự tập số thực hai nét (`<m:scr m:val="double-struck"/>`).
   - Ma trận phân loại tuyến tính probe: W ∈ ℝ^{128 × 1}.
   - Ký hiệu khe tham số đầu vào: [L_i, 4].
3. **Thước đo thống kê và kiểm định biên:**
   - Phương sai biểu diễn: Var(z) với dấu ngoặc co giãn tự động `<m:grow/>`.
   - Độ lệch hiệu năng cặp đôi: ΔAP, ΔROC-AUC, và Δ = Multi-View - Sequence.
   - Biên không thua kém tiền đăng ký: δ ≥ -0.02.
   - Giá trị trung bình kèm phương sai: ΔAP = -0.3392 ± 0.0885, 0.6694 ± 0.0468, 0.8142 ± 0.0675.
   - Cỡ mẫu thực nghiệm: N = 3.
   - Hàm nhúng thời gian liên tục điều hòa: φ(Δt) (được chuẩn hóa thay thế toàn bộ văn bản thô `phi(Delta t)` trong Mục 3.1.3 và Bảng 3.5).
4. **Tuyệt đối không sử dụng:**
   - Không chứa mã nguồn LaTeX thô như `\frac`, `\Delta`, `\in`, `\mathbb`, `\text{` trong văn bản chạy.
   - Không dùng công thức giả bằng văn bản thô (pseudo-equations).
   - Không dùng ảnh chụp công thức.
   - Không làm phẳng (flatten) các nút OMML hiện hữu khi chỉnh sửa đoạn văn.

---

## 4. CẤU TRÚC VĂN BẢN VÀ CÁC NỘI DUNG TÍCH HỢP

Công trình giữ nguyên kiến trúc **3 Chương chuẩn** của chuyên đề chuyên sâu theo quy định của Học viện Kỹ thuật Mật mã, không tự ý chia nhỏ thành 4 hoặc 5 chương:

### 4.1. Mục 3.1.3: Chuẩn hóa Giao thức Đầu dò Tuyến tính Đóng băng V3
- Bổ sung định nghĩa chuẩn hóa cho giao thức `TRAIN_FIT_FULL_FIXED_VALIDATION_EVALUATE`.
- Đóng băng 100% trọng số backbone đã học, huấn luyện bộ phân loại tuyến tính mỏng W ∈ ℝ^{128 × 1} trên 35.000 phiên Train (50 epochs, AdamW lr=10^{-2}, weight decay 10^{-4}, batch size 256, 6.850 bước/mô hình, seed 10007).
- Đánh giá cố định trên 100% tập Kiểm định (7.500 phiên cố định, 119.531 sự kiện), ghi nhận AP và ROC-AUC.
- Xác nhận tập Kiểm thử (Test) tiếp tục được niêm phong mật mã 100%.

### 4.2. Mục 3.2.3 (Mục mới): Đánh giá chuẩn hóa V3 hạ nguồn cho các mô hình xác nhận Sequence và Multi-View
- **Bảng 3.6:** Kết quả đánh giá hạ nguồn V3 trên 100% tập Validation cho bộ ba xác nhận triển vọng:
  - Sequence-Only (Seeds 42, 7, 999): AP = 1.0000 ± 0.0000, ROC-AUC = 1.0000 ± 0.0000, Var(z) = 0.005462 ± 0.000821.
  - Multi-View Aligned VICReg (Seeds 42, 7, 999): AP = 0.6608 ± 0.0885, ROC-AUC = 0.8573 ± 0.1204, Var(z) = 0.006069 ± 0.001734.
- **Bảng 3.7:** Đối sánh hiệu năng cặp đôi và kiểm định biên không thua kém (δ ≥ -0.02):
  - Seed 42: ΔAP = -0.2396 (vi phạm).
  - Seed 7: ΔAP = -0.3691 (vi phạm).
  - Seed 999: ΔAP = -0.4089 (vi phạm).
  - Trung bình cặp: ΔAP = -0.3392 ± 0.0885 (không thỏa mãn biên không thua kém trên 100% các cặp).
- Giải trình việc dừng đợt huấn luyện Graph-only triển vọng: Chi phí tính toán pilot đạt ~190 phút/epoch (~38 giờ GPU/chạy, tương ứng trần danh định ~114 giờ GPU cho bộ ba), do đó nhánh Graph-only lịch sử được bảo lưu đúng vị trí `HISTORICAL_EXPLORATORY_REFERENCE_ONLY`.
- Kế toán bước tối ưu hóa: 82.200 bước probe (41.100 bước V3 probe + 20.550 bước H1 masking probe + 20.550 bước H2 sensitivity probe); 0 bước tối ưu backbone.

### 4.3. Mục 3.3.2: Đối chiếu trạng thái bằng chứng đối với các giả thuyết nghiên cứu
- **Giả thuyết H1 (Parameter Semantic Fidelity):**
  - Trạng thái: `NOT_DIRECTLY_EVALUABLE_WITH_CURRENT_SESSION_REPRESENTATION`.
  - Phân tích bất tương thích độ mịn: Mục tiêu nhãn tham số ở cấp token [L_i, 4], trong khi biểu diễn trích xuất ở cấp phiên z_{session} ∈ ℝ^{128}. Phân tích nhãn ở cấp phiên bị thoái hóa nặng (2 danh mục xuất hiện ở 100% số phiên, 18/25 danh mục có 0 mẫu dương trong tập Validation).
  - **Bảng 3.8:** Kiểm thử cắt bỏ che tham số đầu vào trên Sequence-Only đóng băng (FROZEN_INPUT_MASKING_ABLATION): Cosine similarity dịch chuyển về 0.8201 - 0.9581, khoảng cách Euclid 3.27 - 6.78, AP duy trì 1.0000.
  - Phân định ranh giới suy diễn: Xác nhận tham số động có đi vào không gian biểu diễn z; tuyệt đối không tuyên bố H1 đã được xác nhận hay mô hình có hiểu biết ngữ nghĩa sâu sắc.
- **Giả thuyết H2 (Multi-View Alignment & Negative Transfer Prevention):**
  - Trạng thái: `NOT_SUPPORTED_WITHIN_SEQUENCE_COMPARATOR_SCOPE`.
  - Mô hình đơn chuỗi đạt trần phân tách (AP = 1.0000), trong khi mô hình đa góc nhìn đạt AP = 0.6608 (suy giảm trung bình -0.3392 AP).
  - **Bảng 3.9:** Kiểm tra độ nhạy bỏ tham số Sequence (`H2_SEQUENCE_NOPARAM_SENSITIVITY`): Khi che toàn bộ tham số, Sequence vẫn duy trì AP tuyệt đối 1.0000 trên cả 3 hạt giống, xác nhận kết quả âm tính là vững chắc (`H2_NEGATIVE_RESULT_ROBUST_TO_SEQUENCE_PARAMETER_INPUT_REMOVAL = true`).
  - Khẳng định cỡ mẫu N = 3 không sử dụng để đưa ra các kết luận suy diễn thống kê sai lệch.
- **Giả thuyết H3, H4, H5:** Bảo lưu trạng thái `NOT_TESTED`.
- **Yêu cầu kỹ thuật vận hành ER1:** Xác nhận trạng thái `PARTIAL_PRELIMINARY_MEMORY_EVIDENCE` (VRAM dưới 550 MB).
- **Kiểm toán thao tác hóa ngưỡng phương sai chống sụp đổ:** Xác nhận sự nhập nhằng do phương sai cũ đo lường trên biểu diễn che `<MASK>`, trong khi V3 đo lường trên biểu diễn sạch. Báo cáo minh bạch giá trị thực tế Var(z), không dùng ngưỡng 0.01000 cũ làm tiêu chí phán quyết.
- **Kiểm toán tính toàn vẹn khôi phục Seed 999:** Phân loại là `CONFIRMATORY_WITH_DOCUMENTED_PROTOCOL_DEVIATION` do nạp trọng số từng phần kết hợp tái tạo xác định trạng thái RNG.

### 4.4. Mục 3.3.3 (Mục mới): Phân tích cơ chế và các giả thuyết giải thích kết quả âm tính H2
- Đặt ra 3 giả thuyết cơ chế mở đường cho nghiên cứu tương lai:
  1. Đặc tính phân tách mạnh của chuỗi mẫu sự kiện HDFS (Sequence đạt trần AP = 1.0000).
  2. Sự đánh đổi điều hòa đa góc nhìn VICReg (nén không gian biểu diễn).
  3. Tính dị thể và giới hạn thông tin bổ sung của đồ thị HDFS.
- Khẳng định rõ đây là các giả thuyết khoa học cho các nghiên cứu tiếp theo, không phải kết luận nhân quả đã chứng minh.

### 4.5. Mục 3.4.2: Tám giới hạn thực nghiệm cốt lõi
- Cập nhật đầy đủ 8 giới hạn phương pháp luận và thực nghiệm: (1) Quy mô hạt giống xác nhận (N = 3); (2) Giới hạn nhánh đơn đồ thị; (3) Niêm phong tập Kiểm thử; (4) Bất tương thích độ mịn mục tiêu H1 ([L_i, 4] vs z ∈ ℝ^{128}); (5) Nhập nhằng thao tác hóa ngưỡng chống sụp đổ (Var(z) = 0.01000); (6) Sai lệch giao thức khôi phục Seed 999; (7) Phạm vi thực nghiệm trên tập HDFS; (8) Các cơ chế chưa kiểm chứng thực nghiệm.

### 4.6. Phần Kết luận (UH1)
- Tái cấu trúc toàn diện theo tinh thần liêm chính học thuật: phản ánh trung thực kết quả thực nghiệm đạt được, phân định rõ ràng giữa quan sát trực tiếp và suy diễn, ghi nhận đầy đủ kết quả âm tính H2 và các sai lệch thực nghiệm, nêu 3 định hướng phát triển thực tế.

---

## 5. THÔNG SỐ VẬT LÝ VÀ CHUẨN THỂ THỨC MASTER DOCX / PDF

| Thuộc tính | Tiêu chuẩn KMA quy định | Thực tế kiểm định trong DOCX/PDF | Đánh giá |
| :--- | :--- | :--- | :--- |
| **Số trang văn bản** | Khuyến nghị 80 - 120 trang | **113 trang** (Word Statistics: 113) | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Hướng trang (Orientation)** | 100% Portrait (Đứng) | **100% Portrait** (113/113 trang) | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Kích thước khổ giấy** | A4 (210 × 297 mm) | **595.3 × 841.9 pt** (A4 chuẩn xác) | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Font chữ & Cỡ chữ** | Times New Roman, 14 pt | Times New Roman, 14 pt | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Dãn dòng (Line Spacing)** | 1.5 lines | 1.5 lines (ONE_POINT_FIVE) | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Thụt lề đầu dòng** | 1.27 cm (0.5 inch) | 1.27 cm (First line indent) | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Căn lề trang (Margins)** | Trái 3cm; Trên/Dưới/Phải 2cm | Trái 3cm; Trên/Dưới/Phải 2cm | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Căn lề đoạn văn (Alignment)**| Justified (Đều hai bên) | Justified (WD_ALIGN_PARAGRAPH.JUSTIFY)| **HOÀN TOÀN ĐẠT CHUẨN** |
| **Bảng biểu Chương 3** | Đánh số thứ tự liên tục 3.1 - 3.9 | Đánh số tự động qua trường SEQ: Bảng 3.1 - 3.9 | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Mục lục & Danh mục bảng** | Đồng bộ tự động theo trường Word | Cập nhật hoàn tất qua Word COM | **HOÀN TOÀN ĐẠT CHUẨN** |
| **Dung lượng file PDF** | Định dạng vector nhúng chuẩn | **2.416.283 bytes** (~2.4 MB) | **TỐI ƯU XUẤT BẢN** |

---

## 6. DANH SÁCH BẢNG BIỂU CHƯƠNG 3 SAU KHI TÍCH HỢP

1. **Bảng 3.1:** Thông số kỹ thuật môi trường thực nghiệm và khóa xác thực mật mã
2. **Bảng 3.2:** Phân chia tập dữ liệu HDFS theo giao thức theo dòng thời gian chống rò rỉ
3. **Bảng 3.3:** Kết quả huấn luyện Stage A2 trên 5 hạt ngẫu nhiên thực nghiệm
4. **Bảng 3.4:** Trạng thái hồ sơ và điều kiện kết thúc các đợt thực nghiệm Stage A2
5. **Bảng 3.5:** Đối sánh đặc tính phương pháp luận giữa khung biểu diễn đề xuất và các phương pháp cơ sở
6. **Bảng 3.6 [MỚI]:** Kết quả đánh giá hạ nguồn V3 trên 100% tập Validation cho các mô hình Sequence và Multi-View
7. **Bảng 3.7 [MỚI]:** Đối sánh hiệu năng cặp đôi Multi-View so với Sequence-Only và kiểm định biên không thua kém
8. **Bảng 3.8 [MỚI]:** Kết quả kiểm thử cắt bỏ che tham số đầu vào trên Sequence-Only đóng băng (H1)
9. **Bảng 3.9 [MỚI]:** Kiểm tra độ nhạy bỏ tham số đầu vào Sequence đối với hiệu năng phát hiện bất thường hạ nguồn (H2)

---

## 7. KẾT LUẬN VÀ KIẾN NGHỊ

Quá trình tích hợp bằng chứng chiến dịch Nineplus V3 vào Master Thesis đã hoàn tất với mức độ liêm chính học thuật và độ chính xác kỹ thuật cao nhất:
- Mọi con số định lượng trong báo cáo đều được truy vết nguồn gốc toán học và thực nghiệm độc lập từ các tệp log và báo cáo đã được chấp thuận.
- 100% các biểu thức toán học được biểu diễn bằng Office Math (OMML) bản địa (600 nút OMML), tuân thủ nghiêm ngặt chính sách công thức của hội đồng khoa học.
- Không có bất kỳ kết quả thực nghiệm nào bị thêm thắt, làm mờ, hay bóp méo; kết quả âm tính của giả thuyết H2 được trình bày một cách khoa học, khách quan và có trách nhiệm.
- Tập Kiểm thử (Test split) tiếp tục được bảo vệ tuyệt đối trong trạng thái niêm phong mật mã.
- Toàn bộ tài liệu Master DOCX và PDF đã được biên dịch, làm mới trường tự động và định dạng chuẩn hóa theo quy chuẩn thể thức của Học viện Kỹ thuật Mật mã.
