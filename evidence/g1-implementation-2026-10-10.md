# Evidence — triển khai tạm thời G1 — 2026-10-10

Tài liệu này ghi nhận những gì đã chạy thật trên máy hiện tại sau khi người dùng
cho phép tạm triển khai các phần còn thiếu. Đây chưa phải biên bản nghiệm thu G1.
Không ghi credential, access token hoặc nội dung secret vào evidence.

## Phạm vi và provenance

- Repository đang ở nhánh `main`, HEAD trước thay đổi chưa commit là
  `a2693f6154753cca2f1d2eb3d84e3a831a42bbf0`.
- Harness working tree dirty do phần triển khai tạm thời; không bịa SHA cho
  thay đổi chưa commit.
- Baseline: Directus `12.5.0`, PostgreSQL `16-alpine`, Schemathesis `4.30.0`,
  image digest theo [`manifest/baseline.yaml`](../manifest/baseline.yaml).
- URL host `http://127.0.0.1:8055`; runner dùng `http://directus:8055` trong
  network `r06-k05_network`.
- Credential editor/reader đã được tạo cục bộ qua các khóa trong
  `config/lab.env`; giá trị không xuất hiện trong log/metadata.

## Kết quả run

| Lệnh | Run ID | Kết quả thật |
|---|---|---|
| `./lab.sh doctor` | `20261010T063601Z-68170` | Exit `0`; Docker/Compose, digest, URL và admin authenticated health đạt |
| `./lab.sh seed` | `20261010T063111Z-64428` | Exit `1` sau khi schema đã tương thích, seed 3 category + 12 article, ghi ID map và login actor; bị chặn khi đọc license policy Reader |
| `./lab.sh smoke` | `20261010T063020Z-62841` | Exit `1`; validation `score/status` trả 400 đúng, quan hệ `SET NULL` đạt, Reader article trả 403 vì chưa có permission |
| `./lab.sh export-schema` | `20261010T063207Z-65790` | Exit `0`; raw schema immutable: admin 14 operation, editor 14, reader 2, anonymous 0 |
| `./lab.sh test scenarios` | `20261010T063203Z-65359` | Exit `1`; S1 Editor CRUD, S2 filter status, S3 sort/pagination đạt; S4–S6 blocked vì operation article không có trong Reader schema |
| `./lab.sh test schema-smoke` | `20261010T062453Z-61302` | Exit `1`; 5/5 operation được chạy, report và coverage lưu, fixture snapshot khôi phục PASS |

Các artefact chi tiết nằm trong `artifacts/runs/<run_id>/` và bị Git ignore.
ID map hiện tại nằm ở `runtime/fixture-ids.json` và có ba category cùng 12 article
với ID thật 14–25; test không hard-code các ID này.

## License và policy Reader

Component đọc `GET /license` bằng admin trước khi tạo policy có filter/field
restriction. Instance hiện trả entitlement
`custom_permission_rules_enabled=false`. Vì vậy component dừng với lỗi rõ ràng,
không sửa trực tiếp database, không thêm license giả và không gửi request quyền
âm tính khi operation đã bị lọc khỏi schema. Đây là blocker môi trường/license,
chưa phải defect sản phẩm.

## Pilot Schemathesis

Pilot dùng schema editor raw làm nguồn, tạo overlay tạm chỉ giữ năm operation
`qa_articles` (GET/POST list và GET/PATCH/DELETE detail). Raw schema không bị sửa.
Budget thực tế: một worker, `max-examples=20`, seed `101`, request timeout 10
giây, rate 5 request/giây, tối đa 300 giây.

Run tạo 1.418 test cases, 9 case có failure và 11 unique failure; thời gian
300,36 giây. Coverage operation đạt 5/5 (100%); parameter/keyword/example/
response coverage lần lượt khoảng 41,6% / 18,6% / 62,5% / 30,7% theo report.
Các failure đang được giữ nguyên để triage, gồm status DELETE 204 chưa có trong
schema raw, phản hồi 403/400 từ input/query của Directus và các mismatch schema
liên quan quan hệ. Chưa kết luận thành defect sản phẩm. Snapshot/restore sau pilot
khớp fixture trước pilot.

## Trạng thái nghiệm thu

- Đạt một phần: stack healthy, schema/fixture/ID map/editor CRUD/query và raw
  actor schema đã có bằng chứng.
- Chưa đạt: policy Reader published + ẩn `internal_notes`, Reader write
  rejection, đủ 10 operation campaign, raw/guided/replay và kiểm tra chéo độc
  lập trên máy thứ hai.
- Không tạo commit, tag, push hoặc PR trong phiên này. `AGENTS.md` và `mnhy/`
  vẫn không được đưa vào Git.

## Việc cần người dùng quyết định

Nếu có license Directus hợp lệ với entitlement
`custom_permission_rules_enabled`, hãy cấu hình nó cục bộ (không gửi secret vào
chat), báo tôi biết đã sẵn sàng, rồi chạy lại seed → schema export → smoke →
scenarios. Nếu không có license này, cần chấp nhận giới hạn Reader hiện tại và
đưa blocker vào báo cáo thay vì bypass.

G1 còn cần một lần dựng/kiểm tra trên máy độc lập theo README và người review
chéo xác nhận artefact; chạy hai container trên cùng máy không đủ bằng chứng đó.
