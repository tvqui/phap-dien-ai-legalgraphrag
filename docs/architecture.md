# Kiến trúc tổng thể

```text
Nguồn pháp luật → OFFLINE pipeline → Registry/Provisions/Graph/Indexes
                                               ↓
Frontend → ONLINE API → Query analysis → Hybrid retrieval → Applicability
                                               ↓
                                  Verified Evidence Pack
                                               ↓
                                  Adjudication → Reference Audit
```

Mã nguồn backend nằm trong `src/offline/src/vn_labor_offline` và `src/online/backend/src/vn_labor_online`; `src/online/frontend` chỉ gọi API và không tự thực hiện suy luận pháp lý.
