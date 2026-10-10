# G0 — Quyết định kỹ thuật và trạng thái bàn giao

Ngày ghi nhận: 2026-10-09

Tài liệu này chuyển các điểm thống nhất trong hai kế hoạch thành giao diện làm việc ban đầu. Đây là checkpoint G0 của harness; nó chưa phải bằng chứng G1. Sau khi tạo scaffold, stack local đã được pull và kiểm tra liveness/bootstrap vào ngày 2026-10-09; seed, schema và pilot vẫn chưa chạy.

## Quyết định áp dụng cho checkpoint

| Hạng mục | Giá trị | Trạng thái kiểm chứng |
|---|---|---|
| Directus | `12.5.0`, tag `v12.5.0`, commit `4f77933bf9551cac6b289576078783e189b8f4e3` | Commit tag đã đối chiếu trong checkout `/home/mlanh/projects/KTPM/directus`; instance chưa chạy |
| Image Directus | `docker.io/directus/directus:12.5.0` với digest trong [`manifest/baseline.yaml`](../manifest/baseline.yaml) | Manifest registry và local pull đã xác nhận |
| Database | PostgreSQL 16, image `postgres:16-alpine` với digest đã ghi | Manifest registry và local pull đã xác nhận |
| Schemathesis | `4.30.0`, runner Docker | Manifest registry và local pull đã xác nhận; pilot chưa chạy |
| Compose project | `r06-k05` | Được cố định trong `compose.yaml` và `lab.sh` |
| API từ host | `http://127.0.0.1:8055` | `/server/ping` trả `200`; `/server/health` trả `200` với admin accountability |
| API từ runner | `http://directus:8055` | Là hostname trong network lab, chưa có runner request |
| Cache/telemetry | Tắt trong Compose | Chưa có instance để xác minh runtime |
| Rate limiter | Tắt; giá trị tham chiếu `25` điểm/giây nếu bật về sau | Chưa chạy |
| Actor | `admin`, `editor`, `reader`, `anonymous` | Chưa tạo tài khoản/policy |
| Collection | `qa_categories`, `qa_articles` | Chưa seed; mô hình chi tiết theo kế hoạch nhóm |

Digest được ghi theo manifest đa kiến trúc để giữ cùng tham chiếu trên các máy hỗ trợ kiến trúc khác nhau. Bằng chứng pull/runtime hiện có ở [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md); G1 vẫn cần seed, schema, pilot và dựng lại bởi người khác.

## Giao diện chung

`./lab.sh` là điểm vào duy nhất của lab:

| Lệnh | Chủ sở hữu đầu ra | Trạng thái trong checkpoint này |
|---|---|---|
| `doctor` | Lành | Đã có kiểm tra Docker, cấu hình, image và compose |
| `up` / `down` | Lành | Đã có; `down` không xóa volume |
| `seed` | Trâm | Đã giữ tên lệnh, chưa có seed implementation |
| `smoke` | Trâm | Đã giữ tên lệnh, chưa có scenario implementation |
| `export-schema` | Nhân | Đã giữ tên lệnh, chưa có exporter implementation |
| `test schema-smoke` | Nhân | Chưa triển khai |
| `test scenarios` | Trâm | Chưa triển khai |
| `test raw` / `test guided` / `replay` | Nhân | Sau mốc giữa kỳ |
| `reset` | Lành | Chưa bật thao tác phá dữ liệu; chỉ thêm sau khi xác minh project/volume |

Các gói dùng chung sau này phải lấy URL, actor, credential, fixture ID và `run_id` từ lớp này. Không tạo helper đăng nhập/reset cạnh tranh trong từng suite.

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
- Chưa có fixture, policy, schema snapshot, report, coverage hay defect.
- Schemathesis image đã pull local nhưng chưa chạy campaign.
