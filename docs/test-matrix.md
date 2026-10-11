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

Giá trị mặc định: một worker, `5/s`, timeout request 10 giây, tối đa 100 example/operation, tối đa 1.200 giây/profile/seed, seed `101,202,303`. Pilot ngắn dùng seed `101`, max examples `1` và max time 30 giây (`raw`) / 20 giây (`guided`); kết quả pilot không được trộn với campaign đầy đủ.

Campaign bật tường minh các check `not_a_server_error`, `status_code_conformance`, `content_type_conformance`, `response_schema_conformance`, `unsupported_method`, `negative_data_rejection` và `positive_data_acceptance`. Không dùng blanket skip/xfail; failure và warning được giữ trong report.

Mỗi seed tạo thư mục `artifacts/runs/<run_id>/<profile>/seed-<seed>/` với schema copy, hash, diff, inventory, metrics, report JSON/NDJSON, coverage, generation database, summary và snapshot để restore. Fixture được khôi phục trước khi seed kế tiếp tiếp tục.

## Kết quả campaign đầy đủ trên baseline hiện tại

| Profile/run | Seed | Operation tested | Cases generated | Unique failure | Errored | Restore | Trạng thái runner |
|---|---:|---:|---:|---:|---:|---|---|
| raw / `20261011T050204Z-28735` | 101 | 10/10 | 59 | 20 | 0 | PASS | `failed`, `max_time`, exit 1 |
| raw / cùng run | 202 | 10/10 | 65 | 18 | 0 | PASS | `failed`, `max_time`, exit 1 |
| raw / cùng run | 303 | 10/10 | 51 | 19 | 0 | PASS | `failed`, `max_time`, exit 1 |
| guided / `20261011T060247Z-30882` | 101 | 10/10 | 5.809 | 63 | 111 | PASS | `failed`, `max_time`, exit 1 |
| guided / cùng run | 202 | 10/10 | 5.874 | 65 | 176 | PASS | `failed`, `max_time`, exit 1 |
| guided / cùng run | 303 | 10/10 | 5.899 | 62 | 200 | PASS | `failed`, `max_time`, exit 1 |

Các số unique failure là số của từng seed, không cộng thành số defect. Report cần triage theo request/chuỗi stateful cụ thể; `500`, response ngoài schema, status/content type ngoài hợp đồng và unsupported method không tự động là defect. Ba case guided đã replay được (`AmXHZz`, `jShXuk`, `VllBgh`); trong đó hai case POST được gộp thành một schema/contract candidate và `VllBgh` là product robustness candidate kèm schema omission, chưa phải defect đã xác nhận. Raw dùng schema hash `433cb61a...`; guided dùng overlay hash `dc3f057a...`, được lưu tách khỏi schema raw. Triage và replay đại diện được ghi tại [`docs/campaign-triage-2026-10-11.md`](campaign-triage-2026-10-11.md); chưa có product defect nào được xác nhận.

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

## Positive operation acceptance

Case `positive-operations` chạy tuần tự bằng Editor và tạo dữ liệu tạm. Case
này kiểm tra từng operation trong allowlist 10 method–path:

- POST/GET list/GET detail/PATCH/DELETE cho `qa_categories`.
- POST/GET list/GET detail/PATCH/DELETE cho `qa_articles`.

ID được lấy từ response POST; PATCH được đọc lại để kiểm tra field không cập
nhật vẫn giữ nguyên; DELETE được đọc lại để xác nhận tài nguyên không còn data;
cuối case dữ liệu tạm được dọn. Report tách positive operation coverage khỏi
operation hit của Schemathesis.

## Invariant/replay IDs

Các case ổn định được chạy bởi `scripts/invariants.py` trong runner Docker:
`auth-invalid-token`, `anonymous-denied`, `editor-crud`, `positive-operations`,
`query-fixture`, `relation-nullification`, `invalid-field-rejection`,
`reader-visibility`, `reader-write`. `reader-visibility` và `reader-write`
kiểm tra schema trước; khi operation vắng mặt chúng ghi `blocked` và không gửi
request cấm.

Expected status của negative case là quan hệ `non-2xx`, không gán cứng 401/403/404 khi baseline chưa chứng minh mã cụ thể. Chi tiết precondition, request path, expected/actual và response summary được lưu trong `invariant-report.json`; token không được ghi.
