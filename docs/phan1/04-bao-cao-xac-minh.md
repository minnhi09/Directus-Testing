# 04 — Báo cáo xác minh môi trường và giới hạn

## 1. Phạm vi xác minh

Mục tiêu của lần chạy này là kiểm tra an toàn stack R06/K05 đang có, không thay đổi code Directus, không cài dependency, không build checkout, không bootstrap/migrate/seed lại, không dừng stack và không xóa volume. Các kết quả runtime dưới đây đến từ container image đã pin; các nhận định source đến từ checkout Directus hiện tại.

## 2. Trạng thái repository trước kiểm tra

| Repository | Branch/HEAD | Git status | Kết quả |
|---|---|---|---|
| `directus/` | `main`, `d3c9a8bb0c0096148c4740ce908e76c24f2413a0` | sạch | Đã đọc source và manifest |
| `DAMH/` | `feat/g1-shared-interface`, `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72` | có các file untracked có trước nhiệm vụ | Giữ nguyên, không reset/commit |

Directus package ghi `12.5.0`, nhưng baseline nguồn K05 ghi commit `4f77933bf9551cac6b289576078783e189b8f4e3`. Đây là hai provenance khác nhau.

## 3. Lệnh đã thực thi và kết quả thực tế

### 3.1 Công cụ và Docker

```text
node --version                 v26.10.0       (host PATH)
pnpm --version                 12.9.1         (host PATH)
docker --version               29.8.1
docker compose version         v5.5.1
docker info                    server 29.8.1
```

Docker daemon và Compose khả dụng. Host Node/pnpm không khớp yêu cầu source Node 22/pnpm 10.27.0, nên không dùng chúng để build checkout.

`docker ps` ghi nhận:

```text
r06-k05-runner-1     schemathesis/schemathesis:4.30.0   Up, healthy
r06-k05-directus-1  directus/directus:12.5.0            Up, healthy, 127.0.0.1:8055->8055
r06-k05-database-1  postgres:16-alpine                  Up, healthy
```

`docker inspect r06-k05-directus-1` xác nhận image đầy đủ `docker.io/directus/directus:12.5.0@sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331`, health `healthy`, container bắt đầu lúc `2026-10-12T09:58:28.146201202Z`. `docker exec ... node -p ...` trả Node `v22.23.3`, Directus `12.5.0`. `docker exec r06-k05-database-1 pg_isready` trả `/var/run/postgresql:5432 - accepting connections`.

### 3.2 `doctor` của lab

Lệnh:

```bash
cd /home/mlanh/projects/KTPM/DAMH
./lab.sh doctor
```

Kết quả:

```text
Run: 20261012T103055Z-13919
Doctor: PASS
Run status: passed (exit 0)
```

Artefact metadata và log được ghi tại `/home/mlanh/projects/KTPM/DAMH/artifacts/runs/20261012T103055Z-13919/`. Doctor xác minh thành công:

- Docker daemon, Docker Compose, `docker`, `curl`, `jq`;
- `config/lab.env` tồn tại và quyền file hợp lệ, các key bắt buộc hiện diện (giá trị được redact trong output);
- `compose config` hợp lệ;
- ba image digest-pinned Directus/PostgreSQL/Schemathesis hiện có;
- fixture ID map hợp lệ;
- API liveness trả HTTP 200;
- authenticated Directus health;
- license source `env`, status `active`, `custom_permission_rules_enabled=true`.

`runtime/fixture-ids.json` được đọc bằng `jq` không in ID: schema `1`, fixture version `r06-k05-v2`, project `r06-k05`, gồm 3 key category và 12 key article. Đây là fixture map đã tồn tại trước lần báo cáo; không chứng minh rằng seed vừa chạy trong nhiệm vụ này.

### 3.3 HTTP endpoint

```bash
curl --max-time 10 -i http://127.0.0.1:8055/server/ping
```

Kết quả thực tế: HTTP `200 OK`, body `pong`.

```bash
curl --max-time 10 -i http://127.0.0.1:8055/server/health
```

Kết quả thực tế khi không gửi token: HTTP `403 Forbidden`, JSON code `FORBIDDEN`. Điều này phù hợp với `ServerService.health`, nơi `isUnauthenticated(accountability)` ném `ForbiddenError`; doctor đã kiểm tra nhánh authenticated health riêng mà không in credential.

## 4. Những gì chưa chạy

Các bước sau chưa được thực thi trong nhiệm vụ này:

| Bước | Trạng thái | Lý do/giới hạn |
|---|---|---|
| `pnpm install --frozen-lockfile` từ checkout | Chưa xác minh | Host PATH đang Node 26/pnpm 12; không tự đổi toolchain trong nhiệm vụ tài liệu. |
| `pnpm build` hoặc build API/App | Chưa xác minh | Runtime đang dùng image digest, không phải build checkout `d3c9a8b...`. |
| `directus bootstrap`, `database install`, `database migrate:latest` | Chưa chạy | Stack đã khởi tạo; không chạy thao tác database ghi thêm khi không cần. |
| `./lab.sh seed` | Chưa chạy | Fixture map và schema runtime đã có; seed có thể ghi dữ liệu/probe. |
| `./lab.sh smoke`, `export-schema`, scenarios/campaign | Chưa chạy trong lần này | Báo cáo Phần 1 chỉ kiểm tra liveness/health và setup; không lặp campaign K05. |
| `directus/docker-compose.yml` | Chưa chạy | Đây là compose debug nhiều dependency, không phải stack Directus lab hiện hành. |

Không có bước nào bị BLOCKED do Docker/Compose; Docker đã khả dụng. Những mục trên là `chưa xác minh` do phạm vi và bảo toàn dữ liệu, không được diễn giải thành PASS.

## 5. Lỗi chẩn đoán và giới hạn provenance

Một lệnh chẩn đoán phụ `docker image inspect directus/directus:12.5.0` trả lỗi `No such image` vì local image được tham chiếu bằng tên đầy đủ kèm registry và digest. `docker inspect` container và `./lab.sh doctor` sau đó xác nhận image đầy đủ hiện diện; lỗi tên ngắn không phải lỗi khởi động hệ thống.

Liveness của image đang chạy không chứng minh source checkout hiện tại build được, vì SHA source `d3c9a8b...` khác SHA baseline nguồn K05 và container dùng image digest. Tương tự, fixture map chứng minh map tồn tại và hợp lệ, không chứng minh lệnh seed đã được chạy lại trong phiên này.

## 6. Đánh giá lần xác minh

Môi trường Docker lab đạt điều kiện healthy, API public ping hoạt động, database nhận kết nối, authenticated health hoạt động và cấu hình/image/fixture được doctor kiểm tra với exit `0`. Phần runtime hiện hữu đủ làm nền cho phân tích và hướng dẫn Phần 1. Mức xác minh source-build từ máy sạch, migration/seed mới và chức năng CRUD đầy đủ vẫn để `chưa xác minh`; không có tuyên bố pass cho các bước đó.
