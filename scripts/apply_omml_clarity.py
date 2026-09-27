from __future__ import annotations
import copy, hashlib, json, re, sys, tempfile, zipfile
from pathlib import Path
from lxml import etree


ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from omml_helper import omath
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
 248: 'Watermark lấy mốc thời gian sự kiện lớn nhất đã thấy rồi trừ dung sai đến muộn δdelay; mọi đại lượng thời gian phải cùng đơn vị. Ví dụ minh họa: mốc lớn nhất là giây 100 và δdelay=5 giây thì ⟦twm=100−5=95 giây⟧. Một sự kiện mang mốc 93 giây đã ở phía sau watermark và cần xử lý theo chính sách đến muộn, không được âm thầm đảo lại quá khứ.',
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
def paragraph(text, template_ppr):
    p=etree.Element(Q('p'))
    if template_ppr is not None:p.append(copy.deepcopy(template_ppr))
    last=0
    for m in MATH_RE.finditer(text):
        if m.start()>last:
            r=etree.SubElement(p,Q('r')); t=etree.SubElement(r,Q('t')); t.text=text[last:m.start()]; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
        p.append(copy.deepcopy(omath(m.group(1))))
        last=m.end()
    if last<len(text):
        r=etree.SubElement(p,Q('r')); t=etree.SubElement(r,Q('t')); t.text=text[last:]; t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    return p

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
    for idx in sorted(NOTES,reverse=True):
        if not 111<=idx<523:raise ValueError(f'Out of scope index {idx}')
        p=paragraph(NOTES[idx],template_ppr)
        body.insert(idx+1,p)
    # Bảng 2.4 có ngắt trang bắt buộc từ bản nền. Sau khi thêm chú giải,
    # ngắt này bỏ lại gần cả một trang trắng trước bảng; để Word tự đặt bảng.
    ppr=caption.find(Q('pPr'))
    page_break=ppr.find(Q('pageBreakBefore')) if ppr is not None else None
    if page_break is None:raise RuntimeError('Table 2.4 page break missing')
    ppr.remove(page_break)
    fix_verified_math(targets[332],targets[337])
    current=[hashlib.sha256(etree.tostring(x,method='c14n')).hexdigest() for x in root.iter(f'{{{M}}}oMath')]
    n_new=sum(len(MATH_RE.findall(s)) for s in NOTES.values())
    changed={original_math.index(targets[332]),original_math.index(targets[337])}
    unchanged=[originals[j] for j in range(len(originals)) if j not in changed]
    new_counter={h:current.count(h) for h in set(unchanged)}
    old_counter={h:unchanged.count(h) for h in set(unchanged)}
    if any(new_counter[h]<n for h,n in old_counter.items()):raise RuntimeError('Unapproved original OMML node changed')
    if len(current)!=len(originals)+n_new:raise RuntimeError('Unexpected math count')
    payload=etree.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    replace_member(DOCX,payload)
    print(json.dumps({'notes':len(NOTES),'new_omml':n_new,'original_omml':len(originals),'final_omml':len(current),'corrected_equations':2},ensure_ascii=False))
if __name__=='__main__':main()
