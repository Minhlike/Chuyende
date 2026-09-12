# KMA Reference Directory & Provenance Ledger

Thư mục này lưu trữ các tài liệu quy chuẩn định dạng và căn cứ pháp lý của Học viện Kỹ thuật Mật mã (KMA) phục vụ công tác đối soát hình thức trình bày văn bản khoa học.

---

## Danh mục tài liệu và phân loại thẩm quyền (Authority Classification)

### 1. `KMA_AT17_2024_Ke_hoach_bao_ve_DATN.pdf`
- **Phân loại**: `OFFICIAL_KMA`
- **Mô tả**: Văn bản chính thức của Học viện Kỹ thuật Mật mã ban hành Kế hoạch tổ chức bảo vệ Đồ án tốt nghiệp ngành An toàn thông tin khóa AT17 (năm 2024), xác nhận Quyết định số 268/QĐ-HVM ngày 10/04/2024 là quy chuẩn hình thức áp dụng.
- **Nguồn / URL**: Cổng thông tin chính thức Học viện Kỹ thuật Mật mã: [https://actvn.edu.vn/News/DownloadFile?idFile=4347](https://actvn.edu.vn/News/DownloadFile?idFile=4347)
- **Định dạng / Magic bytes**: PDF document (`%PDF-1.5`)
- **Kích thước**: 1,530,364 bytes
- **Ngày truy xuất**: 12/09/2026
- **Mức độ thẩm quyền**: **Cấp 1 - Văn bản chính thức có giá trị pháp lý cao nhất**

### 2. `QD268_HVM_2024_Scribd_snapshot.html`
- **Phân loại**: `THIRD_PARTY_MIRROR`
- **Mô tả**: Bản snapshot định dạng HTML lưu trữ trực quan tài liệu "Quy định hình thức trình bày quyển Đồ án tốt nghiệp kèm theo Quyết định số 268/QĐ-HVM ngày 10/04/2024 của Học viện Kỹ thuật Mật mã" từ nền tảng lưu trữ trực tuyến Scribd. File này là HTML/web snapshot, không phải file PDF gốc.
- **Nguồn / URL**: [https://www.scribd.com/document/732860888/QD268-HVM-2024-Quy-Dinh-Trinh-Bay-DATN](https://www.scribd.com/document/732860888/QD268-HVM-2024-Quy-Dinh-Trinh-Bay-DATN)
- **Định dạng / Magic bytes**: HTML text (`<!doctype html>`)
- **Kích thước**: 1,170,537 bytes
- **Ngày truy xuất**: 12/09/2026
- **Mức độ thẩm quyền**: **Cấp 3 - Bản sao lưu trực quan từ bên thứ ba (dùng để tham chiếu chéo giao diện và bố cục)**

### 3. `QD268_HVM_2024_extracted_readable.txt`
- **Phân loại**: `DERIVED_TEXT`
- **Mô tả**: Toàn bộ nội dung quy định cốt lõi (Phụ lục I: Hình thức trình bày ĐATN, khổ giấy, căn lề, phông chữ, cỡ chữ, giãn dòng, đánh số trang, tiểu mục, bảng biểu, hình vẽ, trích dẫn tài liệu tham khảo) được trích xuất sạch sẽ, loại bỏ toàn bộ mã kịch bản / wrapper HTML.
- **Nguồn gốc dẫn xuất**: Trích xuất từ các trang 1, 2 và 3 của văn bản QĐ 268/QĐ-HVM.
- **Định dạng**: Plain text UTF-8
- **Ngày tạo**: 12/09/2026
- **Mức độ thẩm quyền**: **Cấp 2 - Dữ liệu trích xuất văn bản phục vụ phân tích máy và kiểm toán quy chuẩn**

### 4. `page_1.jpg`
- **Phân loại**: `DERIVED_TEXT` / `THIRD_PARTY_MIRROR`
- **Mô tả**: Bản quét hình ảnh quang học trang 1 Phụ lục I QĐ 268/QĐ-HVM, phục vụ kiểm chứng thị giác trực tiếp (Visual Ground Truth).
- **Định dạng / Magic bytes**: JPEG image (`\xff\xd8\xff\xe0`)
- **Kích thước**: 215,864 bytes
- **Mức độ thẩm quyền**: **Cấp 2 - Bằng chứng thị giác trực tiếp**

### 5. `embed_pages_1_to_3.txt`
- **Phân loại**: `AUDIT_ARTIFACT`
- **Mô tả**: Bản kết xuất nguyên gốc từ DOM của các trang 1-3 chứa đầy đủ metadata phục vụ truy vết kiểm toán.
- **Định dạng**: Plain text UTF-8
- **Kích thước**: 7,871 bytes

### 6. `KMA_FORMATTING_COMPLIANCE.md`
- **Phân loại**: `AUDIT_ARTIFACT`
- **Mô tả**: Bảng ma trận đối soát chi tiết từng tiêu chí định dạng giữa văn bản Master (`Chuyên đề chuyên sâu.docx`) và các quy định tại QĐ 268/QĐ-HVM và Kế hoạch AT17.
