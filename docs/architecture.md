# Kiến trúc phòng kiểm thử R06 + K05

```mermaid
flowchart LR
    U["Sinh viên / client"] --> L["lab.sh"]
    L --> D["Directus 12.5.0"]
    S["Seed và smoke"] --> D
    T["Schemathesis runner"] --> D

    subgraph API["Directus trong network r06-k05_network"]
        D1["Auth và query middleware"] --> D2["REST controllers"]
        D2 --> D3["Item services"]
        D3 --> D4["Permissions và validation"]
        D4 --> DB[("PostgreSQL 16")]
        D1 --> O["OpenAPI theo accountability"]
    end

    O --> F["Schema snapshot theo actor"]
    F --> T
    T --> R["Run metadata, report, reproducer"]
```

Luồng kiểm thử phải tách thành ba phần có thể kiểm tra riêng:

1. `lab.sh` xác minh URL, container, cấu hình và precondition.
2. Seed/scenario tạo dữ liệu biết trước, actor và oracle nghiệp vụ.
3. Schemathesis nhận schema đã xuất từ instance đã seed, chạy đúng allowlist rồi lưu metadata và report.

Request REST đi qua xác thực và chuẩn hóa query, vào controller, qua service item, permission/validation rồi mới truy vấn PostgreSQL. Endpoint OpenAPI dùng accountability của người gọi nên schema của `admin`, `editor` và `reader` phải được lưu riêng.

Phạm vi trước giữa kỳ là REST trên `qa_categories` và `qa_articles`, năm operation mỗi collection. GraphQL, WebSocket, Studio, API quản trị, nhiều database, load testing và dịch vụ ngoài lab nằm ngoài campaign chính.
