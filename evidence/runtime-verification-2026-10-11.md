# Bằng chứng triển khai và xác minh runtime — 2026-10-11

Tài liệu này chỉ ghi kết quả đã quan sát trên máy hiện tại. Không dùng nó để khẳng định G1 hoặc kiểm tra chéo trên máy độc lập; campaign đầy đủ đã được chạy và giữ nguyên trạng thái kết thúc thực tế bên dưới.

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
- Chưa có kết luận defect độc lập, chưa có kiểm tra chéo máy thứ hai.

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
