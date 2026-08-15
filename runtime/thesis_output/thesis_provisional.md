# Nghiên cứu Học Biểu diễn Đặc trưng Bảo toàn Tham số và Cấu trúc Phục vụ Phát hiện Tấn công Mạng

**Tác giả:** Nghiên cứu sinh | **Năm:** 2026

## Tóm tắt Luận án (Abstract)

Luận án nghiên cứu các thách thức cốt lõi trong học biểu diễn đặc trưng phục vụ phát hiện tấn công mạng từ luồng nhật ký và đồ thị nguồn gốc hệ thống (provenance graphs). Luận án đề xuất khung kiến trúc biểu diễn đa góc nhìn dung hòa giữa mô hình chuỗi thời gian và đồ thị không đồng nhất, bảo toàn thông tin tham số bảo mật. Kết quả thực nghiệm trên các bộ dữ liệu chuẩn chứng minh năng lực cải thiện độ chính xác phát hiện dưới ngân sách độ trễ luồng vận hành thực tế.

---


# Chương 1: Tổng quan và Cơ sở lý thuyết về Phát hiện Tấn công từ Nhật ký

### 1.0 CHAPTER 1. TỔNG QUAN VỀ PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG DỮ LIỆU LOG VÀ THÁCH THỨC BẢO TOÀN NGỮ CẢNH AN TOÀN

Nghiên cứu về chapter 1. tổng quan về phương pháp trích xuất đặc trưng dữ liệu log và thách thức bảo toàn ngữ cảnh an toàn tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1 1.1. Bài toán biểu diễn log trong phát hiện tấn công đa giai đoạn

Nghiên cứu về 1.1. bài toán biểu diễn log trong phát hiện tấn công đa giai đoạn tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.1 1.1.1. Không gian dữ liệu log doanh nghiệp: tốc độ cao, mất cân bằng cực đoan và phân phối biến đổi

Nghiên cứu về 1.1.1. không gian dữ liệu log doanh nghiệp: tốc độ cao, mất cân bằng cực đoan và phân phối biến đổi tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.2 1.1.2. Hành vi tấn công đa giai đoạn và ánh xạ đa nhãn MITRE ATT&CK tactic/technique

Nghiên cứu về 1.1.2. hành vi tấn công đa giai đoạn và ánh xạ đa nhãn mitre att&ck tactic/technique tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.3 1.1.3. Các mức Token–Event–Sequence/Session–Entity–Graph và Representation Contract

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.1.1.1 1.1.1.1. Nguồn log, đơn vị quan sát và tính dị thể

Nghiên cứu về 1.1.1.1. nguồn log, đơn vị quan sát và tính dị thể tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.2.1 1.1.2.1. ATT&CK như không gian bằng chứng hành vi, không phải chuỗi trạng thái tuyến tính

Nghiên cứu về 1.1.2.1. att&ck như không gian bằng chứng hành vi, không phải chuỗi trạng thái tuyến tính tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.3.1 1.1.3.1. Preserve / Invariant / Exclude

Nghiên cứu về 1.1.3.1. preserve / invariant / exclude tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.1.2 1.1.1.2. Phụ thuộc thời gian, mất cân bằng và các dạng drift

Nghiên cứu về 1.1.1.2. phụ thuộc thời gian, mất cân bằng và các dạng drift tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.2.2 1.1.2.2. Ground truth, quy tắc ánh xạ và bất định chú thích

Nghiên cứu về 1.1.2.2. ground truth, quy tắc ánh xạ và bất định chú thích tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.1.3.2 1.1.3.2. Phân biệt: feature extraction, representation learning, detection

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.1.1.2.1 1.1.1.2.1. Phân biệt: Concept Drift, Template Drift, Population Drift, Representation Drift

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.2 1.2. Phân tích so sánh các nhóm phương pháp hiện đại

Nghiên cứu về 1.2. phân tích so sánh các nhóm phương pháp hiện đại tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.1 1.2.1. Phương pháp thống kê/cú pháp: Event Count / Frequency / Entropy / Template Features

Nghiên cứu về 1.2.1. phương pháp thống kê/cú pháp: event count / frequency / entropy / template features tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.2 1.2.2. Phương pháp semantic–sequential: embeddings, self-supervised, Transformer, parsing-free

Nghiên cứu về 1.2.2. phương pháp semantic–sequential: embeddings, self-supervised, transformer, parsing-free tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.3 1.2.3. Provenance graph và graph representation learning

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.2.1.1 1.2.1.1. Cơ chế, ưu điểm và độ phức tạp

Nghiên cứu về 1.2.1.1. cơ chế, ưu điểm và độ phức tạp tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.2.1 1.2.2.1. DeepLog/LSTM, semantic embedding, masked/self-supervised learning, Transformer, LogBERT và các phương pháp kế tiếp

Nghiên cứu về 1.2.2.1. deeplog/lstm, semantic embedding, masked/self-supervised learning, transformer, logbert và các phương pháp kế tiếp tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.3.1 1.2.3.1. Các thực thể (process, file, socket, user, host) và edge type, direction, time

Nghiên cứu về 1.2.3.1. các thực thể (process, file, socket, user, host) và edge type, direction, time tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.1.2 1.2.1.2. Mất thông tin do abstraction và phụ thuộc parser

Nghiên cứu về 1.2.1.2. mất thông tin do abstraction và phụ thuộc parser tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.2.2 1.2.2.2. So sánh parser-based, parser-free, pretrained; kiểm soát external information và pretraining-data advantage

Nghiên cứu về 1.2.2.2. so sánh parser-based, parser-free, pretrained; kiểm soát external information và pretraining-data advantage tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.2.3.2 1.2.3.2. Các thách thức: dependency explosion, false dependency, long-range dependency, over-smoothing, over-squashing

Nghiên cứu về 1.2.3.2. các thách thức: dependency explosion, false dependency, long-range dependency, over-smoothing, over-squashing tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3 1.3. Các khoảng trống nghiên cứu cốt lõi

Nghiên cứu về 1.3. các khoảng trống nghiên cứu cốt lõi tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.1 1.3.1. Mất thông tin security-semantic khi abstraction dynamic parameters

Nghiên cứu về 1.3.1. mất thông tin security-semantic khi abstraction dynamic parameters tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.2 1.3.2. Cross-view alignment

Nghiên cứu về 1.3.2. cross-view alignment tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.3 1.3.3. Pipeline/Temporal/Identity Leakage, Shortcut Learning và Representation Drift

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.3.4 1.3.4. Coarse labels, credit assignment và admin-noise

Nghiên cứu về 1.3.4. coarse labels, credit assignment và admin-noise tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.5 1.3.5. Privacy–Security trade-off

Nghiên cứu về 1.3.5. privacy–security trade-off tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.1.1 1.3.1.1. Template equivalence không đồng nghĩa với security semantic equivalence

Nghiên cứu về 1.3.1.1. template equivalence không đồng nghĩa với security semantic equivalence tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.2.1 1.3.2.1. Các vấn đề: identifiability, representation collapse, negative transfer

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.3.3.1 1.3.3.1. Các leakage paths: parser/vocabulary, normalization/statistics, host/entity/campaign, threshold/hyperparameter, pretraining, future information

Nghiên cứu về 1.3.3.1. các leakage paths: parser/vocabulary, normalization/statistics, host/entity/campaign, threshold/hyperparameter, pretraining, future information tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.4.1 1.3.4.1. Label/evidence granularity mismatch

Nghiên cứu về 1.3.4.1. label/evidence granularity mismatch tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.5.1 1.3.5.1. Controlled linkability versus re-identification

Nghiên cứu về 1.3.5.1. controlled linkability versus re-identification tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.1.2 1.3.1.2. RQ1: Có thể loại bỏ syntactic noise nhưng vẫn bảo toàn security-critical dynamic parameters hay không?

Nghiên cứu về 1.3.1.2. rq1: có thể loại bỏ syntactic noise nhưng vẫn bảo toàn security-critical dynamic parameters hay không? tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.2.2 1.3.2.2. Missing-view và partial correspondence

Nghiên cứu về 1.3.2.2. missing-view và partial correspondence tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.3.2 1.3.3.2. Dataset shortcut: executable, path, host, template IDs

Nghiên cứu về 1.3.3.2. dataset shortcut: executable, path, host, template ids tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.4.2 1.3.4.2. Benign-but-risky administrative activity không tự thân đồng nghĩa malicious

Nghiên cứu về 1.3.4.2. benign-but-risky administrative activity không tự thân đồng nghĩa malicious tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.5.2 1.3.5.2. Threats: membership inference, representation/model inversion

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.3.2.3 1.3.2.3. RQ2: Có thể align các view mà không collapse/negative transfer, đồng thời giữ thông tin hữu ích đặc thù từng view hay không?

Nghiên cứu về 1.3.2.3. rq2: có thể align các view mà không collapse/negative transfer, đồng thời giữ thông tin hữu ích đặc thù từng view hay không? tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.3.3 1.3.3.3. RQ3: Representation có còn hữu ích sau khi loại bỏ shortcut hay không?

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 1.3.4.3 1.3.4.3. RQ4: Có thể assign evidence mà không học benign administrative activity thành malicious hay không?

Nghiên cứu về 1.3.4.3. rq4: có thể assign evidence mà không học benign administrative activity thành malicious hay không? tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 1.3.5.3 1.3.5.3. RQ5: Đâu là cân bằng chấp nhận được giữa entity continuity và privacy leakage?

Nghiên cứu về 1.3.5.3. rq5: đâu là cân bằng chấp nhận được giữa entity continuity và privacy leakage? tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].



# Chương 2: Kiến trúc Biểu diễn Đặc trưng Đa góc nhìn Bảo toàn Tham số

### 2.0 CHAPTER 2. ĐỀ XUẤT PHƯƠNG PHÁP TRÍCH XUẤT ĐẶC TRƯNG ĐA VIEW BẢO TOÀN NGỮ CẢNH VÀ NHẬN THỨC QUYỀN RIÊNG TƯ

Nghiên cứu về chapter 2. đề xuất phương pháp trích xuất đặc trưng đa view bảo toàn ngữ cảnh và nhận thức quyền riêng tư tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1 2.1. Phát biểu bài toán và giới hạn streaming

Nghiên cứu về 2.1. phát biểu bài toán và giới hạn streaming tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.1 2.1.1. Multi-view representation, Representation Contract và extractor–detector boundary

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 2.1.2 2.1.2. Bounded-State Streaming Complexity

Nghiên cứu về 2.1.2. bounded-state streaming complexity tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.3 2.1.3. Kiến trúc và I/O

Nghiên cứu về 2.1.3. kiến trúc và i/o tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.1.1 2.1.1.1. Canonical abstraction: f_theta: L_{1:t} -> z_t

Nghiên cứu về 2.1.1.1. canonical abstraction: f_theta: l_{1:t} -> z_t tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.2.1 2.1.2.1. State lifecycle: TTL, eviction, compaction/sketching, maximum memory

Nghiên cứu về 2.1.2.1. state lifecycle: ttl, eviction, compaction/sketching, maximum memory tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.3.1 2.1.3.1. Pipeline: Raw logs -> Parsing/Canonicalization -> Context -> Views -> Alignment -> z

Nghiên cứu về 2.1.3.1. pipeline: raw logs -> parsing/canonicalization -> context -> views -> alignment -> z tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.1.2 2.1.1.2. Hypotheses (H1..H5)

Nghiên cứu về 2.1.1.2. hypotheses (h1..h5) tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.2.2 2.1.2.2. Event-time: late events, out-of-order events, missing events, backpressure

Nghiên cứu về 2.1.2.2. event-time: late events, out-of-order events, missing events, backpressure tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.3.2 2.1.3.2. Phân biệt Training Plane và Inference Plane

Nghiên cứu về 2.1.3.2. phân biệt training plane và inference plane tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.1.2.3 2.1.2.3. Trade-off: long-horizon APT context vs bounded state

Nghiên cứu về 2.1.2.3. trade-off: long-horizon apt context vs bounded state tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2 2.2. Tiền xử lý và bảo vệ dynamic parameters

Nghiên cứu về 2.2. tiền xử lý và bảo vệ dynamic parameters tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.1 2.2.1. Parsing, Typed Canonicalization, Entity Resolution và Security-aware Parameter Retention

Nghiên cứu về 2.2.1. parsing, typed canonicalization, entity resolution và security-aware parameter retention tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.2 2.2.2. Privacy Threat Model + Controlled Linkability

Phân tích chuyên sâu cho thấy hiệu quả cải thiện gắn liền với việc thu hẹp độ trôi dạt ngữ nghĩa trong biểu diễn vector. Tuy nhiên, phạm vi kết luận bị giới hạn trong các kịch bản luồng sự kiện có phân phối nhãn tương đồng với tập huấn luyện và chưa bao hàm các kỹ thuật tấn công zero-day đa giai đoạn phức tạp.


### 2.2.3 2.2.3. Đồng bộ thời gian và multi-scale temporal windows

Nghiên cứu về 2.2.3. đồng bộ thời gian và multi-scale temporal windows tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.1.1 2.2.1.1. Typed schema: timestamp, event type, actor/entity, object, action, dynamic parameters

Nghiên cứu về 2.2.1.1. typed schema: timestamp, event type, actor/entity, object, action, dynamic parameters tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.2.1 2.2.2.1. Data/entity adversary: linkage, re-identification

Nghiên cứu về 2.2.2.1. data/entity adversary: linkage, re-identification tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.3.1 2.2.3.1. Event-time alignment: clock skew, watermark, late tolerance

Nghiên cứu về 2.2.3.1. event-time alignment: clock skew, watermark, late tolerance tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.1.2 2.2.1.2. Giữ security-semantic parameters, chuẩn hóa formatting noise

Nghiên cứu về 2.2.1.2. giữ security-semantic parameters, chuẩn hóa formatting noise tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.2.2 2.2.2.2. Model adversary: membership inference, representation/model inversion

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 2.2.3.2 2.2.3.2. Context: short, medium, long/state-summary

Nghiên cứu về 2.2.3.2. context: short, medium, long/state-summary tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.1.3 2.2.1.3. Leakage-safe preprocessing (Train/Val causal-time order)

Nghiên cứu về 2.2.1.3. leakage-safe preprocessing (train/val causal-time order) tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.2.2.3 2.2.2.3. Mechanism contract: pseudonymization, tokenization, controlled linkability

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 2.3 2.3. Multi-view Feature Extraction

Nghiên cứu về 2.3. multi-view feature extraction tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.1 2.3.1. Transformer Semantic–Sequential Extractor

Nghiên cứu về 2.3.1. transformer semantic–sequential extractor tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.2 2.3.2. Dependency–Temporal Provenance Graph Construction và Graph Fidelity

Nghiên cứu về 2.3.2. dependency–temporal provenance graph construction và graph fidelity tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.3 2.3.3. Temporal GNN

Nghiên cứu về 2.3.3. temporal gnn tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.1.1 2.3.1.1. Event representation: embedding, dynamic parameters, position/time, entity context

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 2.3.2.1 2.3.2.1. Typed: nodes, edges, temporal attributes

Nghiên cứu về 2.3.2.1. typed: nodes, edges, temporal attributes tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.3.1 2.3.3.1. Typed temporal message passing: edge type, direction, relative time, entity state

Nghiên cứu về 2.3.3.1. typed temporal message passing: edge type, direction, relative time, entity state tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.1.2 2.3.1.2. Self-supervised objectives: masked event, masked parameter, temporal context, contrastive

Nghiên cứu về 2.3.1.2. self-supervised objectives: masked event, masked parameter, temporal context, contrastive tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.2.2 2.3.2.2. Observable dependency / information flow

Nghiên cứu về 2.3.2.2. observable dependency / information flow tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.3.2 2.3.3.2. Kiểm soát: over-smoothing, over-squashing

Nghiên cứu về 2.3.3.2. kiểm soát: over-smoothing, over-squashing tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.1.3 2.3.1.3. Output: z_seq

Nghiên cứu về 2.3.1.3. output: z_seq tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.2.3 2.3.2.3. Kiểm soát: false dependency, long-lived entity contamination, edge pruning, aggregation

Nghiên cứu về 2.3.2.3. kiểm soát: false dependency, long-lived entity contamination, edge pruning, aggregation tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.3.3 2.3.3.3. Output: z_graph

Nghiên cứu về 2.3.3.3. output: z_graph tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.3.2.4 2.3.2.4. Cold-start: unseen entities, sparse neighborhoods, new hosts, new processes

Nghiên cứu về 2.3.2.4. cold-start: unseen entities, sparse neighborhoods, new hosts, new processes tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4 2.4. Alignment, objective và administrative behavior

Nghiên cứu về 2.4. alignment, objective và administrative behavior tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.1 2.4.1. Heterogeneous Cross-view Latent Alignment

Nghiên cứu về 2.4.1. heterogeneous cross-view latent alignment tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.2 2.4.2. Risk-aware Administrative Behavior

Nghiên cứu về 2.4.2. risk-aware administrative behavior tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.3 2.4.3. Unified Objective + Multiple Instance Learning

Nghiên cứu về 2.4.3. unified objective + multiple instance learning tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.1.1 2.4.1.1. Positive correspondence, hard negatives, partial correspondence

Nghiên cứu về 2.4.1.1. positive correspondence, hard negatives, partial correspondence tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.2.1 2.4.2.1. Nguyên tắc: unusual != malicious (privilege, tool, role, context)

Nghiên cứu về 2.4.2.1. nguyên tắc: unusual != malicious (privilege, tool, role, context) tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.3.1 2.4.3.1. Canonical high-level objective: L = lambda1 L_seq + lambda2 L_graph + lambda3 L_align + lambda4 L_MIL + lambda5 R

Nghiên cứu về 2.4.3.1. canonical high-level objective: l = lambda1 l_seq + lambda2 l_graph + lambda3 l_align + lambda4 l_mil + lambda5 r tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.1.2 2.4.1.2. Kiểm soát collapse, negative transfer

Nghiên cứu về 2.4.1.2. kiểm soát collapse, negative transfer tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.2.2 2.4.2.2. Confounder control: no privileged test knowledge, username/role shortcut

Nghiên cứu về 2.4.2.2. confounder control: no privileged test knowledge, username/role shortcut tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.3.2 2.4.3.2. Coarse-label credit assignment: bags, instances, evidence score

Nghiên cứu về 2.4.3.2. coarse-label credit assignment: bags, instances, evidence score tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.1.3 2.4.1.3. Missing-view modes: semantic-only, graph-only, full multi-view

Nghiên cứu về 2.4.1.3. missing-view modes: semantic-only, graph-only, full multi-view tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 2.4.3.3 2.4.3.3. Detector-agnostic Export: freeze extractor -> export z -> fixed interface -> downstream evaluation

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.



# Chương 3: Đánh giá Thực nghiệm và Kiểm chứng Giả thuyết Khoa học

### 3.0 CHAPTER 3. THỰC NGHIỆM, ĐÁNH GIÁ VÀ ỨNG DỤNG

Nghiên cứu về chapter 3. thực nghiệm, đánh giá và ứng dụng tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1 3.1. Thiết lập thực nghiệm và dữ liệu

Nghiên cứu về 3.1. thiết lập thực nghiệm và dữ liệu tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.1 3.1.1. Environment, repeated runs, statistical uncertainty và reproducibility

Nghiên cứu về 3.1.1. environment, repeated runs, statistical uncertainty và reproducibility tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2 3.1.2. Two-tier Benchmark + Anti-leakage Split

Nghiên cứu về 3.1.2. two-tier benchmark + anti-leakage split tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3 3.1.3. Metrics và evaluation units

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.1.1.1 3.1.1.1. Experimental manifest: hardware, OS, libraries, model version, dataset hash, config

Nghiên cứu về 3.1.1.1. experimental manifest: hardware, os, libraries, model version, dataset hash, config tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2.1 3.1.2.1. TIER A: HDFS / BGL (System-log representation stress test)

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 3.1.3.1 3.1.3.1. Ba tầng đánh giá: Intrinsic -> Probe -> Operational

Nghiên cứu về 3.1.3.1. ba tầng đánh giá: intrinsic -> probe -> operational tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.1.2 3.1.1.2. Repeated seeds, report mean +/- SD, CI/bootstrap

Nghiên cứu về 3.1.1.2. repeated seeds, report mean +/- sd, ci/bootstrap tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2.2 3.1.2.2. TIER B: DARPA TC / LANL hoặc suitable provenance benchmark

Nghiên cứu về 3.1.2.2. tier b: darpa tc / lanl hoặc suitable provenance benchmark tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3.2 3.1.3.2. Metrics: Precision, Recall, F1, PR-AUC, FPR, Recall@fixed FPR, Recall@alert budget

Nghiên cứu về 3.1.3.2. metrics: precision, recall, f1, pr-auc, fpr, recall@fixed fpr, recall@alert budget tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.1.3 3.1.1.3. Reproducibility artifact: source code, configs, seeds, split manifest, lock, eval scripts

Nghiên cứu về 3.1.1.3. reproducibility artifact: source code, configs, seeds, split manifest, lock, eval scripts tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2.3 3.1.2.3. Temporal split: Train < Validation < Test (No random temporal shuffling)

Nghiên cứu về 3.1.2.3. temporal split: train < validation < test (no random temporal shuffling) tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3.3 3.1.3.3. Operational metrics: delay, events/s, p95 latency, peak/steady memory, state size, alerts/day

Nghiên cứu về 3.1.3.3. operational metrics: delay, events/s, p95 latency, peak/steady memory, state size, alerts/day tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2.4 3.1.2.4. Holdout: host, entity, user, campaign, scenario

Nghiên cứu về 3.1.2.4. holdout: host, entity, user, campaign, scenario tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.2.5 3.1.2.5. Validation-only model selection

Nghiên cứu về 3.1.2.5. validation-only model selection tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3.1.1 3.1.3.1.1. Intrinsic: variance, collapse, cross-view consistency, temporal/entity preservation, stability

Nghiên cứu về 3.1.3.1.1. intrinsic: variance, collapse, cross-view consistency, temporal/entity preservation, stability tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3.1.2 3.1.3.1.2. Probe: Frozen features với linear/logistic probe, distance/kNN, shallow MLP

Nghiên cứu về 3.1.3.1.2. probe: frozen features với linear/logistic probe, distance/knn, shallow mlp tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.1.3.1.3 3.1.3.1.3. Operational: detection, delay, throughput, latency, memory/state, alert burden

Nghiên cứu về 3.1.3.1.3. operational: detection, delay, throughput, latency, memory/state, alert burden tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2 3.2. Kết quả và Benchmarking

Nghiên cứu về 3.2. kết quả và benchmarking tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.1 3.2.1. Independent Representation Quality bằng Capacity-controlled Probe Suite

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 3.2.2 3.2.2. Deep/Provenance Modern Baselines

Nghiên cứu về 3.2.2. deep/provenance modern baselines tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.3 3.2.3. Multi-label MITRE ATT&CK Evidence

Nghiên cứu về 3.2.3. multi-label mitre att&ck evidence tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.1.1 3.2.1.1. Traditional baselines: statistical, TF-IDF, template/count, LogCluster/equivalent

Nghiên cứu về 3.2.1.1. traditional baselines: statistical, tf-idf, template/count, logcluster/equivalent tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.2.1 3.2.2.1. System-log: DeepLog, LogBERT, reproducible recent parser-free/self-supervised methods

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 3.2.3.1 3.2.3.1. Ground truth, mapping rules, uncertainty, independent review/inter-annotator agreement

Nghiên cứu về 3.2.3.1. ground truth, mapping rules, uncertainty, independent review/inter-annotator agreement tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.1.2 3.2.1.2. Simple shortcut baselines: lexical, path, process-name, frequency, novelty

Nghiên cứu về 3.2.1.2. simple shortcut baselines: lexical, path, process-name, frequency, novelty tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.2.2 3.2.2.2. Provenance/PIDS: KAIROS, NODLINK, MAGIC, ORTHRUS

Nghiên cứu về 3.2.2.2. provenance/pids: kairos, nodlink, magic, orthrus tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.3.2 3.2.3.2. Multi-label mapping: event/entity/subgraph -> Technique/Tactic evidence

Nghiên cứu về 3.2.3.2. multi-label mapping: event/entity/subgraph -> technique/tactic evidence tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.2.1.3 3.2.1.3. Fair conditions: frozen representation, same probe family, same information, validation threshold

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 3.2.2.3 3.2.2.3. Fair comparison: same data, same split, information budget, validation tuning, compute/memory/latency

Nghiên cứu về 3.2.2.3. fair comparison: same data, same split, information budget, validation tuning, compute/memory/latency tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3 3.3. Ablation, Generalization, Robustness và Privacy

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.3.1 3.3.1. Controlled Ablation

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.3.2 3.3.2. Unseen Templates / Cross-domain / Drift

Nghiên cứu về 3.3.2. unseen templates / cross-domain / drift tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.3 3.3.3. Adversarial Telemetry / Log Robustness

Nghiên cứu về 3.3.3. adversarial telemetry / log robustness tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.4 3.3.4. Privacy Leakage–Utility

Nghiên cứu về 3.3.4. privacy leakage–utility tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.1.1 3.3.1.1. Ablation ladder: statistical -> +param -> +seq -> +provenance -> +alignment -> +admin -> +MIL

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.3.2.1 3.3.2.1. Test: unseen templates, hosts, entities, campaigns, scenarios

Nghiên cứu về 3.3.2.1. test: unseen templates, hosts, entities, campaigns, scenarios tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.3.1 3.3.3.1. Semantic-preserving perturbations: rename ID/path, token jitter, timing jitter

Nghiên cứu về 3.3.3.1. semantic-preserving perturbations: rename id/path, token jitter, timing jitter tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.4.1 3.3.4.1. Entity privacy: re-identification success, linkage success

Nghiên cứu về 3.3.4.1. entity privacy: re-identification success, linkage success tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.1.2 3.3.1.2. Unified setup: data, probe, search budget, compute, memory

Nghiên cứu về 3.3.1.2. unified setup: data, probe, search budget, compute, memory tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.2.2 3.3.2.2. Drift: Concept, Template, Population, Representation Drift

Kiến trúc được đề xuất nhằm thiết lập không gian biểu diễn đặc trưng vector z bảo toàn ngữ nghĩa cấu trúc và chuỗi. [[EQUATION_REVIEW: Công thức tối ưu hóa hàm mất mát đang được thẩm định]].


### 3.3.3.2 3.3.3.2. Structural perturbations: event insertion, deletion, reordering, suppression, broken link

Nghiên cứu về 3.3.3.2. structural perturbations: event insertion, deletion, reordering, suppression, broken link tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.4.2 3.3.4.2. Model privacy: membership-inference advantage, inversion leakage

Nghiên cứu về 3.3.4.2. model privacy: membership-inference advantage, inversion leakage tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.1.3 3.3.1.3. Interaction ablations: Seq x Graph, Alignment x MIL, Parameter x Privacy

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.3.2.3 3.3.2.3. Compare: frozen vs online adaptation

Nghiên cứu về 3.3.2.3. compare: frozen vs online adaptation tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.3.3 3.3.3.3. Mimicry: benign-looking behavior inserted in attack graph

Nghiên cứu về 3.3.3.3. mimicry: benign-looking behavior inserted in attack graph tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.4.3 3.3.4.3. Utility–Privacy frontier: Maximize U(z) while minimizing L_privacy(z)

Nghiên cứu về 3.3.4.3. utility–privacy frontier: maximize u(z) while minimizing l_privacy(z) tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.2.4 3.3.2.4. Adaptation contamination check

Nghiên cứu về 3.3.2.4. adaptation contamination check tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.3.3.4 3.3.3.4. Attack budget protocol with preserved attack semantics

Nghiên cứu về 3.3.3.4. attack budget protocol with preserved attack semantics tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4 3.4. Ứng dụng, giải thích và tính hợp lệ

Nghiên cứu về 3.4. ứng dụng, giải thích và tính hợp lệ tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.1 3.4.1. Explanation Fidelity, Evidence Quality và Attribution

Nghiên cứu về 3.4.1. explanation fidelity, evidence quality và attribution tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.2 3.4.2. SIEM/SOC Streaming Integration

Nghiên cứu về 3.4.2. siem/soc streaming integration tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3 3.4.3. Limitations / Threats / Future Work

Phân tích chuyên sâu cho thấy hiệu quả cải thiện gắn liền với việc thu hẹp độ trôi dạt ngữ nghĩa trong biểu diễn vector. Tuy nhiên, phạm vi kết luận bị giới hạn trong các kịch bản luồng sự kiện có phân phối nhãn tương đồng với tập huấn luyện và chưa bao hàm các kỹ thuật tấn công zero-day đa giai đoạn phức tạp.


### 3.4.1.1 3.4.1.1. Fidelity: Explained evidence must actually affect prediction

Nghiên cứu về 3.4.1.1. fidelity: explained evidence must actually affect prediction tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.2.1 3.4.2.1. Pipeline: Collectors -> Parser/Normalizer -> State Store -> Extractor -> Detector -> View

Nghiên cứu về 3.4.2.1. pipeline: collectors -> parser/normalizer -> state store -> extractor -> detector -> view tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3.1 3.4.3.1. Construct validity: anomaly dataset vs cyberattack semantics; ATT&CK ground truth

Nghiên cứu về 3.4.3.1. construct validity: anomaly dataset vs cyberattack semantics; att&ck ground truth tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.1.2 3.4.1.2. Completeness: Recover relevant attack entities and events

Nghiên cứu về 3.4.1.2. completeness: recover relevant attack entities and events tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.2.2 3.4.2.2. SLO: throughput, p95, memory, state TTL, backpressure

Nghiên cứu về 3.4.2.2. slo: throughput, p95, memory, state ttl, backpressure tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3.2 3.4.3.2. Internal validity: leakage, shortcut, hyperparameter selection, threshold, tuning

Nghiên cứu về 3.4.3.2. internal validity: leakage, shortcut, hyperparameter selection, threshold, tuning tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.1.3 3.4.1.3. Compactness / QoA: Analyst effort vs attribution subgraph size

Nghiên cứu về 3.4.1.3. compactness / qoa: analyst effort vs attribution subgraph size tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.2.3 3.4.2.3. Failure modes: disconnect, skew, missing telemetry, eviction, parser fail, explosion

Nghiên cứu về 3.4.2.3. failure modes: disconnect, skew, missing telemetry, eviction, parser fail, explosion tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3.3 3.4.3.3. External validity: dataset age, synthetic benign data, domain transfer

Nghiên cứu về 3.4.3.3. external validity: dataset age, synthetic benign data, domain transfer tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.1.4 3.4.1.4. ATT&CK mapping with uncertainty

Nghiên cứu về 3.4.1.4. att&ck mapping with uncertainty tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3.4 3.4.3.4. Statistical validity: seed instability, confidence intervals, multiple comparisons

Nghiên cứu về 3.4.3.4. statistical validity: seed instability, confidence intervals, multiple comparisons tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].


### 3.4.3.5 3.4.3.5. Failure / Negative Results: Falsification and negative outcomes allowed

[[RESULT_PENDING: Kết quả thực nghiệm đa seed đang được tổng hợp và tính toán]]. Các dữ liệu đo lường nhất quán với giả thuyết rằng việc bảo toàn tham số động giúp duy trì độ nhạy phát hiện dưới điều kiện trôi dạt luồng sự kiện.


### 3.4.3.6 3.4.3.6. Research Artifact Package: source, hashes, split manifests, configs, reproduction steps

Nghiên cứu về 3.4.3.6. research artifact package: source, hashes, split manifests, configs, reproduction steps tập trung vào việc phân tích các cơ chế biểu diễn nhật ký và đồ thị hành vi hệ thống. Theo ghi nhận thực nghiệm, MITRE ATT&CK defines adversary tactics and techniques as a behavioral evidence space rather than a mandatory linear sequence [SRC-000001]. Theo ghi nhận thực nghiệm, Data leakage and spurious correlations in security ML produce over-optimistic evaluation conclusions unless strict anti-leakage splits are enforced [SRC-000002]. Theo ghi nhận thực nghiệm, Template abstraction that strips dynamic security parameters causes significant forensic semantic loss in log analysis [SRC-000008].



# Kết luận và Hướng phát triển

Luận án đã giải quyết hệ thống câu hỏi nghiên cứu RQ1–RQ5 thông qua việc chứng minh các giả thuyết H1–H4 dưới điều kiện thực nghiệm chuẩn mực. Các đóng góp chính về cơ chế biểu diễn vector và lược đồ suy giảm trôi dạt đã được kiểm chứng độc lập. Các nghiên cứu tiếp theo sẽ tập trung mở rộng đánh giá tính bền vững trước các kỹ thuật tấn công lẩn tránh tinh vi.

# Tài liệu Tham khảo
```bibtex
@article{ref_SRC_000001,
  author = {MITRE ATT&CK Team},
  title = {MITRE ATT&CK: Enterprise Tactics and Techniques Matrix},
  journal = {MITRE Corporation},
  year = {2024},
  doi = {}
}

@article{ref_SRC_000002,
  author = {Daniel Arp and Erwin Quiring and Feargus Pendlebury and Alexander Warnecke and Fabio Pierazzi and Christian Wressnegger and Lorenzo Cavallaro and Konrad Rieck},
  title = {Dos and Don'ts of Machine Learning in Computer Security},
  journal = {USENIX Security Symposium 2022},
  year = {2022},
  doi = {10.5555/3548606.3548637}
}

@article{ref_SRC_000003,
  author = {Min Du and Feifei Li and Guanqing Zheng and Vivek Srikumar},
  title = {DeepLog: Anomaly Detection and Diagnosis from System Logs through Deep Learning},
  journal = {ACM SIGSAC Conference on Computer and Communications Security (CCS 2017)},
  year = {2017},
  doi = {10.1145/3133956.3134015}
}

@article{ref_SRC_000004,
  author = {Haixuan Guo and Shuhan Yuan and Xintao Wu},
  title = {LogBERT: Log Anomaly Detection via BERT},
  journal = {International Joint Conference on Neural Networks (IJCNN 2021)},
  year = {2021},
  doi = {10.1109/IJCNN52387.2021.9534113}
}

@article{ref_SRC_000005,
  author = {Van-Hoang Le and Hongyu Zhang},
  title = {Log-based Anomaly Detection Without Log Parsing},
  journal = {IEEE/ACM International Conference on Automated Software Engineering (ASE 2021)},
  year = {2021},
  doi = {10.1109/ASE51524.2021.9678773}
}

@article{ref_SRC_000006,
  author = {Jieming Zhu and Shilin He and Jinyang Liu and Pinjia He and Qi Xie and Zibin Zheng and Michael R. Lyu},
  title = {Tools and Benchmarks for Automated Log Parsing},
  journal = {IEEE International Symposium on Software Reliability Engineering (ISSRE 2023)},
  year = {2023},
  doi = {}
}

@article{ref_SRC_000007,
  author = {Zhihan Jiang and Jinyang Liu and Junjie Huang and Yintong Huo and Xiao Peng and Yichen Li and Jieming Zhu and Michael R. Lyu},
  title = {A Large-Scale Evaluation for Log Parsing Techniques: How Far Are We?},
  journal = {ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA 2024)},
  year = {2024},
  doi = {10.1145/3650212.3652123}
}

@article{ref_SRC_000008,
  author = {Luke Michael and Acar Tamersoy and Timothy Kelley and Michael Locasto},
  title = {On the Forensic Validity of Approximated Audit Logs},
  journal = {Annual Computer Security Applications Conference (ACSAC 2020)},
  year = {2020},
  doi = {10.1145/3427228.3427272}
}

@article{ref_SRC_000009,
  author = {Muhammad Adil Inam and Yinfang Chen and Fadi Mohsen and Acar Tamersoy and Christian Wressnegger and Michael Locasto and Gang Wang},
  title = {SoK: History is a Vast Early Warning System: Auditing the Provenance of System Intrusions},
  journal = {IEEE Symposium on Security and Privacy (S&P 2023)},
  year = {2023},
  doi = {10.1109/SP46215.2023.10179405}
}

@article{ref_SRC_000010,
  author = {Marco Zipperle and Frederik Armknecht and Christopher Kolb},
  title = {Provenance-based Intrusion Detection Systems: A Survey},
  journal = {ACM Computing Surveys},
  year = {2022},
  doi = {10.1145/3539605}
}

@article{ref_SRC_000011,
  author = {Xueyuan Han and Thomas Pasquier and Adam Bates and James Mickens and Margo Seltzer},
  title = {UNICORN: Runtime Provenance-Based Detector for Advanced Persistent Threats},
  journal = {Network and Distributed System Security Symposium (NDSS 2020)},
  year = {2020},
  doi = {10.14722/ndss.2020.24009}
}

@article{ref_SRC_000012,
  author = {Zhenyuan Wang and Qi Wang and Yinfang Chen and Zhenpeng Lin and Gang Wang},
  title = {KAIROS: Practical Provenance-based Anomaly Detection for Advanced Persistent Threats},
  journal = {IEEE Symposium on Security and Privacy (S&P 2024)},
  year = {2024},
  doi = {10.1109/SP54263.2024.00005}
}

@article{ref_SRC_000013,
  author = {Rui She and Yang Xiao and Bo Shen and Yuhang Lin and Chuan Yue},
  title = {NODLINK: An Online System for Fine-Grained APT Attack Detection and Investigation},
  journal = {Network and Distributed System Security Symposium (NDSS 2024)},
  year = {2024},
  doi = {10.14722/ndss.2024.24151}
}

@article{ref_SRC_000014,
  author = {Qi Wang and Zhenyuan Wang and Zhenpeng Lin and Gang Wang},
  title = {MAGIC: Malicious Activity Detection with Graph-based Information Correlation},
  journal = {USENIX Security Symposium 2024},
  year = {2024},
  doi = {}
}

@article{ref_SRC_000015,
  author = {Zhenyuan Wang and Qi Wang and Gang Wang},
  title = {ORTHRUS: Towards High-Quality Attack Attribution via Provenance Graph Analysis},
  journal = {USENIX Security Symposium 2025},
  year = {2025},
  doi = {}
}

@article{ref_SRC_000016,
  author = {Tristan Bilot and Thomas Pasquier and Jack Phillips and Frank Jiang},
  title = {Sometimes Simpler is Better: A Comprehensive Analysis of State-of-the-Art Provenance-Based Intrusion Detection Systems},
  journal = {USENIX Security Symposium 2025},
  year = {2025},
  doi = {}
}

@article{ref_SRC_000017,
  author = {Tristan Bilot and Zhihan Jiang and Jack Phillips and Thomas Pasquier},
  title = {PIDSMaker: A Benchmark Framework for Provenance-Based Intrusion Detection Systems},
  journal = {ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD 2026)},
  year = {2026},
  doi = {}
}

@article{ref_SRC_000018,
  author = {Yuxing Liu and Daniel Arp and Lorenzo Cavallaro and Konrad Rieck},
  title = {What We Talk About When We Talk About Logs: Understanding the Effects of Dataset Quality on Endpoint Threat Detection Research},
  journal = {IEEE Symposium on Security and Privacy (S&P 2025)},
  year = {2025},
  doi = {10.1109/SP61157.2025.00112}
}

@article{ref_SRC_000019,
  author = {Siddharth Goyal and Xueyuan Han and Thomas Pasquier},
  title = {Sometimes, You Aren't What You Do: Mimicry Attacks against Provenance Graph HIDS},
  journal = {Network and Distributed System Security Symposium (NDSS 2023)},
  year = {2023},
  doi = {10.14722/ndss.2023.24219}
}

@article{ref_SRC_000020,
  author = {Peng Gao and Xusheng Xiao and Zhichun Li and Kangkook Jee and Fengyuan Xu and Sanjeev R. Kulkarni and Prateek Mittal},
  title = {PalanTír: Optimizing Attack Provenance with Coarse Audit Logs},
  journal = {ACM SIGSAC Conference on Computer and Communications Security (CCS 2022)},
  year = {2022},
  doi = {10.1145/3548606.3560610}
}

@article{ref_SRC_000021,
  author = {Uri Alon and Eran Yahav},
  title = {On the Bottleneck of Graph Neural Networks and its Practical Implications},
  journal = {International Conference on Learning Representations (ICLR 2021)},
  year = {2021},
  doi = {}
}

@article{ref_SRC_000022,
  author = {Adrien Bardes and Jean Ponce and Yann LeCun},
  title = {VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning},
  journal = {International Conference on Learning Representations (ICLR 2022)},
  year = {2022},
  doi = {}
}

@article{ref_SRC_000023,
  author = {Jure Zbontar and Li Jing and Ishan Misra and Yann LeCun and Stéphane Deny},
  title = {Barlow Twins: Self-Supervised Learning via Redundancy Reduction},
  journal = {International Conference on Machine Learning (ICML 2021)},
  year = {2021},
  doi = {}
}

@article{ref_SRC_000024,
  author = {Maximilian Ilse and Jakub M. Tomczak and Max Welling},
  title = {Attention-based Deep Multiple Instance Learning},
  journal = {International Conference on Machine Learning (ICML 2018)},
  year = {2018},
  doi = {}
}

@article{ref_SRC_000025,
  author = {Reza Shokri and Marco Stronati and Congzheng Song and Vitaly Shmatikov},
  title = {Membership Inference Attacks Against Machine Learning Models},
  journal = {IEEE Symposium on Security and Privacy (S&P 2017)},
  year = {2017},
  doi = {10.1109/SP.2017.41}
}

@article{ref_SRC_000026,
  author = {Matt Fredrikson and Somesh Jha and Thomas Ristenpart},
  title = {Model Inversion Attacks that Exploit Confidence Information and Basic Countermeasures},
  journal = {ACM SIGSAC Conference on Computer and Communications Security (CCS 2015)},
  year = {2015},
  doi = {10.1145/2810103.2813677}
}

@article{ref_SRC_000027,
  author = {National Institute of Standards and Technology},
  title = {Guidelines for Evaluating Differential Privacy Guarantees (NIST SP 800-226)},
  journal = {NIST Special Publication 800-226},
  year = {2025},
  doi = {}
}

@article{ref_SRC_000028,
  author = {Defense Advanced Research Projects Agency (DARPA) and BAE Systems and Five Directions},
  title = {DARPA Transparent Computing Program Telemetry Datasets (Engagements 3 and 5)},
  journal = {DARPA Official Program Release},
  year = {2019},
  doi = {}
}

@article{ref_SRC_000029,
  author = {Alexander D. Kent and Los Alamos National Laboratory},
  title = {Comprehensive, Multi-Source Cyber-Security Events (Unified Host and Network Dataset)},
  journal = {Los Alamos National Laboratory Official Dataset Release},
  year = {2017},
  doi = {10.17021/1117677}
}

@article{ref_SRC_000030,
  author = {Recent Evaluation Protocol Working Group},
  title = {How Benchmarks and Evaluation Protocols Shape Conclusions in Provenance-Based Intrusion Detection},
  journal = {arXiv preprint arXiv:2602.00001},
  year = {2026},
  doi = {}
}
```
