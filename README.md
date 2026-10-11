# DAMH — R06 Directus + K05 Schemathesis

Đây là harness kiểm thử REST API Directus theo schema, tập trung vào CRUD, query, quyền và invariant nghiệp vụ của hai collection `qa_categories` và `qa_articles`.

Checkpoint local hiện tại đã xác minh license thật trên Directus `12.5.0`: `/license` báo `source=env`, `status=active` và `custom_permission_rules_enabled=true`. Baseline đang dùng fixture/schema version `r06-k05-v2`; snapshot `r06-k05-v1` trước license được giữ bất biến để truy vết. Seed, smoke, schema export, sáu scenario và Reader invariants đã chạy trên máy hiện tại. Raw/guided đều chạy đủ ba seed, 10/10 operation và restore PASS, nhưng runner giữ exit 1 do check failures/max-time; không coi đây là campaign pass. Candidate aggregate HTTP 500 đã replay lại được; recheck `20261011T134519Z-160153` dưới harness `bcbf219` ghi `unknown-function-shape=500`, còn hai control `aggregate={}` và `aggregate={"count":["id"]}` đều `200`, vẫn phân loại product robustness candidate + schema omission, chưa xác nhận defect. Audit replay mới phát hiện và đã sửa một lỗi harness khiến case không có check failure bị coi là reproduced dù status khác; commit `a713481` bổ sung expected status từ response nguồn và ghi `source_status`. Theo tiêu chí G1 đã điều chỉnh, baseline kỹ thuật được ghi nhận **đạt có phát hiện chưa đóng**; không yêu cầu review chéo hoặc xác minh trên máy thứ hai.

## Chuẩn bị lab

Yêu cầu chính là Docker Engine/Compose. Không cần cài Node hoặc Python trên host để chạy stack dự kiến.

```bash
cp config/lab.env.example config/lab.env
chmod 600 config/lab.env
```

Mở `config/lab.env` và thay các giá trị `REPLACE_*` bằng giá trị cục bộ. File này bị Git ignore. Không ghi credential thật vào source, log hoặc report. Bốn khóa `EDITOR_*` và `READER_*` là credential cho API actor; chúng được seed/policy dùng sau khi admin bootstrap, không dùng quyền Studio. Máy hiện tại đã có credential cục bộ cho hai actor; giá trị không được ghi vào Git hay artefact. Nếu có license Directus hợp lệ, đặt khóa vào `LICENSE_KEY` trong `config/lab.env` (không commit), rồi chạy `./lab.sh up` để container nhận khóa và kiểm tra lại endpoint `/license`.

`API_URL` mặc định là `http://127.0.0.1:8055`; `RUNNER_API_URL` là `http://directus:8055` trong network Compose. Chỉ đổi URL khi có quyết định baseline mới; API host vẫn phải bind loopback.

Lab đặt `ACCESS_TOKEN_TTL=2h` để một campaign tuần tự ba seed không bị token mặc định 15 phút hết hạn giữa lúc Schemathesis chạy. Đây là cấu hình thử nghiệm được ghi trong manifest, không phải thay đổi phiên bản Directus.

Các image đã được ghi bằng tag và digest trong [`manifest/baseline.yaml`](manifest/baseline.yaml). Pull rõ ràng trước khi chạy:

```bash
docker compose --env-file config/lab.env --project-name r06-k05 -f compose.yaml pull
```

Image Schemathesis được dùng sau khi exporter và schema đã sẵn sàng; kiểm tra image runner bằng digest trong manifest trước campaign.

## Giao diện

```bash
./lab.sh doctor
./lab.sh up
./lab.sh down
./lab.sh seed
./lab.sh smoke
./lab.sh export-schema
./lab.sh test schema-smoke
./lab.sh test scenarios
./lab.sh test invariants
./lab.sh test raw
./lab.sh test guided
./lab.sh replay editor-crud
./lab.sh replay positive-operations
./lab.sh reset
```

`./lab.sh test smoke` là alias tương đương `./lab.sh smoke`. `raw` và `guided` mặc định chạy ba seed `101,202,303`; dùng biến môi trường để pilot ngắn, ví dụ `LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test raw`. Không fuzz URL ngoài lab.

Mỗi lệnh được nhận diện tạo một thư mục `artifacts/runs/<run_id>/` bị Git ignore, gồm `metadata.json` và `run.log`. Metadata ghi command, mã thoát, SHA harness, trạng thái working tree, baseline image, actor nếu được truyền qua `LAB_ACTOR` (`admin`, `editor`, `reader`, `anonymous` hoặc `unspecified`), fixture/schema/seed/budget nếu có và đường dẫn ID map. `test schema-smoke` luôn dùng actor `editor` và tự ghi actor này; truyền actor khác là lỗi để tránh provenance sai. Token và password không được ghi vào đó. Có thể đặt `LAB_RUN_ID` để chọn ID ổn định cho một lệnh; ID phải chưa tồn tại, chỉ gồm chữ, số, `.`, `-`, `_` và tối đa 64 ký tự.

`runtime/fixture-ids.json` là vị trí dùng chung để seed bàn giao `fixture_version` và ánh xạ tên fixture → ID tự sinh. Hình dạng tối thiểu là `{"schema":1,"fixture_version":"...","fixtures":{"qa_categories":{"name":1},"qa_articles":{"name":1}}}`; ID phải là số nguyên dương. Lệnh đọc schema/test phải dùng đường dẫn này thay vì hard-code ID.

Trạng thái lệnh trên máy hiện tại:

- `doctor`: đạt; Compose, digest, URL loopback, admin health và entitlement `/license` rút gọn đều được kiểm tra mà không ghi license/token; run mới nhất `20261011T142245Z-177107` dưới HEAD `9d26617` (các recheck trước vẫn được giữ trong evidence).
- `up`: đạt; database và Directus healthy.
- `seed`: tạo/kiểm tra schema, seed 3 category + 12 article, ghi ID map và tạo actor/policy; baseline v2 PASS ở run `20261011T084845Z-72361`.
- `smoke`: validation field, quan hệ `SET NULL` và Reader published filter PASS; run `20261011T085023Z-75556`.
- `export-schema`: raw schema actor v2 bất biến; admin/editor/reader/anonymous lần lượt 14/14/6/0 operation, hash được ghi ở manifest/run `20261011T085027Z-75998`.
- `test scenarios`: S1–S6 đều PASS ở run mới nhất `20261011T141418Z-174367`; Reader projection private bị từ chối an toàn và Reader PATCH bị từ chối, không làm đổi dữ liệu. Run cũ `20261011T105231Z-104612` được giữ làm evidence lịch sử.
- `test invariants`: baseline run `20261011T105236Z-105096` có 9 PASS và 1 failure aggregate; recheck mới nhất `20261011T141918Z-175886` dưới harness `8a0d042` có 9 PASS, 2 failure (aggregate và contract probe), 0 blocked, exit `1`. Run trước `20261011T134626Z-160826` vẫn được giữ làm lịch sử. Các failure được giữ nguyên để làm evidence, không nới assertion.
- `test raw`: campaign run `20261011T085034Z-76481` chọn đúng 10 operation trên seed `101,202,303`; lần lượt 59/65/51 case, restore PASS, runner exit 1 do `max_time`/check failure.
- `test guided`: campaign run `20261011T095117Z-89079` dùng overlay riêng và stateful phase; lần lượt 5.770/5.864/5.894 case, restore PASS, runner exit 1 do `max_time`/check failure.
- `replay <case-id>`: chạy lại case ổn định từ fixture map hiện tại; `editor-crud`, `positive-operations` và `anonymous-denied` đã có run pass. `aggregate-query-robustness` là reproducer deterministic cho candidate 500; run mới `20261011T134519Z-160153` dưới harness `bcbf219` đồng thời kiểm tra hai control 200 và vẫn giữ exit `1` vì variant unknown trả 500. `contract-schema-candidates` ở run `20261011T130227Z-139257` ghi bốn schema candidate và giữ exit `1` có chủ đích. Commit `baaee4b` đã bổ sung replay parent chain khi artifact có đủ dữ liệu: `pM4r4g` ở run `20261011T131321Z-144935` replay đủ `mvlcIV → pM4r4g`, final `200` trái expected `400`, restore PASS và exit `1`; `CkqaOB` không có parent chain nên vẫn `reproduced_request_only` ở run `20261011T131350Z-145631`. Sau commit `a713481`, replay dưới HEAD `916152e` xác nhận `tFjhQT` source/expected `200`, actual `403`, `mismatch`, restore PASS, exit `1` ở run `20261011T132550Z-151921`; `Q8K5Nh` source/expected/actual `403`, `reproduced`, restore PASS, exit `0` ở run `20261011T132604Z-152556`. Recheck chain dưới HEAD `3960f55` xác nhận `aZmz3k` full-chain `C7nkph → aZmz3k`, `200→200`, restore PASS, exit `0`; `Ag8Csb` bị dừng trung thực vì source pool 100 ID không khớp fixture snapshot 3 ID. Replay bổ sung `kb5gjq` ở run `20261011T135006Z-162769` tái hiện request-only `500` với `published_at=""`, restore PASS, exit `1`; log ghi SQLSTATE `22007`, nên giữ là schema-semantic/product robustness candidate. Replay `6IayFG` ở run `20261011T140814Z-170794` tái hiện request positive có `offset` vượt safe-number và `400 INVALID_QUERY`, restore PASS, exit `1`; đây là schema semantic/generator-positive candidate. Replay `6THjzP` ở run `20261011T141024Z-171863` tái hiện `name` integer được Directus ép thành string, source/actual `200` trái negative expected `400`, restore PASS, exit `1`; đây là semantic coercion/negative-oracle mismatch. Replay `QPKZ6w` ở run `20261011T141213Z-172805` tái hiện projection trả `200` chỉ có `title` trong khi schema yêu cầu `score`; `response_schema_conformance` vẫn failure, nhưng exit `0` chỉ phản ánh reproducer status, không phải contract PASS. Không tự đếm mỗi check failure thành một defect.
- `reset`: kiểm tra đúng project/volume label rồi mới dừng stack, xóa đúng volume `r06-k05_db_data` và runtime children; safety reset đã được thực thi ở run `20261011T050050Z-26220`, sau đó stack được dựng và seed lại.
- `test schema-smoke`: pilot legacy 5 operation vẫn có thể chạy để đối chiếu; campaign chính là `raw`/`guided` 10 operation.

Khi `custom_permission_rules_enabled` chưa bật, không được tự thêm license key vào repository, sửa trực tiếp DB hoặc nới assertion để biến blocker thành pass. `seed` sẽ chạy tiếp được phần policy Reader sau khi license hợp lệ được cấu hình cục bộ và người dùng xác nhận xử lý snapshot schema cũ.

`down` mặc định giữ volume `r06-k05_db_data`. Không dùng `docker compose down -v`, `docker system prune` hoặc lệnh xóa volume hàng loạt để xử lý lỗi lab.

## Quy trình dựng lại từ máy sạch

1. Cài Docker Engine và Docker Compose plugin; không cần cài Node, PostgreSQL hay Python package trên host.
2. Sao chép `config/lab.env.example` thành `config/lab.env`, thay toàn bộ `REPLACE_*`, rồi chạy `chmod 600 config/lab.env`. Không commit file này.
3. Kiểm tra dependency, digest và URL bằng `./lab.sh doctor`.
4. Khởi động stack bằng `./lab.sh up`. Lệnh chờ Directus healthy; nếu cần xem trạng thái, dùng `docker compose --env-file config/lab.env --project-name r06-k05 -f compose.yaml ps`.
5. Chạy `./lab.sh seed`. Seed tạo schema/fixture idempotent và ghi `runtime/fixture-ids.json`; để đạt Reader policy, `LICENSE_KEY` phải hợp lệ và được cấu hình cục bộ trước `up`.
6. Chạy `./lab.sh test smoke` và `./lab.sh test scenarios`. `blocked` là trạng thái cần xử lý, không phải pass giả.
7. Chạy `./lab.sh export-schema` sau seed. Schema raw theo actor nằm dưới `runtime/schemas/<fixture_version>/`; hash và inventory nằm trong run artifact.
8. Chạy `./lab.sh test raw` hoặc `./lab.sh test guided` với ngân sách mặc định. Dùng override ngắn chỉ cho pilot và ghi rõ trong report.
9. Xem `artifacts/runs/<run_id>/metadata.json`, `run.log`, `campaign-index.json`, `metrics.json`, report JSON/NDJSON và `invariant-report.json`. Ví dụ: `jq . artifacts/runs/<run_id>/metadata.json`.
10. Replay ca ổn định bằng `./lab.sh replay <case-id>`. Reproducer failed/blocked nằm cùng run directory.
11. Khi kết thúc, dùng `./lab.sh down` để giữ dữ liệu hoặc `./lab.sh reset` để xóa đúng lab sau khi đã xác minh volume; reset không thể khôi phục fixture nếu không có backup ngoài lab.

## Khắc phục lỗi thường gặp

- `config/lab.env` thiếu hoặc sai quyền: copy lại file example, điền giá trị cục bộ và `chmod 600`.
- Compose báo thiếu biến: mọi lệnh phải đi qua `lab.sh`, hoặc dùng đủ `--env-file config/lab.env --project-name r06-k05 -f compose.yaml`.
- Directus chưa healthy: kiểm tra `docker compose ... ps` và `artifacts/runs/<run_id>/run.log`; không dừng container của project khác.
- `seed` dừng ở `custom_permission_rules_enabled=false`: đây là blocker license đã xác minh. Không bypass bằng DB/UI; cấu hình license ngoài Git rồi seed/export schema lại.
- Raw schema hash thay đổi: giữ snapshot cũ bất biến, lưu schema mới như baseline/fixture version mới sau khi được chấp thuận; không overwrite âm thầm.
- Campaign có failure: giữ `runner` exit code, report, coverage và restore status; triage theo [`docs/replay-cases.md`](docs/replay-cases.md), không dùng `|| true` để biến pass.
- Campaign dài báo `TOKEN_EXPIRED`: kiểm tra `ACCESS_TOKEN_TTL` trong Compose/manifest, chạy `./lab.sh up` để recreate Directus rồi bắt đầu run mới; token được refresh trước snapshot và restore.
- Cổng `8055` bận: dừng đúng container thuộc project `r06-k05` hoặc đổi port chỉ khi có quyết định baseline mới; không chiếm/dừng dịch vụ project khác.

## Tài liệu bàn giao

- [Quyết định G0](docs/g0-quyet-dinh-ky-thuat.md)
- [Tiêu chí nghiệm thu G1](docs/g1-acceptance.md)
- [Kiến trúc](docs/architecture.md)
- [Ma trận quyền](docs/permissions.md)
- [Ma trận operation/scenario/invariant](docs/test-matrix.md)
- [Replay và reproducer](docs/replay-cases.md)
- [Kịch bản demo](docs/demo.md)
- [Nhật ký triển khai và hướng dẫn đọc code](docs/implementation-log-g0.md)
- [Bản bàn giao checkpoint cuối local](evidence/final-handoff-2026-10-11.md)
- [Manifest baseline](manifest/baseline.yaml)
- [AGENTS.md](AGENTS.md) — quy tắc local tại máy làm việc; không thuộc checkpoint tracked hiện tại

Các kết quả chạy sau này phải ghi run ID, SHA harness, baseline/image digest, actor, fixture version, schema hash, seed, budget, thời gian và trạng thái kết thúc. Kết quả chưa chạy phải giữ nguyên trạng thái chưa chạy.

## Bằng chứng triển khai và giới hạn

Run gần nhất và giới hạn được tổng hợp tại [`evidence/g1-implementation-2026-10-10.md`](evidence/g1-implementation-2026-10-10.md) và [`evidence/runtime-verification-2026-10-11.md`](evidence/runtime-verification-2026-10-11.md). Report thô nằm trong `artifacts/runs/<run_id>/` (Git ignore); schema và ID map runtime nằm trong `runtime/` (Git ignore). Các thư mục này cần được giữ cục bộ để replay/triage, nhưng không được đưa credential hoặc response nhạy cảm vào commit.

Full raw/guided v2 đã chứng minh pipeline 10 operation, artifact và restore trên ba seed; cả hai run vẫn giữ runner failure để triage, không được báo là pass. Raw có 59/65/51 case; guided có 5.770/5.864/5.894 case. Reader policy thật đã được kiểm tra: schema có 6 operation, published filter trả đúng fixture, projection `internal_notes` bị từ chối và PATCH bị từ chối, không làm đổi dữ liệu. Candidate `aggregate={"foo":1}` vẫn tái hiện HTTP 500 ở replay `20261011T134519Z-160153`; cùng run ghi `aggregate={}` và `aggregate={"count":["id"]}` trả 200. Phân loại hiện tại là schema omission + product robustness candidate, chưa phải defect đã xác nhận. Replay guided `kb5gjq` tái hiện `POST /items/qa_articles` với `published_at=""` trả `500` do PostgreSQL `22007`; `F8j8Gl` tái hiện `export=json` trả raw array ngoài schema object; `UNKW3j` tái hiện `export=xml` trả `text/xml`, còn `R0sH5o` tái hiện `export=yaml` trả `text/yaml` ngoài schema JSON; `DhqXrn` full-chain tái hiện source `204` thành actual `403` do field `id` bị từ chối; `UTk4sa` dừng ở parent ID mapping và không gửi target; `6IayFG` tái hiện `400 INVALID_QUERY` do `offset` vượt safe-number; `6THjzP` tái hiện `name` integer được Directus ép thành string, source/actual `200` trái negative expected `400`; `QPKZ6w` tái hiện projection chỉ trả `title` trong khi schema yêu cầu `score`, response-schema failure vẫn được giữ; các finding này chưa xác nhận defect. Một nguyên nhân có thể sinh nhiều check failure. Triage/replay và contract probe đã xác nhận POST object/array, export CSV/XML/JSON/YAML và DELETE 204 là các contract/schema candidate riêng; probe hiện tại ghi bốn candidate tại run `20261011T130227Z-139257` và vẫn giữ exit `1`. Chi tiết full campaign mới và giới hạn nằm trong [`evidence/runtime-verification-2026-10-11.md`](evidence/runtime-verification-2026-10-11.md), còn phân tích line-level nằm trong [`evidence/failure-triage-v2-2026-10-11.md`](evidence/failure-triage-v2-2026-10-11.md).

G1 không phải tuyên bố mọi test đều PASS. Checklist, nguồn yêu cầu và cách phân biệt
baseline đạt với failure còn mở được ghi tại [`docs/g1-acceptance.md`](docs/g1-acceptance.md).
