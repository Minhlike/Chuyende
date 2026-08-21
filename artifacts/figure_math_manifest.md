# Figure Mathematical Typography Manifest

This manifest audits and tracks the mathematical typography, generation pipeline, and vector compliance for all 8 figures across Chapters 1 and 2.

## Audit Matrix for All 8 Figures

| Figure ID | Title | Math / Typography Tokens | Canonical Source in Body | Generation Method | Format | QA Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hình 1.1** | Phân cấp các đơn vị quan sát nhật ký hệ thống | Mức sự kiện $, chuỗi $[e_{t-k+1}, \dots, e_t]$, Context Richness vs Resource Cost | Mục 1.1 | Python Matplotlib Vector Render | Vector PNG (600 DPI) | PASS |
| **Hình 1.2** | Không gian bằng chứng hành vi MITRE ATT&CK phi tuyến | Initial Access $\to$ Execution $\to$ PrivEsc, Nhảy cóc, Lặp vòng, Phân nhánh | Mục 1.2 | Python Matplotlib Vector Render | Vector PNG (600 DPI) | PASS |
| **Hình 1.3** | Kiến trúc ba tầng nghiên cứu và vai trò trung tâm của vector biểu diễn z | \theta(X)$, $\mathbf{z} = f_\theta(X)$, $\mathbf{z} \in \mathbb{R}^d$, Frozen Probe | Mục 1.3 | Python Matplotlib Vector Render | Vector PNG (600 DPI) | PASS |
| **Hình 1.4** | Sơ đồ ánh xạ 3 nhóm phương pháp biểu diễn với 5 khoảng trống nghiên cứu | $\mathcal{O}(N)$, $\mathcal{O}(L^2)$, Over-smoothing/squashing, RQ1–RQ5 | Mục 1.4 | Python Matplotlib Vector Render | Vector PNG (600 DPI) | PASS |
| **Hình 2.1** | Kiến trúc hai mặt phẳng: Huấn luyện đa góc nhìn và Suy luận dòng | $\mathcal{D}_{\mathrm{train}}$, \theta$, $\min \mathcal{L}_{\mathrm{align}}(\mathbf{z}_{\mathrm{seq}}, \mathbf{z}_{\mathrm{graph}})$, $\theta^*$,  \in \mathcal{L}_{1:t}$, $\mathcal{S}_t = \mathrm{Upd}(\mathcal{S}_{t-1}, e_t)$, $\mathbf{z}_t = f_{\theta^*}(\mathcal{S}_t) \in \mathbb{R}^d$, $\hat{y} = \sigma(\mathbf{W}^\top \mathbf{z}_t + b)$ | Mục 2.1.1, 2.1.2 | Python Matplotlib Vector Render | Vector PNG (600 DPI) | PASS |
| **Hình 2.2** | Kiến trúc bộ trích xuất đặc trưng chuỗi ngữ nghĩa dựa trên Transformer | Cửa sổ $, Bộ sáu sự kiện  = (t_i, \tau_i, v_i, o_i, a_i, p_i)$, Vector  \in \mathbb{R}^d$, Transformer Encoder, Vector chuỗi \mathrm{seq}$, Mục tiêu tự học \mathrm{MEP}, L_\mathrm{MPP}, L_\mathrm{time}$ | Mục 2.2.1.1, 2.3.1 | Word Native Drawing Canvas | Word Native Vector Shapes | PASS |
| **Hình 2.3** | Kiến trúc xây dựng đồ thị nguồn gốc phụ thuộc thời gian và Bộ trích xuất Temporal GNN | Đồ thị $, Tập đỉnh $, Tập cạnh $, Suy giảm thời gian $\exp(-\lambda \Delta t)$, Thông điệp {v \to u}(t)$, Gom cụm {u,\mathrm{agg}}(t)$, Cập nhật (t)$, Vector đồ thị \mathrm{graph}$ trên $ | Mục 2.2.1.1, 2.3.3 | Word Native Drawing Canvas | Word Native Vector Shapes | PASS |
| **Hình 2.4** | Cơ chế gióng hàng đa góc nhìn, điều hòa chống sụp đổ và học biểu diễn thống nhất | Đầu vào \mathrm{seq}, z_\mathrm{graph}$, Đầu chiếu \mathrm{seq}, p_\mathrm{graph}$, Mất mát \mathrm{inv}, L_\mathrm{preserv}$, Phẫu thuật $\Theta_\mathrm{PCGrad}$, Dung hợp chéo \mathrm{cross} = u_\mathrm{seq} \odot u_\mathrm{graph}$, Vector thống nhất \mathrm{mv}$, Đóng gói \mathrm{mv}$ | Mục 2.4.1, 2.4.2, 2.4.3 | Word Native Drawing Canvas | Word Native Vector Shapes | PASS |

## Mathematical Typography Compliance Rules

1. **No Pseudo-Math / Raw Underscores**: Zero raw characters such as _seq, ^2, R^{d_model}. All mathematical terms use proper LaTeX mathtext (STIX font set) in Matplotlib renderers or proper Unicode mathematical characters and semantic academic labels in Word Native Shapes.
2. **Double-Struck Real Sets**: Real Euclidean spaces use $\mathbb{R}^d$ / $\mathbb{R}$ / ℝ, never plain Latin R.
3. **Subscript/Superscript Fidelity**: All subscripts and superscripts are positioned on their true mathematical tiers.
4. **Vector/Matrix/Scalar Distinction**: Vectors are bolded or clearly designated by semantic role; matrices use bold uppercase $\mathbf{W}, \mathbf{H}$; parameter sets use uppercase Greek $\Theta_\mathrm{PCGrad}$.
5. **No AI-Generated Mathematical Raster Images**: All figures are strictly deterministic vector renderings (Matplotlib 600 DPI vector exports and Word Native Drawing Canvas Shapes).
