# Nhật ký triển khai lab và hướng dẫn đọc code

Ngày cập nhật: 2026-10-11

Tài liệu này ghi lại phần nền tảng và bản triển khai tạm thời để người tiếp nhận có thể đọc code theo luồng, hiểu vì sao các tệp tồn tại và phân biệt quan sát đã chạy với phần còn bị chặn. Bản ghi này không thay thế [`AGENTS.md`](../AGENTS.md), hai kế hoạch trong `mnhy/` hoặc bằng chứng chạy riêng.

## Mốc Git

- Nhánh hiện tại tại lần cập nhật: `feat/g1-shared-interface`.
- HEAD hiện tại tại lần cập nhật: `a713481 fix: validate replay status for successful cases`.
- HEAD nền tảng trước các thay đổi G1: `a2693f6 Merge branch 'feat/g0-lab-foundation'`.
- Remote dự kiến: `origin` trỏ tới repository đồ án `minnhi09/Directus-Testing`.
- Dòng `/AGENTS.md` trong `.gitignore` có từ thay đổi người dùng trước đó và được giữ lại ngoài commit nền tảng; không xóa để làm worktree sạch giả tạo.
- `config/lab.env` là file cục bộ bị ignore. Credential trong đó chỉ dùng cho lab hiện tại, không được đưa vào commit hoặc report.

## Bản đồ tệp

| Tệp | Vai trò khi đọc code |
|---|---|
| [`lab.sh`](../lab.sh) | Điểm vào duy nhất của lab; kiểm tra điều kiện, tạo metadata/run log, gọi Compose hoặc shared component và giữ mã lỗi thật |
| [`scripts/lab-components.sh`](../scripts/lab-components.sh) | Seed schema/fixture/actor, smoke, schema export, sáu scenario, campaign raw/guided và replay; credential chỉ truyền qua môi trường tiến trình |
| [`compose.yaml`](../compose.yaml) | Khai báo ba service `database`, `directus` và `runner`, network `r06-k05_network`, volume `r06-k05_db_data`, port loopback và healthcheck |
| [`config/lab.env.example`](../config/lab.env.example) | Danh sách biến cấu hình cần sao chép thành `config/lab.env`; chứa digest image và placeholder, không chứa credential thật |
| [`manifest/baseline.yaml`](../manifest/baseline.yaml) | Baseline phiên bản, source commit, digest, runtime và trạng thái kiểm chứng |
| [`docs/g0-quyet-dinh-ky-thuat.md`](g0-quyet-dinh-ky-thuat.md) | Quyết định G0, giao diện lệnh, sở hữu phần việc và giới hạn nghiệm thu |
| [`docs/architecture.md`](architecture.md) | Sơ đồ và mô tả request đi qua Directus đến PostgreSQL/OpenAPI |
| [`docs/traceability.md`](traceability.md) | Truy vết yêu cầu A–H và backlog theo chủ sở hữu/phụ thuộc |
| [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md) | Các lệnh và kết quả thật của lần dựng lab đầu tiên |

## Luồng đọc và luồng chạy

### 1. Từ lệnh CLI vào Compose

Đọc `main()` ở cuối `lab.sh` trước. Lệnh được phân nhánh thành:

- `doctor`: kiểm tra Docker, Compose, file cấu hình, placeholder, digest image, container của đúng project, URL và liveness/auth health.
- `up`: yêu cầu `config/lab.env`, render Compose, gọi `docker compose up -d`, sau đó đợi trạng thái health của service `directus` tối đa 30 lần, mỗi lần 2 giây.
- `down`: gọi `docker compose down` và không dùng `--volumes`, nên volume dữ liệu được giữ lại.
- `seed`, `smoke`, `export-schema`, `test scenarios`, `test invariants`, `test raw`, `test guided`, `replay` và `reset` gọi shared component. Các run luôn lưu report và trả mã lỗi thật khi precondition, policy hoặc check chưa đạt; artifact không bị xóa khi test thất bại.

Hàm `compose()` cố định `--project-name r06-k05`, `compose.yaml` và `config/lab.env`. Vì vậy không được chạy một Compose project khác rồi suy luận đó là lab này.

### 2. Từ Compose vào container

`compose.yaml` có hai service:

1. `database` dùng PostgreSQL 16, chỉ nằm trong network Compose, có volume `r06-k05_db_data` và healthcheck `pg_isready`.
2. `directus` phụ thuộc database healthy, bind `127.0.0.1:8055:8055`, nhận thông tin DB/bootstrap từ env và tắt cache, telemetry, rate limiter cho baseline.

Network được đặt tên cố định `r06-k05_network` để runner Schemathesis sau này có thể dùng hostname `directus:8055`. DB không publish port host, nên các dịch vụ PostgreSQL khác trên máy không dùng chung cổng hoặc volume.

Image dùng dạng `tag@sha256:digest`. Digest trong `config/lab.env.example` phải khớp [`manifest/baseline.yaml`](../manifest/baseline.yaml); không đổi sang `latest` hoặc tự nâng phiên bản khi gặp lỗi.

### 3. Liveness và health của Directus

Trong source Directus `v12.5.0`, `/server/health` yêu cầu accountability. Vì vậy healthcheck Docker dùng `/server/ping` để kiểm tra process/API liveness công khai. `lab.sh doctor` cũng kiểm tra `/server/ping` và xác nhận container thuộc project `r06-k05` đang chạy.

Health nghiệp vụ của Directus được kiểm tra riêng bằng admin token qua `/server/health`. Lần chạy G0 đã quan sát:

- `/server/ping`: HTTP `200` không xác thực.
- `POST /server/setup`: HTTP `204` để hoàn tất admin bootstrap sau lần khởi động đầu bị lỗi email.
- `POST /auth/login`: HTTP `200`; token không được ghi vào file.
- `/server/health` với admin accountability: HTTP `200`, `status=ok`.

Không đổi healthcheck sang `/server/health` không xác thực vì sẽ làm container giữ trạng thái `starting` dù Directus đã phục vụ request.

### 4. Cấu hình và bảo vệ secret

`config/lab.env.example` chỉ là mẫu. Người chạy sao chép thành `config/lab.env`, thay các giá trị `REPLACE_*`, đặt quyền `600`, rồi chạy `doctor`. `lab.sh` đọc key bằng `awk` để kiểm tra sự hiện diện mà không in giá trị secret.

Không dùng `source config/lab.env` trong harness, không nhúng token vào code và không lưu response login vào artefact. Khi viết reproducer hoặc report, credential phải đi qua biến môi trường và body/header phải được làm sạch.

## Những gì đã xác minh

Ngày 2026-10-09 trên máy hiện tại:

- Docker `29.8.1`, Compose `v5.5.1`.
- Directus `12.5.0` từ tag `v12.5.0`, source commit `4f77933bf9551cac6b289576078783e189b8f4e3`.
- Ba image mục tiêu đã pull theo digest; local image inspect khớp manifest.
- `./lab.sh doctor` exit `0`.
- `./lab.sh up` exit `0`; database và Directus healthy.
- Admin bootstrap/login và authenticated health thành công.

Bằng chứng chi tiết và giới hạn nằm trong [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md). Kết quả lịch sử này chỉ chứng minh một máy và một baseline local; chưa chứng minh tái lập trên máy thứ hai. Đây không còn là gate G1 sau điều chỉnh tiêu chí.

## Bản triển khai tạm thời — 2026-10-10

Component ở [`scripts/lab-components.sh`](../scripts/lab-components.sh) đã thực hiện các phần độc lập cần cho bản demo:

- Kiểm tra/tạo hai collection, field validation và quan hệ `qa_articles.category` với `SET NULL`; seed lặp lại theo tên fixture, không hard-code ID và ghi [`runtime/fixture-ids.json`](../runtime/fixture-ids.json).
- Tạo role/policy/actor editor và reader. Editor có CRUD hai collection. Reader category read tạo được; policy article có filter published và field giới hạn bị Directus từ chối vì entitlement `custom_permission_rules_enabled=false`.
- Smoke kiểm tra score/status invalid và nullification quan hệ; không gửi request negative cho Reader nếu operation đã bị lọc khỏi schema.
- Export raw OpenAPI riêng cho bốn actor và giữ hash bất biến. Editor có 14 operation do Directus xuất cả bulk operation; pilot lọc đúng 5 operation `qa_articles` bằng file overlay tạm, ghi lý do và không sửa raw.
- Sáu scenario ghi rõ `passed`, `failed` hoặc `blocked`. S1–S3 đạt; S4–S6 blocked do Reader schema chỉ có hai operation category.
- Campaign Schemathesis chính chạy tuần tự một worker, rate mục tiêu 5 request/giây,
  timeout request 10 giây, tối đa 100 example/operation, ngân sách 1.200 giây/profile/seed
  với seed `101,202,303`; pilot có thể override bằng biến môi trường. Raw giữ schema
  operation gốc trong allowlist 10 operation; guided dùng overlay riêng với fixture
  ID/example và stateful phase. Snapshot/restore fixture được chạy giữa các seed để
  campaign không làm bẩn trạng thái baseline.
- Replay Schemathesis case dùng artifact event NDJSON, allowlist hai collection,
  credential Editor hiện tại và snapshot/restore; body binary được truyền qua file
  `--data-binary`, không qua command substitution.

Chi tiết run ID, status và giới hạn nằm trong [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md). Đây là checkpoint lịch sử trước khi license Reader hoạt động; không dùng các blocker lịch sử đó để phủ nhận checkpoint v2 hiện tại.

## Bổ sung giao diện dùng chung — 2026-10-10

Phần Lành đã bổ sung vào `lab.sh` và cấu hình mẫu:

- URL host/runner có khóa cấu hình riêng với giá trị mặc định của baseline.
- Credential API của `editor` và `reader` có tên khóa thống nhất, vẫn nằm ngoài Git.
- Mỗi lệnh hợp lệ tạo `artifacts/runs/<run_id>/metadata.json` và `run.log`; metadata ghi SHA harness, trạng thái working tree, baseline image, actor và các trường fixture/schema/seed/budget khi caller cung cấp.
- `runtime/fixture-ids.json` được cố định làm điểm bàn giao ID fixture giữa Trâm và Nhân.
- Docker preflight dừng sớm với thông báo rõ ràng khi CLI/daemon/Compose không khả dụng; không coi lần chạy lỗi là G1.

Kiểm tra đã thực hiện: `bash -n lab.sh scripts/lab-components.sh`, ShellCheck và `git diff --check` đạt. Lần `doctor` đầu giữ mã thoát `1` vì Docker Desktop đang dừng; sau khi khởi động Docker Desktop bằng CLI chính thức, `./lab.sh doctor` và `./lab.sh up` đều đạt, hai container ở trạng thái healthy; auth check mới của `doctor` cũng nhận HTTP `200` từ `/server/health` bằng admin credential mà không ghi token. Các run seed/smoke/schema/scenario/pilot mới nhất được ghi ở [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md).

## Cách tiếp nhận phần việc tiếp theo

1. Chạy `./lab.sh doctor` và xác nhận đúng project/URL trước khi gọi API.
2. Đọc `docs/g0-quyet-dinh-ky-thuat.md` và `docs/traceability.md` để lấy interface, chủ sở hữu và phụ thuộc.
3. Nếu có license Directus phù hợp, cấu hình entitlement `custom_permission_rules_enabled` cục bộ, không ghi secret vào repo; sau đó chạy `./lab.sh seed`, kiểm tra schema snapshot mới và chạy lại smoke/scenarios.
4. Không tự ghi đè schema raw cũ: nếu policy làm schema actor thay đổi, chọn fixture version/run directory mới sau khi xác nhận quyết định baseline.
5. Triage các failure Schemathesis bằng report raw và reproducer có precondition; không sửa expected chỉ để pilot pass.
6. Replay các candidate đã ghi trong `docs/campaign-triage-2026-10-11.md`, đặc biệt
   `AmXHZz`, `jShXuk` và `VllBgh`; không gộp check failure thành defect nếu chưa
   đối chiếu contract/precondition.
7. Lành đối chiếu run/artifact với [`docs/g1-acceptance.md`](g1-acceptance.md),
   cập nhật evidence/manifest và giữ nguyên failure chưa đóng. License Reader
   đã được bật ở checkpoint v2; không yêu cầu kiểm tra máy khác hoặc review chéo
   để kết luận G1.

## Checkpoint local sau khi license hoạt động — 2026-10-11

Phần trên giữ nguyên lịch sử G0 trước license. Checkpoint thực tế mới dùng
fixture/schema version `r06-k05-v2`; snapshot `r06-k05-v1` không bị overwrite.

- `20261011T084813Z-71356`: reset đúng volume/project `r06-k05`, sau đó
  `20261011T084821Z-71845` dựng lại stack healthy.
- `20261011T084845Z-72361`: seed v2 PASS; 3 category, 12 article, 6 draft,
  6 published, actor/policy PASS.
- `20261011T085023Z-75556`: smoke PASS; `20261011T085027Z-75998`: export
  schema PASS, Reader 6 operation.
- `20261011T105231Z-104612`: S1–S6 PASS; `20261011T105236Z-105096`: 9
  invariant PASS, 1 regression failure aggregate HTTP 500.
- Raw `20261011T085034Z-76481` và guided `20261011T095117Z-89079` chạy đủ
  seed `101,202,303`, 10/10 operation và restore PASS; runner exit 1 do
  `max_time`/check failure, không báo campaign pass.
- `20261011T105242Z-105524`: replay aggregate candidate tái hiện HTTP 500.
- `20261011T134519Z-160153`: replay aggregate mở rộng dưới commit `bcbf219`
  ghi unknown shape `500`,
  control `{}` và `{"count":["id"]}` trả `200`; exit `1` được giữ nguyên.

Doctor cuối `20261011T105225Z-104013` báo license `source=env`, `status=active`,
`custom_permission_rules_enabled=true`. Reader visibility/write đã được kiểm tra
qua API thật. G1 đạt baseline kỹ thuật với findings; aggregate HTTP 500 và các
campaign `failed_or_incomplete` tiếp tục là backlog triage, không bị đổi trạng
thái để làm đẹp.

## Recheck sau hardening và contract probe — 2026-10-11

- Doctor recheck `20261011T130338Z-139934` và latest `20261011T131803Z-147694`
  PASS; license active, entitlement
  `custom_permission_rules_enabled=true`, digest image khớp manifest.
- Invariant recheck `20261011T130457Z-141013` có `9 passed`, `2 failed`, `0
  blocked`, exit `1`: aggregate HTTP 500 và `contract-schema-candidates` ghi
  bốn schema candidate. Replay aggregate mở rộng `20261011T134519Z-160153`
  xác nhận unknown shape `500`, hai control `200`; kết quả này bổ sung
  evidence, không thay thế run lịch sử `20261011T105236Z-105096`.
- Full invariant recheck `20261011T134626Z-160826` dưới `bcbf219` vẫn có
  `9 passed`, `2 failed`, `0 blocked`, exit `1`; không có regression mới ngoài
  aggregate candidate và bốn contract candidate.
- Contract probe commit `7018107` và tài liệu commit `01e14d1` được ghi trong
  README, G1 acceptance, replay/test matrix, runtime evidence và manifest.
- Stateful replay từ commit `baaee4b` dựng full chain khi artifact đủ parent;
  `pM4r4g` đã được kiểm chứng, còn case thiếu parent vẫn gọi
  `reproduced_request_only`; không tự đổi mismatch thành full-chain PASS.

## Sửa oracle status của replay — 2026-10-11

- Audit `tFjhQT` phát hiện lỗi harness: case nguồn không có check failure nên
  `expected_status` rỗng, replay `403` vẫn bị ghi `reproduced` dù interaction
  nguồn là `200`.
- Commit `a713481` sửa fallback expected status từ response nguồn khi mọi check
  nguồn PASS và ghi thêm `source_status` vào reproducer. Artifact lịch sử trước
  sửa được giữ nguyên, không chỉnh sửa để làm đẹp kết quả.
- Run `20261011T132137Z-149741`: `tFjhQT` full chain `D3mEEJ → tFjhQT`,
  source/expected `200`, actual `403`, restore PASS, `mismatch`, exit `1`.
- Run `20261011T132145Z-150356`: `Q8K5Nh` source/expected/actual `403`,
  `reproduced`, restore PASS, exit `0`.
- Kiểm tra sau commit gồm `bash -n`, ShellCheck, diff check và hai replay; không
  chạy lại campaign dài vì thay đổi chỉ ảnh hưởng replay oracle.
- Sau commit tài liệu `916152e`, đã recheck dưới HEAD hiện hành:
  `20261011T132550Z-151921` giữ `tFjhQT` mismatch `200→403`, còn
  `20261011T132604Z-152556` giữ `Q8K5Nh` reproduced `403→403`; cả hai restore
  PASS và metadata ghi harness SHA `916152e` đầy đủ.

## Doctor cuối dưới HEAD `d0d199f`

- Run `20261011T132716Z-153452`: `./lab.sh doctor` PASS, Directus/DB/runner
  healthy, license active với `custom_permission_rules_enabled=true`, ba image
  digest đúng manifest và exit `0`.

## Doctor chốt sau aggregate probe dưới HEAD `a153e99`

- Run `20261011T134705Z-161373`: `./lab.sh doctor` PASS; Compose, ba image
  digest, fixture map, authenticated health và license
  `source=env/status=active`, `custom_permission_rules_enabled=true` đều đạt.
- Metadata ghi harness SHA đầy đủ `a153e9920febc9801b3556482b15bc16cd5b3ad6`;
  working tree dirty chỉ do file untracked có trước. Không thay đổi baseline,
  credential hoặc kết quả failure.

## Xác minh full-chain stateful bổ sung

- Run `20261011T133817Z-157078` dưới HEAD `3960f55`: replay `aZmz3k` đủ chain
  `C7nkph → aZmz3k`, parent/target HTTP 200, source/expected/actual 200, restore
  PASS, exit `0`.
- Run `20261011T133626Z-155874`: replay `Ag8Csb` bị dừng ở setup vì parent source
  có 100 ID còn snapshot hiện tại có 3 category và không có target `298`; report
  `stateful_sequence_failed`, target không gửi, restore PASS, exit `1`.
- Hai kết quả được phân biệt trong README, replay guide, campaign/failure/runtime
  evidence, G1, final handoff và manifest; không coi setup failure là product bug.

## Triage guided ServerError timestamp — 2026-10-11

- Chạy `./lab.sh replay kb5gjq` ở run `20261011T135006Z-162769` dưới harness
  `a8c4a510c03fbd7325f952e786f43103aab2c817`.
- Case guided stateful `POST /items/qa_articles` có body array với
  `published_at=""`; source/expected/actual đều HTTP `500`, report ghi
  `reproduced_request_only`, `sequence_replayed=false`, restore PASS và exit
  `1`. Không có parent transition trong artifact nên không gọi là full-chain
  reproduction.
- Log Directus ghi `DatabaseError`, PostgreSQL SQLSTATE `22007` và thông báo
  timestamp rỗng không hợp lệ. Đây là bằng chứng root cause kỹ thuật cho
  request đã tái hiện, nhưng vẫn là schema-semantic/product robustness
  candidate vì generator coi chuỗi rỗng là dữ liệu positive; chưa kết luận
  product defect.
- Đối chiếu snapshot `runtime/schemas/r06-k05-v2/editor.json` và source Directus
  pin `4f77933bf9551cac6b289576078783e189b8f4e3`: `published_at` là string
  nullable với custom `format: timestamp`, không có `pattern`/`minLength`; POST
  cho phép object hoặc array. Evidence này củng cố phân loại schema semantic gap,
  nhưng chưa đủ để kết luận lỗi upstream.
- Đã cập nhật failure triage, replay guide, runtime/final evidence, G1,
  traceability, README và manifest. Không sửa expected, không xóa artifact
  thất bại và không chạy lại campaign dài.

## Triage export JSON response shape — 2026-10-11

- Run `20261011T135713Z-165099`: `./lab.sh replay F8j8Gl` dưới harness
  `778ef20561843be0841d47779a776f88b2c56b2d`; source/expected/actual đều
  HTTP `200`, restore PASS, exit `1`, `reproduced_request_only`.
- Request `GET /items/qa_articles?backlink=true&export=json` trả raw array 12
  item, trong khi response schema của operation yêu cầu object có `data`.
  Đây là schema/contract candidate về alternate export shape; không có 5xx và
  không kết luận product defect.
- Artifact không có parent transition nên giữ đúng phạm vi request-only; không
  giả lập full-chain và không gộp case này thành defect độc lập với nhóm
  response-shape đã triage.

## Triage export XML media type — 2026-10-11

- Run `20261011T135951Z-166351`: `./lab.sh replay UNKW3j` dưới harness
  `a0e8996456fd56f37c3558d5e140db735bee9c3f`; source/expected/actual đều
  HTTP `200`, restore PASS, exit `1`, `reproduced_request_only`.
- Request `GET /items/qa_articles?export=xml&search=Directus` trả
  `text/xml; charset=utf-8`, trong khi operation schema chỉ khai báo
  `application/json`. Đây là cùng nhóm export media-type contract với
  `vx21yF` (`csv`), không phải product defect độc lập.
- Không có parent transition trong artifact; giữ request-only và không đổi
  expected/check để làm campaign xanh.

## Triage export YAML media type — 2026-10-11

- Run `20261011T140125Z-167402`: `./lab.sh replay R0sH5o` dưới harness
  `4160c925ed4fcd525eaa1319bbaf7c182278f34b`; source/expected/actual đều
  HTTP `200`, restore PASS, exit `1`, `reproduced_request_only`.
- Request `GET /items/qa_articles?fields=*.*&limit=59189288&export=yaml&page=2`
  trả `text/yaml; charset=utf-8`, trong khi schema chỉ khai báo
  `application/json`. Đây là cùng nhóm export media-type contract với CSV/XML,
  không phải product defect độc lập.
- Giữ nguyên exit `1`, không sửa expected/check và không gộp các replay
  request-only thành full-chain evidence.

## Triage accepted-negative stateful mismatch — 2026-10-11

- Run `20261011T140307Z-168360`: `./lab.sh replay DhqXrn` dưới harness
  `231842ac827f29822af9b8f2eb3095ec5e1943fa`; parent chain `UqHibT → DhqXrn`
  được replay đầy đủ, restore PASS, exit `1`.
- Campaign source ghi `204` cho negative request; replay hiện tại trả `403` với
  lỗi Directus không cho cập nhật field `id`. Vì actual không tái hiện việc
  accepted negative và replay giữ expected failure, trạng thái là mismatch
  precondition/policy/negative oracle, không phải product defect.
- Không có mutation tồn tại sau restore; không đổi expected status, không nới
  assertion và không coi full-chain mismatch là PASS.

## Triage accepted-negative stateful setup failure — 2026-10-11

- Run `20261011T140452Z-169384`: `./lab.sh replay UTk4sa` dưới harness
  `6bfe3ad1f7ef81a113e3488c90811ce683d8ca52`.
- Parent `vfAiah` được gửi và trả `200`, nhưng số ID không khớp transition
  mapping; target `PATCH /items/qa_articles/117` không được gửi. Report ghi
  `stateful_sequence_failed`, `actual_status=not-sent`, restore PASS, exit `1`.
- Đây là giới hạn artifact/precondition của stateful replay. Không dùng nó để
  kết luận API accepted/rejected negative data, không đổi expected và không
  che failure.

## Triage positive query safe-number — 2026-10-11

- Run `20261011T140814Z-170794`: `./lab.sh replay 6IayFG` dưới harness
  `8bfefad50d5fc205d51d2387e595f0a732b04c20`.
- Request `GET /items/qa_articles` có `offset` vượt giới hạn safe number;
  source/expected/actual đều `400`, response code `INVALID_QUERY`, report ghi
  `reproduced_request_only`, restore PASS và exit `1`.
- Đây là schema semantic/generator-positive candidate và response-map gap;
  không phải product defect. Giữ nguyên failure và expected, không thêm skip.

## Triage negative type coercion — 2026-10-11

- Run `20261011T141024Z-171863`: `./lab.sh replay 6THjzP` dưới harness
  `9d71e9c351fb2000c8bb23d358ab000d84b1f7b0`.
- Negative mutation gửi `POST /items/qa_categories` với `name` integer. Directus
  trả `200`, response lưu `name` thành string; source/actual `200`, expected
  negative `400`, restore PASS và exit `1`.
- Giữ `mismatch` như bằng chứng semantic coercion/negative-oracle mismatch;
  chưa kết luận product defect, không đổi expected và không che failure.
