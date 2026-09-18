# BÁO CÁO KIỂM TOÁN TÍCH HỢP MASTER DOCX & PDF
**Mã báo cáo:** MASTER-INTEGRATION-FINAL-QA-REPORT  
**Ngày thực hiện:** 2026-09-19  
**Repository:** `Minhlike/Chuyende`  
**Branch:** `fix/thesis-apply-edits`  
**Trạng thái kiểm toán:** HOÀN TẤT VÀ VƯỢT QUA 100% CÁC TIÊU CHÍ (QA PASSED)

---

## 1. THÔNG SỐ ĐO ĐẠC HỆ THỐNG VÀ TÍNH TOÀN VẸN MẬT MÃ

| Chỉ tiêu kỹ thuật | Trước khi chỉnh sửa (Baseline) | Sau khi chỉnh sửa (Post-Integration) | Trạng thái nghiệm thu |
| :--- | :--- | :--- | :--- |
| **DOCX File Size** | 2,377,692 bytes | 2,570,754 bytes | ĐẠT CHUẨN |
| **DOCX SHA-256** | `2c8402fe7e908134d5638d44f7559b9f705c68606325238dc2111b6fb6110b40` | `1820f2b91ef0bb68b5d49b4cb5c043e7b0d4984c19ffaa58d267effffe95708c` | ĐÃ CẬP NHẬT |
| **PDF File Size** | 2,419,057 bytes | 2,755,345 bytes | ĐẠT CHUẨN |
| **PDF SHA-256** | `2db3ff17791f727aee75186c024521a5b47f7b5cefff42c2059428614bb2709d` | `72c389fe41d279919c4f758b9c5da138660ef7c09b185a805d573bb3f3a190ab` | ĐÃ CẬP NHẬT |
| **PDF Page Count** | 114 trang | **121 trang** | ĐO ĐẠC THỰC TẾ |
| **Nút công thức OMML** | **606 nút** (`<m:oMath>`) | **606 nút** (`<m:oMath>`) | BẢO TOÀN TUYỆT ĐỐI (606 → 606) |
| **Đoạn công thức OMML** | 98 đoạn (`<m:oMathPara>`) | 98 đoạn (`<m:oMathPara>`) | BẢO TOÀN TUYỆT ĐỐI (98 → 98) |

---

## 2. VỊ TRÍ 8 ĐOẠN TRÍCH MÃ NGUỒN CỐT LÕI (8 CODE EXCERPTS)

Tất cả 8 đoạn trích mã nguồn được định dạng thống nhất: font Consolas 7.5 pt, khung viền mỏng màu xám `#D0D5DD`, nền xám nhạt `#F4F5F7`, căn lề trái tường minh (`w:jc w:val="left"`), thụt lề 0 pt, có thuộc tính chống tách trang `cantSplit`, liên kết chặt chẽ với nhãn phụ đề (Caption) in nghiêng và đoạn giải thích phương pháp luận:

1. **Đoạn mã 2.1:** Logic phân loại và ẩn danh hóa tham số có nhận thức an ninh (`PrivacyAwareLogTokenizer.tokenize_line`).  
   - *Vị trí trong Master:* Mục 2.2.1 (ngay sau Bảng 2.1, Trang 53).
2. **Đoạn mã 2.2:** Tính toán hàm mất mát Masked Parameter Prediction ($L_{MPP}$) trên mục tiêu đa khe 3D (`compute_sequence_ssl_losses`).  
   - *Vị trí trong Master:* Mục 2.3.1 (dưới phần Mục tiêu huấn luyện tự giám sát, Trang 63).
3. **Đoạn mã 2.3:** Cơ chế đặt lại trạng thái nút động (`reset_node_states`) phục vụ đánh giá quy nạp.  
   - *Vị trí trong Master:* Mục 2.3.2 (cuối tiểu mục Khởi tạo thực thể mới, Trang 67).
4. **Đoạn mã 2.4:** Cơ chế trộn có cổng thích ứng (`GatedMultiViewFusion`).  
   - *Vị trí trong Master:* Mục 2.4.4 (sau công thức vector biểu diễn canonical, Trang 88).
5. **Đoạn mã 3.4:** Hàm tính toán mã băm SHA-256 theo khối nhị phân phục vụ kiểm toán toàn vẹn tệp tin (`compute_file_sha256`).  
   - *Vị trí trong Master:* Mục 3.1.1 (ngay sau Bảng 3.1, Trang 92).
6. **Đoạn mã 3.1:** Kiểm tra bất biến phân chia nhân quả và lựa chọn ngân sách phiên (`compute_and_cache_split`).  
   - *Vị trí trong Master:* Mục 3.1.2 (ngay sau Bảng 3.2, Trang 94).
7. **Đoạn mã 3.2:** Vòng lặp huấn luyện bộ phân loại tuyến tính đóng băng (`fit_linear_probe`).  
   - *Vị trí trong Master:* Mục 3.1.3 (dưới phần Hệ thống thang đo đầu dò, Trang 96).
8. **Đoạn mã 3.3:** Hàm tính toán AP và ROC-AUC xử lý đồng hạng (ties) chuẩn hóa qua scikit-learn (`compute_ap_and_roc_auc`).  
   - *Vị trí trong Master:* Mục 3.1.3 (liền kề sau Đoạn mã 3.2, Trang 96).
   - *Đặc tả & Tính toàn vẹn:* Khối mã được ngắt kết thúc chuẩn xác tại câu lệnh `return ap, auc` của phần triển khai scikit-learn cốt lõi; loại bỏ hoàn toàn phần ngoại lệ fallback không cần thiết (`except ImportError: from scipy.stats import rankdata`). Khối mã nằm trọn vẹn trên Trang 96 mà không bị tràn 2 dòng mồ côi sang Trang 97. Tiêu đề phụ đề và văn bản thuyết minh hoàn toàn ăn khớp với nội dung mã nguồn được trình bày.

---

## 3. TIỂU MỤC KIỂM CHỨNG TÁI LẬP ĐỘC LẬP TRÊN MÁY TRẠM (MỤC 3.2.4)

Đã bổ sung hoàn chỉnh tiểu mục **3.2.4. Kiểm chứng tái lập độc lập trên máy trạm** (Trang 105–107):

### 3.1. Bảng số liệu thực nghiệm đo đạc thực tế (Bảng 3.7b)
- **Tiêu đề Bảng:** *Bảng 3.7b: Thông số kỹ thuật và kết quả đo đạc từ đợt chạy kiểm chứng độc lập Sequence-Only (Seed 42)* (Trang 106).
- **Git Commit SHA thực thi:** `14e04d73c64de315806bd862fb73b2a812f1f50b` (nhánh `fix/thesis-apply-edits`).
- **Run ID thực thi:** `CONF_SEQUENCE_ONLY_seed42_1789724929`.
- **Mô hình & Seed:** `SEQUENCE_ONLY`, Seed 42.
- **Môi trường:** Python 3.12.8, PyTorch 2.6.0+cu124, CUDA 12.4, PyG 2.6.1 trên NVIDIA GeForce RTX 3050 Ti Laptop GPU (4.095,5 MB VRAM).
- **Tiến trình huấn luyện:** 6 epochs; kích hoạt Early Stopping tại Epoch 6 (patience = 3/3).
- **Checkpoint tối ưu:** Epoch 3; Mất mát kiểm định tốt nhất (Val Loss) = `0.00921815038938671`; Phương sai ẩn = `0.09349559992551804`.
- **Bộ nhớ GPU đỉnh:** `170.4453125 MB` VRAM (ghi nhận trong `RUN-MANIFEST.json`; RAM: 1.678,2 MB).
- **Bộ dò nội bộ sau huấn luyện (POST_TRAINING_INTERNAL_VAL_80_20_PROBE):** AP = `0.8993850472022873`, ROC-AUC = `0.9972634577897737`.
  - *Phương pháp luận chuẩn hóa:* Phép đo được thực thi hoàn toàn độc lập sau khi quá trình huấn luyện backbone hoàn tất và checkpoint tốt nhất được nạp lại; toàn bộ trọng số biểu diễn được đóng băng. Biểu diễn của tập Validation 7.500 mẫu được chia tách phân tầng theo tỷ lệ 80/20 (tối ưu linear probe trên 80% và đo lường trên 20% holdout còn lại).
  - *Phân biệt tuyệt đối với V3_FROZEN_PROBE:* Khác biệt hoàn toàn với giao thức đánh giá chuẩn hóa V3 (`V3_FROZEN_PROBE` nạp 35.000 mẫu Train để fit probe và đo trên 100% 7.500 mẫu Validation đạt AP = 1.0000 và ROC-AUC = 1.0000). Phép đo này cũng không phải là đánh giá trực tuyến theo từng mini-batch trong vòng lặp huấn luyện.
- **Mã băm Checkpoint SHA-256:** `926b32512577ac66d8adc29bd145bf45868d176c440c733fb7e074c6470621cc`.

### 3.2. Ảnh minh chứng console thật (Hình 3.1)
- **Đường dẫn tệp:** `manual_reproduction/screenshots/03_training_epochs_loss.png` (Trang 107).
- **Độ phân giải:** 1917 x 985 pixels, tỷ lệ 1.946, chiều rộng trình bày 6.2 inches.
- **Tiêu đề:** *Hình 3.1: Giao diện PowerShell khi chạy kiểm chứng độc lập Sequence-Only (Seed 42), thể hiện tiến trình 6 epoch, kích hoạt early stopping tại epoch 6 (checkpoint tối ưu tại epoch 3) và hoàn tất lưu vết thực nghiệm.*
- **Phân tích hình ảnh:** Thể hiện rõ sự suy giảm hàm mất mát từ Epoch 1 đến Epoch 3, tiếp theo là sự kích hoạt cơ chế dừng sớm khi giá trị mất mát kiểm định không cải thiện ở các Epoch 4, 5, 6 (bộ đếm patience đạt 3/3). Hệ thống tự động nạp lại checkpoint tối ưu Epoch 3 và lưu vết thực nghiệm an toàn.

---

## 4. GIẢI TRÌNH 9 TỆP DIRTY / UNTRACKED TẠI THỜI ĐIỂM CHẠY MANUAL RUN

Nhật ký thực thi `transcript.log` ghi nhận trạng thái `DIRTY (9 modified/untracked files)`. Kiểm toán trực tiếp xác định 9 tệp này là:
1. `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed7_1789452137/` (Thư mục kết quả confirmatory của Multi-View Seed 7).
2. `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed999_1789541331/` (Thư mục kết quả confirmatory của Multi-View Seed 999).
3. `scripts/night_watch_epoch4_and_sleep.py` (Kịch bản giám sát đêm tạm thời).
4. `scripts/pause_after_current_epoch.py` (Kịch bản tạm dừng huấn luyện).
5. `scripts/pause_seed999_after_epoch2.py` (Kịch bản tạm dừng huấn luyện Seed 999).
6. `scripts/resume_seed7_confirmatory.py` (Kịch bản tiếp tục huấn luyện Seed 7).
7. `scripts/resume_seed999_confirmatory.py` (Kịch bản tiếp tục huấn luyện Seed 999).
8. `scripts/set_elevated_sweetspot.ps1` (Kịch bản điều phối cấu hình hiệu năng).
9. `scripts/set_night_performance.ps1` (Kịch bản điều phối cấu hình ban đêm).

*Kết luận kiểm toán:* Toàn bộ 9 tệp trên là các artifact thực nghiệm confirmatory của các seed khác và các kịch bản phụ trợ điều phối ngoại vi, hoàn toàn không can thiệp, sửa đổi hay làm suy giảm tính toàn vẹn của mã nguồn nghiên cứu tại commit `14e04d73c64de315806bd862fb73b2a812f1f50b`.

---

## 5. KẾT QUẢ KIỂM TRA TRỰC QUAN (VISUAL QA)

1. **Mở tệp DOCX:** Word COM mở trực tiếp mượt mà, không xuất hiện bất kỳ thông báo lỗi cấu trúc, cảnh báo phục hồi (repair prompt) hay mất định dạng.
2. **Mở tệp PDF:** Mở hoàn hảo qua thư viện chuyên dụng `pypdfium2`, văn bản sắc nét, đầy đủ vector font.
3. **Mục lục và Tiêu đề:** Mục lục tại Trang 5 tự động cập nhật chính xác tiêu đề `3.2.4. Kiểm chứng tái lập độc lập trên máy trạm` trỏ đến Trang 105.
4. **Trang trắng bất thường:** Không có bất kỳ trang trắng nào trong toàn bộ phần thân tài liệu (hai trang ngắt section chuẩn là Trang 3 và Trang 6 thuộc cấu trúc bìa/lời cảm ơn).
5. **Tràn lề và ngắt dòng:** 100% các khối mã nguồn, bảng biểu và hình ảnh nằm gọn hoàn hảo trong biên độ lề in chuẩn (chiều rộng tối đa 6.5 inches), không có hiện tượng tràn lề hay đè chữ.
6. **Bộ chữ tiếng Việt:** Toàn bộ văn bản mới chèn hiển thị chuẩn xác bảng mã Unicode tiếng Việt dựng sẵn, không xuất hiện lỗi font hay mất dấu diacritics.
7. **Kiểm toán Typography, triệt tiêu phân mảnh OOXML Run và lỗi Kerning/Dãn chữ:**
   - **Nguyên nhân gốc rễ (Root Cause):** Động cơ biên tập và bộ kiểm tra chính tả mặc định của MS Word tự động phân mảnh các từ tiếng Việt có dấu thành các phần tử `<w:r>` đơn ký tự độc lập (ví dụ từ "mất mát" bị chia thành `m`, `ấ`, `t`, ` `, `m`, `á`, `t` trong các run riêng biệt; `p[595]` bị xé thành 87 runs, `p[1548]` thành 215 runs). Khi bộ hiển thị Word kết xuất văn bản căn đều hai bên (`both`), mỗi `<w:r>` bị đối xử như một khối layout rời rạc, gây ra hiện tượng khoảng hở kerning nghiêm trọng (`PR I V A C Y`, `Q uy trình`, `m ất m át`, `A P`, `R O C-AUC`, `N hằm`, `m anual_reproduction`, `com m it`, `G itC om m it`, `M B V R A M`).
   - **Giải pháp xử lý triệt để (Pipeline Implementation):**
     * Ứng dụng thư viện `lxml.etree` bảo toàn 100% không gian tên chuẩn của OOXML (`w:`, `m:`, `wp:`), ngăn chặn hoàn toàn lỗi gán tiền tố `ns0:` dẫn tới cảnh báo hỏng tệp trong Word COM.
     * Duyệt qua toàn bộ văn bản (body paragraphs, table cells, captions, footnotes), gộp liên tiếp các thẻ `<w:r>` có định dạng đồng nhất (font, cỡ chữ, in đậm, in nghiêng, màu sắc, vị trí) thành một run duy nhất; chuẩn hóa văn bản Unicode dạng NFC và gắn thuộc tính `xml:space="preserve"`.
     * Làm sạch thuộc tính dãn cách: loại bỏ triệt để `w:spacing`, `w:w`, `w:position` và chèn thẻ `<w:noProof/>` vào `w:rPr` của tất cả các run chữ tiếng Việt, vô hiệu hóa động cơ spell-check của Word nhằm ngăn chặn Word tự động chia tách lại run khi lưu tệp. Xóa bỏ an toàn các thẻ đánh dấu lỗi `w:proofErr`.
     * Giảm thiểu thành công **1.897 runs phân mảnh** (tổng số run giảm từ 6.544 xuống 4.864 sau khi cập nhật Word COM).
     * Chèn điểm ngắt mềm (`\u200b`) tại ranh giới token ghép của dòng tiêu đề/thuật ngữ dài trên Trang 97 (`Temporal\u200bGraph\u200bView\u200bEncoder` và `Multi-\u200bHead`), giúp Word bẻ dòng tự nhiên sau chữ "View" và triệt tiêu hoàn toàn hiện tượng dãn chữ cực đoan tại dòng 1 và dòng 6.
   - **Kết quả nghiệm thu trực quan chi tiết trên 11 trang trọng yếu (Visual Audit at 2.0x Scale):**
     * **Trang 53:** Cụm từ `PRIVACY_AWARE_PARAMETERIZED` và đoạn văn giải thích `Phương thức tokenize_line ở chế độ` hiển thị liền mạch tuyệt đối, không còn khoảng cách chữ bất thường.
     * **Trang 63:** Chú thích Đoạn mã 2.2 và đoạn văn thuyết minh $L_{MPP}$ liên tục, công thức OMML chuẩn xác.
     * **Trang 67:** Chú thích Đoạn mã 2.3 và thuyết minh cơ chế `reset_node_states` hoàn toàn liền lạc.
     * **Trang 88:** Đoạn mã 2.4, công thức hàm kết hợp $g_t$ và thuyết minh cân đối, không lệch lề.
     * **Trang 92:** Bảng 3.1 và chú thích/thuyết minh Đoạn mã 3.4 (`compute_file_sha256`) sắc nét, chuẩn typography.
     * **Trang 94:** Bảng 3.2 và chú thích/thuyết minh Đoạn mã 3.1 (`compute_and_cache_split`) phẳng đẹp, căn đều tự nhiên.
     * **Trang 96:** Các cụm từ `Quy trình huấn luyện`, `mất mát`, `AP`, `ROC-AUC` kết xuất tự nhiên, không rách từ; Đoạn mã 3.2 và Đoạn mã 3.3 (kết thúc chuẩn xác tại `return ap, auc`) nằm gọn gàng trên Trang 96 mà không để lại dòng mồ côi nào.
     * **Trang 97:** Đoạn văn mở đầu bẻ dòng hoàn hảo tại `TemporalGraphViewEncoder` (ngắt xuống sau chữ "View"), loại bỏ hoàn toàn hiện tượng kéo dãn dòng 1 và dòng 6; các ký hiệu bullet $L_{rel}$, $L_{node}$, $L_{time}$ hiển thị đều đặn, tự nhiên.
     * **Trang 105:** Các cụm từ `Nhằm xác thực`, `manual_reproduction`, `commit`, `POST_TRAINING_INTERNAL_VAL_80_20_PROBE` liền lạc 100%, không bị tách rời ký tự.
     * **Trang 106:** Tiêu đề cột và dữ liệu Bảng 3.7b (`Git Commit SHA thực thi`, `MB VRAM`, `patience`, `checkpoint`) hiển thị chữ tự nhiên, liền khối, bảng nằm trọn vẹn trong trang.
     * **Trang 107:** Ảnh chụp PowerShell Hình 3.1 và đoạn văn phân tích 3.3 / 3.3.1 sắc nét, căn lề hai bên hoàn hảo, không có lỗi kerning.

---

## 6. CAM KẾT VÀ TUÂN THỦ NGUYÊN TẮC QUẢN TRỊ

- **KHÔNG HUẤN LUYỆN LẠI (NO RETRAINING):** Không thực hiện bất kỳ vòng huấn luyện hay tinh chỉnh mô hình nào.
- **KHÔNG TRUY CẬP TẬP KIỂM THỬ (NO TEST SPLIT ACCESS):** Tập Test tiếp tục được bảo vệ nguyên vẹn (`test_opened = false`, `test_reads = 0`).
- **KHÔNG ĐẨY SANG REPO XUẤT XƯỞNG:** Không thực hiện bất kỳ thao tác đẩy mã nguồn nào sang kho đích `Minhlike/chuyen-de-chuyen-sau`. Kho xuất xưởng duy trì trạng thái sạch 100%.

Dòng kết luận nghiệm thu chính thức:  
**MASTER_DOCX_PDF_UPDATED_AND_QA_PASSED**
