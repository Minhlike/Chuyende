from __future__ import annotations
import copy, hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path
from lxml import etree


ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.omml_clarity_math import EXAMPLES, make_example
from scripts.omml_source_style import SourceMathStyle
DOCX=ROOT/'Chuyên đề chuyên sâu.docx'
EXPECTED='9bb11639807081f6ee3dafa8907f5293913ffec5697b945993b905ad93a67033'
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
Q=lambda x:f'{{{W}}}{x}'
MATH_RE=re.compile(r'⟦(.*?)⟧')

# Các chỉ số là vị trí con trực tiếp của w:body trong Master đã khóa bằng EXPECTED.
# Mọi số ở đây là ví dụ giả định, không phải số đo từ thí nghiệm.
NOTES={
 127: 'Ở bốn biểu thức trên, P_t là phân phối tại thời điểm t; X là dữ liệu quan sát, Y là nhãn mục tiêu và z là biểu diễn do bộ mã hóa tạo ra. Dấu khác nhau mô tả hai phân phối ở hai thời điểm có thể thay đổi; nó không tự xác định nguyên nhân trôi dạt hay chứng minh có tấn công. Ví dụ minh họa: cùng một mẫu log X có thể xuất hiện trong hai giai đoạn vận hành nhưng đi kèm tỷ lệ nhãn Y khác nhau; chỉ so sánh định dạng log sẽ bỏ lỡ thay đổi đó.',
 132: 'Tích Descartes ở đây ghép một chiến thuật với một kỹ thuật, còn tập nhãn của một phiên có thể chứa nhiều cặp như vậy. Ví dụ minh họa: một phiên có thể có bằng chứng liên quan đến cả Duy trì và Thu thập, nhưng công thức chỉ mô tả không gian nhãn có thể gán, không xác nhận phiên ấy thực sự bị tấn công.',
 156: 'Trong công thức đầu dò, z là vector d chiều đã học; W có d trọng số, b là độ lệch và σ biến điểm tuyến tính thành giá trị trong khoảng 0–1. Ví dụ minh họa: nếu ⟦Wᵀz+b=0⟧ thì ⟦σ(0)=0,5⟧. Đây là đầu ra của bộ phân loại được huấn luyện và hiệu chuẩn theo giao thức đánh giá, không phải bằng chứng rằng bộ mã hóa hiểu nguyên nhân an ninh.',
 164: 'Mỗi tọa độ của x đếm một loại sự kiện trong cùng cửa sổ W; vì có M loại nên x có M tọa độ và số đếm không âm. Ví dụ minh họa: với E gồm A và B, cửa sổ A, A, B cho ⟦x=(2,1)ᵀ⟧. Hai cửa sổ có cùng số đếm nhưng thứ tự khác nhau vẫn cho cùng x, nên vector này không giữ được thứ tự hành vi.',
 165: 'Trong hệ số nghịch đảo của TF-IDF, N là số cửa sổ hoặc phiên trong kho tham chiếu, còn n(eᵢ) là số cửa sổ có loại sự kiện eᵢ; phải dùng cùng đơn vị đếm cho cả hai. Ví dụ minh họa: nếu N=10, A có trong 2 cửa sổ và B có trong cả 10, thì với cùng tần suất cục bộ, hệ số nghịch đảo của A là ⟦log(1+10/2)=log 6⟧, lớn hơn hệ số của B là ⟦log(1+10/10)=log 2⟧, bất kể dùng cùng một cơ số log hợp lệ. Độ hiếm chỉ điều chỉnh trọng số thống kê, không biến A thành dấu hiệu tấn công.',
 166: 'Ở đây W là cửa sổ đang xét; M là số loại sự kiện trong tập mẫu; p(eᵢ) là số lần loại eᵢ xuất hiện chia cho tổng số sự kiện của W. Các loại không xuất hiện đóng góp 0 theo quy ước giới hạn ⟦0 log₂ 0=0⟧. Ví dụ minh họa: W gồm A, A, B, B thì p(A)=p(B)=0,5 và ⟦H(W)=−[0,5 log₂(0,5)+0,5 log₂(0,5)]=1 bit⟧; bốn sự kiện đều là A cho H(W)=0. Entropy đo độ phân tán loại sự kiện, không tự kết luận cửa sổ là tấn công.',
 168: 'P gồm các phương PCA được giữ lại và có các cột trực chuẩn; x là vector đã tâm hóa, I là ma trận đơn vị cùng chiều, còn xₐ là phần không được P giải thích. Ví dụ minh họa: với ⟦x=(3,2)ᵀ, P=(1,0)ᵀ⟧, phép chiếu giữ lại (3,0)ᵀ nên ⟦xₐ=(0,2)ᵀ, ‖xₐ‖²=4⟧. Nếu ngưỡng minh họa γα=3 thì 4>3 gắn cờ lệch khỏi không gian nền; cờ này không xác nhận nguyên nhân độc hại.',
 170: 'A là ma trận hệ số các quan hệ bất biến, x là vector số đếm sự kiện và 0 là vector không tương ứng; từng hàng của Ax kiểm tra một quan hệ tuyến tính. Ví dụ minh họa: ⟦A=[1,−1], x=(2,2)ᵀ⟧ cho ⟦Ax=0⟧, còn x=(2,1)ᵀ cho Ax=1, tức quan hệ “hai loại xuất hiện bằng nhau” bị vi phạm. Quan hệ chỉ có giá trị nếu được học và kiểm định trong đúng ngữ cảnh hệ thống; vi phạm không tự chứng minh tấn công.',
 175: 'Eₜ là tập g loại sự kiện có xác suất dự đoán cao nhất cho bước t, không phải xác suất của chính sự kiện quan sát. Ví dụ minh họa: nếu mô hình gán A: 0,6; B: 0,3; C: 0,1 và g=2, thì Eₜ={A,B}; quan sát C nằm ngoài tập này và là ứng viên bất thường. Việc gắn nhãn an ninh cần bằng chứng và ngưỡng đánh giá riêng.',
 177: 'Ví dụ minh họa cho chú ý tự thân: hai điểm Query–Key bằng nhau cho trọng số softmax 0,5 và 0,5; đầu ra là trung bình có trọng số của hai vector Value. Trọng số cho biết mô hình đang tổng hợp thông tin từ đâu trong cửa sổ, không chỉ ra quan hệ nhân quả giữa hai sự kiện.',
 182: 'Trong bộ ký hiệu đồ thị, ϕ gán mỗi đỉnh vào một kiểu trong Tᵥ, ψ gán mỗi cạnh vào một kiểu trong Tₑ, còn τ gán mốc thời gian cho cạnh/sự kiện quan sát. Ví dụ khái niệm: một tiến trình đọc một tệp tạo cạnh có hướng kiểu read tại thời điểm ghi nhận; cạnh thể hiện quan hệ phụ thuộc đã quan sát, không chứng minh nội dung tệp gây ra hành vi tiếp theo.',
 222: 'Bộ sáu tách “khi nào, loại gì, ai, tác động lên gì, bằng thao tác nào, kèm tham số nào” cho một sự kiện; ký hiệu ⊥ nghĩa là không có đối tượng đích được ghi nhận. Ví dụ minh họa: tại giây 10, tiến trình P đọc tệp F với tham số đường dẫn đã chuẩn hóa; đây là một sự kiện, không phải kết luận rằng P độc hại.',
 224: 'Update chỉ dùng trạng thái trước Sₜ₋₁ và sự kiện vừa đến eₜ để tạo Sₜ; fθ đọc trạng thái này thành vector zₜ gồm d số thực. Ví dụ khái niệm: từ trạng thái rỗng, sau sự kiện đọc tệp, bộ nhớ có thể lưu tóm tắt rằng tiến trình đã tương tác với tệp. Công thức không quy định chính xác nội dung bộ nhớ hay giá trị vector nếu chưa biết tham số đã học.',
 234: 'Utility là thước đo hạ nguồn phải chọn và khóa trước đánh giá; εmargin là biên dung sai cùng đơn vị với Utility. Bất đẳng thức đang viết cho phép kém góc nhìn đơn tốt nhất trong biên này, nên chỉ phát biểu mức không thua quá biên, không tự chứng minh vượt trội nghiêm ngặt. Ví dụ minh họa: điểm đơn tốt nhất 0,80, εmargin=0,02 và điểm đa góc nhìn 0,79 vẫn thỏa ⟦0,79>0,80−0,02⟧. Các ngưỡng phương sai và thông tin tương hỗ cũng là tiêu chí dự kiến kiểm định, chưa phải kết quả.',
 237: 'T là phép biến đổi cú pháp được xác định trước là vô hại; εinv chặn khoảng cách giữa hai vector trên cùng thang đo đã khóa. Ví dụ minh họa: nếu chỉ đổi định dạng thời gian nhưng giữ nguyên sự kiện, khoảng cách biểu diễn 0,1 nhỏ hơn ngưỡng minh họa 0,2 sẽ thỏa điều kiện hình học. Điều đó không chứng minh mọi biến đổi T đều an toàn; điều kiện thông tin về S cần phép ước lượng và kiểm định riêng.',
 239: 'Δt(eₜ) là độ trễ xử lý một sự kiện; Tbudget phải dùng cùng đơn vị thời gian. Mem(Sₜ) và Mmax phải đo cùng đơn vị bộ nhớ. Ví dụ minh họa: giới hạn 5 mili-giây và 100 MiB được thỏa ở một bước có độ trễ 4 mili-giây, bộ nhớ 80 MiB; ký hiệu ∀t đòi hỏi điều kiện đúng ở mọi bước, không chỉ một phép đo mẫu.',
 241: 'Hai vế so sánh cùng một điểm vận hành với đường cơ sở trên hai thước đo đã khóa: Utility càng cao càng tốt, PrivacyLoss càng thấp càng tốt. Ví dụ minh họa: ứng viên (0,82; 0,25) so với cơ sở (0,80; 0,30) thỏa cả hai chiều; các số này hoàn toàn giả định, không phải bằng chứng H5 đã đạt. Cần phép đo quyền riêng tư từ mô hình đe dọa cụ thể.',
 245: 'tlast(v) là lần tương tác gần nhất của v và τTTL là thời lượng sống theo cùng đơn vị thời gian. Ví dụ minh họa: nếu v hoạt động lần cuối ở giây 10 và τTTL=5 giây, tại giây 14 v còn trong tập hoạt động, tại giây 16 thì không. Ký hiệu |Sₜ| được hiểu là số mục trạng thái được lưu; để khẳng định chặn bộ nhớ vật lý phải đo thêm Mem(Sₜ) bằng byte như ER1, vì số mục không quyết định số byte.',
 248: 'Watermark lấy mốc thời gian sự kiện lớn nhất đã thấy rồi trừ dung sai đến muộn δdelay; mọi đại lượng thời gian phải cùng đơn vị. Ví dụ minh họa: mốc lớn nhất là giây 100 và δdelay=5 giây thì ⟦twm=100−5=95 giây⟧ giây. Một sự kiện mang mốc 93 giây đã ở phía sau watermark và cần xử lý theo chính sách đến muộn, không được âm thầm đảo lại quá khứ.',
 251: 'Cstep là tổng chi phí cho một bước, còn Cseq, Cgraph, Cstate và Calign là chi phí từng nhánh với đầu vào và cấu trúc dữ liệu đã nêu. Ví dụ minh họa: nếu giữ d và số tầng cố định, tăng độ dài cửa sổ L từ 10 lên 20 làm số cặp chú ý từ khoảng 100 lên 400; đó là tỷ lệ của số hạng bậc hai, không phải cam kết thời gian chạy đầu-cuối.',
 270: 'Retain(x) là chỉ báo nhận giá trị 1 khi trường x thuộc kiểu an ninh đã đặc tả hoặc khớp quy tắc tiền nghiệm; Normalize(x)=ϕ(x) chỉ chuẩn hóa biểu diễn của trường, không xóa đặc trưng có ý nghĩa an ninh. Ví dụ khái niệm: một đường dẫn cấu hình được giữ lại và chuẩn hóa dạng viết; nhãn “giữ lại” không phải phán quyết đường dẫn đó độc hại.',
 299: 'πψ dùng khóa hoặc tham số ψ trong phạm vi liên kết đã chọn: cùng thực thể trong cùng phạm vi phải cho cùng mã, còn việc đổi phạm vi/khóa có thể cho mã khác. Ví dụ khái niệm: hai lần truy cập của cùng một tiến trình trong một phiên vẫn nối được với nhau; điều này không bảo đảm chống tái định danh từ mẫu hành vi hay tạo ra quyền riêng tư vi sai.',
 303: 'ParamProtect chỉ nhận pᵢ sau phân loại chính sách: loại bỏ trường đã biết cần loại, giữ token an ninh đã chuẩn hóa và dùng token kiểu an toàn cho giá trị chưa biết. Đây là mô tả biến đổi dữ liệu đầu vào, chưa là chứng minh rằng z không rò rỉ thuộc tính nhạy cảm.',
 314: 'Wₛ là chuỗi gần, Wₘ là ngữ cảnh trung hạn và Wₗ là bản tóm tắt lịch sử cũ có chặn; chúng khác nhau về thông tin giữ lại. Ví dụ minh họa: ba sự kiện mới nhất nằm ở Wₛ, các tương tác trong một giờ nằm ở Wₘ, còn lịch sử xa hơn chỉ còn bộ đếm nén trong Wₗ. Các khoảng này là ví dụ thiết kế, không phải giá trị đã đo hoặc khóa trong thí nghiệm.'
}

# Phần còn lại được thêm dưới đây theo đúng chỉ số baseline.
NOTES.update({
 326: 'Tất cả các số hạng cộng vào xᵢ phải cùng kích thước dmodel; tổng trên pᵢ chỉ chạy qua các token tham số còn được giữ sau bảo vệ quyền riêng tư. Ví dụ minh họa ở hai chiều: nếu nhúng kiểu là (1,0), nhúng thao tác là (0,1) và các thành phần khác bằng 0, thì ⟦xᵢ=(1,1)⟧. Với mã thời gian, t và ω phải dùng đơn vị tương thích; riêng một thành phần cos có tính tuần hoàn nên không thể khôi phục duy nhất mọi khoảng thời gian từ một giá trị mã hóa.',
 330: 'Mₑᵥₑₙₜ là tập vị trí bị che, |Mₑᵥₑₙₜ| là số vị trí đó; chỉ xác suất của lớp đúng τᵢ đi vào log. Ví dụ minh họa: một vị trí có xác suất lớp đúng 0,8 tạo mất mát ⟦−ln(0,8)≈0,223⟧ khi dùng log tự nhiên như hàm cross-entropy. Mất mát thấp chỉ nói mô hình đoán token bị che tốt hơn theo mục tiêu này, không chứng minh đã nhận ra tấn công.',
 332: '⟦Pᵢᵐᵃˢᵏ⟧ là tập các khe tham số thực sự bị che và không phải khe đệm ở sự kiện i; mẫu số của công thức là tổng số khe như vậy trong lô. Mục tiêu của mỗi khe là token tham số đã bảo vệ, không phải giá trị nhạy cảm thô. Ví dụ minh họa: nếu hai khe hợp lệ bị che có xác suất lớp đúng lần lượt 0,8 và 0,5, trung bình cross-entropy trên hai khe là ⟦[−ln(0,8)−ln(0,5)]/2≈0,458⟧; khe đệm không tham gia. Công thức trung bình chỉ dùng khi có ít nhất một khe hợp lệ; nếu không, triển khai trả mất mát 0 cho tác vụ này. Khi số khe hợp lệ ở từng sự kiện khác nhau, phải dùng đúng mẫu số là số khe được tính trong triển khai để tránh thay đổi trọng số giữa các sự kiện.',
 337: 'Δtᵢ là khoảng cách thời gian không âm giữa hai sự kiện kề nhau; log(1+Δtᵢ) yêu cầu Δt đo theo cùng đơn vị thời gian đã quy ước. Đầu hồi quy được mô tả là nhận cặp trạng thái ẩn liên tiếp, còn Lδ là mất mát Huber với δ=1. Ví dụ minh họa: khoảng cách 2 đơn vị cho đích ⟦ln(3)≈1,099⟧; nếu dự đoán 1,000 thì sai số khoảng 0,099 và phần mất mát bậc hai là khoảng 0,0049. Đây là lỗi dự đoán thời gian, không phải điểm nghi vấn an ninh.',
 342: 'αᵢ là trọng số chuẩn hóa trên L vị trí nên không âm và có tổng bằng 1; Wproj chuyển mỗi hᵢ từ dmodel sang dseq trước khi cộng. Ví dụ minh họa: với hai vị trí có trọng số 0,25 và 0,75, ⟦h₁=(1,0), h₂=(0,2), Wproj=I⟧, ta được ⟦zseq=(0,25;1,5)⟧. Trọng số nói vị trí nào được dùng nhiều trong phép tổng hợp, không phải xác suất vị trí đó gây ra tấn công.',
 360: 'λ là tốc độ suy giảm có đơn vị nghịch đảo đơn vị thời gian của t; để trọng số không vượt 1 cần xét cạnh đã xảy ra với t≥tₑ. Ví dụ minh họa: nếu λ=ln(2) mỗi giờ, sau một giờ trọng số từ 1 giảm còn ⟦exp(−ln 2)=0,5⟧. Đây là chính sách ưu tiên cạnh cũ/mới, không xóa bỏ chứng cứ gốc hay xác định quan hệ nhân quả.',
 378: 'Msg tạo thông điệp từ hai trạng thái trước sự kiện, độ trễ, kiểu quan hệ và thuộc tính cạnh; Agg gộp các thông điệp đến cùng đỉnh u, rồi Update sinh trạng thái mới. Ví dụ minh họa: nếu một cấu hình chọn phép cộng và nhận hai thông điệp (1,0) và (0,2), thông điệp gộp là (1,2). Không thể tính giá trị hᵤ mới nếu chưa biết hàm Update và trọng số đã học; cạnh được dùng ở đây vẫn chỉ là phụ thuộc quan sát được.',
 387: 'Ba số hạng đồ thị xử lý ba câu hỏi khác nhau: tái tạo thuộc tính đỉnh đã che, đoán loại cạnh đã che và dự đoán khoảng thời gian. Ví dụ minh họa: một đỉnh có vector đích (1,1), dự đoán (1,2) cho sai số bình phương ⟦(1−1)²+(2−1)²=1⟧; một lớp cạnh đúng được dự đoán với xác suất 0,8 cho mất mát ⟦−ln(0,8)≈0,223⟧. Các giá trị chỉ kiểm tra mục tiêu tự giám sát, không xác nhận đồ thị ghi lại đầy đủ hành vi tấn công.',
 395: 'Readoutgraph gán trọng số cho các trạng thái đỉnh đang hoạt động rồi chiếu và cộng chúng thành một vector dgraph chiều. Ví dụ minh họa: nếu có hai đỉnh, trọng số chuẩn hóa đều 0,5, phép chiếu là đồng nhất và trạng thái lần lượt là (1,0), (0,2), thì ⟦zgraph=(0,5;1)⟧. Đây là bản tóm tắt của đồ thị quan sát trong Wₘ; nó không giữ nguyên mọi cạnh hay chứng minh luồng nhân quả.',
 401: 'Trong Bảng 2.2, L là số sự kiện của cửa sổ chuỗi, Nlayers là số tầng Transformer, d là chiều trạng thái ẩn và dff là chiều tầng truyền thẳng; E_W là tập cạnh được xử lý trong cửa sổ, Vupd là tập đỉnh được cập nhật. dseq và dgraph là chiều hai vector đầu ra. Ví dụ minh họa: giữ các chiều và số tầng cố định, tăng L từ 10 lên 20 làm riêng số cặp chú ý tăng từ 100 lên 400; giữ d cố định và gấp đôi số cạnh được xử lý làm số hạng phụ thuộc card(E_W) xấp xỉ gấp đôi. Ký hiệu O chỉ tốc độ tăng theo giả định của từng hàng, không phải độ trễ hay bộ nhớ đo được của toàn hệ thống.',
 416: 'Hai đầu chiếu có thể nhận vector gốc khác số chiều nhưng đều phải xuất dproj chiều để phép gióng hàng có nghĩa. Ví dụ khái niệm: vector chuỗi hai chiều và vector đồ thị ba chiều có thể cùng được chiếu về không gian bốn chiều; các ma trận ở hai nhánh vì vậy có kích thước đầu vào khác nhau. Gần nhau trong không gian chiếu không buộc hai vector gốc mất hết thông tin riêng.',
 426: 'B là số cặp chuỗi–đồ thị tương ứng trong lô; mỗi hạng tử là bình phương khoảng cách Euclid giữa hai vector chiếu cùng dproj chiều. Ví dụ minh họa với hai cặp: cặp thứ nhất lệch một đơn vị ở một chiều, cặp thứ hai trùng nhau; khi đó ⟦Linv=(1+0)/2=0,5⟧. Chỉ có độ gần trong không gian chiếu được tối ưu, chưa có chứng cứ về tính đúng an ninh.',
 428: 'P là ma trận B hàng và dproj cột; p_:,j là cột j, γ là độ lệch chuẩn tối thiểu và ε tránh căn của số 0. Công thức dùng phương sai mẫu nên cần B≥2. Ví dụ minh họa với B=2, một cột (0,2) có phương sai mẫu 2, độ lệch chuẩn xấp xỉ 1,414 nên không bị phạt khi γ=1; cột (0,0) có độ lệch chuẩn xấp xỉ 0,01 khi ε=10⁻⁴ và bị phạt khoảng 0,99. Số hạng này chống sụp đổ từng chiều trong lô, không bảo đảm thông tin an ninh còn nguyên.',
 434: 'C(P) là ma trận dproj×dproj; chỉ các phần tử ngoài đường chéo của nó đi vào Lcov, còn chuẩn Frobenius bình phương cộng bình phương mọi phần tử đó. Ví dụ minh họa: với B=2 và hai vector chiếu (0,0), (2,2), hiệp phương sai ngoài đường chéo bằng 2 ở cả hai ô; do đó ⟦Lcov=(2²+2²)/2=4⟧. Phạt này giảm tương quan tuyến tính giữa các chiều, không chứng minh chúng độc lập thống kê hoặc có nghĩa an ninh riêng.',
 441: 'ρoverlap là tỷ lệ Jaccard giữa phần giao và phần hợp của phạm vi tương ứng đã xác định; nó chỉ được tính khi cả hai góc nhìn hiện diện. Ví dụ minh họa: hai phạm vi có 2 thực thể chung trong 4 thực thể hợp thì ρoverlap=0,5; nếu Linv=2, số hạng gióng hàng có trọng số là 1. Giảm trọng số không tự sửa được cặp ghép sai về thời gian hoặc thực thể.',
 472: 'Lpreserv giữ các tác vụ tự giám sát của cả hai nhánh; Lfuse-rec yêu cầu vector dung hợp tái tạo gần biểu diễn gốc nhưng stopgrad chỉ chặn đường gradient ở đích, không thay đổi giá trị số của sai số. Ví dụ minh họa với các giá trị mất mát giả định Linv=0,1, hai Lvar đều 0,1, hai Lcov đều 0, Lpreserv=0,2, Lfuse-rec=0,3 và trọng số tham chiếu đã nêu, ta được ⟦LStage-A=25×0,1+25×(0,1+0,1)+0,2+0,3=8,0⟧. Giá trị 8,0 chỉ là phép cộng minh họa, không đo chất lượng phát hiện.',
 478: 'qseq và qgraph gồm cờ có/không góc nhìn cùng các đại lượng chất lượng quan sát; Cov_event, Cov_graph và Density_edge là các chỉ báo độ phủ/mật độ dự kiến, chưa được công thức này khóa cách đo nên không thể thay số cho q một cách tái lập. Với riêng cổng đã biết điểm số, ví dụ minh họa sseq=0, sgraph=ln 3 và τ=0,05 cho ⟦wrelseq=0,05+0,90×1/(1+3)=0,275⟧, wrelgraph=0,725. Đây là trọng số dung hợp của mô hình, không phải xác suất góc nhìn nào “đúng” về an ninh.',
 482: 'PCGrad chỉ chiếu khi hai gradient trên cùng tập tham số chia sẻ có tích vô hướng âm; mẫu số là bình phương độ dài của gpreserv và khi có xung đột âm thì gpreserv khác 0. Ví dụ minh họa: ⟦galign=(1,−1), gpreserv=(−1,0)⟧ có tích vô hướng −1; trừ thành phần đối kháng cho ⟦galign,proj=(0,−1)⟧ và tích vô hướng mới bằng 0. Phép chiếu cục bộ này không bảo đảm hai mục tiêu đều cải thiện sau cả quá trình huấn luyện.',
 493: 'Trong túi có K thể hiện, các điểm chú ý được chuẩn hóa để aᵢ≥0 và tổng bằng 1; zbag là trung bình có trọng số rồi đầu phân lớp cho xác suất nhãn túi. Ví dụ minh họa: hai điểm chú ý bằng nhau cho a₁=a₂=0,5; nếu logit túi bằng 0 thì xác suất dự đoán là 0,5 và nhãn thật 1 cho mất mát ⟦−ln(0,5)≈0,693⟧. Trọng số aᵢ chỉ là tín hiệu gợi ý xem xét thể hiện, không phải xác suất tấn công của sự kiện i.',
 509: 'Pfuse đưa hai vector về cùng dcross chiều; tích Hadamard nhân từng tọa độ, còn mseq và mgraph chặn nhánh bị khuyết trước khi cộng rồi chuẩn hóa. Ví dụ minh họa: nếu ⟦useq=(1,2), ugraph=(3,4)⟧ thì ⟦ucross=(3,8)⟧; chưa thể tính zmv nếu không biết các ma trận Wout, trọng số cổng và LayerNorm. Tương tác lớn ở một tọa độ không tự có nghĩa là bằng chứng tấn công.',
 518: 'B là số cặp trong lô, K là số thể hiện trong túi, còn dseq, dgraph, dproj, dmv, dcross và datt là các kích thước vector/không gian tương ứng. Ví dụ minh họa: giữ nguyên các chiều, tăng K từ 10 lên 20 làm số lần tính điểm chú ý MIL xấp xỉ gấp đôi; tăng dproj thì phép hiệp phương sai có số phần tử bậc hai. Ký hiệu O mô tả tốc độ tăng theo giả định kiến trúc, không phải số mili-giây hay MiB thực đo.'
})

# Biên tập lại các đoạn quá dài của bản thử trước. Công thức thay số vẫn giữ
# trong dấu ⟦...⟧ để được dựng thành OMML có cấu trúc ở paragraph().
NOTES.update({
 127: 'Ở bốn biểu thức trên, P_t là phân phối tại thời điểm t; X là log quan sát, Y là nhãn và z là biểu diễn đã học. Ví dụ khái niệm: cùng dạng log X ở hai giai đoạn có thể đi kèm tỷ lệ nhãn Y khác nhau. Dấu khác nhau chỉ mô tả phân phối đổi, chưa chỉ ra nguyên nhân hay xác nhận tấn công.',
 164: 'Mỗi tọa độ của x đếm một loại sự kiện trong cửa sổ W. Ví dụ minh họa: nếu tập loại là A, B và cửa sổ là A, A, B thì ⟦x=(2,1)ᵀ⟧. Cửa sổ B, A, A cho cùng vector; phép đếm không giữ thứ tự.',
 165: 'N là số cửa sổ tham chiếu, còn n(eᵢ) là số cửa sổ chứa loại eᵢ. Ví dụ minh họa: N=10, A có trong 2 cửa sổ và B có trong 10; hệ số nghịch đảo lần lượt là ⟦log(1+10/2)=log 6⟧ và ⟦log(1+10/10)=log 2⟧. Loại hiếm được tăng trọng số thống kê, chưa phải dấu hiệu tấn công.',
 166: 'W là cửa sổ, M là số loại sự kiện, p(eᵢ) là tỷ lệ loại eᵢ trong W; loại không xuất hiện đóng góp 0 theo quy ước giới hạn. Ví dụ minh họa: W gồm A, A, B, B nên p(A)=p(B)=0,5. Khi thay số: ⟦H(W)=−[0,5 log₂(0,5)+0,5 log₂(0,5)]=1 bit⟧',
 170: 'A chứa hệ số của các quan hệ bất biến; x là vector số đếm, 0 là vector không. Ví dụ minh họa: ⟦A=[1,−1], x=(2,2)ᵀ⟧ cho ⟦Ax=0⟧; x=(2,1)ᵀ cho Ax=1, tức quan hệ “hai loại bằng nhau” bị vi phạm. Quan hệ phải được học và kiểm định trong ngữ cảnh hệ thống; vi phạm không tự xác nhận tấn công.',
 234: 'Utility là thước đo đã khóa trước đánh giá; εmargin là biên dung sai cùng đơn vị. Bất đẳng thức chỉ yêu cầu điểm đa góc nhìn không kém điểm đơn tốt nhất quá biên. Ví dụ minh họa: 0,79 vẫn thỏa ⟦0,79>0,80−0,02⟧. Đây chưa phải chứng cứ vượt trội; các điều kiện phương sai và thông tin cũng cần kiểm định riêng.',
 237: 'T là phép đổi cú pháp đã xác định trước là vô hại; εinv chặn khoảng cách giữa hai biểu diễn cùng thang đo. Ví dụ minh họa: đổi định dạng thời gian mà giữ sự kiện, khoảng cách 0,1 nhỏ hơn ngưỡng giả định 0,2. Điều này chỉ thỏa điều kiện hình học cho ví dụ đó, chưa chứng minh mọi T an toàn hoặc điều kiện thông tin về S.',
 326: 'Các số hạng của xᵢ đều có dmodel chiều; tổng tham số chỉ gồm token còn được giữ sau bảo vệ quyền riêng tư. Ví dụ minh họa ở hai chiều: nhúng kiểu (1,0) cộng nhúng thao tác (0,1), các phần khác bằng 0, cho ⟦xᵢ=(1,1)⟧. Mã thời gian cần đơn vị tương thích; một thành phần cos riêng lẻ không xác định duy nhất khoảng thời gian.',
 332: '⟦Pᵢᵐᵃˢᵏ⟧ là tập khe tham số bị che, không gồm khe đệm; mẫu số đếm tổng khe hợp lệ trong lô. Ví dụ minh họa: hai khe có xác suất lớp đúng 0,8 và 0,5 cho mất mát trung bình: ⟦[−ln(0,8)−ln(0,5)]/2≈0,458⟧',
 337: 'Δtᵢ là khoảng thời gian không âm giữa hai sự kiện; log(1+Δtᵢ) dùng đơn vị thời gian đã quy ước. Đầu hồi quy nhận cặp trạng thái liên tiếp và Lδ là mất mát Huber với δ=1. Ví dụ minh họa: Δtᵢ=2 cho đích ⟦ln(3)≈1,099⟧; dự đoán 1,000 cho mất mát xấp xỉ 0,0049. Đây là lỗi dự đoán thời gian, không phải điểm tấn công.',
 378: 'Msg tạo thông điệp từ trạng thái trước sự kiện và thuộc tính cạnh; Agg gộp thông điệp đến đỉnh u, rồi Update tạo trạng thái mới. Ví dụ minh họa: nếu chọn phép cộng, hai thông điệp (1,0) và (0,2) gộp thành (1,2). Chưa thể tính trạng thái mới khi không biết Update và trọng số đã học; cạnh chỉ là quan hệ quan sát được.',
 387: 'Ba mất mát đồ thị lần lượt tái tạo thuộc tính đỉnh, dự đoán loại cạnh và khoảng thời gian. Ví dụ minh họa: đích (1,1), dự đoán (1,2) cho sai số ⟦(1−1)²+(2−1)²=1⟧; xác suất lớp cạnh đúng 0,8 cho ⟦−ln(0,8)≈0,223⟧. Đây là kiểm tra tác vụ tự giám sát, không xác nhận đồ thị đã ghi đủ hành vi tấn công.',
 401: 'Trong Bảng 2.2, L là độ dài chuỗi, ⟦Nlayers⟧ là số tầng, d và ⟦dff⟧ là chiều trạng thái và tầng truyền thẳng; ⟦E_W⟧ và ⟦Vupd⟧ là tập cạnh và đỉnh được xử lý, còn ⟦dseq⟧ và ⟦dgraph⟧ là chiều đầu ra. Ví dụ minh họa: giữ các chiều cố định, L tăng từ 10 lên 20 làm số cặp chú ý tăng từ 100 lên 400. Ký hiệu O nói về bậc tăng trưởng theo giả định, không phải độ trễ đo được.',
 428: 'P có B hàng, dproj cột; p_:,j là cột j, γ là độ lệch chuẩn tối thiểu và ε tránh căn của 0. Phương sai mẫu cần B≥2. Ví dụ minh họa: với B=2, cột (0,2) có độ lệch chuẩn khoảng 1,414, không bị phạt khi γ=1; cột (0,0) với ε=10⁻⁴ bị phạt khoảng 0,99. Hình phạt chống sụp đổ từng chiều, chưa bảo đảm thông tin an ninh.',
 434: 'C(P) là ma trận dproj×dproj; Lcov chỉ cộng bình phương các phần tử ngoài đường chéo. Ví dụ minh họa: B=2 với hai vector (0,0), (2,2) cho hai phần tử ngoài đường chéo đều bằng 2, nên ⟦Lcov=(2²+2²)/2=4⟧. Phạt này giảm tương quan tuyến tính, không chứng minh độc lập thống kê.',
 472: 'Lpreserv giữ tác vụ tự giám sát; Lfuse-rec yêu cầu vector dung hợp tái tạo hai biểu diễn gốc, còn stopgrad chỉ chặn gradient ở đích. Ví dụ minh họa: Linv=0,1, hai Lvar đều 0,1, hai Lcov bằng 0, Lpreserv=0,2, Lfuse-rec=0,3 với trọng số đã nêu cho: ⟦LStage-A=25×0,1+25×(0,1+0,1)+0,2+0,3=8,0⟧',
 478: 'qseq và qgraph chứa cờ hiện diện cùng chỉ báo chất lượng; Cov_event, Cov_graph, Density_edge chưa khóa phép đo nên chưa thể thay số cho q. Với điểm cổng giả định sseq=0, sgraph=ln 3, τ=0,05, ta có: ⟦wrelseq=0,05+0,90×1/(1+3)=0,275⟧',
 482: 'PCGrad chỉ chiếu hai gradient trên cùng tham số khi tích vô hướng âm; mẫu số là bình phương chuẩn gradient được giữ. Ví dụ minh họa: ⟦galign=(1,−1), gpreserv=(−1,0)⟧ có tích −1; chiếu cho ⟦galign,proj=(0,−1)⟧, tích mới bằng 0. Phép chiếu tại bước này không bảo đảm cả hai mục tiêu cùng cải thiện.',
 493: 'Trong túi K thể hiện, các trọng số chú ý không âm và cộng thành 1; zbag là tổng có trọng số để phân lớp túi. Ví dụ minh họa: hai trọng số bằng 0,5, logit túi bằng 0, nhãn thật 1 cho mất mát ⟦−ln(0,5)≈0,693⟧. Trọng số chỉ gợi ý thể hiện cần xem, không phải xác suất sự kiện là tấn công.',
 518: 'B là số cặp trong lô, K là số thể hiện; các d có chỉ số là chiều tương ứng của từng vector. Ví dụ minh họa: giữ các chiều cố định, K từ 10 lên 20 làm số điểm chú ý MIL xấp xỉ gấp đôi; tăng dproj làm số phần tử hiệp phương sai tăng bậc hai. Ký hiệu O mô tả bậc tăng, không phải mili-giây hay MiB đã đo.',
})

DISPLAY_EXAMPLES={
 'H(W)=−[0,5 log₂(0,5)+0,5 log₂(0,5)]=1 bit': 'Giá trị entropy là 1 bit. Nếu cả bốn sự kiện đều thuộc loại e₁ thì H(W)=0. Entropy đo độ phân tán, không xác nhận tấn công.',
 '[−ln(0,8)−ln(0,5)]/2≈0,458': 'Đích là token đã bảo vệ, không phải giá trị thô. Khi không có khe hợp lệ, triển khai trả 0; mất mát thấp chưa chứng minh mô hình hiểu an ninh.',
 'LStage-A=25×0,1+25×(0,1+0,1)+0,2+0,3=8,0': 'Giá trị 8,0 chỉ là phép cộng giả định, không phải kết quả phát hiện.',
 'wrelseq=0,05+0,90×1/(1+3)=0,275': 'Khi đó trọng số góc nhìn đồ thị là 0,725. Đây là trọng số dung hợp, không phải xác suất góc nhìn đúng về an ninh.',
}

# Viết ký hiệu trong lời giải thích theo cùng dạng toán với công thức gốc.
# Chỉ các tên kỹ thuật được kiểm duyệt ở đây mới được chuyển; không đụng vào
# các biểu thức đã nằm trong ⟦...⟧ và không biến mọi chữ cái thành math zone.
PROSE_SYMBOLS=(
 'Utility','PrivacyLoss','Update','Msg','Agg','ParamProtect','Readoutgraph','LayerNorm','stopgrad','cos',
 'Nlayers','dff','dmodel','dseq','dgraph','dproj','dcross','datt','dmv',
 'E_W','Vupd','Wproj','Lpreserv','Lfuse-rec','Linv','Lvar','Lcov','LStage-A',
 'qseq','qgraph','sseq','sgraph','wrelseq','wrelgraph','zseq','zgraph',
 'zbag','zmv','useq','ugraph','ucross','galign','gpreserv',
 'Cov_event','Cov_graph','Density_edge','Cstep','Cseq','Cgraph','Cstate',
 'Calign','Mmax','Tbudget','εinv','εmargin',
 'P_t','X','Y','z','x','W','M','N','P','I','d','b','g','u','v','L','A','B','C','F','K','T','S','t',
 'σ','γ','ε','λ','ϕ','ψ','τ','⊥','∀t',
 'n(eᵢ)','p(eᵢ)','eᵢ','e₁','e₂','e₃','N=10','p(e₁)=p(e₂)=0,5','H(W)=0','xₐ','(3,0)ᵀ','γα=3','4>3',
 'x=(2,1)ᵀ','Ax=1','g=2','Eₜ={e₁,e₂}','Eₜ','Tᵥ','Tₑ',
 'Sₜ₋₁','eₜ','Sₜ','fθ','zₜ','Δt(eₜ)','Mem(Sₜ)','|Sₜ|',
 'τTTL=5','τTTL','δdelay=5','δdelay','tlast(v)','Retain(x)','Normalize(x)=ϕ(x)','πψ','pᵢ',
 'Wₛ','Wₘ','Wₗ','xᵢ','|Mₑᵥₑₙₜ|','Mₑᵥₑₙₜ','τᵢ',
 'log(1+Δtᵢ)','Δtᵢ=2','Δtᵢ','Lδ','δ=1','αᵢ','hᵢ',
 't≥tₑ','λ=ln(2)','ε=10⁻⁴','B≥2','B=2','γ=1','C(P)','p_:,j','dproj×dproj',
 'ρoverlap=0,5','ρoverlap','τ=0,05','Linv=2','Linv=0,1',
 'Lpreserv=0,2','Lfuse-rec=0,3','sseq=0','sgraph=ln 3','mseq','mgraph',
 'Pfuse','Wout','q','O',
)
assert all(symbol in EXAMPLES for symbol in PROSE_SYMBOLS)
SYMBOL_RE=re.compile(r'(?<!\w)(?:'+ '|'.join(map(re.escape,sorted(PROSE_SYMBOLS,key=len,reverse=True))) +r')(?!\w)')
def mathify_prose(value):
    out=[];last=0
    for match in MATH_RE.finditer(value):
        out.append(SYMBOL_RE.sub(lambda m:'⟦'+m.group(0)+'⟧',value[last:match.start()]))
        out.append(match.group(0))
        last=match.end()
    out.append(SYMBOL_RE.sub(lambda m:'⟦'+m.group(0)+'⟧',value[last:]))
    return ''.join(out)
for index in (164,165,166,175):
    # Các loại sự kiện dùng đúng họ e_i của baseline; A/B/C ở bản cũ
    # là những đối tượng khác, không được mượn kiểu chữ cho tên ví dụ.
    NOTES[index]=re.sub(r'\bA\b','e₁',NOTES[index])
    NOTES[index]=re.sub(r'\bB\b','e₂',NOTES[index])
    NOTES[index]=re.sub(r'\bC\b','e₃',NOTES[index])
NOTES[170]=NOTES[170].replace('0 là vector không','⟦zero_vector⟧ là vector không')
NOTES[222]=NOTES[222].replace('tiến trình P đọc tệp F','một tiến trình đọc một tệp').replace('P độc hại','tiến trình đó độc hại')
NOTES[222]=re.sub(r'\bP\b','tiến trình đó',NOTES[222])
NOTES[222]=re.sub(r'\bF\b','tệp đó',NOTES[222])
NOTES[332]=NOTES[332].replace('⟦Pᵢᵐᵃˢᵏ⟧ là tập khe tham số bị che','Tập khe tham số trong mẫu số chỉ gồm các khe bị che')
NOTES[478]=NOTES[478].replace('thay số cho q','thay số cho các vector chất lượng')
NOTES[518]=NOTES[518].replace('các d có chỉ số','các ký hiệu chiều có chỉ số')
NOTES[360]=NOTES[360].replace('Ví dụ minh họa:','Ví dụ minh họa: dùng logarit tự nhiên,')
NOTES={index:mathify_prose(note.replace('Ví dụ minh họa','Ví dụ').replace('Ví dụ khái niệm','Ví dụ')
                         .replace('ngưỡng minh họa','ngưỡng giả định')
                         .replace('galign,proj=(0,−1)','galign^proj=(0,−1)')
                         .replace('Pfuse đưa hai vector','Hai phép chiếu dung hợp đưa hai vector')
                         .replace('các ma trận Wout','các ma trận đầu ra'))
       for index,note in NOTES.items()}

def added_expressions():
    for anchor, note in NOTES.items():
        for raw in MATH_RE.findall(note):
            yield anchor, raw
            if raw in DISPLAY_EXAMPLES:
                for tail in MATH_RE.findall(mathify_prose(DISPLAY_EXAMPLES[raw])):
                    yield anchor, tail

def math_run(value):
    r=etree.Element(f'{{{M}}}r')
    rp=etree.SubElement(r,Q('rPr'))
    fonts=etree.SubElement(rp,Q('rFonts'))
    fonts.set(Q('ascii'),'Cambria Math'); fonts.set(Q('hAnsi'),'Cambria Math')
    etree.SubElement(rp,Q('noProof'))
    t=etree.SubElement(r,f'{{{M}}}t'); t.text=value
    if value.startswith(' ') or value.endswith(' '):t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    return r

def fix_verified_math(mpp, time):
    # L_MPP: triển khai 3D lấy trung bình trên toàn bộ khe bị che không đệm,
    # không chia cho số sự kiện khi mỗi sự kiện có số khe khác nhau.
    f=mpp.find(f'{{{M}}}f')
    outer=mpp.find(f'{{{M}}}nary')
    if f is None or outer is None:raise RuntimeError('MPP structure changed')
    den=f.find(f'{{{M}}}den')
    den.clear()
    n=etree.SubElement(den,f'{{{M}}}nary')
    prop=etree.SubElement(n,f'{{{M}}}naryPr')
    etree.SubElement(prop,f'{{{M}}}chr').set(f'{{{M}}}val','∑')
    etree.SubElement(prop,f'{{{M}}}limLoc').set(f'{{{M}}}val','undOvr')
    etree.SubElement(prop,f'{{{M}}}supHide').set(f'{{{M}}}val','1')
    n.append(copy.deepcopy(outer.find(f'{{{M}}}sub')))
    etree.SubElement(n,f'{{{M}}}sup')
    e=etree.SubElement(n,f'{{{M}}}e')
    e.append(math_run('card('))
    ps=etree.SubElement(e,f'{{{M}}}sSubSup')
    for tag,val in (('e','P'),('sub','i'),('sup','mask')):
        slot=etree.SubElement(ps,f'{{{M}}}{tag}')
        slot.append(math_run(val))
    e.append(math_run(')'))
    inner=outer.find(f'{{{M}}}e/{{{M}}}nary')
    if inner is None:raise RuntimeError('MPP inner sum missing')
    p_candidates=[x for x in inner.find(f'{{{M}}}sub').iter(f'{{{M}}}sSubSup') if ''.join(t.text or '' for t in x.find(f'{{{M}}}e').iter(f'{{{M}}}t'))=='p']
    if len(p_candidates)!=1:raise RuntimeError('MPP parameter set not unique')
    pp=p_candidates[0]
    pp.find(f'{{{M}}}e').find(f'.//{{{M}}}t').text='P'
    pp.find(f'{{{M}}}sup').find(f'.//{{{M}}}t').text='mask'
    # L_time: đầu hồi quy được khai báo R^{2d}->R và nhận [h_i;h_{i+1}].
    hs=[x for x in time.iter(f'{{{M}}}sSubSup') if ''.join(t.text or '' for t in x.find(f'{{{M}}}e').iter(f'{{{M}}}t'))=='h']
    if len(hs)!=1:raise RuntimeError('time input h_i not unique')
    h=hs[0]; parent=h.getparent(); idx=parent.index(h)
    parent.insert(idx,math_run('['))
    other=copy.deepcopy(h)
    other.find(f'{{{M}}}sub').find(f'.//{{{M}}}t').text='i+1'
    parent.insert(idx+2,math_run('; '))
    parent.insert(idx+3,other)
    parent.insert(idx+4,math_run(']'))
def paragraphs(text, template_ppr, equation_ppr, *, anchor, source_style, keep_lines=False):
    result=[]
    p=etree.Element(Q('p'))
    if template_ppr is not None:p.append(copy.deepcopy(template_ppr))
    if keep_lines and p.find(Q('pPr')) is not None:etree.SubElement(p.find(Q('pPr')),Q('keepLines'))
    last=0
    for m in MATH_RE.finditer(text):
        if m.start()>last:
            chunk=text[last:m.start()]
            if m.group(1) in DISPLAY_EXAMPLES:chunk=chunk.rstrip()
            r=etree.SubElement(p,Q('r')); t=etree.SubElement(r,Q('t')); t.text=chunk; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        raw=m.group(1)
        if raw in DISPLAY_EXAMPLES:
            if p.find(Q('pPr')) is not None:etree.SubElement(p.find(Q('pPr')),Q('keepNext'))
            result.append(p)
            eq=etree.Element(Q('p'))
            if equation_ppr is not None:eq.append(copy.deepcopy(equation_ppr))
            if eq.find(Q('pPr')) is not None:etree.SubElement(eq.find(Q('pPr')),Q('keepNext'))
            display=etree.SubElement(eq,f'{{{M}}}oMathPara')
            display.append(source_style.apply(make_example(raw), anchor, raw))
            result.append(eq)
            tail=paragraphs(mathify_prose(DISPLAY_EXAMPLES[raw]),template_ppr,equation_ppr,
                            anchor=anchor,source_style=source_style,keep_lines=keep_lines)
            if len(tail)!=1:raise RuntimeError('Display follow-up unexpectedly contains another display')
            p=tail[0]
        else:
            p.append(source_style.apply(make_example(raw), anchor, raw))
        last=m.end()
    if last<len(text):
        r=etree.SubElement(p,Q('r')); t=etree.SubElement(r,Q('t')); t.text=text[last:]; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    result.append(p)
    return result

def replace_member(docx, payload):
    with tempfile.NamedTemporaryFile(delete=False,suffix='.docx',dir=docx.parent) as t:
        tmp=Path(t.name)
    try:
        with zipfile.ZipFile(docx) as src, zipfile.ZipFile(tmp,'w') as dst:
            for info in src.infolist():
                dst.writestr(info,payload if info.filename=='word/document.xml' else src.read(info.filename))
        tmp.replace(docx)
    finally:
        if tmp.exists():tmp.unlink()

def main():
    got=hashlib.sha256(DOCX.read_bytes()).hexdigest()
    if got!=EXPECTED:raise SystemExit(f'Baseline mismatch: {got}')
    with zipfile.ZipFile(DOCX) as z:root=etree.fromstring(z.read('word/document.xml'))
    body=root.find(Q('body'))
    original_math=list(root.iter(f'{{{M}}}oMath'))
    originals=[hashlib.sha256(etree.tostring(x,method='c14n')).hexdigest() for x in original_math]
    targets={i:body[i].find(f'.//{{{M}}}oMath') for i in (332,337)}
    if any(v is None for v in targets.values()):raise RuntimeError('Math correction targets missing')
    caption=body[462]
    if 'Kiểm toán các khối tham số' not in ''.join(caption.itertext()):
        raise RuntimeError('Table 2.4 caption moved')
    template_ppr=body[165].find(Q('pPr'))
    equation_ppr=body[166].find(Q('pPr'))
    source_style=SourceMathStyle(body)
    fix_verified_math(targets[332],targets[337])
    for idx in sorted(NOTES,reverse=True):
        if not 111<=idx<523:raise ValueError(f'Out of scope index {idx}')
        for p in reversed(paragraphs(NOTES[idx],template_ppr,equation_ppr,anchor=idx,source_style=source_style,
                keep_lines=idx in (165,166,168,177,234,248,251,332,342,401,472,478,509))):
            body.insert(idx+1,p)
    # Ngắt trang cứng của caption Bảng 2.4 chỉ hữu ích ở bản nền 120 trang;
    # với chú giải mới nó để gần trọn một trang trống. Giữ các thuộc tính khác.
    ppr=caption.find(Q('pPr'))
    page_break=ppr.find(Q('pageBreakBefore')) if ppr is not None else None
    if page_break is None:raise RuntimeError('Expected original Table 2.4 page break missing')
    ppr.remove(page_break)
    current=[hashlib.sha256(etree.tostring(x,method='c14n')).hexdigest() for x in root.iter(f'{{{M}}}oMath')]
    n_new=sum(1 for _ in added_expressions())
    changed={original_math.index(targets[332]),original_math.index(targets[337])}
    unchanged=[originals[j] for j in range(len(originals)) if j not in changed]
    new_counter={h:current.count(h) for h in set(unchanged)}
    old_counter={h:unchanged.count(h) for h in set(unchanged)}
    if any(new_counter[h]<n for h,n in old_counter.items()):raise RuntimeError('Unapproved original OMML node changed')
    if len(current)!=len(originals)+n_new:raise RuntimeError('Unexpected math count')
    payload=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    replace_member(DOCX,payload)
    (ROOT/'docs/OMML-TYPOGRAPHY-SOURCE-MAP.json').write_text(
        json.dumps(source_style.matches,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'notes':len(NOTES),'new_omml':n_new,'original_omml':len(originals),'final_omml':len(current),'corrected_equations':2},ensure_ascii=False))
if __name__=='__main__':main()
