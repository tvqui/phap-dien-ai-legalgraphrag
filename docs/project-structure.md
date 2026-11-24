# Cấu trúc dự án Pháp Điển AI

## Cây chức năng

```text
legal-agentic-rag/
├── src/
│   ├── run.ps1
│   ├── offline/
│   │   ├── src/
│   │   │   └── vn_labor_offline/
│   │   ├── config/ scripts/ kaggle/ review/ tests/
│   │   └── README.md
│   └── online/
│       ├── backend/
│       │   │   ├── src/
│       │   │   │   └── vn_labor_online/
│       │   ├── config/ scripts/ kaggle/ tests/
│       │   └── README.md
│       └── frontend/
├── evaluation/
│   ├── core/ suite/ graph_qa/ retrieval_comparison/ online_upgrade/
│   ├── notebooks/ scripts/ tests/ gold/ results_summary/
│   └── README.md
├── docs/ data/ dev/tools/coding_team/
├── artifacts/ build/ .cache/ .venv/  # local/ignored
└── README.md, AGENTS.md, pyproject.toml, run.bat, docker-compose.yml
```

Runtime OFFLINE và ONLINE giữ nguyên tên package Python; chỉ đổi vị trí source
để phân tách rõ cấu hình, scripts, Kaggle notebooks và tests. Frontend chỉ gọi
API, không tự thực hiện suy luận pháp lý. Evaluation giữ riêng các protocol,
runner, Gold và notebooks; các bộ đo không được trộn giao thức hay nhãn.

## Điểm vào theo công việc

| Việc cần làm | Thư mục/file bắt đầu |
|---|---|
| Build dữ liệu OFFLINE | `src/offline/src/vn_labor_offline/`, `src/offline/config/pipeline.yaml`, `run.bat offline` |
| Nạp artifact và chạy API | `src/online/backend/src/vn_labor_online/`, `src/online/backend/config/`, `run.bat online` |
| Chạy giao diện | `src/online/frontend/README.md`, `run.bat frontend` |
| Chạy Kaggle backend | `src/online/backend/kaggle/ONLINE_Backend.ipynb`, `src/online/backend/kaggle/online_notebook.py` |
| Đo retrieval/QA/ablation | `evaluation/README.md`, `evaluation/notebooks/`, `evaluation/core/` |
| Đo Graph QA | `evaluation/graph_qa/README.md`, `evaluation/graph_qa/Kaggle_Graph_QA.ipynb` |
| Kiểm thử | `src/offline/tests/`, `src/online/backend/tests/`, `evaluation/tests/`, `src/online/frontend/tests/` |
| Đọc giới hạn và bàn giao | `docs/project-completion.md`, `docs/submission-check.md` |

## Dữ liệu vận hành và nghiên cứu

- Gói runtime ONLINE do OFFLINE tạo chứa retrieval units, BM25, Dense/FAISS,
  graph nodes/edges, metadata và manifest/hash. Dùng đúng gói runtime cùng
  kiểm tra fingerprint.
- Gói review OFFLINE chứa báo cáo, dữ liệu trung gian và biểu mẫu cần người
  duyệt; không dùng thay artifact runtime.
- Gold và kết quả benchmark có trạng thái riêng. Không coi điểm AI judge là
  phê duyệt pháp lý.
- `.env`, `.venv/`, `.cache/`, frontend `node_modules/`, output `artifacts/`,
  `build/`, corpus local và ZIP kết quả Kaggle không phải mã nguồn nộp Git;
  xem `.gitignore`.

Chỉ chuyển file khi mọi import, đường dẫn, notebook và hướng dẫn phụ thuộc được
cập nhật cùng lúc. Không xóa dữ liệu/artifact local để làm gọn repository; nếu
không chắc file có thể dựng lại, giữ lại hoặc lưu trữ thay vì xóa.
