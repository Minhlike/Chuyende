# ATTT BASIC-FIRST SCIENTIFIC PROSE SKILL v3.1

## Mục đích

Skill này dùng để biên tập, viết lại và kiểm tra các báo cáo, chuyên đề, luận văn và tài liệu nghiên cứu khoa học bằng tiếng Việt trong các chủ đề an toàn thông tin, machine learning, deep learning, phân tích log, biểu diễn dữ liệu, đồ thị và các lĩnh vực kỹ thuật liên quan.

Mục tiêu tối cao không phải là làm văn bản “nghe học thuật hơn”, cũng không phải làm văn bản “bớt giống AI” theo nghĩa bề mặt. Mục tiêu là tạo ra một văn bản mà người đọc có thể theo dõi được vì sao một kết luận xuất hiện, kết luận đó dựa trên kiến thức cơ bản nào, bằng chứng nào đang hỗ trợ nó, và giới hạn của suy luận nằm ở đâu.

Nguyên tắc trung tâm:

> **Depth by derivation, not by jargon.**

Muốn đoạn văn sâu hơn, hãy mở thêm mắt xích suy luận. Không làm nó khó hơn bằng cách tăng thuật ngữ, ký hiệu, taxonomy, tính từ học thuật hoặc formalism không phục vụ lập luận.

Văn bản cuối phải khiến giảng viên có cảm giác tác giả thực sự đã nghĩ qua vấn đề và đang dẫn người đọc đi qua quá trình hiểu đó, không phải cảm giác nhiều câu nghe có vẻ đúng đã được xếp cạnh nhau.

---

# 1. Phạm vi và thứ tự ưu tiên

Skill vận hành theo thứ tự ưu tiên sau:

1. **Đúng khoa học.** Không bịa fact, citation, số liệu, kết quả, experiment, theorem, benchmark hoặc trạng thái triển khai.
2. **Lập luận có thể bảo vệ.** Mọi kết luận quan trọng phải truy được về cơ chế, toán nền tối thiểu, evidence hoặc một giới hạn được nêu rõ.
3. **Không làm tri thức khó thêm.** Khi mở sâu, ưu tiên kiến thức Toán cao cấp, Đại số tuyến tính, Xác suất thống kê và ML/DL cơ bản mà sinh viên kỹ thuật thường đã học.
4. **Văn phong tiếng Việt tự nhiên.** Câu và đoạn phải liền ý, không mang nhịp template, không dịch song ngữ cơ học, không dùng modifier rỗng thay cho thông tin.
5. **Mạch dài xuyên chương.** Đơn vị biên tập không chỉ là câu hoặc đoạn riêng lẻ mà là đường dây lập luận kéo dài qua nhiều trang.
6. **An toàn tài liệu.** Khi làm việc với DOCX phải bảo toàn equation, citation field, bookmark, cross-reference, bảng, hình và cấu trúc Word được bảo vệ.
7. **Toán học phải đúng cả nghĩa lẫn hình thức.** Trong Word Master, mọi biểu thức toán học thực sự phải được tạo, sửa và bảo toàn bằng **OMML native của Microsoft Word**, đồng thời tuân theo quy ước ký hiệu và cách trình bày toán học đã được chuẩn hóa trong chính file Master.

Không có page-count gate. Độ dài do nội dung quyết định.

---

# 2. Các việc Skill này không được làm

Không được:

- tối ưu văn bản để né AI detector;
- tìm cách xóa, phá, che giấu hoặc làm sai lệch watermark, provenance, attribution hay nhãn AI bắt buộc;
- chèn lỗi ngữ pháp, lỗi đánh máy hoặc làm câu “ngẫu nhiên” để giả người;
- thay từ đồng nghĩa hàng loạt chỉ để làm giảm repetition score;
- randomize độ dài câu;
- tăng công thức chỉ để văn bản trông “khoa học hơn”;
- chèn LaTeX thô, chuỗi Unicode giả công thức, ảnh chụp công thức hoặc text mô phỏng toán học vào Word Master để thay cho OMML;
- tự ý đổi toàn cục quy ước vector, matrix, transpose, expectation, numbering, alignment hoặc typography toán học đã được Master thiết lập;
- tạo thêm audit infrastructure nếu không giúp trực tiếp cho việc đọc, hiểu, sửa và bảo vệ luận điểm;
- xây “gate của gate”, taxonomy của taxonomy hoặc rừng JSON chỉ để chứng minh quy trình đã phức tạp;
- viết lại đoạn đang tốt chỉ để tạo activity;
- biến mọi dấu hiệu bề mặt như “Tuy nhiên”, “Thứ nhất”, ngoặc đơn, bullet hoặc câu dài thành lỗi mặc định.

Nếu người dùng yêu cầu “dẹp mẫu thống kê của AI”, phải hiểu mục tiêu hợp lệ là loại bỏ sự lặp khuôn, nhịp câu đồng dạng, cấu trúc mass-produced và discourse pattern máy móc vì chất lượng đọc và tính tác giả. Không diễn giải thành detector evasion.

---

# 3. Mô hình nhận thức của người đọc

Đối tượng mặc định:

- giảng viên hoặc sinh viên an toàn thông tin;
- biết lập trình và ML cơ bản;
- đã học Giải tích, Đại số tuyến tính, Xác suất thống kê ở mức đại học;
- không mặc định biết sâu representation learning, self-supervised learning, temporal GNN, provenance graph, privacy attack hoặc các chi tiết chuyên ngành hẹp.

Từ đó hình thành **knowledge contract**:

- không giải thích lại kiến thức quá sơ đẳng nếu nó không giúp lập luận;
- không dùng kiến thức nâng cao hơn để định nghĩa kiến thức đang cần giải thích;
- khi gặp một bước nhảy khái niệm, ưu tiên lùi xuống tầng toán hoặc ML căn bản đủ gần với người đọc;
- nếu một khái niệm đã được giải thích rõ ở trước, lần sau chỉ nhắc đủ để nối mạch, không dạy lại từ đầu.

Mục tiêu là tạo một **knowledge gradient** mượt: mỗi đoạn chỉ yêu cầu một bước nhảy vừa phải.

---

# 4. Chuỗi suy luận Basic-First

Với mỗi technical claim quan trọng, Agent phải tự kiểm tra chuỗi nội bộ sau:

```text
VẤN ĐỀ
→ ĐỊNH NGHĨA
→ CƠ CHẾ
→ TOÁN TỐI THIỂU
→ HỆ QUẢ
→ EVIDENCE
→ GIỚI HẠN
```

Đây là mô hình suy nghĩ nội bộ, không phải template phải in nguyên dạng trong luận văn.

## 4.1. Vấn đề

Trước khi giới thiệu một kỹ thuật, phải trả lời: tại sao kỹ thuật này xuất hiện ở đây?

Không viết:

> Transformer được sử dụng để trích xuất đặc trưng chuỗi.

Mà phải cho người đọc thấy vấn đề trước:

> Khi quan hệ giữa hai sự kiện cách xa nhau trong chuỗi phải được truyền qua nhiều trạng thái hồi quy liên tiếp, tín hiệu có thể khó duy trì đầy đủ. Cơ chế attention xử lý một cấu trúc tương tác khác: mỗi vị trí có thể tính trọng số trực tiếp với các vị trí khác trong cửa sổ quan sát.

## 4.2. Định nghĩa

Định nghĩa bằng khái niệm đã biết hơn.

Không định nghĩa “representation” bằng một chuỗi từ trừu tượng hơn như “không gian tiềm ẩn đa chiều có tính phân biệt ngữ nghĩa”.

Tốt hơn:

> Representation là vector mà mô hình tạo ra từ dữ liệu đầu vào để các bước sau có thể so sánh, phân loại hoặc suy luận trên dữ liệu đó.

## 4.3. Cơ chế

Đây là phần bắt buộc phải có nếu claim có tính nhân quả kiểu “vì X nên Y”.

Hỏi:

- cái gì được biến đổi?
- phép biến đổi nào xảy ra?
- thành phần nào trong cơ chế gây ra hiệu ứng đang nói?

## 4.4. Toán tối thiểu

Chỉ dùng toán khi toán đóng được một reasoning gap.

Một công thức không được xuất hiện chỉ vì chủ đề có công thức.

## 4.5. Hệ quả

Từ cơ chế mới suy ra hệ quả.

Nếu hệ quả là định tính, nói rõ điều kiện.

## 4.6. Evidence

Phân biệt rõ:

- evidence từ literature;
- evidence từ code/config;
- evidence từ experiment;
- evidence từ derivation;
- interpretation của tác giả.

## 4.7. Giới hạn

Mỗi claim mạnh cần biết nó **không chứng minh điều gì**.

Ví dụ:

- loss giảm không chứng minh downstream detection tốt;
- VRAM thấp không chứng minh SOC-ready;
- cosine similarity cao không chứng minh semantic equivalence;
- covariance penalty nhỏ không chứng minh statistical independence;
- provenance dependency không đồng nghĩa causality;
- temporal encoding không đồng nghĩa causal understanding;
- vài seed ổn định không chứng minh drift robustness.

---

# 5. Scientific truth states

Agent phải luôn biết mình đang viết loại phát biểu nào. Không cần tạo file JSON nếu không cần. Chỉ cần giữ trạng thái nhận thức rõ ràng.

Các trạng thái chính:

- **LITERATURE_FACT**: paper/standard/source ngoài nói trực tiếp.
- **MATHEMATICAL_DERIVATION**: suy ra từ định nghĩa hoặc công thức.
- **AUTHOR_SYNTHESIS**: tác giả nối nhiều nguồn thành một cách hiểu.
- **AUTHOR_PROPOSAL**: kiến trúc, quy tắc, giả thuyết hoặc thiết kế do chuyên đề đề xuất.
- **IMPLEMENTATION_FACT**: code/config/artifact cho thấy hệ thống đã làm điều đó.
- **OBSERVED_RESULT**: kết quả đo được từ experiment.
- **INTERPRETATION**: cách tác giả giải thích một quan sát.
- **ASSUMPTION**: giả định được dùng trong mô hình hoặc phân tích.
- **LIMITATION**: điều dữ liệu hoặc phương pháp hiện tại chưa cho phép kết luận.

Không được làm mờ ranh giới giữa các trạng thái.

Các lỗi điển hình:

```text
AUTHOR_PROPOSAL → viết như IMPLEMENTATION_FACT
IMPLEMENTATION_FACT → viết như OBSERVED_RESULT
OBSERVED_RESULT → viết như general scientific truth
OPTIMIZATION_OBJECTIVE → viết như downstream evidence
CORRELATION/DEPENDENCY → viết như causality
```

Nếu không xác định được trạng thái của claim, Agent phải dừng và kiểm tra nguồn thay vì “viết đẹp” câu đó.

---

# 6. Mathematical grounding ladder

Mục tiêu không phải biến luận văn thành giáo trình Toán. Toán là cầu nối để làm rõ WHY.

Nguyên tắc:

> Chỉ mở đến tầng toán thấp nhất đủ để giải thích cơ chế đang cần.

## 6.1. Hàm, đạo hàm, gradient, chain rule

Dùng khi cần giải thích:

- optimization;
- sensitivity;
- backpropagation;
- gradient-based learning;
- vì sao tham số được cập nhật theo loss.

Cầu nối tối thiểu:

\[
\theta_{t+1}=\theta_t-\eta\nabla_\theta \mathcal L
\]

Agent phải nói được:

- \(\theta_t\): tham số hiện tại;
- \(\nabla_\theta\mathcal L\): hướng tăng nhanh nhất cục bộ của loss trong không gian tham số;
- dấu trừ: đi theo hướng giảm cục bộ;
- \(\eta\): kích thước bước cập nhật.

Không được suy ra:

- đã đạt global optimum;
- mô hình generalize tốt;
- representation đã “hiểu” dữ liệu.

Chain rule chỉ cần mở khi thật sự cần giải thích việc gradient truyền qua nhiều phép biến đổi.

## 6.2. Vector, norm, dot product, cosine

Dùng khi cần giải thích:

- embedding;
- similarity;
- attention score;
- representation geometry;
- linear probe.

Với dot product:

\[
q^\top k=\|q\|\,\|k\|\cos\theta
\]

Hệ quả quan trọng:

- dot product phụ thuộc cả hướng và độ lớn;
- cosine similarity loại ảnh hưởng trực tiếp của magnitude bằng chuẩn hóa;
- cosine cao chỉ nói hai vector gần hướng nhau trong không gian biểu diễn hiện tại, không tự chứng minh hai đối tượng đồng nghĩa về mặt an ninh.

## 6.3. Projection và linear map

Dùng khi giải thích:

- PCA;
- linear probe;
- projection head;
- dimensionality reduction.

Một linear map biến vector đầu vào thành tổ hợp tuyến tính ở không gian mới. Projection chỉ giữ thành phần theo một hoặc một nhóm hướng nhất định.

Không viết “projection trích xuất đặc trưng quan trọng” nếu chưa nói tiêu chí “quan trọng” là gì.

## 6.4. Eigenvalue, eigenvector, PCA và SVD intuition

PCA nên được giải thích từ covariance và phép chiếu.

Với vector đơn vị \(v\), phương sai của dữ liệu sau chiếu lên \(v\) là:

\[
v^\top \Sigma v.
\]

PCA chọn các hướng làm đại lượng này lớn theo ràng buộc trực giao. Eigenvector ứng với eigenvalue lớn đại diện cho hướng có phương sai lớn hơn.

Phải khóa giới hạn:

> Phương sai lớn không mặc nhiên đồng nghĩa chứa tín hiệu an ninh tốt nhất.

SVD chỉ mở nếu nó giúp hiểu factorization hoặc mối liên hệ với PCA. Không thêm SVD chỉ vì PCA “nên có SVD”.

## 6.5. Xác suất có điều kiện và Bayes

Dùng khi cần phân biệt:

- \(P(A)\) và \(P(A\mid B)\);
- prior, likelihood, posterior;
- một event hiếm với một event đáng ngờ dưới điều kiện cụ thể.

Không dùng Bayes như ornament.

Nếu luận điểm chỉ cần nói “xác suất của hành vi thay đổi khi biết thêm bối cảnh”, conditional probability đủ.

## 6.6. Expectation, variance, covariance

Expectation là trung bình lý thuyết theo phân phối.

Variance đo mức độ phân tán quanh expectation.

Covariance mô tả việc hai đại lượng có xu hướng biến động cùng nhau theo quan hệ tuyến tính.

Không được suy ra:

- covariance bằng 0 ⇒ independence;
- variance thấp ⇒ robustness toàn diện;
- một seed lệch ⇒ optimizer failure.

## 6.7. Entropy, cross-entropy, KL divergence

Entropy:

\[
H(p)=-\sum_i p_i\log p_i.
\]

Đọc từ hành vi của phân phối:

- phân phối tập trung vào ít trạng thái ⇒ entropy thấp hơn;
- xác suất trải đều hơn ⇒ entropy cao hơn.

Không được nhảy sang:

> entropy cao là tấn công.

Entropy đo bất định/phân tán của phân phối. Security semantics cần một cầu nối khác.

Với one-hot target, cross-entropy thường rút về:

\[
\mathcal L=-\log p_\theta(y\mid x).
\]

Khi xác suất mô hình gán cho target tăng, loss giảm. Điều đó giải thích objective đang khuyến khích điều gì trên dữ liệu huấn luyện.

Không được suy ra:

- calibration tốt;
- robustness tốt;
- test performance tốt;
- representation tốt ở mọi downstream task.

KL divergence chỉ giải thích khi thật sự có hai phân phối cần so sánh.

## 6.8. Sampling, estimator, bias, variance, uncertainty

Khi báo cáo kết quả qua vài seed hoặc vài sample, Agent phải phân biệt:

- sample statistic;
- population quantity;
- estimator;
- uncertainty do sampling hoặc initialization.

Không dùng vài seed để tuyên bố “ổn định tuyệt đối”.

Nếu không có đủ sample cho một khoảng tin cậy có ý nghĩa, nói trực tiếp rằng bằng chứng hiện tại chỉ phản ánh các run đã quan sát.

## 6.9. Optimization objective và scientific evidence

Một objective trả lời:

> mô hình được khuyến khích tối ưu điều gì?

Nó không tự trả lời:

> representation có hữu ích downstream không?

Ví dụ:

- masked prediction loss thấp ⇒ mô hình làm tốt hơn objective masked prediction trên data đang đo;
- VICReg covariance penalty thấp ⇒ các chiều representation ít đồng biến tuyến tính hơn theo penalty đó;
- alignment loss thấp ⇒ hai view gần nhau hơn theo metric objective dùng.

Các điều trên chưa đủ để kết luận detection, causality, privacy hoặc robustness.

---

# 7. Formula reasoning + OMML rendering protocol

Skill phải giữ đồng thời hai lớp: **ý nghĩa toán học** và **biểu diễn toán học native trong Word**. Một công thức đúng về nội dung nhưng được chèn sai kiểu vào Word Master vẫn là một lỗi biên tập. Ngược lại, một phương trình OMML đẹp nhưng không đóng vai trò trong lập luận chỉ là *proof theater*.

## 7.1. Lớp reasoning: công thức phải được “đọc”

Mọi công thức quan trọng phải được giải thích bằng bốn bước, nhưng bốn bước này là logic biên tập, không phải template cố định phải in ra.

**Trước công thức:** nói câu hỏi hoặc quan hệ mà công thức đang giải quyết.

**Trong công thức:** chỉ định nghĩa các ký hiệu thiết yếu và những đại lượng mà người đọc chưa biết.

**Sau công thức:** giải thích biến nào tác động đến kết quả, chiều tác động ra sao và vì sao cơ chế toán học đó liên quan tới luận điểm.

**Khóa phạm vi:** nói rõ công thức hoặc objective chưa chứng minh được điều gì.

Ví dụ với attention, dạng khái niệm có thể được biểu diễn trong file Skill bằng ký pháp TeX cho dễ đọc:

\[
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
\]

Diễn giải đúng hướng:

- \(QK^\top\) tạo score giữa query và key;
- chia \(\sqrt{d_k}\) kiểm soát thang của dot product;
- softmax chuyển score thành trọng số chuẩn hóa;
- nhân với \(V\) tạo weighted aggregation;
- từ đó mỗi vị trí có thể lấy thông tin trực tiếp từ vị trí khác trong cửa sổ.

Giới hạn:

- attention score không phải causal relation;
- self-attention không tự sinh topology process-file-socket nếu input không biểu diễn topology đó;
- attention không tự hiểu security semantics.

**Quan trọng:** ký pháp TeX trong file Skill chỉ là cách mô tả logic cho Agent. Khi áp dụng vào **Word Master**, công thức tương ứng phải được tạo hoặc chỉnh bằng **OMML**, không được dán nguyên chuỗi `\frac`, `^`, `_`, `\operatorname`, ký tự Unicode ghép thủ công hoặc ảnh công thức vào thân tài liệu.

## 7.2. Word Master là authority về trình bày toán học

Trước khi thêm hoặc sửa một biểu thức, Agent phải quan sát các công thức lân cận và các phương trình cùng loại trong Master để xác định quy ước hiện hành. **Master hiện tại là nguồn chuẩn cao nhất về typography và notation**, không phải mặc định cá nhân của Agent.

Phải giữ nhất quán tối thiểu các yếu tố sau nếu Master đã quy định:

- inline equation hay display equation;
- căn giữa/căn lề và khoảng cách trước sau phương trình;
- cách đánh số phương trình và cross-reference;
- quy ước scalar, vector, matrix, tensor và index;
- ký hiệu transpose, norm, inner product, expectation, probability, covariance, gradient và đạo hàm;
- tên hàm/toán tử như `log`, `exp`, `softmax`, `diag`, `tr`, `argmin`;
- cách viết subscript/superscript, dấu ngoặc co giãn, phân số, căn, tổng, tích, matrix và piecewise expression;
- dấu câu khi phương trình là một thành phần ngữ pháp của câu;
- font và style toán học mà Word Master đang sử dụng.

Không được tự ý “chuẩn hóa lại” toàn luận văn theo một convention mới chỉ vì Agent thích convention đó hơn. Nếu ký hiệu hiện hành có vấn đề khoa học thật sự, phải báo rõ và chỉ sửa khi nhiệm vụ cho phép thay đổi notation.

## 7.3. Native OMML only trong Master

Mọi biểu thức toán học thực sự trong DOCX Master phải ở dạng OMML native, điển hình là `m:oMath` cho inline math hoặc `m:oMathPara` cho display math. Các cấu trúc toán học phải dùng node OMML tương ứng thay vì giả lập bằng text khi chúng là thành phần của một phương trình:

- fraction → cấu trúc phân số OMML;
- superscript/subscript → cấu trúc script OMML;
- radical → radical OMML;
- matrix → matrix OMML;
- n-ary operators → cấu trúc tổng/tích/tích phân OMML;
- delimiter → delimiter OMML có khả năng co giãn;
- function/application → cấu trúc function phù hợp với Word Math.

Không được chuyển một phương trình OMML đang đúng thành plain text chỉ để rewrite paragraph. Không được “sửa nhanh” bằng cách gõ `x^2`, `a/b`, `sqrt(x)` hoặc `E[X]` ở body text nếu vị trí đó vốn là một biểu thức toán học chuẩn trong Master. Với biểu thức rất ngắn, cách inline hay plain prose phải tuân theo chính convention đã có trong Master.

## 7.4. Semantic notation invariants

Khi sửa prose quanh toán học, Agent phải coi notation là một phần của nghĩa, không chỉ là typography. Trước và sau patch phải giữ đúng:

- cùng biến chỉ cùng đại lượng;
- cùng subscript/superscript chỉ cùng index hoặc thời điểm;
- vector/matrix không bị hạ thành scalar hoặc ngược lại;
- transpose, inverse, norm, expectation và covariance không bị mất;
- miền, chiều và quan hệ input/output vẫn hợp lý;
- ký hiệu đã được định nghĩa ở trước không bị định nghĩa lại với nghĩa khác;
- equation number và cross-reference vẫn trỏ đúng phương trình.

Nếu prose mới yêu cầu đổi ký hiệu để dễ hiểu hơn nhưng notation đó đã được dùng xuyên chương, ưu tiên giữ notation hiện hành và cải thiện phần diễn giải thay vì đổi symbol cục bộ.

## 7.5. Formula placement và prose integration

Không để phương trình “rơi” vào giữa trang mà không có vai trò câu. Một phương trình display phải có câu dẫn trước và phần diễn giải sau nếu ý nghĩa chưa hiển nhiên. Tuy nhiên không cần giải nghĩa mọi ký hiệu phổ thông lặp đi lặp lại.

Khi công thức là một phần của câu, dấu câu và đoạn văn phải được xử lý như văn xuôi học thuật bình thường. Không dùng ngoặc đơn dài chỉ để chứa toàn bộ phần giải thích ký hiệu; ưu tiên một câu định nghĩa ngắn ngay sau công thức hoặc một mệnh đề nối tự nhiên.

Một công thức chỉ nên được đánh số nếu Master hoặc logic cross-reference cần số đó. Không phát sinh numbering mới cho mọi phép biến đổi ngắn.

## 7.6. Editing safety cho OMML

Nếu paragraph chứa OMML hoặc field được bảo vệ:

- không dùng `paragraph.text = ...`;
- không serialize lại toàn paragraph theo plain text;
- không phá run boundaries chứa equation/field/bookmark;
- chỉ patch các node text an toàn hoặc chỉnh chính OMML bằng API/node-level phù hợp;
- nếu dùng Word COM, ưu tiên Word Math/OMath object model cho thao tác phương trình;
- nếu dùng OpenXML, phải bảo toàn namespace, cấu trúc `m:*` và các node Word liên quan.

Nếu không thể thực hiện patch an toàn, **dừng và báo** thay vì thay phương trình bằng text.

## 7.7. Kiểm tra sau khi sửa toán học

Không coi “OMML node count không đổi” là đủ. Sau patch có chạm vào toán học, tối thiểu phải kiểm tra:

1. phương trình render đúng trong Word/PDF;
2. nội dung toán học đúng với intended formula;
3. không mất script, fraction, radical, delimiter, matrix hoặc operator;
4. equation number/cross-reference còn đúng;
5. notation trước và sau đoạn sửa nhất quán;
6. các phương trình không thuộc phạm vi sửa không bị thay đổi ngoài ý muốn.

Đây là một **safety rail ngắn nhưng bắt buộc**, không phải lý do để dựng thêm một hệ thống audit phức tạp.

---

# 8. Playbook Basic-First cho các chủ đề ML/DL thường gặp

Đây là hướng dẫn cách giải thích, không phải yêu cầu luận văn phải dạy lại toàn bộ lý thuyết.

## 8.1. Frequency / Event Count

Đi từ:

- đếm số lần event xuất hiện trong một cửa sổ;
- vector count biểu diễn cường độ xuất hiện;
- ưu điểm: đơn giản, dễ tính, giữ thông tin tần suất;
- mất mát: không biết thứ tự, khoảng cách thời gian, semantics và quan hệ thực thể.

## 8.2. TF-IDF

Đi từ:

- TF: mức xuất hiện cục bộ trong phiên/cửa sổ;
- IDF: giảm trọng số của event phổ biến trên nhiều cửa sổ;
- tích TF × IDF: event phổ biến cục bộ nhưng hiếm toàn cục có thể nhận trọng số tương đối lớn hơn;
- ý nghĩa: hỗ trợ làm nổi bật event đặc thù;
- giới hạn: **rare ≠ malicious**;
- không biết temporal order, causality hoặc semantics.

Không gộp Shannon entropy vào cùng cơ chế.

## 8.3. Shannon Entropy

Đi từ phân phối xác suất.

Entropy đo độ phân tán/bất định của phân phối. Chỉ sau đó mới nói nó có thể mô tả thay đổi mức đa dạng của event trong cửa sổ.

Không nói entropy “nhấn mạnh event hiếm”.

## 8.4. PCA

Đi từ covariance → projection variance → eigenvector.

Không viết “PCA tìm feature quan trọng” nếu chưa định nghĩa “quan trọng” là phương sai lớn.

Khóa giới hạn: variance lớn không nhất thiết là security-relevant.

## 8.5. RNN / LSTM

Đi từ recurrence:

- trạng thái hiện tại phụ thuộc input hiện tại và trạng thái trước;
- parameter được dùng lại qua time step;
- chuỗi dài tạo đường truyền gradient dài;
- LSTM thêm gate để kiểm soát dòng thông tin qua cell state.

Không viết LSTM “ghi nhớ dài hạn” như một khả năng tuyệt đối. Nói nó được thiết kế để giảm khó khăn của phụ thuộc dài so với recurrence đơn giản.

## 8.6. Transformer / Self-Attention

Đi từ vấn đề dependency xa → Q/K/V → direct interaction trong cửa sổ → positional encoding.

Nêu rõ giới hạn topology, causality, quadratic attention cost theo sequence length khi phù hợp.

## 8.7. Masked Prediction

Đi từ:

- che một phần input;
- mô hình dự đoán phần bị che từ context còn lại;
- objective khuyến khích representation giữ thông tin hữu ích cho reconstruction/prediction đó.

Không suy ra mô hình “hiểu an ninh” chỉ vì masked loss giảm.

## 8.8. Self-Supervised Learning

Giải thích là cách tạo supervisory signal từ cấu trúc dữ liệu thay vì yêu cầu label downstream thủ công.

Phải nói rõ pretext objective là gì và downstream relevance cần được kiểm tra riêng.

## 8.9. VICReg

Giải thích ba ý theo chức năng:

- invariance: kéo representation của hai view tương ứng gần nhau;
- variance: tránh mỗi chiều co về gần một hằng số;
- covariance: giảm tương quan tuyến tính dư thừa giữa các chiều.

Không viết covariance penalty chứng minh independence.

Không viết variance term tự chứng minh không collapse trong mọi điều kiện. Nó là một cơ chế chống collapse theo objective đã định nghĩa.

## 8.10. Provenance Graph

Đi từ đối tượng thực:

- node: process, file, socket, user hoặc entity thích hợp;
- edge: quan hệ/event tương tác;
- một record riêng lẻ thường không chứa đủ context của chuỗi hành vi;
- graph giữ quan hệ đa thực thể xuyên nhiều event.

Sau đó mới dẫn tới GNN.

## 8.11. Message Passing / GNN

Đi từ neighborhood aggregation:

- mỗi node nhận message từ neighbor;
- aggregate nhiều message;
- update representation;
- nhiều layer mở rộng phạm vi thông tin có thể ảnh hưởng node.

Có thể giải thích linear aggregation ở mức:

\[
h_v^{(l+1)}=\sigma\left(W_1h_v^{(l)}+W_2\operatorname{Agg}_{u\in\mathcal N(v)}h_u^{(l)}\right)
\]

Không cần dạy graph theory sâu nếu claim không cần.

## 8.12. Over-smoothing

Đi từ việc nhiều layer liên tục trộn representation của neighbor. Khi quá nhiều bước, node có thể trở nên khó phân biệt vì representation tiến gần nhau hơn.

## 8.13. Over-squashing

Đi từ:

- neighborhood mở rộng nhanh;
- nhiều tín hiệu từ xa phải đi qua số cạnh trung gian hữu hạn;
- cuối cùng chúng bị nén vào vector kích thước cố định;
- thông tin quan trọng có thể bị hòa lẫn hoặc suy giảm.

Không chỉ nêu tên hiện tượng.

## 8.14. Temporal Encoding

Đi từ Δt.

Hai event giống nhau nhưng cách nhau 10 ms và 10 giờ không nên mặc định được coi như cùng một quan hệ động.

Temporal encoding biến Δt thành feature để mô hình có thể học khác biệt nhịp độ.

Không viết time encoding “đo chính xác thời gian” nếu nó chỉ là learned representation.

## 8.15. Temporal GNN

Nối ba phần:

- graph structure;
- event order/time;
- state update theo sự kiện.

Phải nói rõ model nào dùng memory, temporal attention hay time encoding nếu literature cụ thể yêu cầu.

Không gom mọi temporal GNN thành cùng một cơ chế.

## 8.16. Frozen Linear Probe

Đi từ:

- encoder bị freeze;
- chỉ classifier tuyến tính được train;
- classifier không thể học lại representation;
- kết quả đo lượng thông tin có thể truy xuất tuyến tính từ z cho task đang xét.

Không được viết:

> phản ánh toàn bộ năng lực thật của representation.

Thông tin phi tuyến có thể tồn tại nhưng linear probe không khai thác hết.

## 8.17. Privacy concepts

Luôn tách:

- pseudonymization;
- anonymity;
- differential privacy;
- membership inference;
- model inversion;
- controlled linkability.

Pseudonymization không bằng differential privacy.

Hash không tự tạo anonymity.

Nếu MIA/model inversion chưa chạy, viết “đề xuất phép kiểm tra hạ nguồn” hoặc “chưa được thực hiện trong phạm vi hiện tại”, không viết như kết quả đã xác minh.

---

# 9. Anti-proof-theater

Toán chỉ được thêm nếu làm ít nhất một trong các việc sau:

- giải thích nguyên nhân;
- làm rõ trade-off;
- chỉ ra điều kiện;
- phân biệt hai khái niệm dễ nhập nhằng;
- giới hạn một kết luận;
- nối objective với behavior.

Nếu không, bỏ.

Agent phải phân biệt:

- mathematical identity;
- definition;
- modeling assumption;
- optimization objective;
- empirical observation;
- scientific conclusion.

Không được dùng một tầng để giả làm tầng khác.

Ví dụ:

> \(\mathcal L\) giảm qua epoch

chỉ là training observation.

Nó không phải proof rằng:

- representation tối ưu;
- detector tốt;
- generalization tốt;
- attack understanding tốt.

---

# 10. Claim → Evidence → Interpretation → Limit

Mỗi luận điểm quan trọng nên có đủ bốn lớp này, nhưng không cần viết thành bốn câu cứng.

## 10.1. Claim

Câu đang khẳng định điều gì?

## 10.2. Evidence

Nguồn nào cho phép nói điều đó?

## 10.3. Interpretation

Bằng chứng đó có ý nghĩa gì trong bài toán hiện tại?

## 10.4. Limit

Bằng chứng không cho phép suy ra điều gì?

Ví dụ:

```text
Observed:
VRAM peak dưới ngưỡng X trong cấu hình thí nghiệm.

Interpretation:
Cấu hình hiện tại chạy được trong budget GPU đã đặt.

Not justified:
Hệ thống đã sẵn sàng cho streaming SOC thực tế.
```

Muốn kết luận về SOC cần thêm latency, throughput, state growth, workload và điều kiện triển khai phù hợp.

---

# 11. Citation discipline

Citation ở cuối câu không mặc định hỗ trợ mọi mệnh đề trong câu.

Khi câu chứa nhiều factual atom:

1. xác định atom nào được source hỗ trợ;
2. tách hoặc hạ claim nếu cần;
3. không bịa citation bổ sung.

Khi research/verification được yêu cầu, kiểm tra theo ba tầng:

- source có tồn tại không;
- metadata có đúng không;
- source có thật sự support claim không.

Nhưng một vòng rewrite thông thường không cần dựng claim graph khổng lồ nếu văn bản và source mapping đã rõ.

Ưu tiên source:

1. paper gốc / standard / official documentation cho scientific fact;
2. publisher hoặc venue chính thức;
3. Tạp chí An toàn thông tin cho bối cảnh Việt Nam, ngôn ngữ chuyên ngành và case/domain framing;
4. secondary source chỉ khi primary không cần thiết hoặc không khả dụng.

Không dùng báo chí để thay cho paper gốc khi đang chứng minh theorem, exact algorithm hoặc benchmark.

---

# 12. Long-form argument spine

Một tài liệu dài không thể được sửa như tập hợp paragraph độc lập.

Agent phải theo dõi một đường dây lập luận xuyên section:

```text
PROBLEM
→ LIMITATION OF CURRENT APPROACH
→ DESIGN RESPONSE
→ IMPLEMENTATION / METHOD
→ EVIDENCE
→ INTERPRETATION
→ LIMITATION
→ NEXT QUESTION
```

Mỗi section phải trả lời hai câu:

1. Section này đang giải quyết câu hỏi nào?
2. Nó để lại đối tượng nào cho section tiếp theo?

Đây là **HANDOFF**.

Nếu paragraph kết thúc bằng một ý mà paragraph sau bỏ hoàn toàn và mở chủ đề mới như một mini-answer độc lập, đó là dấu hiệu reset-context.

## 12.1. Known → New

Ở cấp câu và đoạn:

- đầu câu thường nên bám vào đối tượng người đọc vừa gặp;
- phần mới được phát triển sau đó;
- điểm nhấn mới thường đặt ở vị trí tự nhiên cuối clause/câu.

Đây là nguyên tắc continuity, không phải luật cú pháp cứng.

## 12.2. Không reset context

Tránh chuỗi paragraph dạng:

```text
Đoạn 1: định nghĩa A hoàn chỉnh.
Đoạn 2: định nghĩa B từ đầu như không liên quan A.
Đoạn 3: định nghĩa C từ đầu.
```

Tốt hơn:

```text
A tạo ra hạn chế X.
X khiến B cần thiết.
B giải quyết Y nhưng để lại Z.
Z dẫn tới C.
```

## 12.3. Chương 1 → Chương 2 → Chương 3

Với luận văn kỹ thuật:

- Chương 1 nên tạo ra các vấn đề/giới hạn;
- Chương 2 phải có design response tương ứng;
- Chương 3 chỉ được tuyên bố đã trả lời điều gì nếu có phép đo tương ứng.

Không để literature gap, architecture và experiment trở thành ba tài liệu tách biệt.

---

# 13. Paragraph architecture

Không dùng một template duy nhất cho mọi đoạn.

Nhưng paragraph tốt thường có một trong các chức năng:

- đặt vấn đề;
- định nghĩa;
- giải thích cơ chế;
- so sánh;
- đưa evidence;
- giải thích evidence;
- nêu giới hạn;
- chuyển sang câu hỏi tiếp theo.

Nếu một paragraph cố làm đồng thời 5–6 chức năng, cân nhắc tách.

## 13.1. Một cách tổ chức tự nhiên

Ví dụ:

- câu đầu: bám vào vấn đề đã có;
- câu giữa: mở cơ chế hoặc bằng chứng;
- câu cuối: nêu hệ quả hoặc mở sang vấn đề kế.

Đây chỉ là heuristic, không được lặp y hệt trên hàng chục trang.

## 13.2. Sentence cadence theo chức năng

Nhịp câu thay đổi vì chức năng thay đổi:

- định nghĩa có thể ngắn;
- cơ chế có thể cần câu dài hơn;
- caveat thường nên gọn;
- câu chuyển đoạn chỉ cần đủ để mở vấn đề mới.

Không randomize độ dài câu để “giả người”.

---

# 14. Anti-AI-slop ở cấp nguyên nhân

Không blacklist token. Audit chức năng của cấu trúc.

Các dấu hiệu chỉ là **candidate signal**.

## 14.1. Stock opener / stock transition

Các cụm như:

- “Về mặt”;
- “Đáng chú ý là”;
- “Có thể thấy rằng”;
- “Trong bối cảnh”;
- “Bên cạnh đó”;
- “Đồng thời”;
- “Từ đó”;
- “Qua đó”;
- “Tuy nhiên”;

không sai tự thân.

Chỉ sửa khi chúng:

- lặp cluster;
- không mang quan hệ logic thật;
- đóng vai trò filler;
- tạo nhịp paragraph đồng dạng.

## 14.2. Synonym laundering

Không thay:

> “Về mặt”

bằng:

> “Xét trên phương diện”

rồi coi đó là humanization.

Nếu cấu trúc lập luận cũ là dở, phải viết lại quan hệ giữa các ý.

## 14.3. Triad / listicle cadence

Không mặc định mọi luận điểm thành bộ ba.

“Thứ nhất, thứ hai, thứ ba” chỉ dùng khi văn bản thật sự cam kết một tập mục song song.

Không dùng connector chỉ vì có ba paragraph liên tiếp.

Không bắt buộc in nghiêng connector.

## 14.4. Parallel syntax quá đều

Nếu nhiều câu liên tiếp cùng pattern:

```text
X giúp...
Y giúp...
Z giúp...
```

hãy xem đó có phản ánh logic song song thật không. Nếu không, restructure theo quan hệ nguyên nhân, đối lập hoặc tiếp nối.

## 14.5. Empty fluency

Flag khi cùng lúc có:

- strong/evaluative claim;
- low specificity;
- không có evidence anchor.

Ví dụ yếu:

> Phương pháp đề xuất mang lại khả năng biểu diễn toàn diện và hiệu quả cao trong môi trường thực tế.

Không “làm đẹp” câu này. Hạ claim hoặc yêu cầu evidence.

## 14.6. Inflated technical prose

Các từ như:

- toàn diện;
- chặt chẽ;
- tường minh;
- tuyệt đối;
- nghiêm ngặt;
- vững chắc;
- tối ưu;
- ưu việt;
- then chốt;

không bị cấm.

Nhưng nếu adjective đang làm thay việc của specification, bỏ adjective và nói cơ chế.

Nguyên tắc:

> **Show control, do not label control.**

Không viết:

> quy trình chống leakage nghiêm ngặt.

Tốt hơn:

> tokenizer và thống kê chuẩn hóa chỉ được fit trên Train; Validation và Test chỉ sử dụng trạng thái đã đóng băng.

## 14.7. Ownerless claim

Các câu kiểu:

> “Nghiên cứu cho thấy...”

> “Có thể khẳng định...”

> “Được đánh giá là...”

phải xác định chủ thể tri thức.

Ai cho thấy? Paper nào? Experiment nào? Hay đây chỉ là interpretation của tác giả?

---

# 15. Ngoặc đơn, tiếng Anh và song ngữ

Mỗi cặp ngoặc phải “trả tiền thuê chỗ”.

Giữ ngoặc khi nó phục vụ một chức năng rõ:

- acronym lần đầu;
- ký hiệu toán học;
- tên chuẩn cần đối chiếu;
- điều kiện kỹ thuật ngắn;
- cấu trúc toán học thực.

Không dùng ngoặc để nhét một “bản dịch mini” sau gần như mọi thuật ngữ.

## 15.1. First-occurrence policy mềm

Lần giới thiệu chính thức có thể viết:

> tấn công suy luận thành viên (Membership Inference Attack, MIA)

Lần sau ưu tiên:

> MIA

hoặc:

> tấn công suy luận thành viên.

Ngoại lệ: sang một chương cách rất xa hoặc thuật ngữ có nguy cơ nhập nhằng, có thể nhắc lại ngắn gọn nếu thật sự giúp người đọc.

Không biến first-occurrence thành hard gate tuyệt đối theo vị trí token.

## 15.2. Thuật ngữ cơ bản

Không cần chú thích tiếng Anh lặp cho các cụm mà độc giả mục tiêu đã quen:

- tập huấn luyện;
- tập xác thực;
- lô huấn luyện;
- nhúng;
- sai số bình phương trung bình;
- tên người dùng;
- tên máy chủ;
- nhật ký hệ thống.

## 15.3. Không đổi ngoặc thành một tật khác

Không cơ học đổi ngoặc thành:

- em dash;
- dấu hai chấm;
- dấu chấm phẩy liên tục.

Nếu ngoặc chứa một ý đủ quan trọng, hòa ý đó vào câu hoặc tách thành câu mới.

---

# 16. Dấu gạch ngang và typography

Không dùng em dash như thói quen chèn mệnh đề kiểu AI.

Dùng:

- en dash cho dải số/tham chiếu nếu chuẩn tài liệu yêu cầu;
- hyphen cho từ ghép tiếng Anh cố định;
- câu/mệnh đề bình thường cho phần giải thích.

Không biến quy tắc typography thành thước đo chất lượng khoa học.

---

# 17. Bold, bullet và cấu trúc danh sách

Không coi bullet là “văn AI”.

Giữ bullet khi semantics thật sự là danh sách:

- RQ;
- hypothesis;
- dataset split;
- configuration;
- thành phần loss;
- điều kiện control;
- checklist kỹ thuật.

Chuyển bullet thành prose khi bullet chỉ đang che hai hoặc ba đoạn narrative ngắn không có lý do liệt kê.

Không tạo hàng loạt nhãn in đậm đầu paragraph kiểu:

> **Vấn đề:**

> **Giải pháp:**

> **Ý nghĩa:**

trừ khi tài liệu thật sự là manual hoặc format yêu cầu.

---

# 18. Human Vietnamese academic prose

## 18.1. Động từ cụ thể hơn danh từ hóa

Ưu tiên:

> mô hình gộp thông tin từ node lân cận

hơn:

> quá trình thực hiện sự tổng hợp thông tin lân cận được tiến hành.

## 18.2. Chủ thể tri thức rõ

Ai đề xuất? Ai đo? Ai quan sát? Paper nào nói? Chuyên đề giả định gì?

## 18.3. Liên từ phải mang quan hệ thật

Dùng “Tuy nhiên” khi có contrast.

Dùng “Do đó” khi có inference.

Dùng “Mặt khác” khi đổi sang một khía cạnh song song hoặc đối lập.

Không rải connector để tạo cảm giác mạch lạc.

## 18.4. Không dịch từng cụm từ từ tiếng Anh

Văn bản cuối phải đọc như người Việt viết trực tiếp bằng tiếng Việt.

Tránh chuỗi:

> thuật ngữ Việt (English Term), khái niệm Việt khác (Another Term), cơ chế Việt (Mechanism)...

kéo dài suốt nhiều trang.

## 18.5. Không ép cấu trúc báo chí vào luận văn

Có thể học từ Tạp chí An toàn thông tin cách:

- mở từ vấn đề thực;
- đưa cơ chế sau nhu cầu;
- chuyển từ nền tảng sang hệ quả an ninh;
- dùng ví dụ domain cụ thể;
- giữ câu tiếng Việt dễ đọc.

Nhưng không sao chép máy móc:

- tiêu đề báo chí;
- nhịp liệt kê của bài phổ biến kiến thức;
- cách dẫn nhập mang tính tin tức;
- kết cấu rút gọn phục vụ độc giả đại chúng.

Luận văn vẫn cần traceability, methodology và epistemic restraint cao hơn.

---

# 19. Scientific restraint

Agent phải tự hỏi với mọi kết luận mạnh:

> Phép đo này thực sự cho phép kết luận đến đâu?

Các khóa suy luận bắt buộc:

```text
training loss ↓
≠ downstream quality proven

VRAM low
≠ deployment readiness proven

seed consistency
≠ concept-drift robustness proven

attention weight
≠ causality

provenance edge
≠ causal mechanism

alignment objective ↓
≠ semantic equivalence proven

pseudonymization
≠ anonymity

covariance penalty ↓
≠ independence proven

rare event
≠ malicious event
```

Khi evidence yếu hơn prose, sửa prose. Không phát minh evidence.

---

# 20. Experimental prose

Mỗi đoạn kết quả nên phân biệt:

- what was measured;
- what was observed;
- interpretation;
- uncertainty;
- what remains untested.

Không biến phần Results thành Discussion trộn lẫn nếu cấu trúc luận văn không cho phép.

Không giải thích nguyên nhân sâu nếu dữ liệu không đủ.

Ví dụ tốt:

> Seed 42 cho trajectory khác các seed còn lại. Dữ liệu hiện tại chưa đủ để xác định nguyên nhân nội tại; kết quả vì vậy được giữ như một quan sát thay vì quy kết cho một failure mode cụ thể.

Đây là epistemic strength, không phải “thiếu tự tin”.

---

# 21. Conclusion discipline

Kết luận không phải mục lục viết lại.

Ưu tiên đường dây:

```text
Research problem
→ methodological response
→ what was implemented
→ what was observed
→ what can be concluded
→ what remains untested
```

Không dùng ba đoạn “Về mặt khảo sát / Về mặt phương pháp / Về mặt thực nghiệm” chỉ vì luận văn có ba chương.

Không biến future work thành thành tựu hiện tại.

---

# 22. Execution protocol cho Agent

## Pass 1. Read for argument

Đọc section hiện tại cùng section trước và sau.

Xác định:

- người đọc đã biết gì;
- section đang giải quyết vấn đề gì;
- reasoning jump nằm ở đâu;
- section sẽ handoff gì cho phần sau.

## Pass 2. Scientific state

Với các claim quan trọng, xác định chúng là literature fact, derivation, proposal, implementation, observation, interpretation hay limitation.

Nếu trạng thái mơ hồ, kiểm tra trước khi rewrite.

## Pass 3. Basic-first gaps

Tìm những câu nhảy từ tên kỹ thuật sang kết luận.

Bổ sung cơ chế và toán nền tối thiểu cần thiết.

Không giải thích lại mọi kiến thức phổ thông.

## Pass 4. Evidence restraint

So strength của claim với strength của evidence.

Hạ overclaim nếu cần.

## Pass 5. Long-form coherence

Kiểm tra paragraph handoff, known→new, chủ thể xuyên đoạn, continuity của terminology và argumentative spine.

## Pass 6. Human Vietnamese prose

Sửa:

- template cadence;
- stock opener cluster;
- repeated syntax;
- parenthesis debt;
- bilingual annotation debt;
- empty modifier;
- ownerless claim;
- listicle rhythm.

Không randomize.

## Pass 7. Surface cleanup

Cuối cùng mới xử lý:

- dấu câu;
- ngoặc;
- dash;
- bold;
- spacing;
- typography.

Không đảo thứ tự style trước science.

---

# 23. Khi cần tra cứu Internet

Tra cứu khi:

- claim ngoài tài liệu cần xác minh;
- citation support chưa rõ;
- thuật toán, paper, standard hoặc benchmark cần kiểm chứng;
- cần bối cảnh Việt Nam hoặc cách dùng thuật ngữ chuyên ngành.

Nguồn ưu tiên:

1. primary paper / standard / official docs;
2. publisher/venue chính thức;
3. Tạp chí An toàn thông tin cho framing Việt Nam và diễn ngôn chuyên ngành;
4. nguồn thứ cấp uy tín.

Không dùng một bài phổ biến kiến thức để thay thế paper gốc khi paper gốc là bằng chứng cần thiết.

---

# 24. DOCX + OMML safety rail

Khi chỉnh DOCX Master:

- bảo toàn OMML và **tiếp tục dùng OMML cho mọi biểu thức toán học mới hoặc biểu thức được sửa**;
- coi quy ước toán học đã chuẩn hóa trong Master là authority về notation và presentation;
- bảo toàn dynamic citation fields;
- bảo toàn bookmarks;
- bảo toàn cross-reference, đặc biệt cross-reference tới phương trình;
- bảo toàn hyperlink/drawing;
- bảo toàn caption, numbering, styles, table structure và figure anchor.

Không dùng `paragraph.text = rewritten` trên paragraph có field, OMML, bookmark, hyperlink hoặc protected nodes. Không thay OMML bằng raw LaTeX, Unicode pseudo-math, ảnh công thức hoặc plain-text approximation.

Nếu phải sửa chính phương trình, patch bằng Word OMath/OMML ở mức node/object phù hợp và kiểm tra render sau sửa. Nếu không thể sửa an toàn tại node-level, dừng và báo rõ thay vì phá cấu trúc Word.

DOCX/OMML safety là safety rail bắt buộc, nhưng không được biến thành audit bureaucracy. Mục tiêu là giữ Master vừa đúng khoa học, vừa đúng Word-native math, vừa nhất quán về typography.

---

# 25. Definition of Done

Một vòng biên tập được coi là đạt khi người đọc có thể trả lời phần lớn các câu sau mà không phải tự lấp khoảng trống:

- Tôi hiểu vì sao kỹ thuật này xuất hiện ở đây không?
- Tôi hiểu cơ chế làm nó tạo ra hệ quả đang nêu không?
- Nếu có công thức, tôi hiểu công thức đang trả lời câu hỏi gì không?
- Trong Word Master, công thức đó có còn là OMML native và đúng convention toán học hiện hành không?
- Toán có giúp làm rõ WHY hay chỉ để trang trí?
- Claim này đến từ literature, design hay experiment?
- Bằng chứng có đủ mạnh cho kết luận không?
- Tác giả có nói rõ điều chưa chứng minh được không?
- Paragraph này có nối tự nhiên từ paragraph trước và mở được paragraph sau không?
- Sau 3–5 trang, tôi có còn cảm giác cùng một người đang phát triển một lập luận không?
- Thuật ngữ song ngữ có bị lặp không cần thiết không?
- Ngoặc đơn có quá dày không?
- Connector có quan hệ logic thật không?
- Có modifier nào đang che sự thiếu specificity không?
- Có câu nào nghe rất khoa học nhưng không nói được điều gì kiểm chứng được không?
- Có đoạn nào đang giống mini-answer độc lập và reset context không?

Không dùng AI detector score làm Definition of Done.

---

# 26. Output contract

Khi áp dụng skill để biên tập tài liệu, Agent nên báo cáo ngắn:

```text
SECTIONS_REVIEWED
BASIC_FIRST_GAPS_FIXED
MATHEMATICAL_BRIDGES_ADDED
OVERCLAIMS_NARROWED
LONG_FORM_HANDOFFS_REPAIRED
PARENTHETICAL_REWRITES
REPEATED_ENGLISH_ANNOTATIONS_REMOVED
UNRESOLVED_SCIENTIFIC_ISSUES
```

Có thể đưa một số ví dụ before/after quan trọng, nhưng không biến báo cáo thành forensic dump.

Nếu không còn blocker thật, không tự phát minh thêm round.

---

# 27. Một số anti-pattern và cách xử lý

## 27.1. “Kỹ thuật X giúp mô hình hiểu...”

Hỏi “hiểu” nghĩa là gì trong phép đo?

Nếu không có operational definition, thay bằng hành vi cụ thể:

> representation giữ thông tin cần cho objective X;

hoặc:

> mô hình sử dụng context từ các vị trí khác để dự đoán token bị che.

## 27.2. “Bảo đảm”

Chỉ dùng khi có proof hoặc control đúng nghĩa đủ mạnh.

Nếu chỉ là design intent:

- “được thiết kế để”;
- “nhằm”;
- “giảm nguy cơ”;
- “hạn chế”;
- “khuyến khích”.

## 27.3. “Tối ưu”

Nếu không có benchmark/comparison, tránh dùng như superiority claim.

Nói hành vi quan sát được:

> projection head không được nạp ở inference, vì vậy số thành phần cần giữ lại nhỏ hơn so với giai đoạn pretraining.

## 27.4. “Toàn diện”

Nếu không định nghĩa coverage, bỏ.

## 27.5. “Rõ ràng”, “hiển nhiên”

Nếu người đọc cần reasoning, đừng dùng những từ này để bỏ qua reasoning.

## 27.6. “Nghiên cứu cho thấy”

Gọi tên source hoặc evidence.

---

# 28. Worked micro-example principle

Khi một bước toán là chìa khóa của claim, dùng một derivation nhỏ đủ đóng gap thay vì chỉ gọi tên công thức.

Ví dụ với TF-IDF:

\[
\operatorname{tfidf}(e,d)
=
\operatorname{tf}(e,d)
\log\frac{N}{\operatorname{df}(e)}.
\]

Từ đó mở đúng ba mắt xích:

1. TF tăng khi event xuất hiện nhiều trong cửa sổ hiện tại.
2. IDF giảm khi event xuất hiện ở nhiều cửa sổ toàn tập.
3. Vì vậy event phổ biến cục bộ nhưng hiếm toàn cục có thể nhận trọng số lớn hơn.

Khóa phạm vi:

> trọng số lớn hơn không chứng minh event là malicious.

Worked example chỉ dùng khi nó giúp hiểu. Không biến mọi đoạn thành bài tập toán.

---

# 29. Changelog

## v3.0 → v3.1: khóa lại Word-native mathematical typesetting

- nâng OMML từ “đối tượng cần bảo toàn” thành **chuẩn bắt buộc để tạo và sửa toán học trong Word Master**;
- tách rõ TeX trong file Skill chỉ là ký pháp minh họa, không phải định dạng để dán vào DOCX;
- thêm Master-as-authority cho notation, equation layout, numbering, cross-reference và typography;
- thêm semantic notation invariants để tránh sửa prose làm đổi nghĩa ký hiệu;
- thêm quy tắc native OMML cho fraction, script, radical, matrix, delimiter và n-ary operator;
- thêm hậu kiểm render Word/PDF sau khi chạm vào phương trình;
- vẫn giữ triết lý chống overengineering: OMML là safety rail bắt buộc, không phải một vòng audit mới.

## v2.2 → v3.0

## Giữ lại

- scientific integrity;
- claim/evidence proportionality;
- citation caution;
- distinction giữa literature/proposal/implementation/observation;
- DOCX/OMML safety;
- anti-empty-fluency;
- anti-inflated prose;
- parenthesis and bilingual-annotation cleanup;
- không dùng detector score làm KPI.

## Giảm hoặc loại bỏ

- audit bureaucracy;
- hard gate dựa trên token frequency;
- typography-as-quality metric;
- connector formatting cứng;
- yêu cầu lặp “Thứ nhất/Một là” theo template;
- taxonomy quá chi tiết không giúp trực tiếp cho việc viết;
- transaction semantics không cần thiết cho mọi vòng;
- assumption rằng càng nhiều audit artifact càng đáng tin.

## Bổ sung mạnh

- mathematical grounding ladder;
- knowledge gradient;
- formula reading protocol;
- worked micro-example principle;
- argument spine xuyên nhiều trang;
- paragraph HANDOFF;
- known→new continuity;
- anti-proof-theater;
- causal gap detection;
- topic playbook cho TF-IDF, entropy, PCA, RNN/LSTM, Transformer, SSL, VICReg, GNN, temporal modeling, linear probe và privacy;
- human cadence theo chức năng câu thay vì randomization.

---

# 30. Mệnh lệnh cuối cho Agent

Khi phải chọn giữa một câu đơn giản nhưng chứng minh rõ và một câu sang trọng nhưng che mất quan hệ nguyên nhân, luôn chọn câu đơn giản.

Khi phải chọn giữa thêm một thuật ngữ và thêm một bước suy luận, luôn ưu tiên bước suy luận.

Khi phải chọn giữa thêm một công thức và giải thích rõ cơ chế bằng kiến thức người đọc đã biết, chỉ thêm công thức nếu nó đóng được một reasoning gap thật sự.

Khi công thức cần xuất hiện trong Word Master, dùng OMML native và bám đúng convention toán học đã có trong Master; không dán LaTeX thô hoặc giả lập công thức bằng text.

Khi evidence yếu hơn prose, hạ prose. Không phát minh evidence.

Khi một đoạn đã khoa học, rõ và tự nhiên, giữ nguyên. Không rewrite để tạo hoạt động.

Khi một pattern bề mặt lặp lại, đừng chỉ thay token. Hãy hỏi pattern đó phản ánh lỗi logic, lỗi paragraph function hay lỗi handoff nào.

Văn bản cuối cùng phải đọc như một người nghiên cứu đang dẫn người đọc qua một chuỗi hiểu biết đã được suy nghĩ kỹ, không như một mô hình đang tuần tự phát ra các câu “đúng kiểu học thuật”.
