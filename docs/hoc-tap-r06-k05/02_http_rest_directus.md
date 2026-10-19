# Bài 2 — HTTP, REST và Directus

## 2.1. Cấu trúc một request

Một request API gồm method, URL/path, query, headers và body:

```http
PATCH /items/qa_articles/17?fields=id,title,score HTTP/1.1
Host: 127.0.0.1:8055
Authorization: Bearer <token-lấy-từ-login>
Content-Type: application/json

{"score": 5}
```

- **Method** biểu diễn ý định: `GET` đọc, `POST` tạo, `PATCH` cập nhật một phần, `DELETE` xóa.
- **Path** xác định tài nguyên.
- **Query** điều khiển filter, sort, phân trang, projection hoặc aggregate.
- **Authorization** gắn actor; token không được ghi vào Git/log/report.
- **Body** chứa dữ liệu tạo hoặc cập nhật.

Response cần đọc cả status, headers và body. `Content-Type: application/json` không đảm bảo body đúng schema hoặc đúng nghiệp vụ.

## 2.2. Nhóm status thường gặp

| Nhóm | Ý nghĩa học tập |
|---|---|
| `2xx` | Thao tác được xử lý thành công; vẫn cần kiểm body và side effect |
| `3xx` | Chuyển hướng; API harness thường phải xử lý rõ, không bỏ qua |
| `4xx` | Request/actor không hợp lệ hoặc không được phép; cần phân biệt oracle |
| `5xx` | Lỗi phía server; là tín hiệu quan trọng nhưng cần triage root cause |

Trong baseline của đồ án, token sai được kiểm tra như lỗi xác thực và Reader PATCH bị từ chối với `403` trong evidence cuối. Không được chuyển quy tắc của run này thành quy luật bất biến cho mọi Directus version/configuration.

## 2.3. Login và token

Luồng xác thực cơ bản:

```http
POST /auth/login
Content-Type: application/json

{"email":"<actor-email>","password":"<actor-password>"}
```

Response login chứa access token. Harness lưu token trong biến chạy hoặc artifact đã redaction, sau đó gửi `Authorization: Bearer ...`. Test token không hợp lệ phải dùng giá trị giả không mang bí mật thật; expected là request không được coi là authenticated.

Không đặt password/key/license vào ví dụ, issue, screenshot hoặc commit. File `config/lab.env` bị ignore và phải có quyền `600`.

## 2.4. Resource và collection của đồ án

Lab có hai collection nghiệp vụ:

### `qa_categories`

- `id`: số nguyên tự tăng.
- `name`: bắt buộc.

### `qa_articles`

- `id`: số nguyên tự tăng.
- `title`: bắt buộc, tối đa 120 ký tự.
- `status`: `draft` hoặc `published`.
- `score`: số nguyên từ 0 đến 5.
- `published_at`: nullable.
- `metadata`: JSON, nullable.
- `internal_notes`: trường nội bộ, nullable.
- `category`: quan hệ nhiều–một tới `qa_categories`, có thể null; xóa category đặt relation về null.

ID là tự sinh. Test phải đọc [fixture map](../../scripts/lab-components.sh) hoặc artifact `fixture-map.json`, không hard-code `1`, `2`, `3` như thể ID luôn giống nhau.

## 2.5. Query Directus cần hiểu

Ví dụ đọc các article published, chọn field, sort và phân trang:

```http
GET /items/qa_articles?filter[status][_eq]=published&fields=id,title,status,category&sort=-id&limit=2&offset=0
```

Các query trọng tâm của kế hoạch:

| Query | Câu hỏi cần kiểm |
|---|---|
| `fields` | Projection có chỉ trả field được yêu cầu và tôn trọng policy không? |
| `filter` | Điều kiện có lọc đúng fixture không? |
| `sort` | Thứ tự có ổn định với khóa phụ `id` không? |
| `limit/offset` | Trang có đúng kích thước và không trùng/mất item không? |
| `page` | Cách quy đổi trang có đúng baseline không? |
| `search` | Tìm kiếm có trả đúng nhóm dữ liệu không? |

Khi kiểm tra pagination, nên dùng sort ổn định như `-id,id` hoặc chiến lược tương đương được Directus hỗ trợ. Nếu dữ liệu đồng hạng, sort một field không đủ để chứng minh thứ tự ổn định.

## 2.6. Năm luồng nghiệp vụ

### Luồng 1 — Đăng nhập

Precondition: Directus healthy và actor đã seed. Gửi login đúng; sau đó gửi token sai. Oracle gồm login đúng tạo token sử dụng được và token sai không cho truy cập được tài nguyên bảo vệ.

### Luồng 2 — Editor CRUD article

Editor tạo article hợp lệ, đọc lại, PATCH một field, đọc lại để xác minh field khác còn nguyên, rồi DELETE và kiểm tra không còn truy cập theo semantics thực tế. Dữ liệu tạo tạm phải có `run_id` để cleanup không nhầm fixture.

### Luồng 3 — Query

Dùng fixture cố định để kiểm filter `status`, sort, `limit/offset`, `page` và projection. Expected phải tính từ dữ liệu seed, không lấy response hiện tại làm expected sau khi test đã chạy.

### Luồng 4 — Quan hệ category

Tạo/read article có category thật; đọc quan hệ; thử category null theo scenario hợp lệ; kiểm tra xóa category có đặt article relation về null như contract đã thiết kế.

### Luồng 5 — Reader

Reader đọc published, không thấy draft hoặc `internal_notes`, không ghi. Với operation không xuất hiện trong schema Reader, harness không gửi request có chủ đích để “chứng minh bị cấm”; đó là trường hợp schema đã lọc operation và phải ghi semantics đúng.

## 2.7. Quyền trong lab

| Actor | Quyền chính |
|---|---|
| Admin | Bootstrap, schema và policy; dùng để kiểm tra trạng thái, không làm actor fuzz mặc định |
| Editor | CRUD hai collection trong phạm vi được cấp |
| Reader | Đọc category và article published; không thấy `internal_notes`; không ghi/quản trị/Studio |
| Anonymous | Không truy cập hai collection |

Policy phải được kiểm qua API thật. Nếu request anonymous bị từ chối, cần ghi actor không có token; nếu Reader đã login nhưng bị cấm, cần ghi actor và status thực tế.

## 2.8. Bài thực hành nhỏ

1. Gọi health và giải thích vì sao health chưa chứng minh quyền.
2. Login Editor, tạo một article có `metadata` Unicode và `published_at: null`.
3. Đọc lại bằng `fields=id,title,status,metadata,published_at,category`.
4. PATCH chỉ `score`, sau đó chứng minh `title` và `metadata` không mất.
5. Xóa item tạm và ghi `run_id`/evidence.

Không dán token vào terminal history công khai. Hãy dùng `lab.sh test scenarios` để học luồng đã được redaction và cleanup.

Đọc tiếp: [Bài 3 — Kiến trúc lab](03_kien_truc_lab.md).

