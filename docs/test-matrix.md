# Ma trận operation, scenario và invariant

## Campaign chính: 10 method–path

Allowlist dùng chung cho `raw` và `guided`:

| Collection | List GET | List POST | Detail GET | Detail PATCH | Detail DELETE |
|---|---|---|---|---|---|
| `qa_articles` | `/items/qa_articles` | `/items/qa_articles` | `/items/qa_articles/{id}` | `/items/qa_articles/{id}` | `/items/qa_articles/{id}` |
| `qa_categories` | `/items/qa_categories` | `/items/qa_categories` | `/items/qa_categories/{id}` | `/items/qa_categories/{id}` | `/items/qa_categories/{id}` |

Bulk `PATCH` và bulk `DELETE` trên đường dẫn list không thuộc campaign chính. `scripts/lab-components.sh` kiểm tra editor schema có đủ 10 operation trước khi chạy.

## Profile và ngân sách

| Profile | Input | Overlay | Phases | Mục đích |
|---|---|---|---|---|
| `raw` | Editor raw schema | Chỉ chọn 10 operation; không sửa contract operation | `examples,coverage,fuzzing` | Kiểm schema gốc trong phạm vi đã chọn |
| `guided` | Bản copy riêng từ editor raw schema | Thêm ID fixture, request example hợp lệ và `x-r06-k05-guidance` | `examples,coverage,fuzzing,stateful` | Đi sâu vào dữ liệu và liên kết nghiệp vụ |

Giá trị mặc định: một worker, `5/s`, timeout request 10 giây, tối đa 100 example/operation, tối đa 1.200 giây/profile/seed, seed `101,202,303`. Pilot ngắn đã chạy với seed `101`, max examples `1`, và max time lần lượt 30 giây (`raw`) / 20 giây (`guided`); đó không phải kết quả campaign đầy đủ.

Campaign bật tường minh các check `not_a_server_error`, `status_code_conformance`, `content_type_conformance`, `response_schema_conformance`, `unsupported_method`, `negative_data_rejection` và `positive_data_acceptance`. Không dùng blanket skip/xfail; failure và warning được giữ trong report.

Mỗi seed tạo thư mục `artifacts/runs/<run_id>/<profile>/seed-<seed>/` với schema copy, hash, diff, inventory, metrics, report JSON/NDJSON, coverage, generation database, summary và snapshot để restore. Fixture được khôi phục trước khi seed kế tiếp tiếp tục.

## Sáu scenario demo

| ID | Precondition | Expected/oracle | Kết quả baseline |
|---|---|---|---|
| S1 Editor CRUD | Fixture + Editor login | Create/read/PATCH/delete; PATCH giữ field không cập nhật; item bị xóa không còn data | passed |
| S2 Filter status | 6 published + 6 draft | Filter published trả đúng sáu fixture ID | passed |
| S3 Sort/pagination | Fixture cố định | `sort=title,id`, `limit`, `offset` và projection khớp oracle fixture | passed |
| S4 Reader không đọc draft | Reader schema có detail GET | Draft không lộ | blocked: Reader article operation absent |
| S5 Reader không lộ `internal_notes` | Reader có published read | Field kín không xuất hiện hoặc request bị từ chối | blocked: Reader article operation absent |
| S6 Reader ghi | Reader có detail PATCH | PATCH bị từ chối và Editor đọc lại thấy dữ liệu không đổi | blocked: Reader PATCH absent |

Run `20261011T035341Z-11908` ghi S1–S3 passed, S4–S6 blocked; exit code 1 là có chủ đích vì còn precondition blocked.

## Invariant/replay IDs

Các case ổn định được chạy bởi `scripts/invariants.py`: `auth-invalid-token`, `anonymous-denied`, `editor-crud`, `query-fixture`, `relation-nullification`, `invalid-field-rejection`, `reader-visibility`, `reader-write`. `reader-visibility` và `reader-write` kiểm tra schema trước; khi operation vắng mặt chúng ghi `blocked` và không gửi request cấm.

Expected status của negative case là quan hệ `non-2xx`, không gán cứng 401/403/404 khi baseline chưa chứng minh mã cụ thể. Chi tiết precondition, request path, expected/actual và response summary được lưu trong `invariant-report.json`; token không được ghi.
