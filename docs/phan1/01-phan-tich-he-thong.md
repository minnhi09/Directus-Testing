# 01 — Phân tích hệ thống Directus (R06)

## 1. Phạm vi, thời điểm và provenance

Đối tượng chính của báo cáo là mã nguồn tại `/home/mlanh/projects/KTPM/directus/`. Khảo sát được thực hiện ngày `2026-10-12` trên branch `main`, HEAD `d3c9a8bb0c0096148c4740ce908e76c24f2413a0`. Working tree Directus sạch tại thời điểm khảo sát. Manifest `directus/package.json` ghi phiên bản `12.5.0`; `api/package.json` ghi `@directus/api` `40.0.0`, `app/package.json` ghi `@directus/app` `18.1.0` và `sdk/package.json` ghi `@directus/sdk` `27.0.0`.

Baseline image đang chạy trong lab K05 là Directus `12.5.0` với digest `sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331`. Baseline nguồn được ghi trong DAMH là tag `v12.5.0`, commit `4f77933bf9551cac6b289576078783e189b8f4e3`, khác với checkout đang đọc. Vì vậy, kết luận tĩnh dưới đây áp dụng cho checkout `d3c9a8b...`; kết luận runtime áp dụng cho image digest nêu trên, không gộp hai provenance thành một.

Repository DAMH hiện ở branch `feat/g1-shared-interface`, HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, có các file untracked có trước nhiệm vụ (`01_ke_hoach_trien_khai_R06_K05.md`, `AGENTS.md`, và các evidence ngày 2026-10-11). Chúng được giữ nguyên. Năm file báo cáo của Phần 1 nằm riêng trong thư mục được yêu cầu.

Đã đọc `directus/AGENTS.md`, `directus/readme.md` và `DAMH/AGENTS.md`. `directus/AGENTS.md` là nguồn cho yêu cầu Node/pnpm, cấu trúc package và lệnh phát triển; `readme.md` xác nhận đây là nền tảng quản lý dữ liệu/API/dashboard nhưng không được dùng thay cho bằng chứng từ source. `DAMH/AGENTS.md` được dùng để giữ provenance, phạm vi K05 và quy tắc không reset/xóa volume.

## 2. Công nghệ và cấu trúc monorepo

Directus là monorepo pnpm dùng TypeScript/ES modules. `directus/package.json` yêu cầu Node `22` và pnpm `>=10 <11`, pin package manager `pnpm@10.27.0`; `pnpm-workspace.yaml` khai báo các workspace `directus`, `app`, `api`, `sdk`, `packages/*` và `tests/*`. Các phiên bản dependency bên ngoài tập trung trong catalog của `pnpm-workspace.yaml`, còn dependency nội bộ dùng `workspace:*`.

| Khu vực | Vai trò thực tế | Bằng chứng và quy mô khảo sát |
|---|---|---|
| `directus/` | Gói runtime/CLI đóng gói API và update check | `directus/package.json`, `cli.js` |
| `api/src/` | Backend Node/Express; REST, GraphQL, database, auth, permission, extension và WebSocket | 54 controller, 188 service, 273 file database, 30 middleware, 93 permission, 53 WebSocket file |
| `app/src/` | Dashboard Vue 3; component, view, Pinia store, layout, field interface và module | `app/src/main.ts`; khảo sát 237 component, 130 view, 103 composable, 25 store, 397 interface |
| `sdk/` | JavaScript/TypeScript SDK cho client | `sdk/package.json`, version `27.0.0` |
| `packages/*` | Package dùng chung: types, utils, schema, validation, storage, extension, env, themes, driver | 33 `package.json` trong thư mục `packages` |
| `tests/*` | Unit/e2e/sandbox và fixture kiểm thử | `tests/e2e/package.json`, các test trong `tests/e2e/tests` |

Phần backend được tổ chức theo lớp. `api/src/controllers` ánh xạ HTTP route; `api/src/services` chứa nghiệp vụ; `api/src/database` tạo Knex connection, schema helper, migration và seed; `api/src/middleware` xử lý auth/query/response; `api/src/permissions` thực hiện policy, field permission, filter và validation; `api/src/extensions` và emitter mở rộng hook/endpoint; `api/src/websocket` phục vụ real-time. Đây là cấu trúc đọc trực tiếp từ thư mục và import trong `api/src/app.ts`, không phải suy luận từ kiến thức chung về Directus.

## 3. Dependency chính

Backend `@directus/api` khai báo các dependency quan trọng sau trong `api/package.json`:

- HTTP và middleware: `express`, `cors`, `helmet`, `cookie-parser`, `qs`, `pino`.
- Database và query: `knex`, các driver PostgreSQL/MySQL/SQLite/MSSQL/Oracle trong catalog; code kết nối nằm ở `api/src/database/index.ts`.
- Authentication và security: `argon2`, `jsonwebtoken`, `jose`, `openid-client`, `ldapts`, `samlify`, `otplib`.
- Schema/permission/validation: các package `@directus/schema`, `@directus/types`, `@directus/validation`, `zod`, `joi`, `openapi3-ts`.
- Tệp và storage: `@directus/storage`, các driver local/S3/Azure/GCS/Supabase/Cloudinary, `sharp`, `busboy`, `tus`.
- Extension, event và runtime: `@directus/extensions`, `@directus/extensions-registry`, `eventemitter2`, `pm2`, `@godaddy/terminus`.

Dashboard `@directus/app` dùng Vue, Pinia, Vue Router, Vite, `@directus/sdk`, các package UI/editor, map và field renderer. `sdk/package.json` chỉ có nhóm build/test trong devDependencies và xuất `dist/index.js`/`dist/index.cjs`. `packages/env` cung cấp lớp đọc biến môi trường; `packages/types`, `utils`, `schema` và `system-data` được dùng xuyên suốt API/app.

Không có dependency được cài hoặc nâng cấp trong nhiệm vụ này. `pnpm-lock.yaml` được đọc như lockfile hiện hành.

## 4. Entry point và quy trình khởi tạo

Entry point đóng gói là `directus/cli.js`: nạp version/update check rồi import `@directus/api/cli/run.js`. `api/src/cli/run.ts` tạo CLI và gọi `parseAsync(process.argv)`. `api/src/cli/index.ts` đăng ký các lệnh `start`, `database install`, `database migrate:latest/up/down`, `bootstrap`, snapshot/apply schema và quản lý user/role.

Lệnh start gọi `startServer()` trong `api/src/server.ts`. `createServer()` tạo HTTP server từ `createApp()`, gắn shutdown hook/Terminus, metrics và WebSocket nếu được bật; `startServer()` lấy `HOST`, `PORT` hoặc UNIX socket từ env rồi listen. `packages/env/src/constants/defaults.ts` đặt mặc định `HOST=0.0.0.0`, `PORT=8055`, `CONFIG_PATH=<cwd>/.env`, `ACCESS_TOKEN_TTL=15m`, storage local và rate limiter tắt.

`api/src/app.ts` thực hiện các bước trước khi nhận request:

1. kiểm tra database và trạng thái đã cài đặt (`validateDatabaseConnection`, `isInstalled`);
2. cảnh báo nếu migration chưa đầy đủ, kiểm tra `SECRET`, `PUBLIC_URL`, database extension và storage;
3. khởi tạo license/entitlement, auth provider, deployment driver, extension manager và flow manager;
4. tạo Express app, query parser, security/rate-limit middleware;
5. đăng ký `/server/ping` public, sau đó `authenticate`, `schema`, `sanitizeQuery`, cache và các router `/auth`, `/items`, `/schema`, `/server`, `/users`, `/permissions`, `/relations`, `/graphql`, `/files` cùng các module khác;
6. đăng ký custom extension endpoint, not-found và error handler.

Frontend bắt đầu từ `app/src/main.ts`: tạo Vue app, cài i18n, Pinia, head manager, register component/directive/view, nạp và đăng ký extension, cài router rồi mount `#app`.

## 5. Database, migration và seed hệ thống

`api/src/database/index.ts` dùng `getConfigFromEnv('DB_')`, kiểm tra các biến bắt buộc theo `DB_CLIENT` rồi tạo một Knex instance dùng chung. PostgreSQL cần `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USER` và password hoặc connection string; SQLite cần `DB_FILENAME`; các dialect khác có nhánh kiểm tra riêng.

`api/src/cli/commands/bootstrap/index.ts` là quy trình khởi tạo runtime:

- chờ database tối đa 5 lần, mỗi lần cách 5 giây;
- nếu `isInstalled()` false, gọi `database/seeds/run.ts` để tạo các bảng hệ thống YAML, sau đó `database/migrations/run.ts` với `latest`, tạo admin mặc định và cập nhật settings/owner;
- nếu đã cài, bỏ qua install nhưng vẫn chạy migration mới nhất;
- đóng database và thoát thành công.

`api/src/database/seeds/run.ts` đọc các YAML seed `01-collections.yaml` đến `15-migrations.yaml`, tạo bảng, kiểu cột, primary key, nullable/default/unique và foreign key. Nó dừng với lỗi `Database is already installed` nếu bảng `directus_collections` đã tồn tại. `api/src/database/migrations/run.ts` đọc migration built-in và `MIGRATIONS_PATH`, đối chiếu bảng `directus_migrations`, chạy từng `up`, ghi version/name và flush cache.

Fixture `qa_categories`/`qa_articles` không thuộc core seed của Directus; đó là dữ liệu lab do `DAMH/scripts/lab-components.sh` tạo qua REST, được mô tả ở các báo cáo 03 và 04. Không nhầm fixture K05 với seed system tables của Directus.

## 6. Giới hạn của phân tích

Phân tích bao phủ backend/API, dashboard, SDK, package dùng chung, database, authentication, authorization, query, relation, Docker và lab runtime. GraphQL, WebSocket, storage driver cụ thể và extension được xác nhận ở mức module/route nhưng không được chạy thành chiến dịch chức năng trong nhiệm vụ này. Không sửa code nghiệp vụ Directus, không build checkout nguồn, không chạy migration/seed mới và không reset volume.
