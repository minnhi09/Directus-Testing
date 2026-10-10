# Nhật ký triển khai G0 và hướng dẫn đọc code

Ngày cập nhật: 2026-10-10

Tài liệu này ghi lại phần nền tảng đã triển khai để người tiếp nhận có thể đọc code theo luồng, hiểu vì sao các tệp tồn tại và phân biệt phần đã chạy với phần mới chỉ giữ interface. Bản ghi này không thay thế [`AGENTS.md`](../AGENTS.md), hai kế hoạch trong `mnhy/` hoặc bằng chứng chạy riêng.

## Mốc Git

- Nhánh: `feat/g0-lab-foundation`.
- Commit nền tảng trước tài liệu này: `99b2f6d feat: add G0 lab foundation`.
- Remote dự kiến: `origin` trỏ tới repository đồ án `minnhi09/Directus-Testing`.
- Dòng `/AGENTS.md` trong `.gitignore` có từ thay đổi người dùng trước đó và được giữ lại ngoài commit nền tảng; không xóa để làm worktree sạch giả tạo.
- `config/lab.env` là file cục bộ bị ignore. Credential trong đó chỉ dùng cho lab hiện tại, không được đưa vào commit hoặc report.

## Bản đồ tệp

| Tệp | Vai trò khi đọc code |
|---|---|
| [`lab.sh`](../lab.sh) | Điểm vào duy nhất của lab; kiểm tra điều kiện, gọi Compose, chờ liveness và giữ mã lỗi của lệnh chưa triển khai |
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

- `doctor`: chỉ kiểm tra Docker, Compose, file cấu hình, placeholder, digest image, container của đúng project và liveness URL.
- `up`: yêu cầu `config/lab.env`, render Compose, gọi `docker compose up -d`, sau đó đợi trạng thái health của service `directus` tối đa 30 lần, mỗi lần 2 giây.
- `down`: gọi `docker compose down` và không dùng `--volumes`, nên volume dữ liệu được giữ lại.
- `seed`, `smoke`, `export-schema`, các profile `test`, `replay`, `reset`: hiện trả mã `2` cùng thông báo chưa triển khai. Đây là trạng thái có chủ ý để không báo pass giả.

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

## Những gì chưa được triển khai

Các lệnh dưới đây có tên trong interface nhưng chưa có implementation:

- Seed `qa_categories`, `qa_articles`, actor, policy và bảng ánh xạ ID.
- Smoke sáu scenario của Trâm.
- Xuất OpenAPI theo `admin`, `editor`, `reader` và allowlist năm operation `qa_articles`.
- Pilot `schema-smoke`, raw/guided, metrics, replay và reproducer.
- Reset có kiểm soát dữ liệu lab.

Không được xuất schema trước khi seed xong, dùng schema admin thay schema actor, hard-code ID tự sinh hoặc biến lệnh chưa triển khai thành exit `0` để che phần thiếu.

## Cách tiếp nhận phần việc tiếp theo

1. Chạy `./lab.sh doctor` và xác nhận đúng project/URL trước khi gọi API.
2. Đọc `docs/g0-quyet-dinh-ky-thuat.md` và `docs/traceability.md` để lấy interface, chủ sở hữu và phụ thuộc.
3. Trâm triển khai seed/policy/six scenarios theo fixture contract; Nhân dùng ID map và schema thực để triển khai exporter/pilot.
4. Sau mỗi phần, cập nhật evidence với command, exit code, actor, schema/fixture version và giới hạn; không ghi kết quả chưa chạy.
5. Lành tích hợp tuần tự từ baseline sạch, review diff và chỉ công bố G1 khi có seed, CRUD/quyền, schema, pilot và dựng lại bởi người khác.
