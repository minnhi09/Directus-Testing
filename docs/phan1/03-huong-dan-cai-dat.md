# 03 — Hướng dẫn cài đặt, cấu hình, build/run và seed

## 1. Kết luận về môi trường đã xác minh

Stack lab `r06-k05` đang chạy bằng Docker, không phải một build mới từ checkout Directus. Vì vậy các lệnh dưới đây được chia thành:

- quy trình dựng Directus từ source để tái lập;
- quy trình chạy image lab R06/K05 đã pin digest;
- các bước seed fixture của lab.

Trong nhiệm vụ này chỉ chạy kiểm tra an toàn trên stack hiện có (`doctor`, health/liveness, trạng thái container và database). Chưa chạy `pnpm install`, build, `directus bootstrap`, migration mới hoặc `./lab.sh seed`.

## 2. Chuẩn bị môi trường từ source

Mã nguồn yêu cầu Node.js `22` và pnpm `>=10 <11`; root `package.json` pin `pnpm@10.27.0`. Không có `.env.example` tracked trong checkout Directus, nên phải tạo `.env` theo deployment thật hoặc dùng CLI `directus init` tương tác. Không dùng Node/pnpm hiện tại trên PATH của máy này (`node v26.10.0`, `pnpm 12.9.1`) cho build source nếu chưa chuyển về phiên bản yêu cầu.

Ví dụ chuẩn bị bằng NVM/Corepack (không sửa `.zshrc` tự động):

```bash
cd /home/mlanh/projects/KTPM/directus
# Dùng Node 22 qua NVM hoặc trình quản lý Node tương đương.
# nvm use 22                 # nếu NVM đã được nạp trong shell
corepack enable
corepack prepare pnpm@10.27.0 --activate
node --version
pnpm --version
pnpm install --frozen-lockfile
```

Trong phiên khảo sát hiện tại, `nvm` không được expose như một shell function, nhưng executable Node `v22.23.3` có tại `/home/mlanh/.nvm/versions/node/v22.23.3/bin/`. Nếu NVM chưa được nạp, dùng Node 22 từ trình quản lý khác hoặc điều chỉnh `PATH` cục bộ; không cần sửa `.zshrc` để thực hiện một lần build.

`api/package.json` và `app/package.json` dùng workspace dependency; vì vậy cài từ root để pnpm resolve toàn bộ monorepo. Lockfile `pnpm-lock.yaml` phải được giữ nguyên.

## 3. Cấu hình runtime source

Tạo `/home/mlanh/projects/KTPM/directus/.env` cục bộ, không commit. Tối thiểu với PostgreSQL cần các biến `KEY`, `SECRET` (secret nên dài ít nhất 32 bytes), `DB_CLIENT=pg`, `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USER`, `DB_PASSWORD`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `PUBLIC_URL`, `HOST` và `PORT`. `api/src/database/index.ts` xác nhận các biến `DB_*` theo dialect; `packages/env/src/constants/defaults.ts` đặt `HOST=0.0.0.0`, `PORT=8055`, `CONFIG_PATH=.env`, `ACCESS_TOKEN_TTL=15m` và storage local mặc định.

Các tuỳ chọn thường dùng khi chạy lab/dev:

```dotenv
KEY=<random-application-key>
SECRET=<random-secret-at-least-32-bytes>
DB_CLIENT=pg
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=directus
DB_USER=directus
DB_PASSWORD=<local-password>
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=<local-admin-password>
PUBLIC_URL=http://127.0.0.1:8055
HOST=0.0.0.0
PORT=8055
```

Có thể dùng `pnpm --filter @directus/api cli security:key:generate` và `security:secret:generate` để tạo giá trị, hoặc tạo bằng cơ chế quản lý secret của môi trường. Không đưa giá trị thật vào report.

CLI `directus init` trong `api/src/cli/commands/init/index.ts` là quy trình tương tác: hỏi database, cài driver bằng npm, chạy seed/migration, tạo `.env`, rồi hỏi admin. Với monorepo đã có lockfile, quy trình pnpm + `.env` kiểm soát thủ công dễ truy vết hơn; `init` chỉ dùng khi chấp nhận các prompt và side effect cài driver.

## 4. Database, bootstrap và migration

Chuẩn bị một database riêng cho Directus. Không trỏ vào database của project khác. Từ root source, các lệnh CLI được đăng ký ở `api/src/cli/index.ts`:

```bash
cd /home/mlanh/projects/KTPM/directus
pnpm --filter @directus/api cli bootstrap
```

`bootstrap` trong `api/src/cli/commands/bootstrap/index.ts` chờ database, kiểm tra `isInstalled()`, gọi `database/seeds/run.ts` nếu chưa có bảng Directus, chạy `database/migrations/run.ts latest`, tạo admin từ `ADMIN_EMAIL`/`ADMIN_PASSWORD`, cập nhật settings/owner rồi đóng connection. Nếu database đã cài, nó bỏ qua install nhưng vẫn chạy migration mới nhất.

Các lệnh riêng tương ứng:

```bash
pnpm --filter @directus/api cli database install
pnpm --filter @directus/api cli database migrate:latest
pnpm --filter @directus/api cli schema snapshot -y --format json ./snapshot.json
```

Tên command chính xác được định nghĩa trong `api/src/cli/index.ts`. `database install` chỉ dành cho database chưa cài; `api/src/database/seeds/run.ts` sẽ báo `Database is already installed` nếu `directus_collections` đã tồn tại. Không chạy `database migrate:down` trong quy trình thiết lập bình thường vì đây là thao tác hạ migration.

## 5. Build và run từ source

Build toàn monorepo hoặc từng package:

```bash
cd /home/mlanh/projects/KTPM/directus
pnpm build
pnpm --filter @directus/api build
pnpm --filter @directus/app build
```

Chạy dev backend và dashboard ở hai terminal:

```bash
cd /home/mlanh/projects/KTPM/directus
pnpm --filter @directus/api dev
pnpm --filter @directus/app dev -- --host
```

Theo `AGENTS.md`, API dev mặc định dùng port `8055`, app Vite dùng port `8080`. API dev script đặt `SERVE_APP=true`; nếu chạy API không phục vụ app, dùng CLI `start` sau khi build hoặc cấu hình `SERVE_APP=false` theo script.

Kiểm tra sau khi run:

```bash
curl --fail --max-time 10 http://127.0.0.1:8055/server/ping
curl --i --max-time 10 http://127.0.0.1:8055/server/health
```

`/server/ping` là route public. `/server/health` nằm sau authentication và `ServerService.health` ném `ForbiddenError` nếu chưa xác thực; với admin/token hợp lệ endpoint thực hiện health check database, Redis, storage và email tùy cấu hình.

## 6. Build/run bằng Docker

`directus/Dockerfile` là multi-stage build dùng `node:22-alpine`, cài build tools, `pnpm fetch`, `pnpm install --recursive --offline --frozen-lockfile`, build các workspace không phải e2e và deploy package `directus` vào image production. Runtime mặc định là SQLite tại `/directus/database/database.sqlite`, expose port `8055`. `docker-entrypoint.cjs` chạy `directus bootstrap` trước rồi hand off cho `pm2-runtime`; khi dùng PostgreSQL phải truyền đầy đủ `DB_*` env và mount/network database tương ứng.

Lệnh build source image (chưa chạy trong nhiệm vụ này):

```bash
cd /home/mlanh/projects/KTPM/directus
docker build --build-arg NODE_VERSION=22 -t directus-local:12.5.0 .
```

`directus/docker-compose.yml` hiện là compose phục vụ debug dependency (PostgreSQL, MySQL, MariaDB, MSSQL, Oracle, Redis, RustFS, Azurite, Keycloak, MailDev); file không phải compose production chứa service Directus. Không khởi động toàn bộ file này chỉ để xác minh R06.

## 7. Chạy image lab R06/K05 (đường tái lập đã pin)

Quy trình hiện hành nằm trong `DAMH/compose.yaml`, `DAMH/config/lab.env.example` và `DAMH/lab.sh`:

```bash
cd /home/mlanh/projects/KTPM/DAMH
cp config/lab.env.example config/lab.env
# điền giá trị cục bộ cho DB_PASSWORD, DIRECTUS_KEY, DIRECTUS_SECRET,
# ADMIN_PASSWORD, EDITOR_PASSWORD, READER_PASSWORD, LICENSE_KEY nếu cần
chmod 600 config/lab.env
./lab.sh doctor
./lab.sh up
./lab.sh doctor
```

Compose project là `r06-k05`; API bind loopback `127.0.0.1:8055`; database không publish cổng host; network là `r06-k05_network`; volume là `r06-k05_db_data`. Image được pin trong file example: Directus 12.5.0, PostgreSQL 16-alpine và Schemathesis 4.30.0 với digest cụ thể. Compose đặt `DB_CLIENT=pg`, `DB_HOST=database`, `PUBLIC_URL=http://127.0.0.1:8055`, telemetry/cache/rate limiter tắt cho baseline, `ACCESS_TOKEN_TTL=2h`.

## 8. Seed dữ liệu lab

`./lab.sh seed` là seed fixture của K05, không phải core seed của `directus/api/src/database/seeds/run.ts`. Nó thực hiện theo thứ tự:

1. login admin và xác nhận schema `qa_categories`, `qa_articles`;
2. bảo đảm collection/field/validation/relation `qa_articles.category -> qa_categories` với `on_delete=SET NULL`;
3. tạo hoặc nhận diện theo tên ba category;
4. tạo hoặc nhận diện theo title mười hai article, gồm sáu `draft`, sáu `published`, score 0–5, `published_at` nullable, JSON metadata, Unicode và `internal_notes`;
5. ghi `runtime/fixture-ids.json`, không hard-code ID tự tăng;
6. tạo role/policy/user Editor và Reader; Reader cần license entitlement `custom_permission_rules_enabled` để dùng filter/policy custom.

Seed có tính lặp lại: nếu category trùng tên hoặc article trùng title nhưng dữ liệu không khớp contract, script dừng lỗi thay vì nhân bản hoặc âm thầm sửa. Sau seed chạy:

```bash
./lab.sh smoke
./lab.sh export-schema
./lab.sh test scenarios
```

Các lệnh trên có thể ghi dữ liệu probe/artefact. Chỉ chạy trên project/volume lab `r06-k05`; không dùng database khác và không dùng `docker compose down -v`. Trong nhiệm vụ này chỉ đọc fixture map đã có; không chạy lại seed.

## 9. Dừng và giới hạn an toàn

`./lab.sh down` giữ volume. `./lab.sh reset` xóa volume lab và runtime artefact, nên chỉ thực hiện sau khi đã xác nhận đúng project/volume và có phê duyệt riêng. Không dùng `docker system prune`, không xóa volume toàn máy. Nếu Docker daemon/Compose không khả dụng, các bước image lab và health bị BLOCKED; có thể tiếp tục phân tích source và tài liệu, nhưng không được tuyên bố runtime đã chạy.
