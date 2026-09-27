# Nghiệm thu xưởng: chú giải OMML Chương 1–2

## Nguồn và phạm vi

- Master nguồn là DOCX ở repo `Minhlike/chuyen-de-chuyen-sau`, commit `d7578872c9b101450ce1b1fcaa73f52dd1c97309`, SHA-256 `9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033`.
- Repo xưởng bắt đầu tại `cb6b30028501690c8b7dc70f8e72f78a68ce38f0`; mọi sửa đổi ở nhánh `codex/omml-ch1-ch2-clarity`.
- Đã kiểm kê cả 555 vùng OMML gốc trong Chương 1–2: 30 ở Chương 1, 525 ở Chương 2, gồm 52 vùng nằm trong bảng. Hồ sơ từng vùng ở `OMML-CLARITY-INVENTORY.json`; không còn trạng thái chờ soát.
- Đã bổ sung 45 đoạn chú giải gọn theo ngữ cảnh, sát 304 vùng OMML gốc; 251 vùng còn lại được đối chiếu với văn cảnh hiện có. Có 31 phép thay số được kiểm tra độc lập và 33 vùng OMML native mới cho minh họa. Không chuyển phương trình thành ảnh hoặc văn bản giả công thức.

## Các trường hợp trước → sau tiêu biểu

| Nhóm | Trước | Sau |
|---|---|---|
| Entropy | Chỉ nêu xác suất loại sự kiện và phép cộng log. | Giải thích cửa sổ, tần suất, đơn vị bit; thay A,A,B,B cho 1 bit và A,A,A,A cho 0; khẳng định entropy không tự xác nhận tấn công. |
| PCA | Nêu phần dư và ngưỡng một cách trừu tượng. | Thay vector (3,2) với trục giữ lại (1,0), được phần dư (0,2) và bình phương chuẩn 4; phân biệt cờ lệch nền với nguyên nhân độc hại. |
| MPP | Mẫu số đếm sự kiện dù tử số cộng khe tham số. | Mẫu số đếm đúng khe bị che không đệm; ví dụ xác suất 0,8 và 0,5 cho mất mát trung bình khoảng 0,458; nêu trường hợp không có khe hợp lệ. |
| VICReg | Nêu phương sai/hiệp phương sai mà khó hình dung hình phạt. | Lô hai vector cho độ lệch chuẩn khoảng 1,414, chiều hằng bị phạt khoảng 0,99 và hiệp phương sai ngoài đường chéo cho hình phạt 4; không suy ra độc lập thống kê hay ngữ nghĩa an ninh. |
| PCGrad | Nêu phép chiếu gradient. | Với (1,−1) và (−1,0), tích vô hướng −1 được chiếu thành (0,−1); chỉ là xử lý xung đột cục bộ, không bảo đảm cả hai mục tiêu cùng cải thiện. |

## Hai chỉnh sửa thực sự vào công thức gốc

1. `L_MPP`: thay trung bình theo số sự kiện bằng trung bình theo tổng số khe tham số bị che hợp lệ. Mã ngay trong Đoạn mã 2.2 dùng `mpp_logits[mpp_mask]` và trung bình cross-entropy trên các khe đã chọn.
2. `L_time`: đầu hồi quy được văn bản định nghĩa nhận vector ghép kích thước `2d_model`, nhưng công thức cũ chỉ truyền `h_i`; đối số nay là `[h_i; h_(i+1)]`.

Chi tiết trước/sau, bằng chứng và phạm vi claim ở `OMML-CLARITY-MATH-CORRECTIONS.json`. Không sửa claim khoa học, số liệu thực nghiệm hoặc nội dung Chương 3.

## Cổng QA

| Cổng | Kết quả |
|---|---|
| Toán học/ví dụ | PASS: 31 kiểm tra số; hai công thức sửa được đối chiếu với prose và triển khai. |
| OMML/OOXML | PASS: 622→655 vùng toàn tài liệu; 620 vùng gốc còn nguyên nội dung và thứ tự; 2 sửa có ledger; không vùng rỗng, không quan hệ gói hoặc rId treo. |
| Word thật | PASS: mở, cập nhật trường, phân trang, lưu, mở lại và xuất PDF từ bản đã lưu; không báo repair. PDF tái xuất có 129 trang. `ComputeStatistics` trong Word COM ẩn trả giá trị tạm 156, nên lấy PDF tái xuất làm chuẩn phân trang. |
| Hình thức | PASS: soát PDF trang 15–98; không thấy phương trình tràn lề, chú giải mồ côi, trang trắng, hình/bảng vỡ; Bảng 2.4 qua trang 88–89 có hàng tiêu đề lặp. |
| Citation/fields | PASS: 186 `CITATION`, 82 `PAGEREF`, 24 `SEQ`, 8 `REF`, 3 `TOC`, 1 `BIBLIOGRAPHY`; 114 bookmark và 11 drawing được giữ. Danh mục bảng giữ Bảng 3.7b. |
| PDF/A/phông | PASS: PDF/A‑1a XMP, output intent, tất cả 11 phông được nhúng; 9 phần phông trong DOCX còn nguyên. |
| Chương 3/References | PASS: băm văn bản và OMML Chương 3 trước/sau trùng chính xác; References nằm trong vùng đối chiếu này. |

DOCX cuối SHA-256 `93b8df9d8485b153b97cacb9025aeeca475d28c454299852131b7db06e0937c7`; PDF cuối SHA-256 `307154e3d4cdabf35f73dbd7e95666baa6dbffd3d70da74c2a2ffc0989b3883b`. Các báo cáo máy đọc được nằm ở `OMML-CLARITY-*` trong cùng thư mục.

Giới hạn còn lại của thiết kế gốc: `Cov_event`, `Cov_graph`, `Density_edge` mới là chỉ báo chất lượng dự kiến, chưa khóa công thức đo. Bản chú giải nêu rõ điều này và không tự đặt số giả để thay vào.
