# KẾ HOẠCH TINH GỌN VÀ CHUẨN HÓA KHO LƯU TRỮ DÀNH CHO PHẢN BIỆN
**Tài liệu:** `SIMPLE-REVIEW-REPO-PLAN.md`  
**Dự án:** Chuyên đề chuyên sâu của Sinh viên  
**Kho lưu trữ:** `Minhlike/Chuyende` | **Nhánh:** `fix/thesis-apply-edits`  
**Mục tiêu:** Tinh giản cấu trúc kho mã nguồn, loại bỏ thủ tục hành chính phức tạp, xây dựng tài liệu hướng dẫn trực quan, thiết thực cho giảng viên phản biện và lộ trình thực nghiệm độc lập cho sinh viên.

---

## 1. PHÂN TÍCH CÁC VẤN ĐỀ TỒN ĐỌNG VÀ RÀO CẢN KỸ THUẬT (BLOCKERS)

### 1.1. Các tồn đọng cốt lõi của repository hiện tại

1. **Sai lệch định danh học thuật và quá tải thuật ngữ hành chính:**
   - Tệp `README.md` hiện tại viết bằng tiếng Anh và tuyên bố sai lệch học vị: *"PhD-level research study..."*, trong khi đây là chuyên đề chuyên sâu của sinh viên.
   - Trạng thái nghiên cứu trong `README.md` đã lỗi thời: Chương 3 vẫn ghi *"PRE-REGISTRATION LOCKED / All experiments in PLANNED state"*, trong khi toàn bộ thực nghiệm Nineplus V3 đã hoàn tất và được tích hợp vào văn bản Master DOCX/PDF.
   - Sử dụng quá nhiều thuật ngữ hàn lâm mang phong cách quản trị doanh nghiệp nặng nề: *"Research Constitution", "Invariants", "RC-01 - RC-18", "Hard firewall", "Authority", "Evidence matrix", "Contract"*. Cần chuyển đổi về ngôn ngữ kỹ thuật chuẩn mực, dễ hiểu của một báo cáo chuyên đề sinh viên.

2. **Tình trạng phân mảnh và quá tải tệp tin tại thư mục gốc (Root Clutter):**
   - Thư mục gốc `D:\Research` có hơn 120 tệp tin, bao gồm hàng chục script phụ trợ dùng một lần (`test_omml.py`, `test_word_com.py`, `test_canvas_order.py`, `patch_section_2_3_and_2_4.py`, `add_chapter1_sources.py`), các tệp tạm (`.tmp`, `~$uyên đề...`), các bản sao lưu DOCX (`Chuyên đề chuyên sâu.pre_sweep_backup.docx`, `clean_tgn_buildup.docx`).
   - Người phản biện khi truy cập thư mục gốc rất khó phân biệt đâu là mã nguồn cốt lõi, đâu là script thực thi chính thức và đâu là dữ liệu kết quả.

3. **Thiếu vắng tài liệu dẫn đường thực hành trực tiếp (Reviewer Onboarding Barrier):**
   - Chưa có tệp `HUONG_DAN_CHAY_VA_XAC_MINH.md` để giảng viên phản biện có thể mở lên, nắm bắt quy trình chuẩn bị môi trường, kiểm tra cấu hình và tái lập kết quả trong vòng vài phút.
   - Chưa có thư mục và cẩm nang `manual_reproduction/` hướng dẫn sinh viên tự chạy một thực nghiệm độc lập từ PowerShell mà không phụ thuộc vào công cụ AI.

4. **Chú thích mã nguồn (Docstrings / Comments) quá dài dòng:**
   - Nhiều module trong `src/research_agent/` chứa các khối docstring tiếng Anh quá dài, nhắc lại các điều khoản quy ước nội bộ thay vì giải thích trực diện logic toán học và luồng xử lý dữ liệu.

---

### 1.2. Các điểm nghẽn và mâu thuẫn cần khóa cứng (Critical Blockers)

> [!CAUTION]
> **BLOCKER 1: Checkpoint `*.pt`, dữ liệu thô HDFS và cache nhị phân hiện không có trong Git**
> Toàn bộ các tệp trọng số mô hình PyTorch `*.pt` (bao gồm `best_checkpoint.pt`), tập dữ liệu thô (`datasets/raw/hdfs/`), và các tệp đệm nhị phân phân vùng (`experiments/runs/data/hdfs/*.pt`, `runtime/cache/`) đều nằm trong quy tắc `.gitignore` và **hoàn toàn không được lưu trữ trong Git** nhằm tránh phình to kích thước kho lưu trữ.
> **Hệ quả trực tiếp:** Một bản sao chép mã nguồn sạch (`git clone`) **chưa thể chạy được ngay lập tức** nếu chưa có quy trình chuẩn bị dữ liệu và nạp checkpoint từ kho lưu trữ ngoại vi (Zenodo / Release asset). Tuyệt đối không đưa ra phát biểu sai lệch rằng kho Git sạch có thể bấm chạy huấn luyện hoặc đánh giá ngay.

> [!WARNING]
> **BLOCKER 2: Mâu thuẫn về số trang tài liệu Master (100 / 104 / 114 trang)**
> Hiện tại đang tồn tại sự không nhất quán giữa các tài liệu mô tả về dung lượng trang của bản thuyết minh Master:
> - *Quy định đề cương chuyên đề:* Tối thiểu 100 trang.
> - *Báo cáo nghiệm thu giai đoạn trước (`FINAL-ACCEPTANCE-REPORT.md`):* Ghi nhận 104 trang (trước khi tích hợp thực nghiệm xác nhận Nineplus).
> - *Bản Master PDF thực tế hiện tại (`Chuyên đề chuyên sâu.pdf`):* Đạt chính xác **114 trang** (sau khi mở rộng Mục 3.2, bổ sung 6 mô hình Nineplus V3 và đồng bộ 606 công thức toán học OMML).
> **Giải pháp bắt buộc:** Khóa sự thật Master ở mốc **114 trang** và giải trình minh bạch lịch sử phát triển tài liệu (từ 104 lên 114 trang) trong mọi báo cáo nghiệm thu.

> [!IMPORTANT]
> **BLOCKER 3: Multi-View Seed 7 và Seed 999 hiện mới chỉ có result JSON trong Git**
> Trong cây Git hiện tại, nhánh Multi-View chỉ có duy nhất Seed 42 là có đầy đủ `RUN-MANIFEST.json` và `TRAIN-LOG.jsonl`. Hai lượt chạy của Seed 7 và Seed 999 mới chỉ có tệp kết quả đầu dò `V3-PROBE-RESULT.json` trong thư mục `experiments/nineplus/evaluation_v3/`, trong khi các thư mục chạy gốc `experiments/nineplus/confirmatory/CONF_MULTI_VIEW_ALIGNED_seed7_...` và `..._seed999_...` vẫn ở trạng thái chưa được theo dõi trong Git. Cần khóa rõ ràng trạng thái này và bổ sung commit cho manifest/log.

> [!NOTE]
> **BLOCKER 4: Chưa chốt chỉ số đánh giá cho nhánh Đồ thị lịch sử (Graph-Only)**
> Nhánh `GRAPH_ONLY` (Seed 42, 7, 999) thuộc giai đoạn khảo sát lịch sử Stage A2. Trong giao thức Nineplus V3 và chiến lược tối ưu hóa chi phí (`COST-OPTIMIZED EVIDENCE STRATEGY`), nhánh này được giữ nguyên ở trạng thái tham chiếu lịch sử (`HISTORICAL_EXPLORATORY_REFERENCE_ONLY`) và chưa thực hiện lại quy trình đánh giá đầu dò đóng băng V3 chuẩn hóa. Chỉ số của nhánh này phải ghi rõ là **chưa chốt (PENDING_AUDIT)** cho tới khi xác định được tệp artifact kết quả tương ứng.

---

## 2. CẤU TRÚC CÂY THƯ MỤC TINH GỌN MỤC TIÊU (MINIMAL TARGET TREE)

Repository sẽ được tổ chức lại gọn gàng, trong sáng theo đúng mô hình một đồ án/chuyên đề nghiên cứu sinh viên:

```text
D:\Research\
├── README.md                              # Giới thiệu tổng quan ngắn gọn, tự nhiên, súc tích (1-2 trang tiếng Việt)
├── HUONG_DAN_CHAY_VA_XAC_MINH.md           # Cẩm nang thực hành cho giảng viên / reviewer tái lập kết quả
├── manual_reproduction/
│   ├── README.md                          # Hướng dẫn chi tiết cho sinh viên tự chạy thực nghiệm độc lập
│   └── run_manual_sequence42.ps1          # Script PowerShell tinh gọn chuẩn bị sẵn để sinh viên chạy
│
├── Chuyên đề chuyên sâu.docx              # Bản thảo Master DOCX chính thức (606 nút OMML)
├── Chuyên đề chuyên sâu.pdf               # Bản xuất bản Master PDF 114 trang đồng bộ
├── SPECIALIZED-TOPIC-FINAL-QA-REPORT.md   # Báo cáo kiểm toán chất lượng học thuật và 8 chỉ tiêu bất biến
├── SPECIALIZED-TOPIC-NINEPLUS-INTEGRATION-REPORT.md # Báo cáo tích hợp số liệu V3 đã chuẩn hóa
│
├── src/                                   # Mã nguồn chính của chuyên đề (research_agent)
│   └── research_agent/
│       ├── core/                          # Tiện ích hàm băm, hằng số hệ thống
│       └── experiments/
│           ├── data/                      # Đọc log HDFS, trích xuất thuộc tính, phân chia causal split
│           ├── extractor/                 # Tokenizer bảo vệ tham số, Transformer Sequence View, Multi-View
│           ├── models/                    # Mô hình TemporalGraphViewEncoder
│           └── training/                  # Module huấn luyện Stage A2
│
├── scripts/                               # Các script chạy thực nghiệm và kiểm tra chính
│   ├── run_nineplus_confirmatory.py       # Huấn luyện mô hình xác nhận (Sequence, Multi-View)
│   ├── evaluate_nineplus_v3.py            # Đánh giá đầu dò tuyến tính V3 trên tập Validation
│   ├── run_h1_masking_ablation.py         # Kiểm thử cắt bỏ che tham số đầu vào H1
│   ├── run_h2_sequence_noparam_sensitivity.py # Phân tích độ nhạy bỏ tham số Sequence H2
│   └── gpu_smoke_test.py                  # Kiểm tra môi trường GPU, CUDA, PyTorch
│
├── experiments/
│   ├── experiment_index.csv               # Bảng mục lục tra cứu nhanh các đợt thực nghiệm (9 cột)
│   └── nineplus/
│       ├── confirmatory/                  # Checkpoints và nhật ký huấn luyện (checkpoint nạp ngoại vi)
│       └── evaluation_v3/                 # Tệp JSON tổng hợp kết quả đánh giá V3, H1, H2
│
└── datasets/
    └── raw/hdfs/                          # Dữ liệu HDFS nén gốc và bộ nhớ đệm phân vùng (nạp ngoại vi)
```

---

## 3. ĐỀ CƯƠNG CHI TIẾT CHO `README.md`

Tệp `README.md` mới sẽ được viết lại hoàn toàn bằng tiếng Việt chuẩn mực, ngắn gọn, súc tích, phản ánh chính xác học vị và đối tượng nghiên cứu:

1. **Tên đề tài & Thông tin chung:**
   - Tên đề tài: *Nghiên cứu các phương pháp học biểu diễn đặc trưng log phục vụ phát hiện bất thường an toàn thông tin*.
   - Đối tượng thực hiện: Sinh viên thực hiện chuyên đề nghiên cứu chuyên sâu.
   - Tài liệu báo cáo chính thức: Liên kết tới `Chuyên đề chuyên sâu.docx` và `Chuyên đề chuyên sâu.pdf` (114 trang, 606 công thức toán học OMML).

2. **Tóm tắt chuyên đề (1–2 đoạn tự nhiên):**
   - Trình bày bài toán biểu diễn đặc trưng nhật ký hệ thống (log telemetry) bảo toàn ngữ cảnh an ninh phục vụ phát hiện bất thường.
   - Khung phương pháp luận tích hợp: Chuỗi thời gian ngữ nghĩa dựa trên Transformer kết hợp Đồ thị phụ thuộc thời gian liên tục (Temporal GNN) thông qua hàm mất mát tự giám sát đa góc nhìn VICReg và cơ chế hòa trộn động (Gated Fusion).

3. **Cấu trúc thư mục tối giản:** Sơ đồ khối cây thư mục ngắn gọn như Mục 2.

4. **Yêu cầu môi trường & Khóa phụ thuộc (Dependency Lock):**
   - Hệ điều hành: Windows 11 (hoặc Linux tương đương).
   - Python: 3.12+.
   - Cài đặt thư viện qua tệp khóa phụ thuộc: `pip install -r requirements-lock.txt` (ghim cứng các phiên bản `torch==2.6.0+cu124`, `numpy`, `scipy`, `scikit-learn`, `psutil`, `python-docx`).
   - Phần cứng thực tế: Laptop GPU NVIDIA GeForce RTX 3050 Ti (4GB VRAM), RAM 16GB.

5. **Bộ dữ liệu thực nghiệm & Cơ chế chuẩn bị dữ liệu:**
   - Tập dữ liệu HDFS (Hadoop Distributed File System log telemetry).
   - Phân chia theo dòng thời gian chống rò rỉ (Causal Temporal Split): 35.000 phiên Train (68,4%), 7.500 phiên Validation (14,7%). Tập Test chưa từng được truy cập (`test_opened = false`, `test_reads = 0`).
   - **Lưu ý ngoại vi:** Dữ liệu raw và cache tensor `.pt` không nằm trong Git; hướng dẫn người đọc tải về từ kho lưu trữ dữ liệu nghiên cứu công khai và kiểm tra mã băm SHA-256 đối soát với `SUBSET-MANIFEST-HDFS.json`.

6. **Cách chạy nhanh (Quick Start cho Reviewer - Yêu cầu đã nạp Artifacts):**
   - Lệnh 1: Kiểm tra môi trường phần cứng (`python scripts/gpu_smoke_test.py`).
   - Lệnh 2: Tái lập bảng kết quả đánh giá hạ nguồn V3 trên checkpoint đã nạp (`python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42`).

7. **Vị trí lưu trữ Checkpoints, Logs và Kết quả:**
   - Checkpoints: `experiments/nineplus/confirmatory/<run_id>/best_checkpoint.pt` (lưu trữ cục bộ / tải qua kho ngoại vi).
   - Nhật ký huấn luyện: `experiments/nineplus/confirmatory/<run_id>/TRAIN-LOG.jsonl`.
   - Kết quả tổng hợp: `experiments/nineplus/evaluation_v3/V3_SIX_BACKBONE_EVALUATION_SUMMARY.json`.

8. **Tóm tắt kết quả chính (Bảng số liệu ngắn):**
   - Trình bày bảng so sánh ngắn gọn giữa Sequence-Only (AP = 1.0000, ROC-AUC = 1.0000) và Multi-View (AP trung bình = 0.6608, ROC-AUC trung bình = 0.8573).
   - Tóm tắt trung thực kết quả kiểm chứng: H2 không được hỗ trợ trong phạm vi đối chứng trực tiếp với Sequence-Only trên tập HDFS ($\Delta\text{AP} = -0.3392 \pm 0.0885$, vi phạm biên $\delta \ge -0.02$); H1 chưa thể đánh giá trực tiếp do bất tương thích độ mịn mục tiêu; H3, H4, H5 được bảo lưu cho nghiên cứu tiếp theo.

9. **Chỉ mục chuyển tiếp:** Đường dẫn trực tiếp tới `HUONG_DAN_CHAY_VA_XAC_MINH.md`.

---

## 4. ĐỀ CƯƠNG CHI TIẾT CHO `HUONG_DAN_CHAY_VA_XAC_MINH.md`

Đây là tài liệu thực hành trung tâm dành cho Thầy/Cô và Reviewer để chuẩn bị môi trường và tái lập kết quả:

- **Mục A: Cài đặt môi trường từ máy sạch & Khóa phụ thuộc (Dependency Lock):**
  - Hướng dẫn thiết lập môi trường ảo:
    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```
  - Cài đặt các gói phụ thuộc cố định phiên bản:
    ```powershell
    pip install -r requirements-lock.txt
    ```
  - Tệp `requirements-lock.txt` ghim cứng chính xác: `torch==2.6.0+cu124`, `numpy==1.26.4`, `scipy==1.13.1`, `scikit-learn==1.5.0`, `python-docx==1.1.2`, `psutil==5.9.8`.

- **Mục B: Kiểm tra cấu hình phần cứng và PyTorch:**
  - Lệnh thực thi: `python scripts/gpu_smoke_test.py`.
  - Kết quả in ra kỳ vọng: Tên GPU (NVIDIA GeForce RTX 3050 Ti Laptop GPU), dung lượng VRAM khả dụng, CUDA capability 8.6, cờ xác định `CUBLAS_WORKSPACE_CONFIG=:4096:8`.

- **Mục C: Quy trình chuẩn bị dữ liệu và Checkpoint từ máy sạch (Clean-room Preparation):**
  - Do Git không chứa dữ liệu nhị phân và checkpoint `*.pt`:
    1. Tải gói dữ liệu đệm tiền xử lý `experiments/runs/data/hdfs/` (`hdfs_ssl_train.pt`, `hdfs_ssl_val.pt`, `hdfs_vocab.json`) và nhãn kiểm định `experiments/runs/data/vault/hdfs_probe_labels_val.pt` từ kho phát hành dữ liệu ngoại vi.
    2. Đối soát mã băm SHA-256 của các tệp đệm với mã chuẩn trong `SUBSET-MANIFEST-HDFS.json`.
    3. Tải các tệp trọng số `best_checkpoint.pt` về đúng thư mục `experiments/nineplus/confirmatory/<run_id>/` và kiểm tra SHA-256 trước khi thực hiện đánh giá.

- **Mục D: Lệnh chạy thực nghiệm đại diện (Representative Training Run):**
  - Chạy mô hình Sequence-Only hạt giống 42:
    ```powershell
    python scripts/run_nineplus_confirmatory.py --mode sequence_only --seed 42 --epochs 12 --patience 3 --device cuda
    ```
  - *Lưu ý quan trọng về đường dẫn đầu ra:* Script ghi nhận toàn bộ tệp đầu ra vào:
    `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_<timestamp>/`
  - Thời gian dự kiến: ~13.6 phút trên laptop GPU RTX 3050 Ti.
  - Bộ nhớ VRAM chiếm dụng đo được nội bộ: ~170.4 MB (ghi vào manifest, không hiển thị trên console).
  - Cơ chế Early Stopping tự động kích hoạt tại Epoch 6 sau khi đạt val loss tốt nhất ở Epoch 3 (`best_epoch = 3`).

- **Mục E: Lệnh nạp và kiểm tra Checkpoint có sẵn:**
  - Lệnh Python một dòng để đọc siêu dữ liệu checkpoint mà không cần chạy lại từ đầu:
    ```powershell
    python -c "import torch; ckpt=torch.load('experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_1789413645/best_checkpoint.pt', map_location='cpu', weights_only=False); print('Keys:', list(ckpt.keys())); print('Best Epoch:', ckpt['epoch']); print('Best Val Loss:', ckpt['val_loss'])"
    ```

- **Mục F: Lệnh tái lập các chỉ số Validation trong báo cáo:**
  - Tái lập kết quả đầu dò tuyến tính đóng băng cho mô hình Sequence-Only Seed 42:
    ```powershell
    python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42
    ```
  - Kết quả in ra xác nhận: Average Precision = 1.0000, ROC-AUC = 1.0000, thời gian trích xuất ~10 giây.
  - Tái lập trên toàn bộ 6 mô hình xác nhận (Sequence và Multi-View):
    ```powershell
    python scripts/evaluate_nineplus_v3.py --all
    ```

- **Mục G: Bảng tra cứu vị trí tệp tin bằng chứng:**
  - Bảng liệt kê chi tiết: Tên mô hình, Seed, Đường dẫn Checkpoint, Đường dẫn nhật ký huấn luyện `TRAIN-LOG.jsonl`, Đường dẫn hồ sơ thực nghiệm `RUN-MANIFEST.json`.

- **Mục H: Hướng dẫn kiểm tra mã băm toàn vẹn SHA-256:**
  - Sử dụng lệnh PowerShell chuẩn: `Get-FileHash <đường_dẫn_tệp> -Algorithm SHA256`.
  - Cung cấp mã băm chuẩn của tệp dữ liệu và checkpoint để đối soát.

- **Mục I: Cam kết về tập dữ liệu Kiểm thử (Test split):**
  - Tuyên bố minh bạch: Tập dữ liệu Kiểm thử tiếp tục được bảo toàn trạng thái chưa mở (`TEST_OPENED=false`, `TEST_READ_COUNT=0`), toàn bộ kết quả báo cáo được đo kiểm độc lập trên tập Kiểm định (Validation).

---

## 5. KẾ HOẠCH THỰC NGHIỆM ĐỘC LẬP DÀNH CHO SINH VIÊN (`manual_reproduction/`)

Thư mục `manual_reproduction/` được thiết kế riêng để sinh viên có thể tự tay mở cửa sổ Windows PowerShell độc lập (không thông qua giao diện AI Agent) và thực hiện lại một đợt chạy huấn luyện:

### 5.1. Lý do lựa chọn cấu hình `SEQUENCE_ONLY seed42`
- *Thời lượng tối ưu:* Chỉ mất ~13.6 phút (12.45 phút huấn luyện + 1.16 phút kiểm định qua 6 epochs).
- *Tài nguyên phần cứng thấp:* VRAM đỉnh chỉ 170.4 MB (chiếm chưa đầy 5% dung lượng GPU 4GB), RAM hệ thống ~1.4 GB. Không gây nóng máy hay rủi ro tràn bộ nhớ.
- *Tính tái lập xác định:* Đã cấu hình `CUBLAS_WORKSPACE_CONFIG=:4096:8` và khóa seed ngẫu nhiên 42, đảm bảo hàm mất mát hội tụ khớp chính xác với lịch sử.

### 5.2. Cơ chế lưu trữ đầu ra thực tế
- **Cơ chế mặc định của script:** `scripts/run_nineplus_confirmatory.py` luôn ghi tệp đầu ra vào thư mục tự sinh:
  `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_<timestamp>/`
  chứ **không tự động ghi trực tiếp vào `manual_reproduction/`**.
- **Giải pháp kịch bản PowerShell:** Script `manual_reproduction/run_manual_sequence42.ps1` sẽ đảm nhận việc:
  1. Ghi nhật ký console (`Start-Transcript`).
  2. Kích hoạt lệnh huấn luyện `run_nineplus_confirmatory.py`.
  3. Sau khi chạy xong, xác định thư mục `CONF_SEQUENCE_ONLY_seed42_<timestamp>` mới nhất vừa tạo ra.
  4. Trích xuất thông tin `RUN-MANIFEST.json`, tính mã băm SHA-256 của `best_checkpoint.pt`.
  5. Xuất bản tóm tắt đối soát sang `manual_reproduction/MANUAL_RUN_SUMMARY.txt` để sinh viên đối chiếu độc lập mà không can thiệp vào các tệp gốc.

### 5.3. Quy trình thực hiện từng bước
1. Mở Windows PowerShell thông thường.
2. Kích hoạt môi trường: `.venv\Scripts\Activate.ps1`.
3. Chuyển vào thư mục gốc: `cd D:\Research`.
4. Thực thi kịch bản độc lập:
   ```powershell
   powershell -ExecutionPolicy Bypass -File manual_reproduction\run_manual_sequence42.ps1
   ```
5. Đọc tệp tóm tắt kết quả tại `manual_reproduction\MANUAL_RUN_SUMMARY.txt` và đối soát với số liệu trong báo cáo chuyên đề.

---

## 6. KẾ HOẠCH 5–7 ẢNH CHỤP MÀN HÌNH MINH CHỨNG (SCREENSHOT PLAN)

Để minh chứng tính trung thực và khả năng thực thi thực tế trong báo cáo, thiết kế danh mục 7 ảnh chụp màn hình cụ thể từ cửa sổ dòng lệnh Windows PowerShell (tuyệt đối không chụp giao diện AI):

| STT | Tên tệp ảnh dự kiến | Lệnh / Màn hình thực hiện | Mục đích chứng minh & Nội dung hiển thị thực tế |
| :---: | :--- | :--- | :--- |
| **1** | `01_environment_gpu_git.png` | `python scripts/gpu_smoke_test.py`<br>`git log -n 1 --oneline` | Môi trường thực tế trên máy trạm: Windows 11, GPU RTX 3050 Ti Laptop, CUDA capability, và mã commit Git hiện tại. |
| **2** | `02_manual_run_command.png` | Cửa sổ PowerShell với dấu nhắc `PS D:\Research>` hiển thị dòng lệnh sinh viên tự gõ để chạy Sequence-Only Seed 42. | Thao tác dòng lệnh trực tiếp từ hệ điều hành bởi sinh viên. |
| **3** | `03_training_epochs_loss.png` | Tiến trình huấn luyện Epoch 1–3 in trên console (`Epoch x/12 \| Train: ...m \| Val: ...m \| Val Loss: ...`). | Mạng nơ-ron thực sự tối ưu hóa và hàm mất mát giảm dần.<br>*(Lưu ý: Console in thời gian và val loss; dung lượng VRAM ~170 MB được ghi nhận trong RUN-MANIFEST.json, không tuyên bố console in VRAM nếu script không in dòng này)*. |
| **4** | `04_early_stopping_best_checkpoint.png` | Thông báo Early Stopping tại Epoch 6 (dừng sớm với patience=3, lưu best_checkpoint tại Epoch 3). | Cơ chế dừng sớm tự động và việc lưu trữ checkpoint thành công. |
| **5** | `05_checkpoint_hash_verification.png` | `Get-FileHash ...\best_checkpoint.pt -Algorithm SHA256` | Tính toàn vẹn và khả năng truy vết mật mã của checkpoint đã lưu. |
| **6** | `06_validation_metric_reproduction.png` | `python scripts/evaluate_nineplus_v3.py --architecture SEQUENCE_ONLY --seed 42` | Việc tái lập độc lập các chỉ số đánh giá hạ nguồn (AP = 1.0000, ROC-AUC = 1.0000) trên 7.500 phiên Validation. |
| **7** | `07_repository_file_structure.png` *(Tùy chọn)* | `Get-ChildItem -Directory` hoặc hiển thị cây thư mục dự án sạch sẽ. | Cấu trúc repository ngăn nắp, sẵn sàng nghiệm thu. |

---

## 7. LỰA CHỌN 8 ĐOẠN MÃ NGUỒN TIÊU BIỂU CHO WORD (CODE EXCERPTS)

Tuyển chọn 8 đoạn trích mã nguồn then chốt (mỗi đoạn từ 8 đến 26 dòng) đại diện cho các đóng góp kỹ thuật cốt lõi trong văn bản chuyên đề, bảo đảm tính trọn vẹn của logic lập trình:

### Đoạn trích 1: Phân chia tập dữ liệu theo trục thời gian và chọn lọc ngân sách nhân quả
- **FILE:** `src/research_agent/experiments/data/hdfs_split_authority.py`
- **FUNCTION:** `compute_and_cache_split` (Kiểm tra bất biến và chọn lọc phiên)
- **LINE_RANGE:** 177–196 (20 dòng)
- **THESIS_SECTION:** Mục 3.1.2 (Khung dữ liệu đối chuẩn và giao thức phân chia theo dòng thời gian chống rò rỉ)
- **SHORT_CAPTION:** Phép kiểm tra tính bất giao và chọn lọc ngân sách 35.000 Train / 7.500 Val theo thời gian
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích được các phép `assert` kiểm tra tính bất giao giữa Train, Val, Test nhằm ngăn chặn rò rỉ thông tin tương lai (`assert train_max_end < val_min_start`), kết hợp logic sắp xếp theo mốc thời gian bắt đầu của phiên để chọn lọc chính xác ngân sách nhân quả 35.000 phiên Train và 7.500 phiên Val.

### Đoạn trích 2: Kiểu hóa và mã giả danh tham số có nhận thức an ninh
- **FILE:** `src/research_agent/experiments/extractor/tokenizer.py`
- **FUNCTION:** `PrivacyAwareLogTokenizer.tokenize_line`
- **LINE_RANGE:** 138–159 (22 dòng)
- **THESIS_SECTION:** Mục 2.2.1 / 2.2.2 (Lược đồ kiểu hóa và bảo toàn tham số có nhận thức an ninh)
- **SHORT_CAPTION:** Phân loại và mã hóa tham số động bảo vệ quyền riêng tư
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Phân biệt được địa chỉ IP nội bộ (RFC1918) và ngoại vi, phân loại đường dẫn tập tin hệ thống trọng yếu (`/etc/`, `/tmp/`, `/var/log/`), và việc sử dụng hàm băm HMAC có khóa ngắn hạn để tạo mã giả danh nhất quán trong phiên.

### Đoạn trích 3: Hàm mất mát tự giám sát dự đoán tham số động đa khe (L_MPP)
- **FILE:** `src/research_agent/experiments/extractor/sequence_view.py`
- **FUNCTION:** `SequenceViewExtractor.compute_sequence_ssl_losses`
- **LINE_RANGE:** 201–218 (18 dòng)
- **THESIS_SECTION:** Mục 2.3.1 (Mục tiêu huấn luyện tự giám sát của bộ trích xuất tuần tự)
- **SHORT_CAPTION:** Tính toán hàm mất mát Cross-Entropy cho các khe tham số bị che giấu
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Trình bày được cấu trúc đầu ra đa khe `[B, T, K, V_param]`, cách tạo mặt nạ loại bỏ token đệm `<PAD_PARAM>` để chỉ phạt trên các tham số có nghĩa thực tế, và cơ chế tính toán mất mát tự giám sát L_MPP.

### Đoạn trích 4: Khôi phục trạng thái bộ nhớ rỗng cho đồ thị động (Inductive Reset)
- **FILE:** `src/research_agent/experiments/models/temporal_graph_view_encoder.py`
- **FUNCTION:** `TemporalGraphViewEncoder.reset_node_states`
- **LINE_RANGE:** 161–168 (8 dòng)
- **THESIS_SECTION:** Mục 2.3.2 / Mục 3.1.2 (Bộ trích xuất đồ thị động và thiết lập ranh giới phân vùng)
- **SHORT_CAPTION:** Xóa bộ nhớ trạng thái thực thể tại ranh giới chuyển đổi phân vùng
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích tại sao trong mô hình đồ thị động có bộ nhớ (GRUCell), bắt buộc phải xóa sạch bộ nhớ nút, mốc thời gian và bộ đệm lịch sử khi chuyển giữa Train và Validation để đảm bảo tính quy nạp (inductive) và không rò rỉ trạng thái.

### Đoạn trích 5: Cơ chế hòa trộn đa góc nhìn động dựa trên cổng (Gated Fusion)
- **FILE:** `src/research_agent/experiments/extractor/multi_view.py`
- **FUNCTION:** `GatedMultiViewFusion` (`__init__` và `forward`)
- **LINE_RANGE:** 107–120 (14 dòng)
- **THESIS_SECTION:** Mục 2.4.4 (Cổng độ tin cậy động và Biểu diễn thống nhất canonical)
- **SHORT_CAPTION:** Khởi tạo mạng cổng MLP và hòa trộn biểu diễn chuỗi - đồ thị qua vector Sigmoid
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích cấu trúc mạng cổng MLP (`Linear -> GELU -> Linear -> Sigmoid`) nhận đầu vào kết hợp `[z_seq; z_graph]`, sinh vector trọng số $\alpha \in [0, 1]^d$, và tính vector biểu diễn đa góc nhìn cuối cùng qua phép tổ hợp lồi $z_{mv} = \alpha \odot z_{seq} + (1-\alpha) \odot z_{graph}$.

### Đoạn trích 6: Giao thức huấn luyện đầu dò tuyến tính đóng băng (Frozen Linear Probe)
- **FILE:** `scripts/evaluate_nineplus_v3.py`
- **FUNCTION:** `V3Evaluator.fit_linear_probe`
- **LINE_RANGE:** 305–327 (23 dòng)
- **THESIS_SECTION:** Mục 3.1.3 (Chuẩn hóa Giao thức Đầu dò Tuyến tính Đóng băng V3)
- **SHORT_CAPTION:** Huấn luyện bộ phân loại tuyến tính mỏng trên biểu diễn đóng băng
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích nguyên lý đánh giá chất lượng biểu diễn tự giám sát: đóng băng 100% trọng số backbone, chỉ huấn luyện ma trận $W \in \mathbb{R}^{128 \times 1}$ với bộ tối ưu AdamW trong 50 epochs trên biểu diễn Train, cố định hạt giống 10007 để đảm bảo tính khách quan tuyệt đối.

### Đoạn trích 7: Tính toán các chỉ số an ninh Average Precision (AP) và ROC-AUC
- **FILE:** `scripts/evaluate_nineplus_v3.py`
- **FUNCTION:** `compute_ap_and_roc_auc`
- **LINE_RANGE:** 57–82 (26 dòng)
- **THESIS_SECTION:** Mục 3.1.3 (Hệ thống thang đo ba tầng và hàm mục tiêu)
- **SHORT_CAPTION:** Thuật toán tính toán tích phân AP và thống kê xếp hạng ROC-AUC hoàn chỉnh
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích trọn vẹn hàm toán học từ bước kiểm tra nhãn hai lớp, tính toán tích phân hình thang Precision-Recall cho AP trên tập mất cân bằng cực đoan, tính toán thống kê Mann-Whitney U cho ROC-AUC, tới lệnh hoàn trả giá trị `return ap, auc` mà không bị cắt cụt logic.

### Đoạn trích 8: Hàm băm SHA-256 theo khối dữ liệu lớn (Chunk-based Hashing)
- **FILE:** `src/research_agent/core/hash_utils.py`
- **FUNCTION:** `compute_file_sha256`
- **LINE_RANGE:** 11–21 (11 dòng)
- **THESIS_SECTION:** Mục 3.1.1 (Môi trường tính toán, tính tái lập và kiểm định độ bất định)
- **SHORT_CAPTION:** Tính toán mã băm SHA-256 theo từng khối dữ liệu 64KB
- **NỘI DUNG SINH VIÊN CẦN NẮM VỮNG:** Giải thích kỹ thuật đọc luồng nhị phân theo khối (chunk-based streaming) giúp tính toán mã băm toàn vẹn cho các tệp checkpoint và tập dữ liệu dung lượng hàng gigabyte mà không làm tràn bộ nhớ RAM.

---

## 8. RÀ SOÁT TÍNH DỄ ĐỌC CỦA MÃ NGUỒN (SOURCE READABILITY AUDIT)

Rà soát các tệp mã nguồn để chuẩn bị cho giai đoạn tinh gọn tiếp theo (tuyệt đối không chỉnh sửa mã nguồn trong pha này):

| Tệp mã nguồn | Vấn đề phát hiện | Khuyến nghị xử lý |
| :--- | :--- | :--- |
| `src/research_agent/experiments/extractor/sequence_view.py` | Docstring đầu tệp chứa các thuật ngữ hợp đồng nội bộ: *"Frozen Specification", "Bang 2.1", "Stage A1 Contract", "BOUNDED_MULTI_SLOT_..."*. | `SHORTEN`: Rút gọn docstring thành mô tả kỹ thuật kiến trúc Transformer Encoder và các hàm mất mát MEP, MPP, Time. |
| `src/research_agent/experiments/models/temporal_graph_view_encoder.py` | Docstring đầu tệp chứa các quy ước hành chính: *"Contract V1.3 Amended", "Relation Target Firewall", "Node Target Firewall"*. | `SHORTEN`: Rút gọn docstring, mô tả rõ cơ chế GRUCell, hàm nhúng thời gian liên tục $\phi(\Delta t)$, và các đầu ra tự giám sát. |
| `src/research_agent/experiments/data/hdfs_split_authority.py` | Docstring nhắc lại *"Single-source-of-truth session interval extraction, SPL-HDFS-001 Shared Module"*. | `SHORTEN`: Đổi thành mô tả kỹ thuật phân chia dữ liệu nhân quả Train/Val/Test theo dòng thời gian. |
| `src/research_agent/experiments/extractor/tokenizer.py` | Docstring dài dòng về *"Chapter 2 Frozen Specification & Key Governance"*. | `SHORTEN`: Tóm tắt ngắn gọn 4 chế độ tiền xử lý và cơ chế mã giả danh HMAC bảo vệ quyền riêng tư. |
| `src/research_agent/core/hash_utils.py` | Docstring nhắc tới *"RC-10, RC-15, RC-16"* (các quy tắc hiến pháp nội bộ của AI). | `REMOVE_REDUNDANT_COMMENT`: Xóa các ký hiệu mã hiệu nội bộ `(RC-...)`. |
| Toàn bộ các script trong `scripts/` | Các chú thích hiển nhiên, lặp lại mã lệnh (ví dụ: `# Save DOCX`, `# Create directory if not exists`). | `REMOVE_REDUNDANT_COMMENT`: Loại bỏ các chú thích hiển nhiên để mã nguồn gọn gàng. |

---

## 9. CHỈ MỤC BẰNG CHỨNG THỰC NGHIỆM (`experiments/experiment_index.csv`)

Nhằm giúp Thầy/Cô phản biện tra cứu tức thì bất kỳ mô hình nào mà không cần duyệt cây thư mục phức tạp, đề xuất xây dựng duy nhất **MỘT** bảng chỉ mục `experiments/experiment_index.csv` với cấu trúc cột phân định rạch ròi giữa `run_source_commit` (mã commit khi chạy mô hình) và `evidence_commit` (mã commit khóa nghiệm thu bằng chứng), đồng thời cập nhật chính xác `best_epoch` và hiện trạng trong Git:

| run_id | architecture | seed | best_epoch | checkpoint (ngoại vi) | log / manifest | validation_result | run_source_commit | evidence_commit | status |
| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: | :---: |
| `CONF_SEQUENCE_ONLY_seed42_1789413645` | SEQUENCE_ONLY | 42 | **3** | `.../best_checkpoint.pt` | `TRAIN-LOG.jsonl`<br>`RUN-MANIFEST.json` | `AP=1.0000, ROC=1.0000` | `47e4ad6` | `878a3db` | `COMPLETED` |
| `CONF_SEQUENCE_ONLY_seed7_1789415728` | SEQUENCE_ONLY | 7 | **11** | `.../best_checkpoint.pt` | `TRAIN-LOG.jsonl`<br>`RUN-MANIFEST.json` | `AP=1.0000, ROC=1.0000` | `47e4ad6` | `878a3db` | `COMPLETED` |
| `CONF_SEQUENCE_ONLY_seed999_1789420295` | SEQUENCE_ONLY | 999 | **12** | `.../best_checkpoint.pt` | `TRAIN-LOG.jsonl`<br>`RUN-MANIFEST.json` | `AP=1.0000, ROC=1.0000` | `47e4ad6` | `878a3db` | `COMPLETED` |
| `CONF_MULTI_VIEW_ALIGNED_seed42_1789393292` | MULTI_VIEW_ALIGNED | 42 | **6** | `.../best_checkpoint.pt` | `TRAIN-LOG.jsonl`<br>`RUN-MANIFEST.json` | `AP=0.7604, ROC=0.9946` | `7bdcade` | `878a3db` | `COMPLETED` |
| `CONF_MULTI_VIEW_ALIGNED_seed7_1789452137` | MULTI_VIEW_ALIGNED | 7 | **3** | `.../best_checkpoint.pt` | *(Chưa commit log/manifest)* | `AP=0.6309, ROC=0.8081` | `1dc6741` | `878a3db` | `RESULT_JSON_ONLY_IN_GIT` |
| `CONF_MULTI_VIEW_ALIGNED_seed999_1789541331` | MULTI_VIEW_ALIGNED | 999 | **4** | `.../best_checkpoint.pt` | *(Chưa commit log/manifest)* | `AP=0.5911, ROC=0.7693` | `0cc1752` | `878a3db` | `RESULT_JSON_ONLY_IN_GIT` |
| `CONF_GRAPH_ONLY_seed42_1789448995` | GRAPH_ONLY | 42 | 1 | *Historical Checkpoint* | `RUN-MANIFEST.json` | *Chưa chốt (Chờ artifact V3)* | `3e0bcef` | `878a3db` | `HISTORICAL_REF (PENDING_AUDIT)` |
| `CONF_GRAPH_ONLY_seed7_1789449292` | GRAPH_ONLY | 7 | 12 | *Historical Checkpoint* | `RUN-MANIFEST.json` | *Chưa chốt (Chờ artifact V3)* | `d6fb10b` | `878a3db` | `HISTORICAL_REF (PENDING_AUDIT)` |
| `CONF_GRAPH_ONLY_seed999_1789449583` | GRAPH_ONLY | 999 | 12 | *Historical Checkpoint* | `RUN-MANIFEST.json` | *Chưa chốt (Chờ artifact V3)* | `d6fb10b` | `878a3db` | `HISTORICAL_REF (PENDING_AUDIT)` |

*Ghi chú quan trọng cho bảng chỉ mục:*
1. **best_epoch chính xác:** Sequence seeds 42, 7, 999 lần lượt đạt val loss tối ưu tại epoch 3, 11, 12. Multi-View seeds 42, 7, 999 lần lượt đạt val loss tối ưu tại epoch 6, 3 (val loss 48.7659), và 4.
2. **run_source_commit vs evidence_commit:** `run_source_commit` là commit xác lập mã nguồn tại thời điểm huấn luyện backbone; `evidence_commit` (`878a3db`) là commit đóng gói và nghiệm thu toàn bộ báo cáo bằng chứng thực nghiệm của chiến dịch Nineplus V3.
3. **Multi-View seed 7 & 999:** Hiện trong Git chỉ mới có tệp kết quả `V3-PROBE-RESULT.json`; thư mục huấn luyện cục bộ chứa manifest và log chưa được thêm vào Git.
4. **Graph-Only:** Không chốt chỉ số đánh giá AP/ROC-AUC cho tới khi xác định được tệp artifact kết quả đo kiểm V3 tương ứng.

---

## 10. TRẢI NGHIỆM ĐỌC CỦA NGƯỜI PHẢN BIỆN (REVIEWER EXPERIENCE)

Hành trình trải nghiệm của Thầy/Cô phản biện được tối ưu hóa theo lộ trình 4 bước tinh giản:

```text
[Mở README.md]
     │
     ▼
[Hiểu mục tiêu đề tài & cấu trúc gọn gàng (trong 2 phút)]
     │
     ▼
[Mở HUONG_DAN_CHAY_VA_XAC_MINH.md]
     │
     ▼
[Chạy 1 lệnh kiểm tra GPU & 1 lệnh đánh giá tái lập số liệu AP=1.0000 (trong 1 phút)]
```

- Không bắt buộc người đọc phải đi qua hàng chục tài liệu đặc tả trung gian.
- Mọi phát ngôn khoa học đều dẫn trực tiếp tới dòng lệnh kiểm tra và tệp kết quả JSON cụ thể.

---

## 11. THỨ TỰ HÀNH ĐỘNG TRIỂN KHAI TIẾP THEO (IMPLEMENTATION BACKLOG)

Quá trình hoàn thiện kho lưu trữ và đóng gói đồ án được thực hiện nghiêm ngặt theo trình tự 9 bước logic sau:

```text
1. Khóa sự thật Master
   └── Thống nhất số trang chính thức 114 trang; giải trình lịch sử mở rộng từ 104 trang lên 114 trang.
        │
2. Khóa provenance experiment
   └── Tách biệt run_source_commit vs evidence_commit; đưa manifest/log Multi-View 7 & 999 vào Git.
        │
3. Cơ chế artifact ngoại vi
   └── Xác lập nơi lưu trữ bên ngoài cho checkpoint *.pt, raw HDFS, và cache; lập bảng mã băm SHA-256.
        │
4. Dependency lock
   └── Tạo tệp requirements-lock.txt ghim cứng phiên bản chính xác của mọi thư viện (PyTorch, CUDA, ...).
        │
5. Manual reproduction setup
   └── Hoàn thiện kịch bản PowerShell tự điều phối thư mục đầu ra trong experiments/nineplus/confirmatory/.
        │
6. Chạy thật và chụp ảnh minh chứng
   └── Thực thi lệnh trên PowerShell thật; chụp 7 ảnh màn hình phản ánh chính xác kết quả in ra.
        │
7. Chèn code/ảnh vào Word
   └── Chèn 8 đoạn trích mã nguồn và 7 ảnh chụp vào Master DOCX; bảo toàn 606 OMML; xuất PDF 114 trang.
        │
8. Reviewer clean-room test
   └── Kiểm thử độc lập trên máy sạch từ bước clone Git, nạp artifact ngoại vi tới chạy lệnh tái lập.
        │
9. Xuất xưởng và đóng gói hoàn thiện
   └── Dọn dẹp tệp tạm ở thư mục gốc; tạo experiment_index.csv; gắn tag release hoàn tất chuyên đề.
```

Chi tiết từng bước trong backlog:

1. **Khóa sự thật Master (Lock Master Truth):**  
   Thống nhất toàn bộ tài liệu thuyết minh và báo cáo nghiệm thu ở mốc **114 trang**, 606 công thức toán học OMML chuẩn Word. Giải trình rõ ràng tiến trình mở rộng tự nhiên từ 104 trang (trước Nineplus) lên 114 trang (sau khi tích hợp đầy đủ bảng biểu, kết quả kiểm định 6 backbone và phân tích H1/H2).

2. **Khóa provenance experiment (Lock Experiment Provenance):**  
   Xác lập ranh giới rõ ràng giữa `run_source_commit` và `evidence_commit`. Đưa các tệp `RUN-MANIFEST.json` và `TRAIN-LOG.jsonl` của Multi-View Seed 7 và Seed 999 vào theo dõi trong Git để xóa bỏ trạng thái `RESULT_JSON_ONLY_IN_GIT`.

3. **Cơ chế artifact ngoại vi (External Artifact Storage):**  
   Xây dựng quy chế lưu trữ ngoại vi (Zenodo / OSF / Release Asset) cho các tệp nhị phân dung lượng lớn không thể đưa vào Git: các checkpoint `best_checkpoint.pt`, tập dữ liệu thô HDFS, và các tệp đệm PyTorch `.pt`. Công bố bảng mã băm SHA-256 đối soát công khai.

4. **Khóa phụ thuộc môi trường (Dependency Lock):**  
   Tạo tệp `requirements-lock.txt` ghi rõ chính xác phiên bản của PyTorch (`2.6.0+cu124`), numpy, scipy, scikit-learn, psutil, python-docx để máy trạm mới có thể cài đặt môi trường đồng nhất 100%.

5. **Thiết lập quy trình tái lập độc lập (Manual Reproduction Setup):**  
   Biên soạn `manual_reproduction/README.md` và hoàn thiện `manual_reproduction/run_manual_sequence42.ps1` có cơ chế tự động bắt đúng thư mục `experiments/nineplus/confirmatory/CONF_SEQUENCE_ONLY_seed42_<timestamp>/` và trích xuất tóm tắt.

6. **Chạy thực tế và chụp ảnh minh chứng (Execute & Capture Real Screenshots):**  
   Mở PowerShell thật trên Windows 11, chạy thực tế kiểm tra môi trường và chạy huấn luyện Sequence-Only Seed 42. Chụp 7 ảnh màn hình thực tế, không tuyên bố sai lệch về các thông số console không in ra.

7. **Chèn mã nguồn và ảnh minh họa vào Word (Insert Code & Visuals into Word):**  
   Chèn 8 đoạn trích mã nguồn chuẩn hóa (không cắt cụt logic) và 7 ảnh chụp thực tế vào các vị trí tương ứng trong bản thảo `Chuyên đề chuyên sâu.docx`. Bảo toàn tuyệt đối 606 nút công thức toán học OMML và xuất khẩu `Chuyên đề chuyên sâu.pdf` 114 trang đồng bộ.

8. **Thử nghiệm môi trường sạch độc lập (Reviewer Clean-Room Test):**  
   Mô phỏng quy trình của một giảng viên phản biện trên máy sạch: Clone kho Git, tải artifact ngoại vi, cài môi trường ảo qua `requirements-lock.txt`, chạy lệnh kiểm tra GPU và chạy tái lập kết quả đánh giá AP=1.0000.

9. **Xuất xưởng và nghiệm thu (Final Release & Clean Repository Packaging):**  
   Di chuyển toàn bộ các script tạm thời dùng một lần vào thư mục lưu trữ nội bộ hoặc xóa bỏ; tạo tệp `experiments/experiment_index.csv` hoàn chỉnh; gắn thẻ Git Release cho kho lưu trữ `Minhlike/Chuyende`.

---

## 12. DANH MỤC CÁC MÂU THUẪN ĐANG MỞ VÀ TRẠNG THÁI XỬ LÝ (UNRESOLVED CONTRADICTIONS LOG)

Nhằm đảm bảo tính trung thực học thuật tối đa, toàn bộ các mâu thuẫn được ghi nhận minh bạch và có phương án xử lý dứt điểm:

| Mâu thuẫn phát hiện | Hiện trạng kỹ thuật | Phương án giải quyết trong Backlog |
| :--- | :--- | :--- |
| **Mâu thuẫn số trang Master (100 / 104 / 114 trang)** | `Chuyên đề chuyên sâu.pdf` thực tế có 114 trang; báo cáo cũ ghi 104 trang; yêu cầu khung là $\ge$ 100 trang. | Khóa chính thức ở **Bước 1**: Xác nhận bản Master chính thức là **114 trang**, giải trình rõ sự phát triển nội dung sau khi tích hợp Nineplus V3. |
| **Tính sẵn sàng của bản clone sạch (Clean Clone Readiness)** | Checkpoint `*.pt`, dữ liệu raw và cache nhị phân không có trong Git; người clone sạch chưa thể chạy ngay. | Xử lý tại **Bước 3 & 4**: Hướng dẫn nạp artifact từ kho ngoại vi và đối soát mã băm SHA-256 trước khi chạy. |
| **Thiếu hụt tệp bằng chứng Multi-View Seed 7 & 999 trong Git** | Git chỉ có `V3-PROBE-RESULT.json`; chưa commit `RUN-MANIFEST.json` và `TRAIN-LOG.jsonl` tương ứng. | Xử lý tại **Bước 2**: Đưa các tệp manifest và log huấn luyện của Seed 7 & 999 vào Git. |
| **Chỉ số đánh giá Graph-Only chưa được kiểm chứng V3** | Checkpoints Stage A2 là tham chiếu lịch sử; chưa chạy qua quy trình đầu dò V3 chuẩn hóa. | Xử lý tại **Bước 2**: Giữ nguyên trạng thái `PENDING_AUDIT`, không đưa ra phát biểu vượt quá bằng chứng. |
