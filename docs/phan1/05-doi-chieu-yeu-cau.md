# 05 — Đối chiếu yêu cầu Phần 1

## 1. Ma trận đối chiếu

| Yêu cầu Phần 1 | Bằng chứng mã nguồn/tài liệu | Bằng chứng đã chạy | Trạng thái và giới hạn |
|---|---|---|---|
| 1. Phân tích cấu trúc mã nguồn, module và dependency chính của R06 | [`01-phan-tich-he-thong.md`](./01-phan-tich-he-thong.md); `directus/package.json`, `pnpm-workspace.yaml`, `api/package.json`, `app/package.json`, `sdk/package.json`; `api/src/app.ts`, `api/src/server.ts`, `api/src/database/index.ts`, `packages/env/src/constants/defaults.ts` | Đọc manifest, workspace, source tree, Dockerfile và entrypoint; Directus working tree sạch tại HEAD `d3c9a8bb0c0096148c4740ce908e76c24f2413a0` | Đạt ở mức phân tích tĩnh. Không cài lại dependency hoặc build source. |
| 2. Phân tích kiến trúc và luồng dữ liệu của 3–5 nghiệp vụ trọng tâm | [`02-kien-truc-va-luong-du-lieu.md`](./02-kien-truc-va-luong-du-lieu.md); các hàm `createApp`, `authenticate`, `LocalAuthDriver`, `AuthenticationService.login`, `ItemsService.createOne/readByQuery/updateOne/deleteOne`, `processAst`, `validateAccess`, `processPayload`, `RelationsService.createOne` | Đối chiếu route/middleware và chức năng từ mã nguồn; Mermaid thể hiện kiến trúc Directus, ranh giới lab và 5 luồng | Đạt cho 5 nghiệp vụ có bằng chứng. Chức năng GraphQL/WebSocket/storage/extension không được chạy chiến dịch riêng. |
| 3. Xác minh khả năng thiết lập và chạy hệ thống hiện tại hoặc Docker | [`04-bao-cao-xac-minh.md`](./04-bao-cao-xac-minh.md); [`03-huong-dan-cai-dat.md`](./03-huong-dan-cai-dat.md) | `./lab.sh doctor` run `20261012T103055Z-13919`: exit `0`, Docker/Compose/image digest/config/fixture/API/authenticated health PASS; `GET /server/ping` HTTP 200; `pg_isready` accepting; container Directus/PostgreSQL/runner healthy | Đạt cho stack Docker hiện hữu. Source checkout chưa build; image runtime dùng digest và provenance khác SHA source hiện tại. |
| 4. Hướng dẫn cài đặt, cấu hình, build/run và seed data | [`03-huong-dan-cai-dat.md`](./03-huong-dan-cai-dat.md); `Dockerfile`, `docker-entrypoint.cjs`, `api/src/cli/index.ts`, `api/src/cli/commands/bootstrap/index.ts`, `api/src/database/migrations/run.ts`, `api/src/database/seeds/run.ts`, `DAMH/lab.sh`, `DAMH/compose.yaml`, `DAMH/config/lab.env.example` | Hướng dẫn được đối chiếu với lệnh CLI/compose thật; doctor đọc config/image/fixture hiện hành | Đạt về tài liệu tái lập. `pnpm install/build`, bootstrap/migration/seed mới không chạy trong nhiệm vụ này; không ghi chúng là kết quả thành công. |

## 2. Phân biệt trạng thái bằng chứng

| Nhãn | Ý nghĩa trong bộ báo cáo |
|---|---|
| Đã đọc mã | Nhận định được truy vết tới file và hàm/class trong checkout Directus hiện tại. |
| Đã chạy | Có lệnh/output hoặc artefact run cụ thể; ví dụ doctor run `20261012T103055Z-13919`. |
| Chưa xác minh | Có hướng dẫn hoặc code path nhưng chưa thực thi trong nhiệm vụ này. |
| BLOCKED | Chỉ dùng khi dependency thực tế không khả dụng. Lần này Docker/Compose không bị BLOCKED. |

## 3. Đánh giá mức độ sẵn sàng

Bộ Phần 1 sẵn sàng ở mức báo cáo phân tích source + xác minh Docker runtime hiện hữu. Năm file đã tách đúng yêu cầu, có provenance, đường dẫn bằng chứng, sơ đồ Mermaid, hướng dẫn cài đặt/cấu hình/build/run/seed và ma trận đối chiếu.

Không nên ghi trong phần trình bày rằng checkout Directus đã được build từ máy này, migration/seed vừa chạy hoặc toàn bộ CRUD/campaign đã PASS. Những khẳng định đó cần một run mới với Node 22/pnpm 10.27.0, database/volume riêng và artefact tương ứng. Mức sẵn sàng hiện tại phù hợp để nộp Phần 1 với giới hạn đã nêu; nếu giảng viên yêu cầu clean-room build hoặc seed fresh, đó là bước xác minh bổ sung.
