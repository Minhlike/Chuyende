# ATTT WARRANTED-DERIVATION SCIENTIFIC WRITING SKILL v4.0

## Mục đích

Skill này dùng để biên tập, viết lại và kiểm tra báo cáo, chuyên đề, luận văn và tài liệu nghiên cứu khoa học bằng tiếng Việt trong các chủ đề an toàn thông tin, machine learning, deep learning, phân tích log, học biểu diễn, đồ thị, temporal learning, quyền riêng tư và các lĩnh vực kỹ thuật liên quan.

v4 kế thừa toàn bộ tinh thần đúng của v3.1 nhưng chuyển trọng tâm từ:

> claim có evidence

sang:

> claim có evidence, có warrant giải thích vì sao evidence hoặc cơ chế đó cho phép đi đến claim, có phạm vi đo lường rõ ràng, và có giới hạn suy luận tương xứng.

Ba nguyên tắc trung tâm của v4:

> **Depth by derivation, not by jargon.**

> **Trust by warrant, not by citation density.**

> **Clarity by reader state, not by sentence simplification alone.**

Mục tiêu cuối cùng là tạo một văn bản mà người đọc có thể trả lời được bốn câu hỏi:

1. Tác giả đang muốn tôi chấp nhận điều gì?
2. Vì sao điều đó hợp lý về mặt cơ chế hoặc toán học?
3. Bằng chứng nào thực sự hỗ trợ nó?
4. Bằng chứng đó cho phép kết luận đến đâu và chưa cho phép kết luận điều gì?

Skill không nhằm biến luận văn thành giáo trình, không nhằm làm mọi đoạn đều dài hơn, và không coi số lượng công thức, citation hoặc thuật ngữ là đại diện cho chiều sâu.

---

# 1. Thứ tự ưu tiên

Khi có xung đột, ưu tiên theo thứ tự:

1. **Đúng khoa học.**
2. **Claim có thể bảo vệ bằng warrant, derivation hoặc evidence phù hợp.**
3. **Metric đo đúng thứ cần đo và claim không vượt quá metric.**
4. **Không làm kiến thức khó thêm cho người đọc mục tiêu.**
5. **Mạch lập luận dài xuyên câu, đoạn, mục và chương.**
6. **Văn phong tiếng Việt tự nhiên, có tác giả, không mang nhịp sản xuất hàng loạt.**
7. **Toán học đúng cả nghĩa, ký hiệu và hình thức Word-native.**
8. **An toàn cấu trúc DOCX, OMML, citation field, cross-reference, bảng, hình và numbering.**

Không có page-count gate.

Không có mục tiêu “càng nhiều formalism càng tốt”.

Không có mục tiêu “càng ngắn càng tốt”.

Độ dài chỉ được quyết định bởi lượng reasoning cần thiết để người đọc theo được lập luận.

---

# 2. Những việc v4 tuyệt đối không làm

Không được:

- bịa fact, citation, benchmark, số liệu, kết quả, theorem, experiment hoặc trạng thái triển khai;
- dùng citation để che một reasoning gap;
- thêm công thức chỉ để tăng cảm giác khoa học;
- mở một chứng minh toán học dài khi một derivation ngắn đã đủ trả lời WHY;
- dùng thuật ngữ nâng cao hơn để giải thích một khái niệm đơn giản hơn;
- coi một optimization objective là bằng chứng downstream;
- coi một metric là chính construct mà metric đang đại diện;
- coi correlation, temporal order, graph dependency hoặc attention weight là causal effect;
- coi vài random seed ổn định là drift robustness;
- coi memory footprint thấp là deployment feasibility;
- coi pseudonymization là anonymity;
- coi covariance gần 0 là statistical independence;
- coi linear probe tốt là representation “chứa toàn bộ thông tin cần thiết”;
- coi ablation drop là chứng minh duy nhất về cơ chế;
- randomize độ dài câu để “trông giống người”;
- thay từ đồng nghĩa hàng loạt để giảm repetition score;
- tối ưu để né AI detector;
- xóa hoặc phá watermark, provenance, attribution hoặc nhãn bắt buộc;
- tạo thêm audit framework, scanner, gate, JSON taxonomy hoặc “gate của gate” nếu không giải quyết trực tiếp một vấn đề khoa học hay tài liệu cụ thể;
- viết lại đoạn đang tốt chỉ để tạo activity;
- global-normalize ký hiệu toán học theo sở thích của Agent;
- chèn LaTeX thô, Unicode giả công thức hoặc ảnh công thức vào Word Master thay cho OMML.

Nếu người dùng yêu cầu loại bỏ “mẫu AI”, mục tiêu hợp lệ là sửa sự đồng dạng trong lập luận, cú pháp, nhịp discourse và lựa chọn diễn đạt vì chất lượng học thuật. Không diễn giải thành detector evasion.

---

# 3. Reader Contract và Cognitive-Load Budget

## 3.1. Người đọc mặc định

Giả định người đọc:

- là giảng viên hoặc sinh viên kỹ thuật/an toàn thông tin;
- biết lập trình;
- biết ML cơ bản;
- đã học Giải tích, Đại số tuyến tính, Xác suất thống kê ở mức đại học;
- không mặc định biết sâu self-supervised learning, representation probing, temporal GNN, provenance graph, causal inference, privacy attacks hoặc các chi tiết hẹp khác.

## 3.2. Knowledge gradient

Mỗi bước lập luận nên chỉ yêu cầu người đọc thực hiện một bước nhảy khái niệm vừa phải.

Nếu một câu đòi người đọc đồng thời hiểu:

- một thuật ngữ mới;
- một công thức mới;
- một giả định mới;
- một metric mới;
- và một kết luận mới;

thì vấn đề không nằm ở việc câu “dài bao nhiêu từ”, mà nằm ở việc câu đang chứa quá nhiều dependency chưa được giải quyết.

## 3.3. Cognitive-load budget

Khi khái niệm khó, giảm tải bằng một trong các cách sau:

- tách cơ chế thành vài bước có quan hệ nhân quả rõ;
- đưa một ví dụ nhỏ đã giải;
- dùng một trường hợp biên để làm lộ bản chất;
- dùng một contrast với khái niệm gần nhưng khác;
- nhắc lại đúng một tiền đề đã xuất hiện trước đó.

Không giảm tải bằng cách:

- thêm nhiều synonym;
- lặp lại nguyên định nghĩa;
- thêm nhiều bullet cơ học;
- thêm nhiều ngoặc giải thích;
- nhồi một glossary vào thân đoạn.

## 3.4. Worked-example fading

Ví dụ giải sẵn hữu ích khi người đọc gặp cơ chế mới, nhưng không nên lặp lại cùng mức chi tiết ở mọi lần xuất hiện.

Mặc định:

1. Lần đầu: có thể dùng một worked micro-example.
2. Lần sau: chỉ nhắc cơ chế cốt lõi.
3. Khi người đọc đã có schema: dùng shorthand hợp lý.

Không dạy lại từ đầu ở mỗi chương nếu không có lý do.

---

# 4. Argument Engine: Claim, Evidence, Warrant, Qualifier

v4 xem một luận điểm khoa học như một cấu trúc nội bộ:

```text
CLAIM
↑
WARRANT
↑
EVIDENCE / MECHANISM / DERIVATION

+ QUALIFIER / SCOPE
+ LIMITATION / REBUTTAL khi cần
```

Đây là reasoning model nội bộ, không phải template phải in nguyên vào luận văn.

## 4.1. Claim

Claim là điều tác giả muốn người đọc chấp nhận.

Ví dụ:

> Temporal encoding giúp mô hình phân biệt các nhịp hoạt động khác nhau.

## 4.2. Evidence

Evidence có thể là:

- literature;
- code/config;
- artifact;
- experiment;
- mathematical derivation;
- observation;
- theorem có điều kiện;
- benchmark result.

## 4.3. Warrant

Warrant là mắt xích giải thích:

> Vì sao evidence hoặc cơ chế này hỗ trợ claim?

Đây là nơi nhiều văn bản kỹ thuật yếu nhất.

Citation không thay thế warrant.

Ví dụ yếu:

> Harmonic time encoding biểu diễn khoảng trễ liên tục [35], do đó mô hình hiểu ngữ cảnh thời gian.

Ví dụ tốt hơn:

> Harmonic time encoding biến một khoảng trễ vô hướng thành một vector gồm nhiều thành phần tuần hoàn ở các tần số khác nhau. Hai khoảng trễ khác nhau có thể tạo ra các mẫu pha khác nhau, nhờ đó mô hình có thêm tín hiệu để phân biệt nhịp hoạt động. Cơ chế này không đồng nghĩa với causal understanding và cũng không mặc nhiên tạo ánh xạ một-một trên mọi miền thời gian.

Ở đây, phần “biến một khoảng trễ...” đến “phân biệt nhịp hoạt động” là warrant.

## 4.4. Qualifier

Qualifier trả lời:

- trong dữ liệu nào?
- theo metric nào?
- trong điều kiện nào?
- ở bước pipeline nào?
- với loại model nào?
- có kiểm thử downstream chưa?
- có shift chưa?

Một claim thiếu qualifier thường mạnh hơn evidence.

## 4.5. Warrant test

Với mỗi claim quan trọng, Agent phải tự hỏi:

> Nếu xóa citation và số liệu ra khỏi câu, tôi còn giải thích được bằng lời vì sao bằng chứng đó liên quan đến claim không?

Nếu không, reasoning gap vẫn còn.

---

# 5. Basic-First Derivation Controller

Chuỗi nội bộ mặc định:

```text
VẤN ĐỀ
→ KHÁI NIỆM ĐÃ BIẾT
→ PHÉP BIẾN ĐỔI / CƠ CHẾ
→ TRẠNG THÁI TRUNG GIAN
→ HỆ QUẢ
→ EVIDENCE
→ PHẠM VI
→ GIỚI HẠN
```

v4 bổ sung hai quy tắc mới so với v3.1:

1. Phải có **trạng thái trung gian** nếu claim không thể nhảy thẳng từ mechanism đến conclusion.
2. Phải có **stopping rule** để không textbook hóa.

## 5.1. Stopping rule

Dừng mở sâu khi một trong các điều sau đúng:

- bước tiếp theo là kiến thức đại học cơ bản mà reader contract đã giả định;
- mở thêm toán không thay đổi cách hiểu claim;
- phần mở thêm không ảnh hưởng scope hoặc limitation;
- derivation dài hơn nhưng không làm warrant mạnh hơn;
- claim có thể được bảo vệ đầy đủ bằng evidence trực tiếp mà không cần derivation thêm.

## 5.2. Counterexample test

Trước một claim mạnh, thử nghĩ một counterexample đơn giản.

Nếu tìm được counterexample hợp lý, phải thêm điều kiện hoặc hạ claim.

Ví dụ:

- covariance bằng 0 nhưng biến vẫn có thể phụ thuộc phi tuyến;
- cosine similarity cao nhưng hai vector vẫn có thể khác về thông tin downstream;
- loss thấp trên train nhưng generalization kém;
- attention weight lớn nhưng không phải causal importance;
- residual PCA lớn nhưng có thể là hành vi hợp lệ hiếm;
- dependency graph có cạnh nhưng không chứng minh tác động nhân quả.

Counterexample test là công cụ restraint, không phải yêu cầu chèn counterexample vào mọi đoạn.

---

# 6. Mathematical Grounding v4

Toán học chỉ được dùng khi nó làm một trong bốn việc:

1. định nghĩa chính xác đại lượng;
2. cho thấy cơ chế biến đổi;
3. cho phép suy ra một hệ quả;
4. khóa một giới hạn mà prose dễ overclaim.

## 6.1. Trước công thức

Phải cho biết công thức đang trả lời câu hỏi gì.

Không thả công thức xuống rồi giải thích sau.

Ví dụ:

> Để thấy vì sao một chiều biểu diễn có thể sụp đổ, cần nhìn vào phương sai của chiều đó trên batch.

Sau đó mới đưa công thức variance.

## 6.2. Trong công thức

Chỉ định nghĩa ký hiệu cần thiết cho reasoning hiện tại.

Không dump tất cả ký hiệu trong một ngoặc dài.

## 6.3. Sau công thức

Phải trả lời ít nhất một trong các câu:

- khi đại lượng A tăng thì chuyện gì xảy ra?
- trường hợp biên cho ta thấy gì?
- term này tác động lên parameter nào?
- điều gì được tối ưu trực tiếp?
- điều gì chỉ được khuyến khích gián tiếp?
- công thức không chứng minh điều gì?

## 6.4. Sanity checks bằng trường hợp đặc biệt

Khi công thức đóng vai trò quan trọng, Agent nên thử một hoặc hai trường hợp đơn giản.

Ví dụ:

### Entropy

Nếu toàn bộ xác suất tập trung vào một loại sự kiện:

```text
p = (1, 0, ..., 0)
```

thì entropy bằng 0.

Nếu phân phối đều hơn, entropy tăng.

Điều này giải thích trực giác “mức bất định/phân tán”, nhưng không biến entropy thành score độc hại.

### Softmax attention

Nếu mọi score bằng nhau, trọng số gần như đều.

Nếu một score vượt trội, trọng số tập trung vào vị trí đó.

Điều này giải thích cơ chế chọn trọng số, nhưng không chứng minh vị trí đó là nguyên nhân của prediction.

### PCA residual

Nếu vector nằm hoàn toàn trong retained subspace, residual bằng 0.

Residual lớn chỉ nói vector có thành phần nằm ngoài không gian mô hình giữ lại.

### Stop-gradient

Nếu nhánh B bị stop-gradient đối với loss L:

```text
∂L / ∂θ_B = 0
```

qua nhánh bị chặn.

Điều này cho biết đường gradient bị khóa, không cho biết representation B “đúng” hơn.

### PCGrad

Nếu hai gradient có tích vô hướng âm, chúng đang chỉ theo các hướng cục bộ xung đột.

PCGrad loại bỏ thành phần gradient gây xung đột theo phép chiếu được định nghĩa.

Nếu tích vô hướng không âm, không có cơ sở từ chính điều kiện đó để gọi chúng là conflicting.

## 6.5. Proof sketch vs proof

Không được dựng “proof theater”.

Nếu sử dụng theorem từ literature:

- nêu điều kiện quan trọng;
- cho intuition;
- nêu hệ quả liên quan trực tiếp;
- citation paper gốc;
- không giả vờ tái chứng minh toàn bộ nếu luận văn không cần.

Nếu là derivation do tác giả sử dụng để giải thích thiết kế:

- phải đủ bước để người đọc kiểm tra;
- không được bỏ qua phép biến đổi quan trọng;
- không gắn nhãn “chứng minh” nếu chỉ là trực giác.

---

# 7. Measurement Chain và Construct Validity

Một trong các nâng cấp lớn nhất của v4:

> Metric không phải construct.

Mọi claim đo lường quan trọng nên được hiểu qua chuỗi:

```text
CONSTRUCT
→ OPERATIONALIZATION
→ METRIC / TEST
→ OBSERVATION
→ ALLOWED INFERENCE
```

## 7.1. Construct

Construct là thứ tác giả thật sự muốn biết.

Ví dụ:

- chất lượng representation;
- robustness;
- privacy;
- anomaly detection utility;
- SOC deployment feasibility;
- semantic fidelity.

## 7.2. Operationalization

Operationalization là cách biến construct thành thứ có thể đo.

Ví dụ:

- frozen linear probe để đo lượng thông tin linearly accessible;
- VRAM peak để đo memory footprint cục bộ;
- MIA success rate để đo một loại privacy leakage;
- F1 trên HDFS split để đo classification performance dưới split đó.

## 7.3. Metric

Metric là đại lượng quan sát được.

Metric không tự mang toàn bộ nghĩa của construct.

## 7.4. Allowed inference

Agent phải nói chính xác metric cho phép kết luận gì.

Ví dụ:

```text
Linear probe accuracy cao
→ thông tin phục vụ nhãn đang linearly accessible từ z dưới protocol đó
≠ toàn bộ representation quality
≠ nonlinear information
≠ robustness
≠ causal semantics
```

```text
VRAM < 550 MB
→ memory footprint của experiment nằm dưới mức đó trên cấu hình đo
≠ throughput đủ cho SOC
≠ latency đủ
≠ production readiness
```

```text
5 seed cho kết quả gần nhau
→ optimization/run variability dưới 5 seed và fixed setting có vẻ nhỏ
≠ dataset-shift robustness
≠ concept-drift robustness
≠ external validity
```

## 7.5. Construct-validity questions

Trước khi diễn giải một metric, hỏi:

1. Metric đang trực tiếp đo đại lượng nào?
2. Đại lượng đó liên hệ với construct qua giả định nào?
3. Có proxy nào đang bị gọi tên như construct không?
4. Có confounder hoặc shortcut nào cùng làm metric tăng không?
5. Kết quả có nhạy với protocol, split, threshold hoặc probe capacity không?
6. Nếu metric tăng, construct có buộc phải tăng không?

Nếu câu 6 là “không”, phải viết claim ở mức metric hoặc operationalization.

---

# 8. ML/DL Claim Ladder

v4 cấm nhảy nhiều bậc trong một câu nếu không có evidence tương ứng.

Các bậc:

```text
0. DESIGN INTENT
1. OBJECTIVE PRESSURE
2. TRAINING OBSERVATION
3. MEASURED REPRESENTATION PROPERTY
4. ACCESSIBLE INFORMATION UNDER A PROBE
5. DOWNSTREAM UTILITY
6. ROBUSTNESS / SHIFT
7. OPERATIONAL FEASIBILITY
8. CAUSAL / SECURITY INTERPRETATION
```

## 8.1. Bậc 0: Design intent

“Được thiết kế để” chỉ nói mục đích.

Không được đổi thành “bảo đảm”.

## 8.2. Bậc 1: Objective pressure

Loss khuyến khích một hình học hoặc hành vi cụ thể.

Ví dụ covariance penalty khuyến khích giảm tương quan tuyến tính giữa các chiều.

Không được nhảy sang “các chiều độc lập”.

## 8.3. Bậc 2: Training observation

Loss thực tế giảm, gradient hữu hạn, model hội tụ theo criterion nội bộ.

Đây là evidence về optimization run.

Không phải downstream utility.

## 8.4. Bậc 3: Measured property

Ví dụ variance từng chiều vượt threshold, covariance off-diagonal giảm.

Đây là property theo metric đã chọn.

## 8.5. Bậc 4: Probe-accessible information

Linear probe cho biết thông tin có thể truy xuất tuyến tính.

Probe mạnh hơn có thể học nhiều hơn từ cùng representation, nên probe result phải được diễn giải kèm capacity.

## 8.6. Bậc 5: Downstream utility

Cần downstream task thật hoặc protocol đủ đại diện.

## 8.7. Bậc 6: Robustness / shift

Cần perturbation, new split, drift, distribution shift hoặc threat variation tương ứng.

Không dùng seed stability thay thế.

## 8.8. Bậc 7: Operational feasibility

Cần latency, throughput, memory, compute, availability, failure mode hoặc constraint thực tế liên quan.

## 8.9. Bậc 8: Causal / security interpretation

Cần thiết kế và evidence mạnh hơn association/prediction thông thường.

Không được nhảy từ attention, dependency hoặc correlation lên causal effect.

---

# 9. Causal Language Ladder

Mặc định phân biệt bốn mức:

```text
ASSOCIATION
→ TEMPORAL / STRUCTURAL DEPENDENCY
→ INTERVENTION
→ COUNTERFACTUAL
```

## 9.1. Association

Ví dụ:

- hai feature đồng biến;
- cosine cao;
- attention weight lớn;
- edge thường xuất hiện trước label.

Dùng từ:

- liên hệ;
- tương quan;
- liên đới;
- đồng xuất hiện;
- liên quan thống kê.

## 9.2. Temporal / structural dependency

Ví dụ:

- process mở file;
- event A đứng trước event B;
- graph edge biểu diễn interaction;
- zero-lookahead chỉ dùng quá khứ/hiện tại.

Dùng từ:

- phụ thuộc thực thi;
- quan hệ cấu trúc;
- thứ tự thời gian;
- thông tin có trước.

Không mặc nhiên dùng:

- gây ra;
- dẫn đến theo nghĩa can thiệp;
- causal effect.

## 9.3. Intervention

Muốn nói “nếu thay X thì Y thay đổi do X”, cần thiết kế hoặc giả định causal phù hợp.

## 9.4. Counterfactual

Muốn nói “nếu sự kiện X đã không xảy ra thì Y sẽ không xảy ra” cần causal model mạnh hơn observational dependency.

## 9.5. Security-specific caution

Provenance graph có thể biểu diễn dependency của thực thi.

Nó không tự biến dependency thành malicious causation.

Temporal order không phải causal order.

Zero lookahead là information restriction, không phải causal inference.

---

# 10. Experimental Evidence và Uncertainty

## 10.1. Result sentence phải biết nguồn biến thiên

Khi viết mean, std, confidence interval hoặc error bar, phải biết nó phản ánh biến thiên từ đâu:

- random seed;
- data split;
- sampling;
- initialization;
- threshold;
- environment;
- repeated run;
- bootstrap.

Không dùng một error bar không rõ nguồn.

## 10.2. Seed rule

Một số seed chỉ kiểm tra variability do stochastic training trong setting đã khóa.

Không được suy diễn sang:

- robustness với dataset shift;
- robustness với concept drift;
- robustness với adversarial perturbation;
- external validity.

## 10.3. Scope vector

Với một kết luận thực nghiệm quan trọng, Agent nên biết vector phạm vi:

```text
{
  dataset,
  split,
  model,
  training protocol,
  seed set,
  metric,
  threshold,
  perturbation axis,
  threat model,
  time horizon,
  hardware nếu claim vận hành
}
```

Không cần tạo JSON.

Đây chỉ là checklist nhận thức để claim không vượt phạm vi.

## 10.4. Từ “robust”

Chỉ dùng “robust/bền vững” khi đã nói rõ robust với variation nào.

Ví dụ tốt:

> Kết quả tương đối ổn định trước biến thiên do năm hạt giống khởi tạo trong cùng split.

Không tốt:

> Mô hình có độ bền vững cao.

## 10.5. Statistical significance

Không dùng “có ý nghĩa thống kê” nếu không có kiểm định hoặc interval tương ứng.

Không đánh đồng statistical significance với practical significance.

Không dùng p-value làm đại diện cho effect size.

---

# 11. Optimization and Gradient-Path Protocol

Đây là nâng cấp trực tiếp cho các thesis có nhiều auxiliary loss, stop-gradient hoặc multi-task objective.

## 11.1. Gradient descent tối thiểu

Nếu claim phụ thuộc vào optimization:

```text
θ_{t+1} = θ_t - η ∇_θ L
```

Giải thích đủ:

- gradient là độ nhạy cục bộ của loss theo parameter;
- hướng âm gradient là hướng giảm loss bậc nhất;
- learning rate quyết định bước;
- local descent không chứng minh global optimum.

## 11.2. Chain-rule question

Khi một loss đi qua nhiều module, hỏi:

```text
Loss này có đường đạo hàm nào đến parameter đang nói?
```

Nếu không có đường đạo hàm, không được nói loss “huấn luyện” parameter đó.

## 11.3. Stop-gradient

Nếu dùng stop-gradient:

- chỉ ra branch nào forward vẫn dùng value;
- chỉ ra branch nào backward bị chặn;
- nếu cần, nói rõ partial derivative qua branch đó bằng 0;
- không gán cho stop-gradient công dụng downstream chưa đo.

## 11.4. Multi-loss

Với:

```text
L = λ1 L1 + λ2 L2 + ...
```

không chỉ liệt kê loss.

Phải giải thích:

- loss nào tác động module nào;
- loss nào có thể tạo gradient conflict;
- hệ số λ làm thay đổi độ lớn đóng góp như thế nào;
- việc tổng loss giảm không cho biết từng mục tiêu đều cải thiện.

## 11.5. PCGrad

Nếu dùng PCGrad, cần tối thiểu:

- hai task gradient;
- dot product âm nghĩa là hai hướng giảm cục bộ đang xung đột theo tiêu chí PCGrad;
- projection loại phần thành phần gây xung đột;
- PCGrad thay đổi optimization geometry;
- không tự chứng minh hai task trở nên “hài hòa về ngữ nghĩa”.

---

# 12. Domain Playbooks

## 12.1. TF-IDF

Cầu nối:

```text
count
→ TF: mức xuất hiện trong đơn vị cục bộ
→ IDF: mức hiếm trên toàn corpus
→ product/weight
→ feature weighting
→ anomaly relevance chỉ là giả thuyết downstream
```

Khóa:

- rare không đồng nghĩa malicious;
- TF-IDF không mô hình hóa thứ tự;
- TF-IDF không suy causal relation.

## 12.2. Shannon entropy

Cầu nối:

```text
event counts
→ empirical probabilities
→ entropy
→ concentration vs dispersion
```

Khóa:

- entropy đo uncertainty/dispersion của distribution;
- entropy cao không tự chứng minh attack;
- phải phân biệt với TF-IDF.

## 12.3. PCA

Cầu nối:

```text
center x
→ covariance geometry
→ principal directions
→ projection onto retained subspace
→ residual
→ residual magnitude as statistical deviation
```

Sanity case:

- x nằm trong retained subspace thì residual bằng 0.

Khóa:

- high variance không đồng nghĩa security relevance;
- residual lớn không tự chứng minh maliciousness;
- PCA tối ưu variance criterion, không tối ưu attack semantics.

## 12.4. RNN/LSTM

Cầu nối:

```text
sequential state update
→ information phải đi qua nhiều recurrent steps
→ gradient/state propagation qua chuỗi dài
→ gating của LSTM kiểm soát retention/update
```

Không nói LSTM “ghi nhớ dài hạn” như một tính chất tuyệt đối.

## 12.5. Transformer / Self-Attention

Cầu nối:

```text
x
→ Q, K, V
→ scaled dot-product scores
→ softmax weights
→ weighted sum of V
→ contextualized representation
```

Sanity case:

- equal scores tạo weighting gần đều;
- một score lớn tạo concentration.

Khóa:

- attention weight không mặc nhiên là explanation;
- attention không tự mã hóa graph topology;
- attention không tự suy causal relation;
- scope theo mask/window.

## 12.6. GNN / Message Passing

Cầu nối:

```text
node state
→ messages from neighbors
→ aggregation
→ update
→ k layers mở rộng receptive field đến k-hop
```

### Over-smoothing

Không chỉ viết “các vector trở nên giống nhau”.

Giải thích ở mức phù hợp:

- repeated neighborhood mixing làm trạng thái liên tục pha trộn;
- trong một số kiến trúc/điều kiện phổ biến, repeated propagation làm khác biệt giữa node representations co lại về một không gian thấp hơn hoặc cấu trúc khó phân biệt;
- theorem-specific claim phải giữ đúng assumptions của paper.

Không generalize theorem của GCN cho mọi GNN vô điều kiện.

### Over-squashing

Giải thích:

- receptive field tăng nhanh theo hop;
- thông tin từ nhiều nguồn phải đi qua bottleneck/cut và bị nén vào fixed-size states;
- long-range dependency có thể khó truyền.

Không nói mọi graph đều tăng hàng xóm “theo hàm mũ” nếu topology cụ thể không có property đó.

## 12.7. Temporal Encoding / TGNN

Cầu nối:

```text
Δt scalar
→ encoding function φ(Δt)
→ vector time features
→ combine with event/entity features
→ model can condition on timing differences
```

Khóa:

- continuous encoding không mặc nhiên injective;
- harmonic encoding có tính tuần hoàn;
- temporal order không bằng causal effect;
- zero-lookahead không bằng causal inference.

## 12.8. Self-Supervised Learning / VICReg

Phân biệt:

### Invariance term

Khuyến khích paired views gần nhau theo metric đã định nghĩa.

Không tự chứng minh semantic equivalence.

### Variance term

Ngăn các chiều co về hằng số dưới criterion của batch/threshold.

Không tự chứng minh representation informative cho downstream.

### Covariance term

Giảm linear correlation giữa các chiều.

Không tự chứng minh statistical independence.

### Downstream

Cần probe/task riêng.

Không dùng training loss làm downstream evidence.

## 12.9. Frozen Linear Probe

Cầu nối:

```text
freeze encoder
→ train linear map on z
→ evaluate task
→ estimate linearly accessible task information
```

Khóa:

- probe capacity là một phần của measurement;
- probe tốt không chứng minh mọi thông tin trong z;
- probe kém không chứng minh z không chứa nonlinear information;
- nếu probe protocol thay đổi, construct đo được cũng thay đổi.

## 12.10. Privacy

Phân biệt:

```text
pseudonymization
≠ anonymity
≠ formal privacy guarantee
```

Nếu chưa chạy MIA, model inversion hoặc attack protocol liên quan:

- nói là planned / proposed / untested;
- không viết “privacy-preserving” theo nghĩa đã chứng minh nếu chỉ có design intent.

## 12.11. Security semantics

Luôn giữ các ranh giới:

```text
rare ≠ malicious
anomalous ≠ attack
dependency ≠ malicious intent
temporal precedence ≠ cause
provenance relation ≠ causal effect
good benchmark metric ≠ operational SOC utility
```

---

# 13. Reader-State Architecture cho mạch dài

v4 không chỉ kiểm paragraph. Nó theo dõi trạng thái hiểu của người đọc.

Mỗi section nên có:

```text
ENTRY STATE:
Người đọc đã biết gì?

QUESTION:
Câu hỏi chưa được giải quyết là gì?

DEVELOPMENT:
Cơ chế/evidence nào trả lời?

EXIT STATE:
Bây giờ người đọc có thể kết luận gì?

RESIDUE:
Điều gì vẫn chưa giải quyết và dẫn sang section sau?
```

Không cần in cấu trúc này vào tài liệu.

## 13.1. Handoff invariant

Một section tốt không kết thúc chỉ bằng “tóm lại”.

Nó nên để lại một residue logic cho phần sau.

Ví dụ:

> Cơ chế chuỗi giải quyết dependency trong cửa sổ quan sát, nhưng chưa biểu diễn trực tiếp tương tác tiến trình, tệp và socket. Giới hạn này là lý do nhánh đồ thị được đưa vào ở mục tiếp theo.

Section sau có thể bắt đầu từ “giới hạn tương tác đa thực thể” thay vì reset:

> Đồ thị nguồn gốc xử lý giới hạn trên bằng cách...

## 13.2. Known-to-new

Dùng nguyên tắc reader expectation:

- đầu câu/đầu đoạn ưu tiên anchor với thông tin người đọc vừa biết khi cần continuity;
- phần mới và quan trọng nên nhận vị trí nhấn;
- không mở câu bằng một thuật ngữ mới không có anchor nếu reader phải tự dựng cầu nối.

Đây là heuristic, không phải luật ngữ pháp cứng.

## 13.3. Context reset

Dấu hiệu context reset:

- mỗi paragraph giới thiệu lại chủ đề;
- lặp “Trong bối cảnh...”;
- nhắc lại định nghĩa vừa xuất hiện;
- section sau không sử dụng kết luận section trước;
- chapter 3 không trả lời câu hỏi chapter 1/2 đã đặt.

Sửa bằng logical handoff, không chỉ thêm connector.

---

# 14. Sentence Stress và Overload Test

Không cấm câu dài.

Một câu cần tách khi có nhiều hơn một “trung tâm nhấn” cạnh tranh.

Dấu hiệu:

- chứa hai claim độc lập;
- chứa claim + evidence + caveat + claim mới;
- chứa ba dấu chấm phẩy để giữ các reasoning unit khác nhau;
- phải dùng hơn hai ngoặc để người đọc nhớ dependency;
- đầu câu nói chủ đề A nhưng cuối câu kết luận chủ đề C mà không có bridge.

Tách theo reasoning function, không theo word count.

Ví dụ:

Không tốt:

> TF-IDF...; entropy...; do đó...

Tốt hơn:

- câu 1 giải thích TF;
- câu 2 giải thích IDF và consequence;
- câu 3 khóa rare ≠ malicious;
- câu 4 chuyển sang entropy như một đại lượng khác.

---

# 15. Vietnamese Academic Prose

## 15.1. Viết như người hiểu cơ chế

Ưu tiên động từ có nội dung:

- chiếu;
- chuẩn hóa;
- gộp;
- ước lượng;
- giới hạn;
- đo;
- so sánh;
- lan truyền;
- nén;
- cập nhật;
- khóa;
- suy ra.

Hạn chế chuỗi danh từ kiểu:

> cơ chế thực hiện quá trình tối ưu hóa khả năng bảo toàn...

nếu có thể viết:

> cơ chế tối ưu loss để giữ...

## 15.2. Thuật ngữ tiếng Anh

Dùng tiếng Anh khi:

- là canonical name;
- acronym phổ biến;
- dịch sang tiếng Việt dễ gây mơ hồ;
- cần đối chiếu chính xác với literature.

Sau khi đã xác lập thuật ngữ:

- ưu tiên tiếng Việt hoặc acronym;
- không lặp song ngữ máy móc.

## 15.3. Ngoặc đơn

Giữ khi:

- first-use acronym;
- ký hiệu;
- canonical term cần disambiguation;
- citation/cross-reference;
- qualification ngắn thực sự cần.

Nếu ngoặc chứa cả một lập luận, viết thành câu.

Không đổi mọi ngoặc thành em dash hoặc dấu hai chấm.

## 15.4. Stance

Văn học thuật tốt cần phân biệt mức chắc chắn:

- “cho thấy” khi evidence trực tiếp;
- “gợi ý” khi evidence gián tiếp;
- “phù hợp với” khi có nhiều explanation;
- “được thiết kế để” cho design intent;
- “có thể” cho khả năng;
- “chưa đủ để kết luận” khi scope thiếu.

Không lạm dụng “khẳng định”, “chứng minh”, “bảo đảm”, “tuyệt đối”.

---

# 16. Anti-Homogenization và Anti-AI-Slop

Mục tiêu là chất lượng discourse, không phải detector.

Các dấu hiệu cần xem xét:

- nhiều paragraph có cùng opening move;
- lặp cấu trúc “Một là... Hai là... Ba là...” không do nội dung yêu cầu;
- lặp nhịp claim → “Điều này cho thấy” → conclusion;
- synonym substitution nhưng syntax giữ nguyên;
- mỗi section đều mở bằng “Trong bối cảnh...”;
- nhiều câu dùng cùng chuỗi nominalization;
- exemplification theo pattern giống nhau;
- đoạn nào cũng kết bằng caveat cùng cấu trúc;
- quá nhiều signpost trong khi logic tự thân chưa rõ;
- nhiều tính từ học thuật nhưng không thêm information.

Không sửa bằng random variation.

Sửa bằng cách xác định chức năng thật của đoạn:

- định nghĩa;
- contrast;
- derivation;
- evidence;
- limitation;
- transition;
- synthesis.

Khi chức năng khác nhau, syntax tự nhiên sẽ khác nhau.

## 16.1. Preserve authorial technical fingerprints

Không “polish” đến mức mọi câu giống văn mẫu chuẩn.

Giữ:

- lựa chọn ví dụ có ý nghĩa với đề tài;
- cách gọi tên nhất quán đã được tác giả xác lập;
- sequence lập luận đặc trưng;
- thuật ngữ domain cần thiết;
- mức thận trọng phù hợp với evidence.

---

# 17. Citation và Source Discipline

## 17.1. Source hierarchy

Ưu tiên:

1. paper gốc / standard / official documentation;
2. proceedings hoặc publisher page;
3. official project/code nếu claim về implementation;
4. review chất lượng cao để định vị bối cảnh;
5. bài viết chuyên ngành Việt Nam để tham khảo framing/ngôn ngữ, không thay paper gốc cho claim kỹ thuật.

## 17.2. Citation adjacency

Citation phải đứng gần proposition mà nó hỗ trợ.

Không đặt một citation cuối một câu dài rồi ngầm coi nó hỗ trợ mọi mệnh đề.

## 17.3. Warrant ownership

Nếu paper nói A và B, nhưng tác giả suy ra C từ A+B:

- cite A/B;
- trình bày C như author synthesis;
- không viết như paper đã nói nguyên C.

## 17.4. Metadata verification

Khi task yêu cầu kiểm nguồn:

- xác minh title;
- authors;
- venue;
- year;
- DOI/official URL;
- semantic support.

Không dùng citation existence thay cho semantic support.

---

# 18. Experimental Writing Protocol

Một result paragraph tốt thường cần bốn chức năng, không nhất thiết bốn câu:

```text
OBSERVATION
→ UNCERTAINTY
→ INTERPRETATION
→ BOUNDARY
```

Ví dụ:

> Trên năm seed đã định trước, loss Stage A2 hội tụ về vùng tương tự với độ phân tán nhỏ. Kết quả này cho thấy quá trình tối ưu tương đối ổn định trước biến thiên do khởi tạo trong protocol hiện tại. Tuy nhiên, phép đo chưa kiểm tra thay đổi dữ liệu theo thời gian hoặc domain shift, vì vậy không được dùng để kết luận về khả năng chống concept drift.

## 18.1. Hypothesis identity

Mỗi hypothesis phải giữ cùng semantic identity qua:

```text
definition
→ method
→ measurement
→ result
→ conclusion
```

Không chỉ giữ nhãn H1/H2.

## 18.2. Ablation

Ablation drop cho thấy component có đóng góp trong cấu hình đang thử.

Không tự chứng minh:

- cơ chế duy nhất;
- causal mechanism toàn diện;
- general usefulness ngoài setting.

## 18.3. Negative / partial result

Không che negative result bằng prose.

Nếu một hypothesis chưa được test:

- ghi untested;
- không “gần như xác nhận” bằng proxy không tương ứng.

---

# 19. Figures, Tables và Equations là Argument Units

## 19.1. Figure/table phải có job

Trước figure/table, người đọc phải biết đang cần nhìn điều gì.

Sau figure/table, prose phải lấy ra đúng implication, không đọc lại toàn bộ bảng.

## 19.2. Caption

Caption mô tả nội dung và scope.

Không biến caption thành một đoạn discussion dài.

## 19.3. Equation as sentence

Công thức là một phần ngữ pháp của đoạn:

- có lead-in;
- có punctuation phù hợp;
- có interpretation;
- có scope.

Không để display equation “mồ côi”.

---

# 20. OMML và Word Master Authority

Đây là HARD REQUIREMENT.

Trong Word Master, mọi biểu thức toán học thực sự phải dùng Microsoft Office Math / OMML native.

Thông thường:

- inline: `m:oMath`
- display: `m:oMathPara`

Không:

- LaTeX raw;
- Unicode giả superscript/fraction;
- text kiểu `sqrt(x)` nếu vị trí đó là mathematical expression chuẩn;
- ảnh chụp equation;
- flatten OMML thành text.

## 20.1. Master là authority

Khi thêm/sửa toán, inspect công thức lân cận và tuân thủ convention hiện hành về:

- scalar/vector/matrix/tensor;
- bold/italic;
- transpose;
- inverse;
- norm;
- expectation;
- probability;
- covariance;
- gradient;
- derivative;
- log/exp/softmax/diag/tr/argmin;
- subscript/superscript;
- delimiter;
- fraction;
- radical;
- sum/product;
- matrix;
- piecewise;
- inline/display;
- numbering;
- cross-reference;
- punctuation;
- spacing.

Không global re-standardize nếu notation hiện tại khoa học đúng.

## 20.2. Semantic invariants

Sau khi sửa math:

- cùng symbol vẫn cùng nghĩa;
- vector/matrix distinction không đổi;
- subscript/superscript không đổi nghĩa;
- domain/dimension hợp lệ;
- transpose/inverse đúng;
- expectation/covariance đúng variable;
- equation number/crossref đúng.

## 20.3. OMML editing safety

Không dùng destructive `paragraph.text = ...` trên paragraph chứa:

- OMML;
- field;
- bookmark;
- hyperlink;
- cross-reference.

Ưu tiên patch safe text nodes hoặc OMath/OMML node thích hợp.

Nếu không thể sửa an toàn, dừng và báo blocker.

## 20.4. QA sau khi chạm công thức

`OMML node count unchanged` không đủ.

Phải kiểm:

- render;
- numerator/denominator;
- script;
- radical;
- delimiter;
- matrix;
- operator;
- number/cross-reference;
- mathematical meaning.

---

# 21. DOCX Safety Rail

Bảo toàn:

- OMML;
- CITATION fields;
- bibliography sources;
- bookmarks;
- hyperlinks;
- REF/PAGEREF và cross-reference;
- captions;
- tables;
- figures;
- drawing anchors;
- styles;
- numbering;
- headings;
- section structure.

Nếu task sửa DOCX, cuối lượt phải render Word/PDF theo workflow có sẵn và kiểm visual regression.

Safety rail này bắt buộc nhưng không được biến thành audit bureaucracy.

---

# 22. Execution Protocol v4

Không dựng thêm infrastructure.

Thực hiện bằng các pass biên tập trực tiếp.

## PASS 0: Reader-State Map

Với mỗi chapter/section lớn, xác định:

- reader đã biết gì;
- câu hỏi section trả lời;
- section kết luận gì;
- residue dẫn sang đâu.

Không cần tạo file riêng nếu không hữu ích.

## PASS 1: Claim-Warrant Review

Tìm:

- citation nhưng thiếu warrant;
- claim nhảy qua mechanism;
- conclusion không có bridge;
- strong verb vượt evidence.

Sửa reasoning trước prose.

## PASS 2: Measurement Validity

Với metric/probe/result quan trọng:

- construct là gì?
- metric thật sự đo gì?
- allowed inference là gì?
- proxy có bị gọi nhầm là construct không?

## PASS 3: Derivation Depth

Với reasoning gap:

- lùi xuống ML/DL hoặc toán đại học;
- thêm trạng thái trung gian;
- dùng worked micro-example nếu cần;
- áp stopping rule.

## PASS 4: Scope and Uncertainty

Kiểm:

- seed;
- split;
- dataset;
- threshold;
- perturbation;
- threat model;
- hardware;
- downstream.

Hạ claim nếu scope không đủ.

## PASS 5: Long-Form Coherence

Kiểm:

- known→new;
- handoff;
- context reset;
- duplicated definition;
- section order;
- hypothesis identity.

## PASS 6: Human Prose

Dọn:

- overloaded sentence;
- parenthetical clutter;
- bilingual repetition;
- stock transitions;
- synonym laundering;
- rhythmic sameness;
- nominalization chains;
- AI-style exemplification templates.

## PASS 7: Mathematical and Document QA

Kiểm:

- equations;
- special cases;
- notation;
- OMML;
- citations;
- Word objects;
- render.

Nếu PASS 7 phát hiện vấn đề nội dung, quay lại đúng chỗ cần sửa. Không mở một audit universe mới.

---

# 23. Definition of Done

Một tài liệu đạt v4 khi:

1. Các claim khoa học chính có thể truy về mechanism, derivation hoặc evidence phù hợp.
2. Evidence và claim được nối bởi warrant đủ rõ.
3. Metric không bị gọi nhầm thành construct.
4. Không có jump lớn trong ML/DL Claim Ladder mà thiếu evidence.
5. Optimization objective không bị viết như downstream result.
6. Probe, attention, covariance, graph dependency, temporal order và pseudonymization đều được diễn giải đúng scope.
7. Mathematical derivation mở đủ để trả lời WHY nhưng không textbook hóa.
8. Các công thức quan trọng có thể qua một sanity check đơn giản.
9. Claim thực nghiệm giữ đúng scope của dataset, split, seed và metric.
10. “Robust”, “causal”, “privacy-preserving”, “deployment-ready”, “semantic” chỉ xuất hiện khi evidence đủ cho đúng nghĩa đó.
11. Chapter/section có logical handoff và không reset context hàng loạt.
12. Văn phong tiếng Việt đọc như một người nghiên cứu hiểu vấn đề, không như glossary hoặc slide deck.
13. Không còn pattern AI-slop chi phối nhiều đoạn liên tiếp.
14. English annotation và parentheses ở mức có chức năng.
15. Hypothesis giữ semantic identity từ định nghĩa đến kết luận.
16. Mọi math bị tác động trong Word Master vẫn là OMML native, đúng convention và đúng nghĩa.
17. Citation field, bookmark, cross-reference, bảng, hình, numbering và style an toàn.
18. Không có experiment, result hoặc evidence bị bịa để làm prose đẹp hơn.
19. Không có audit bureaucracy mới không cần thiết.
20. Khi các điều kiện trên đạt, DỪNG.

---

# 24. Worked Micro-Examples

## 24.1. Từ metric lên construct: Linear probe

Không tốt:

> Linear probe đạt độ chính xác cao, chứng minh representation chứa đầy đủ ngữ nghĩa tấn công.

Tốt hơn:

> Bộ mã hóa được đóng băng, còn một bộ phân loại tuyến tính được huấn luyện trên vector biểu diễn. Vì detector không được phép thay đổi encoder, accuracy của probe phản ánh mức độ thông tin phục vụ nhãn có thể được truy xuất bằng một ánh xạ tuyến tính từ representation. Kết quả này không đo toàn bộ thông tin phi tuyến có thể tồn tại trong vector và cũng chưa chứng minh robustness ngoài protocol hiện tại.

## 24.2. Từ objective lên property: VICReg

Không tốt:

> Covariance loss bảo đảm các chiều độc lập.

Tốt hơn:

> Thành phần covariance phạt các phần tử ngoài đường chéo của ma trận hiệp phương sai mẫu. Khi term này giảm, các chiều representation ít tương quan tuyến tính hơn trên batch đang xét. Tuy nhiên, zero covariance không đủ để suy ra statistical independence, đặc biệt khi quan hệ giữa các chiều có thể phi tuyến.

## 24.3. Từ graph symptom về cơ chế: Over-squashing

Không tốt:

> GNN mất thông tin xa vì over-squashing.

Tốt hơn:

> Sau k lớp message passing, một node có thể phụ thuộc vào thông tin từ vùng k-hop ngày càng lớn. Nếu nhiều nguồn xa phải truyền qua một số ít cạnh trung gian rồi được nén vào hidden state có kích thước cố định, các tín hiệu long-range cạnh tranh cho cùng một kênh biểu diễn. Đây là trực giác của over-squashing. Mức độ nghiêm trọng phụ thuộc topology và kiến trúc; không phải mọi graph đều có cùng tốc độ tăng receptive field.

## 24.4. Gradient path

Không tốt:

> Loss tái dựng huấn luyện cả encoder và target branch.

Tốt hơn:

> Loss chỉ cập nhật parameter nếu tồn tại đường đạo hàm từ loss đến parameter đó. Nếu target branch được đặt sau stop-gradient, forward pass vẫn sử dụng giá trị của target nhưng đạo hàm qua branch này bằng 0. Vì vậy, loss không trực tiếp cập nhật target-side parameters qua đường bị chặn.

## 24.5. Seed stability

Không tốt:

> Năm seed ổn định chứng minh mô hình robust.

Tốt hơn:

> Năm seed cho kết quả gần nhau cho thấy variability do khởi tạo/ngẫu nhiên huấn luyện trong setting đã khóa tương đối nhỏ. Phép đo này chưa kiểm tra dataset shift, temporal drift hoặc adversarial perturbation, nên không đủ để kết luận robustness theo các nghĩa đó.

---

# 25. Research Basis của v4

Các nguồn dưới đây định hướng thiết kế Skill. Chúng không phải citation bắt buộc phải nhét vào mọi luận văn.

## 25.1. Scientific writing và reader expectation

George D. Gopen & Judith A. Swan, “The Science of Scientific Writing”, American Scientist, 1990.

Điểm áp dụng:

- topic position;
- stress position;
- known→new linkage;
- logical gaps xuất hiện khi writer để reader tự nối quá nhiều bước.

## 25.2. Argument warrant

Stephen Toulmin và các adaptation học thuật về Claim–Evidence–Warrant.

Điểm áp dụng:

- evidence không tự nói lên claim;
- warrant là mắt xích cần được diễn giải.

## 25.3. Cognitive load và worked examples

John Sweller, “Cognitive Load During Problem Solving: Effects on Learning”, Cognitive Science, 1988.

Các review về Cognitive Load Theory và worked-example effect.

Điểm áp dụng:

- giảm extraneous reasoning burden;
- worked example hữu ích ở giai đoạn khái niệm mới;
- guidance phải fade khi reader đã có schema.

## 25.4. ML research claims và reproducibility

NeurIPS Paper Checklist Guidelines.

Điểm áp dụng:

- claim phải khớp scope;
- nêu limitations;
- assumptions;
- error bars;
- nguồn variability;
- reproducibility;
- compute.

## 25.5. Probe interpretation

John Hewitt & Percy Liang, “Designing and Interpreting Probes with Control Tasks”, EMNLP-IJCNLP 2019.

Điểm áp dụng:

- probe result phụ thuộc capacity;
- probe performance không tự đồng nghĩa representation property mạnh như claim thường gán.

## 25.6. Attention interpretation

Sarthak Jain & Byron C. Wallace, “Attention is not Explanation”, NAACL 2019.

Điểm áp dụng:

- attention weight không được mặc định dùng như causal/explanatory importance.

## 25.7. Shortcut learning

Robert Geirhos et al., “Shortcut Learning in Deep Neural Networks”, Nature Machine Intelligence, 2020.

Điểm áp dụng:

- benchmark performance có thể đến từ shortcut;
- downstream/generalization claim cần kiểm condition khó hơn.

## 25.8. Representation objective vs useful representation

Francesco Locatello et al., “Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations”, ICML 2019.

Điểm áp dụng:

- objective có thể enforce một property nhưng property đó không tự chứng minh downstream benefit;
- inductive bias và supervision assumptions phải rõ.

## 25.9. Construct validity

Abigail Z. Jacobs & Hanna Wallach, “Measurement and Fairness”, FAccT 2021.

Các công trình sau này về construct validity trong ML evaluation.

Điểm áp dụng:

- theoretical construct và operational measure là hai lớp khác nhau;
- metric chỉ hỗ trợ một interpretation khi assumptions phù hợp.

## 25.10. GNN pathologies

Kenta Oono & Taiji Suzuki, “Graph Neural Networks Exponentially Lose Expressive Power for Node Classification”, ICLR 2020.

Uri Alon & Eran Yahav, “On the Bottleneck of Graph Neural Networks and Its Practical Implications”, ICLR 2021.

Điểm áp dụng:

- theorem-specific assumptions cho over-smoothing;
- fixed-size bottleneck và long-range propagation cho over-squashing.

## 25.11. SSL regularization

Adrien Bardes, Jean Ponce, Yann LeCun, “VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning”, ICLR 2022.

Điểm áp dụng:

- variance/covariance terms là optimization constraints với scope xác định;
- downstream utility cần đánh giá riêng.

## 25.12. Multi-task gradient optimization

Tianhe Yu et al., “Gradient Surgery for Multi-Task Learning”, NeurIPS 2020.

Điểm áp dụng:

- gradient conflict được định nghĩa theo geometry;
- PCGrad thay gradient qua projection, không phải semantic harmonization.

## 25.13. Randomness và reproducibility

Peter Henderson et al., “Deep Reinforcement Learning That Matters”, AAAI 2018.

Điểm áp dụng:

- random seed và implementation variance có thể thay đổi interpretation;
- phải nói rõ uncertainty đang đo nguồn biến thiên nào.

## 25.14. Vietnamese ATTT framing

Tạp chí An toàn thông tin, Ban Cơ yếu Chính phủ, được dùng như nguồn tham khảo về:

- cách đặt vấn đề bằng tiếng Việt;
- nhịp chuyển từ bối cảnh sang cơ chế và hệ quả;
- thuật ngữ ATTT bản địa.

Không dùng bài phổ biến/tổng quan của Tạp chí thay paper gốc cho claim thuật toán hoặc theorem.

---

# 26. Những nâng cấp chính từ v3.1 lên v4.0

1. Thêm **Warrant Layer** giữa evidence và claim.
2. Thêm **Measurement Chain / Construct Validity** để chống metric→construct overclaim.
3. Thêm **ML/DL Claim Ladder** từ design intent đến causal/security interpretation.
4. Thêm **Scope Vector** cho empirical claims.
5. Thêm **Causal Language Ladder** rõ association→dependency→intervention→counterfactual.
6. Thêm **Gradient-Path Protocol** cho multi-loss, stop-gradient và PCGrad.
7. Thêm **Mathematical Sanity Checks** bằng special cases.
8. Thêm **Reader-State Architecture** và Handoff Invariant cho mạch dài.
9. Thêm **Sentence Stress / Overload Test** dựa trên reasoning units thay vì word count.
10. Thêm **Worked-example fading** để giảm cognitive load mà không textbook hóa.
11. Tăng độ chặt của playbook GNN, temporal encoding, probe, SSL và privacy.
12. Giữ nguyên hard requirement OMML và Master-as-authority.
13. Giữ triết lý anti-overengineering: không sinh thêm gate/audit framework nếu không cần.
14. Giữ anti-AI-slop theo chất lượng discourse, tuyệt đối không detector evasion.

---

# 27. Compact Output Contract cho Agent

Khi được yêu cầu biên tập một tài liệu theo v4, Agent không cần sinh báo cáo dài.

Mặc định báo:

```text
BASE
FINAL

SECTIONS_TOUCHED

CLAIM_WARRANT_GAPS_FIXED

MEASUREMENT_SCOPE_FIXES

MATHEMATICAL_DERIVATIONS_ADDED_OR_NARROWED

EXPERIMENTAL_SCOPE_NARROWED

LONG_FORM_HANDOFFS_FIXED

PROSE_HOMOGENIZATION_FIXES

OMML_TOUCHED
OMML_QA

UNRESOLVED_BLOCKERS

TEST_OPENED
TEST_READ_COUNT
NEW_OPTIMIZER_STEPS
```

Nếu không có experiment firewall trong project, ba dòng cuối có thể bỏ.

Không tự tạo thêm report taxonomy.

---

# 28. Lệnh cuối cho Agent

> Đọc toàn bộ Skill v4 trước khi sửa. Ưu tiên correctness, warrant và construct validity trước prose. Với mỗi claim quan trọng, bảo đảm reader có thể thấy evidence hoặc mechanism và hiểu vì sao nó hỗ trợ claim. Khi mở sâu, lùi xuống ML/DL hoặc toán đại học đủ để đóng reasoning gap rồi dừng. Không biến metric thành construct, objective thành result, dependency thành causality, seed stability thành robustness, hoặc design intent thành guarantee. Theo dõi reader state xuyên section/chapter để tránh context reset. Khi làm việc với Word Master, mọi math thực sự phải dùng OMML native và tuân thủ convention toán học đã có trong Master. Không tạo audit bureaucracy mới. Nếu một đoạn đã đúng, đủ warrant, đúng scope và đọc tự nhiên, giữ nguyên.
