# Kế hoạch hiệu chỉnh độ rõ ràng OMML Chương 1–2

## Nền và phạm vi

- Baseline nội dung: `D:\chuyen-de-chuyen-sau\Chuyên đề chuyên sâu.docx`, SHA-256 `9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033`.
- Repo xưởng khởi đầu tại `cb6b30028501690c8b7dc70f8e72f78a68ce38f0`; nhánh `codex/omml-ch1-ch2-clarity` trong worktree sạch thuộc `D:\Research\.tmp\omml-ch1-ch2-clarity`.
- Chỉ chèn chú giải/ví dụ quanh công thức thuộc Chương 1–2. Không tái dựng tài liệu từ builder cũ vì bản builder không chứa Master xuất xưởng hiện hành. Dùng chỉnh sửa OOXML cục bộ trên bản sao chính xác của Master, giữ nguyên toàn bộ OMML hiện có trừ lỗi toán học được chứng minh.
- Kiểm kê XML ở `docs/OMML-CLARITY-INVENTORY.json`: 30 công thức Chương 1, 525 Chương 2, gồm cả inline và 52 nút trong bảng; toàn tài liệu 622. Mỗi nút có vị trí, ngữ cảnh, dấu vân tay XML, ký hiệu bề mặt, phân loại ban đầu và rủi ro đơn giản hóa. `INITIAL_TRIAGE` phải được chuyển thành trạng thái đã soát trước khi nghiệm thu.

## Thứ tự biên tập

1. Rà từng nhóm tại 197 vị trí chứa OMML. Phân biệt ký hiệu đã định nghĩa đủ với chỗ thiếu miền giá trị, kích thước, đơn vị hoặc trực giác. Ưu tiên các công thức độc lập và các nhóm có rủi ro kết luận khoa học.
2. Chương 1: cửa sổ và trôi dạt; không gian nhãn; Hợp đồng Biểu diễn; vector đếm, TF-IDF, entropy; PCA và bất biến; top-g; đồ thị nguồn gốc. Giải thích ngắn ngay cạnh công thức, thêm ví dụ số cho các phép tính trung bình/cốt lõi.
3. Chương 2: bộ sáu, trạng thái dòng, H1–H5 và ER1; chuẩn hóa/giả danh hóa/thời gian; chuỗi Transformer và các mất mát; Temporal GNN; VICReg; Stage A, PCGrad, Attention-MIL, dung hợp và ngân sách. Những ví dụ không phải số liệu thực nghiệm đều ghi `Ví dụ minh họa`.
4. Chỉ tạo phép thay số mới dưới dạng OMML native. Giữ nguyên kiểu trình bày học thuật, không tạo hộp lặp lại. Không làm sai hàm ý: bất thường ≠ tấn công, attention ≠ giải thích nhân quả, loss thấp ≠ hiểu an ninh, phụ thuộc đồ thị ≠ nhân quả, giả danh hóa ≠ bảo đảm riêng tư.
5. Mọi lỗi công thức được xử lý riêng: bằng chứng từ công thức, prose và mã hiện hành; ghi ledger lý do và kiểm tra claim trước/sau. Nếu không đủ bằng chứng thì giữ công thức và chỉ làm rõ điều kiện diễn giải.

## Cổng nghiệm thu xưởng

- Soát hết 555 hồ sơ, không còn trạng thái chờ, không ký hiệu vô nguồn ở phạm vi đọc hợp lý; kiểm tra độc lập mọi phép thay số.
- So sánh thứ tự/dấu vân tay 555 OMML gốc; công thức sửa phải có ledger riêng. XML và quan hệ gói DOCX hợp lệ; bookmark, field, citation, section break, shape/vector/metadata được bảo toàn.
- Word COM mở bằng bản Word riêng, cập nhật field, phân trang, lưu, xuất PDF, đóng/mở lại không repair. PDF/A và font embedding theo quy trình hiện hành.
- Render toàn bộ trang Chương 1–2 và các vùng lân cận; kiểm tra equation, đoạn chú giải, hình/bảng, header/footer, số trang, TOC/TOF/Table List. Kiểm tra Chương 3 qua hash văn bản và toàn bộ OMML gốc; references/citation integrity không giảm.
- Tạo provenance ghi HEAD/branch, SHA-256 trước/sau, danh sách thay đổi, số công thức/ví dụ/chỉnh toán, kết quả từng gate. Không đồng bộ/push bản xuất xưởng nếu một gate FAIL.

## Xuất xưởng

Sau khi mọi gate xưởng PASS, chỉ đưa DOCX/PDF và báo cáo/provenance cần thiết sang `D:\chuyen-de-chuyen-sau`, chạy lại cùng các kiểm tra trên chính bản này, rồi commit/push tuần tự không force push. Lưu exact final HEAD và SHA-256.
