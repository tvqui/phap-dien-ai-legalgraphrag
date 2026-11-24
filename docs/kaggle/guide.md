# Chạy pipeline OFFLINE trên Kaggle

> Đây là trang tóm tắt. Hướng dẫn đầy đủ và mới nhất nằm tại [README — Dựng hoặc tiếp tục dữ liệu OFFLINE trên Kaggle](../../README.md#dựng-hoặc-tiếp-tục-dữ-liệu-offline-trên-kaggle).

## Trạng thái notebook hiện hành

`build/kaggle/VN_Labor_Kaggle_V8.ipynb` là notebook **checkpoint-first**. Notebook yêu cầu hai Kaggle Input Private:

1. Dataset mã nguồn và corpus, được đóng gói thành `vn_labor_bundle/`.
2. Đúng một checkpoint OFFLINE có `artifacts/00_manifest/files.jsonl` hoặc ZIP kết quả có thư mục `artifacts/`.

Notebook không dựng lần đầu từ Kaggle Input trống. Nếu chỉ muốn chạy Backend ONLINE/demo, dùng artifact mẫu `sample_data/vn_labor_online.zip` theo README; không cần chạy lại OFFLINE. Chỉ khi cần dựng hoặc cập nhật dữ liệu thì mới cần corpus và checkpoint OFFLINE. Corpus nguồn không nằm trong Git; người chạy phải được cấp riêng.

## Tạo gói và chạy

Tại PowerShell ở thư mục repo, sau khi đã đặt corpus và có checkpoint:

```powershell
run.bat setup-full
run.bat offline
run.bat validate
run.bat kaggle
```

Nếu đã có build OFFLINE đã kiểm định, không cần chạy lại `run.bat offline`; tạo/update gói bằng `run.bat kaggle`. Kiểm tra `build/kaggle/package_report.json`, rồi giải nén `build/kaggle/vn_labor_kaggle_v8.zip` và tải cây `vn_labor_bundle/` lên Kaggle Dataset **Private**. Import `build/kaggle/VN_Labor_Kaggle_V8.ipynb`, thêm Dataset mã/corpus và một Dataset checkpoint, bật Internet và GPU T4 x2. Theo dõi checkpoint, cấu hình model, Aura Secrets và đầu ra theo hướng dẫn README ở trên.

`package_report.json` chỉ chứng minh việc đóng gói và cú pháp notebook ở local; nó không chứng minh Kaggle đã chạy thành công. Sau khi chạy, chỉ dùng `vn_labor_online.zip` làm Input cho Backend ONLINE nếu các kiểm định đi kèm đạt yêu cầu. Giữ `vn_labor_offline_review.zip`, `release.json` và checkpoint để xem lại hoặc tiếp tục xử lý.