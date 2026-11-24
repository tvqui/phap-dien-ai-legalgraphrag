# Đo vai trò mở rộng Graph trong Pháp Điển AI

Mục tiêu: kiểm tra **câu nào, đặc điểm nào được mở rộng Graph hỗ trợ**, mức thay đổi đúng/đủ/căn cứ và thời gian. Không bảo đảm trước Graph phải thắng; không sửa thuật toán ONLINE trong thư mục này.

## Chạy trên Kaggle: đưa lên những gì?

Có hai cách lấy code. **ZIP dùng được ngay, chưa cần commit/push.**

1. Import notebook **`Kaggle_Graph_120.ipynb`**.
2. Trong Add Input, thêm **`Graph_Study_Code.zip`** ở cùng thư mục này. Nếu Kaggle tự giải nén ZIP thành Dataset, notebook cũng tự tìm `GRAPH_CODE_SHA256.json` và kiểm SHA từng file trước khi chép code; không cần nén lại. Gói này chứa code, cấu hình đo và Gold120 gốc; không chứa API key, model hay corpus luật.
3. Thêm **một** artifact hiện đang dùng cho ONLINE: `vn_labor_online.zip` hoặc Dataset đã giải nén có `artifacts/`. Không thêm đồng thời nhiều bản artifact vì chế độ auto phải chọn đúng một bản. Không đưa gói báo cáo OFFLINE thay artifact vận hành.
4. Settings: **Internet ON, GPU T4 x2**. Bật Secrets **GEMINI_API_KEY**, tùy chọn **HF_TOKEN**. Không dán key vào notebook. Tên Dataset có thể khác; đặt đường dẫn ARTIFACT cụ thể nếu auto báo nhiều bản.
5. Lần kiểm tra đầu: `PROFILE='smoke'`, `ARM='graph_on'`. Smoke chạy 5 câu cố định để kiểm luồng; không dùng kết luận nghiên cứu. Chạy Run All và tải ZIP.
6. Đo chính thức: phiên sạch, `PROFILE='standard'`, `GRAPH_SCOPE='focused'`, `ARM='graph_on'`, giữ `SOURCE='attached_zip'`. Run All. Tải **`graph_on_graph_results.zip`**.
7. Chạy phiên thứ hai trên cùng loại GPU: chỉ đổi **`ARM='graph_off'`**. Giữ nguyên code ZIP, artifact, model, profile, scope, token budget và các cấu hình khác. Run All. Tải **`graph_off_graph_results.zip`**.

Đường dẫn tải thực tế chứa RUN_NAME/PROFILE/ARM. Notebook luôn xuất link ZIP sau generation/judge, kể cả khi có lỗi. Cất hai ZIP vào `results/` trong thư mục này hoặc nơi bạn giữ kết quả báo cáo.

Muốn lấy code qua GitHub: sau khi **commit/push thư mục mới**, đổi `SOURCE='github'`. Ghim `CODE_REF` bằng **cùng một commit SHA** cho cả hai nhánh. Chế độ GitHub không cần Graph_Study_Code.zip; vẫn cần artifact và Secrets. Hiện nhiệm vụ này chưa commit/push.

## Đang đo những câu nào?

`question_groups.json` lưu đủ 120 câu, thời điểm áp dụng và phân nhóm theo **nội dung câu hỏi + định vị căn cứ trong Gold**, không theo điểm hay trace Graph.

| Nhóm theo giả thuyết | Toàn bộ 120 | Tập focused |
|---|---:|---:|
| Quan hệ/dẫn chiếu/nhiều điều hoặc nhiều văn bản | 7 | 7 |
| Điều kiện/ngoại lệ | 16 | 16 |
| Đối chứng một điều, chưa thấy dấu hiệu cần nối quan hệ | 80 | 12 |
| Thiếu dữ kiện/ngoài phạm vi và hành vi kiểm soát | 12 | 12 |
| Câu trả lời được khác | 5 | 0 |
| **Tổng** | **120** | **47** |

12 đối chứng một điều được lấy mẫu seed42 trước lần chạy mới. Không chọn câu vì Graph thắng. Focused = **47 câu × 2 nhánh = 94 lần sinh câu trả lời**; số API request thường lớn hơn 94 vì mỗi câu có nhiều bước và judge riêng. Muốn đo hết: đổi `GRAPH_SCOPE='all120'` ở **cả hai phiên** → 240 lần sinh. Một số nhóm có ít câu, khoảng tin cậy có thể rộng; không tự suy rộng ra toàn bộ luật lao động.

Các nhóm là **giả thuyết có thể hưởng lợi**, không phải nhãn “chắc chắn cần Graph”. Bộ này đã được dùng phát triển, nhãn **DRAFT**, không phải tập kiểm định độc lập. Điều kiện/ngoại lệ đôi khi nằm đủ trong một khoản và không cần Graph. Giữ nguyên ngày trong từng câu, không đổi sang ngày chạy.

## Hai nhánh khác gì?

Adapter riêng trong `run.py` nạp `OnlinePipeline` thật. Chỉ `cfg.graph.enabled` đổi true/false; không tắt exact/profile, case/community, issue anchors hay các agent chỉ để tạo lợi thế cho Graph. Cache truy xuất theo request được tắt ở cả hai nhánh để không trộn hiệu ứng cache với Graph.

Vì thế đây là phép đo **đóng góp bổ sung của mở rộng Graph theo chỗ thiếu**, không phải xóa mọi dữ liệu/đường phân cấp được sinh từ Graph. Graph OFF vẫn có các kênh chung như cả hai nhánh. Câu có đủ căn cứ có thể bỏ qua mở rộng ở nhánh ON — đây là hành vi đúng thiết kế.

Cấu hình `full/without_graph` của bộ ablation cũ còn tắt case/community và issue anchors. Không trộn hai ZIP đó vào phép đối chứng chỉ một cờ này. Bộ cũ không bị sửa.

## Model, lỗi và tiếp tục

- Researcher/hậu kiểm trong pipeline dùng backend Gemini **3.1 Flash-Lite** theo cấu hình notebook; Auditor/sinh dự thảo dùng Ollama **qwen3:8b**. Judge ngoài pipeline dùng Gemini **3.5 Flash-Lite**. Cả hai nhánh giữ giống nhau; xem effective_config/initialization để xác nhận model thực tế.
- `ACTION='generate_only'` chỉ sinh; `judge_only` chấm lại từ checkpoint, không sinh lại. `run_and_judge` chạy cả hai giai đoạn.
- Khi quota hết: tải checkpoint, chờ dịch vụ khôi phục, thêm ZIP checkpoint làm Input và đặt CHECKPOINT_ARCHIVE đúng đường dẫn. Giữ code/data/settings cũ; bật RETRY_ERRORS có chủ đích. Không đổi model giữa một phép đối chứng và không tự xoay key để vượt quota.
- Cơ chế retry dùng bộ đo hiện có: danh sách câu lỗi riêng, số vòng hữu hạn, không tính lỗi thành câu trả lời đúng. Trường hợp không an toàn vẫn dừng và giữ checkpoint.

## Ghép và xem kết quả trên máy

Tại PowerShell trong `D:\data_thô\legal-agentic-rag`:

```powershell
.\.venv\Scripts\python.exe -B -X utf8 "evaluation/graph_qa/study/run.py" compare `
  --on "evaluation/graph_qa/study/results/graph_on_graph_results.zip" `
  --off "evaluation/graph_qa/study/results/graph_off_graph_results.zip" `
  --out "evaluation/graph_qa/study/results/so_sanh_lan_1"
```

Mỗi lần ghép dùng folder output mới. Không gọi model/API trong bước ghép. Công cụ từ chối ghép nếu code, Gold, dữ liệu, model, điều kiện phần cứng/phần mềm không khớp hoặc effective_config khác ngoài graph.enabled (bỏ qua đường dẫn output/cache).

Đầu ra:

- `comparison.md`, `group_comparison.csv/json`: điểm OFF/ON theo nhóm, chênh lệch ON−OFF, CI95 bootstrap theo **câu hỏi**, số câu chấm được và lỗi/thiếu.
- `question_by_question.json/csv`: từng câu, đáp án hai nhánh, nguyên trích dẫn, độ đúng/đủ, recall nhóm căn cứ, metadata trích dẫn, thời gian và căn cứ đi qua Graph được dùng.
- `provenance.json`: hash hai ZIP, comparison key và giới hạn diễn giải.
- ZIP gốc giữ đầy đủ trace, thông tin máy, model pins, câu lỗi và logs phục vụ xem lại. JSON/CSV ghép không thay ZIP gốc.

AI đúng/đủ là điểm mô hình chấm, không phải xác nhận pháp lý. Metadata khớp không chứng minh câu kết luận được nguồn hỗ trợ. Chỉ số AI chỉ ghép khi cả hai lượt có AI_JUDGED; ERROR/N/A không thành 0 hoặc PASS. Nếu có nhiều repeats, lấy trung bình mỗi câu trước khi bootstrap. CI theo nhóm mang tính khám phá, chưa điều chỉnh nhiều phép thử; không tự gọi là “cải thiện có ý nghĩa thống kê”. Thời gian là pipeline local, không gồm HTTP/frontend hay judge.

## Trace của lần cũ đã phân tích

Xem `historical_usage/full120/graph_usage.csv` và `summary.json`:

- 12/120 câu có vòng mở rộng; 6 câu có căn cứ được chấp nhận sau mở rộng.
- 2 câu có căn cứ đi qua Graph được chọn vào gói bằng chứng.
- 1 câu (`TD012`) có căn cứ đó được trích dẫn và gắn vào claim.

Đây là **phân tích sau khi xem kết quả**, chỉ minh họa cơ chế. Một căn cứ được Graph đi qua và dùng không chứng minh chỉ Graph mới tìm được, cũng không chứng minh đáp án tốt hơn. Không dùng TD012 hay tập 6 câu này làm tập chính để chứng minh lợi ích. Giữ riêng kết quả cũ và mới.

Chạy lại phân tích ZIP cũ (không API):

```powershell
.\.venv\Scripts\python.exe -B -X utf8 "evaluation/graph_qa/study/run.py" audit `
  --zip "D:\data_thô\kaggle_download\bộ đo để đưa vào báo cáo\full_ablation_results.zip" `
  --out "evaluation/graph_qa/study/results/audit_moi"
```

## Kiểm thử và đóng code ZIP lại nếu sửa

```powershell
.\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s "evaluation/core/đo graph" -p test_study.py -q
.\.venv\Scripts\python.exe -B -X utf8 "evaluation/graph_qa/study/run.py" package --output "evaluation/graph_qa/study/Graph_Study_Code.zip"
```

Không cần chép thủ công các module của bộ đo cũ: công cụ đóng ZIP lấy đúng source cần thiết. Không đưa .env, token, cache hoặc model vào gói. Không thay ZIP code giữa hai nhánh. Kiểm thử local và kiểm cú pháp notebook không thay thế lần chạy model thật trên GPU Kaggle.

## Đã kiểm chứng trên máy

- Nạp artifact vận hành thực và Gold120: 120 câu, 19.144 đơn vị, nhãn DRAFT; đóng băng thành công.
- Khởi tạo cả hai adapter thật, đối chiếu cấu hình: chỉ khác graph.enabled (ngoài đường dẫn trace). BM25 top5 của câu smoke giống nhau.
- Kiểm thử hành vi, so sánh, phân nhóm và bootstrap notebook: xem test_study.py. Kiểm tra cả Input ZIP lẫn Dataset code đã giải nén.
- Chưa sinh QA bằng LLM/GPU Kaggle trong nhiệm vụ chuẩn bị này; chưa có kết quả mới để khẳng định Graph cải thiện đúng/đủ.
- Reviewer API không được gọi vì kiểm duyệt tự động từ chối quyền gửi đoạn source; các kiểm tra ghi trên là kiểm tra local thực tế.

## Sửa lỗi Kaggle làm mất ZIP Gold bên trong code Dataset

Kaggle có thể giải nén luôn `evaluation/gold/PhapDienAI_Gold_120_Labor_v0_2.zip`. Các file bên trong vẫn còn nhưng ZIP gốc không còn, nên không thể kiểm SHA gốc. Không nén lại tùy ý và không bỏ kiểm fingerprint.

Đã sửa notebook và gói code: Gold đi kèm dưới dạng `.zip.b64.txt`, được khôi phục đúng từng byte rồi kiểm SHA của ZIP gốc. Đây chỉ là thay cách vận chuyển, không sửa câu hỏi/đáp án/nhãn.

**Dùng tiếp Dataset cũ:** import notebook mới, thêm file `PhapDienAI_Gold_120_Labor_v0_2.zip.b64.txt` cùng thư mục này vào một Kaggle Input mới; giữ code Dataset và artifact hiện tại. Không sửa nội dung file text. Chạy lại cell lấy code. Nếu muốn chạy sạch, dùng gói `Graph_Study_Code.zip` mới để tạo phiên bản mới của code Dataset; gói mới đã có file text này, không cần bổ sung riêng.
