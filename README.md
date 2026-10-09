# DAMH — R06 Directus + K05 Schemathesis

Đây là harness kiểm thử REST API Directus theo schema, tập trung vào CRUD, query, quyền và invariant nghiệp vụ của hai collection `qa_categories` và `qa_articles`.

Trạng thái hiện tại là checkpoint G0: đã tạo giao diện lab, Compose, manifest baseline và tài liệu kiến trúc. Stack local đã được pull, bootstrap admin và kiểm tra health có xác thực; seed, schema snapshot, coverage và defect chưa có, nên chưa tuyên bố G1.

## Chuẩn bị lab

Yêu cầu chính là Docker Engine/Compose. Không cần cài Node hoặc Python trên host để chạy stack dự kiến.

```bash
cp config/lab.env.example config/lab.env
chmod 600 config/lab.env
```

Mở `config/lab.env` và thay các giá trị `REPLACE_*` bằng giá trị cục bộ. File này bị Git ignore. Không ghi credential thật vào source, log hoặc report.

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

Ở checkpoint hiện tại, `doctor`, `up` và `down` là các lệnh nền tảng có thể kiểm tra. `seed`, `smoke`, `export-schema` và các suite sẽ trả lỗi rõ ràng cho đến khi phần bàn giao tương ứng được tích hợp.

`down` mặc định giữ volume `r06-k05_db_data`. Không dùng `docker compose down -v`, `docker system prune` hoặc lệnh xóa volume hàng loạt để xử lý lỗi lab.

## Tài liệu bàn giao

- [Quyết định G0](docs/g0-quyet-dinh-ky-thuat.md)
- [Kiến trúc](docs/architecture.md)
- [Manifest baseline](manifest/baseline.yaml)
- [AGENTS.md](AGENTS.md) — quy tắc bắt buộc tại máy làm việc; file này bị ignore theo quy ước riêng của nhóm

Các kết quả chạy sau này phải ghi run ID, SHA harness, baseline/image digest, actor, fixture version, schema hash, seed, budget, thời gian và trạng thái kết thúc. Kết quả chưa chạy phải giữ nguyên trạng thái chưa chạy.
