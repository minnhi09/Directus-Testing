# Bằng chứng triển khai và xác minh runtime — 2026-10-11

Tài liệu này chỉ ghi kết quả đã quan sát trên máy hiện tại. Các phần trước
heading “Checkpoint license và baseline v2” là bằng chứng lịch sử của fixture v1;
phần v2 là checkpoint dùng để đánh giá G1 hiện hành. Không có run máy thứ hai
được ghi nhận và cũng không cần tạo run đó để đóng G1; campaign vẫn giữ nguyên
trạng thái kết thúc thực tế bên dưới.

## Baseline đã xác minh

- Directus `12.5.0`, image digest `sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331`, image label revision `4f77933bf9551cac6b289576078783e189b8f4e3`.
- PostgreSQL 16 Alpine, digest `sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea`.
- Schemathesis `4.30.0`, digest `sha256:bb9cecfc9ac4058a15fcf9b505d9d9f972e2dde7c74c4e9289a35922f4cbc0a5`.
- Docker project/network/volume: `r06-k05`, `r06-k05_network`, `r06-k05_db_data`.
- Host API `http://127.0.0.1:8055`; runner API `http://directus:8055`.

## Run đã thực hiện

| Run | Lệnh | Kết quả quan sát |
|---|---|---|
| `20261011T035004Z-7785` | `./lab.sh seed` | Dựng schema, fixture map và actor; dừng ở `custom_permission_rules_enabled=false` |
| `20261011T035010Z-8515` | `./lab.sh export-schema` | PASS; lưu 4 schema theo actor, hash và operation count |
| `20261011T035014Z-9007` | `./lab.sh test invariants` | 5 passed, 0 failed, 2 blocked; exit 1 do Reader precondition |
| `20261011T035021Z-9361` | raw pilot, seed 101 | 10/10 operation có hit, 69 test case, report/coverage có, restore PASS; runner failure và dừng max-time |
| `20261011T035101Z-9882` | guided pilot, seed 101 | 10/10 operation có hit, 86 test case, stateful phase có chạy, restore PASS; runner failure và dừng max-time |
| `20261011T035323Z-10548` | `./lab.sh replay editor-crud` | PASS; create/read/PATCH/delete và field preservation |
| `20261011T035333Z-10935` | `./lab.sh doctor` | PASS; image digest, fixture map, liveness và authenticated health |
| `20261011T035337Z-11497` | `./lab.sh smoke` | Field validation và `SET NULL` PASS; Reader article GET HTTP 403 nên run failed |
| `20261011T035341Z-11908` | `./lab.sh test scenarios` | S1–S3 passed, S4–S6 blocked; không gửi forbidden Reader request |
| `20261011T035355Z-12361` | `./lab.sh test smoke` | Xác nhận alias interface; kết quả Reader blocker như trên |
| `20261011T035408Z-12774` | `./lab.sh replay anonymous-denied` | PASS; hai collection trả non-2xx |
| `20261011T035610Z-13294` | `./lab.sh export-schema` recheck | PASS; bốn hash schema không đổi |
| `20261011T035615Z-13741` | `./lab.sh replay editor-crud` recheck | PASS; cleanup không gửi DELETE lặp |
| `20261011T035618Z-14109` | `./lab.sh replay query-fixture` | PASS; filter/sort/page/projection |
| `20261011T035623Z-14472` | `./lab.sh replay auth-invalid-token` | PASS; token giả trả HTTP 401 trên baseline |
| `20261011T035626Z-14831` | `./lab.sh test invariants` recheck | 6 passed, 0 failed, 2 blocked; exit 1 do Reader precondition |
| `20261011T035638Z-15197` | raw pilot recheck, seed 101, 10s | 10/10 operation tested, 41 case, 13 unique failure, restore PASS; exit 1 giữ failure |
| `20261011T035658Z-15731` | guided pilot recheck, seed 101, 10s | 10/10 operation tested, stateful chạy, 17 unique failure, restore PASS; exit 1 giữ failure |
| `20261011T035904Z-17158` | `./lab.sh doctor` final recheck | PASS; static checks, YAML và Compose config cũng PASS trong cùng checkpoint |
| `20261011T035909Z-17742` | `./lab.sh replay editor-crud` final recheck | PASS; CRUD invariant và cleanup |
| `20261011T040004Z-18580` | raw campaign metadata recheck, seed 101, 3s | Runner failure/restore PASS; top-level metadata now contains scoped schema hash, seed, budget và campaign index |
| `20261011T040029Z-19303` | `./lab.sh doctor` final runtime recheck | PASS; Directus authenticated health and all pinned images |
| `20261011T040109Z-19973` | `./lab.sh replay editor-crud` cleanup recheck | PASS; explicit cleanup path vẫn giữ CRUD invariant |
| `20261011T040113Z-20338` | `./lab.sh smoke` cleanup recheck | Field validation và `SET NULL` PASS; Reader vẫn HTTP 403 nên run failed đúng blocker |
| `20261011T040317Z-21776` | `./lab.sh replay ralwaW` | PASS/reproduced; Schemathesis case HTTP 403, reproducer sanitized và restore PASS |
| `20261011T040346Z-22406` | `./lab.sh replay ralwaW` scoped-hash recheck | PASS/reproduced; reproducer ghi đúng hash schema scoped `433cb61a...`, restore PASS |
| `20261011T040415Z-23383` | `./lab.sh doctor` final replay-code recheck | PASS; syntax/lint, YAML và Compose config cũng PASS |
| `20261011T043809Z-24724` | `./lab.sh test invariants` sau positive-operation | 7 passed, 0 failed, 2 blocked; đủ 10 operation positive đạt, Reader vẫn blocked |
| `20261011T043919Z-25183` | raw campaign lần đầu | Seed 101 hết budget nhưng token hết hạn trước restore; các seed sau không được chạy; run giữ lại để chứng minh lỗi lifecycle, không dùng làm campaign chính |
| `20261011T050050Z-26220` | `./lab.sh reset` | Safety preflight khớp project/volume/label; chỉ reset lab `r06-k05` và giữ artifact cũ |
| `20261011T050059Z-26669` | `./lab.sh up` sau reset | PASS; tạo lại stack riêng, Directus/PostgreSQL/runner healthy |
| `20261011T050124Z-27123` | `./lab.sh seed` sau reset | Schema/fixture/actor đạt; exit 1 tại license `custom_permission_rules_enabled=false` |
| `20261011T050148Z-27885` | `./lab.sh export-schema` sau reset | PASS; bốn schema theo actor, hash không đổi |
| `20261011T050155Z-28328` | `./lab.sh test invariants` sau reset | 7 passed, 0 failed, 2 blocked; runner Docker dùng image Schemathesis đã pin |
| `20261011T050204Z-28735` | `./lab.sh test raw` campaign đầy đủ | Seed 101/202/303 đều 10/10 operation; lần lượt 59/65/51 cases; đều `max_time`, runner exit 1, restore PASS |
| `20261011T060247Z-30882` | `./lab.sh test guided` campaign đầy đủ | Seed 101/202/303 đều 10/10 operation; lần lượt 5.809/5.874/5.899 cases; đều `max_time`, runner exit 1, restore PASS |
| `20261011T070408Z-35276` | `./lab.sh doctor` sau full campaigns | PASS; pinned images, fixture map và authenticated health đạt |
| `20261011T070417Z-35832` | `./lab.sh smoke` sau full campaigns | Field validation và `SET NULL` PASS; Reader article vẫn HTTP 403 do license |
| `20261011T070430Z-36257` | `./lab.sh test scenarios` sau full campaigns | S1–S3 passed, S4–S6 blocked; không gửi forbidden Reader request |
| `20261011T070437Z-36709` | `./lab.sh test invariants` sau full campaigns | 7 passed, 0 failed, 2 blocked; positive 10 operation và các invariant non-Reader đạt |
| `20261011T070445Z-37115` | `./lab.sh export-schema` final | PASS; schema hash actor giữ nguyên sau campaign |

Sau full campaign và các recheck cuối, cả `database`, `directus` và `runner` đều ở trạng thái `running/healthy`; image hiển thị đúng digest đã pin. Raw và guided đều thực thi đủ ba seed và đủ 10 operation mỗi seed, nhưng runner trả failure vì các check phát hiện; đây không phải trạng thái campaign pass. Cả sáu lần restore của hai profile đều PASS.

Các run metadata ghi `harness_sha` riêng. Tại thời điểm các run đầu, working tree còn dirty do thay đổi tích hợp có sẵn; đây là provenance thực tế, không được coi là clean release.

## Schema snapshot

Schema export final `20261011T070445Z-37115` (hash giữ nguyên so với `20261011T035010Z-8515`):

- Admin: 14 operation, hash `993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e`.
- Editor: 14 operation, hash `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26`.
- Reader: 2 operation, hash `20fbfe9a517710ac73d05622f4b158bab4ccbcd96da51ec61363268ed92683cb`.
- Anonymous: 0 operation, hash `2070c25c68193a4a42501935974bb3045697aceb1fe072bb3461f43c0a0342b3`.

## Triage sơ bộ

- Môi trường: Compose stack chạy và fixture được restore sau pilot.
- Policy/schema blocker: license không cho custom permission rules; không thể chứng minh Reader published-only/field restriction.
- Schema/contract candidate: full raw/guided có status `204/400/403` ngoài response map, content type export, POST response shape và unsupported `TRACE`; guided còn ghi nhận response schema, negative/positive data và một số `500`. Đây là nhóm phát hiện để triage, chưa kết luận product defect vì cần replay request cụ thể và đối chiếu contract/semantics của Directus.
- Chưa có product defect được xác nhận; chưa có run máy thứ hai trong provenance
  local, đây là giới hạn phạm vi chứ không phải gate G1 hiện hành.

### Số liệu campaign đầy đủ

| Profile | Run | Seed | Operation | Cases | Unique failure | Errored | Restore | Kết thúc |
|---|---|---:|---:|---:|---:|---:|---|---|
| raw | `20261011T050204Z-28735` | 101 | 10/10 | 59 | 20 | 0 | PASS | `max_time`, runner 1 |
| raw | cùng run | 202 | 10/10 | 65 | 18 | 0 | PASS | `max_time`, runner 1 |
| raw | cùng run | 303 | 10/10 | 51 | 19 | 0 | PASS | `max_time`, runner 1 |
| guided | `20261011T060247Z-30882` | 101 | 10/10 | 5.809 | 63 | 111 | PASS | `max_time`, runner 1 |
| guided | cùng run | 202 | 10/10 | 5.874 | 65 | 176 | PASS | `max_time`, runner 1 |
| guided | cùng run | 303 | 10/10 | 5.899 | 62 | 200 | PASS | `max_time`, runner 1 |

Schema hash raw của cả ba seed là `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`; guided overlay dùng hash `dc3f057aefb095c4c51ddb712de33d762176d0472f8e7af313522b0551824d7e`. Harness SHA trong metadata của cả hai run là `57d4c2dd25e6c99f128de0336e88e918a2deee79`.

## Recheck sau khi tiếp tục triển khai

Sau commit `c7cc8d7`, Compose nhận biến môi trường tùy chọn `LICENSE_KEY` nhưng
`config/lab.env` hiện không có khóa license. Run `20261011T073328Z-39520` xác
nhận `doctor` PASS, còn `/license` trả `source=null`, `status=active` và
`custom_permission_rules_enabled.default=false`.

Các run tiếp theo ghi nhận chính xác blocker và phần độc lập:

| Run | Lệnh | Kết quả |
|---|---|---|
| `20261011T073335Z-40109` | `./lab.sh seed` | Schema/fixture/actor idempotent đạt; exit 1 tại license precondition |
| `20261011T073350Z-40854` | `./lab.sh smoke` | Field validation và `SET NULL` PASS; Reader article GET HTTP 403 |
| `20261011T073356Z-41277` | `./lab.sh export-schema` | PASS; hash actor không đổi |
| `20261011T073401Z-41735` | `./lab.sh test scenarios` | S1–S3 passed, S4–S6 blocked |
| `20261011T073406Z-42194` | `./lab.sh test invariants` | 7 passed, 0 failed, 2 blocked |
| `20261011T073454Z-42697` | `./lab.sh replay UETNPW` | PASS/reproduced, actual 204, restore PASS |
| `20261011T073501Z-43256` | `./lab.sh replay 7DpEST` trước sửa | Mismatch do replay làm mất byte NUL; restore PASS |
| `20261011T073559Z-43850` | `./lab.sh replay 7DpEST` sau `686f4d1` | PASS/reproduced, expected/actual 400, restore PASS |

Mismatch của `7DpEST` là lỗi harness đã được sửa trong commit `686f4d1`; không
được tính là lỗi Directus. Phân loại campaign chi tiết nằm tại
[`docs/campaign-triage-2026-10-11.md`](../docs/campaign-triage-2026-10-11.md).

Pilot xác nhận sau sửa đổi:

- Raw `20261011T074023Z-44637`: 10/10 operation, 47 case, 15 unique failure,
  errored 0, restore PASS, runner exit 1 do `max_time`.
- Guided `20261011T074112Z-45270`: 10/10 operation, 134 case, 29 unique failure,
  errored 1, stateful phase chạy, restore PASS, runner exit 1 do `max_time`.
- Doctor `20261011T074209Z-45910`: PASS; fixture map, image digest và
  authenticated health đạt.
- Doctor `20261011T074349Z-47097`: PASS; probe `/license` báo
  `source=null`, `status=active`, `custom_permission_rules_enabled=false` và
  không ghi giá trị license/token.

## Replay triage tiếp theo trên HEAD `6fe1865`

| Run | Lệnh/kết quả thực tế |
|---|---|
| `20261011T075613Z-48561` | `./lab.sh replay AmXHZz`: `reproduced`; POST article expected/actual `200`, response `data` object thay vì array theo schema; restore PASS |
| `20261011T075622Z-49153` | `./lab.sh replay jShXuk`: `reproduced`; POST category expected/actual `200`, response `data` object thay vì array theo schema; restore PASS |
| `20261011T075632Z-49739` | `./lab.sh replay VllBgh`: `reproduced`; GET query expected/actual `500`, restore PASS |

Triage không đếm hai response-shape thành hai defect: chúng cùng một nhóm
schema/contract candidate. Với `VllBgh`, log container ở thời điểm replay ghi
`TypeError: fields is not iterable` tại `extractPathsFromQuery`. Phép thu gọn
chỉ GET trên cùng fixture cho thấy `fields=&aggregate={"foo":1}` vẫn trả
`500 INTERNAL_SERVER_ERROR`, trong khi `aggregate={}` và
`aggregate={"count":["id"]}` trả `200`. Schema OpenAPI hiện không cấm
`additionalProperties` của object `aggregate`, nên kết quả được phân loại là
schema omission + product robustness candidate; chưa kết luận product defect.

Các reproducer JSON, request đầy đủ và metadata nằm trong ba thư mục artifact
run nêu trên. Credential/token không được ghi vào report. Đây là bằng chứng local
trên một máy, không phải kiểm tra chéo hay xác nhận upstream.

Regression case deterministic sau triage: `./lab.sh replay
aggregate-query-robustness` ở run mới `20261011T134519Z-160153` dưới harness
`bcbf21955e87a03529f970eaccbe4d4312b74af6` dùng Editor GET
`/items/qa_articles?fields=&aggregate=%7B%22foo%22%3A1%7D` cùng hai control
`aggregate={}` và `aggregate={"count":["id"]}`. Kết quả lần lượt là `500`,
`200`, `200`; report giữ `failed`, exit `1`, harness SHA
`bcbf21955e87a03529f970eaccbe4d4312b74af6`; metadata ghi working tree dirty do
file untracked có trước. Đây là regression evidence cho
candidate đã triage, không phải kết luận product defect đã xác nhận. Run lịch sử
`20261011T080746Z-51887` vẫn được giữ để đối chiếu.

Toàn bộ invariant suite sau commit `66ee05f` ở run `20261011T080753Z-52280`:
7 case passed (`auth-invalid-token`, `anonymous-denied`, `editor-crud`,
`positive-operations`, `query-fixture`, `relation-nullification`,
`invalid-field-rejection`), 1 regression case failed
(`aggregate-query-robustness`, HTTP 500), và 2 Reader case blocked do schema
không có operation article/PATCH. Exit `1` được giữ nguyên; dữ liệu tạm được
cleanup, không có request Reader forbidden nào được gửi.

Final local doctor `20261011T081001Z-52769` PASS trên HEAD `828c339`: ba service
`database`, `directus`, `runner` healthy; image digest đúng manifest; Directus
authenticated health PASS; `/license` vẫn quan sát `source=null`, `status=active`,
`custom_permission_rules_enabled=false`. Static syntax/lint, YAML/Compose config
và tracked secret-pattern scan cũng PASS.

## Checkpoint license và baseline v2

Phần trên giữ nguyên bằng chứng lịch sử trước khi có license. Checkpoint mới sau
khi người dùng cấu hình `LICENSE_KEY` cục bộ không ghi giá trị key vào report:

| Run | Lệnh | Kết quả quan sát |
|---|---|---|
| `20261011T084813Z-71356` | `./lab.sh reset` | Safety preflight khớp project/volume; chỉ xóa `r06-k05_db_data` và runtime của lab |
| `20261011T084821Z-71845` | `./lab.sh up` | Network/volume/container tạo lại; database, Directus, runner healthy |
| `20261011T084845Z-72361` | `LAB_FIXTURE_VERSION=r06-k05-v2 ./lab.sh seed` | PASS; 3 category, 12 article, 6 draft/6 published, actor/policy PASS |
| `20261011T084854Z-73115` | `LAB_FIXTURE_VERSION=r06-k05-v2 ./lab.sh export-schema` | PASS; admin/editor/reader/anonymous 14/14/6/0 operation |
| `20261011T085023Z-75556` | `./lab.sh smoke` | PASS; validation, relation `SET NULL`, Reader published filter |
| `20261011T085027Z-75998` | `./lab.sh export-schema` | PASS theo default v2; raw schema hash bất biến |
| `20261011T105225Z-104013` | `./lab.sh doctor` | PASS; `/license` `source=env`, `status=active`, `custom_permission_rules_enabled=true` |
| `20261011T105231Z-104612` | `./lab.sh test scenarios` | S1–S6: 6 passed, 0 failed, 0 blocked |
| `20261011T105236Z-105096` | `./lab.sh test invariants` | 9 passed, 1 failed; failure duy nhất aggregate HTTP 500 |
| `20261011T105242Z-105524` | `./lab.sh replay aggregate-query-robustness` | Tái hiện HTTP 500, exit 1, không mutation |
| `20261011T134519Z-160153` | `./lab.sh replay aggregate-query-robustness` | `unknown-function-shape=500`, `empty-object-control=200`, `count-function-control=200`; exit 1 được giữ, không mutation |
| `20261011T130227Z-139257` | `./lab.sh replay contract-schema-candidates` | Exit 1 có chủ đích; ghi bốn schema candidate, cleanup dữ liệu tạm PASS |
| `20261011T130338Z-139934` | `./lab.sh doctor` | PASS; license active, custom permission rules enabled, image digest đúng manifest |
| `20261011T130457Z-141013` | `./lab.sh test invariants` | 9 passed, 2 failed, 0 blocked; aggregate 500 và contract probe bốn candidate, harness giữ exit 1 |
| `20261011T131803Z-147694` | `./lab.sh doctor` | PASS; latest recheck, license active, permission rules enabled, digest đúng manifest |
| `20261011T134626Z-160826` | `./lab.sh test invariants` | 9 passed, 2 failed, 0 blocked dưới `bcbf219`; không có regression mới, exit 1 được giữ |

Run doctor mới nhất dưới HEAD `a153e99`:

| Run | Lệnh | Kết quả |
|---|---|---|
| `20261011T134705Z-161373` | `./lab.sh doctor` | PASS; Directus/DB/runner healthy, license `source=env/status=active`, `custom_permission_rules_enabled=true`, ba image digest đúng manifest, exit `0` |

### Campaign v2

Raw run `20261011T085034Z-76481` dùng schema hash
`433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`; seed
101/202/303 lần lượt có 59/65/51 case, 20/18/19 unique failure, 10/10
operation và restore PASS. Guided run `20261011T095117Z-89079` dùng overlay hash
`cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`; seed
101/202/303 lần lượt có 5770/5864/5894 case, 63/65/62 unique failure,
111/176/200 errored, stateful 1141/1183/1195 scenario, restore PASS. Cả hai
profile đều kết thúc `max_time`, runner exit 1; đây là kết quả chưa hoàn tất về
pass/fail acceptance, không được báo là campaign pass.

Reader v2 đã được kiểm chứng qua API thật: projection hợp lệ trả sáu published
fixture; projection yêu cầu `internal_notes` trả 403 không lộ dữ liệu; PATCH
Reader trả non-2xx và Editor read-back không đổi. Candidate aggregate vẫn được
phân loại `schema omission + product robustness candidate`, chưa xác nhận
product defect. Theo [`docs/g1-acceptance.md`](../docs/g1-acceptance.md), G1 đạt
baseline kỹ thuật với findings; raw/guided `failed_or_incomplete` và aggregate
HTTP 500 tiếp tục được giữ làm backlog triage.

### Triage replay v2 sau campaign

Tám replay đại diện được chạy tuần tự sau checkpoint trên. Chi tiết request,
phân loại và giới hạn stateful nằm tại
[`evidence/failure-triage-v2-2026-10-11.md`](failure-triage-v2-2026-10-11.md).

| Case | Run | Quan sát | Trạng thái |
|---|---|---|---|
| `Q8K5Nh` | `20261011T122512Z-124267` | `403` do query chạm collection không được cấp quyền | replay request, restore PASS |
| `VbURdO` | `20261011T122519Z-124858` | campaign `204`, direct replay `403` | mismatch, unresolved |
| `lwZKEo` | `20261011T122522Z-125422` | `TRACE` trả `404`, check kỳ vọng `405` | replay request, restore PASS |
| `3Ble8Q` | `20261011T122526Z-125993` | invalid query trả `400` | replay request, restore PASS |
| `vx21yF` | `20261011T122531Z-126570` | export trả `200 text/csv` ngoài schema JSON | replay request, restore PASS |
| `Z6K7ww` | `20261011T122536Z-127156` | POST trả object ngoài schema array | replay request, restore PASS |
| `CkqaOB` | `20261011T122539Z-127722` | final request stateful tái hiện `500` | candidate; chưa đủ full-chain replay |
| `pM4r4g` | `20261011T122542Z-128284` | campaign `200`, direct replay `403` | mismatch, unresolved |
| `kb5gjq` | `20261011T135006Z-162769` | POST article với `published_at=""` tái hiện `500`; source/expected/actual đều `500` | `reproduced_request_only`, restore PASS, exit `1`; SQLSTATE `22007` |
| `F8j8Gl` | `20261011T135713Z-165099` | GET article `export=json` trả `200` với array 12 item ngoài schema object | `reproduced_request_only`, restore PASS, exit `1`; schema/contract candidate |
| `UNKW3j` | `20261011T135951Z-166351` | GET article `export=xml` trả `200` với `text/xml` ngoài schema JSON | `reproduced_request_only`, restore PASS, exit `1`; export media-type candidate |
| `R0sH5o` | `20261011T140125Z-167402` | GET article `export=yaml` trả `200` với `text/yaml` ngoài schema JSON | `reproduced_request_only`, restore PASS, exit `1`; export media-type candidate |
| `DhqXrn` | `20261011T140307Z-168360` | Full chain `UqHibT → DhqXrn`; source `204`, replay `403` do field `id` forbidden | `full_transition_chain`, restore PASS, exit `1`; mismatch, chưa kết luận |
| `UTk4sa` | `20261011T140452Z-169384` | Parent `vfAiah` trả ID count khác transition mapping; PATCH target không gửi | `stateful_sequence_failed`, restore PASS, exit `1`; precondition/artifact limitation |
| `6IayFG` | `20261011T140814Z-170794` | GET article list positive với `offset` vượt safe-number; Directus trả `400 INVALID_QUERY` | `reproduced_request_only`, source/expected/actual `400`, restore PASS, exit `1`; schema semantic/generator-positive candidate |
| `6THjzP` | `20261011T141024Z-171863` | POST category negative với `name` integer; Directus trả `200` và ép thành string | `mismatch`, source/actual `200`, expected `400`, restore PASS, exit `1`; coercion/negative-oracle mismatch |

Trước commit `baaee4b`, harness chỉ gửi interaction cuối của stateful case.
Sau commit này, chain được dựng lại khi artifact có đủ parent case, interaction
và transition mapping; case thiếu parent vẫn giữ request-only/unresolved.

`kb5gjq` là replay bổ sung sau bảng tám case ban đầu. Request array được
Schemathesis đánh dấu positive nhưng truyền timestamp rỗng; log Directus ghi
PostgreSQL `invalid input syntax for type timestamp with time zone: ""`
(`22007`). Vì đây là giá trị sai ngữ nghĩa dù JSON type là string, finding được
giữ là schema-semantic/product robustness candidate, chưa kết luận product
defect.

Replay `F8j8Gl` bổ sung cho thấy biến thể `export=json` trả raw array nhưng
schema operation đang kiểm tra envelope object `data`; đây là contract/schema
candidate cần giữ riêng với timestamp candidate, không phải 5xx hoặc product
defect đã xác nhận.

Replay `UNKW3j` bổ sung xác nhận biến thể `export=xml` cũng trả media type
ngoài schema JSON; gộp với `vx21yF` thành export contract candidate, không đếm
riêng thành defect.

Replay `R0sH5o` xác nhận biến thể `export=yaml` có cùng hành vi; ba media type
CSV/XML/YAML được giữ trong cùng nhóm export contract candidate.

Replay `DhqXrn` là ca negative khác với request-only: parent transition được
replay đầy đủ nhưng kết quả hiện tại là `403` thay source `204`. Restore PASS và
không có thay đổi dữ liệu tồn tại; giữ mismatch, không đổi thành PASS.

Replay `UTk4sa` không vượt qua setup parent nên target không được gửi; đây là
giới hạn tái dựng stateful, không phải bằng chứng request bị chấp nhận hoặc bị
từ chối trên baseline hiện tại.

Replay `6IayFG` gửi request positive nhưng `offset` là số vượt giới hạn safe
number. Directus trả `400 INVALID_QUERY`, restore PASS và report giữ exit `1`;
đây là bằng chứng query semantic chưa được mô tả đủ trong schema/generator,
không phải product defect đã xác nhận.

Replay `6THjzP` gửi negative mutation đổi `name` thành integer. Directus trả
`200` và response canonicalize giá trị thành string; restore PASS nhưng report
giữ mismatch với negative expected `400`. Đây là semantic coercion/negative
oracle mismatch cần quyết định theo contract, không phải product defect đã xác
nhận.

Commit `64e88f9` đã làm rõ phạm vi này trong report replay. Kiểm chứng sau sửa:

| Run | Lệnh | Kết quả |
|---|---|---|
| `20261011T123728Z-131951` | `./lab.sh replay CkqaOB` | final request `500`, `reproduced_request_only`, `sequence_replayed=false`, restore PASS, exit `1` |
| `20261011T123735Z-132524` | `./lab.sh replay Q8K5Nh` | `reproduced`, `sequence_replayed=true`, restore PASS, exit `0` |

Đây là thay đổi trung thực hóa trạng thái replay, không phải nới assertion hoặc
xóa failure.

### Replay parent chain sau `baaee4b`

| Run | Lệnh | Kết quả |
|---|---|---|
| `20261011T131321Z-144935` | `./lab.sh replay pM4r4g` | `mvlcIV → pM4r4g`, `sequence_replayed=true`, parent `200`, final `200` trái expected `400`, restore PASS, exit `1` |
| `20261011T131350Z-145631` | `./lab.sh replay CkqaOB` | Không có parent chain trong event, `reproduced_request_only`, final `500`, restore PASS, exit `1` |
| `20261011T131702Z-146905` | `./lab.sh replay Q8K5Nh` | Non-stateful `reproduced`, restore PASS, exit `0` sau chain hardening |

### Replay status oracle sau commit `a713481`

Audit một case positive cho thấy logic cũ có thể báo `reproduced` khi case nguồn
không có check failure nhưng replay trả status khác. Commit `a713481` bổ sung
fallback expected từ interaction nguồn và ghi `source_status`; không đổi artifact
cũ hoặc bỏ failure.

| Run | Lệnh | Kết quả thực tế |
|---|---|---|
| `20261011T132137Z-149741` | `./lab.sh replay tFjhQT` | Full chain `D3mEEJ → tFjhQT`; source/expected `200`, actual `403`, `mismatch`, restore PASS, exit `1` |
| `20261011T132145Z-150356` | `./lab.sh replay Q8K5Nh` | Source/expected/actual `403`, `reproduced`, restore PASS, exit `0` |

Metadata hai run ghi harness SHA `139b3176...` và working tree dirty vì patch
đang được kiểm thử trước commit `a713481`; code thay đổi tương ứng đã được
commit sau đó. Run `20261011T131957Z-148748` trước sửa được giữ nhưng không dùng
làm bằng chứng PASS cuối cho `tFjhQT`.

Recheck cuối dưới HEAD `916152e`:

| Run | Lệnh | Kết quả thực tế |
|---|---|---|
| `20261011T132550Z-151921` | `./lab.sh replay tFjhQT` | `source_status=200`, `expected_status=200`, actual `403`, full-chain `D3mEEJ → tFjhQT`, `mismatch`, restore PASS, exit `1` |
| `20261011T132604Z-152556` | `./lab.sh replay Q8K5Nh` | `source_status=403`, `expected_status=403`, actual `403`, `reproduced`, restore PASS, exit `0` |

Hai run đều ghi `harness_sha=916152ec983559303ec6c69dec07456ba5c5f25f`; working
tree dirty do bốn file untracked có trước, không do thay đổi tracked chưa commit.

### Stateful chain recheck dưới HEAD `3960f55`

| Run | Lệnh | Kết quả thực tế |
|---|---|---|
| `20261011T133817Z-157078` | `./lab.sh replay aZmz3k` | Full chain `C7nkph → aZmz3k`, source/expected/actual `200`, `sequence_replayed=true`, restore PASS, exit `0` |
| `20261011T133626Z-155874` | `./lab.sh replay Ag8Csb` | Parent 200 nhưng source pool 100 ID khác snapshot 3 ID; `stateful_sequence_failed`, target không gửi, restore PASS, exit `1` |

Đây là hai trạng thái khác nhau: `aZmz3k` chứng minh full-chain replay thành
công; `Ag8Csb` chứng minh harness dừng an toàn khi precondition/stateful artifact
không tái lập được.
