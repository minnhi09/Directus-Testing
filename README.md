# DAMH — R06 Directus + K05 Schemathesis

Đây là harness kiểm thử REST API Directus theo schema, tập trung vào CRUD, query, quyền và invariant nghiệp vụ của hai collection `qa_categories` và `qa_articles`.

Trạng thái hiện tại là bản triển khai tạm thời sau G0. Compose, seed fixture, actor, schema export, sáu scenario và pilot Schemathesis đã có đường chạy thật trên máy hiện tại. G1 chưa được tuyên bố: Directus đang báo `custom_permission_rules_enabled=false`, nên chưa tạo được policy lọc/ẩn field cho Reader; kiểm tra độc lập trên máy thứ hai cũng chưa có.

## Chuẩn bị lab

Yêu cầu chính là Docker Engine/Compose. Không cần cài Node hoặc Python trên host để chạy stack dự kiến.

```bash
cp config/lab.env.example config/lab.env
chmod 600 config/lab.env
```

Mở `config/lab.env` và thay các giá trị `REPLACE_*` bằng giá trị cục bộ. File này bị Git ignore. Không ghi credential thật vào source, log hoặc report. Bốn khóa `EDITOR_*` và `READER_*` là credential cho API actor; chúng được seed/policy dùng sau khi admin bootstrap, không dùng quyền Studio. Máy hiện tại đã có credential cục bộ cho hai actor; giá trị không được ghi vào Git hay artefact.

`API_URL` mặc định là `http://127.0.0.1:8055`; `RUNNER_API_URL` là `http://directus:8055` trong network Compose. Chỉ đổi URL khi có quyết định baseline mới; API host vẫn phải bind loopback.

Các image đã được ghi bằng tag và digest trong [`manifest/baseline.yaml`](manifest/baseline.yaml). Pull rõ ràng trước khi chạy:

```bash
docker compose --env-file config/lab.env --project-name r06-k05 -f compose.yaml pull
```

Image Schemathesis được dùng ở bước pilot sau khi exporter và schema đã sẵn sàng; kiểm tra image runner bằng digest trong manifest trước campaign.

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
```

Mỗi lệnh được nhận diện tạo một thư mục `artifacts/runs/<run_id>/` bị Git ignore, gồm `metadata.json` và `run.log`. Metadata ghi command, mã thoát, SHA harness, trạng thái working tree, baseline image, actor nếu được truyền qua `LAB_ACTOR` (`admin`, `editor`, `reader`, `anonymous` hoặc `unspecified`), fixture/schema/seed/budget nếu có và đường dẫn ID map. Token và password không được ghi vào đó. Có thể đặt `LAB_RUN_ID` để chọn ID ổn định cho một lệnh; ID phải chưa tồn tại, chỉ gồm chữ, số, `.`, `-`, `_` và tối đa 64 ký tự.

`runtime/fixture-ids.json` là vị trí dùng chung để seed bàn giao `fixture_version` và ánh xạ tên fixture → ID tự sinh. Hình dạng tối thiểu là `{"schema":1,"fixture_version":"...","fixtures":{"qa_categories":{"name":1},"qa_articles":{"name":1}}}`; ID phải là số nguyên dương. Lệnh đọc schema/test phải dùng đường dẫn này thay vì hard-code ID.

Trạng thái lệnh trên máy hiện tại:

- `doctor`: đạt; Compose, digest, URL loopback và admin health đều được kiểm tra.
- `up`: đạt; database và Directus healthy.
- `seed`: tạo/kiểm tra schema, seed 3 category + 12 article, ghi ID map và tạo actor; kết thúc lỗi có chủ đích khi license không cho permission filter của Reader.
- `smoke`: validation field và quan hệ `SET NULL` đạt; phần Reader bị chặn bởi cùng blocker.
- `export-schema`: đạt; lưu schema raw bất biến cho `admin` (14 operation), `editor` (14), `reader` (2) và `anonymous` (0).
- `test scenarios`: S1–S3 đạt; S4–S6 được ghi `blocked` vì operation article không xuất hiện trong schema Reader, nên harness không gửi request quyền bị cấm.
- `test schema-smoke`: pilot 5 operation chạy với Schemathesis, lưu report/coverage và khôi phục fixture; run hiện thất bại để giữ nguyên các failure cần triage.

Khi `custom_permission_rules_enabled` chưa bật, không được tự thêm license key vào repository, sửa trực tiếp DB hoặc nới assertion để biến blocker thành pass. `seed` sẽ chạy tiếp được phần policy Reader sau khi license hợp lệ được cấu hình cục bộ và người dùng xác nhận xử lý snapshot schema cũ.

`down` mặc định giữ volume `r06-k05_db_data`. Không dùng `docker compose down -v`, `docker system prune` hoặc lệnh xóa volume hàng loạt để xử lý lỗi lab.

## Tài liệu bàn giao

- [Quyết định G0](docs/g0-quyet-dinh-ky-thuat.md)
- [Kiến trúc](docs/architecture.md)
- [Nhật ký triển khai và hướng dẫn đọc code](docs/implementation-log-g0.md)
- [Manifest baseline](manifest/baseline.yaml)
- [AGENTS.md](AGENTS.md) — quy tắc bắt buộc tại máy làm việc; file này bị ignore theo quy ước riêng của nhóm

Các kết quả chạy sau này phải ghi run ID, SHA harness, baseline/image digest, actor, fixture version, schema hash, seed, budget, thời gian và trạng thái kết thúc. Kết quả chưa chạy phải giữ nguyên trạng thái chưa chạy.

## Bằng chứng triển khai tạm thời

Run gần nhất và giới hạn được tổng hợp tại [`evidence/g1-implementation-2026-10-10.md`](evidence/g1-implementation-2026-10-10.md). Report thô nằm trong `artifacts/runs/<run_id>/` (Git ignore); schema và ID map runtime nằm trong `runtime/` (Git ignore). Các thư mục này cần được giữ cục bộ để replay/triage, nhưng không được đưa credential hoặc response nhạy cảm vào commit.

Các profile `test raw`, `test guided`, `replay` và `reset` vẫn chưa bật. Pilot hiện chỉ là `schema-smoke` năm operation của `qa_articles`, có overlay allowlist được ghi lý do; schema raw không bị sửa.
