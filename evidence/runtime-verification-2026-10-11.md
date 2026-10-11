# Bằng chứng triển khai và xác minh runtime — 2026-10-11

Tài liệu này chỉ ghi kết quả đã quan sát trên máy hiện tại. Không dùng nó để khẳng định G1, kiểm tra chéo hoặc campaign đầy đủ đã hoàn thành.

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

Sau pilot recheck, cả `database`, `directus` và `runner` đều ở trạng thái `running/healthy`; image hiển thị đúng digest đã pin. Hai campaign ngắn đều dừng `max_time`, không đại diện cho campaign đủ ngân sách.

Các run metadata ghi `harness_sha` riêng. Tại thời điểm các run đầu, working tree còn dirty do thay đổi tích hợp có sẵn; đây là provenance thực tế, không được coi là clean release.

## Schema snapshot

Schema export `20261011T035010Z-8515`:

- Admin: 14 operation, hash `993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e`.
- Editor: 14 operation, hash `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26`.
- Reader: 2 operation, hash `20fbfe9a517710ac73d05622f4b158bab4ccbcd96da51ec61363268ed92683cb`.
- Anonymous: 0 operation, hash `2070c25c68193a4a42501935974bb3045697aceb1fe072bb3461f43c0a0342b3`.

## Triage sơ bộ

- Môi trường: Compose stack chạy và fixture được restore sau pilot.
- Policy/schema blocker: license không cho custom permission rules; không thể chứng minh Reader published-only/field restriction.
- Schema/contract candidate: pilot có các check failure như response status ngoài schema và POST response shape; chưa kết luận product defect vì cần replay request cụ thể và đối chiếu contract.
- Chưa có kết luận defect độc lập, chưa có kiểm tra chéo máy thứ hai.

Chưa chạy campaign đầy đủ ba seed `101,202,303` ở ngân sách 100 example/operation và 20 phút/profile/seed; không báo cáo coverage đầy đủ như đã đạt.
