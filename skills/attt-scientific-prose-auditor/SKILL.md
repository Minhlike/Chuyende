---
name: attt-scientific-prose-auditor
description: >-
  Audit and refine academic and scientific prose according to ATTT Scientific Prose Auditor v2.2 guidelines
  (Khúc Hữu Hùng, Tạp chí An toàn thông tin, 19/08/2026). Detects AI-slop, empty fluency, ownerless claims,
  inflated technical adjectives, and template clustering, while strictly enforcing 100% preservation of
  mathematical equations (OMML), scientific invariants, hypotheses, tables, figures, headings, and empirical metrics.
---

# ATTT Scientific Prose Auditor v2.2

## 1. Triết lý Cốt lõi & Định nghĩa AI-Slop (Tạp chí ATTT 19/08/2026)

Theo công bố *"AI slop hay rác AI: Từ hiện tượng ngôn ngữ đến rủi ro an ninh mạng"* (Khúc Hữu Hùng, *Tạp chí An toàn thông tin*), AI-slop không đồng nghĩa với văn bản do AI tạo ra, mà là **nội dung trôi chảy nhưng rỗng, lặp khuôn, vắng chủ thể chịu trách nhiệm và chuyển gánh nặng kiểm chứng sang người đọc**.

Trọng tâm của Skill không phải là che giấu sự tham gia của AI hay tối ưu điểm số AI-detector, mà là **nâng cao chất lượng khoa học, tính chịu trách nhiệm và khả năng kiểm chứng độc lập** của văn bản nghiên cứu.

---

## 2. Kiến trúc Ba Lớp (Three-Tier Architecture)

| Lớp | Trọng tâm kiểm toán | Quy tắc bất biến bắt buộc |
|---|---|---|
| **1. Scientific Invariants** | Giả thuyết (H1–H5), Trích dẫn ([1]–[43]), Số liệu đo đạc Stage A2, Ranh giới phân định (Extractor–Detector), Giới hạn (Caveats) | **100% bất biến**: Không đổi ý nghĩa hypothesis, không đổi claim–citation mapping, không sửa raw metrics, không suy diễn vượt phép đo. |
| **2. Rhetorical Auditor** | Mẫu câu dập khuôn (Template clusters), Từ mở đầu lặp lại (Stock openers), Văn phong sáo rỗng (Empty fluency), Tính từ khoa trương (Inflated prose), Mệnh đề vô chủ (Ownerless claims) | Phân tích chức năng lập luận thay vì đếm token cơ học; xóa bỏ nợ mẫu cục bộ; quy rõ chủ thể tri thức. |
| **3. DOCX/OMML Safety** | Phân loại đoạn văn (`PLAIN_TEXT`, `MIXED_PROTECTED`, `PROTECTED_ONLY`, `FIELD_OR_DRAWING`), Bảo vệ cấu trúc XML | **Tuyệt đối cấm** `paragraph.text = rewritten` trên đoạn chứa OMML hoặc Word Fields; bảo toàn toàn vẹn 202 phương trình OMML và 14 bảng. |

---

## 3. Bốn Chế độ Hoạt động (Operating Modes)

```yaml
modes:
  - AUDIT_ONLY: Quét pháp chứng, lập kho lưu trữ (inventory), phát hiện vi phạm và xuất báo cáo JSON/MD (Mặc định).
  - VERIFY_REFERENCES: Kiểm tra 2 tầng: Nguồn có tồn tại (existence) và Nguồn có hỗ trợ claim hay không (semantic claim support).
  - PREVIEW_REWRITE: Soạn thảo bản vá dạng before/after hash có kiểm tra invariants, trình tác giả duyệt.
  - APPLY_REWRITE: Áp dụng bản vá đã duyệt vào file DOCX theo transaction semantics an toàn.
```

---

## 4. Tám Cổng Kiểm soát Bắt buộc (Hard Gates)

| Mã Cổng | Tên Cổng | Điều kiện ĐẠT (PASS) |
|---|---|---|
| **GATE-1** | `REFERENCE_INTEGRITY` | 100% citation tồn tại từ nguồn chính thống, metadata chuẩn xác, hỗ trợ đúng ngữ nghĩa claim. |
| **GATE-2** | `HYPOTHESIS_ID_CONSISTENCY` | Các mã định danh H1–H5 mang cùng một ý nghĩa thống nhất từ định nghĩa (Chương 2) đến kiểm chứng (Chương 3) và kết luận. |
| **GATE-3** | `CLAIM_EVIDENCE_PROPORTIONALITY` | Kết luận không vượt quá bằng chứng thực nghiệm (ví dụ: GPU VRAM < 550 MB chỉ kết luận về dung lượng bộ nhớ cục bộ, không suy diễn sang đáp ứng luồng SOC thời gian thực khi chưa có độ trễ/thông lượng). |
| **GATE-4** | `EPISTEMIC_ACCOUNTABILITY` | Mọi khẳng định thực chất đều có chủ thể: `CITED_LITERATURE`, `AUTHOR_PROPOSAL`, `OBSERVED_RESULT`, `DERIVED_RESULT`, `ASSUMPTION`, `LIMITATION`, `REQUIREMENT`, `INTERPRETATION`. Cấm `UNKNOWN`. |
| **GATE-5** | `SPECIFICITY` | Sử dụng chỉ số, phương pháp, tập dữ liệu hoặc điều kiện cụ thể; không dùng tính từ đánh giá rỗng thay thế cho đặc tả kỹ thuật. |
| **GATE-6** | `NO_NEW_CLAIMS` | Quá trình biên tập/viết lại tuyệt đối không tạo thêm dữ kiện, số liệu hoặc giả định mới ngoài tài liệu gốc. |
| **GATE-7** | `CITATION_PRESERVATION` | Mối liên kết giữa mệnh đề và tài liệu trích dẫn được bảo toàn 100%. |
| **GATE-8** | `OMML_INTEGRITY` | Toàn bộ các công thức toán học OMML và các trường dữ liệu động (Fields) giữ nguyên vẹn cấu trúc XML. |
| **GATE-9** | `NO_REPEATED_ENGLISH_ANNOTATION` | Tuyệt đối không chú thích tiếng Anh trong ngoặc đơn quá 1 lần cho cùng một thuật ngữ (chỉ giữ ở lần đầu xuất hiện). |
| **GATE-10** | `NO_BODY_UNWARRANTED_BOLD` | Thân bài chỉ dùng chữ in thường (regular text), cấm các tiền tố/nhãn in đậm tùy tiện kiểu Markdown/AI. |
| **GATE-11** | `UNIFIED_DASH_STANDARD` | 0 em-dash `—` kiểu AI; hạn chế tối đa dấu gạch ngang; quy chuẩn dải số/tham chiếu về chuẩn Microsoft Word; không lạm dụng ngoặc đơn. |
| **GATE-12** | `DISCOURSE_CONNECTOR_TYPOGRAPHY` | Không có gạch ngang đầu dòng khi đã có Thứ nhất/Một là; liên từ nghị luận in nghiêng (`*Thứ nhất, *`, `*Một là, *`), phần sau in thường. |
| **GATE-13** | `DYNAMIC_TABLE_CITATION_FIELDS` | 100% chú thích trong bảng là Word dynamic CITATION field hỗ trợ Edit Source / Edit Citation. |

---

## 5. Quy tắc Nhận diện Vi phạm Văn phong Học thuật

### 5.1. Cụm từ Mở đầu Dập khuôn (`REPEATED_STOCK_OPENERS` & `TEMPLATE_CLUSTERING`)
- **Regex nhận diện**:
  ```regex
  ^\s*(?:\d+[\.\)]\s*|-\s*|\*\s*)?(Về mặt|Nhằm|Để|Trong bối cảnh|Đáng chú ý(?: là)?|Cần nhấn mạnh rằng|Có thể thấy rằng|Từ đó|Qua đó|Bên cạnh đó|Đồng thời|Mặt khác)\b
  ```
- **Ngưỡng vi phạm nghiêm trọng (Clustering Threshold)**:
  - Xuất hiện $\ge 2$ lần trong cửa sổ 3 đoạn văn liên tiếp; hoặc
  - Xuất hiện $\ge 3$ lần cùng một từ mở đầu trong cửa sổ 20 đoạn văn.
- **Biện pháp xử lý**: Tái cấu trúc logic đoạn văn (restructuring), **tuyệt đối không "rửa từ đồng nghĩa" (synonym laundering)** như đổi "Về mặt" thành "Xét trên phương diện" hay "Ở khía cạnh".

### 5.2. Văn phong Sáo rỗng (`EMPTY_FLUENCY`)
- **Đặc trưng**: Khẳng định mạnh mang tính đánh giá ("toàn diện", "hiệu quả cao", "tối ưu vượt trội") kết hợp mức độ đặc tả kỹ thuật thấp và không có bằng chứng neo (no evidence anchor).
- **Biện pháp xử lý**: Thu hẹp phạm vi khẳng định (`NARROW_CLAIM`) hoặc bổ sung tham chiếu bằng chứng nội tại (`ANCHOR_EVIDENCE`). Cấm bịa số liệu.

### 5.3. Mệnh đề Vô chủ (`OWNERLESS_CLAIM`)
- **Cụm từ cảnh báo**: "có thể thấy rằng", "có thể khẳng định", "được đánh giá là", "được xem là", "rõ ràng là".
- **Biện pháp xử lý**: Gắn rõ chủ thể phát ngôn: theo tài liệu [k], theo thiết kế đề xuất của Chuyên đề, hoặc theo kết quả ghi nhận từ thực nghiệm Stage A2.

### 5.4. Tính từ Kỹ thuật Khoa trương (`INFLATED_TECHNICAL_PROSE`)
- **Các từ cần rà soát**: `cốt lõi`, `toàn diện`, `tường minh`, `chặt chẽ`, `tuyệt đối`, `nghiêm ngặt`, `vững chắc`, `then chốt`.
- **Nguyên tắc**: **"SHOW CONTROL, DO NOT LABEL CONTROL"** — Trình bày cơ chế kiểm soát kỹ thuật thay vì dán nhãn tính từ khoa trương.

### 5.5. Cấu trúc Điểm nối Nghị luận Học thuật (`ACADEMIC_DISCOURSE_CONNECTORS`)
- **Đặc trưng**: Các danh sách liệt kê cộc lốc hoặc chuỗi đoạn văn rời rạc, thiếu liên từ lập luận tự nhiên; hoặc có liên từ (*Thứ nhất*, *Một là*) nhưng vẫn bị gắn gạch ngang đầu dòng (`– `) do list bullet (`w:numPr`).
- **Biện pháp xử lý**:
  - Chuyển đổi sang hệ thống liên từ chuẩn: *"Thứ nhất, ... Thứ hai, ... Thứ ba, ... Thứ tư, ..."* hoặc *"Một là, ... Hai là, ... Ba là, ..."*.
  - **Tuyệt đối cấm gạch ngang đầu dòng**: Khi đã dùng liên từ nghị luận, phải gỡ bỏ 100% thuộc tính `w:numPr` và gạch đầu dòng, định dạng thành đoạn văn xuôi độc lập (firstLine=720).
  - **In nghiêng cụm liên từ đầu đoạn**: Cụm từ liên từ kèm dấu phẩy (`*Thứ nhất, *`, `*Thứ hai, *`, `*Một là, *`, `*Hai là, *`) bắt buộc phải in nghiêng (`w:i`), phần nội dung tiếp theo in thường (regular roman).

### 5.6. Tiền tố In đậm Tùy tiện trong Thân bài (`UNWARRANTED_BOLD_PREFIX`)
- **Đặc trưng**: Tự ý in đậm các tiền tố đánh số hoặc nhãn định danh đầu đoạn theo cú pháp Markdown (`**Concept Drift:**`, `**1.**`, `**(i)**`, `**Giả thuyết H1:**`).
- **Nguyên tắc**: Thân bài chỉ dùng chữ in thường (regular text). In đậm chỉ dành riêng cho Heading các cấp, Caption Bảng/Hình và Header của Bảng.
- **Biện pháp xử lý**: Gỡ bỏ triệt để thuộc tính in đậm `<w:b/>` ở mức OpenXML.

### 5.7. Khử Trùng lặp Chú thích Tiếng Anh & Tinh giản Thuật ngữ Cơ bản (`ENGLISH_PARENTHETICAL_DEDUPLICATION_AND_PRUNING`)
- **Quy tắc Chú thích Duy nhất (Single Annotation Policy)**: Tuyệt đối không chú thích tiếng Anh 2 lần cho cùng một thuật ngữ. Chỉ giữ lại chú thích tiếng Anh trong ngoặc đơn ở lần xuất hiện đầu tiên, xóa bỏ 100% từ lần thứ 2 trở đi.
- **Lược bỏ chú thích ở thuật ngữ Deep Learning / CNTT cơ bản**: Lược bỏ các chú thích tiếng Anh trong ngoặc đơn đối với những khái niệm quen thuộc với giới nghiên cứu Việt Nam (*nhật ký hệ thống*, *nhúng từ*, *lô huấn luyện*, *sai số toàn phương trung bình*, *tập xác thực*, *kỹ thuật khởi động*, *các kênh rò rỉ*, v.v.).
- **Mục tiêu**: Giảm thiểu mật độ ngoặc đơn dày đặc, tối ưu hóa mạch văn tự nhiên, thuần Việt cho độc giả.

### 5.8. Loại bỏ Dấu Gạch Ngang Kiểu AI, Chuẩn hóa & Tinh giản Dấu Gạch Ngang (`UNWARRANTED_DASH_ELIMINATION`)
- **Cấm triệt để Em-dash (`—` `\u2014`)**: Loại bỏ 100% dấu gạch ngang dài kiểu AI khỏi toàn bộ văn bản và bảng biểu; đưa về chuẩn Microsoft Word 2016 hoặc xóa bỏ/viết lại mạch lạc.
- **Quy chuẩn về 1 kiểu duy nhất theo mục đích**: En-dash (`–` `\u2013`) cho dải số/tham chiếu (`RQ1–RQ5`, `H1–H5`, `0,550–0,609`); Hyphen (`-` `\u002D`) cho từ ghép tiếng Anh cố định (`multi-view`, `fit-freeze`).
- **Hạn chế tối đa dấu gạch ngang**: Không dùng dấu gạch ngang để ngắt câu hoặc chèn giải thích giữa chừng.
- **Không lạm dụng ngoặc đơn thay thế**: Nối từ nối ý học thuật sáng tạo (*"tức"*, *"qua đó bảo đảm"*, *"đóng vai trò"*).
- **Bảo toàn tuyệt đối ngữ nghĩa học thuật**: Không làm sai lệch bản chất khoa học, không bịa đặt số liệu hay giả định.

### 5.9. Chuẩn hóa Chú thích Bảng biểu thành Trường động (`DYNAMIC_TABLE_CITATION_FIELDS`)
- **Nguyên tắc**: 100% chú thích trích dẫn trong bảng phải dùng cấu trúc trường Word dynamic CITATION (`w:fldSimple` hoặc `w:instrText CITATION ...`), không để chuỗi tĩnh `[k]`.
- **Hỗ trợ chuột phải**: Khi nhấp chuột phải vào số trích dẫn trong bảng, hiển thị đầy đủ tùy chọn *"Edit Citation"* / *"Edit Source"*, đồng bộ chuẩn xác với Bảng 2.3 và Bảng 3.5.

---

## 6. Giao thức Bản vá An toàn (Safe Patch Transaction Semantics)

Mỗi thay đổi văn phong bắt buộc phải tuân theo cấu trúc giao dịch máy đọc được:

```json
{
  "paragraph_idx": 547,
  "before_hash": "sha256...",
  "before_text": "1. Về mặt khảo sát và xác lập bài toán (Chương 1)...",
  "after_text": "Chương 1 xác lập phạm vi bài toán và phân tích các giới hạn của những nhóm phương pháp hiện hữu...",
  "finding_ids": ["REPEATED_STOCK_OPENER", "TEMPLATE_CLUSTERING"],
  "protected_class": "PLAIN_TEXT",
  "invariants_checked": {
    "omml_count": 0,
    "citations": [],
    "metrics_preserved": true
  }
}
```

Nếu `before_hash` không khớp chính xác với đoạn văn trong tài liệu tại thời điểm thực thi, hệ thống lập tức **DỪNG (ABORT)**, không cho phép áp dụng chắp vá mờ (fuzzy matching).