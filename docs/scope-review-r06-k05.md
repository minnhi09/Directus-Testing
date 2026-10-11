# Rà soát phạm vi R06 + K05

Ngày rà soát: `2026-10-11`
Baseline local: Directus `12.5.0`, PostgreSQL `16`, Schemathesis `4.30.0`,
fixture `r06-k05-v2`.

Tài liệu này là điểm quy chiếu cho việc kiểm tra dự án có còn đúng phạm vi đề
tài hay không. Nó không thay thế `yeu_cau.pdf`, không sửa kế hoạch nguồn và
không biến kết quả chưa xác minh thành kết luận.

## 1. Nguồn yêu cầu và nguyên tắc kết luận

Thứ tự ưu tiên khi đối chiếu là:

1. `yeu_cau.pdf` — yêu cầu môn học, được giữ nguyên.
2. Kế hoạch triển khai và kế hoạch phân công hiện có — dùng để truy vết đầu
   ra A–H, mốc và phân công; không coi mọi đề xuất trong kế hoạch là bằng
   chứng đã triển khai.
3. Quyết định kỹ thuật và tiêu chí G1 đã được cập nhật — quyết định phạm vi
   nội bộ đã được người dùng chốt.
4. Run metadata, report, log và artifact — nguồn duy nhất để kết luận một
   bước đã thực sự chạy.

Các tài liệu hiện có ghi nhận `yeu_cau.pdf` không định nghĩa thuật ngữ G1.
Vì vậy G1 là mốc nghiệm thu kỹ thuật nội bộ. Yêu cầu README để người khác có
thể dựng lại và yêu cầu peer-review/peer-evaluation cuối kỳ của đề bài vẫn
được giữ; chúng không bị chuyển thành điều kiện phải chạy trên máy thứ hai
hoặc review chéo để đóng G1. Schema, report và failure history vẫn phải được
giữ nguyên khi kiểm tra lại.

Trạng thái dùng trong tài liệu này:

- `PASS`: lệnh đã chạy, precondition hợp lệ và oracle đạt.
- `FAIL`: lệnh hoặc oracle thất bại; giữ mã thoát và artifact.
- `BLOCKED`: chưa được phép gửi request hoặc thiếu điều kiện bắt buộc.
- `UNRESOLVED`: có hiện tượng/reproducer nhưng chưa đủ căn cứ phân loại thành
  lỗi sản phẩm.
- `INCOMPLETE`: hết budget/thời gian; không suy diễn thành coverage đạt.

## 2. Phạm vi R06 — hệ thống được kiểm thử

R06 trong repository này là kiểm thử REST API của Directus, không phải phát
triển hoặc sửa Directus upstream.

| Thành phần | Phạm vi đang áp dụng |
|---|---|
| SUT | Directus `12.5.0`, image và digest được pin trong `manifest/baseline.yaml` |
| Dữ liệu | `qa_categories` và `qa_articles`; 3 category, 12 article, 6 draft và 6 published, Unicode và nullable |
| Actor | Admin bootstrap, Editor CRUD, Reader chỉ đọc published/không thấy `internal_notes`, Anonymous bị từ chối |
| Quy tắc dữ liệu | title bắt buộc/tối đa 120 ký tự, status `draft/published`, score nguyên 0–5, `published_at` nullable, metadata JSON, quan hệ category nullable |
| Hạ tầng | Compose project `r06-k05`, PostgreSQL riêng, API host loopback `127.0.0.1:8055`, runner truy cập `directus:8055` |
| Dữ liệu kiểm thử | ID lấy từ `runtime/fixture-ids.json`; không hard-code ID tự sinh |

Ngoài phạm vi chính: GraphQL, WebSocket, frontend automation, load/performance
testing, nhiều DB đối chứng, Redis/S3/email và quét API quản trị. Đây cũng
không phải bài sửa lỗi Directus upstream; candidate chỉ được gọi là product
defect sau khi có đủ bằng chứng contract/source/runtime.

## 3. Phạm vi K05 — kỹ thuật kiểm thử

K05 được thực hiện như schema-based API testing/fuzzing có kiểm soát:

1. Seed và policy trước, sau đó xuất OpenAPI động riêng cho Admin, Editor,
   Reader và Anonymous. Raw snapshot không bị sửa.
2. Campaign chính dùng đúng 10 method–path: GET/POST list và
   GET/PATCH/DELETE detail cho mỗi collection. Bulk PATCH/DELETE trên list
   không thuộc allowlist.
3. `raw` giữ hợp đồng gốc trong allowlist; `guided` dùng bản overlay riêng
   với ID fixture, example hợp lệ và links/hooks khi phù hợp. Kết quả guided
   không được ghi đè kết quả raw.
4. Check nền gồm 5xx, status, content type và response schema; các check
   positive/negative và unsupported method được bật tường minh.
5. Test bổ trợ kiểm tra auth, CRUD, query, quan hệ, Reader policy, invariant
   read-after-write, PATCH preservation, delete semantics, rejected-request
   immutability và replay có precondition/expected/actual.
6. Ngân sách mặc định là một worker, khoảng `5/s`, timeout `10s`, tối đa 100
   example/operation, tối đa 1.200 giây/profile/seed với seed `101`, `202`,
   `303`. Hết budget phải ghi `INCOMPLETE`/`failed_or_incomplete`.

Không dùng Schemathesis để tuyên bố coverage code của Directus. Số request,
check failure và số defect là ba đại lượng khác nhau.

## 4. Năm luồng nghiệp vụ trong phạm vi

| Luồng R06 | Hoạt động | K05 kiểm tra và bằng chứng |
|---|---|---|
| 1. Xác thực | Login actor, token sai và anonymous | Smoke/invariant `auth-invalid-token`, `anonymous-denied`; không ghi token vào artifact |
| 2. Editor CRUD | Tạo, đọc, sửa, xóa article/category | S1, `positive-operations` và allowlist 10 operation; ID lấy từ response, read-back và cleanup |
| 3. Query | Filter status, sort, pagination, fields/projection | S2–S3, fixture oracle, raw/guided query checks |
| 4. Quan hệ category | Đọc/ghi relation và xóa category theo ngữ nghĩa `SET NULL` | Smoke relation, positive operation và invariant relation |
| 5. Reader policy | Published-only, không lộ `internal_notes`, không ghi | S4–S6, `reader-visibility`, `reader-write`; không gửi request cấm nếu operation không xuất trong schema |

Các tài liệu cũ tách luồng thành sáu scenario để dễ demo: S1 Editor CRUD,
S2 filter, S3 sort/pagination, S4 Reader draft, S5 private field và S6 Reader
write. Đây là cách phân rã của năm luồng trên, không phải mở rộng phạm vi.

## 5. Đối chiếu tiêu chí G1 hiện hành

| Tiêu chí kỹ thuật | Bằng chứng gần nhất | Kết luận |
|---|---|---|
| Stack healthy, version/digest đúng | Doctor `20261011T145849Z-187766`, exit `0` | Đạt trên máy hiện tại |
| Seed, fixture, actor và policy | Smoke `20261011T145854Z-188363`, exit `0` | Đạt trên baseline v2 |
| Năm luồng/nghiệp vụ và oracle | Scenarios `20261011T145912Z-189309`: 6 passed, 0 failed, 0 blocked | Đạt |
| Schema theo actor và 10 operation | Export `20261011T145907Z-188832`: 14/14/6/0 theo actor; allowlist campaign 10/10 | Đạt; raw hash bất biến |
| Raw/guided độc lập, artifact và restore | Raw `20261011T085034Z-76481`, guided `20261011T095117Z-89079` | Có bằng chứng chạy đủ 3 seed/10 operation; runner vẫn `exit 1` do check failure/max-time |
| Invariant, replay và phân loại | Invariant `20261011T145918Z-189799`: 9 pass, 2 fail, 0 blocked; targeted replay `20261011T144640Z-184631`/`20261011T144648Z-185062`, replay demo 7/7 PASS | Harness đạt; finding chưa đóng, không phải PASS giả |
| Tái lập | README, Compose, manifest, fixture map, schema hash, metadata và replay | Có hướng dẫn/cấu hình; chưa tuyên bố đã chạy trên máy khác |
| Review chéo thành viên | Đã loại khỏi gate G1 | Không áp dụng cho G1; provenance review thật vẫn không được bịa |
| Dựng/xác minh máy thứ hai | Đã loại khỏi gate G1 | Không áp dụng cho G1; khả năng dựng máy sạch vẫn phải được tài liệu hóa |

Kết luận hiện tại: **G1 đạt baseline kỹ thuật local với findings chưa đóng**.
Đây không phải kết luận rằng raw/guided hoặc invariant đều PASS.

## 6. Failure đang mở và cách phân loại

- Aggregate `{"foo":1}` tái hiện HTTP 500, trong khi hai control trả 200:
  `schema omission + product robustness candidate`, chưa xác nhận product
  defect.
- POST response shape, alternate export media type/shape, DELETE `204` và
  projection thiếu field là `schema/contract candidate`; không đếm mỗi
  response/check thành một defect.
- `published_at=""`, safe-number query, coercion `name` và các negative/status
  mismatch là `schema-semantic`, generator hoặc precondition/oracle mismatch
  cho đến khi có bằng chứng ngược lại.
- Parent-ID mapping và stateful final-request-only là
  `harness/fixture/stateful limitation`; không kết luận API đã chấp nhận hay
  từ chối cả chuỗi nếu target chưa được gửi.
- Hết `max_time`/check failure của campaign là `INCOMPLETE` hoặc failure cần
  triage, không phải defect count.

Không có product defect Directus nào được xác nhận chính thức tại checkpoint
này. Các failure và exit code vẫn được giữ trong artifact/evidence.

## 7. Phần còn lại theo đúng phạm vi

Không còn blocker kỹ thuật ngăn việc demo pipeline local. Nếu cần nâng mức
kết luận cuối kỳ, các việc tiếp theo là:

1. Đối chiếu các contract candidate với schema/runtime của đúng bản Directus
   đã pin và ghi quyết định triage; không sửa raw schema để làm campaign xanh.
2. Hoàn thiện replay full-chain cho case có đủ parent artifact; case thiếu
   precondition tiếp tục để `UNRESOLVED`.
3. Nếu chạy lại campaign, phải giữ ba seed, budget và mã thoát; không cần chạy
   lại chỉ vì tài liệu được đồng bộ.
4. Chuẩn bị demo và peer-evaluation cuối kỳ theo yêu cầu riêng của đề bài,
   không ghi chúng thành bằng chứng G1 đã xảy ra.

Tài liệu liên quan: [`docs/g1-acceptance.md`](g1-acceptance.md),
[`docs/test-matrix.md`](test-matrix.md), [`docs/traceability.md`](traceability.md),
[`evidence/final-handoff-2026-10-11.md`](../evidence/final-handoff-2026-10-11.md)
và [`README.md`](../README.md).
