# Pháp Điển AI — LegalGraphRAG cho pháp luật lao động Việt Nam

Repository: [tvqui/phap-dien-ai-legalgraphrag](https://github.com/tvqui/phap-dien-ai-legalgraphrag)

Dự án gồm quy trình **OFFLINE** để xây dựng/kiểm tra dữ liệu, Backend **ONLINE** để truy xuất căn cứ và tạo câu trả lời, giao diện web và bộ đánh giá. Backend đọc artifact đã xây dựng; nó không tự tìm luật mới trên web theo từng câu hỏi.

## Chọn đúng quy trình

| Nhu cầu | Hướng dẫn | Đầu ra |
|---|---|---|
| Chạy API và giao diện trên máy | [Chạy ONLINE local](#chạy-online-trên-máy-local-windows) | API http://127.0.0.1:8000, giao diện http://127.0.0.1:5173 |
| Chạy Backend trên Kaggle | [Chạy Backend ONLINE trên Kaggle](#chạy-backend-online-trên-kaggle) | URL Backend tạm thời và log |
| Dựng dữ liệu từ đầu | [OFFLINE](docs/offline.md), [đóng gói artifact](docs/offline/artifact-layout.md) | vn_labor_online.zip và gói review |
| Dùng output đã dựng sẵn | `sample_data/vn_labor_online.zip` | Chạy Backend mà không phải chạy lại OFFLINE |
| Nộp/chạy thử mẫu | [Notebook OFFLINE trên Kaggle](build/submission/offline/VN_Labor_Kaggle_V8.ipynb), [ZIP input mẫu ONLINE](build/submission/online/sample_input/vn_labor_online.zip) | Hai file bàn giao có sẵn sau khi clone |
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

Corpus PDF/DOCX, cache dựng trung gian, model weights và API keys không thuộc Git. Repo có kèm một artifact ONLINE đã dựng để dùng nhanh tại `sample_data/vn_labor_online.zip`; hai file bàn giao trong `build/submission/` là ngoại lệ được chọn để đưa vào Git. Các output khác trong `build/` vẫn bị Git bỏ qua. Không commit `.env`, token hay khóa API.

**Sau khi clone:** `build/releases/vn_labor_online.zip` được tạo bằng lệnh copy từ ZIP mẫu ở trên; `build/online_pinned.yaml` được sinh bởi lệnh ghim artifact. `build/kaggle/` chỉ xuất hiện sau `run.bat kaggle` và cần corpus đầu vào. Các thư mục `data/`, `review/attachments/` và `artifacts/` không được đóng gói trong Git: người dùng phải tự cung cấp nguồn được cấu hình rồi chạy pipeline để tạo artifacts. `.env` cũng không được clone; dùng `.env.example` làm mẫu nếu cần cấu hình secret.

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

Đường dẫn mẫu phải là build/releases/vn_labor_online.zip. Repo có sẵn artifact OFFLINE đã dựng tại `sample_data/vn_labor_online.zip`; để chạy thử hoặc demo mà không mất thời gian chạy lại OFFLINE, dùng lệnh:

~~~powershell
Copy-Item -LiteralPath sample_data/vn_labor_online.zip -Destination build/releases/vn_labor_online.zip -Force
~~~

Nếu nhóm đã có ZIP mới hơn, có thể thay file mẫu bằng bản đó. Không dùng vn_labor_offline_review.zip, Gold ZIP, checkpoint hoặc thư mục nghiên cứu làm artifact chạy.

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

## Dựng dữ liệu OFFLINE trên máy local (Windows)

Đây là cách dựng mới từ corpus PDF/HTML/DOCX đang có trên máy. Dữ liệu nguồn không nằm trên Git; bạn phải cấp đủ bộ corpus theo danh mục của dự án.

### 1. Chuẩn bị nguồn

Đặt nguồn theo cấu hình mặc định trong thư mục data/:

~~~text
data/
  legal_corpus/       Văn bản pháp luật lao động và văn bản liên quan
  judicial_corpus/    Bản án/án lệ nếu có trong bộ nguồn được duyệt
  supplementary/      Tài liệu bổ sung được cấu hình
review/attachments/   Tệp đính kèm được source_attachments.yaml tham chiếu
~~~

Không đổi tên hoặc bỏ tệp được liệt kê trong src/offline/config/source_catalog.yaml, src/offline/config/source_attachments.yaml và src/offline/review/corrections/. Kiểm tra file nguồn đúng phiên bản/hash khi cấu hình có khai báo. Nếu bộ dữ liệu của bạn đặt ở nơi khác, cập nhật data_dir trong src/offline/config/pipeline.yaml trước khi chạy.

### 2. Cài môi trường và chạy pipeline

Mở PowerShell tại thư mục gốc repo:

~~~powershell
run.bat setup-full
run.bat offline
~~~

run.bat offline chạy pipeline theo src/offline/config/pipeline.yaml: quét nguồn, trích xuất văn bản/OCR có chọn lọc, chuẩn hóa, dựng registry và Điều–Khoản–Điểm, provenance/phiên bản, tri thức và graph, rồi xây BM25 và Dense/FAISS. Lần đầu cần Internet để cài thư viện và tải model BGE-M3; thời gian phụ thuộc dung lượng corpus, phần OCR và phần cứng.

Nếu cấu hình cần Neo4j local, mở Docker Desktop trước rồi chạy trong PowerShell:

~~~powershell
run.bat neo4j
run.bat load-neo4j
~~~

Không chạy lệnh load Neo4j nếu bạn không dùng Neo4j local hoặc đã cấu hình một đích khác phù hợp.

### 3. Kiểm tra và đóng gói kết quả

~~~powershell
run.bat validate
~~~

Khi audit đạt, hệ thống tạo thư mục release có timestamp cạnh artifact làm việc, thường theo dạng releases/YYYYMMDDTHHMMSSffffffZ/. Trong đó:

- vn_labor_online.zip: gói nhỏ đưa cho Backend ONLINE.
- vn_labor_offline_review.zip: báo cáo và dữ liệu trung gian để xem/đối chiếu; không dùng làm artifact Backend.
- release.json: build ID và SHA-256 của hai ZIP.

Kiểm tra reports/final_outputs_validation.json, reports/dense_validation.json, reports/neo4j_validation.json, reports/validation_issues.jsonl và release.json. Nếu validation chưa PASS, xem từng check/detail trong báo cáo, sửa đúng nguồn hoặc cấu hình rồi chạy lại bước phụ thuộc; không đổi nhãn UNVERIFIED thành VERIFIED bằng tay. Trạng thái kỹ thuật PASS không đồng nghĩa nội dung đã được người có chuyên môn duyệt pháp lý.

Muốn chạy ONLINE local sau đó, chép đúng vn_labor_online.zip vào build/releases/ và làm theo các bước [chạy ONLINE local](#chạy-online-trên-máy-local-windows).
## Chạy Backend ONLINE trên Kaggle

Notebook Backend tự lấy mã mới nhất từ main, dò artifact theo cấu trúc, kiểm fingerprint và dừng nếu không tương thích. Chỉ cần thêm Dataset artifact; **không cần tải code thành Kaggle Dataset**. Notebook phải chạy trong phiên tương tác để API/tunnel còn hoạt động.

### 1. Import đúng notebook

Mở [ONLINE_Backend.ipynb trên GitHub](https://github.com/tvqui/phap-dien-ai-legalgraphrag/blob/main/src/online/backend/kaggle/ONLINE_Backend.ipynb), tải file .ipynb về máy. Trong Kaggle, tạo Notebook mới, chọn **File → Import Notebook** rồi tải file vừa lưu. Đây là notebook Backend, không phải notebook OFFLINE hay notebook đo.

### 2. Thêm tài nguyên Kaggle

1. Bật **Internet** trong Settings.
2. Chọn GPU **T4 x2** nếu tùy chọn có sẵn.
3. Chọn **Add Input → Datasets**, thêm đúng **một** Dataset chứa artifact OFFLINE đã kiểm tra.
4. Trong Secrets, tạo và cấp quyền cho các tên chính xác: GEMINI_API_KEY, VN_LABOR_API_KEY (chuỗi ngẫu nhiên ít nhất 32 ký tự), NGROK_AUTHTOKEN; HF_TOKEN là tùy chọn.

Để dùng ngay dữ liệu đã dựng sẵn trong repo, tải `sample_data/vn_labor_online.zip` từ GitHub, tạo Kaggle Dataset **Private** tên `phapdienai-labor-artifact-final-v2`, tải đúng file `vn_labor_online.zip` lên Dataset rồi gắn Dataset đó qua **Add Input**. Không cần giải nén và không cần chạy lại OFFLINE. Notebook Backend tự dò ZIP hợp lệ trong `/kaggle/input`; nếu chỉ có một artifact hợp lệ thì không cần nhập đường dẫn. Nếu tải artifact đã giải nén, cấu trúc nhận diện là thư mục `artifacts/` gồm `00_manifest/`, `01_extracted/`, `02_registry/`, `03_structure/`, `04_knowledge/`, `05_graph/`, `06_indexes/` và `reports/`.

Không thêm gói review, Gold ZIP, checkpoint hoặc code bundle thay artifact ONLINE.

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

## Dựng hoặc tiếp tục dữ liệu OFFLINE trên Kaggle

**Lưu ý về notebook hiện hành:** VN_Labor_Kaggle_V8.ipynb được thiết kế theo kiểu checkpoint-first. Mặc định nó tiếp tục AI enrichment từ một checkpoint OFFLINE có sẵn; nó không khởi đầu từ một Kaggle Input trống. Muốn dựng toàn bộ từ corpus thô lần đầu, chạy run.bat offline trên local trước, hoặc cần một notebook cold-start riêng. Đặt RESUME_AI_ONLY=False không bỏ yêu cầu checkpoint.

#### A. Tạo Dataset chứa mã nguồn và corpus

1. Trước hết phải có corpus trong `data/` và một checkpoint OFFLINE hợp lệ. Nếu bắt đầu từ repo clone mới, đặt corpus cùng các tệp review được cấu hình vào đúng chỗ rồi chạy pipeline local theo mục trên:
   ~~~powershell
   run.bat setup-full
   run.bat offline
   run.bat validate
   ~~~
   Chỉ tiếp tục khi validation đạt và `artifacts/` có đủ dữ liệu. Bước này cũng tạo bản DOCX đã chuyển đổi từ các nguồn `.doc`; bộ đóng gói Kaggle cần các bản này. Nếu đã có checkpoint đã kiểm định, có thể dùng lại thay vì dựng lại.
2. Sau đó tạo gói Kaggle:
   ~~~powershell
   run.bat kaggle
   ~~~
   Lệnh tương đương là `./.venv/Scripts/python.exe -X utf8 src/offline/scripts/package_kaggle.py`.
3. Kiểm tra build/kaggle/package_report.json. Cần thấy zip_crc_check là PASS, notebook_code_syntax là PASS và corpus_files lớn hơn 0. `uploaded: false` và `remote_execution_tested: false` là trạng thái bình thường: script chỉ đóng gói, chưa tải lên hoặc chạy trên Kaggle.
4. File ZIP được tạo ở build/kaggle/vn_labor_kaggle_v8.zip. Giải nén ZIP này trên máy; bên trong phải có thư mục vn_labor_bundle/ với bundle_manifest.json, src/offline/kaggle/bootstrap.py, src/ và data/.
5. Tạo một Kaggle Dataset **Private** tên mẫu vn-labor-code-corpus-v8. Tải nội dung đã giải nén sao cho Kaggle nhìn thấy cùng trong một cây thư mục:
   ~~~text
   vn_labor_bundle/bundle_manifest.json
   vn_labor_bundle/src/offline/kaggle/bootstrap.py
   vn_labor_bundle/data/
   ~~~
   Không chỉ tải file ZIP lồng bên trong: notebook cần đọc trực tiếp bundle_manifest.json và src/offline/kaggle/bootstrap.py trong Input. Không sửa file bên trong sau khi đóng gói vì notebook xác minh SHA-256 từng file.

#### B. Tạo Dataset chứa checkpoint

Notebook cần đúng một checkpoint bên cạnh Dataset mã nguồn/corpus. Tạo một Kaggle Dataset **Private**, ví dụ vn-labor-checkpoint-current, từ một trong các nguồn sau:

- Thư mục artifact đầy đủ có artifacts/00_manifest/files.jsonl; hoặc
- ZIP checkpoint do lần chạy OFFLINE trước xuất, thường là vn_labor_results.zip hoặc vn_labor_results_recovery.zip.

Nếu tiếp tục sau một lần chạy bị ngắt, ưu tiên vn_labor_results_recovery.zip mới nhất vì nó có thể giữ AI cache và tiến độ mới nhất. vn_labor_results_technical_checkpoint.zip được tạo trước AI; dùng nó khi cần trở về mốc kỹ thuật trước bước AI. Chỉ gắn một checkpoint. Nếu gắn nhiều bản, RESTORE_ARCHIVE="AUTO" sẽ báo tìm thấy nhiều nguồn; không chọn ngẫu nhiên hoặc trộn các build khác nhau.

#### C. Import notebook và cài Kaggle Inputs

1. Trong repo, mở `build/submission/offline/VN_Labor_Kaggle_V8.ipynb`. Bước `package_kaggle.py` ở trên cũng sinh notebook tương đương tại `build/kaggle/VN_Labor_Kaggle_V8.ipynb` cùng ZIP.
2. Tải file notebook về. Trong Kaggle chọn Code → New Notebook → File → Import Notebook và tải VN_Labor_Kaggle_V8.ipynb lên.
3. Trong Settings, bật Internet và chọn GPU T4 x2. AI mặc định cần hai GPU: Dense chạy trên GPU 0, Ollama qwen3:8b chạy trên GPU 1. Nếu không chạy AI, hãy đổi cấu hình có chủ đích; đừng bỏ qua preflight GPU.
4. Trong Input → Add Input → Datasets, gắn đúng hai Dataset: vn-labor-code-corpus-v8 và vn-labor-checkpoint-current. Nếu dùng tên khác, không cần sửa code; notebook nhận diện theo manifest và cấu trúc bên trong.
5. Trong Add-ons → Secrets, tạo và cấp quyền đúng bốn tên: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE. URI Aura phải có dạng neo4j+s://...; không đặt giá trị secret trong cell hoặc Dataset.

#### D. Chọn chế độ và chạy

Cấu hình mặc định trong cell đầu:

~~~python
RESTORE_ARCHIVE = "AUTO"
RESUME_AI_ONLY = True
REFRESH_EXTRACTION_QUALITY = False
RUN_AI_ENRICHMENT = True
OFFLINE_AI_MODEL = "qwen3:8b"
OFFLINE_AI_MAX_PROVISIONS = 250
LOAD_AURA = True
~~~

Giữ các giá trị này khi mục tiêu là tiếp tục AI từ checkpoint. Notebook kiểm SHA/provenance/index trước khi gọi Ollama, giữ cache AI, xuất technical checkpoint trước AI, chạy phần enrichment còn thiếu, nạp Aura, audit rồi xuất kết quả. Vì resume AI-only, nó không OCR lại toàn corpus và không dựng lại Dense/BM25.

Nếu cần làm mới extraction trên checkpoint hiện có, chỉ bật REFRESH_EXTRACTION_QUALITY=True đồng thời đặt RESUME_AI_ONLY=False; việc này chạy lại extraction/OCR có chọn lọc và mất thời gian hơn. Không chọn tổ hợp RESUME_AI_ONLY=True cùng REFRESH_EXTRACTION_QUALITY=True. Đây vẫn là làm mới từ checkpoint, không phải chạy trắng từ corpus.

Chọn **Save Version → Save & Run All**, chờ các cell hoàn tất. Theo dõi HEARTBEAT, stage, số câu AI đã xử lý, log và trạng thái GPU. Nếu Kaggle/Ollama lỗi, giữ output và dùng recovery ZIP mới nhất cho lượt tiếp tục; không xóa checkpoint cũ trước khi xác nhận ZIP mới tải được.

#### E. Lấy và kiểm tra đầu ra

Notebook hiện các liên kết tải trong Output. Tải và lưu riêng:

- vn_labor_online.zip: chỉ gói này đưa vào Kaggle Backend ONLINE. Tạo Dataset, ví dụ phapdienai-labor-artifact-final-v2, rồi dùng nó theo mục [chạy Backend ONLINE trên Kaggle](#chạy-backend-online-trên-kaggle).
- vn_labor_offline_review.zip và release.json: hồ sơ kiểm tra, trung gian, build ID và SHA-256.
- vn_labor_results.zip: checkpoint hoàn tất để lưu hoặc tiếp tục công việc sau.
- vn_labor_results_technical_checkpoint.zip: mốc kỹ thuật xuất trước AI.
- vn_labor_results_recovery.zip: checkpoint phục hồi sau lỗi, nếu notebook tạo được.

Trong báo cáo, kiểm tra offline_final_run.json, tong_hop_sau_chay.md, reports/final_outputs_validation.json, reports/dense_validation.json, reports/neo4j_validation.json, reports/validation_issues.jsonl và release.json. Chỉ dùng vn_labor_online.zip khi audit/validation báo PASS; nhãn dữ liệu pháp lý và human review vẫn phải được công bố đúng trạng thái.
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
