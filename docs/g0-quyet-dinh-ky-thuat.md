# G0 — Quyết định kỹ thuật và trạng thái bàn giao

Ngày ghi nhận: 2026-10-09; cập nhật trạng thái chạy: 2026-10-10

Tài liệu này chuyển các điểm thống nhất trong hai kế hoạch thành giao diện làm việc ban đầu. Đây là quyết định baseline G0 và không thay thế bằng chứng G1. Sau scaffold, bản triển khai tạm thời đã chạy seed/schema/scenario/pilot trên máy hiện tại vào ngày 2026-10-10; G1 vẫn bị chặn bởi entitlement policy Reader và thiếu kiểm tra độc lập trên máy khác.

## Quyết định áp dụng cho checkpoint

| Hạng mục | Giá trị | Trạng thái kiểm chứng |
|---|---|---|
| Directus | `12.5.0`, tag `v12.5.0`, commit `4f77933bf9551cac6b289576078783e189b8f4e3` | Commit tag đã đối chiếu; image/runtime local đã được kiểm tra theo manifest |
| Image Directus | `docker.io/directus/directus:12.5.0` với digest trong [`manifest/baseline.yaml`](../manifest/baseline.yaml) | Manifest registry và local pull đã xác nhận |
| Database | PostgreSQL 16, image `postgres:16-alpine` với digest đã ghi | Manifest registry và local pull đã xác nhận |
| Schemathesis | `4.30.0`, runner Docker | Manifest registry/local pull đã xác nhận; pilot report có, failure còn chờ triage |
| Compose project | `r06-k05` | Được cố định trong `compose.yaml` và `lab.sh` |
| API từ host | `http://127.0.0.1:8055` | `/server/ping` trả `200`; `/server/health` trả `200` với admin accountability |
| API từ runner | `http://directus:8055` | Schemathesis pilot đã gửi request qua hostname trong network lab |
| Cache/telemetry | Tắt trong Compose | Đã dùng trong stack local; cần xác nhận lại khi dựng máy khác |
| Rate limiter | Tắt; giá trị tham chiếu `25` điểm/giây nếu bật về sau | Đã ghi trong Compose; pilot tự giới hạn 5 request/giây |
| Access token TTL | `2h` trong lab Compose | Để campaign tuần tự ba seed không hết token mặc định `15m`; được ghi trong manifest |
| Actor | `admin`, `editor`, `reader`, `anonymous` | Admin/editor/reader đăng nhập được; anonymous schema đã xuất, không có operation |
| Collection | `qa_categories`, `qa_articles` | Đã tạo/seed 3 category + 12 article; ID map runtime |

Digest được ghi theo manifest đa kiến trúc để giữ cùng tham chiếu trên các máy hỗ trợ kiến trúc khác nhau. Bằng chứng pull/runtime hiện có ở [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md); bằng chứng triển khai tạm thời ở [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md). G1 vẫn cần policy Reader đầy đủ và dựng lại bởi người khác.

## Giao diện chung

`./lab.sh` là điểm vào duy nhất của lab:

| Lệnh | Chủ sở hữu đầu ra | Trạng thái trong checkpoint này |
|---|---|---|
| `doctor` | Lành | Đã có kiểm tra Docker, cấu hình, image và compose |
| `up` / `down` | Lành | Đã có; `down` không xóa volume |
| `seed` | Lành triển khai tạm thời; Trâm chưa review | Đã chạy schema/fixture/actor; policy Reader bị chặn bởi license |
| `smoke` | Lành triển khai tạm thời; Trâm chưa review | Field/quan hệ đạt; Reader article bị chặn |
| `export-schema` | Lành triển khai tạm thời; Nhân chưa review | Raw schema 4 actor đã xuất và giữ hash |
| `test schema-smoke` | Lành triển khai tạm thời; Nhân chưa review | Pilot 5 operation đã chạy; report/coverage có, exit lỗi cần triage |
| `test scenarios` | Lành triển khai tạm thời; Trâm chưa review | S1–S3 đạt; S4–S6 blocked theo precondition schema |
| `test raw` / `test guided` / `replay` | Nhân | Sau mốc giữa kỳ |
| `reset` | Lành | Chưa bật thao tác phá dữ liệu; chỉ thêm sau khi xác minh project/volume |

Các gói dùng chung sau này phải lấy URL, actor, credential, fixture ID và `run_id` từ lớp này. Không tạo helper đăng nhập/reset cạnh tranh trong từng suite.

Lớp dùng chung hiện thực hóa các quy ước sau: URL đọc từ `API_URL`/`RUNNER_API_URL` với giá trị mặc định của baseline và vẫn bị kiểm tra là loopback/hostname nội bộ; credential editor/reader nằm ngoài Git trong `config/lab.env`; ID fixture nằm ở `runtime/fixture-ids.json` theo dạng `{schema, fixture_version, fixtures}`; mỗi lệnh lưu `metadata.json` và `run.log` dưới `artifacts/runs/<run_id>/`. Metadata không chứa token hoặc password. `lab.sh` cho phép truyền `LAB_ACTOR`, `LAB_FIXTURE_VERSION`, `LAB_SCHEMA_HASH`, `LAB_SEED` và `LAB_BUDGET` để các gói chuyên môn bổ sung thông tin run mà không tạo cơ chế cấu hình khác. Một run ID không được dùng lại để tránh ghi đè artefact.

## Phân công và phụ thuộc

| Gói | Chủ sở hữu | Điều kiện bắt đầu | Đầu ra nghiệm thu |
|---|---|---|---|
| Compose, manifest, script chung, README | Lành | G0 được áp dụng | Dựng đúng project/volume, mã thoát có ý nghĩa, tài liệu không chứa secret |
| Fixture, policy, seed, six scenarios | Trâm | Interface này và lab healthy | Seed lặp lại không nhân bản, có ID map và oracle theo actor |
| Schema exporter, allowlist, pilot | Nhân | Seed thành công và schema theo actor xuất được | Schema gốc bất biến, pilot đúng năm operation `qa_articles` |
| Tích hợp G1 | Lành | Hai gói có bằng chứng chạy | Health, seed, CRUD/quyền, schema, pilot và dựng lại đều được ghi kết quả |

## Chưa được tuyên bố

- Chưa tuyên bố G0/G1 đã được nghiệm thu bởi cả nhóm.
- Lần chạy local hiện tại chứng minh Directus và PostgreSQL healthy trên máy này; chưa chứng minh tái lập trên máy thứ hai.
- Reader policy filter/field restriction chưa tạo được vì license hiện báo `custom_permission_rules_enabled=false`; không bypass bằng DB/license giả.
- Raw schema, scenario report và Schemathesis report/coverage đã có trong runtime/artefact local; các failure pilot chưa được phân loại thành defect sản phẩm.
- Chưa có kiểm tra dựng lại độc lập trên máy khác và chưa có review chéo của thành viên; vì vậy chưa nghiệm thu G1.
