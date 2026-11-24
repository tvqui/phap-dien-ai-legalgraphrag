# Đánh giá hai nhánh Graph, ngày 22/11/2026

## Kết luận

Hai nhánh chạy đủ và có thể ghép theo các điều kiện được kiểm: 47/47 OK, 47/47 AI_JUDGED mỗi nhánh; comparison_key giống nhau; cấu hình thực tế chỉ khác graph.enabled sau khi bỏ đường dẫn vận hành. **Chưa chứng minh được lợi ích tăng đúng/đủ của mở rộng Graph trong phép thử này.** Không sửa source hoặc chấm lại trong bước phân tích.

## Kết quả tổng hợp thô (không chỉnh điểm)

| Chỉ số | Graph OFF | Graph ON | ON − OFF |
|---|---:|---:|---:|
| Điểm AI đúng | 0,9362 | 0,9468 | +0,0106 |
| Điểm AI đủ | 0,9340 | 0,9213 | −0,0128 |
| Điểm AI bám bằng chứng | 0,9362 | 0,9149 | −0,0213 |
| Recall nhóm căn cứ theo Gold của bộ đo | 0,6383 | 0,6383 | 0 |
| Thời gian trung bình pipeline | 31,126 giây | 29,328 giây | −1,797 giây |

Không coi điểm AI đúng tăng thành bằng chứng Graph tốt hơn. CI95 paired bootstrap của chênh lệch đúng là [-0,0319; 0,0638], chứa 0. Chênh lệch thời gian tổng có CI95 [-3,991; 0,948] giây, chứa 0; phiên/phần cứng dịch vụ/biến thiên suy luận có thể ảnh hưởng. Không suy luận Graph làm nhanh hơn từ hai lần chạy này. Recall nhóm là chỉ số căn cứ theo nhãn hiện có, không phải độ đúng pháp lý hay Recall@K thuần của retrieval.

Hai nhóm mục tiêu không thay đổi điểm giữa hai nhánh: 7 câu quan hệ/dẫn chiếu (AI đúng/đủ/bám nguồn đều 0,8571) và 16 câu điều kiện/ngoại lệ (đều 0,9375). Đây là giả thuyết chọn theo đầu vào, không phải bảo đảm chúng bắt buộc cần Graph.

## Graph thực sự làm gì?

- 45/47 câu không chạy vòng mở rộng ở nhánh ON.
- CD004 chạy một vòng, có 3 căn cứ được chấp nhận từ mở rộng: Điều 97 và Khoản 2 Điều 35 trong các bản văn bản hiện có. Chúng không được giữ vào gói bằng chứng cuối, không được trích dẫn; hai nhánh cùng từ chối do thiếu bằng chứng. Trace vẫn có gap wage_payment_principles. Chưa xác định từ dữ kiện này rằng nguyên nhân chỉ nằm ở Graph; cần đối chiếu selection/requirements/audit.
- CD007 chạy hai vòng qua quan hệ REFERENCES nhưng không có căn cứ mới được chấp nhận. Câu trả lời giống hệt nhánh OFF; AI chấm đúng/đủ/bám nguồn đều 1 ở cả hai nhánh.
- Không có căn cứ từ vòng mở rộng được trích trong đáp án của bất kỳ câu nào.
- Bộ evidence_id trích dẫn giống nhau ở cả 47 cặp; chuỗi answer giống hệt ở 46/47 cặp. Câu khác chuỗi answer là CD009. Trạng thái trả lời của từng cặp đều giống nhau.

Phép thử chỉ tắt/bật mở rộng adaptive. Các kênh phân cấp, exact/profile, case/community và issue anchors dùng chung vẫn được giữ, nên không thể kết luận mọi chức năng/dữ liệu Graph đều không có ích.

## Dấu hiệu judge không nhất quán cần xử lý trước khi diễn giải điểm

1. **MR002**: hai nhánh có cùng câu “Không thể tạo câu trả lời có trích dẫn được xác minh.”, cùng claims/citations/questions/parts/warnings. Graph không mở rộng. Judge ON cho correctness=1 nhưng OFF cho 0; ngay lý do ON cũng nói không trả lời được yêu cầu. Completeness/evidence_support đều 0 ở cả hai. Đây không phải bằng chứng Graph cải thiện.
2. **TD003**: hai nhánh có cùng câu trả lời hỏi bổ sung, cùng cả ba câu hỏi bổ sung và các trường công khai khác. Graph không mở rộng. Judge ON chấm đúng=0,5, đủ=0,4, bám nguồn=0; OFF chấm cả ba=1. Không quy kết chênh lệch này cho Graph.

Toàn bộ chênh lệch AI đúng giữa các nhánh nằm ở hai câu trên; chênh lệch đủ/bám nguồn nằm ở TD003. Giữ nguyên điểm gốc để minh bạch, không âm thầm sửa hoặc chọn nhánh chấm có lợi.

## 47 OK có nghĩa gì?

47 OK là hoàn tất lượt gọi pipeline; không đồng nghĩa 47 câu đủ căn cứ hoặc đúng luật. Mỗi nhánh có 33 PARTIAL_ALLOWED, 11 NEED_MORE_FACTS, 3 INSUFFICIENT_EVIDENCE. Có 33 câu có claims; 14 câu không có trích dẫn. Trace mỗi nhánh vẫn có 1 OLLAMA_TIMEOUT và 1 SEMANTIC_CLAIM_REJECTED được xử lý bên trong pipeline. Nhãn DRAFT và artifact PROVISIONAL vẫn giữ nguyên; PARTIAL_ALLOWED có thể liên quan chính sách dữ liệu, không tự suy ra tất cả những câu này sai.

## Nên làm gì tiếp?

Giữ hai ZIP làm kết quả thí nghiệm trung thực; không cần chạy lại y nguyên chỉ để tìm điểm tăng. Nếu tiếp tục cải tiến, trước tiên rà soát (1) Graph đã đưa về căn cứ nào nhưng selection không giữ, (2) gap thực tế có được quan hệ trong artifact hỗ trợ không, (3) tính nhất quán và cách judge chấm câu từ chối/hỏi bổ sung. Chỉ sau khi có thay đổi cơ chế có kiểm thử mới chạy một phiên bản thí nghiệm mới, giữ riêng các kết quả. Không ép Graph chạy mọi câu hoặc chọn riêng câu Graph thắng để làm kết luận chính.

Các bảng CSV/JSON và đối chiếu từng câu nằm cùng thư mục. File nguồn ZIP giữ nguyên; không gọi API và không sửa code ONLINE trong lượt đánh giá này.
