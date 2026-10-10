# Nhật ký triển khai lab và hướng dẫn đọc code

Ngày cập nhật: 2026-10-10

Tài liệu này ghi lại phần nền tảng và bản triển khai tạm thời để người tiếp nhận có thể đọc code theo luồng, hiểu vì sao các tệp tồn tại và phân biệt quan sát đã chạy với phần còn bị chặn. Bản ghi này không thay thế [`AGENTS.md`](../AGENTS.md), hai kế hoạch trong `mnhy/` hoặc bằng chứng chạy riêng.

## Mốc Git

- Nhánh hiện tại: `main`.
- HEAD trước các thay đổi chưa commit: `a2693f6 Merge branch 'feat/g0-lab-foundation'`.
- Remote dự kiến: `origin` trỏ tới repository đồ án `minnhi09/Directus-Testing`.
- Dòng `/AGENTS.md` trong `.gitignore` có từ thay đổi người dùng trước đó và được giữ lại ngoài commit nền tảng; không xóa để làm worktree sạch giả tạo.
- `config/lab.env` là file cục bộ bị ignore. Credential trong đó chỉ dùng cho lab hiện tại, không được đưa vào commit hoặc report.

## Bản đồ tệp

| Tệp | Vai trò khi đọc code |
|---|---|
| [`lab.sh`](../lab.sh) | Điểm vào duy nhất của lab; kiểm tra điều kiện, tạo metadata/run log, gọi Compose hoặc component tạm thời và giữ mã lỗi thật |
| [`scripts/lab-components.sh`](../scripts/lab-components.sh) | Seed schema/fixture/actor, smoke, schema export, sáu scenario và pilot Schemathesis; credential chỉ truyền qua môi trường tiến trình |
| [`compose.yaml`](../compose.yaml) | Khai báo hai service `database` và `directus`, network `r06-k05_network`, volume `r06-k05_db_data`, port loopback và healthcheck |
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
- `seed`, `smoke`, `export-schema` và `test scenarios` gọi component tạm thời. Các run này luôn lưu report và trả mã lỗi thật khi precondition/policy chưa đạt. `test raw`, `test guided`, `replay`, `reset` vẫn chưa bật.

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

Bằng chứng chi tiết và giới hạn nằm trong [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md). Kết quả này chỉ chứng minh một máy và một baseline local; chưa chứng minh tái lập trên máy thứ hai.

## Bản triển khai tạm thời — 2026-10-10

Component ở [`scripts/lab-components.sh`](../scripts/lab-components.sh) đã thực hiện các phần độc lập cần cho bản demo:

- Kiểm tra/tạo hai collection, field validation và quan hệ `qa_articles.category` với `SET NULL`; seed lặp lại theo tên fixture, không hard-code ID và ghi [`runtime/fixture-ids.json`](../runtime/fixture-ids.json).
- Tạo role/policy/actor editor và reader. Editor có CRUD hai collection. Reader category read tạo được; policy article có filter published và field giới hạn bị Directus từ chối vì entitlement `custom_permission_rules_enabled=false`.
- Smoke kiểm tra score/status invalid và nullification quan hệ; không gửi request negative cho Reader nếu operation đã bị lọc khỏi schema.
- Export raw OpenAPI riêng cho bốn actor và giữ hash bất biến. Editor có 14 operation do Directus xuất cả bulk operation; pilot lọc đúng 5 operation `qa_articles` bằng file overlay tạm, ghi lý do và không sửa raw.
- Sáu scenario ghi rõ `passed`, `failed` hoặc `blocked`. S1–S3 đạt; S4–S6 blocked do Reader schema chỉ có hai operation category.
- Pilot Schemathesis chạy một worker, tối đa 20 example/operation, seed `101`, timeout request 10 giây, rate 5 request/giây và tối đa 300 giây. Snapshot/restore fixture đã được thêm để pilot không làm bẩn trạng thái seed.

Chi tiết run ID, status và giới hạn nằm trong [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md). Không dùng output này để tuyên bố G1: license Reader và kiểm tra chéo trên máy khác còn thiếu.

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
6. Lành điều phối kiểm tra chéo trên máy khác, cập nhật evidence/manifest rồi mới xem xét G1.
