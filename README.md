# Pháp Điển AI — LegalGraphRAG cho pháp luật lao động Việt Nam

Repository: [tvqui/phap-dien-ai-legalgraphrag](https://github.com/tvqui/phap-dien-ai-legalgraphrag)

Dự án gồm quy trình **OFFLINE** để xây dựng/kiểm tra dữ liệu, Backend **ONLINE** để truy xuất căn cứ và tạo câu trả lời, giao diện web và bộ đánh giá. Backend đọc artifact đã xây dựng; nó không tự tìm luật mới trên web theo từng câu hỏi.

## Chọn đúng quy trình

| Nhu cầu | Hướng dẫn | Đầu ra |
|---|---|---|
| Chạy API và giao diện trên máy | [Chạy ONLINE local](#chạy-online-trên-máy-local-windows) | API http://127.0.0.1:8000, giao diện http://127.0.0.1:5173 |
| Chạy Backend trên Kaggle | [Chạy Backend ONLINE trên Kaggle](#chạy-backend-online-trên-kaggle) | URL Backend tạm thời và log |
| Dựng dữ liệu từ đầu | [OFFLINE](docs/offline.md), [đóng gói artifact](docs/offline/artifact-layout.md) | vn_labor_online.zip và gói review |
| Đo chất lượng | [evaluation/README.md](evaluation/README.md) | Kết quả theo từng phép đo |

## Cấu trúc repository

~~~text
src/
  offline/src/vn_labor_offline/       Xây dựng, chuẩn hóa và kiểm tra dữ liệu
  offline/config, scripts, kaggle, tests
  online/backend/src/vn_labor_online/ API, truy xuất, kiểm chứng, tạo câu trả lời
  online/backend/config, scripts, kaggle, tests
  online/frontend/                    Giao diện React/Vite
evaluation/                           Gold, giao thức đo, mã đo, notebook Kaggle
data/                                 Hướng dẫn về dữ liệu; dữ liệu lớn không lên Git
docs/                                 Kiến trúc và hướng dẫn
~~~

Artifact lớn, PDF nguồn, cache, model weights và API keys không thuộc Git. Không commit .env, token hay khóa API.

## Chạy ONLINE trên máy local (Windows)

### Điều kiện

- Windows 10/11, Git, Python **3.12 hoặc 3.13**, Node.js LTS được Vite hỗ trợ.
- Một artifact OFFLINE đã qua kiểm tra, thường là vn_labor_online.zip.
- Internet lần đầu để cài thư viện/tải model. GPU không bắt buộc nhưng giúp Dense retrieval nhanh hơn.
- Ollama, Docker/Neo4j chỉ cần nếu cấu hình bạn chọn yêu cầu; không bắt buộc cho các bước mặc định dưới đây.

### 1. Clone repo và cài môi trường

Mở PowerShell:

~~~powershell
git clone https://github.com/tvqui/phap-dien-ai-legalgraphrag.git
Set-Location -LiteralPath ./phap-dien-ai-legalgraphrag
run.bat setup-full
~~~

Nếu repo đã có trên máy, mở PowerShell tại thư mục gốc repo và chạy run.bat setup-full.

### 2. Đặt artifact

Tạo thư mục rồi chép **file vn_labor_online.zip** vào:

~~~powershell
New-Item -ItemType Directory -Force build/releases | Out-Null
~~~

Đường dẫn mẫu phải là build/releases/vn_labor_online.zip. Không dùng vn_labor_offline_review.zip, Gold ZIP, checkpoint hoặc thư mục nghiên cứu làm artifact chạy.

### 3. Ghim đúng artifact vào cấu hình

Chạy từ thư mục gốc:

~~~powershell
./.venv/Scripts/python.exe -B -X utf8 src/online/backend/scripts/pin_online_artifact.py --artifact build/releases/vn_labor_online.zip --base-config src/online/backend/config/online.yaml --output build/online_pinned.yaml
~~~

Lệnh kiểm tra tương thích kỹ thuật và ghi fingerprint vào build/online_pinned.yaml; nó không phê duyệt nội dung pháp luật. Mỗi lần đổi artifact, chạy lại lệnh. Không giữ fingerprint cũ và không bỏ kiểm tra.

Nếu file gốc .env có VN_LABOR_ARTIFACT_SOURCE, bảo đảm nó cũng trỏ tới đúng ZIP:

~~~dotenv
VN_LABOR_ARTIFACT_SOURCE=build/releases/vn_labor_online.zip
~~~

### 4. Kiểm tra và chạy API

~~~powershell
run.bat online-check -Config build/online_pinned.yaml
run.bat online -Config build/online_pinned.yaml
~~~

Giữ cửa sổ PowerShell mở. API ở http://127.0.0.1:8000; tài liệu API ở http://127.0.0.1:8000/docs. Trạng thái có ở /health và /ready.

Cấu hình mẫu dùng deterministic cho một số vai trò. Chỉ khi bật Gemini mới cần GEMINI_API_KEY; nếu bật Ollama thì cần chạy Ollama và tải đúng model. Gemini qua Internet không đồng nghĩa hệ thống tra luật mới trên web.

### 5. Chạy giao diện

Mở **PowerShell thứ hai** tại thư mục gốc repo:

~~~powershell
run.bat frontend
~~~

Mở http://127.0.0.1:5173. Dừng từng tiến trình bằng Ctrl+C trong cửa sổ tương ứng.

Kiểm tra local bằng run.bat help, run.bat test hoặc run.bat validate. Test dùng fixture/mock ở các bước cần dịch vụ ngoài; PASS không thay việc duyệt pháp lý.

## Chạy Backend ONLINE trên Kaggle

Notebook Backend tự lấy mã mới nhất từ main, dò artifact theo cấu trúc, kiểm fingerprint và dừng nếu không tương thích. Chỉ cần thêm Dataset artifact; **không cần tải code thành Kaggle Dataset**. Notebook phải chạy trong phiên tương tác để API/tunnel còn hoạt động.

### 1. Import đúng notebook

Mở [ONLINE_Backend.ipynb trên GitHub](https://github.com/tvqui/phap-dien-ai-legalgraphrag/blob/main/src/online/backend/kaggle/ONLINE_Backend.ipynb), tải file .ipynb về máy. Trong Kaggle, tạo Notebook mới, chọn **File → Import Notebook** rồi tải file vừa lưu. Đây là notebook Backend, không phải notebook OFFLINE hay notebook đo.

### 2. Thêm tài nguyên Kaggle

1. Bật **Internet** trong Settings.
2. Chọn GPU **T4 x2** nếu tùy chọn có sẵn.
3. Chọn **Add Input → Datasets**, thêm đúng **một** Dataset chứa artifact OFFLINE cuối đã kiểm tra.
4. Trong Secrets, tạo và cấp quyền cho các tên chính xác: GEMINI_API_KEY, VN_LABOR_API_KEY (chuỗi ngẫu nhiên ít nhất 32 ký tự), NGROK_AUTHTOKEN; HF_TOKEN là tùy chọn.

Ví dụ tên Dataset để tìm trong Add Input, theo Dataset đã dùng:

~~~text
phapdienai-labor-artifact-final-v2
~~~

Bên trong Dataset, cấu trúc mẫu là artifacts/ gồm 00_manifest/, 01_extracted/, 02_registry/, 03_structure/, 04_knowledge/, 05_graph/, 06_indexes/ và reports/. Đường dẫn mount ví dụ:

~~~text
/kaggle/input/phapdienai-labor-artifact-final-v2/artifacts
~~~

Kaggle có thể chuẩn hóa tên mount; notebook tự dò trong /kaggle/input, không cần nhập đường dẫn nếu chỉ có một artifact hợp lệ. Không thêm gói review, Gold ZIP, checkpoint hay code bundle thay artifact ONLINE.

### 3. Chạy và xác nhận

1. Chọn **Run All** trong phiên tương tác.
2. Đợi kiểm tra GPU, Input, Secrets, lấy code GitHub, ghim artifact và khởi động Backend.
3. Log cần có Preflight GPU/Internet/Input/Secrets: PASS, dòng Input đã chọn: trỏ vào Dataset vừa thêm và URL Backend.
4. Để cell cuối tiếp tục chạy. Dừng cell hoặc đóng phiên sẽ làm server/tunnel ngừng hoạt động.

Để dùng giao diện local với Backend Kaggle, ghi URL và token vào src/online/frontend/.env trên máy local:

~~~dotenv
VITE_BACKEND_TARGET=https://URL-BACKEND-VUA-NHAN
BACKEND_PROXY_TOKEN=GIA_TRI_VN_LABOR_API_KEY
~~~

Sau đó chạy run.bat frontend, mở http://127.0.0.1:5173. Không commit .env. URL tunnel có thể đổi sau khi Kaggle restart. Khi báo lỗi, lưu Commit đang dùng:, Input đã chọn: và mã lỗi; không gửi API key/token.

### Dựng dữ liệu OFFLINE trên Kaggle

Đây là quy trình khác với chạy Backend ONLINE:

1. Tạo bundle private từ repo local:
   ~~~powershell
   ./.venv/Scripts/python.exe src/offline/scripts/package_kaggle.py
   ~~~
2. Dùng notebook và bundle trong build/kaggle/; import notebook, thêm Dataset code/corpus cần thiết và làm theo [hướng dẫn OFFLINE Kaggle](docs/kaggle/guide.md).
3. Khi OFFLINE qua validation, tải vn_labor_online.zip từ Output, đưa vào một Dataset (ví dụ tên ở trên), rồi thêm Dataset làm Input cho Backend.
4. Giữ vn_labor_offline_review.zip để xem báo cáo/trung gian; không dùng nó làm artifact Backend.

## Notebook đánh giá

Notebook đo chính nằm dưới evaluation/: evaluation/suite/, evaluation/notebooks/, evaluation/graph_qa/. Chúng clone repo, cài package từ checkout và lưu kết quả theo lần chạy. Notebook recovery cần checkpoint và commit gốc; không đổi commit khi tiếp tục lần đo cũ.

Trước khi so sánh, kiểm tra cùng artifact, Gold, commit, model và cấu hình. Xem [README bộ đánh giá](evaluation/README.md). Không gộp Retrieval, QA, AI-judge và human review thành một điểm chính xác chung.

## Giới hạn

- Hệ thống chỉ trả lời trong phạm vi dữ liệu và phiên bản luật có trong artifact; công bố ngày chốt và trạng thái phê duyệt.
- Fingerprint xác nhận artifact khớp cấu hình, không chứng minh căn cứ đúng luật.
- Không đưa secret, dữ liệu nhạy cảm hoặc artifact riêng tư lên GitHub công khai.

## Tài liệu

- [Kiến trúc](docs/architecture.md)
- [ONLINE và nạp artifact](docs/online.md)
- [Pipeline OFFLINE](docs/offline.md)
- [Cấu trúc đầu ra OFFLINE](docs/offline/artifact-layout.md)
- [Notebook Backend Kaggle](src/online/backend/kaggle/ONLINE_Backend.ipynb)
- [Bộ đánh giá](evaluation/README.md)
- [Kiểm tra trước khi nộp](docs/project-completion.md)
