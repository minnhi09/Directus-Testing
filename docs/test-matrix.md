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

## Kết quả campaign lịch sử trước license — `r06-k05-v1`

| Profile/run | Seed | Operation tested | Cases generated | Unique failure | Errored | Restore | Trạng thái runner |
|---|---:|---:|---:|---:|---:|---|---|
| raw / `20261011T050204Z-28735` | 101 | 10/10 | 59 | 20 | 0 | PASS | `failed`, `max_time`, exit 1 |
| raw / cùng run | 202 | 10/10 | 65 | 18 | 0 | PASS | `failed`, `max_time`, exit 1 |
| raw / cùng run | 303 | 10/10 | 51 | 19 | 0 | PASS | `failed`, `max_time`, exit 1 |
| guided / `20261011T060247Z-30882` | 101 | 10/10 | 5.809 | 63 | 111 | PASS | `failed`, `max_time`, exit 1 |
| guided / cùng run | 202 | 10/10 | 5.874 | 65 | 176 | PASS | `failed`, `max_time`, exit 1 |
| guided / cùng run | 303 | 10/10 | 5.899 | 62 | 200 | PASS | `failed`, `max_time`, exit 1 |

Các số unique failure là số của từng seed, không cộng thành số defect. Report cần triage theo request/chuỗi stateful cụ thể; `500`, response ngoài schema, status/content type ngoài hợp đồng và unsupported method không tự động là defect. Mười case guided đã replay được hoặc được replay có report (`AmXHZz`, `jShXuk`, `VllBgh`, `kb5gjq`, `F8j8Gl`, `UNKW3j`, `R0sH5o`, `DhqXrn`, `UTk4sa`, `6IayFG`); trong đó hai case POST response shape được gộp thành một schema/contract candidate, `VllBgh` là aggregate robustness candidate, `kb5gjq` là timestamp schema-semantic/robustness candidate, `F8j8Gl`/`UNKW3j`/`R0sH5o` là export candidates, `DhqXrn` là negative precondition/policy mismatch, `UTk4sa` là stateful setup limitation và `6IayFG` là query safe-number schema/generator candidate, chưa phải defect đã xác nhận. Raw dùng schema hash `433cb61a...`; guided dùng overlay hash `dc3f057a...`, được lưu tách khỏi schema raw. Triage và replay đại diện được ghi tại [`docs/campaign-triage-2026-10-11.md`](campaign-triage-2026-10-11.md); chưa có product defect nào được xác nhận.

## Kết quả campaign local hiện tại — `r06-k05-v2`

Raw run `20261011T085034Z-76481`, schema hash
`433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`:

| Seed | Operation | Cases | Unique failure | Errored | Restore | Kết thúc |
|---:|---:|---:|---:|---:|---|---|
| 101 | 10/10 | 59 | 20 | 0 | PASS | `max_time`, exit 1 |
| 202 | 10/10 | 65 | 18 | 0 | PASS | `max_time`, exit 1 |
| 303 | 10/10 | 51 | 19 | 0 | PASS | `max_time`, exit 1 |

Guided run `20261011T095117Z-89079`, overlay hash
`cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`:

| Seed | Operation | Cases | Unique failure | Errored | Stateful scenarios | Links | Restore | Kết thúc |
|---:|---:|---:|---:|---:|---:|---:|---|---|
| 101 | 10/10 | 5770 | 63 | 111 | 1141 | 14/20 | PASS | `max_time`, exit 1 |
| 202 | 10/10 | 5864 | 65 | 176 | 1183 | 19/20 | PASS | `max_time`, exit 1 |
| 303 | 10/10 | 5894 | 62 | 200 | 1195 | 16/20 | PASS | `max_time`, exit 1 |

Các campaign v2 có report/coverage đầy đủ và restore PASS, nhưng `failed` là
trạng thái trung thực do check failure và hết budget; không xem số case hay
operation coverage là defect count. Raw/guided sử dụng cùng 10 operation đã
được allowlist, còn guided chỉ sửa bản overlay riêng.

Triage đại diện sau campaign (kèm phân loại schema/precondition, stateful
replay mismatch và candidate HTTP 500) được lưu tại
[`evidence/failure-triage-v2-2026-10-11.md`](../evidence/failure-triage-v2-2026-10-11.md).
Hai stateful mismatch trong báo cáo không làm campaign thành PASS; chúng là
giới hạn tái dựng chuỗi cần giữ ở trạng thái chưa kết luận.

## Sáu scenario demo

| ID | Precondition | Expected/oracle | Kết quả baseline |
|---|---|---|---|
| S1 Editor CRUD | Fixture + Editor login | Create/read/PATCH/delete; PATCH giữ field không cập nhật; item bị xóa không còn data | passed |
| S2 Filter status | 6 published + 6 draft | Filter published trả đúng sáu fixture ID | passed |
| S3 Sort/pagination | Fixture cố định | `sort=title,id`, `limit`, `offset` và projection khớp oracle fixture | passed |
| S4 Reader không đọc draft | Reader schema có detail GET | Draft không lộ | passed: HTTP 403, không có draft payload |
| S5 Reader không lộ `internal_notes` | Reader có published read | Field kín không xuất hiện hoặc request bị từ chối | passed: published projection 2xx; private projection HTTP 403 |
| S6 Reader ghi | Reader có detail PATCH | PATCH bị từ chối và Editor đọc lại thấy dữ liệu không đổi | passed: HTTP 403, dữ liệu không đổi |

Run v2 `20261011T105231Z-104612` ghi S1–S6 passed. Run v1
`20261011T035341Z-11908` vẫn được giữ như bằng chứng lịch sử S1–S3 passed,
S4–S6 blocked trước license.

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
`query-fixture`, `aggregate-query-robustness`, `contract-schema-candidates`, `relation-nullification`,
`invalid-field-rejection`, `reader-visibility`, `reader-write`.
`aggregate-query-robustness` là regression probe không mutation, dùng query
`fields=&aggregate={"foo":1}` và hai control `aggregate={}`/
`aggregate={"count":["id"]}`. Probe yêu cầu variant unknown không có HTTP 5xx,
control trả 2xx; trên baseline v2 variant unknown tái hiện candidate 500 và giữ
trạng thái `failed`, còn hai control trả 200. Recheck này nằm ở run
`20261011T134519Z-160153` dưới harness `bcbf219`. `reader-visibility` và
`reader-write` kiểm tra schema trước; v2 có operation cần thiết nên đã gửi request
và xác minh projection/private write theo hành vi thực tế. Nếu dựng máy không có
license và operation vắng mặt, hai case vẫn ghi `blocked` và không gửi request cấm.

`contract-schema-candidates` đối chiếu runtime Editor với response map/content
type/POST shape trong `editor.json`, dùng dữ liệu tạm và cleanup sau probe. Run
`20261011T130227Z-139257` ghi bốn schema candidate và giữ exit `1`; đây là số
candidate contract, không phải số product defect.

Expected status của negative case là quan hệ `non-2xx`, không gán cứng 401/403/404 khi baseline chưa chứng minh mã cụ thể. Chi tiết precondition, request path, expected/actual và response summary được lưu trong `invariant-report.json`; token không được ghi.
