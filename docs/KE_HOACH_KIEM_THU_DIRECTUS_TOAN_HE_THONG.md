> Làm rõ hiệu lực M2 ngày16/11/2026 theo chỉ đạo người dùng và văn bản giảng viên: nghiệm thu **công việc kiểm thử** tách biệt với PASS/FAIL của Directus và chỉ số Verified Coverage. Không yêu cầu sửa Directus hoặc zero FAIL để hoàn thành đồ án; required assertions/FAIL/raw evidence vẫn giữ nguyên. Công thức §6.2 không thay đổi. Sai khác encoding P01 và missing trace/CI/fuzz phải công khai, không sửa dữ liệu để xanh. Xem [review M2](coverage/acceptance/M2-REVIEW-20261116/README.md). Các gate “mandatory PASS” phía dưới chỉ mô tả chất lượng SUT/qualified verification, không tự áp thành nghĩa vụ khắc phục sản phẩm của nhóm QA.

# KẾ HOẠCH KIỂM THỬ DIRECTUS TOÀN HỆ THỐNG

## Hiệu lực phạm vi sau đối chiếu văn bản — 15/11/2026

**Nguồn hiện hành:** [Rà soát đủ 20 phase và scope R06–K05](RA_SOAT_20_PHASE_R06_K05_2026-11-15.md), đối chiếu yeu_cau.pdf §2.1, §4 và K05. Văn bản yêu cầu tập trung luồng cốt lõi/module rủi ro cao, cho phép giới hạn scope; không bắt kiểm thử mọi module/giao thức Directus. Tên file yeu_cau(9).pdf do người dùng nêu chưa được xác minh là cùng binary; hai bản PDF sẵn repo đã đọc có cùng hash b032a7a78a6ea02bb6f5bf52f037c2e06f80cba18bbffef02c2fce39c56cd405 và nội dung liên quan phù hợp.

Regression13 TC01–TC13 trên qa_articles/qa_categories đã được nhóm 11 xác nhận nội bộ ngày 15/11/2026; **không ghi giảng viên phê duyệt subset này**. Giữ TC13 contract FAIL, không sửa expected. Inventory P03–P05 và thiết kế P06 rộng hơn là tài liệu tham khảo/backlog; không tự động là nghĩa vụ triển khai test hay mẫu số coverage đã chọn. Chưa có bằng chứng yêu cầu bổ sung bằng lời bắt buộc toàn hệ thống. Những diễn giải “toàn bộ phải chạy” và gate mở rộng dưới đây là snapshot kế hoạch trước, được điều chỉnh bởi bảng rà soát mới.

Đường K05 khả thi đề xuất: P09 → P10 → P14 → P15 → P18 → P19, tái dùng P00–P08/P02; P11–P13/P16/P17 chỉ thêm khi có chọn scope có lý do. Không xóa phase, inventory hoặc sản phẩm cũ; không chuyển chức năng chưa chọn thành NOT_APPLICABLE. Toàn inventory chưa LOCKED không được dùng làm lý do giả 100% hoặc chặn vô thời hạn subset K05 đã có căn cứ. P09 chưa bắt đầu trong lượt rà soát tài liệu.

---

**Nhóm 11 — R06–K05 — Ngày khảo sát: 15/11/2026 (Asia/Bangkok).**

**Bản chỉnh kế hoạch:** ưu tiên tái sử dụng và ba mốc nghiệm thu; chỉ sửa tài liệu.

## Tóm tắt điều hành

Bản rà soát này ưu tiên **Coverage Baseline trước mở rộng số lượng test**. Giữ nguyên số liệu lịch sử, TC01–TC13 và công thức coverage; 257 ID là tài sản để tái sử dụng. Đã đối chiếu tĩnh cả 257 mục với 44 thiết kế: không thấy trùng hoàn toàn; 16 thiết kế tái dùng một phần, 4 thiết kế cần chỉnh/tách, 24 thiết kế chưa có hành vi tương ứng trong catalog cũ (chi tiết mục 8). Đây không phải kết quả chạy test.

TC42, TC49, TC55 được thu hẹp và tách thêm TC58–TC62 để mỗi hành vi có oracle/verdict riêng. Sau sửa có 49 mục thiết kế bổ sung, không còn gọi cả 44 mục ban đầu là “ca mới đã sẵn sàng”. Không cộng 257 + 13 + 49: phải đếm canonical test ID, alias, phiên bản và tập phạm vi được chọn. Tổng ca thực thi cuối cùng **CHƯA XÁC MINH**.

Ba mốc: **M1 — Coverage Baseline**, **M2 — Automated Testing + CI**, **M3 — Full-Scope Coverage Evidence**. “Full-Scope” chỉ tập phạm vi giảng viên và nhóm đã chốt, gồm cả khoảng trống công khai; không có nghĩa mọi đầu vào Directus. CI static/offline bắt đầu ngay ở M1, smoke sau precondition đủ; không chờ mọi module.

Lộ trình môn học tối thiểu: giữ regression có bằng chứng → kiểm kê toàn hệ thống → chọn Core theo rủi ro → bổ sung một số hành vi ngoài hai collection, ưu tiên auth/quyền, model, file local → raw/guided pilot → CI và báo cáo coverage có mẫu số. Extended mở theo thời gian; Conditional chỉ triển khai khi feature/provider/license và quyết định phạm vi đủ.

### Công việc ưu tiên và phụ thuộc

| Thứ tự | Công việc / người đề xuất | Phụ thuộc | Đầu ra và Definition of Done |
|---|---|---|---|
| 1 | Inventory và Coverage Baseline / Nhân; Lành chốt applicability; Trâm map catalog | Source baseline, manifest và 257 ID đã có | Danh mục chức năng/route/giao thức có nguồn và cờ UNKNOWN; RTM/canonical map; mẫu số theo revision, báo NOT_MEASURED khi thiếu |
| 2, song song 1 | Thiết kế CI static/offline / Lành | Audit interface và secrets | Định nghĩa checks/gate/artifact; ở giai đoạn triển khai có log CI; không cần khởi động mọi module |
| 3 | Tái dùng regression cũ, smoke tối thiểu / Trâm | Actor/fixture/license và môi trường thử đủ | Selection manifest trỏ ID cũ, giữ FAIL lịch sử; report và cleanup có nguồn; không copy test thành ID mới |
| 4 | Pilot Core ngoài hai collection / Trâm + Nhân | M1 đủ inventory/oracle cho nhóm được chọn | Auth/permission, model, file local có ca độc lập và restore; ưu tiên theo mục 4.1 |
| 5 | Contract/fuzz theo nhóm và CI smoke / Nhân + Lành | Pilot Core; CLI/tracecov gate | Raw/guided riêng, report/coverage extractor có kiểm chứng, job fail/blocked/incomplete rõ |
| 6 | Extended và Conditional / cả nhóm theo module | Quyết định phạm vi, baseline feature và budget | Evidence riêng từng transport/module hoặc gap/N/A có quyết định; không trì hoãn bàn giao Core |

Các đầu ra máy đọc được ở mục 6.8 hiện chỉ được **đặc tả trong Markdown**, chưa tạo file/code/workflow. Mục **12.5** chia công việc thành **20 phase P00–P19 cho GPT 6.1 Sol Medium**, có prompt nền, prompt từng phase, phạm vi, dependency, DoD và handoff; chưa thực thi các phase.



## 1. Mục tiêu, phạm vi nhiệm vụ và quy ước

Theo thông tin người dùng cung cấp, giảng viên yêu cầu mở rộng từ hai collection sang toàn hệ thống và chứng minh độ bao phủ. Đây là yêu cầu mới của người dùng, chưa đối chiếu văn bản giảng viên: **CHƯA XÁC MINH nguồn yêu cầu độc lập**. Kế hoạch này bao gồm cả Data Studio theo yêu cầu mới, dù trao đổi trước đó loại giao diện. K05 vẫn là kỹ thuật trọng tâm; REST, GraphQL, Realtime, giao diện và vận hành được đánh giá riêng.

“Kiểm thử toàn hệ thống” được hiểu là kiểm kê mọi phân hệ của bản pin, chọn yêu cầu áp dụng, thiết kế và thực thi các hành vi/rủi ro đã xác định. Không thể duyệt mọi dữ liệu hoặc mọi chuỗi thao tác có thể có. Không hứa “100% Directus”; nếu đạt 100% một chỉ số phải nói rõ tập hữu hạn, phiên bản và tiêu chí.

Chỉ tạo file Markdown này. Không chạy lab, API, campaign, cài package, chỉnh fixture/config/workflow, sửa test, commit hoặc push. Những lệnh trình bày dưới đây là kế hoạch cho giai đoạn triển khai, không phải lệnh đã chạy. Bằng chứng lịch sử giữ nguyên ngày và verdict.

- **ĐÃ XÁC MINH**: quan sát được trong mã/tệp hoặc Git tại lần khảo sát này.
- **LỊCH SỬ**: kết quả trong báo cáo đã lưu; không xác nhận runtime ngày 15/11.
- **ĐỀ XUẤT**: thiết kế cần triển khai sau; không phải tính năng sẵn có của harness.
- **CHƯA XÁC MINH**: thiếu bằng chứng đúng môi trường/phiên bản.
- **NOT_MEASURED**: chưa có số đo và mẫu số hợp lệ.

## 2. Hiện trạng repository và môi trường

### 2.1. Cấu trúc và Git

Workspace có hai repository riêng: `DAMH/` chứa harness, Compose, script, tài liệu và artifacts; `../directus/` chứa monorepo đầy đủ với `api/`, `app/`, `sdk/`, `packages/`, `tests/e2e/`. Không đồng nhất mã nguồn upstream với test do nhóm viết.

Repo DAMH: nhánh `feat/g1-shared-interface`, HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`. Working tree có thay đổi và nhiều tệp chưa track, gồm các tài liệu/harness; đây không phải checkout sạch để tái lập. Không chỉnh hoặc gom các thay đổi đó vào kế hoạch.

Checkout Directus HEAD `8e140f94250834cea0a0fb6eb822cac39ed9faec` khác commit baseline. Không có tag để `describe --exact-match` tại HEAD. Tuy nhiên object baseline tồn tại và đã đọc bằng `git show <baseline>:api/src/app.ts` và `api/package.json`; không checkout/reset. Dùng object baseline để đối chiếu route. Version package `@directus/api=40.0.0` là version package nội bộ, không thay version sản phẩm 12.5.0.

Không thấy `.github/` trong DAMH hoặc workflow YAML trong kiểm kê repo; **chưa có bằng chứng CI GitHub Actions của harness**. Workflow của upstream, nếu có, không chứng minh nhóm đã có CI. Branch protection, Actions trên remote, quyền tài khoản, quota và lịch sử PR: CHƯA XÁC MINH; không truy cập tài khoản ngoài để thay đổi gì.

### 2.2. Baseline đã lưu

Nguồn: [manifest](../manifest/baseline.yaml), [Compose](../compose.yaml), [env mẫu](../config/lab.env.example).

| Thành phần | Giá trị có căn cứ | Giới hạn |
|---|---|---|
| Directus | 12.5.0; source commit `4f77933bf9551cac6b289576078783e189b8f4e3` | Runtime hiện tại CHƯA XÁC MINH |
| Directus image digest | `sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331` | Manifest multiarch; cần ghi image ID/arch thực khi chạy |
| Schemathesis | 4.30.0 | Cần chụp CLI help từ đúng image trước mở rộng |
| Schemathesis digest | `sha256:bb9cecfc9ac4058a15fcf9b505d9d9f972e2dde7c74c4e9289a35922f4cbc0a5` | Chưa chạy lại version ngày khảo sát |
| PostgreSQL | image 16-alpine; báo cáo rà soát ghi runtime lịch sử 16.15 | Không suy patch hiện tại từ major tag |
| PostgreSQL digest | `sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea` | Pin được trong env mẫu |
| Docker/Compose | manifest lịch sử 29.8.1 / v5.5.1 | Host ngày khảo sát CHƯA XÁC MINH |
| Network/volume | `r06-k05_network` / `r06-k05_db_data` | Tên cố định gây xung đột nếu chạy nhiều job |
| API | host loopback 8055; container `http://directus:8055` | Không dùng production/public demo |
| Fixture | 3 category, 12 article, 6 draft/6 published | ID động; map sau seed |
| Actors | admin bootstrap; Editor CRUD; Reader chỉ đọc published, che internal_notes; Anonymous bị chặn | Reader policy phụ thuộc điều kiện license trong lab |
| Config baseline | cache, telemetry, limiter tắt; token TTL 2h | Chưa kiểm hành vi cache/limiter khi bật |
| Dịch vụ bổ sung | Compose chỉ có database/directus/runner | Không có Redis/S3/SMTP/provider bên ngoài trong Compose |

Service runner trong Compose chỉ chờ và healthcheck version. Campaign/suite thực tế được script tạo container tạm `docker_run --rm`. Cần thiết kế CI theo đường thực thi này.

Đã có Python standard-library harness: `designed_cases.py`, `invariants.py`, `contract_checks.py`, `replay_cases.py`, `cost_query.py`; shell điều phối `lab-components.sh`, `lab.sh`, PowerShell wrapper. Có `tests/test_harness.py`, `tests/test_cost_query.py`. Không tìm thấy Postman collection trong tập tệp đã kiểm kê; người dùng có dùng Postman nhưng việc có collection tái lập được trong repo là CHƯA XÁC MINH.

### 2.3. Kết quả lịch sử và trạng thái mở

Nguồn khóa 18/10: [coverage-summary.json](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/coverage-summary.json), [báo cáo cuối kỳ](HoanThanhPlan/09-bao-cao-cuoi-ky.md), [rà soát TC và bảng](HoanThanhPlan/10-ra-soat-hinh-bang-bao-cao.md).

| Đơn vị | Kết quả đã lưu | Không được suy luận |
|---|---|---|
| TC01–TC13 | 12 PASS, 1 FAIL hợp đồng | Không phải một run chung mới sau thêm lựa chọn course |
| Danh mục | 257 ID khác nhau; 184 PASS, 7 FAIL, 1 OPEN, 65 NOT_RUN | Không cộng bộ con 58/118 hoặc số generated examples vào 257 |
| Bộ short | Hai lượt 58/58 PASS | Không thành 116 ca độc lập |
| Bộ assertable | 111 PASS, 7 FAIL / 118 | Không chứng minh 100% hệ thống |
| Invariant | 9 PASS, 2 FAIL | Hai FAIL gồm aggregate và contract candidate |
| Operation nghiệp vụ | 10/10 trong allowlist có positive acceptance | Không phải tổng route Directus |
| Biên / quyền | 33/34 điểm biên PASS; 54/69 luật quyền PASS | Chỉ mẫu số cũ; chưa mở rộng toàn hệ thống |
| Phân vùng | 25/48 lớp có đại diện PASS | Không tự gọi 23 lớp còn lại là NOT_RUN |
| BR cũ | 26/26 có ca thực thi liên quan | Không có nghĩa mọi hành vi BR đều đạt |
| Code coverage Directus | NOT_MEASURED | Unit test harness không thay số đo Directus |

Có các bằng chứng Reader BLOCKED trước đáp ứng license; các run sau có request và PASS. Không ghi đè lịch sử BLOCKED. Campaign raw/guided ba seed 101/202/303 đều chạm 10 operation, runner exit 1 và restore exit 0, dừng max_time. Nhãn INCOMPLETE trong tổng hợp diễn đạt giới hạn tìm kiếm; giữ riêng status công cụ failed, trường complete và stop_reason, không diễn giải complete=true thành đã kiểm hết.

Nhóm bất thường lịch sử: aggregate sai trả 500; POST object trả data object nhưng OAS mô tả array; DELETE 204 ngoài response map; export media type; projection thiếu trường so schema. Chưa đồng nhất chúng thành năm product defect độc lập; giữ trạng thái điều tra OPEN, phân loại contract/product/harness/environment. Không thay raw OAS hoặc expected để làm suite xanh.

## 3. Phạm vi hệ thống và cách xác định tính áp dụng

### 3.1. Inventory REST theo đúng baseline

Đã thấy router baseline mount các họ: auth, graphql, activity, access, assets, collections, comments, dashboards, deployments/webhooks, deployments, extensions, fields, files và files/tus có điều kiện, flows, folders, items, license, notifications, operations, panels, permissions, policies, presets, translations, relations, revisions, roles, schema, server, settings, shares, users, utils, versions; ai, ai/files, mcp, mcp-oauth và metrics có điều kiện. Đây là **họ route**, chưa phải số operation hoặc số module đo coverage. Realtime ở websocket, Studio tại /admin; route nested/method cụ thể phải kiểm kê tiếp.

Inventory triển khai phải lưu: module, transport, method, normalized_path, source_path:line@SHA, feature_flag, permission, license, OAS presence, actor schema, applicability, lý do loại trừ và bằng chứng. Không mặc định endpoint tồn tại chỉ vì docs mới có; cũng không coi thiếu trong OAS actor là N/A. Đối chiếu mount trong app.ts, router con, route động và middleware điều kiện tại commit baseline.

Đường dẫn động phải cụ thể hóa collection thử được duyệt; giữ template route riêng để không đếm nhân vô hạn theo item ID. WebSocket message type, GraphQL query/mutation/subscription và UI flow dùng inventory riêng.

### 3.2. Core, Extended và Conditional

Phân loại là **đề xuất cho bản 12.5.0**, dựa trên route baseline, Compose hiện có, công cụ và bằng chứng lịch sử. Chưa xác minh runtime ngày khảo sát nên presence trong source không đồng nghĩa enabled/deployed. Tầng phạm vi tách khỏi mức rủi ro P1–P4: một lỗi Conditional có thể rất nghiêm trọng nhưng chưa được lên lịch khi thiếu môi trường.

| Tầng | Chức năng / thiết kế ban đầu | Căn cứ và điều kiện nghiệm thu |
|---|---|---|
| Core — nền tảng môn học | Regression Items/query/validation/contract và 257 ID đã chọn; AUTH, RBAC, MODEL, FILES local; SERVER chỉ ping/health/info/quyền đọc | Có route bản pin, PostgreSQL/local API không cần provider ngoài. Auth lifecycle/quản trị/file là phần bổ sung chưa có bằng chứng chạy. Chốt subset ca theo oracle và budget; không bắt chạy mọi 257 ID |
| Extended — chức năng native kế tiếp | Bulk Items, M2M/nested rollback và query mới; Flows, lịch sử/version, insight/preset, schema diff/apply, GraphQL, Studio, shares, comments/notification/translation, import, settings mutation | Source baseline có nhóm chức năng nhưng chưa có suite nhóm. Cần fixture/quyền/profile; Studio cần actor có app access, khác Editor cũ. Những mục đã bật và thầy yêu cầu vẫn thuộc mẫu số áp dụng dù chưa triển khai |
| Conditional — cấu hình/provider/phạm vi cần quyết định | Realtime khi bật profile, extension tùy chỉnh, cache/limiter đang tắt; AI/MCP/deployments; SDK nếu thuộc SUT; SSO/MFA, Redis/S3/email ngoài Compose, nhiều DB, tải và phục hồi sâu | Feature/runtime/license/provider và yêu cầu thầy chưa đủ. Có source route không tự tạo obligation chạy provider thật. Cần decision ID, environment profile, oracle và budget trước đưa vào campaign |

HISTORY/SHARE/SCHEMA và các nhóm Extended chỉ áp dụng khi baseline feature được xác minh; nếu phát sinh license/provider thì ghi dependency và chuyển **công việc** sang Conditional có quyết định, không xóa module khỏi inventory. License Reader hiện là dependency của Core: nếu thiếu license hợp lệ để giữ policy đã chốt thì Core liên quan BLOCKED, không loại sang N/A để tăng coverage.

Trạng thái tính áp dụng: APPLICABLE, NOT_APPLICABLE, UNKNOWN; tách với tầng scope và trạng thái chạy. UNKNOWN phải có gap_id và người giải quyết; N/A chỉ khi có nguồn/quyết định, người xác nhận và ngày. Thiếu điều kiện thực thi một requirement đã áp dụng là BLOCKED. Tạm hoãn Extended do thời gian vẫn báo NOT_RUN; chỉ bỏ khỏi scope nghiệm thu bằng quyết định rõ và vẫn công bố inventory đầy đủ.

M1 kiểm kê **toàn chức năng và mọi transport** bất kể tầng. M2 triển khai Core đã chọn. M3 trình bày độ phủ riêng Core/Extended/Conditional và phần chưa làm của tập phạm vi đã duyệt. Nếu thầy yêu cầu toàn mọi tính năng bật, Extended áp dụng phải được thực hiện hoặc ghi mục tiêu chưa đạt; mốc tối thiểu không được gọi thay cho toàn hệ thống.

## 4. Danh mục phân hệ, rủi ro và điều kiện

Bảng dưới là **22 nhóm công việc đề xuất**, không phải tuyên bố Directus có đúng 22 module. Cột phạm vi chỉ ra chức năng/API; danh mục ca ở Phụ lục A nêu hành vi kiểm cụ thể. “Chưa có suite” là chưa có bằng chứng suite của nhóm, không phủ nhận upstream có unit/e2e test.

| Mã | Chức năng/API | Rủi ro / ưu tiên | Hiện trạng nhóm | Công cụ | Tiền đề và tính áp dụng |
|---|---|---|---|---|---|
| AUTH | Xác thực và phiên — `/auth/*` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Đăng nhập chỉ là bước chuẩn bị; chưa có bộ vòng đời phiên | API Python/Postman | Tài khoản dùng một lần; clock/token TTL kiểm soát; Local auth áp dụng; SSO/MFA cần provider riêng |
| RBAC | Users, Roles, Policies và Access — `/users,/roles,/policies,/permissions,/access` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chỉ có policy Editor/Reader cho hai collection | API Python/Postman | Hai user và hai policy chỉ dùng lab; Áp dụng; cần license hợp lệ nếu chức năng yêu cầu |
| MODEL | Collections và Fields — `/collections,/fields` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Hai collection đã seed; quản trị schema chưa có suite | API Python | Admin; collection qa_sys_model riêng; Áp dụng trên DB tạm |
| ITEM | Items và thao tác hàng loạt — `/items/{collection}` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | CRUD đơn đã có; bulk PATCH/DELETE ngoài campaign | API Python; Schemathesis guided | Collection qa_sys_bulk; 3 item ID động; Áp dụng; semantics transaction phải xác minh |
| QUERY | Query, validation và lỗi — `/items/qa_sys_query` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Bảy query và một phần biên đã có trong 257 ID | API Python; Schemathesis | Fixture riêng có timestamp, decimal, null; không dùng lại oracle qa_articles; Áp dụng; tái dùng 257 ID cho query đã thiết kế |
| REL | Relationships và toàn vẹn — `/relations,/items/qa_sys_*` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Quan hệ M2O/SET NULL đã có; chưa phủ các dạng khác | API Python; stateful | Collection M2M và junction riêng; Áp dụng; không thay quan hệ fixture cũ |
| FILES | Files, Folders, Assets — `/files,/folders,/assets` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite file của nhóm | API Python; Postman multipart | Storage local tạm; PNG 16x16 và file text có hash; mount lưu trữ riêng; Áp dụng local; S3/Azure/GCS cần profile riêng |
| FLOW | Flows và Operations — `/flows,/operations; webhook lab` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite flow của nhóm | API Python; sink HTTP nội bộ | Flow manual và webhook vào sink cục bộ; không gửi dịch vụ thật; Áp dụng; scheduler cần thời gian kiểm soát |
| HISTORY | Activity, Revisions và Versions — `/activity,/revisions,/versions` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có bằng chứng kiểm module lịch sử | API Python | Collection bật tracking/version theo baseline; user riêng; Áp dụng nếu tracking bật; xác minh retention |
| INSIGHT | Dashboards, Panels và Presets — `/dashboards,/panels,/presets` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite; API khác kiểm UI | API Python | Hai user; dashboard/panel/preset tạm; Áp dụng API; render panel thuộc UI |
| SERVER | Settings, Server và license — `/settings,/server/*,/license` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Healthcheck có; admin API chưa có suite | API Python; Schemathesis read-only | Admin; snapshot settings; không thay khóa/license; License test chỉ đọc metadata đã làm sạch |
| SCHEMA | Snapshot, diff và apply — `/schema/*` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite schema quản trị | API Python; so schema chuẩn hóa | DB thử dùng một lần; snapshot trước; admin; Áp dụng DB tạm; không apply lab cũ |
| GQL | GraphQL — `/graphql và schema tương ứng` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Ngoài phạm vi cũ; chưa có suite | Client GraphQL Python; Schemathesis GraphQL sau pilot | Introspection theo actor; GraphQL fixture tương đương REST; Không dùng REST OAS làm schema GraphQL |
| RT | Realtime — `WebSocket REST/GraphQL theo config` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Ngoài phạm vi cũ; chưa có suite | Client WebSocket Python/Node | Bật realtime trong profile mới; hai user; timeout hữu hạn; BLOCKED đến khi profile và auth mode được xác minh |
| UI | Data Studio — `/admin` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Ngoài phạm vi cũ; yêu cầu mới đưa vào kế hoạch | Playwright dự kiến; thủ công có bằng chứng | Browser cùng phiên bản cố định; viewport; user thử; Áp dụng theo yêu cầu mới, thay phạm vi loại UI trước đây |
| EXT | Extensions — `/extensions; endpoint extension tạm` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Có loader trong source; chưa xác minh runtime | API Python; unit Vitest có điều kiện | Extension endpoint tối giản do nhóm kiểm soát trong profile riêng; Không cài extension bên thứ ba trong audit |
| SHARE | Shares — `/shares và luồng xác thực share` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite | API Python | Share một item; thời hạn/giới hạn có nguồn baseline; Áp dụng nếu feature bật |
| COLLAB | Comments, Notifications và Translations — `/comments,/notifications,/translations` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Chưa có suite | API Python | Hai user; item tạm; locale vi/en; SMTP không cần cho in-app; Email ngoài phạm vi in-app cần mail sink |
| IMPORT | Utilities, Import và Export — `/utils/*; export API theo inventory` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Export đã có finding cũ; chưa có import roundtrip | API Python; Postman | CSV/JSON fixture 2 dòng; collection qa_sys_import; Tái dùng ca export cũ; mới kiểm import |
| OPS | Cache, rate limit và khả năng phục hồi — `Middleware; health/metrics; storage/DB` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Cache/rate limiter tắt baseline; chưa đo tải | API Python; công cụ tải sau chọn phiên bản | Profile riêng cache/rate limit; fault chỉ trong DB dùng một lần; Không dùng baseline tắt tính năng làm bằng chứng đạt |
| OPTION | AI, MCP và Deployments — `/ai,/mcp,/deployments; feature flags` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Có route điều kiện trong source baseline; runtime CHƯA XÁC MINH | Client giao thức; sink nội bộ | Xác minh feature flag/license; provider và sink riêng; P4 cho provider/hosting trả phí chưa có |
| SDK | SDK và tương thích client — `sdk/ trong monorepo; REST/auth client` | Chấm từng requirement bằng I/L/C mục 4.1; không gán P1 toàn module | Có mã SDK; nhóm chưa có bằng chứng chạy SDK | Vitest hoặc script SDK dự kiến | SDK tương thích bản pin; chưa cài package; Chỉ áp dụng nếu SDK nằm trong phạm vi thầy chốt |

### 4.1. Xếp ưu tiên theo rủi ro, không theo tên module

Đánh giá từng requirement/ca, không tự gán toàn module P1. Dùng ba thang 1–3:

- I — tác động: 3 = vượt quyền/lộ dữ liệu/mất toàn vẹn quan trọng; 2 = sai chức năng hoặc phục hồi được; 1 = hiển thị/tiện ích giới hạn.
- L — khả năng xảy ra/phơi nhiễm: 3 = có finding tái hiện cùng hành vi; 2 = đường dùng thường xuyên/nhiều actor hoặc mutation rủi ro; 1 = cấu hình ít dùng, chưa có finding tương ứng. Đây là đánh giá thiết kế, không phải xác suất đo được.
- C — mức quan trọng: 3 = nền tảng đúng quyền/dữ liệu hoặc mục tiêu K05; 2 = luồng native bổ sung; 1 = tiện ích/provider tùy chọn chưa nằm trong scope bắt buộc.

S = I + L + C; P1: 8–9, P2: 6–7, P3: 4–5, P4: 3. Bằng chứng yếu phải ghi giả định; không dùng thiếu môi trường để hạ I. Nếu module được thầy chọn bắt buộc thì cập nhật C và revision đánh giá. P1 được xếp trước trong **tầng đủ điều kiện**; không bắt provider tùy chọn chỉ vì I cao. Danh mục TC phụ lục có điểm I/L/C và lý do từng ca; 49 thiết kế sau tách phân bố 11 P1, 25 P2, 11 P3, 2 P4 (chỉ số lượng phân loại thiết kế, không phải kết quả test); P1 lịch sử của TC01–TC13 giữ như metadata cũ, không phải tái chấm.


## 5. Gap Analysis TC01–TC13

**Giữ nguyên mã theo tài liệu rà soát Word**, không lấy thứ tự hàng trong E.3 Markdown để đổi mã. E.3 xếp CRUD category trước, còn TC01 trong rà soát là S1 CRUD article. Đây là khác biệt trình bày cần giữ bảng alias khi cập nhật báo cáo.

| TC | ID nguồn | Nội dung và kết quả lịch sử | Hành vi gộp / thiếu |
|---|---|---|---|
| TC01 | S1 | CRUD article, PATCH giữ field, delete/read-back — PASS | Nhiều request; chưa có bulk/transaction |
| TC02 | S2 | Filter published đúng 6 fixture — PASS | Một điều kiện filter; không phủ mọi toán tử |
| TC03 | S3 | Sort title,id; offset 0/3; projection — PASS | Gộp sort/phân trang; chưa đủ page/limit boundary |
| TC04 | S4 | Reader đọc draft bị 403, có control — PASS | Một policy/actor/row condition |
| TC05 | S5 | Reader xin internal_notes bị 403 — PASS | Assertion hiện chấp nhận deny hoặc field bị loại; chưa bắt chặt mọi nhánh |
| TC06 | S6 | Reader PATCH bị từ chối; Editor read-back không đổi — PASS | Gộp negative quyền và bảo toàn trạng thái |
| TC07 | P3-ST-01 | CRUD category — PASS | Chuỗi nhiều request; không tương đương test mọi quan hệ |
| TC08 | P3-AUTHZ-DR-047 | Anonymous GET list bị 403; control Editor 200 — PASS | Không kiểm lifecycle auth |
| TC09 | P3-SCORE-POST-MINUS1 | score=-1, 400 validation, không tạo row — PASS | Một điểm biên POST |
| TC10 | P3-SCORE-POST-0 | score=0 tạo/đọc đúng — PASS | Một điểm biên POST |
| TC11 | P3-SCORE-POST-5 | score=5 tạo/đọc đúng — PASS | Một điểm biên POST |
| TC12 | P3-SCORE-POST-6 | score=6, 400 validation, không tạo row — PASS | Một điểm biên POST |
| TC13 | P3-CONTRACT-QA_ARTICLES-OBJECT | POST object: business PASS, contract FAIL | Một ca có hai chiều verdict; không sửa expected |

Nguồn thực thi: S1–S6 trong evidence/p8-20261018-scenarios/scenario-report.json; P3 trong p8-20261018-assertable/designed-report.json, riêng TC08 ở p8-20261018-short-r2. Các thư mục evidence cùng nằm dưới HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/. Không coi một tên ca trong catalog NOT_RUN là kết quả thực thi; dùng execution index và report.

Có thể tách về sau: TC01 create/read/PATCH giữ field/delete, TC03 sort/pagination/projection, TC06 deny/read-back, TC13 business/contract. Trước mắt dùng subcheck định danh TC01.C1… và giữ parent verdict; khi thực sự tạo ca độc lập thì cấp ID mới từ số tiếp theo chưa dùng. Không tạo nhiều ca mới từ cùng một historical run rồi cộng số lượng; không đánh lại TC01–TC13.

Đối chiếu tĩnh lần này ở mục 8 đã phân loại đủ 44 thiết kế với 257 ID. Trước triển khai, khóa canonical map theo khóa (module, actor/policy, method/path, input partition, precondition, oracle). Nếu trùng hoàn toàn, gắn alias và tái sử dụng; nếu khác giao thức/quan hệ/module thì ghi khác biệt. Danh mục phụ lục ưu tiên tái sử dụng thay vì lặp CRUD đơn, score, basic query, SET NULL và export vốn đã có. TC42/49/55 đã được tách ở bản chỉnh này; các delta khác chỉ tách tiếp khi inventory cho thấy cần oracle/verdict độc lập, cập nhật số lượng có truy vết.

## 6. Phương pháp đo coverage và trạng thái

### 6.1. Tập mẫu số và phiên bản

Mỗi baseline coverage gồm SUT commit/image ID/arch, schema hash theo actor, fixture/config hash đã bỏ secret, inventory revision, test catalog revision, run_id và môi trường. Mẫu số khóa trước campaign. Thay đổi inventory sinh revision mới; không xóa operation khó kiểm khỏi mẫu số để tăng tỷ lệ. Báo cả tổng phát hiện, áp dụng, N/A, chưa xác minh tính áp dụng. Mẫu số chưa chốt: NOT_MEASURED, không ghi 0%.

### 6.2. Requirement Coverage

Gọi R là tập requirement áp dụng đã review; D là yêu cầu có ca với expected đủ nguồn; E là yêu cầu có ít nhất một test thực thi đánh giá được oracle; V là yêu cầu có mọi test bắt buộc mới nhất PASS, không còn BLOCKED/NOT_RUN/INCOMPLETE/FAIL. Một request gửi được nhưng không kiểm được oracle không vào E.

- Phủ thiết kế = |D| / |R| × 100%.
- Phủ thực thi = |E| / |R| × 100%.
- Phủ xác nhận đạt = |V| / |R| × 100%.
- Chưa được thực thi = |R \ E|; liệt kê ID và nguyên nhân.
- Yêu cầu có test chỉ bị BLOCKED không được tính đã thực thi; FAIL có thực thi được tính E, không vào V.
- Một TC phủ nhiều requirement được đếm theo tập ID, không nhân số request. R không lấy từ số endpoint hoặc số test.

Hiện toàn hệ thống R/D/E/V: NOT_MEASURED. 26 BR cũ giữ như một baseline hẹp, không thay thế R mới.

### 6.3. API Operation Coverage

Xuất OAS bằng admin phù hợp và actor schema riêng. Không dùng schema editor hiện có như toàn REST. Giữ raw bất biến, hash, nội dung metadata và allowlist. Gọi O là hợp các method+path REST áp dụng từ source baseline và OAS, đã giải quyết khác biệt. Những route không có OAS vẫn thuộc O nếu áp dụng; bổ sung contract có nguồn hoặc đánh dấu gap OAS.

- Specification coverage = số operation O có hợp đồng đủ dùng / |O|.
- Hit coverage = số operation có request/response chứng minh dispatch tới operation / |O|.
- Positive acceptance = số operation có ca thành công đúng nghiệp vụ và read-back nếu phù hợp / |O|.
- Negative/authorization coverage báo riêng theo ma trận operation × actor × rule áp dụng.
- Auth middleware trả lỗi trước route không tự chứng minh operation đã hit; kết quả từ chối vẫn là bằng chứng của luật quyền tương ứng.
- Normalize query ngoài path, giữ HTTP method, thay ID cụ thể bằng template; không gộp GET list với GET detail, không đếm HEAD/OPTIONS nếu không có requirement áp dụng.
- Cần export danh sách chưa hit/chưa positive, route thiếu OAS và OAS không có route, không chỉ tỷ lệ.

Mẫu số toàn REST: NOT_MEASURED. 10/10 cũ chỉ cho allowlist hai collection.

### 6.4. Module Coverage

M là tập module áp dụng được khóa sau audit, không mặc định 22 nhóm ở mục 4 là chuẩn sản phẩm. Mapped coverage = module có requirement/test / |M|; touched coverage = module có một test thực thi / |M|. Qualified coverage = module đã chạy hết ca bắt buộc theo DoD module, đủ positive/negative/quyền/trạng thái/integration áp dụng, không còn thiếu bằng chứng / |M|. Báo thêm module có FAIL; module được kiểm đủ vẫn có thể có lỗi, không gọi đó là “đạt”. Module acceptance yêu cầu mandatory PASS và xử lý defect theo mục 15. Các chỉ số hiện NOT_MEASURED.

### 6.5. Code Coverage

Source baseline có script api test:coverage = vitest run --coverage và @vitest/coverage-v8. Khả thi cho unit/integration đúng source baseline khi build dependencies và provider được xác minh; xuất statement/line/function/branch, exclude generated/dist/dependency có lý do. Không chạy trên checkout HEAD khác baseline rồi gắn kết quả cho image 12.5.0.

Đo black-box campaign trên image hiện có chưa được instrument: NOT_MEASURED. Đề xuất profile build instrumented từ baseline, sourcemap đúng TypeScript và Node V8 coverage; kiểm pilot một route đã biết trước khi gom coverage. V8 raw coverage cần ánh xạ/source-map và chuyển định dạng phù hợp; không mặc định chỉ bật env là có branch coverage hợp lệ. So behavior control với image pin. Tách test upstream, harness và campaign; merge chỉ cùng build/source/include rules. Nếu không dựng profile được, báo lý do và giữ giới hạn code coverage, dùng RTM/operation coverage thay bằng chứng chức năng chứ không gọi là code coverage.

### 6.6. Schema/Fuzzing Coverage

Đã có artifact coverage version 1.0, tracecov_version 0.25.2, gồm summary, operations, parameters, keywords, responses, unexpected_responses; có state partial/miss. Script local dùng --coverage-format và --coverage-report-json-path. Đây là **bằng chứng pipeline lịch sử có file coverage**, chưa chứng minh mọi flag là tùy chọn chuẩn upstream 4.30.0: source CLI upstream tag đã đọc không thể hiện các flag coverage ở entrypoint. Phải kiểm CLI help, image identity và nguồn tích hợp tracecov trước tái lập; không tự thêm/bỏ option để hợp thức kết quả.

Đóng băng tập parameter location/name, schema pointer/keyword và response status+media type từ raw schema; báo covered/partial/miss theo semantics của công cụ đã xác minh. Báo riêng reached và violated cho response keyword; violated không được gọi là PASS. Đối chiếu report với vài request mẫu để kiểm tính đúng extractor. Không cộng phần trăm giữa schema actor hoặc raw/guided khác mẫu số; nếu union, dùng khóa canonical gắn schema hash và quy tắc merge đã review.

Generated examples, request mục tiêu, request setup/cleanup, check failures, grouped failures và defect độc lập là các đơn vị khác nhau. Generated không phải độ phủ. Campaign max_time luôn có completion_reason riêng; dù đã hit toàn O vẫn chưa duyệt hết input/state. Báo status công cụ và mức hoàn tất kế hoạch riêng.

### 6.7. Quy định trạng thái

| Trạng thái | Quy tắc |
|---|---|
| PASS | Mọi assertion bắt buộc của ca đã kiểm và đạt; cleanup được xác minh |
| FAIL | Có actual vi phạm expected đã có nguồn; không tự kết luận root cause là Directus |
| BLOCKED | Tiền điều kiện/license/provider/oracle chưa đủ nên chưa đánh giá được mục tiêu |
| NOT_RUN | Đã thiết kế nhưng chưa bắt đầu thực thi |
| INCOMPLETE | Đã bắt đầu nhưng timeout/hủy/mất bằng chứng khiến chưa xong phạm vi |
| NOT_APPLICABLE | Không áp dụng với lý do và quyết định có nguồn; không dùng thay BLOCKED |

Giữ thêm business_verdict, contract_verdict, execution_status, tool_status, stop_reason, cleanup_status, infrastructure_status và finding_id. FAIL và INCOMPLETE có thể đồng thời được mô tả ở các chiều khác nhau; không làm mất FAIL khi campaign hết giờ. OPEN cũ là trạng thái chưa chốt oracle/finding, giữ nguyên dữ liệu gốc; ánh xạ sang BLOCKED ở execution plan nếu thiếu oracle và ghi Notes=legacy OPEN.

### 6.8. Đặc tả đầu ra máy đọc được cho Coverage Baseline (ưu tiên cao nhất)

Đề xuất bộ JSON/JSONL dưới `artifacts/baselines/<baseline_id>/` và `artifacts/runs/<run_id>/`; **chưa tạo các file này**. JSON Schema cho từng loại là công việc M1 khi được giao triển khai, version hóa cùng inventory. Không chỉ xuất CSV bảng Markdown vì cần quan hệ nhiều–nhiều và bằng chứng chuẩn hóa.

| Đầu ra dự kiến | Trường bắt buộc / khóa | Quan hệ và mục đích |
|---|---|---|
| baseline-manifest.json | schema_version, baseline_id, inventory_revision, sut_commit, image_digest, image_id, architecture, config_profile, config_hash_sanitized, actor_schema_hashes, catalog_revision, source_refs, generated_at | Null + gap_id nếu chưa xác minh; không chứa env/token thật |
| system-inventory.jsonl | inventory_id, module_id, capability_id, transport, method, path_template hoặc protocol_operation, feature_flag, deployed_state, scope_tier, applicability, decision_id, source_refs, gap_ids | Một capability có nhiều operation; REST/GRAPHQL/WEBSOCKET/UI/CLI/SCHEDULER/INTEGRATION được kiểm kê riêng, không coi thiếu REST route là thiếu chức năng |
| requirements.jsonl | requirement_id, inventory_ids[], statement, actor_policy, preconditions, oracle_ref, mandatory, risk_impact, risk_likelihood, risk_criticality, priority, scope_tier, applicability, decision_id | Tập R xác định từ requirement áp dụng của revision đã duyệt; chưa đủ oracle vẫn giữ gap, không biến N/A |
| test-catalog.jsonl | canonical_test_id, version, aliases[], legacy_ids[], requirement_ids[], operation_ids[], test_type, input_partition, fixture_profile, oracle_refs[], automation_state, owner, prerequisites[], cleanup_ref | TC/P3 là alias nếu cùng mục tiêu/oracle. Fork thiết kế khác module/giao thức có canonical mới, derived_from cũ; không copy verdict |
| rtm-links.jsonl | requirement_id, canonical_test_id, test_version, coverage_role, mandatory_for_requirement, mapping_rationale | coverage_role = DIRECT hoặc SUPPORTING; setup/control tái dùng không được tính đã có ca DIRECT cho requirement mới |
| executions.jsonl | run_id, baseline_id, canonical_test_id, test_version, execution_status, business_verdict, contract_verdict, started_at, finished_at, operation_evidence[], assertion_results[], evidence_refs[], cleanup_status, infrastructure_status | Bằng chứng lịch sử gắn baseline/run gốc. Trường operation_evidence nêu actor, dispatch_verified, positive_acceptance, request/response refs |
| decisions.jsonl / gaps.jsonl | decision_id hoặc gap_id, target_ids[], reason, source_refs, owner, status, approved_by, date, due_milestone | Phân biệt đề xuất quyết định và đã xác nhận; nguồn giảng viên CHƯA XÁC MINH phải giữ rõ |
| coverage-summary.json | baseline_id, selection_id, denominator_revision, filters, unit, applicable_count, unknown_count, excluded_ids[], numerator_ids[], missing_ids[], metrics, evidence_refs | Không chỉ lưu tỷ lệ; phải tái tính được tập tử/mẫu, thống kê unresolved và từng tầng/transport |

`deployed_state` chỉ dùng ENABLED_VERIFIED, DISABLED_VERIFIED, UNKNOWN. `source_refs` gồm path@SHA hoặc artifact+hash; URI schema pointer cho OAS. Khóa operation REST là method + normalized_path + route variant/feature profile cần thiết, không có item ID thực hoặc query. Inventory ID và requirement ID ổn định, không lấy số hàng làm khóa.

Ví dụ cấu trúc **minh họa, không phải số liệu đo**:

```json
{
  "schema_version": "1",
  "baseline_id": "PENDING",
  "inventory_revision": "draft",
  "unit": "REST_OPERATION",
  "scope_tier": "CORE",
  "applicable_count": null,
  "unknown_count": null,
  "metrics": {"hit_coverage": "NOT_MEASURED", "positive_acceptance": "NOT_MEASURED"},
  "numerator_ids": [],
  "missing_ids": [],
  "gap_ids": ["GAP-INVENTORY-NOT-LOCKED"]
}
```

Quy tắc tự động hóa dự kiến:

1. Kiểm schema/enum, ID duy nhất, reference tồn tại; mọi requirement có source/oracle hoặc gap; mọi N/A có decision đã xác nhận. Dùng JSON null cho count chưa biết; danh sách rỗng trong draft không có nghĩa không còn thiếu.
2. Khóa scope và applicability theo baseline revision; đếm UNKNOWN riêng. Không tính phần trăm “toàn hệ thống” khi toàn inventory còn UNKNOWN ảnh hưởng mẫu số. Có thể tính cho subset khóa hoàn chỉnh với nhãn subset rõ.
3. Resolve alias về canonical ID, khử trùng theo (canonical_test_id, test_version, baseline_id). Join RTM DIRECT và execution cùng version/baseline; SUPPORTING không tăng requirement coverage.
4. Giữ mọi lần chạy. Summary nghiệm thu dùng selection manifest và quy tắc chọn run trước chiến dịch; không chọn tùy ý lượt PASS cuối rồi bỏ FAIL không giải thích. Retry/flaky có cờ riêng; historical evidence không nâng thành execution baseline mới.
5. Tính tập D/E/V và O bằng công thức mục 6.2–6.4; operation middleware-denied không vào dispatch hit. Sinh missing requirement/operation/module IDs và lý do.
6. Tách denominator code/schema/protocol/module; không gộp tỷ lệ. Xuất metrics NOT_MEASURED kèm gap khi thiếu raw data/tracecov semantics.
7. DoD công cụ coverage ở M1/M2: lấy mẫu manual một requirement nhiều TC, một TC nhiều requirement, một alias P3/TC, một FAIL, một BLOCKED và một route không OAS; kết quả tập ID và tổng tự động phải khớp kiểm tay. Đây là điều kiện kiểm chứng tương lai, chưa chạy trong nhiệm vụ tài liệu.


## 7. RTM và thiết kế ca

Mỗi requirement mới có ID SYS-<MODULE>-NN, nguồn đặc tả/source baseline và actor/condition rõ. RTM ở Phụ lục B là **mẫu kế hoạch đã điền cho danh mục khởi đầu**, không phải coverage đã đo. Ưu tiên theo I/L/C mục 4.1; scope tier độc lập với rủi ro. Metadata priority cũ không bị viết lại. Cần mở rộng requirement theo inventory mọi route trước khi khóa mẫu số.

Các cột giữ đúng hợp đồng:
Requirement ID | Module | Requirement | Risk | Priority | Test Case ID | Test Type | Automation | Execution Status | Evidence | Notes.

Ca cũ dùng LEGACY-TCxx như khóa truy vết tạm khi chưa đối chiếu toàn bộ UR/BR/AC, không coi khóa tạm là yêu cầu mới. Trước khóa RTM, map về UR/BR/AC gốc và tách requirement thực. Evidence của TC cũ xem mục 5; Evidence ca mới “chưa có”.


Bảng RTM legacy và thiết kế bổ sung chuyển sang **Phụ lục B**. Mẫu máy đọc được và quy tắc DIRECT/SUPPORTING ở mục 6.8 là đầu ra ưu tiên M1.

## 8. Kết quả đối chiếu 257 ID và 44 thiết kế ban đầu

Đã đọc catalog JSON (257 ID duy nhất; 17 group) theo actor, method/path, input partition, oracle và các thiết kế trong tài liệu; đây là **đối chiếu tĩnh**, không chạy test/harness. Tập cũ gồm 2 authentication, 59 authorization, 10 positive-operation, 3 stateful, 3 robustness, 8 contract, 36 pairwise-reference; còn lại field/query/boundary. Authentication cũ chỉ có GET /users/me control/token sai, không có login password/refresh/logout. Query/relation cũ là M2O qa_articles–qa_categories, không có M2M. Không thấy suite files/flows/GraphQL/UI/provider trong 257 ID.

Định nghĩa phân loại: TRÙNG TOÀN PHẦN = cùng mục tiêu/actor/transport/input/oracle, dùng canonical cũ; TÁI DÙNG NGUYÊN = hiện vật cũ đáp ứng đủ requirement, không cần code/assertion mới; TÁI DÙNG MỘT PHẦN = chỉ setup/control/oracle con được tái sử dụng, vẫn cần delta; SỬA/TÁCH = thiết kế hiện tại cần đổi để verdict rõ; MỚI THEO CATALOG = không có hành vi tương ứng trong **257 ID**, chưa phải kết luận không có test upstream.

| TC gốc | Phân loại | ID/nguồn cũ có thể tái dùng | Delta hoặc lý do |
|---|---|---|---|
| TC14 | SỬA/TÁCH | P3-AUTH-CONTROL; P3-AUTH-INVALID | Tái dùng control users/me và lỗi auth; chưa có refresh/logout. Giữ chuỗi trạng thái liên quan, subcheck refresh/logout riêng; không suy revoke access JWT ngay. |
| TC15 | MỚI THEO CATALOG | Không có ID tương ứng | Sai mật khẩu không cấp phiên; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC16 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-024, 025, 028, 032, 033 | Tái dùng oracle row/field read và fixture; cần hai policy/user mới và expected union có nguồn. |
| TC17 | TÁI DÙNG MỘT PHẦN | P3-AUTH-CONTROL; P3-AUTHZ-DR-039 | Control định danh và deny/read-back tái dùng; write users/role/policy là hành vi mới, cần oracle riêng. |
| TC18 | MỚI THEO CATALOG | Không có ID tương ứng | Vòng đời collection và field; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC19 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-044, 045 | Tái dùng kiểm deny + admin read-back; fields/collections khác quyền ghi item, không kế thừa verdict. |
| TC20 | TÁI DÙNG MỘT PHẦN | P3-OP-04; P3-ST-02 | Tái dùng snapshot/PATCH/read-back; bulk list path và tập ID đích là delta mới. |
| TC21 | TÁI DÙNG MỘT PHẦN | P3-OP-05; P3-ST-02 | Tái dùng absence/cleanup; bulk DELETE và item ngoài tập đích cần oracle mới. |
| TC22 | TÁI DÙNG MỘT PHẦN | P3-QUERY-NESTED; P3-QUERY-SORT-SCORE; P3-PW-01–36 | Tái dùng query fixture/sort oracle, không copy 36 ca; M2M join và tập tag mới cần fixture/oracle riêng. |
| TC23 | MỚI THEO CATALOG | Không có ID tương ứng | Payload JSON hỏng cho bulk mới; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC24 | TÁI DÙNG MỘT PHẦN | P3-CATEGORY-POST-NESTED-CREATE; P3-ST-03 | Tái dùng setup/cleanup quan hệ; M2O/SET NULL không chứng minh M2M junction. Ca nested cũ còn OPEN không thành oracle đạt. |
| TC25 | TÁI DÙNG MỘT PHẦN | P3-CATEGORY-POST-INVALID; P3-CATEGORY-POST-NESTED-CREATE; P3-ST-02 | Tái dùng snapshot và foreign-key control; atomic nested rollback chưa có expected chốt, BLOCKED nếu thiếu contract. |
| TC26 | MỚI THEO CATALOG | Không có ID tương ứng | Upload và download bảo toàn nội dung; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC27 | MỚI THEO CATALOG | Không có ID tương ứng | Asset riêng tư không lộ qua biến đổi; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC28 | MỚI THEO CATALOG | Không có ID tương ứng | Flow có nhánh điều kiện; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC29 | MỚI THEO CATALOG | Không có ID tương ứng | Nhánh reject khi operation lỗi; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC30 | MỚI THEO CATALOG | Không có ID tương ứng | Revision truy vết sửa dữ liệu; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC31 | MỚI THEO CATALOG | Không có ID tương ứng | Version không đổi bản chính trước promote; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC32 | MỚI THEO CATALOG | Không có ID tương ứng | Dashboard và panel qua API; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC33 | MỚI THEO CATALOG | Không có ID tương ứng | Preset cá nhân được cách ly; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC34 | MỚI THEO CATALOG | Không có ID tương ứng | Giới hạn thông tin server công khai; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC35 | MỚI THEO CATALOG | Không có ID tương ứng | Thay setting thử rồi khôi phục; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC36 | MỚI THEO CATALOG | Không có ID tương ứng | Diff rỗng khi schema không đổi; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC37 | MỚI THEO CATALOG | Không có ID tương ứng | Apply thay đổi schema trong DB tạm; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC38 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-032, 033 | Tái dùng dữ liệu và yêu cầu field kín; GraphQL introspection/errors khác REST, cần client/assertion mới. |
| TC39 | TÁI DÙNG MỘT PHẦN | P3-ST-02; P3-OP-02, 04 | Tái dùng payload/read-back/cleanup; mutation GraphQL là execution độc lập. |
| TC40 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-024, 025, 028 | Tái dùng policy và tập dữ liệu; event subscription/payload/time window hoàn toàn cần assertion giao thức mới. |
| TC41 | TÁI DÙNG MỘT PHẦN | P3-AUTH-INVALID; P3-AUTH-CONTROL | Tái dùng nguồn token invalid/control, không tái dùng status REST làm oracle WebSocket. |
| TC42 | SỬA/TÁCH | P3-ST-02; P3-OP-02–05 | Giữ TC42 cho login Studio; CRUD UI chuyển TC58. Chỉ tái dùng data/read-back API, không coi API PASS là UI PASS. |
| TC43 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-032, 039 | Tái dùng quyền read/deny; cần actor có app access mới, UI element và route guard assertion. |
| TC44 | MỚI THEO CATALOG | Không có ID tương ứng | Endpoint extension có kiểm quyền; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC45 | MỚI THEO CATALOG | Không có ID tương ứng | Extension lỗi không phá endpoint lõi; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC46 | MỚI THEO CATALOG | Không có ID tương ứng | Share chỉ truy cập item được chia sẻ; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC47 | MỚI THEO CATALOG | Không có ID tương ứng | Share hết hạn bị chặn; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC48 | MỚI THEO CATALOG | Không có ID tương ứng | Comment Unicode gắn đúng item; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC49 | SỬA/TÁCH | Không có notification/translation tương ứng | Giữ TC49 notification isolation; translation locale thành TC59; oracle và verdict riêng. |
| TC50 | MỚI THEO CATALOG | Không có ID tương ứng | Import CSV vào collection riêng; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC51 | TÁI DÙNG MỘT PHẦN | P3-AUTHZ-DR-036, 037, 039; P3-INTERNAL_NOTES-POST-TEXT | Tái dùng forbidden-field/payload/control; import/parser và atomicity là delta, không kế thừa verdict. |
| TC52 | MỚI THEO CATALOG | Không có ID tương ứng | Cache tôn trọng thay đổi quyền; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC53 | MỚI THEO CATALOG | Không có ID tương ứng | Rate limit và phục hồi sau cửa sổ; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC54 | MỚI THEO CATALOG | Không có ID tương ứng | MCP không đọc dữ liệu ngoài policy; khác tài nguyên/giao thức/mục tiêu của hai collection cũ; dùng helper API chung nếu phù hợp nhưng cần oracle và evidence mới. |
| TC55 | SỬA/TÁCH | Không có AI/deployment tương ứng | Giữ TC55 AI success; thêm TC60 AI error, TC61 deployment success, TC62 deployment error; conditional độc lập. |
| TC56 | TÁI DÙNG MỘT PHẦN | P3-AUTH-CONTROL; P3-OP-03 | Tái dùng control/read fixture; SDK session sequence chưa có suite, không tái dùng execution REST. |
| TC57 | TÁI DÙNG MỘT PHẦN | P3-AUTH-INVALID; P3-AUTHZ-DR-033 | Tái dùng kích thích lỗi/quyền; SDK exception mapping và recovery cần assertion mới. |

Kết quả theo **44 thiết kế gốc**, mỗi hàng chỉ thuộc một nhóm: **0 trùng toàn phần; 0 tái dùng nguyên; 16 tái dùng một phần; 4 cần sửa/tách; 24 mới theo catalog**. Nhóm sửa có thể dùng helper/control cũ như TC14/TC42 nhưng không đếm lại vào nhóm 16. “Không trùng toàn phần” không cho phép viết lại helper hay catalog cũ.

> **Đính chính P06 (15/11/2026):** Mapping có kiểm field/oracle ở [catalog P06](coverage/catalog/README.md) và [discrepancy log](coverage/catalog/discrepancies.md). P3-INTERNAL_NOTES-POST-TEXT là Editor roundtrip, không phải forbidden-field oracle; DR-044/045 là quyền ghi category, chỉ SUPPORTING cho schema admin. Nguồn CRUD API của hàng TC42 thuộc phần TC58 sau tách, không trực tiếp kiểm login Studio. Giữ các tổng phân loại 44 hàng ở đây là lịch sử thiết kế, không phải số canonical/execution đã chốt.

### 8.1. Tái dùng catalog trước khi viết thêm

| Nhu cầu kế hoạch | Tài sản cũ ưu tiên | Cách dùng / phần cần hoàn thiện |
|---|---|---|
| TC01–TC13, CRUD/score/permission/contract demo | S1–S6; P3-ST-01; P3-AUTHZ-DR-047; P3-SCORE-POST-MINUS1/0/5/6; P3-CONTRACT-QA_ARTICLES-OBJECT | Giữ alias và historical run; không tạo TC mới vì đổi tên |
| Query cơ bản/biên | P3-QUERY-*, P3-PW-01–36 | Chọn requirement còn thiếu và ID NOT_RUN/OPEN đúng nguồn; không tạo lại 36+9; pairwise 9 là subset |
| Quan hệ M2O/null/invalid/SET NULL | P3-CATEGORY-*, P3-ST-03 | Tái dùng nguyên khi requirement chính là hành vi cũ; M2M/rollback vẫn mới |
| Aggregate regression | P3-ROBUST-AGG-FOO/EMPTY/COUNT | Giữ lỗi candidate 500 và control; không tạo bản “aggregate mới” trùng |
| Export/projection/POST object-array | 8 P3-CONTRACT-* | Tái dùng report/oracle, giữ FAIL; không đổi raw OAS |
| Field validation | Các group field-* trong catalog | Chọn có nguồn expected; O-OPEN không tự thành test executable/PASS |
| Quyền item/field | 59 ID authorization | Tái dùng DIRECT cho đúng requirement cũ; chỉ SUPPORTING khi chuyển GraphQL/WS/UI hoặc endpoint quản trị |

“Sửa” ở đây là **đề xuất sửa thiết kế/harness ở giai đoạn sau**: TC14 cần expected vòng đời token theo source; TC42/49/55 tách; nhiều ca partial cần fixture/assertion mới. Không có sửa code, expected lịch sử hoặc trạng thái catalog trong nhiệm vụ này.

### 8.2. Tách ca và quy tắc đếm

| Thiết kế cũ | Giữ ID hiện tại cho mục tiêu | ID bổ sung và oracle độc lập |
|---|---|---|
| TC42 login + CRUD Studio | TC42 chỉ login/session UI | TC58 CRUD UI trên phiên đã có; login được chuẩn bị riêng, thất bại setup = BLOCKED CRUD |
| TC49 notification + translation | TC49 cách ly notification giữa hai user | TC59 roundtrip bản dịch vi/en; notification fail không định verdict translation |
| TC55 AI + deployments, success + error | TC55 AI success với sink thử | TC60 AI error; TC61 deployment success; TC62 deployment error; mỗi ca có provider/dependency/verdict riêng |

Các ID này chưa có execution lịch sử nên có thể thu hẹp thiết kế mà không đổi TC01–TC13 hoặc report cũ. Ghi derived_from TC42/49/55 và version mới trong canonical map. Requirement cũ SYS-UI-01, SYS-COLLAB-02, SYS-OPTION-02 được thu hẹp tương ứng; requirement mới ở phụ lục A/RTM B. Không đếm parent “đã tách” như thêm một ca ngoài các ca con.

Các chuỗi TC14 refresh/logout, TC26 upload/download, TC58 CRUD vẫn giữ vì kiểm cùng vòng đời/tài nguyên và cần hậu điều kiện. Mỗi bước có subcheck; setup fail = BLOCKED downstream. TC30 thu hẹp truy vết revision, quyền user khác là gap riêng cần RTM trước khi cấp TC, tránh gộp hai verdict. Những ca khác có control positive/negative cho cùng một luật không tự tách chỉ để tăng số.

Sau tách có **49 mục thiết kế TC14–TC62** (44 gốc + 5 mục ròng do tách), đều NOT_RUN/chưa triển khai. 13 legacy giữ nguyên; “62” chỉ là số nhãn TC trong thiết kế hiện tại, **không phải 62 ca độc lập đã triển khai hoặc tổng test dự án**. Tổng canonical của toàn dự án chưa chốt; có overlap P3/TC legacy và reuse. Số ca thực thi MVP phải lấy selection manifest sau M1, không lấy 257 + 62.

Chi tiết ca ở [Phụ lục A](#phụ-lục-a-danh-mục-test-case-chi-tiết); RTM đọc được ở Phụ lục B, hợp đồng dữ liệu mục 6.8.


## 9. Kế hoạch mở rộng Schemathesis

### 9.1. Từ export tới inventory

Nhân phụ trách exporter/schema; Lành duyệt allowlist/admin actor và môi trường; Trâm dựng fixture/oracle. Harness cũ export actor qua GET /server/specs/oas nhưng campaign chỉ chọn 10 operation. Cần exporter riêng cho admin REST, lưu raw theo actor, đối chiếu inventory source trước chạy. Không dùng token admin cho mọi campaign: chỉ setup/admin group khi cần, phần item dùng actor hạn quyền. Luật cũ chỉ gửi ca quyền có chủ đích khi operation có trong schema Reader phải được rà soát và điều chỉnh có chủ đích cho negative admin-route suite theo phạm vi mới; kế hoạch này chưa sửa luật/script hay gửi request.

Mỗi nhóm có module_id, schema_raw_hash, selected_operations, actor, fixture_map, positive_examples, cleanup_plan và budget. Route không có contract không đưa vào fuzz mù: thiết kế ca chức năng riêng và ghi contract gap. Mỗi nhóm seed riêng trên DB tạm hoặc chạy tuần tự có restore.

### 9.2. Raw, guided và liên kết trạng thái

Raw chọn operation nhưng không thay request/response contract. Guided là bản sao độc lập thêm ví dụ hợp lệ, ID từ POST response, auth/setup hooks và links có nguồn; hash/diff đầy đủ. Không sửa response object thành array hay ngược lại để xóa TC13 FAIL. Invalid schema, unresolved reference, positive schema data không hợp policy và runtime product issue phân loại riêng.

Link chain: create user/role/policy thử → gán quyền → tạo item → read/update/delete; file → folder → asset; dashboard → panel; flow → operation → trigger. Chỉ xây chain cần thiết, lấy ID runtime, xác minh predecessor và teardown ngược phụ thuộc. Không dùng auth secrets của request trước làm fuzz data hoặc lưu reproduction.

### 9.3. Ngân sách đề xuất, chưa phải số đã chạy

| Cấp | Phạm vi | Worker/rate/timeout | Budget |
|---|---|---|---|
| Pilot module | 1 nhóm nhỏ, read-only trước rồi mutation | 1; 2 request/s; 10s/request | seed 101; 10 examples/operation; 60s/profile/module |
| CI nhanh | ca deterministic P1, fuzz smoke read-only được duyệt | 1; tối đa 5/s; 10s | fuzz smoke 30–60s; cả job mục tiêu 15–25 phút sau pilot |
| Mở rộng | raw/guided nhóm tuần tự | 1; 5/s; 10s | kế thừa 100 examples, 1200s/profile/seed, seeds 101/202/303 sau đo tài nguyên |

Giả sử cả 22 nhóm đều được fuzz: 22 nhóm × 2 profile × 3 seed × 20 phút có thể tốn tới 44 giờ tuần tự trước setup; không bật mọi nhóm như một job CI ngắn. Chỉ nhóm áp dụng được fuzz và có oracle mới vào lịch. Phân bổ lại dựa trên pilot thời gian/độ ổn định và rủi ro, ghi phiên bản budget. Max-examples không là cap tổng request.

### 9.4. Kiểm tra CLI trước câu lệnh

Trong giai đoạn triển khai, từ image đã pin và đã hiện hữu: chụp schemathesis --version và schemathesis run --help vào metadata; không lấy CLI tài liệu latest làm lệnh bản cũ. Đối chiếu các flag đang dùng trong scripts/lab-components.sh với help thật, đặc biệt --coverage-format, --coverage-report-json-path và tracecov. Nếu không có, dừng phần coverage, xác định image/pipeline sinh file lịch sử; không nâng dependency ngầm.

Khung sau chỉ dùng tập option có trong invocation hiện tại và phải qua gate help; biến môi trường do runner an toàn cung cấp, không in token:

```sh
schemathesis run "$GROUP_RAW_SCHEMA" \
  --url "$RUNNER_API_URL" --workers 1 --seed 101 \
  --max-examples 10 --max-time 60 --rate-limit 2/s \
  --request-timeout 10 --phases examples,coverage,fuzzing \
  --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance,unsupported_method,negative_data_rejection,positive_data_acceptance \
  --report json,ndjson \
  --report-json-path "$RUN_DIR/schemathesis-report.json" \
  --report-ndjson-path "$RUN_DIR/schemathesis-events.ndjson"
```

Đây chưa phải lệnh hoàn chỉnh cấp quyền: auth do runner cấp qua cơ chế đã kiểm và sanitize; không fuzz auth endpoint bằng cùng token setup vô điều kiện. Guided thêm stateful chỉ sau links/setup pilot; không dùng tham số v3 như --hypothesis-max-examples. JSON/NDJSON có căn cứ trong repo; JUnit chỉ bật sau xác minh flag bản pin, HTML cần converter có phiên bản và kiểm output, không khẳng định harness hiện hỗ trợ HTML.

### 9.5. Bảo toàn dữ liệu, failure và công cụ bổ sung

Dùng namespace qa_sys_<module>_<run_id>, DB/storage dùng một lần, không trộn nhóm ghi trên fixture cũ. Ghi snapshot trước, giữ ID tạo mới, cleanup trong finally rồi read-back; restore lỗi thì dừng nhóm sau. Chỉ teardown tài nguyên đúng run/project đã kiểm đường dẫn/tên, không docker prune/xóa volume chung.

Artifact: metadata, inventory/allowlist, raw/guided hash và diff, fixture map không secret, events, report, coverage, request/response đã làm sạch, reproduction chain, cleanup/restore, exit codes. Sanitize token/cookie/password/license/header/query/body và credential trong logs trước upload; generation database cũng có thể chứa bí mật.

Triage: kiểm control, actor/schema/precondition → replay cùng baseline/fixture → giữ request tối thiểu và chuỗi trước nó → nhóm theo nguyên nhân → ghi contract/product/harness/environment/unresolved → regression deterministic. TC13 và aggregate giữ failing oracle gốc; năm nhóm bất thường dùng finding_id gốc nếu có, không tạo defect mới chỉ vì lặp seed.

REST Schemathesis không kiểm Studio hay WebSocket. GraphQL có thể pilot chế độ riêng của Schemathesis 4.30.0 nhưng cần introspection và assertion quyền/nghiệp vụ bổ sung; không áp REST response validator cho GraphQL. Playwright cho UI; client WebSocket cho realtime; API Python/Postman cho fixture/state/oracle; Vitest cho code coverage baseline; mail/HTTP/provider sink cho tích hợp. Postman collection/CLI mới là đề xuất, chưa có artifact triển khai được xác nhận.

## 10. Thiết kế CI GitHub Actions

### 10.1. Điều kiện khả thi và cấu trúc

Chưa tạo workflow YAML. CI static/offline bắt đầu ở M1; smoke Core mở ngay sau environment/fixture gate ở M2, không chờ Phase 4/5/6 hoàn tất. Đề xuất Ubuntu GitHub-hosted runner chạy Docker Compose trên host, test container cùng network; không lồng Docker vào job container nếu chưa xử lý socket/network/mount. Dịch vụ Docker của Actions cần Linux runner theo [GitHub Docs](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers). Nhóm phải pilot đo cold pull/setup, RAM/CPU/disk, timeout và ổn định; không mặc định runner đủ cho toàn campaign.

Compose hiện có name/network/volume cố định và host bind 8055. Khi triển khai CI, cần cấu hình riêng namespace theo run/job, loại hard-coded shared volume/network và không cho nhiều job ghi chung DB. Đây là thay đổi sau được phân công, chưa thực hiện. Self-hosted phải cô lập DB/storage/network theo job và giới hạn concurrency; không dùng lab cá nhân đang demo.

### 10.2. Hai tầng

| Bước | CI nhanh: PR/push | CI mở rộng: schedule/manual |
|---|---|---|
| Điều kiện | Static luôn chạy; integration chỉ khi môi trường/license đủ | Branch tin cậy; kiểm secret/provider và tài nguyên trước |
| Kiểm tĩnh | Markdown/link, Python syntax, shell syntax, catalog/selector và unit harness offline | Như nhanh, thêm inventory diff và schema validation |
| Setup | Pin digest; tạo config thử; healthcheck; seed idempotent; fixture verify | Profile theo module/protocol, feature flags và sinks |
| Thực thi | Deterministic P1 smoke/quyền/regression ổn định; không chạy campaign mutation dài | Ca mở rộng, raw/guided theo shard module và seed; GraphQL/WS/UI job riêng |
| Báo cáo | JSON per-case + summary, coverage trong tập smoke | Operation/RTM/module/schema coverage với inventory revision; failure register |
| Artifact | Reports/sanitized logs/cleanup dù bước test FAIL | Thêm reproduction/coverage/generation data đã rà bí mật |
| Cleanup | Finally/always, đúng tài nguyên job; giữ exit test | Restore trước shard tiếp theo; dừng khi restore lỗi |

Mục tiêu nhanh không được loại TC13 khỏi báo cáo để xanh. Có thể chia regression acceptance và known-issue verification thành job riêng nhưng required tổng hợp phải biểu diễn rõ còn FAIL được chấp nhận có điều kiện; không dùng continue-on-error để làm mất verdict. Nếu giảng viên yêu cầu zero FAIL thì TC13 phải được xử lý hợp đồng có căn cứ, không tự xóa.

### 10.3. Secret, license và runner

Tạo secret riêng của CI: key/secret ứng dụng, mật khẩu DB/admin/test actor, license CI hợp lệ nếu cần, credential sink/provider chỉ cho job tương ứng. Không sao chép config/lab.env local, không coi license local hợp lệ trên runner khác. Gate doctor kiểm license/policy thực; thiếu license = BLOCKED, không báo suite đạt.

PR từ fork thường không nhận secret; dùng static/offline checks và xuất integration BLOCKED với lý do, chạy integration trên context tin cậy sau review. Không dùng pull_request_target để chạy code PR chưa tin cậy cùng secret. Hành vi secret dựa trên [GitHub Docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets). Chỉ cấp contents:read mặc định; quyền khác cần lý do cụ thể. Self-hosted chỉ cho branch/code tin cậy.

### 10.4. Hợp đồng kết quả và gate

| Tình huống | Trạng thái báo cáo | Hành động |
|---|---|---|
| Assertion vi phạm | FAIL, giữ actual/oracle | Required job thất bại; triage trước merge |
| Hạ tầng không lên | infrastructure failure; ca BLOCKED/NOT_RUN | Không gán product defect; giữ log, giới hạn retry có ghi lần đầu |
| Chưa chạy | NOT_RUN kèm lý do | Không cộng thực thi; fail gate nếu mandatory |
| Known issue | FAIL + issue/source + phạm vi + người chấp nhận + hạn xem lại | Không đổi PASS; gate quyết định riêng, không blanket skip |
| Hết budget | INCOMPLETE + stop_reason; giữ các FAIL đã phát hiện | Báo covered/missing; không gọi campaign đạt đầy đủ |
| Cleanup/restore lỗi | cleanup FAIL; subsequent BLOCKED | Dừng reuse DB; tổng job lỗi kể cả assertions PASS |
| Hủy job | INCOMPLETE, ghi tác vụ chưa xong | Cleanup best effort; job sau dùng môi trường mới |

Lưu artifact ngay khi có thể và ở bước always; xử lý exit code test, reporter và cleanup riêng rồi tổng hợp exit cuối, không dùng “|| true” che lỗi. Upload artifact cũng cần kiểm tra thành công. Retention đề xuất 14 ngày PR, 30 ngày campaign sau kiểm quota; giữ bộ bằng chứng nghiệm thu lâu hơn ngoài cache.

## 11. Git, Branch và Commit

Lành phụ trách môi trường/interface/tích hợp; Nhân phụ trách schema/campaign/replay; Trâm phụ trách fixture/quyền/oracle. Đây là phân công đề xuất tiếp nối AGENTS, không ghi thành đóng góp đã làm.

1. Kiểm git status, bảo toàn working tree người khác; tạo nhánh có phạm vi như test/auth-session hoặc test/files-assets trong repo DAMH.
2. Xây nhóm requirement/test liên quan cùng fixture và cleanup, không sửa source upstream ngoài phạm vi đã duyệt.
3. Chạy local đúng baseline; lưu metadata và bằng chứng; kiểm diff và sanitize.
4. Commit độc lập có ý nghĩa, không bắt buộc mỗi test một commit: nhiều ca chung fixture/oracle nên review như một thay đổi nhất quán; vẫn tránh commit trộn module hoặc config chung chưa kiểm.
5. Push nhánh, mở PR mô tả hành vi/rủi ro/validation/missing coverage; CI chạy; review bằng chứng; merge khi gate đạt hoặc có chấp nhận lỗi cụ thể.
6. Giữ lịch sử chia sẻ; không force push/reset/squash mặc định; không mượn danh tính thành viên.

Ví dụ: test(auth): add session lifecycle cases; test(rbac): add multi-policy permission tests; test(api): extend schema conformance checks; ci: add directus regression workflow; docs: update test coverage matrix.

Không commit credential/token/license, config thật, private key, DB dump hoặc report/generation DB chứa secret. Repo có nhiều file untracked; không git add .; chỉ stage phạm vi task. Kế hoạch này chưa tạo branch, commit, push, issue hoặc PR.

## 12. Ba mốc nghiệm thu và lộ trình tối thiểu khả thi

Ba mốc là các cổng chứng minh, không phải nhãn đã hoàn thành. Nhóm ba người, ngày công quy đổi 6 giờ; số ngày dưới là **ước lượng đề xuất**, chưa đo năng suất. Không cộng công việc song song thành lịch tuyến tính. Không tính thời gian chờ thầy/license/provider, sửa Directus, multi-DB/load lớn.

### 12.1. M1 — Coverage Baseline

**Ưu tiên cao nhất.** Nhân kiểm kê source baseline/OAS/transport; Trâm map toàn catalog và requirement; Lành chốt environment/applicability và quyết định phạm vi. Phụ thuộc: manifest và source object đúng SHA; quyền đọc có sẵn. Runtime export chỉ thực hiện khi được giao triển khai, không trong nhiệm vụ sửa tài liệu.

Đầu ra: inventory máy đọc được cho toàn chức năng, route có điều kiện và giao thức; RTM/canonical/decision/gap; snapshot baseline; counter specification mục 6.8. Giữ UNKNOWN và NOT_MEASURED khi chưa đủ nguồn. DoD: mọi họ chức năng phát hiện có record và nguồn; chênh source–OAS có gap; tất cả 257 ID và 44 thiết kế cũ có phân loại; mỗi subset khóa có mẫu số/cách tái tính, chưa khóa phải ghi rõ. Không đòi mọi chức năng đã được test để hoàn tất M1; không đánh dấu coverage toàn hệ thống đã đo nếu còn unresolved mẫu số.

CI static/offline được đưa vào từ mốc này: kiểm config/script syntax/catalog/reference và unit harness theo phạm vi được giao sau. Lành có thể chuẩn bị song song inventory; không chờ baseline mọi module để thiết kế pipeline.

### 12.2. M2 — Automated Testing + CI

Phụ thuộc M1 **cho subset Core được chọn** và môi trường/licensing đủ; các gap phần khác tiếp tục có owner. Trâm tái dùng ID cũ trước, Lành chạy smoke CI ngay sau fixture/actor gate, Nhân mở raw/guided pilot sau CLI gate. Chưa cần hoàn tất Extended.

Tập tối thiểu đề xuất, chốt lại từ RTM: regression 13 alias + lựa chọn ca ASSERTABLE/NOT_RUN rủi ro cao trong 257 (không mặc định chọn mọi 257); kiểm phiên/quyền TC14–TC17; schema metadata TC18/TC19; file local TC26/TC27; health/info TC34. Đây là **backlog ứng viên**, không cam kết số ca mới hay trạng thái đã chạy. Nếu không đủ thời gian, quyết định thứ tự theo I/L/C và ghi thiếu, không giảm denominator âm thầm. TC13 vẫn FAIL historical và được báo riêng khi replay.

DoD: selection manifest không trùng canonical; ca được triển khai có oracle, control và cleanup; static/offline + smoke/integration CI có bằng chứng; raw/guided pilot nhóm Core có report/schema hash/budget; missing/FAIL/BLOCKED/INCOMPLETE được giữ; coverage tính lại được cho subset chốt. Chưa xác minh tracecov thì giữ schema keyword metric NOT_MEASURED nhưng vẫn báo operation/RTM bằng raw evidence hợp lệ.

### 12.3. M3 — Full-Scope Coverage Evidence

Phụ thuộc M1 inventory toàn hệ thống và M2 pipeline ổn định; scope nghiệm thu đã xác nhận. Nhân và Trâm bổ sung evidence cho Extended đã chọn; Lành tích hợp báo cáo và decisions Conditional. GraphQL, Studio, Realtime phải có evidence riêng nếu thuộc scope, không thay bằng REST. Conditional provider/license chỉ được lên lịch sau dependency gate; nếu vẫn thuộc scope mà chưa có điều kiện, để BLOCKED và mục tiêu liên quan chưa đạt.

DoD: RTM và evidence của **toàn scope nghiệm thu** được đối chiếu, mỗi requirement/operation/module có verdict hoặc gap; mẫu số theo tầng/transport được khóa hoặc ghi NOT_MEASURED; mọi tỷ lệ tái tính được; root-cause/defect phân biệt với failure; known issue và cleanup có kết luận; danh sách ngoài scope/conditional và hạn chế công khai. “Đủ evidence” gồm báo trung thực phần thiếu, **không đồng nghĩa acceptance PASS**. Nếu mandatory còn NOT_RUN/BLOCKED/INCOMPLETE/FAIL chưa được chấp nhận, báo mốc evidence đã tổng hợp nhưng nghiệm thu chức năng chưa đạt.

### 12.4. Các gói việc, phụ thuộc và ước lượng

| Gói / phase tương ứng | Người đề xuất | Đầu ra / điều kiện bắt đầu | Cổng DoD / dependency | Công sức đề xuất / rủi ro |
|---|---|---|---|---|
| B1 Audit + System Inventory (Phase 1–2) | Nhân + Lành | Source/manifest; inventory mọi tầng | M1: nguồn/route/flag/transport/applicability có record hoặc gap | 3–5 ngày công; route động/source lệch image |
| B2 RTM + canonical reuse + risk (Phase 3) | Trâm + Nhân | Catalog đã có; inventory increment | M1: 257 ID map, reuse/delta có nguồn; oracle/gap và scoring | 2–3; oracle thiếu, alias nhầm |
| C0 Static CI sớm (phần Phase 7) | Lành | Interface audit; không cần module integration | Chạy song song B1/B2 khi được triển khai; log check/artifact | 1–2; thiếu CLI/dependency offline |
| C1 Regression/smoke Core (Phase 4 + CI Phase 7) | Trâm + Lành | Actor/license/fixture đúng; selection từ RTM | M2: ca cũ được reuse và cleanup; integration smoke không đợi C3 | 2–3; license/fixture |
| C2 Core delta + contract pilot (Phase 4–5) | Trâm chức năng; Nhân schema | B2 cho từng module; CLI help gate | M2: auth/quyền/model/files theo thứ tự; evidence/missing rõ | 3–5; mutation và tracecov |
| C3 Extended native (Phase 6 + phần Phase 4) | Trâm UI/functional; Nhân protocol | Scope/feature đã xác minh; C1/C2; fixture riêng | M3: subset Extended có test/own verdict, còn thiếu ghi gap | Ước lượng sau inventory và pilot; không ép toàn 22 nhóm vào MVP |
| C4 CI extended + campaign (Phase 7–8) | Lành + Nhân | M2; budget shard theo module đã ổn định | Report/cleanup/coverage; schedule/manual không che failure | 1–2 cho pipeline/report MVP; campaign lớn ước lượng riêng |
| E1 Evidence và báo cáo (Phase 9) | Lành tổng hợp; Nhân/Trâm xác nhận phần mình | M1/M2 artifacts, decision scope | M3: coverage truy vết, gap register và bàn giao | 2–3; nhầm mẫu số/thiếu report |
| X1 Conditional/provider/đa DB/tải | Theo dependency, Lành điều phối | Feature/license/provider/cost + thầy chốt | Không là prerequisite của CI static/Core; nếu mandatory thì chặn nghiệm thu scope liên quan | Chưa ước lượng; cần pilot riêng |

MVP B1+B2+C0+C1+C2+C4+E1 khoảng **14–23 ngày công (84–138 giờ)**, chưa gồm C3/X1 và chờ hạ tầng. Với ba người tổng 6–9 giờ/ngày, khoảng 10–23 ngày làm việc trước overhead; không phải deadline cam kết. Estimate đầy đủ bản kế hoạch trước là 35–55 ngày công cho mở rộng sâu nhiều module: giữ như **ước lượng scope rộng chưa xác minh**, không áp làm điều kiện bắt buộc để có smoke CI/MVP. Sau M1 phải ước lượng lại bằng số requirement áp dụng và thời gian pilot, không cố hoàn thành mọi mục chỉ để đủ số ca.

Phụ thuộc chính: B1 → B2 theo increment; B1 audit → C0 song song; B2/Core+environment gate → C1 → C2; C1 mở smoke CI trước khi C2 hoàn tất; C2 → C4; C3/X1 chỉ khi scope/dependency đủ; artifacts/decisions → E1. Không chạy song song hai suite mutation trên cùng DB chưa cách ly.

### 12.5. Hướng dẫn giao việc theo phase cho GPT 6.1 Sol Medium

#### 12.5.1. Cách sử dụng và giới hạn quyền

Phần này chia gói việc thành **20 phase P00–P19** để GPT 6.1 Sol Medium có đầu vào hẹp, đầu ra kiểm chứng được và checkpoint bền vững. Đây là hướng dẫn giao việc, **không phải 20 phase đã được triển khai**. Không tự chuyển model, khởi tạo agent con hoặc chạy bất kỳ phase nào khi đang chỉnh tài liệu.

Dùng một lượt giao việc cho một phase hoặc một batch có tên rõ. Nếu người dùng đã giao triển khai phase và các bước trong scope là cần thiết, thực hiện tới DoD, không hỏi xác nhận lại cho bước thông thường. Không tự mở rộng sang phase chưa giao. Nếu người dùng giao cả một dải phase, được tiếp tục các phase có dependency đủ trong dải đó; checkpoint giữa phase, không bắt người dùng xác nhận máy móc.

**Lượt hiện tại chỉ chỉnh kế hoạch.** Các đường dẫn mới, schema, script, workflow, run/handoff phía dưới là đầu ra tương lai. Quyền sửa tài liệu kế hoạch không tự cấp quyền cài package, start/stop/reset lab, sửa cấu hình, viết test, tạo workflow, commit/push hoặc xuất bản. Khi giao phase triển khai sau này, mô tả cụ thể hành động/môi trường được phép. Không xin lại quyền đã rõ trong lượt đó; nếu thiếu thông tin quyết định, chỉ dừng phần phụ thuộc và tiếp tục phần độc lập.

Đường dẫn trong bảng/prompt tính tương đối từ repo `DAMH/`, không phải workspace root. Source `../directus/` mặc định chỉ đọc object đúng baseline; không sửa checkout hiện có. Phân công tên thành viên là người sở hữu đề xuất; model chỉ hỗ trợ, không nhận danh tính hoặc ghi đóng góp giả của thành viên.

#### 12.5.2. Giữ context nhỏ, tránh làm lại và tránh công việc quá lớn

1. Mở AGENTS áp dụng và handoff phase trước, kiểm Git status; đọc đúng mục kế hoạch được liệt kê và những source file cần cho phase. Không nạp toàn bộ kế hoạch/phụ lục/report JSON/monorepo vào context mỗi lượt.
2. `rg` tên route/test ID trước, đọc đoạn và artifact liên quan; giữ path@SHA và JSON pointer/report ID trong handoff để lượt sau tra cứu trực tiếp. Không đọc/in config thật hoặc token.
3. Trước sửa, ghi danh sách file dự kiến và giới hạn hành vi. Tận dụng interface/helper/schema hiện có; thiếu bằng chứng thì ghi gap, không tự thiết kế lại framework.
4. P01 có thể chia batch manifest+inventory, requirement+catalog+RTM, execution+decision+summary. P03/P04 chia theo họ controller; P06 chia theo group catalog; mỗi batch có checklist đã duyệt/chưa duyệt. Phase chỉ hoàn thành khi hợp nhất đủ batch, không vì một batch đã xong.
5. P11–P14/P16/P17 mỗi lượt tối đa một nhóm fixture/module/giao thức có oracle liên quan; nếu các ca cần fixture hoặc verdict độc lập thì tách lượt. P16 lặp `P16/<module>`, P17 lặp `P17/<feature>`; không tạo cùng lúc tất cả Extended/Conditional.
6. Kiểm nhỏ nhất chứng minh thay đổi khi được phép triển khai. Không chạy lại mọi suite/campaign sau sửa Markdown; không sửa assertion để PASS; không đoán CLI theo trí nhớ hoặc docs mới.
7. Kết thúc bằng delta thực tế, trạng thái, evidence và việc tiếp theo cụ thể. Khi context sắp dài, ghi checkpoint đủ tiếp tục; không bắt đầu lại audit hoặc chạy lại test chỉ vì đổi cuộc trò chuyện/model.

Không đặt số token hoặc thời gian chạy cố định cho mô hình. Giới hạn bằng **đơn vị công việc, file chịu tác động, dependency và DoD**; ngân sách fuzz vẫn theo manifest/budget đã được chốt, không phụ thuộc tốc độ model.

#### 12.5.3. Prompt nền dùng chung

Dán prompt nền này, rồi prompt của đúng phase ở mục 12.5.6. Điền các ô vuông; không để model tự chọn tất cả backlog.

```text
Bạn làm việc trong repo DAMH, dùng kế hoạch
docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md làm nguồn điều phối.

Chỉ thực hiện phase [Pxx / batch hoặc module], với phạm vi được giao:
[đọc và sửa tài liệu / tạo dữ liệu thiết kế / triển khai code và kiểm offline /
 triển khai và kiểm trên lab thử có định danh rõ].
Hành động/môi trường được phép cụ thể: [mô tả].
Nếu chỉ là tài liệu thì không chạy API/test hoặc đổi cấu hình.

Đọc AGENTS.md áp dụng, git status, handoff [đường dẫn] và các mục cần cho phase;
đọc source Directus đúng baseline bằng phương thức không thay checkout.
Không ghi đè thay đổi có sẵn. Không commit/push/tạo PR hoặc liên hệ người khác
trừ khi tôi giao rõ việc đó. Không tạo sub-agent.

Trước làm: nêu đầu vào đã có, file dự kiến sửa, dependency còn thiếu và DoD.
Tái dùng canonical test/helper/oracle có nguồn; giữ bằng chứng lịch sử.
Không tự đặt coverage, không chuyển FAIL thành PASS, không cộng alias/requests
thành test độc lập. Không coi source-present là runtime-enabled.
Không mở rộng sang phase khác trừ khi tôi giao dải phase đó.
Hoàn thành phần đã được giao; chỉ dừng phần phụ thuộc quyết định thật sự thiếu.

Sau làm: lưu handoff theo mẫu của kế hoạch, ghi chính xác việc đã/chưa chạy,
file thay đổi, evidence, gap và bước tiếp theo. Không gọi kế hoạch là triển khai.
```

#### 12.5.4. Mẫu handoff và quy tắc trạng thái phase

Handoff dự kiến: `docs/coverage/handoffs/Pxx.md` hoặc `Pxx/<batch>.md`; nếu đã có cơ chế checkpoint phù hợp thì tái dùng và ghi đường dẫn, không tạo hệ thống thứ hai. Nội dung nhạy cảm/run thô vẫn lưu nơi artifact được kiểm soát, không nhét vào tài liệu Git.

```text
Phase / batch:
Loại công việc và phạm vi được giao:
Trạng thái phase: NOT_STARTED | IN_PROGRESS | READY_FOR_REVIEW | COMPLETE | BLOCKED
Baseline / inventory / catalog revision:
Input đã đọc: path@SHA hoặc artifact ID; phần liên quan, không chép toàn file
Thay đổi đã làm: file và hành vi; bảo toàn thay đổi có sẵn nào
Lệnh/kiểm tra thực sự đã chạy: mục đích, exit/status, artifact
Chưa chạy / CHƯA XÁC MINH:
DoD checklist: đạt / chưa đạt kèm nguồn
Kết quả test riêng: PASS/FAIL/BLOCKED/NOT_RUN/INCOMPLETE/NOT_APPLICABLE
Known issue, cleanup và infrastructure status:
Gap/dependency: ID, owner đề xuất, thông tin cần có, phần nào bị chặn
Batch đã xong / còn lại:
Bước tiếp theo cụ thể: phase/batch, input, file cần đọc đầu tiên
```

Trạng thái phase mô tả **hoàn tất sản phẩm công việc**, khác verdict test. Phase triage có thể COMPLETE khi đã ghi đúng một FAIL; acceptance của M2/M3 vẫn chưa đạt nếu mandatory failure chưa được xử lý/chấp nhận. Phase chạy campaign phải ghi cả completion/budget/restore, không gọi INCOMPLETE campaign là PASS. Mốc có dependency bắt buộc thiếu thì chưa COMPLETE; được tiếp tục phase độc lập đã được giao. Không giả người khác đã review để nâng READY_FOR_REVIEW thành COMPLETE.

#### 12.5.5. Bản đồ phase và thứ tự thực hiện

| Phase | Sản phẩm chính | Dependency | Mốc / đường triển khai |
|---|---|---|---|
| P00 | Chốt ảnh chụp đầu vào | Khởi đầu | M1 — Coverage Baseline |
| P01 | Khóa hợp đồng dữ liệu coverage | P00 | M1 — Coverage Baseline |
| P02 | CI static/offline sớm | P00 + phần hợp đồng cần dùng của P01; không đợi P03–P07 | CI sớm; chạy sau P00/P01, không cần đợi inventory toàn bộ |
| P03 | Inventory auth và API hệ thống | P00 + P01 | M1 — Coverage Baseline |
| P04 | Inventory nội dung và chức năng native | P00 + P01; dùng quy tắc P03 | M1 — Coverage Baseline |
| P05 | Inventory giao thức và tính năng có điều kiện | P01; source shards P03/P04 nếu sẵn | M1 — Coverage Baseline |
| P06 | Canonical map và tái sử dụng catalog | P01 + catalog 257; đối chiếu mục 8 | M1 — Coverage Baseline |
| P07 | Khóa RTM, scope và Coverage Baseline — M1 | P03 + P04 + P05 + P06; P01 | M1 — Coverage Baseline |
| P08 | Validator và bộ tính coverage offline | P01 + baseline subset P07 | M2 — Automated Testing + CI |
| P09 | Profile môi trường thử và preflight | P00 + Core subset P07; được giao triển khai môi trường | M2 — Automated Testing + CI |
| P10 | Regression tái dùng và smoke CI | P06 + P07 subset + P09; nối P02 khi sẵn | M2 — Automated Testing + CI |
| P11 | Core delta: auth/session và policy | P07 oracle nhóm AUTH/RBAC + P09; P10 ưu tiên đã ổn định | M2 — Automated Testing + CI |
| P12 | Core delta: mô hình dữ liệu | P07 oracle MODEL + P09; mô hình DB tạm được giao | M2 — Automated Testing + CI |
| P13 | Core delta: file local và asset privacy | P07 oracle FILES + P09 có storage riêng | M2 — Automated Testing + CI |
| P14 | REST contract/fuzz pilot có kiểm soát | P07 subset inventory + P09 CLI gate; nhóm fixture đã đạt từ P10–P13 | M2 — Automated Testing + CI |
| P15 | Nghiệm thu Automated Testing + CI — M2 | P08 + P10; P11–P14 theo selection Core đã chốt | M2 — Automated Testing + CI |
| P16 | Extended theo từng module/giao thức | P07 scope Extended + P15 hoặc prerequisite subset đã ổn; environment gate riêng | M3 — mở rộng/evidence |
| P17 | Conditional và code coverage theo quyết định | P05/P07 dependency/decision + quyền triển khai profile cụ thể | M3 — mở rộng/evidence |
| P18 | Chiến dịch nghiệm thu theo scope đã khóa | P15 + P16/P17 bắt buộc trong selection; mọi cleanup/precondition đủ | M3 — mở rộng/evidence |
| P19 | Full-Scope Coverage Evidence và báo cáo — M3 | P18 hoặc bộ runs nghiệm thu có nguồn; P07 decisions; P08 calculator | M3 — báo cáo |

**Đường tối thiểu khả thi:** P00 → P01 → P03/P04/P05 → P06 → P07 (M1) → P08/P09 → P10 → các nhóm Core bắt buộc P11/P12/P13 → P14 pilot → P15 (M2) → P18 theo scope tối thiểu → P19 (M3 evidence). P02 bắt đầu sớm sau input cần dùng của P01 và được tích hợp dần, không đợi P07/P15. Dấu “/” chỉ các gói có thể xếp lịch xen kẽ; **không phải chỉ thị tạo agent song song hoặc chạy mutation chung DB**.

P16/P17 chỉ vào đường bắt buộc khi thầy/nhóm đã chốt tính áp dụng. Nếu scope yêu cầu GraphQL/Studio/Realtime thì thêm đúng batch tương ứng trước P18/P19; không dùng đường MVP bỏ chúng rồi tuyên bố toàn hệ thống. Lịch có thể lặp phase để xử lý gap mới, nhưng không thay baseline hoặc budget ngầm.

#### 12.5.6. Chi tiết và prompt từng phase

##### P00 — Chốt ảnh chụp đầu vào

| Mục | Nội dung giao việc |
|---|---|
| Dependency | Khởi đầu |
| Chủ sở hữu đề xuất | Lành |
| Phạm vi sửa/thực thi | Chỉ đọc Git và tài liệu; tạo ghi chú bàn giao tài liệu |
| Đầu vào cần đọc | AGENTS.md; kế hoạch mục 1–2, 5, 17; README; manifest/baseline.yaml; git status/remotes/HEAD |
| Công việc cụ thể | Ghi source/image baseline, branch/dirty state, vị trí repo DAMH và Directus; xác định artifact còn truy cập được; không đọc env thật; phân biệt lịch sử và runtime |
| Đầu ra | docs/coverage/handoffs/P00.md: nguồn đã đọc, SHA, thay đổi có sẵn, CHƯA XÁC MINH và đường dẫn đầu vào |
| Definition of Done | Mọi fact có source; xác định đúng repo harness; không sửa/suy trạng thái lab; chỉ hoàn thành audit đầu vào |
| Điều kiện dừng/giới hạn | Không fetch/pull/checkout/build/start lab để làm audit; thiếu source object thì ghi gap |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P00. Tạo bản bàn giao ngắn xác nhận repo, source baseline và bộ dữ liệu đã có. Không sửa harness hoặc làm inventory toàn bộ trong lượt này.

##### P01 — Khóa hợp đồng dữ liệu coverage

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P00 |
| Chủ sở hữu đề xuất | Nhân + Lành |
| Phạm vi sửa/thực thi | Chỉ thiết kế/tạo schema dữ liệu và ví dụ nhỏ; chưa viết extractor/runner |
| Đầu vào cần đọc | Mục 6.1–6.8, 7; handoff P00 |
| Công việc cụ thể | Chốt kiểu dữ liệu/enum/key/ref của manifest, inventory, requirements, catalog, RTM, executions, decisions/gaps và summary; schema version; null/UNKNOWN/NOT_MEASURED; DIRECT/SUPPORTING; chuẩn hóa operation/alias |
| Đầu ra | docs/coverage/schemas/ và ví dụ tối thiểu; docs/coverage/handoffs/P01.md; đường dẫn là đề xuất cần kiểm tra xung đột trước tạo |
| Definition of Done | Định nghĩa có thể biểu diễn requirement nhiều TC, TC nhiều requirement, alias, FAIL/INCOMPLETE/cleanup riêng; ví dụ không có số coverage giả; không rename interface cũ |
| Điều kiện dừng/giới hạn | Không dùng CSV đơn làm mất quan hệ; không đưa secret/run thực giả vào example |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P01. Chuyển đặc tả mục 6.8 thành hợp đồng máy đọc được có version và ví dụ tối thiểu. Chưa viết công cụ tính coverage hoặc xuất schema runtime.

##### P02 — CI static/offline sớm

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P00 + phần hợp đồng cần dùng của P01; không đợi P03–P07 |
| Chủ sở hữu đề xuất | Lành |
| Phạm vi sửa/thực thi | Triển khai CI kiểm tĩnh/offline theo phạm vi được giao; không cần Docker/live API/secret |
| Đầu vào cần đọc | Mục 10–11; scripts/tests và cấu hình dependency đã có; handoff P00/P01 |
| Công việc cụ thể | Kiểm lệnh offline hiện hữu; chọn syntax/config/catalog và unit harness cần thiết; thiết kế rồi tạo workflow static khi lượt giao việc cho phép; tách integration chưa chạy; artifact nhỏ, exit code thật |
| Đầu ra | Workflow static/offline + tài liệu lệnh tái lập + handoff P02; không push để kích hoạt Actions nếu chưa có quyền |
| Definition of Done | Local offline checks được chạy đúng phạm vi; remote CI chỉ ghi đã chạy khi có run thật; integration thiếu môi trường ghi rõ, không coi static là API PASS |
| Điều kiện dừng/giới hạn | Chưa có quyền tạo workflow thì chỉ làm thiết kế có thể review; thiếu dependency không cài/nâng toàn máy ngầm |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P02 theo quyền triển khai tôi giao trong lượt này. Tận dụng checks offline hiện có và dựng CI static tối thiểu; không chạy API, fuzz hoặc sửa workflow integration.

##### P03 — Inventory auth và API hệ thống

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P00 + P01 |
| Chủ sở hữu đề xuất | Nhân |
| Phạm vi sửa/thực thi | Chỉ inventory một nhóm route nguồn; không thực thi endpoint quản trị |
| Đầu vào cần đọc | Source app.ts/router đúng SHA baseline; manifest; schema hợp đồng P01; kế hoạch mục 3–4 |
| Công việc cụ thể | Kiểm mount và router con auth/users/roles/policies/permissions/access; collections/fields/relations/schema; settings/server/license/metrics; ghi method/path/flag/quyền/source_refs và gap OAS |
| Đầu ra | Inventory shard auth-system theo schema P01 + danh sách route chưa phân giải + handoff P03 |
| Definition of Done | Mỗi route được ghi có source@SHA; route điều kiện giữ flag/UNKNOWN; không lấy số router làm số operation; không gộp template với ID thật |
| Điều kiện dừng/giới hạn | Chưa có admin OAS runtime thì oas_presence UNKNOWN, không bỏ route; source HEAD không thay bản pin |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P03. Kiểm kê source baseline cho nhóm auth và API hệ thống, xuất dữ liệu theo P01. Không gọi API hoặc suy route chưa bật thành N/A.

##### P04 — Inventory nội dung và chức năng native

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P00 + P01; dùng quy tắc P03 |
| Chủ sở hữu đề xuất | Nhân |
| Phạm vi sửa/thực thi | Chỉ inventory nhóm nội dung; không tạo fixture/schema runtime |
| Đầu vào cần đọc | Source baseline routers/services; shard P03; hợp đồng P01 |
| Công việc cụ thể | Kiểm items/query/validation/bulk, files/folders/assets/tus, flows/operations, history/versions, dashboards/panels/presets, shares/comments/notifications/translations/utils/import-export; giữ capability không có operation độc lập |
| Đầu ra | Inventory shard content-native + coverage của chính đợt kiểm kê + gap list + handoff P04 |
| Definition of Done | Không trùng khóa với shard P03; mỗi capability có route/ref hoặc lý do; path động chuẩn hóa; biết nhóm nào chưa kiểm kê, không gọi inventory hoàn chỉnh sớm |
| Điều kiện dừng/giới hạn | Không đếm một query parameter thành HTTP operation mới; hạn chế xuất toàn monorepo vào context |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P04. Kiểm kê nhóm native còn lại theo schema P01, đối chiếu source baseline; không chạy test hoặc nhân bản inventory auth đã có.

##### P05 — Inventory giao thức và tính năng có điều kiện

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P01; source shards P03/P04 nếu sẵn |
| Chủ sở hữu đề xuất | Nhân; Trâm kiểm UI |
| Phạm vi sửa/thực thi | Kiểm kê source/config transport ngoài REST và feature điều kiện; chưa cài client/provider |
| Đầu vào cần đọc | Source graphql/websocket/app/extensions/ai/mcp/deployment/sdk; Compose và env mẫu; mục 3.2 |
| Công việc cụ thể | Lập capability GraphQL/Realtime/Studio/extensions/AI/MCP/deployment/SDK và tích hợp; nối REST route nếu có nhưng inventory riêng giao thức; deployed_state có nguồn; matrix conditional dependency |
| Đầu ra | Inventory shard non-rest-conditional; dependency/decision/gap records; handoff P05 |
| Definition of Done | Không dùng REST OAS thay GraphQL/WS/UI; mọi feature có applicability/UNKNOWN và nguồn; source-present không tự bằng runtime-enabled |
| Điều kiện dừng/giới hạn | Không gọi provider thật, cài extension hoặc chuyển Conditional thành N/A chỉ vì thiếu credential |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P05. Hoàn thiện inventory ngoài REST và conditional bằng source/config có sẵn; giữ mọi điểm chưa xác minh, không bật tính năng để kiểm chứng.

##### P06 — Canonical map và tái sử dụng catalog

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P01 + catalog 257; đối chiếu mục 8 |
| Chủ sở hữu đề xuất | Trâm |
| Phạm vi sửa/thực thi | Chỉ xử lý thiết kế/mapping; không sửa expected hoặc thực thi lại ca |
| Đầu vào cần đọc | Catalog 257; scenario/invariant và report nguồn; TC01–TC13; mục 5, 8; phụ lục A/B |
| Công việc cụ thể | Map toàn 257 ID và alias TC; ghi exact-reuse/partial/delta/revised/new cùng lý do; giữ lineage TC42/49/55 và TC58–TC62; đối chiếu các nhận định reuse trong kế hoạch bằng field/oracle/source thực |
| Đầu ra | Canonical catalog + alias/reuse mapping + discrepancy log + handoff P06; theo schema P01 |
| Definition of Done | Mỗi ID gốc có đúng mapping hoặc gap; alias không tăng số; historical execution không bị đổi baseline; phân biệt DIRECT/SUPPORTING; sửa nhận định kế hoạch nếu tìm được bằng chứng mới |
| Điều kiện dừng/giới hạn | Catalog NOT_RUN/OPEN không được lấy làm PASS; chia đọc theo group nhưng phải có checklist đủ 257 ID |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P06. Khóa canonical/alias và reuse mapping của toàn 257 ID với thiết kế hiện tại. Không viết lại test và không cộng số lượng dựa trên tên mới.

##### P07 — Khóa RTM, scope và Coverage Baseline — M1

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P03 + P04 + P05 + P06; P01 |
| Chủ sở hữu đề xuất | Lành chốt; Nhân/Trâm chuẩn bị |
| Phạm vi sửa/thực thi | Tích hợp dữ liệu/requirement; chỉ chốt subset đủ bằng chứng |
| Đầu vào cần đọc | Inventory shards; canonical map; mục 3.2, 4.1, 6 và decisions giảng viên có thật |
| Công việc cụ thể | Merge inventory; kiểm missing route/capability; tạo requirement/oracle/risk I/L/C; gắn DIRECT/SUPPORTING; Core/Extended/Conditional; chốt selection baseline revision hoặc gap/UNKNOWN; đề xuất MVP |
| Đầu ra | Baseline manifest + RTM/requirements/inventory thống nhất + decision/gap register + handoff P07/M1 |
| Definition of Done | Mọi requirement áp dụng có test hoặc gap; tất cả source groups đã được xét; mẫu số subset rõ; chưa có approval scope thì giữ đề xuất, không giả xác nhận thầy; NOT_MEASURED khi chưa đo |
| Điều kiện dừng/giới hạn | Không tự chốt mọi Conditional ngoài scope; toàn inventory còn UNKNOWN thì không tuyên bố coverage toàn hệ thống đã đo |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P07. Hợp nhất inventory/RTM, tạo Coverage Baseline có revision và backlog tối thiểu. Chốt phần đủ nguồn, ghi phần cần quyết định; chưa triển khai test mới.

##### P08 — Validator và bộ tính coverage offline

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P01 + baseline subset P07 |
| Chủ sở hữu đề xuất | Nhân |
| Phạm vi sửa/thực thi | Chỉ công cụ offline đọc dữ liệu; không gọi SUT |
| Đầu vào cần đọc | Công thức nguyên trạng mục 6.2–6.8; baseline/RTM và reports thật dùng làm đầu vào |
| Công việc cụ thể | Viết validator/reference resolver và calculator tập D/E/V/O; dedup alias; run-selection policy; phân biệt cleanup/infra/FAIL; missing ID lists; không tính partial schema thành PASS |
| Đầu ra | Công cụ coverage offline + mẫu output + checks có ý nghĩa cho alias/FAIL/BLOCKED/many-to-many + handoff P08 |
| Definition of Done | Đối chiếu kiểm tay các tình huống mục 6.8; schema/reference lỗi trả failure; không có execution thì execution coverage NOT_MEASURED theo ngữ cảnh; không sinh evidence thật từ sample |
| Điều kiện dừng/giới hạn | Chỉ kiểm bằng fixture offline đã đánh dấu; giữ baseline/report nguồn bất biến |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P08. Xây validator và tính coverage offline theo công thức kế hoạch. Kiểm các lỗi đếm alias, FAIL, BLOCKED và quan hệ nhiều–nhiều; không chạy API.

##### P09 — Profile môi trường thử và preflight

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P00 + Core subset P07; được giao triển khai môi trường |
| Chủ sở hữu đề xuất | Lành |
| Phạm vi sửa/thực thi | Chỉ profile/preflight cho smoke và Core; chưa seed module mở rộng tùy ý |
| Đầu vào cần đọc | Compose/env mẫu/manifest; interface hiện tại; nguồn CLI/version đúng image; dependency/license gate |
| Công việc cụ thể | Thiết kế namespace network/volume/storage theo run; tái dùng lab hiện hữu nếu đúng; kiểm health/version/license/policy/fixture và CLI help bằng thao tác phù hợp; làm rõ tracecov; không sửa raw OAS |
| Đầu ra | Profile test/CI riêng nếu cần + preflight report đã sanitize + rollback/cleanup procedure + handoff P09 |
| Definition of Done | Định danh đúng lab và actor; URL local; không đụng DB khác; credentials không ra log; điều kiện thiếu được BLOCKED; tracecov chưa xác minh không chặn việc ghi operation evidence hợp lệ |
| Điều kiện dừng/giới hạn | Không reset DB đang demo hoặc sửa license; pull/build/start chỉ trong quyền lượt giao; dừng phần thiếu license mà tiếp tục kiểm tĩnh độc lập |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P09 trong lab thử đã được giao. Làm preflight và cách ly môi trường cho smoke/Core; chưa chạy campaign hoặc seed toàn bộ module.

##### P10 — Regression tái dùng và smoke CI

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P06 + P07 subset + P09; nối P02 khi sẵn |
| Chủ sở hữu đề xuất | Trâm + Lành |
| Phạm vi sửa/thực thi | Tái dùng suite/selection cũ; thay interface/report chỉ khi cần tích hợp |
| Đầu vào cần đọc | Canonical selection manifest, 13 legacy và ca cũ được chọn; metadata/run contract; preflight |
| Công việc cụ thể | Chạy suite được chọn tuần tự trong lab; giữ contract FAIL; ghi cleanup/evidence; thêm integration smoke CI cần thiết; không copy ID cũ thành test mới |
| Đầu ra | Run reports thật + smoke job + missing/known-issue register + handoff P10 |
| Definition of Done | Selection không trùng canonical; evidence đúng baseline; cleanup đạt hoặc báo lỗi; static CI không bị chặn bởi Extended; remote CI chưa chạy phải ghi rõ |
| Điều kiện dừng/giới hạn | Known issue không đổi PASS; PR fork thiếu secrets không giả integration đạt; chưa được push thì không đẩy để lấy log |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P10. Tái dùng regression/smoke đã chọn và nối CI integration tối thiểu. Giữ TC13 FAIL và tách thiếu điều kiện hạ tầng; không triển khai module mới.

##### P11 — Core delta: auth/session và policy

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P07 oracle nhóm AUTH/RBAC + P09; P10 ưu tiên đã ổn định |
| Chủ sở hữu đề xuất | Trâm |
| Phạm vi sửa/thực thi | Một nhóm ca AUTH hoặc RBAC mỗi lượt; không sửa auth Directus |
| Đầu vào cần đọc | TC14–TC17; reuse map; baseline auth services/policy; helper hiện có |
| Công việc cụ thể | Chọn một nhóm liên quan; chốt oracle access/refresh/session TTL; thêm fixture user/policy và assertions delta; reuse control; read-back/cleanup; chạy đúng nhóm khi được phép |
| Đầu ra | Test delta nhỏ + per-case report/cleanup + cập nhật RTM + handoff P11/<group> |
| Definition of Done | Không đổi semantics revoke JWT để test xanh; multi-policy expected có nguồn; user/policy cleanup đúng run; chỉ ghi PASS khi có run |
| Điều kiện dừng/giới hạn | Nếu auth và RBAC khác fixture/oracle, chia hai lượt; không quét admin API ngoài allowlist |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P11 với nhóm [AUTH hoặc RBAC] tôi chỉ định. Tái dùng helper/control, triển khai delta TC liên quan và kiểm nhóm đó; không làm đồng thời cả backlog Core.

##### P12 — Core delta: mô hình dữ liệu

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P07 oracle MODEL + P09; mô hình DB tạm được giao |
| Chủ sở hữu đề xuất | Trâm; Lành interface |
| Phạm vi sửa/thực thi | Chỉ TC18/TC19 hoặc subset đã chọn; không schema apply tổng quát |
| Đầu vào cần đọc | MODEL inventory; source/contract; snapshot/cleanup; reuse deny/read-back |
| Công việc cụ thể | Tạo collection/field thử trong namespace riêng; kiểm metadata và quyền; dùng dữ liệu động; bảo vệ collection cũ |
| Đầu ra | Nhóm MODEL tests + report và schema before/after + handoff P12 |
| Definition of Done | Không thay qa_articles/qa_categories; cleanup khớp snapshot; oracle field/permission đúng baseline; failure không bị che |
| Điều kiện dừng/giới hạn | Không thêm migration hoặc sửa field cũ; thiếu quyền quản trị hợp lệ = BLOCKED |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P12 cho nhóm MODEL đã chọn. Kiểm vòng đời metadata và deny quyền bằng collection thử riêng; không mở rộng sang schema apply hoặc sửa fixture cũ.

##### P13 — Core delta: file local và asset privacy

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P07 oracle FILES + P09 có storage riêng |
| Chủ sở hữu đề xuất | Trâm |
| Phạm vi sửa/thực thi | Chỉ TC26/TC27; không storage cloud/provider |
| Đầu vào cần đọc | File/folder/asset source baseline; multipart helper; policy owner/user khác; storage test mount |
| Công việc cụ thể | Upload/download hash roundtrip; resize control PNG; kiểm deny user khác; cleanup file rồi folder; không dùng file thật |
| Đầu ra | FILE local tests + hash/response evidence + storage cleanup + handoff P13 |
| Definition of Done | Bytes/hash/metadata và policy có oracle; asset transformation không lộ private content; còn object run sau cleanup thì FAIL cleanup |
| Điều kiện dừng/giới hạn | Không dùng S3/email/extension; không gọi load test hoặc public URL |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P13 cho Files local. Triển khai và kiểm roundtrip cùng asset privacy trong storage test; dùng helper và policy sẵn có, không tích hợp cloud.

##### P14 — REST contract/fuzz pilot có kiểm soát

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P07 subset inventory + P09 CLI gate; nhóm fixture đã đạt từ P10–P13 |
| Chủ sở hữu đề xuất | Nhân |
| Phạm vi sửa/thực thi | Chỉ một module REST nhỏ mỗi lượt; raw/guided có budget hữu hạn |
| Đầu vào cần đọc | Admin/actor OAS theo module; source inventory; raw/guided framework; checks/report/budget mục 9 |
| Công việc cụ thể | Export nguyên gốc/hash; đối chiếu route; chọn allowlist; thêm example/link trong overlay riêng; pilot raw rồi guided trên fixture khôi phục; replay finding đại diện |
| Đầu ra | Schema/diff + run config/report/coverage nếu có + reproducer và restore + handoff P14/<module> |
| Definition of Done | Không sửa raw contract; trợ giúp CLI đúng image; restore xác minh; stop_reason và FAIL/INCOMPLETE giữ; keyword coverage thiếu nguồn = NOT_MEASURED |
| Điều kiện dừng/giới hạn | Không chạy hết 22 nhóm/ba seed dài trong pilot; không coi positive schema data luôn hợp policy |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P14 cho module [tên] và budget pilot kế hoạch. Chạy raw/guided riêng, giữ failure và restore; không tăng ngân sách hoặc thêm module tự phát.

##### P15 — Nghiệm thu Automated Testing + CI — M2

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P08 + P10; P11–P14 theo selection Core đã chốt |
| Chủ sở hữu đề xuất | Lành tích hợp; Nhân/Trâm bằng chứng |
| Phạm vi sửa/thực thi | Rà và tích hợp đúng phạm vi Core; không viết thêm module để lấp số |
| Đầu vào cần đọc | Selection manifest, reports, coverage tool, CI static/smoke logs nếu có |
| Công việc cụ thể | Tính coverage subset; kiểm runtime metadata/cleanup/known issues; xem missing mandatory; sửa lỗi integration thuộc scope nếu được giao; tách status milestone và acceptance |
| Đầu ra | Acceptance record M2 + coverage summary/missing IDs + handoff P15 |
| Definition of Done | Mọi claim truy về run; CI chưa có run không coi đã xác minh; mandatory thiếu/FAIL không được gọi acceptance PASS; gap có owner |
| Điều kiện dừng/giới hạn | M2 evidence có thể hoàn thành báo cáo nhưng acceptance chưa đạt; không tự miễn required checks |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P15. Đối chiếu bằng chứng Core và CI với M2, xuất coverage/missing và kết luận có căn cứ. Không nâng cấp dependency hoặc bổ sung Extended.

##### P16 — Extended theo từng module/giao thức

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P07 scope Extended + P15 hoặc prerequisite subset đã ổn; environment gate riêng |
| Chủ sở hữu đề xuất | Trâm chức năng/UI; Nhân giao thức |
| Phạm vi sửa/thực thi | Một module hoặc một giao thức và vài hành vi liên quan mỗi lượt |
| Đầu vào cần đọc | Inventory/RTM subset; TC tương ứng phụ lục A; canonical/reuse map; feature/runtime và oracle |
| Công việc cụ thể | Chọn một đơn vị: bulk, M2M, Flow, History, Insight, Shares, Collaboration, Import, Schema, GraphQL hoặc Studio; design delta → implement → verify → cleanup → RTM; TC58/59 riêng verdict |
| Đầu ra | Handoff P16/<module> + case/report/evidence/missing; cập nhật scope selection nếu được duyệt |
| Definition of Done | Transport có client/assertion riêng; không dùng REST PASS thay UI/GraphQL; không kết luận module đầy đủ vì hai ca đại diện |
| Điều kiện dừng/giới hạn | Không chạy tất cả Extended trong một prompt; schema apply chỉ DB tạm; setup fail ghi BLOCKED downstream |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P16 cho [module/giao thức] với [TC/requirement]. Hoàn thành một nhóm nhỏ và bàn giao evidence/gap, giữ các module khác nguyên trạng.

##### P17 — Conditional và code coverage theo quyết định

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P05/P07 dependency/decision + quyền triển khai profile cụ thể |
| Chủ sở hữu đề xuất | Lành chốt; Nhân/Trâm theo nhóm |
| Phạm vi sửa/thực thi | Mỗi lượt chỉ một dependency/feature; không mặc định mở mọi tùy chọn |
| Đầu vào cần đọc | Conditional matrix; license/provider/scope decision; code coverage feasibility mục 6.5; TC40/41, 44/45, 52–57, 60–62 khi áp dụng |
| Công việc cụ thể | Trước hết kiểm applicability và điều kiện. Nếu đủ, lập/triển khai pilot một profile: Realtime hoặc extension/cache/limiter hoặc AI/MCP/deploy hoặc SDK hoặc instrumented source; nếu thiếu, ghi decision/gap/BLOCKED |
| Đầu ra | Handoff P17/<feature> + quyết định applicability; evidence pilot nếu chạy; code coverage NOT_MEASURED nếu chưa instrument đúng baseline |
| Definition of Done | N/A có nguồn; provider chỉ sink được duyệt; instrumented source đúng SHA/source-map và behavior control; không gán coverage từ HEAD khác |
| Điều kiện dừng/giới hạn | Không cài/bật provider thật, gửi email/deploy thật hoặc mua dịch vụ chỉ vì kế hoạch có tên; conditional chưa bắt buộc không chặn smoke Core |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P17 cho [feature]. Kiểm dependency/scope trước; làm pilot nếu điều kiện và quyền đã đủ, còn thiếu thì ghi rõ gap và dừng đúng phần phụ thuộc.

##### P18 — Chiến dịch nghiệm thu theo scope đã khóa

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P15 + P16/P17 bắt buộc trong selection; mọi cleanup/precondition đủ |
| Chủ sở hữu đề xuất | Nhân chạy; Trâm oracle; Lành điều phối |
| Phạm vi sửa/thực thi | Chỉ chiến dịch có manifest/budget duyệt; chạy shard tuần tự hoặc DB cách ly |
| Đầu vào cần đọc | Frozen baseline/selection/inventory revision; budgets; regression/fuzz/protocol suites ổn định |
| Công việc cụ thể | Kiểm preflight; chạy các nhóm đã chọn; lưu run status/evidence liên tục; restore trước nhóm sau; replay/dedup finding đại diện; ghi missing/skipped lý do |
| Đầu ra | Run manifest + reports/artifacts sanitized + coverage inputs + triage index + handoff P18 |
| Definition of Done | Không thay mẫu số hoặc xóa FAIL giữa run; timeout = INCOMPLETE kèm tool status; restore lỗi dừng reuse DB; không cộng request thành test/defect |
| Điều kiện dừng/giới hạn | Không kéo dài campaign tự phát; cancellation lưu phần đã có; không ghi experiment chưa chạy thành evidence |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P18 theo campaign manifest [đường dẫn]. Không tự thêm module hoặc tăng budget. Giữ mọi status và dừng phần dùng chung DB khi restore thất bại.

##### P19 — Full-Scope Coverage Evidence và báo cáo — M3

| Mục | Nội dung giao việc |
|---|---|
| Dependency | P18 hoặc bộ runs nghiệm thu có nguồn; P07 decisions; P08 calculator |
| Chủ sở hữu đề xuất | Lành tổng hợp; Nhân/Trâm xác nhận phần mình |
| Phạm vi sửa/thực thi | Chỉ tổng hợp/tính lại/viết báo cáo; không chạy lại toàn campaign để làm xanh |
| Đầu vào cần đọc | RTM/inventory/selection revision; run artifacts; findings; CI logs; decisions/exclusions |
| Công việc cụ thể | Tính coverage riêng từng tầng/transport/unit; đối chiếu missing mandatory; phân loại defect/schema/harness/env/unresolved; cập nhật báo cáo/demo/limitations và provenance |
| Đầu ra | M3 evidence package + coverage summary có tập tử/mẫu + acceptance/gap register + hướng dẫn tái lập + handoff P19 |
| Definition of Done | Không có % nếu mẫu số chưa khóa; NOT_MEASURED đúng nơi; full-scope gắn scope duyệt; acceptance chưa đạt được ghi rõ; không giả đóng góp/review người khác |
| Điều kiện dừng/giới hạn | Không gọi toàn hệ thống PASS từ REST hit hoặc số ca; chưa quyền publish thì chỉ lưu local |

**Prompt phase** — dùng cùng prompt nền:

> Chỉ thực hiện P19. Tổng hợp evidence M3, coverage và giới hạn theo scope đã khóa. Giữ mọi finding chưa kết luận và thiếu bằng chứng; không tạo dữ liệu chạy giả.

#### 12.5.7. Cách bắt đầu lượt tiếp theo

Giao **P00** trước. Sau handoff P00, dùng **P01** để khóa cấu trúc dữ liệu. Có thể giao **P02** sớm với quyền triển khai CI static rõ ràng trong khi inventory P03–P05 được xử lý từng lượt. Không bắt đầu bằng “triển khai tất cả 49 ca” hoặc “chạy toàn bộ Directus”.

Ví dụ giao việc ban đầu:

```text
Dùng prompt nền của mục 12.5.3. Chỉ thực hiện P00.
Quyền hiện tại: đọc repo và tạo/cập nhật tài liệu handoff P00; không sửa code,
không chạy API/test, không thay cấu hình, không commit/push.
Đầu ra: xác minh đầu vào và dependency cho P01; không làm trước P01.
```

#### 12.5.8. Prompt độc lập cho từng phase — sao chép và gửi ngay

**Cách dùng:** sao chép đúng **một khối prompt P00–P19** bên dưới và gửi để thực hiện phase đó. Mỗi prompt đã có ngữ cảnh, phạm vi, đầu ra, DoD và giới hạn quyền; **không cần ghép thêm prompt nền, không cần điền ô trống**. Thực hiện xong một phase thì bàn giao và dừng; người dùng gửi prompt phase tiếp theo khi muốn tiếp tục. Đây là bộ prompt thay cho prompt chạy xuyên suốt toàn chuỗi trước đây.

Thứ tự theo dependency ở mục 12.5.5; P02 được làm sớm sau P00/P01. P11, P14, P16 và P17 có nhiều batch thì model xử lý tuần tự các batch thuộc **chính phase được giao**, ghi checkpoint để tiếp tục, không tự mở phase khác. Phase đang có handoff thì tiếp tục phần chưa hoàn tất, không làm lại từ đầu.

Các prompt chỉ có hiệu lực triển khai khi được người dùng gửi hoặc viện dẫn như yêu cầu thực hiện; lần sửa tài liệu này **không thực thi phase nào**.

##### Prompt P00 — Chốt ảnh chụp đầu vào

```text
Hãy thực hiện riêng phase P00 — Chốt ảnh chụp đầu vào trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P00 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: Khởi đầu.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
AGENTS.md; kế hoạch mục 1–2, 5, 17; README; manifest/baseline.yaml; git status/remotes/HEAD.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Chỉ đọc repo/Git và tạo hoặc cập nhật tài liệu handoff. Không sửa code/config, không cài package, không chạy test/API, không khởi động lab.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Ghi source/image baseline, branch/dirty state, vị trí repo DAMH và Directus; xác định artifact còn truy cập được; không đọc env thật; phân biệt lịch sử và runtime.

ĐẦU RA
docs/coverage/handoffs/P00.md: nguồn đã đọc, SHA, thay đổi có sẵn, CHƯA XÁC MINH và đường dẫn đầu vào.

DEFINITION OF DONE
Mọi fact có source; xác định đúng repo harness; không sửa/suy trạng thái lab; chỉ hoàn thành audit đầu vào.
Giới hạn cần giữ: Không fetch/pull/checkout/build/start lab để làm audit; thiếu source object thì ghi gap.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P01 — Khóa hợp đồng dữ liệu coverage

```text
Hãy thực hiện riêng phase P01 — Khóa hợp đồng dữ liệu coverage trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P01 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P00.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Mục 6.1–6.8, 7; handoff P00.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được tạo/cập nhật hợp đồng JSON Schema, ví dụ thiết kế và tài liệu; chỉ kiểm cấu trúc dữ liệu offline cần thiết. Không viết test runner, không gọi API hoặc khởi động lab.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Chốt kiểu dữ liệu/enum/key/ref của manifest, inventory, requirements, catalog, RTM, executions, decisions/gaps và summary; schema version; null/UNKNOWN/NOT_MEASURED; DIRECT/SUPPORTING; chuẩn hóa operation/alias.

ĐẦU RA
docs/coverage/schemas/ và ví dụ tối thiểu; docs/coverage/handoffs/P01.md; đường dẫn là đề xuất cần kiểm tra xung đột trước tạo.

DEFINITION OF DONE
Định nghĩa có thể biểu diễn requirement nhiều TC, TC nhiều requirement, alias, FAIL/INCOMPLETE/cleanup riêng; ví dụ không có số coverage giả; không rename interface cũ.
Giới hạn cần giữ: Không dùng CSV đơn làm mất quan hệ; không đưa secret/run thực giả vào example.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P02 — CI static/offline sớm

```text
Hãy thực hiện riêng phase P02 — CI static/offline sớm trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P02 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P00 + phần hợp đồng cần dùng của P01; không đợi P03–P07.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Mục 10–11; scripts/tests và cấu hình dependency đã có; handoff P00/P01.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được sửa workflow static/offline và script hỗ trợ tối thiểu trong DAMH, chạy các checks offline cần thiết. Không gọi API, chạy integration/fuzz, khởi động lab hoặc push để kích hoạt Actions. Tái dùng dependency đã pin; thiếu công cụ ghi rõ thay vì nâng/cài toàn máy.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Kiểm lệnh offline hiện hữu; chọn syntax/config/catalog và unit harness cần thiết; thiết kế rồi tạo workflow static khi lượt giao việc cho phép; tách integration chưa chạy; artifact nhỏ, exit code thật.

ĐẦU RA
Workflow static/offline + tài liệu lệnh tái lập + handoff P02; không push để kích hoạt Actions nếu chưa có quyền.

DEFINITION OF DONE
Local offline checks được chạy đúng phạm vi; remote CI chỉ ghi đã chạy khi có run thật; integration thiếu môi trường ghi rõ, không coi static là API PASS.
Giới hạn cần giữ: Chưa có quyền tạo workflow thì chỉ làm thiết kế có thể review; thiếu dependency không cài/nâng toàn máy ngầm.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P03 — Inventory auth và API hệ thống

```text
Hãy thực hiện riêng phase P03 — Inventory auth và API hệ thống trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P03 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P00 + P01.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Source app.ts/router đúng SHA baseline; manifest; schema hợp đồng P01; kế hoạch mục 3–4.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được đọc source/config mẫu/report và tạo hoặc sửa inventory, RTM, catalog mapping, decision/gap records và tài liệu thuộc phase. Không chạy test/API, không sửa harness/config runtime, không khởi động lab. OAS runtime chưa có thì ghi gap, không tự export live trong phase này.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Kiểm mount và router con auth/users/roles/policies/permissions/access; collections/fields/relations/schema; settings/server/license/metrics; ghi method/path/flag/quyền/source_refs và gap OAS.

ĐẦU RA
Inventory shard auth-system theo schema P01 + danh sách route chưa phân giải + handoff P03.

DEFINITION OF DONE
Mỗi route được ghi có source@SHA; route điều kiện giữ flag/UNKNOWN; không lấy số router làm số operation; không gộp template với ID thật.
Giới hạn cần giữ: Chưa có admin OAS runtime thì oas_presence UNKNOWN, không bỏ route; source HEAD không thay bản pin.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P04 — Inventory nội dung và chức năng native

```text
Hãy thực hiện riêng phase P04 — Inventory nội dung và chức năng native trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P04 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P00 + P01; dùng quy tắc P03.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Source baseline routers/services; shard P03; hợp đồng P01.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được đọc source/config mẫu/report và tạo hoặc sửa inventory, RTM, catalog mapping, decision/gap records và tài liệu thuộc phase. Không chạy test/API, không sửa harness/config runtime, không khởi động lab. OAS runtime chưa có thì ghi gap, không tự export live trong phase này.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Kiểm items/query/validation/bulk, files/folders/assets/tus, flows/operations, history/versions, dashboards/panels/presets, shares/comments/notifications/translations/utils/import-export; giữ capability không có operation độc lập.

ĐẦU RA
Inventory shard content-native + coverage của chính đợt kiểm kê + gap list + handoff P04.

DEFINITION OF DONE
Không trùng khóa với shard P03; mỗi capability có route/ref hoặc lý do; path động chuẩn hóa; biết nhóm nào chưa kiểm kê, không gọi inventory hoàn chỉnh sớm.
Giới hạn cần giữ: Không đếm một query parameter thành HTTP operation mới; hạn chế xuất toàn monorepo vào context.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P05 — Inventory giao thức và tính năng có điều kiện

```text
Hãy thực hiện riêng phase P05 — Inventory giao thức và tính năng có điều kiện trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P05 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P01; source shards P03/P04 nếu sẵn.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Source graphql/websocket/app/extensions/ai/mcp/deployment/sdk; Compose và env mẫu; mục 3.2.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được đọc source/config mẫu/report và tạo hoặc sửa inventory, RTM, catalog mapping, decision/gap records và tài liệu thuộc phase. Không chạy test/API, không sửa harness/config runtime, không khởi động lab. OAS runtime chưa có thì ghi gap, không tự export live trong phase này.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Lập capability GraphQL/Realtime/Studio/extensions/AI/MCP/deployment/SDK và tích hợp; nối REST route nếu có nhưng inventory riêng giao thức; deployed_state có nguồn; matrix conditional dependency.

ĐẦU RA
Inventory shard non-rest-conditional; dependency/decision/gap records; handoff P05.

DEFINITION OF DONE
Không dùng REST OAS thay GraphQL/WS/UI; mọi feature có applicability/UNKNOWN và nguồn; source-present không tự bằng runtime-enabled.
Giới hạn cần giữ: Không gọi provider thật, cài extension hoặc chuyển Conditional thành N/A chỉ vì thiếu credential.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P06 — Canonical map và tái sử dụng catalog

```text
Hãy thực hiện riêng phase P06 — Canonical map và tái sử dụng catalog trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P06 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P01 + catalog 257; đối chiếu mục 8.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Catalog 257; scenario/invariant và report nguồn; TC01–TC13; mục 5, 8; phụ lục A/B.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được đọc source/config mẫu/report và tạo hoặc sửa inventory, RTM, catalog mapping, decision/gap records và tài liệu thuộc phase. Không chạy test/API, không sửa harness/config runtime, không khởi động lab. OAS runtime chưa có thì ghi gap, không tự export live trong phase này.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Map toàn 257 ID và alias TC; ghi exact-reuse/partial/delta/revised/new cùng lý do; giữ lineage TC42/49/55 và TC58–TC62; đối chiếu các nhận định reuse trong kế hoạch bằng field/oracle/source thực.

ĐẦU RA
Canonical catalog + alias/reuse mapping + discrepancy log + handoff P06; theo schema P01.

DEFINITION OF DONE
Mỗi ID gốc có đúng mapping hoặc gap; alias không tăng số; historical execution không bị đổi baseline; phân biệt DIRECT/SUPPORTING; sửa nhận định kế hoạch nếu tìm được bằng chứng mới.
Giới hạn cần giữ: Catalog NOT_RUN/OPEN không được lấy làm PASS; chia đọc theo group nhưng phải có checklist đủ 257 ID.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P07 — Khóa RTM, scope và Coverage Baseline — M1

```text
Hãy thực hiện riêng phase P07 — Khóa RTM, scope và Coverage Baseline — M1 trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P07 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P03 + P04 + P05 + P06; P01.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Inventory shards; canonical map; mục 3.2, 4.1, 6 và decisions giảng viên có thật.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được đọc source/config mẫu/report và tạo hoặc sửa inventory, RTM, catalog mapping, decision/gap records và tài liệu thuộc phase. Không chạy test/API, không sửa harness/config runtime, không khởi động lab. OAS runtime chưa có thì ghi gap, không tự export live trong phase này.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Merge inventory; kiểm missing route/capability; tạo requirement/oracle/risk I/L/C; gắn DIRECT/SUPPORTING; Core/Extended/Conditional; chốt selection baseline revision hoặc gap/UNKNOWN; đề xuất MVP.

ĐẦU RA
Baseline manifest + RTM/requirements/inventory thống nhất + decision/gap register + handoff P07/M1.

DEFINITION OF DONE
Mọi requirement áp dụng có test hoặc gap; tất cả source groups đã được xét; mẫu số subset rõ; chưa có approval scope thì giữ đề xuất, không giả xác nhận thầy; NOT_MEASURED khi chưa đo.
Giới hạn cần giữ: Không tự chốt mọi Conditional ngoài scope; toàn inventory còn UNKNOWN thì không tuyên bố coverage toàn hệ thống đã đo.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P08 — Validator và bộ tính coverage offline

```text
Hãy thực hiện riêng phase P08 — Validator và bộ tính coverage offline trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P08 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P01 + baseline subset P07.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Công thức nguyên trạng mục 6.2–6.8; baseline/RTM và reports thật dùng làm đầu vào.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai validator/calculator coverage và kiểm thử offline có ý nghĩa trong DAMH. Không gọi SUT, không sửa expected/report lịch sử hoặc cấu hình runtime.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Viết validator/reference resolver và calculator tập D/E/V/O; dedup alias; run-selection policy; phân biệt cleanup/infra/FAIL; missing ID lists; không tính partial schema thành PASS.

ĐẦU RA
Công cụ coverage offline + mẫu output + checks có ý nghĩa cho alias/FAIL/BLOCKED/many-to-many + handoff P08.

DEFINITION OF DONE
Đối chiếu kiểm tay các tình huống mục 6.8; schema/reference lỗi trả failure; không có execution thì execution coverage NOT_MEASURED theo ngữ cảnh; không sinh evidence thật từ sample.
Giới hạn cần giữ: Chỉ kiểm bằng fixture offline đã đánh dấu; giữ baseline/report nguồn bất biến.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P09 — Profile môi trường thử và preflight

```text
Hãy thực hiện riêng phase P09 — Profile môi trường thử và preflight trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P09 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P00 + Core subset P07; được giao triển khai môi trường.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Compose/env mẫu/manifest; interface hiện tại; nguồn CLI/version đúng image; dependency/license gate.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được tạo/sửa profile thử và preflight trong DAMH; chuẩn bị dependency trong môi trường dự án/container theo bản pin, pull image đã pin và khởi động lab thử riêng khi cần. Chỉ thao tác tài nguyên đã xác minh thuộc lab thử; không reset/xóa/ghi đè lab cũ, DB demo hoặc volume chung. Chưa chạy campaign.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Thiết kế namespace network/volume/storage theo run; tái dùng lab hiện hữu nếu đúng; kiểm health/version/license/policy/fixture và CLI help bằng thao tác phù hợp; làm rõ tracecov; không sửa raw OAS.

ĐẦU RA
Profile test/CI riêng nếu cần + preflight report đã sanitize + rollback/cleanup procedure + handoff P09.

DEFINITION OF DONE
Định danh đúng lab và actor; URL local; không đụng DB khác; credentials không ra log; điều kiện thiếu được BLOCKED; tracecov chưa xác minh không chặn việc ghi operation evidence hợp lệ.
Giới hạn cần giữ: Không reset DB đang demo hoặc sửa license; pull/build/start chỉ trong quyền lượt giao; dừng phần thiếu license mà tiếp tục kiểm tĩnh độc lập.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P10 — Regression tái dùng và smoke CI

```text
Hãy thực hiện riêng phase P10 — Regression tái dùng và smoke CI trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P10 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P06 + P07 subset + P09; nối P02 khi sẵn.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Canonical selection manifest, 13 legacy và ca cũ được chọn; metadata/run contract; preflight.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Chạy suite được chọn tuần tự trong lab; giữ contract FAIL; ghi cleanup/evidence; thêm integration smoke CI cần thiết; không copy ID cũ thành test mới.

ĐẦU RA
Run reports thật + smoke job + missing/known-issue register + handoff P10.

DEFINITION OF DONE
Selection không trùng canonical; evidence đúng baseline; cleanup đạt hoặc báo lỗi; static CI không bị chặn bởi Extended; remote CI chưa chạy phải ghi rõ.
Giới hạn cần giữ: Known issue không đổi PASS; PR fork thiếu secrets không giả integration đạt; chưa được push thì không đẩy để lấy log.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P11 — Core delta: auth/session và policy

```text
Hãy thực hiện riêng phase P11 — Core delta: auth/session và policy trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P11 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P07 oracle nhóm AUTH/RBAC + P09; P10 ưu tiên đã ổn định.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
TC14–TC17; reuse map; baseline auth services/policy; helper hiện có.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Chọn một nhóm liên quan; chốt oracle access/refresh/session TTL; thêm fixture user/policy và assertions delta; reuse control; read-back/cleanup; chạy đúng nhóm khi được phép.
Xử lý AUTH rồi RBAC theo RTM đã chốt, từng nhóm fixture/oracle một; không gộp mọi ca vào một thay đổi lớn.

ĐẦU RA
Test delta nhỏ + per-case report/cleanup + cập nhật RTM + handoff P11/<group>.

DEFINITION OF DONE
Không đổi semantics revoke JWT để test xanh; multi-policy expected có nguồn; user/policy cleanup đúng run; chỉ ghi PASS khi có run.
Giới hạn cần giữ: Nếu auth và RBAC khác fixture/oracle, chia hai lượt; không quét admin API ngoài allowlist.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P12 — Core delta: mô hình dữ liệu

```text
Hãy thực hiện riêng phase P12 — Core delta: mô hình dữ liệu trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P12 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P07 oracle MODEL + P09; mô hình DB tạm được giao.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
MODEL inventory; source/contract; snapshot/cleanup; reuse deny/read-back.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Tạo collection/field thử trong namespace riêng; kiểm metadata và quyền; dùng dữ liệu động; bảo vệ collection cũ.

ĐẦU RA
Nhóm MODEL tests + report và schema before/after + handoff P12.

DEFINITION OF DONE
Không thay qa_articles/qa_categories; cleanup khớp snapshot; oracle field/permission đúng baseline; failure không bị che.
Giới hạn cần giữ: Không thêm migration hoặc sửa field cũ; thiếu quyền quản trị hợp lệ = BLOCKED.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P13 — Core delta: file local và asset privacy

```text
Hãy thực hiện riêng phase P13 — Core delta: file local và asset privacy trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P13 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P07 oracle FILES + P09 có storage riêng.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
File/folder/asset source baseline; multipart helper; policy owner/user khác; storage test mount.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Upload/download hash roundtrip; resize control PNG; kiểm deny user khác; cleanup file rồi folder; không dùng file thật.

ĐẦU RA
FILE local tests + hash/response evidence + storage cleanup + handoff P13.

DEFINITION OF DONE
Bytes/hash/metadata và policy có oracle; asset transformation không lộ private content; còn object run sau cleanup thì FAIL cleanup.
Giới hạn cần giữ: Không dùng S3/email/extension; không gọi load test hoặc public URL.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P14 — REST contract/fuzz pilot có kiểm soát

```text
Hãy thực hiện riêng phase P14 — REST contract/fuzz pilot có kiểm soát trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P14 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P07 subset inventory + P09 CLI gate; nhóm fixture đã đạt từ P10–P13.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Admin/actor OAS theo module; source inventory; raw/guided framework; checks/report/budget mục 9.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Export nguyên gốc/hash; đối chiếu route; chọn allowlist; thêm example/link trong overlay riêng; pilot raw rồi guided trên fixture khôi phục; replay finding đại diện.
Chọn module REST đủ fixture/oracle và rủi ro cao nhất chưa pilot trong selection đã chốt; chạy từng module, giữ budget mục 9. Chưa có selection/budget hợp lệ thì hoàn tất thiết kế phần độc lập và ghi điều kiện thiếu.

ĐẦU RA
Schema/diff + run config/report/coverage nếu có + reproducer và restore + handoff P14/<module>.

DEFINITION OF DONE
Không sửa raw contract; trợ giúp CLI đúng image; restore xác minh; stop_reason và FAIL/INCOMPLETE giữ; keyword coverage thiếu nguồn = NOT_MEASURED.
Giới hạn cần giữ: Không chạy hết 22 nhóm/ba seed dài trong pilot; không coi positive schema data luôn hợp policy.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P15 — Nghiệm thu Automated Testing + CI — M2

```text
Hãy thực hiện riêng phase P15 — Nghiệm thu Automated Testing + CI — M2 trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P15 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P08 + P10; P11–P14 theo selection Core đã chốt.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Selection manifest, reports, coverage tool, CI static/smoke logs nếu có.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được chạy công cụ coverage/report offline và chỉnh tài liệu/bộ dữ liệu tổng hợp cần cho nghiệm thu phase. Không chạy lại API/campaign, không sửa test/config hoặc expected để làm báo cáo xanh; thiếu run phải ghi rõ.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Tính coverage subset; kiểm runtime metadata/cleanup/known issues; xem missing mandatory; sửa lỗi integration thuộc scope nếu được giao; tách status milestone và acceptance.

ĐẦU RA
Acceptance record M2 + coverage summary/missing IDs + handoff P15.

DEFINITION OF DONE
Mọi claim truy về run; CI chưa có run không coi đã xác minh; mandatory thiếu/FAIL không được gọi acceptance PASS; gap có owner.
Giới hạn cần giữ: M2 evidence có thể hoàn thành báo cáo nhưng acceptance chưa đạt; không tự miễn required checks.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P16 — Extended theo từng module/giao thức

```text
Hãy thực hiện riêng phase P16 — Extended theo từng module/giao thức trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P16 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P07 scope Extended + P15 hoặc prerequisite subset đã ổn; environment gate riêng.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Inventory/RTM subset; TC tương ứng phụ lục A; canonical/reuse map; feature/runtime và oracle.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được triển khai code/test/fixture/profile thử cần thiết trong DAMH và chạy kiểm tra local phù hợp trên lab thử cách ly, đúng baseline/URL/actor/allowlist. Chỉ ghi/xóa dữ liệu do phase tạo, có cleanup/restore; không sửa fixture/DB demo cũ, không nâng dependency/baseline để né lỗi. Thiếu môi trường thì ghi BLOCKED và làm phần độc lập thuộc phase.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Chọn một đơn vị: bulk, M2M, Flow, History, Insight, Shares, Collaboration, Import, Schema, GraphQL hoặc Studio; design delta → implement → verify → cleanup → RTM; TC58/59 riêng verdict.
Đọc selection để chọn Extended bắt buộc chưa hoàn tất theo rủi ro; thực hiện từng module/giao thức với verdict riêng. Không tự chọn toàn bộ Extended chỉ vì danh sách có tên. Scope chưa chốt thì chỉ chuẩn bị thiết kế và ghi quyết định thiếu.

ĐẦU RA
Handoff P16/<module> + case/report/evidence/missing; cập nhật scope selection nếu được duyệt.

DEFINITION OF DONE
Transport có client/assertion riêng; không dùng REST PASS thay UI/GraphQL; không kết luận module đầy đủ vì hai ca đại diện.
Giới hạn cần giữ: Không chạy tất cả Extended trong một prompt; schema apply chỉ DB tạm; setup fail ghi BLOCKED downstream.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P17 — Conditional và code coverage theo quyết định

```text
Hãy thực hiện riêng phase P17 — Conditional và code coverage theo quyết định trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P17 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P05/P07 dependency/decision + quyền triển khai profile cụ thể.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Conditional matrix; license/provider/scope decision; code coverage feasibility mục 6.5; TC40/41, 44/45, 52–57, 60–62 khi áp dụng.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được khảo sát và triển khai pilot local cho từng feature đã được chốt áp dụng, đủ dependency/license và có profile thử cách ly; được sửa harness/config test tương ứng trong DAMH. Chỉ dùng sink/provider thử, không gọi provider trả phí/dịch vụ thật. Code coverage cần sửa/build source upstream ngoài harness thì ghi phương án/gap, không tự sửa checkout.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Trước hết kiểm applicability và điều kiện. Nếu đủ, lập/triển khai pilot một profile: Realtime hoặc extension/cache/limiter hoặc AI/MCP/deploy hoặc SDK hoặc instrumented source; nếu thiếu, ghi decision/gap/BLOCKED.
Xử lý từng Conditional bắt buộc có quyết định và môi trường đủ; phần còn thiếu giữ gap/BLOCKED, không tự mua/bật provider hoặc biến thành N/A. Không có feature đủ điều kiện thì hoàn thành dependency assessment và nêu phần triển khai bị chặn.

ĐẦU RA
Handoff P17/<feature> + quyết định applicability; evidence pilot nếu chạy; code coverage NOT_MEASURED nếu chưa instrument đúng baseline.

DEFINITION OF DONE
N/A có nguồn; provider chỉ sink được duyệt; instrumented source đúng SHA/source-map và behavior control; không gán coverage từ HEAD khác.
Giới hạn cần giữ: Không cài/bật provider thật, gửi email/deploy thật hoặc mua dịch vụ chỉ vì kế hoạch có tên; conditional chưa bắt buộc không chặn smoke Core.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P18 — Chiến dịch nghiệm thu theo scope đã khóa

```text
Hãy thực hiện riêng phase P18 — Chiến dịch nghiệm thu theo scope đã khóa trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P18 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P15 + P16/P17 bắt buộc trong selection; mọi cleanup/precondition đủ.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
Frozen baseline/selection/inventory revision; budgets; regression/fuzz/protocol suites ổn định.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được chạy các suite/campaign trên lab thử đã xác minh theo selection, allowlist và budget có nguồn; ghi artifacts, replay đại diện và cleanup tài nguyên do run tạo. Không tự thêm module, tăng budget, reset DB cũ hoặc sửa test/config/expected giữa campaign.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Kiểm preflight; chạy các nhóm đã chọn; lưu run status/evidence liên tục; restore trước nhóm sau; replay/dedup finding đại diện; ghi missing/skipped lý do.

ĐẦU RA
Run manifest + reports/artifacts sanitized + coverage inputs + triage index + handoff P18.

DEFINITION OF DONE
Không thay mẫu số hoặc xóa FAIL giữa run; timeout = INCOMPLETE kèm tool status; restore lỗi dừng reuse DB; không cộng request thành test/defect.
Giới hạn cần giữ: Không kéo dài campaign tự phát; cancellation lưu phần đã có; không ghi experiment chưa chạy thành evidence.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

##### Prompt P19 — Full-Scope Coverage Evidence và báo cáo — M3

```text
Hãy thực hiện riêng phase P19 — Full-Scope Coverage Evidence và báo cáo — M3 trong repo DAMH,
theo docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md, mục 12.5.

Bắt đầu: đọc AGENTS.md áp dụng, git status, handoff P19 nếu đã có và
handoff dependency liên quan. Chỉ đọc các mục/source cần cho phase.
Nếu đã làm một phần thì tiếp tục phần còn lại, không làm lại toàn repo.
Dependency cần đối chiếu: P18 hoặc bộ runs nghiệm thu có nguồn; P07 decisions; P08 calculator.
Không giả dependency đã hoàn tất hoặc người khác đã xác nhận.

ĐẦU VÀO
RTM/inventory/selection revision; run artifacts; findings; CI logs; decisions/exclusions.

PHẠM VI VÀ QUYỀN TÔI GIAO CHO PHASE NÀY
Được chạy công cụ coverage/report offline và chỉnh tài liệu/bộ dữ liệu tổng hợp cần cho nghiệm thu phase. Không chạy lại API/campaign, không sửa test/config hoặc expected để làm báo cáo xanh; thiếu run phải ghi rõ.
Không commit/push/tạo PR/issue, xuất bản, liên hệ người khác hoặc tạo sub-agent.
Source ../directus mặc định chỉ đọc đúng baseline; không đổi checkout.
Bảo toàn thay đổi đang có, không in secret hay sao chép credential vào report.

CÔNG VIỆC
Tính coverage riêng từng tầng/transport/unit; đối chiếu missing mandatory; phân loại defect/schema/harness/env/unresolved; cập nhật báo cáo/demo/limitations và provenance.

ĐẦU RA
M3 evidence package + coverage summary có tập tử/mẫu + acceptance/gap register + hướng dẫn tái lập + handoff P19.

DEFINITION OF DONE
Không có % nếu mẫu số chưa khóa; NOT_MEASURED đúng nơi; full-scope gắn scope duyệt; acceptance chưa đạt được ghi rõ; không giả đóng góp/review người khác.
Giới hạn cần giữ: Không gọi toàn hệ thống PASS từ REST hit hoặc số ca; chưa quyền publish thì chỉ lưu local.

Giữ nguyên lịch sử TC01–TC13, report và raw OpenAPI. Tái dùng canonical
ID/helper/fixture/oracle trước khi tạo mới. Không đổi FAIL thành PASS,
không cộng alias/request/retry/generated examples thành ca độc lập,
không bịa coverage; chưa đo ghi NOT_MEASURED, chưa rõ ghi CHƯA XÁC MINH.
Phân biệt trạng thái hoàn thành phase với verdict test và acceptance.

Thực hiện tới DoD trong phạm vi trên; không dừng ở việc lập lại kế hoạch
hoặc xin xác nhận bước thông thường đã được giao. Nếu thiếu điều kiện thật,
ghi gap có nguồn và chỉ dừng phần phụ thuộc; làm tiếp phần độc lập của phase.
Không tự chuyển sang phase khác.

Cuối lượt cập nhật handoff theo mục 12.5.4: input/baseline, file thay đổi,
checks thực sự đã chạy hoặc chưa chạy, evidence, DoD, gap và next action.
Nếu context/phiên không đủ, lưu checkpoint của batch chưa xong.
Trả lời ngắn: đã làm gì, ở đâu, kết quả thật, còn thiếu gì, phase tiếp theo.
```

## 13. Checklist theo mốc nghiệm thu

| Tiến độ | Mốc / công việc | Người đề xuất | Dependency / bằng chứng để đánh dấu |
|---|---|---|---|
| [ ] | M1 xác nhận baseline source/image/runtime khi được triển khai | Lành | Manifest/hash/version và gap runtime |
| [ ] | M1 inventory toàn chức năng/route/transport, kể cả Conditional | Nhân | Records máy đọc được + source_refs; source–OAS gaps |
| [ ] | M1 map 257 ID, canonical/alias, DIRECT/SUPPORTING | Trâm | Crosswalk mục 8 và chi tiết Phụ lục A thành dữ liệu phiên bản hóa |
| [ ] | M1 chốt Core/Extended/Conditional và I/L/C | Lành + Trâm | Decisions thầy/nhóm hoặc UNKNOWN có owner |
| [ ] | M1 CI static/offline sớm | Lành | Log CI và artifact; không đợi toàn module |
| [ ] | M2 reuse regression/smoke và fixture gate | Trâm | Selection manifest, evidence/cleanup; license đủ |
| [ ] | M2 functional Core ngoài hai collection | Trâm | Từng TC có oracle/control/version và missing |
| [ ] | M2 CLI/tracecov gate, raw/guided pilot | Nhân | Help/source/image evidence, schema hash/report |
| [ ] | M2 smoke CI và báo coverage subset | Lành + Nhân | Run CI, counters khớp kiểm tay, known FAIL giữ |
| [ ] | M3 Extended đã chốt gồm protocol/UI nếu áp dụng | Trâm + Nhân | Verdict riêng từng transport; dependency/gap |
| [ ] | M3 Conditional decisions và provider gate | Lành | N/A có nguồn hoặc BLOCKED nếu mandatory |
| [ ] | M3 tổng hợp evidence, coverage, triage và báo cáo | Cả nhóm | Recompute, missing IDs, giới hạn và nguồn thật |

Các ô thể hiện công việc tương lai; rà soát tài liệu không tự hoàn tất milestone hoặc xác nhận thành viên đã làm.


## 14. Rủi ro và biện pháp

| Rủi ro | Dấu hiệu phát hiện | Biện pháp / người xử lý |
|---|---|---|
| Source HEAD khác baseline | SHA không trùng | Lành dùng object baseline/checkout riêng được phép khi triển khai; không sửa upstream hiện tại |
| OAS động theo actor/fixture | Admin/Reader thiếu operation | Nhân union source/OAS, giữ schema actor và liệt kê gap |
| CLI/tracecov không tái lập | Help không có coverage flag | Nhân dừng coverage stage, truy nguồn pipeline; không cài/nâng ngầm |
| Thiếu license trên CI | doctor/policy precondition lỗi | Lành cấu hình license CI hợp lệ hoặc job BLOCKED, giữ static hoạt động |
| Dữ liệu bị fuzz xóa | Snapshot diff ngoài namespace | Trâm fixture riêng; allowlist; stop-on-restore-fail |
| Timeout bị coi PASS | stop_reason=max_time | Nhân giữ FAIL và INCOMPLETE riêng, liệt kê thiếu |
| Thêm hàng loạt ca trùng | Cùng oracle/actor/input partition | Trâm dedup với 257 ID, alias không nhân số ca |
| Dữ liệu nhạy cảm trong artifacts | Header/body/cookie chứa token | Lành sanitizer và review trước upload, hạn retention |
| UI/Realtime flaky | Sai thứ tự hoặc chờ không giới hạn | Trâm/Nhân dùng event correlation, bounded waits, seed riêng; không retry thành PASS mà mất lần lỗi |
| Toàn hệ thống quá rộng cho môn học | Budget vượt lịch | Lành chốt core/conditional và mức coverage với thầy; giữ gap rõ |
| Unknown oracle | Chỉ biết actual lần đầu | BLOCKED tới khi có nguồn; không tự học expected từ runtime |
| Scope nhiều DB/tải/provider | Chưa có môi trường | Ghi CHƯA XÁC MINH/BLOCKED; lập estimate riêng sau quyết định |

## 15. Tiêu chí hoàn thành đồ án mở rộng

Đề xuất để giảng viên duyệt, không phải trích nguyên yêu cầu môn học:

- Inventory toàn bộ nhóm chức năng/transport bản pin đã được review; mọi mục có applicability hoặc gap cần xử lý. Không bỏ qua module vì không có OAS.
- RTM khóa requirement áp dụng; mọi requirement có test và oracle đủ nguồn hoặc ghi thiếu. Mục tiêu thiết kế 100% tập requirement đã chốt; không gọi là 100% Directus.
- Mandatory P1 trong scope nghiệm thu đã chốt thực thi đủ, không còn BLOCKED/NOT_RUN/INCOMPLETE; FAIL nghiêm trọng về quyền/mất dữ liệu phải xử lý hoặc giảng viên chấp nhận cụ thể; không âm thầm đổi PASS.
- REST có inventory method/path hoàn chỉnh; mục tiêu mỗi operation áp dụng có positive/negative phù hợp, hoặc lý do đặc thù rõ; báo hit và positive riêng.
- GraphQL, realtime và Studio có bằng chứng theo requirement riêng, không dùng REST để thay. Conditional N/A cần quyết định; thuộc phạm vi nhưng chưa chạy phải nêu gap và chưa đạt mục tiêu tương ứng.
- Fuzz có budget/seed/schema/config/report và reproduction; campaign hết giờ không biến thành exhaustive. Regression chứa các finding tái hiện được, giữ failed contract.
- Coverage requirement/module/API/schema tính lại được từ artifact; code coverage đo hoặc NOT_MEASURED cùng lý do. Không đặt ngưỡng branch tùy ý trước pilot.
- CI static/offline và smoke Core tích hợp sớm; extended pilot theo scope đã chốt; artifact sạch secret; cleanup/restore được kiểm; không che exit failure.
- Bàn giao hướng dẫn, baseline digest, dependency/config mẫu, script, report, RTM, failure register, limitations và đóng góp thật. Chưa có bằng chứng dựng lại thì không tự nhận tái lập trên máy thứ hai.

## 16. Những điểm cần xác nhận với giảng viên

1. “Toàn hệ thống” áp dụng mọi tính năng bật trong bản 12.5.0 hay mọi tùy chọn có thể bật? Data Studio, SDK, AI/MCP/deployments, SSO/MFA, đa DB, tải và security depth cần mức nào?
2. Mục tiêu coverage bắt buộc: requirement/operation/module/schema hay cả code branch? Có chấp nhận NOT_MEASURED code khi chỉ dùng image không instrument?
3. Có chấp nhận N/A cho provider/license trả phí và chức năng không triển khai? Ai xác nhận và cần bằng chứng gì?
4. TC13 contract FAIL cùng aggregate/export/projection OPEN được đánh giá như thế nào khi không sửa mã Directus? Tiêu chí chấp nhận known issue ra sao?
5. Thời gian bảo vệ, budget runner và mức CI tối thiểu là gì? Mốc giữa kỳ cũ đã qua; không backdate kế hoạch này.
6. Bộ 13 tiếp tục là bộ demo hay cần cập nhật báo cáo chính theo catalog mới? Giữ mã TC và alias lịch sử như mục 5.

Những câu hỏi này không cản việc tạo kế hoạch và audit; chỉ chặn quyết định phạm vi/triển khai phụ thuộc.

## 17. Nguồn, bằng chứng và cách kiểm chứng

### 17.1. Nguồn repository

- [AGENTS.md](../AGENTS.md): vai trò nhóm, baseline, nguyên tắc trung thực, scope cũ. Yêu cầu mới cho phép lập kế hoạch mở rộng, chưa triển khai.
- [README](../README.md): 13 ca đại diện, lựa chọn course/short, cách chạy, phạm vi hai collection.
- [Manifest](../manifest/baseline.yaml), [Compose](../compose.yaml), [env mẫu](../config/lab.env.example): version/digest/config; không đọc/in file env thật.
- [Test matrix](test-matrix.md), [test model](phan2/02-test-model-va-test-cases.md), [thiết kế mở rộng](HoanThanhPlan/03-thiet-ke-test-va-coverage.md): operation/scenario, invariant, query/pairwise và ràng buộc.
- [Báo cáo cuối kỳ](HoanThanhPlan/09-bao-cao-cuoi-ky.md), [rà soát Word](HoanThanhPlan/10-ra-soat-hinh-bang-bao-cao.md): legacy verdict, đúng mã TC và giới hạn assertion.
- [Catalog JSON](../scripts/data/test-catalog-v1.json): đã đếm 257 ID duy nhất; execution_status tĩnh trong thiết kế không thay report.
- [Bộ chọn ca](../scripts/designed_cases.py), [invariant](../scripts/invariants.py), [điều phối](../scripts/lab-components.sh), [replay](../scripts/replay_cases.py), [contract checks](../scripts/contract_checks.py), [cost model](../scripts/cost_query.py).
- [Unit harness](../tests/test_harness.py), [unit cost query](../tests/test_cost_query.py): có test offline; lần này không chạy suite.
- [Coverage lịch sử](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/coverage-summary.json), [execution index](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/executions.json).
- [Scenario nguồn](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/evidence/p8-20261018-scenarios/scenario-report.json), [assertable nguồn](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/evidence/p8-20261018-assertable/designed-report.json), [TC08 nguồn](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/evidence/p8-20261018-short-r2/designed-report.json).
- [Schema coverage raw](HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/evidence/p8-20261018-probe-raw/raw/seed-101/schemathesis-coverage.json): version 1.0, tracecov 0.25.2; không diễn giải là code coverage.
- Source Directus đúng baseline: `git -C ../directus show 4f77933bf9551cac6b289576078783e189b8f4e3:api/src/app.ts`, `api/package.json`; API routers/services, auth/websocket, app/sdk và tests tồn tại ở monorepo. Đọc qua object Git, không thay HEAD.

### 17.2. Tài liệu chính thức đã tham khảo

- [Directus API](https://directus.com/docs/api): REST động theo schema và quyền; trang hiện hành chỉ dùng định hướng, route thực lấy source baseline.
- [Directus overview](https://directus.com/docs/getting-started/overview): các transport/auth/files/automation tổng quan; không dùng docs mới khẳng định behavior bản pin.
- [Schemathesis CLI tag v4.30.0](https://raw.githubusercontent.com/schemathesis/schemathesis/v4.30.0/src/schemathesis/cli/commands/run/__init__.py): phases và các nhóm option; cần help đúng image cho tích hợp coverage.
- [GitHub service containers](https://docs.github.com/en/actions/tutorials/use-containerized-services/use-docker-service-containers): điều kiện Linux và network service.
- [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets): quản lý secret/context fork.

### 17.3. Nguồn đối chiếu bổ sung lần chỉnh tài liệu

Đọc lại cùng catalog 257 ID với id/group/title/actor/request_template/oracle/oracle_readiness, toàn bộ 44 thiết kế và AGENTS; phân loại theo hành vi ở mục 8. Tổng 17 group được kiểm đếm từ JSON, không lấy 69 luật quyền làm số ID authorization. Không chạy test hoặc coverage extractor. Phân loại reuse không thay kết quả lịch sử và không chứng minh helper có thể chạy ngay trên module mới. Metadata Git đầu tài liệu vẫn là ảnh chụp khảo sát đã ghi; không giả làm lần fetch hoặc runtime mới.

### 17.4. Giới hạn khảo sát và kết quả nhiệm vụ

Chỉ đọc tệp/mã/Git và nguồn web chính thức, kiểm đếm catalog; không xác minh runtime, license ngày hiện tại, Docker daemon, remote CI, full source line/branch coverage hoặc chạy lại API. Chưa có mẫu số toàn hệ thống, nên mọi tỷ lệ toàn hệ thống là NOT_MEASURED. File này là kế hoạch có danh mục khởi đầu để triển khai tiếp, không phải báo cáo đã kiểm toàn Directus.


## Phụ lục A. Danh mục test case chi tiết

### A.1. Quy ước và tình trạng

Danh mục sau chỉnh có 49 thiết kế TC14–TC62, tất cả NOT_RUN. Phân loại reuse và cách đếm ở mục 8; không coi đây là 49 phần triển khai mới hoàn toàn. TC01–TC13 không đổi. Giữ tên requirement/alias và version khi thu hẹp các ca tách; không đưa report lịch sử sang ca mới.

Quy ước dùng chung áp dụng rõ cho mọi ca bên dưới:

- Requirement chính là SYS-<module>-NN được ghi từng ca; nguồn oracle phải đối chiếu controller/service baseline và schema/config của profile trước chạy.
- Test data dùng tên qa_sys_<module>_<run_id>, ID lấy từ response, timestamp/seed cố định được lưu. Không dùng tài khoản thật hoặc ID hard-code.
- Precondition chung: đúng digest/profile; healthcheck/control; actor đúng policy; snapshot trước ghi. Điều kiện riêng ghi từng ca. Nếu chưa xác minh contract thì BLOCKED, không suy expected từ actual đầu tiên.
- Test steps có ba giai đoạn: xác minh control/snapshot, thực hiện chuỗi riêng của ca, read-back/so oracle độc lập rồi cleanup. Status/code cụ thể lấy hợp đồng baseline trước chạy; không chấp nhận mọi non-2xx làm lỗi đúng.
- Automation cho REST: mở rộng harness hiện có hoặc Postman collection mới được version hóa; request/response/check/state/cleanup thành artifact riêng. Công cụ khác ghi theo ca; chưa cài thêm.
- Cleanup chung: chỉ xóa ID do ca tạo, child/link trước parent, restore đúng snapshot; kiểm read-back và ghi cleanup_status. Cleanup lỗi dừng phần reuse DB. Những ca settings/schema/flow có điều kiện dọn riêng bên dưới.
- Mục tiêu kiểm thử là chứng minh hành vi trong tên ca theo expected, không suy rộng mọi giá trị cùng lớp.


### A.2. Xác thực và phiên

#### TC14 — Refresh token và chấm dứt phiên

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | AUTH — Xác thực và phiên / SYS-AUTH-01 |
| Mục tiêu | Xác minh refresh token và chấm dứt phiên trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; Negative |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Tài khoản dùng một lần; clock/token TTL kiểm soát; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace auth riêng cho run; Tài khoản dùng một lần; clock/token TTL kiểm soát; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Đăng nhập tài khoản thử; refresh theo mode đã chọn; logout; dùng lại credential phiên đã logout; so oracle và lưu artifact; cleanup |
| Expected Result | Phiên mới dùng được trước logout; credential đã thu hồi không tạo truy cập sau logout; access token tự chứa được đánh giá theo TTL thực tế, không giả định bị thu hồi ngay |
| Phương pháp tự động hóa | API Python/Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python/Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC15 — Sai mật khẩu không cấp phiên

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | AUTH — Xác thực và phiên / SYS-AUTH-02 |
| Mục tiêu | Xác minh sai mật khẩu không cấp phiên trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Equivalence Partitioning; Negative |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Tài khoản dùng một lần; clock/token TTL kiểm soát; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace auth riêng cho run; Tài khoản dùng một lần; clock/token TTL kiểm soát; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Gửi mật khẩu sai cho tài khoản thử; thử truy cập tài nguyên bằng response nhận được; so oracle và lưu artifact; cleanup |
| Expected Result | Không cấp token/cookie phiên hợp lệ; lỗi theo đặc tả bản pin; không lộ mật khẩu hoặc nội dung tài nguyên |
| Phương pháp tự động hóa | API Python/Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python/Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.3. Users, Roles, Policies và Access

#### TC16 — Hợp nhất hai policy của cùng người dùng

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | RBAC — Users, Roles, Policies và Access / SYS-RBAC-01 |
| Mục tiêu | Xác minh hợp nhất hai policy của cùng người dùng trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Decision Table; RBAC |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user và hai policy chỉ dùng lab; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rbac riêng cho run; Hai user và hai policy chỉ dùng lab; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo user có hai policy đọc hai tập bản ghi rời nhau; đọc cả hai; đọc field ngoài cả hai policy; so oracle và lưu artifact; cleanup |
| Expected Result | Kết quả khớp ngữ nghĩa hợp nhất ở source baseline; không thấy bản ghi/trường ngoài tập quyền đã khai báo |
| Phương pháp tự động hóa | API Python/Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python/Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC17 — Reader không tự nâng quyền hệ thống

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | RBAC — Users, Roles, Policies và Access / SYS-RBAC-02 |
| Mục tiêu | Xác minh reader không tự nâng quyền hệ thống trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Negative |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user và hai policy chỉ dùng lab; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rbac riêng cho run; Hai user và hai policy chỉ dùng lab; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Reader gửi thay đổi role/policy của chính user; admin đọc lại cấu hình; so oracle và lưu artifact; cleanup |
| Expected Result | Request bị từ chối theo hợp đồng; role và policy không đổi; control admin đọc được trước và sau |
| Phương pháp tự động hóa | API Python/Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python/Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.4. Collections và Fields

#### TC18 — Vòng đời collection và field

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | MODEL — Collections và Fields / SYS-MODEL-01 |
| Mục tiêu | Xác minh vòng đời collection và field trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; Contract |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Admin; collection qa_sys_model riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace model riêng cho run; Admin; collection qa_sys_model riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo collection tạm; thêm field integer nullable; đọc metadata; ghi item; xóa field sau khi sao lưu; so oracle và lưu artifact; cleanup |
| Expected Result | Metadata và dữ liệu phù hợp schema đã khai báo; xóa field chỉ tác động collection tạm |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC19 — Quyền thay đổi mô hình dữ liệu

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | MODEL — Collections và Fields / SYS-MODEL-02 |
| Mục tiêu | Xác minh quyền thay đổi mô hình dữ liệu trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Negative |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Admin; collection qa_sys_model riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace model riêng cho run; Admin; collection qa_sys_model riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Editor thử thêm field vào collection tạm; admin kiểm metadata và dữ liệu; so oracle và lưu artifact; cleanup |
| Expected Result | Không có field mới; lỗi quyền hợp lệ; collection và dữ liệu cũ không thay đổi |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.5. Items và thao tác hàng loạt

#### TC20 — Sửa nhiều item theo danh sách ID

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | ITEM — Items và thao tác hàng loạt / SYS-ITEM-01 |
| Mục tiêu | Xác minh sửa nhiều item theo danh sách id trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Equivalence Partitioning; Contract |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection qa_sys_bulk; 3 item ID động; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace item riêng cho run; Collection qa_sys_bulk; 3 item ID động; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo ba item; bulk PATCH hai ID; đọc lại cả ba; so oracle và lưu artifact; cleanup |
| Expected Result | Hai item mục tiêu đổi đúng; item ngoài tập giữ nguyên; response theo schema bản pin |
| Phương pháp tự động hóa | API Python; Schemathesis guided; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis guided |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC21 — Xóa nhiều item giới hạn tập đích

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | ITEM — Items và thao tác hàng loạt / SYS-ITEM-02 |
| Mục tiêu | Xác minh xóa nhiều item giới hạn tập đích trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; Regression |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection qa_sys_bulk; 3 item ID động; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace item riêng cho run; Collection qa_sys_bulk; 3 item ID động; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo ba item; bulk DELETE hai ID; đọc lại danh sách; so oracle và lưu artifact; cleanup |
| Expected Result | Hai ID không còn truy cập; item thứ ba giữ nguyên; không xóa dữ liệu ngoài namespace |
| Phương pháp tự động hóa | API Python; Schemathesis guided; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis guided |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.6. Query, validation và lỗi

#### TC22 — Filter đồng thời qua quan hệ nhiều nhiều

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | QUERY — Query, validation và lỗi / SYS-QUERY-01 |
| Mục tiêu | Xác minh filter đồng thời qua quan hệ nhiều nhiều trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Decision Table; Equivalence Partitioning |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Fixture riêng có timestamp, decimal, null; không dùng lại oracle qa_articles; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace query riêng cho run; Fixture riêng có timestamp, decimal, null; không dùng lại oracle qa_articles; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo tags và items M2M với tập ID oracle; kết hợp filter tag và điều kiện số rồi sort ID; so oracle và lưu artifact; cleanup |
| Expected Result | Tập ID đúng oracle độc lập; không nhân đôi item do join; không trả dữ liệu quan hệ cấm |
| Phương pháp tự động hóa | API Python; Schemathesis; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC23 — Payload JSON hỏng cho bulk mới

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | QUERY — Query, validation và lỗi / SYS-QUERY-02 |
| Mục tiêu | Xác minh payload json hỏng cho bulk mới trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Negative; Regression |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Fixture riêng có timestamp, decimal, null; không dùng lại oracle qa_articles; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace query riêng cho run; Fixture riêng có timestamp, decimal, null; không dùng lại oracle qa_articles; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Gửi body JSON không đóng ngoặc đến bulk PATCH ở collection tạm; đọc lại mọi item; so oracle và lưu artifact; cleanup |
| Expected Result | Lỗi client theo parser baseline; không 5xx; không cập nhật bất kỳ item nào |
| Phương pháp tự động hóa | API Python; Schemathesis; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.7. Relationships và toàn vẹn

#### TC24 — Thêm và gỡ liên kết M2M

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | REL — Relationships và toàn vẹn / SYS-REL-01 |
| Mục tiêu | Xác minh thêm và gỡ liên kết m2m trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Stateful; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection M2M và junction riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rel riêng cho run; Collection M2M và junction riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo hai item và hai tag; thêm hai liên kết qua nested write; gỡ một liên kết; đọc hai chiều; so oracle và lưu artifact; cleanup |
| Expected Result | Liên kết còn lại đúng; item/tag gốc còn; junction không trùng hoặc mồ côi |
| Phương pháp tự động hóa | API Python; stateful; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; stateful |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC25 — Rollback khi nested write thất bại

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | REL — Relationships và toàn vẹn / SYS-REL-02 |
| Mục tiêu | Xác minh rollback khi nested write thất bại trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Negative; Stateful |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection M2M và junction riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rel riêng cho run; Collection M2M và junction riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo request nested gồm một con hợp lệ và một con vi phạm constraint đã xác minh; đọc snapshot; so oracle và lưu artifact; cleanup |
| Expected Result | Theo transaction contract đã chốt: thất bại không để lại bản ghi cha/con một phần; nếu contract chưa rõ thì BLOCKED |
| Phương pháp tự động hóa | API Python; stateful; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; stateful |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.8. Files, Folders, Assets

#### TC26 — Upload và download bảo toàn nội dung

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | FILES — Files, Folders, Assets / SYS-FILES-01 |
| Mục tiêu | Xác minh upload và download bảo toàn nội dung trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; Contract |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Storage local tạm; PNG 16x16 và file text có hash; mount lưu trữ riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace files riêng cho run; Storage local tạm; PNG 16x16 và file text có hash; mount lưu trữ riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo folder; upload file text vào folder; download bằng ID; so SHA-256; xóa file; so oracle và lưu artifact; cleanup |
| Expected Result | File tải xuống đúng hash/kích thước; metadata liên kết đúng folder; sau xóa không tải được |
| Phương pháp tự động hóa | API Python; Postman multipart; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Postman multipart |
| Dọn dữ liệu | Xóa file qua API trước folder; kiểm storage tạm không còn object của run. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC27 — Asset riêng tư không lộ qua biến đổi

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | FILES — Files, Folders, Assets / SYS-FILES-02 |
| Mục tiêu | Xác minh asset riêng tư không lộ qua biến đổi trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Negative |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Storage local tạm; PNG 16x16 và file text có hash; mount lưu trữ riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace files riêng cho run; Storage local tạm; PNG 16x16 và file text có hash; mount lưu trữ riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Upload PNG chỉ owner đọc; user khác gọi assets với resize; owner gọi control; so oracle và lưu artifact; cleanup |
| Expected Result | Owner nhận ảnh đúng kích thước; user khác không nhận bytes ảnh hoặc metadata nhạy cảm; cache không làm lộ |
| Phương pháp tự động hóa | API Python; Postman multipart; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Postman multipart |
| Dọn dữ liệu | Xóa file qua API trước folder; kiểm storage tạm không còn object của run. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.9. Flows và Operations

#### TC28 — Flow có nhánh điều kiện

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | FLOW — Flows và Operations / SYS-FLOW-01 |
| Mục tiêu | Xác minh flow có nhánh điều kiện trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Decision Table; Stateful |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Flow manual và webhook vào sink cục bộ; không gửi dịch vụ thật; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace flow riêng cho run; Flow manual và webhook vào sink cục bộ; không gửi dịch vụ thật; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo flow manual với điều kiện score và hai nhánh ghi marker; kích hoạt mỗi nhánh; so oracle và lưu artifact; cleanup |
| Expected Result | Mỗi input chạy đúng một nhánh; marker và log khớp; không gửi request ngoài sink |
| Phương pháp tự động hóa | API Python; sink HTTP nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; sink HTTP nội bộ |
| Dọn dữ liệu | Vô hiệu flow/scheduler trước; xóa operation/flow và marker; dọn sink. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC29 — Nhánh reject khi operation lỗi

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | FLOW — Flows và Operations / SYS-FLOW-02 |
| Mục tiêu | Xác minh nhánh reject khi operation lỗi trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Negative; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Flow manual và webhook vào sink cục bộ; không gửi dịch vụ thật; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace flow riêng cho run; Flow manual và webhook vào sink cục bộ; không gửi dịch vụ thật; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo flow có operation thất bại chủ đích và nhánh reject ghi marker; kích hoạt; so oracle và lưu artifact; cleanup |
| Expected Result | Lỗi và nhánh reject khớp cấu hình; không ghi marker thành công; status/log đủ tái hiện |
| Phương pháp tự động hóa | API Python; sink HTTP nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; sink HTTP nội bộ |
| Dọn dữ liệu | Vô hiệu flow/scheduler trước; xóa operation/flow và marker; dọn sink. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.10. Activity, Revisions và Versions

#### TC30 — Revision truy vết sửa dữ liệu

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | HISTORY — Activity, Revisions và Versions / SYS-HISTORY-01 |
| Mục tiêu | Xác minh revision truy vết sửa dữ liệu trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; RBAC |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection bật tracking/version theo baseline; user riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace history riêng cho run; Collection bật tracking/version theo baseline; user riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; User A tạo item rồi đổi title; đọc activity và revision liên quan; so oracle và lưu artifact; cleanup |
| Expected Result | Actor, action, collection, item và delta của lần sửa đúng snapshot/input; quyền đọc history của user khác là requirement backlog riêng, không gộp verdict ca này |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC31 — Version không đổi bản chính trước promote

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | HISTORY — Activity, Revisions và Versions / SYS-HISTORY-02 |
| Mục tiêu | Xác minh version không đổi bản chính trước promote trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; Regression |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Collection bật tracking/version theo baseline; user riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace history riêng cho run; Collection bật tracking/version theo baseline; user riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo version item; sửa version; đọc bản chính; promote version; đọc lại; so oracle và lưu artifact; cleanup |
| Expected Result | Trước promote bản chính giữ nguyên; sau promote đúng thay đổi; history ghi nhận theo baseline |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.11. Dashboards, Panels và Presets

#### TC32 — Dashboard và panel qua API

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | INSIGHT — Dashboards, Panels và Presets / SYS-INSIGHT-01 |
| Mục tiêu | Xác minh dashboard và panel qua api trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Stateful; Contract |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user; dashboard/panel/preset tạm; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace insight riêng cho run; Hai user; dashboard/panel/preset tạm; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo dashboard; thêm panel cấu hình hợp lệ; đọc lại; cập nhật vị trí; so oracle và lưu artifact; cleanup |
| Expected Result | Quan hệ dashboard-panel và cấu hình được lưu chính xác; không ảnh hưởng dashboard khác |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC33 — Preset cá nhân được cách ly

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | INSIGHT — Dashboards, Panels và Presets / SYS-INSIGHT-02 |
| Mục tiêu | Xác minh preset cá nhân được cách ly trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Decision Table |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user; dashboard/panel/preset tạm; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace insight riêng cho run; Hai user; dashboard/panel/preset tạm; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; User A lưu preset cá nhân; user B liệt kê/đọc ID preset A theo policy đã định; so oracle và lưu artifact; cleanup |
| Expected Result | A đọc đúng cấu hình; B không có dữ liệu preset ngoài quyền; không suy mọi preset đều private |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.12. Settings, Server và license

#### TC34 — Giới hạn thông tin server công khai

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SERVER — Settings, Server và license / SYS-SERVER-01 |
| Mục tiêu | Xác minh giới hạn thông tin server công khai trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Contract |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Admin; snapshot settings; không thay khóa/license; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace server riêng cho run; Admin; snapshot settings; không thay khóa/license; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Anonymous và admin đọc ping/health/info theo route inventory; so allowlist field; so oracle và lưu artifact; cleanup |
| Expected Result | Ping hoạt động; thông tin nhạy cảm không lộ public; route hạn quyền bị chặn; không ghi secret |
| Phương pháp tự động hóa | API Python; Schemathesis read-only; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis read-only |
| Dọn dữ liệu | Khôi phục settings trước, read-back rồi xóa dữ liệu thử; không sửa license/key. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC35 — Thay setting thử rồi khôi phục

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SERVER — Settings, Server và license / SYS-SERVER-02 |
| Mục tiêu | Xác minh thay setting thử rồi khôi phục trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | State Transition; RBAC |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Admin; snapshot settings; không thay khóa/license; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace server riêng cho run; Admin; snapshot settings; không thay khóa/license; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Admin đổi project_name tạm; đọc lại; Editor thử sửa; restore snapshot; so oracle và lưu artifact; cleanup |
| Expected Result | Admin đổi đúng; Editor không đổi được; finally khôi phục giá trị gốc và kiểm read-back |
| Phương pháp tự động hóa | API Python; Schemathesis read-only; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Schemathesis read-only |
| Dọn dữ liệu | Khôi phục settings trước, read-back rồi xóa dữ liệu thử; không sửa license/key. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.13. Snapshot, diff và apply

#### TC36 — Diff rỗng khi schema không đổi

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SCHEMA — Snapshot, diff và apply / SYS-SCHEMA-01 |
| Mục tiêu | Xác minh diff rỗng khi schema không đổi trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Contract; Regression |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | DB thử dùng một lần; snapshot trước; admin; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace schema riêng cho run; DB thử dùng một lần; snapshot trước; admin; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Xuất hai snapshot cùng schema; chuẩn hóa trường volatile theo đặc tả; tính diff; so oracle và lưu artifact; cleanup |
| Expected Result | Diff không có thay đổi nghiệp vụ; snapshot không chứa credential; version/hash được lưu |
| Phương pháp tự động hóa | API Python; so schema chuẩn hóa; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; so schema chuẩn hóa |
| Dọn dữ liệu | Bỏ DB thử dùng một lần sau lưu bằng chứng; không apply ngược trên DB lab cũ. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC37 — Apply thay đổi schema trong DB tạm

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SCHEMA — Snapshot, diff và apply / SYS-SCHEMA-02 |
| Mục tiêu | Xác minh apply thay đổi schema trong db tạm trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Stateful; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | DB thử dùng một lần; snapshot trước; admin; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace schema riêng cho run; DB thử dùng một lần; snapshot trước; admin; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo diff thêm field vào collection tạm; apply; đọc schema và thử ghi field mới; so oracle và lưu artifact; cleanup |
| Expected Result | Chỉ field dự kiến thay đổi; field mới ghi/đọc đúng; snapshot còn đủ để khôi phục hoặc bỏ DB tạm |
| Phương pháp tự động hóa | API Python; so schema chuẩn hóa; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; so schema chuẩn hóa |
| Dọn dữ liệu | Bỏ DB thử dùng một lần sau lưu bằng chứng; không apply ngược trên DB lab cũ. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.14. GraphQL

#### TC38 — GraphQL không vượt quyền theo field

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | GQL — GraphQL / SYS-GQL-01 |
| Mục tiêu | Xác minh graphql không vượt quyền theo field trong phạm vi profile đã chốt |
| Test Type | Tích hợp GraphQL và nghiệp vụ |
| Test Design Technique | RBAC; Contract |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Introspection theo actor; GraphQL fixture tương đương REST; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace gql riêng cho run; Introspection theo actor; GraphQL fixture tương đương REST; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Owner đọc item công khai; Reader yêu cầu field kín qua GraphQL; so oracle và lưu artifact; cleanup |
| Expected Result | Control đúng dữ liệu; request field kín bị từ chối hoặc field không có trong schema actor theo contract; không lộ nội dung |
| Phương pháp tự động hóa | Client GraphQL Python; Schemathesis GraphQL sau pilot; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client GraphQL Python; Schemathesis GraphQL sau pilot |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC39 — Mutation GraphQL tạo và cập nhật

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | GQL — GraphQL / SYS-GQL-02 |
| Mục tiêu | Xác minh mutation graphql tạo và cập nhật trong phạm vi profile đã chốt |
| Test Type | Tích hợp GraphQL và nghiệp vụ |
| Test Design Technique | Stateful; Regression |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Introspection theo actor; GraphQL fixture tương đương REST; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace gql riêng cho run; Introspection theo actor; GraphQL fixture tương đương REST; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; User được phép tạo item tạm qua mutation; sửa; kiểm read-back cả GraphQL và REST; so oracle và lưu artifact; cleanup |
| Expected Result | ID động nhất quán; field sửa đúng; field không gửi giữ nguyên; cleanup qua API được phép |
| Phương pháp tự động hóa | Client GraphQL Python; Schemathesis GraphQL sau pilot; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client GraphQL Python; Schemathesis GraphQL sau pilot |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.15. Realtime

#### TC40 — Subscription chỉ nhận sự kiện được phép

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | RT — Realtime / SYS-RT-01 |
| Mục tiêu | Xác minh subscription chỉ nhận sự kiện được phép trong phạm vi profile đã chốt |
| Test Type | Tích hợp giao thức realtime |
| Test Design Technique | RBAC; Stateful |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Bật realtime trong profile mới; hai user; timeout hữu hạn; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rt riêng cho run; Bật realtime trong profile mới; hai user; timeout hữu hạn; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Reader subscribe; Editor tạo item thuộc và ngoài quyền Reader; chờ cửa sổ sự kiện; so oracle và lưu artifact; cleanup |
| Expected Result | Chỉ nhận sự kiện trong quyền, payload không có field kín; correlation ID và timeout được lưu |
| Phương pháp tự động hóa | Client WebSocket Python/Node; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client WebSocket Python/Node |
| Dọn dữ liệu | Unsubscribe/đóng socket, thu hồi phiên thử rồi dọn item/user. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC41 — Đóng phiên realtime khi auth không hợp lệ

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | RT — Realtime / SYS-RT-02 |
| Mục tiêu | Xác minh đóng phiên realtime khi auth không hợp lệ trong phạm vi profile đã chốt |
| Test Type | Tích hợp giao thức realtime |
| Test Design Technique | Negative; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Bật realtime trong profile mới; hai user; timeout hữu hạn; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace rt riêng cho run; Bật realtime trong profile mới; hai user; timeout hữu hạn; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Kết nối bằng token giả; thử subscribe và gửi operation; chạy control token hợp lệ; so oracle và lưu artifact; cleanup |
| Expected Result | Token giả không tạo subscription/truy cập; kết nối hợp lệ hoạt động; lỗi tuân giao thức baseline |
| Phương pháp tự động hóa | Client WebSocket Python/Node; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client WebSocket Python/Node |
| Dọn dữ liệu | Unsubscribe/đóng socket, thu hồi phiên thử rồi dọn item/user. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.16. Data Studio

#### TC42 — Đăng nhập và duy trì phiên Studio

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | UI — Data Studio / SYS-UI-01 |
| Mục tiêu | Xác minh login/session UI; không kiểm CRUD trong verdict này |
| Test Type | End-to-end giao diện và đối chiếu API |
| Test Design Technique | End-to-end; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | User riêng có app access, viewport/browser pin; không thay Editor cũ; control tài khoản qua API và precondition Phụ lục A.1 |
| Test Data | Namespace ui riêng cho run; Browser cùng phiên bản cố định; viewport; user thử; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Mở Studio bằng browser profile mới; login user thử có app access; reload trang được phép; kiểm user/session hiển thị; logout và quay lại trang hạn quyền |
| Expected Result | Đăng nhập đúng actor; reload giữ phiên theo contract; sau logout UI trở về trạng thái chưa đăng nhập, không hiện dữ liệu cache nhạy cảm |
| Phương pháp tự động hóa | Playwright dự kiến; thủ công có bằng chứng; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Playwright dự kiến; thủ công có bằng chứng |
| Dọn dữ liệu | Logout và đóng browser context; xóa tài khoản thử do ca tạo; không có item CRUD trong ca này |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC43 — Studio với user hạn quyền

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | UI — Data Studio / SYS-UI-02 |
| Mục tiêu | Xác minh studio với user hạn quyền trong phạm vi profile đã chốt |
| Test Type | End-to-end giao diện và đối chiếu API |
| Test Design Technique | End-to-end; RBAC |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Browser cùng phiên bản cố định; viewport; user thử; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace ui riêng cho run; Browser cùng phiên bản cố định; viewport; user thử; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; User có app access nhưng chỉ đọc đăng nhập; mở item; thử truy cập route quản trị trực tiếp; so oracle và lưu artifact; cleanup |
| Expected Result | Nút ghi/quản trị phù hợp quyền; route trực tiếp không cấp quyền; API read-back không có thay đổi |
| Phương pháp tự động hóa | Playwright dự kiến; thủ công có bằng chứng; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Playwright dự kiến; thủ công có bằng chứng |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.17. Extensions

#### TC44 — Endpoint extension có kiểm quyền

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | EXT — Extensions / SYS-EXT-01 |
| Mục tiêu | Xác minh endpoint extension có kiểm quyền trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Integration |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Extension endpoint tối giản do nhóm kiểm soát trong profile riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace ext riêng cho run; Extension endpoint tối giản do nhóm kiểm soát trong profile riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Nạp endpoint thử với auth guard; gọi bằng owner và anonymous; so oracle và lưu artifact; cleanup |
| Expected Result | Owner nhận payload định trước; anonymous không nhận nội dung cấm; phiên bản extension và API được ghi |
| Phương pháp tự động hóa | API Python; unit Vitest có điều kiện; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; unit Vitest có điều kiện |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC45 — Extension lỗi không phá endpoint lõi

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | EXT — Extensions / SYS-EXT-02 |
| Mục tiêu | Xác minh extension lỗi không phá endpoint lõi trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Negative; Regression |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Extension endpoint tối giản do nhóm kiểm soát trong profile riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace ext riêng cho run; Extension endpoint tối giản do nhóm kiểm soát trong profile riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Endpoint thử phát sinh lỗi xử lý; sau đó gọi ping và CRUD control; so oracle và lưu artifact; cleanup |
| Expected Result | Response lỗi được xử lý, không lộ stack/secret; ping và CRUD tiếp tục hoạt động |
| Phương pháp tự động hóa | API Python; unit Vitest có điều kiện; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; unit Vitest có điều kiện |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.18. Shares

#### TC46 — Share chỉ truy cập item được chia sẻ

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SHARE — Shares / SYS-SHARE-01 |
| Mục tiêu | Xác minh share chỉ truy cập item được chia sẻ trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Decision Table |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Share một item; thời hạn/giới hạn có nguồn baseline; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace share riêng cho run; Share một item; thời hạn/giới hạn có nguồn baseline; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo share item A; dùng phiên share đọc A và thử đọc item B; so oracle và lưu artifact; cleanup |
| Expected Result | A truy cập đúng phạm vi; B và field ngoài share không bị lộ; không cấp quyền quản trị |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC47 — Share hết hạn bị chặn

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SHARE — Shares / SYS-SHARE-02 |
| Mục tiêu | Xác minh share hết hạn bị chặn trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Boundary Value; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Share một item; thời hạn/giới hạn có nguồn baseline; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace share riêng cho run; Share một item; thời hạn/giới hạn có nguồn baseline; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo share thời hạn ngắn kiểm soát; đọc trước hạn; đọc sau hạn với dung sai clock đã chốt; so oracle và lưu artifact; cleanup |
| Expected Result | Trước hạn đọc được; sau hạn không truy cập thêm qua share; phân biệt cache/session theo contract |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.19. Comments, Notifications và Translations

#### TC48 — Comment Unicode gắn đúng item

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | COLLAB — Comments, Notifications và Translations / SYS-COLLAB-01 |
| Mục tiêu | Xác minh comment unicode gắn đúng item trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Equivalence Partitioning; Stateful |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user; item tạm; locale vi/en; SMTP không cần cho in-app; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace collab riêng cho run; Hai user; item tạm; locale vi/en; SMTP không cần cho in-app; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Tạo comment tiếng Việt vào item tạm; đọc; sửa; xóa bằng user có quyền; so oracle và lưu artifact; cleanup |
| Expected Result | Nội dung Unicode và item linkage đúng; sửa/xóa đúng actor; không thay item gốc |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC49 — Notification đúng người nhận và cách ly người khác

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | COLLAB — Comments, Notifications và Translations / SYS-COLLAB-02 |
| Mục tiêu | Kiểm một luật notification isolation; bản dịch có TC59 riêng |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Decision Table |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Hai user với policy đã chốt; notification API thuộc baseline; không cần SMTP; precondition Phụ lục A.1 |
| Test Data | Một notification có correlation ID của run gửi riêng A, không chứa dữ liệu thật |
| Test Steps | Tạo notification in-app cho user A; A đọc control; B thử đọc notification theo policy; ghi riêng response và read-back |
| Expected Result | A đọc đúng nội dung; B không nhận dữ liệu notification ngoài quyền; không dùng kết quả translation để định verdict |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Xóa notification và user thử theo ID được tạo; kiểm không còn notification của run |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.20. Utilities, Import và Export

#### TC50 — Import CSV vào collection riêng

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | IMPORT — Utilities, Import và Export / SYS-IMPORT-01 |
| Mục tiêu | Xác minh import csv vào collection riêng trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Equivalence Partitioning; Contract |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | CSV/JSON fixture 2 dòng; collection qa_sys_import; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace import riêng cho run; CSV/JSON fixture 2 dòng; collection qa_sys_import; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Import CSV 2 dòng hợp lệ với dấu phẩy trong chuỗi quoted và Unicode; đọc lại; so oracle và lưu artifact; cleanup |
| Expected Result | Đúng hai item với nội dung đầy đủ; parse không tách sai cột; mapping field khớp |
| Phương pháp tự động hóa | API Python; Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC51 — Import có field không được phép

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | IMPORT — Utilities, Import và Export / SYS-IMPORT-02 |
| Mục tiêu | Xác minh import có field không được phép trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Negative |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | CSV/JSON fixture 2 dòng; collection qa_sys_import; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace import riêng cho run; CSV/JSON fixture 2 dòng; collection qa_sys_import; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; User chỉ ghi title import file có thêm field protected; read-back bằng admin; so oracle và lưu artifact; cleanup |
| Expected Result | Không ghi được field cấm; trạng thái toàn bộ/từng dòng theo contract đã xác minh; không tự giả định atomic |
| Phương pháp tự động hóa | API Python; Postman; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; Postman |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.21. Cache, rate limit và khả năng phục hồi

#### TC52 — Cache tôn trọng thay đổi quyền

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPS — Cache, rate limit và khả năng phục hồi / SYS-OPS-01 |
| Mục tiêu | Xác minh cache tôn trọng thay đổi quyền trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; State Transition |
| Priority | P1 — I=3, L=2, C=3, S=8; quyền/phiên/toàn vẹn quan trọng, nhiều actor hoặc trạng thái (đánh giá thiết kế, cần review M1) |
| Preconditions | Profile riêng cache/rate limit; fault chỉ trong DB dùng một lần; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace ops riêng cho run; Profile riêng cache/rate limit; fault chỉ trong DB dùng một lần; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Bật cache trong profile; A đọc private item; đổi policy theo kịch bản; B thử đọc cùng URL; so oracle và lưu artifact; cleanup |
| Expected Result | Cache không phát dữ liệu A cho B; sau thay đổi quyền hành vi tuân policy/TTL đã chốt; lưu cache config |
| Phương pháp tự động hóa | API Python; công cụ tải sau chọn phiên bản; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; công cụ tải sau chọn phiên bản |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC53 — Rate limit và phục hồi sau cửa sổ

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPS — Cache, rate limit và khả năng phục hồi / SYS-OPS-02 |
| Mục tiêu | Xác minh rate limit và phục hồi sau cửa sổ trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Boundary Value; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | Profile riêng cache/rate limit; fault chỉ trong DB dùng một lần; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace ops riêng cho run; Profile riêng cache/rate limit; fault chỉ trong DB dùng một lần; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Bật limiter ngưỡng nhỏ trong profile; gửi vượt ngưỡng; chờ reset hữu hạn; gửi control; so oracle và lưu artifact; cleanup |
| Expected Result | Có từ chối theo policy giới hạn; sau cửa sổ request hợp lệ hoạt động; không crash; không suy đây là load test |
| Phương pháp tự động hóa | API Python; công cụ tải sau chọn phiên bản; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python; công cụ tải sau chọn phiên bản |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.22. AI, MCP và Deployments

#### TC54 — MCP không đọc dữ liệu ngoài policy

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPTION — AI, MCP và Deployments / SYS-OPTION-01 |
| Mục tiêu | Xác minh mcp không đọc dữ liệu ngoài policy trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Contract |
| Priority | P3 — I=3, L=1, C=1, S=5; lộ dữ liệu/secret có tác động cao nhưng feature/provider chưa áp dụng được xác minh; không hạ impact vì thiếu môi trường (đánh giá thiết kế, cần review M1) |
| Preconditions | Xác minh feature flag/license; provider và sink riêng; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace option riêng cho run; Xác minh feature flag/license; provider và sink riêng; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; Nếu bật MCP: user hạn quyền gọi tool đọc item/field cấm; gọi control được phép; so oracle và lưu artifact; cleanup |
| Expected Result | Tool tuân policy như API; không lộ dữ liệu; nếu feature không áp dụng phải có quyết định N/A và nguồn |
| Phương pháp tự động hóa | Client giao thức; sink nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client giao thức; sink nội bộ |
| Dọn dữ liệu | Dừng provider/sink thử; xóa resource chỉ thuộc run; xác nhận không có deployment ngoài lab. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC55 — AI success qua provider thử trong lab

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPTION — AI, MCP và Deployments / SYS-OPTION-02 |
| Mục tiêu | Kiểm đường AI success tới sink thử; error và deployment có TC riêng |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Integration; Negative |
| Priority | P4 — I=1, L=1, C=1, S=3; đường success provider tùy chọn, chưa được chọn bắt buộc (đánh giá thiết kế, cần review M1) |
| Preconditions | AI enabled được xác minh; provider sink hỗ trợ hợp đồng model bản pin; credentials thử và egress control có bằng chứng; nếu chưa đủ thì BLOCKED |
| Test Data | Prompt vô hại với marker run, model/provider thử đã pin; không dùng nội dung hoặc key thật |
| Test Steps | Nếu feature áp dụng và enabled, cấu hình profile provider thử đã được duyệt; gửi một request AI hợp lệ có correlation ID; đối chiếu response với sink |
| Expected Result | Request tới đúng provider thử; response AI theo contract được xác minh; không có outbound tới provider thật; không gộp verdict deployment/error |
| Phương pháp tự động hóa | Client giao thức; sink nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client giao thức; sink nội bộ |
| Dọn dữ liệu | Dọn conversation/file/resource do ca tạo và log sink; restore profile; không tạo deployment |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.23. SDK và tương thích client

#### TC56 — SDK duy trì phiên và gọi API

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SDK — SDK và tương thích client / SYS-SDK-01 |
| Mục tiêu | Xác minh sdk duy trì phiên và gọi api trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Integration; State Transition |
| Priority | P3 — I=2, L=1, C=1, S=4; client SDK chưa được chốt trong SUT môn học (đánh giá thiết kế, cần review M1) |
| Preconditions | SDK tương thích bản pin; chưa cài package; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace sdk riêng cho run; SDK tương thích bản pin; chưa cài package; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; SDK login, đọc item được phép, refresh theo mode đã xác minh, logout; so oracle và lưu artifact; cleanup |
| Expected Result | Dữ liệu tương đương REST; SDK không đưa token vào log; trạng thái auth tuân contract phiên |
| Phương pháp tự động hóa | Vitest hoặc script SDK dự kiến; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Vitest hoặc script SDK dự kiến |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

#### TC57 — SDK xử lý lỗi có cấu trúc

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | SDK — SDK và tương thích client / SYS-SDK-02 |
| Mục tiêu | Xác minh sdk xử lý lỗi có cấu trúc trong phạm vi profile đã chốt |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Negative; Regression |
| Priority | P3 — I=2, L=1, C=1, S=4; client SDK chưa được chốt trong SUT môn học (đánh giá thiết kế, cần review M1) |
| Preconditions | SDK tương thích bản pin; chưa cài package; áp dụng precondition chung Phụ lục A.1 |
| Test Data | Namespace sdk riêng cho run; SDK tương thích bản pin; chưa cài package; giá trị và ID thực tế lưu trong fixture map trước chạy |
| Test Steps | Control/snapshot trước; SDK đọc field cấm rồi gọi control hợp lệ; so oracle và lưu artifact; cleanup |
| Expected Result | Lỗi giữ status/code cần chẩn đoán; không biến lỗi thành data thành công; client tiếp tục gọi control |
| Phương pháp tự động hóa | Vitest hoặc script SDK dự kiến; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Vitest hoặc script SDK dự kiến |
| Dọn dữ liệu | Theo cleanup chung; xóa tài nguyên liên quan theo thứ tự ngược phụ thuộc. |
| Execution Status / Evidence | NOT_RUN / chưa có; legacy test không được dùng làm bằng chứng chạy ca này |

### A.24. Ca tách có oracle và verdict độc lập

Các mục sau là phần ròng bổ sung do tách, không có report lịch sử; giữ derived_from trong canonical map.

#### TC58 — CRUD Studio trên phiên đã xác thực

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | UI — Data Studio / SYS-UI-03 |
| Mục tiêu | CRUD Studio trên phiên đã xác thực |
| Test Type | End-to-end giao diện và đối chiếu API |
| Test Design Technique | End-to-end; State Transition |
| Priority | P2 — I=2, L=2, C=2, S=6; luồng native hoặc trạng thái bổ sung, cần chạy sau dependency gate (đánh giá thiết kế, cần review M1) |
| Preconditions | User thử đã xác thực bằng fixture setup riêng; collection tạm có app access và policy CRUD; login không là assertion của TC58 |
| Test Data | Item tạm title ban đầu và title mới cố định theo run, ID lấy qua read-back |
| Test Steps | Từ phiên đã chuẩn bị, tạo item qua UI; đọc lại; sửa title; reload; xóa có xác nhận; dùng API độc lập kiểm từng hậu điều kiện |
| Expected Result | Dữ liệu UI/API khớp; reload giữ thay đổi; item bị xóa không còn truy cập; failure login setup là BLOCKED, không FAIL CRUD |
| Phương pháp tự động hóa | Playwright dự kiến; thủ công có bằng chứng; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Playwright dự kiến; thủ công có bằng chứng |
| Dọn dữ liệu | Dọn item theo ID nếu chưa xóa; đóng browser context; không đếm lại verdict login TC42 |
| Execution Status / Evidence | NOT_RUN / chưa có; derived_from=TC42; thiết kế tách, không kế thừa historical verdict |

#### TC59 — Bản dịch vi/en không ghi đè locale khác

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | COLLAB — Comments, Notifications và Translations / SYS-COLLAB-03 |
| Mục tiêu | Bản dịch vi/en không ghi đè locale khác |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | RBAC; Decision Table |
| Priority | P3 — I=2, L=1, C=2, S=5; ít phơi nhiễm hơn trong lab hiện tại; chưa có finding cùng hành vi (đánh giá thiết kế, cần review M1) |
| Preconditions | Translation API được xác minh; actor có quyền quản lý key thử; không cần notification/SMTP |
| Test Data | Một key riêng run với hai chuỗi vi/en biết trước |
| Test Steps | Tạo key vi/en; đọc từng locale; cập nhật vi; đọc lại cả hai locale |
| Expected Result | Chuỗi mỗi locale đúng; thay vi không đổi en; không phụ thuộc notification verdict |
| Phương pháp tự động hóa | API Python; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | API Python |
| Dọn dữ liệu | Xóa hai bản dịch của key thử; không đụng key hệ thống |
| Execution Status / Evidence | NOT_RUN / chưa có; derived_from=TC49; thiết kế tách, không kế thừa historical verdict |

#### TC60 — AI error không lộ secret và không tạo kết quả thành công

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPTION — AI, MCP và Deployments / SYS-OPTION-03 |
| Mục tiêu | AI error không lộ secret và không tạo kết quả thành công |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Integration; Negative |
| Priority | P3 — I=3, L=1, C=1, S=5; lộ dữ liệu/secret có tác động cao nhưng feature/provider chưa áp dụng được xác minh; không hạ impact vì thiếu môi trường (đánh giá thiết kế, cần review M1) |
| Preconditions | AI enabled và provider sink cố định response lỗi theo contract; egress chỉ lab; thiếu provider/oracle = BLOCKED |
| Test Data | Một request AI thử có marker run; sink trả lỗi xác định, không dùng key thật |
| Test Steps | Gửi request tới sink cấu hình lỗi; ghi status/code và response đã sanitize; đối chiếu trace sink và state sau request |
| Expected Result | Lỗi được ánh xạ theo contract bản pin, không lộ token/stack nhạy cảm và không ghi output như success; không định verdict đường deployment |
| Phương pháp tự động hóa | Client giao thức; sink nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client giao thức; sink nội bộ |
| Dọn dữ liệu | Restore sink và dọn resource run kể cả request lỗi |
| Execution Status / Evidence | NOT_RUN / chưa có; derived_from=TC55; thiết kế tách, không kế thừa historical verdict |

#### TC61 — Deployment success chỉ tới đích thử

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPTION — AI, MCP và Deployments / SYS-OPTION-04 |
| Mục tiêu | Deployment success chỉ tới đích thử |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Integration; Negative |
| Priority | P4 — I=1, L=1, C=1, S=3; đường success provider tùy chọn, chưa được chọn bắt buộc (đánh giá thiết kế, cần review M1) |
| Preconditions | Deployment feature/license áp dụng đã xác minh; adapter/hosting sink thử hỗ trợ contract, không gọi hosting thật; thiếu điều kiện = BLOCKED |
| Test Data | Project thử và marker run, URL sink nội bộ được allowlist |
| Test Steps | Gửi một request deployment hợp lệ theo adapter đã chọn; quan sát sink; đọc lại resource/status liên quan |
| Expected Result | Đích và payload khớp contract; trạng thái success có evidence từ sink; không tạo deployment thật hoặc ghi secret; không suy verdict AI |
| Phương pháp tự động hóa | Client giao thức; sink nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client giao thức; sink nội bộ |
| Dọn dữ liệu | Xóa resource thử bằng API đã duyệt; kiểm sink/resource sạch; restore profile |
| Execution Status / Evidence | NOT_RUN / chưa có; derived_from=TC55; thiết kế tách, không kế thừa historical verdict |

#### TC62 — Deployment error không báo thành công giả

| Thuộc tính | Thiết kế dự kiến |
|---|---|
| Module / Requirement ID | OPTION — AI, MCP và Deployments / SYS-OPTION-05 |
| Mục tiêu | Deployment error không báo thành công giả |
| Test Type | Chức năng/tích hợp; kiểm quyền hoặc lỗi khi bước có yêu cầu |
| Test Design Technique | Integration; Negative |
| Priority | P3 — I=3, L=1, C=1, S=5; lộ dữ liệu/secret có tác động cao nhưng feature/provider chưa áp dụng được xác minh; không hạ impact vì thiếu môi trường (đánh giá thiết kế, cần review M1) |
| Preconditions | Như TC61 nhưng sink cố định lỗi có nguồn; precondition độc lập, không phụ thuộc TC61 PASS |
| Test Data | Request deployment marker riêng, lỗi adapter được xác định trước |
| Test Steps | Gửi request hợp lệ tới sink lỗi; đọc response và deployment status theo API bản pin |
| Expected Result | Trạng thái lỗi đúng contract; không báo success hoặc tạo deployment ngoài lab; secret không xuất trong response/log; AI có verdict riêng |
| Phương pháp tự động hóa | Client giao thức; sink nội bộ; assertion từng bước và read-back riêng; UI/protocol có timeout/correlation; chỉ là đề xuất |
| Công cụ thực hiện | Client giao thức; sink nội bộ |
| Dọn dữ liệu | Dọn resource thất bại và sink, restore profile; cleanup lỗi báo riêng |
| Execution Status / Evidence | NOT_RUN / chưa có; derived_from=TC55; thiết kế tách, không kế thừa historical verdict |

## Phụ lục B. RTM thiết kế và alias lịch sử

Bảng này là bản trình bày cho người đọc. Dữ liệu chuẩn cần triển khai theo mục 6.8; mappings DIRECT/SUPPORTING phải được chốt, không coi mọi alias là requirement mới. TC tách dùng version mới và không kế thừa execution. Bảng ghi P1–P4 của ca mới theo I/L/C; legacy giữ metadata cũ.

| Requirement ID | Module | Requirement | Risk | Priority | Test Case ID | Test Type | Automation | Execution Status | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| LEGACY-TC01 | Legacy Items/Query/RBAC | CRUD article | Xem BR/AC cũ | P1 | TC01 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC02 | Legacy Items/Query/RBAC | Filter published | Xem BR/AC cũ | P1 | TC02 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC03 | Legacy Items/Query/RBAC | Sort/pagination | Xem BR/AC cũ | P1 | TC03 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC04 | Legacy Items/Query/RBAC | Reader draft | Xem BR/AC cũ | P1 | TC04 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC05 | Legacy Items/Query/RBAC | Field kín | Xem BR/AC cũ | P1 | TC05 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC06 | Legacy Items/Query/RBAC | Reader write | Xem BR/AC cũ | P1 | TC06 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC07 | Legacy Items/Query/RBAC | CRUD category | Xem BR/AC cũ | P1 | TC07 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC08 | Legacy Items/Query/RBAC | Anonymous | Xem BR/AC cũ | P1 | TC08 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC09 | Legacy Items/Query/RBAC | score=-1 | Xem BR/AC cũ | P1 | TC09 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC10 | Legacy Items/Query/RBAC | score=0 | Xem BR/AC cũ | P1 | TC10 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC11 | Legacy Items/Query/RBAC | score=5 | Xem BR/AC cũ | P1 | TC11 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC12 | Legacy Items/Query/RBAC | score=6 | Xem BR/AC cũ | P1 | TC12 | REST nghiệp vụ/hợp đồng | Có trong harness | PASS lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| LEGACY-TC13 | Legacy Items/Query/RBAC | POST contract | Xem BR/AC cũ | P1 | TC13 | REST nghiệp vụ/hợp đồng | Có trong harness | FAIL lịch sử | Mục 5, nguồn 18/10 | Alias tạm, không đổi TC |
| SYS-AUTH-01 | AUTH | Refresh token và chấm dứt phiên | I3/L2/C3 | P1 | TC14 | State Transition; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-AUTH-02 | AUTH | Sai mật khẩu không cấp phiên | I2/L2/C2 | P2 | TC15 | Equivalence Partitioning; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-RBAC-01 | RBAC | Hợp nhất hai policy của cùng người dùng | I2/L2/C2 | P2 | TC16 | Decision Table; RBAC | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-RBAC-02 | RBAC | Reader không tự nâng quyền hệ thống | I3/L2/C3 | P1 | TC17 | RBAC; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-MODEL-01 | MODEL | Vòng đời collection và field | I2/L2/C2 | P2 | TC18 | State Transition; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-MODEL-02 | MODEL | Quyền thay đổi mô hình dữ liệu | I3/L2/C3 | P1 | TC19 | RBAC; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-ITEM-01 | ITEM | Sửa nhiều item theo danh sách ID | I2/L2/C2 | P2 | TC20 | Equivalence Partitioning; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-ITEM-02 | ITEM | Xóa nhiều item giới hạn tập đích | I2/L2/C2 | P2 | TC21 | State Transition; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-QUERY-01 | QUERY | Filter đồng thời qua quan hệ nhiều nhiều | I2/L2/C2 | P2 | TC22 | Decision Table; Equivalence Partitioning | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-QUERY-02 | QUERY | Payload JSON hỏng cho bulk mới | I2/L2/C2 | P2 | TC23 | Negative; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-REL-01 | REL | Thêm và gỡ liên kết M2M | I2/L2/C2 | P2 | TC24 | Stateful; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-REL-02 | REL | Rollback khi nested write thất bại | I3/L2/C3 | P1 | TC25 | Negative; Stateful | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-FILES-01 | FILES | Upload và download bảo toàn nội dung | I2/L2/C2 | P2 | TC26 | State Transition; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-FILES-02 | FILES | Asset riêng tư không lộ qua biến đổi | I3/L2/C3 | P1 | TC27 | RBAC; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-FLOW-01 | FLOW | Flow có nhánh điều kiện | I2/L2/C2 | P2 | TC28 | Decision Table; Stateful | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-FLOW-02 | FLOW | Nhánh reject khi operation lỗi | I2/L2/C2 | P2 | TC29 | Negative; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-HISTORY-01 | HISTORY | Revision truy vết sửa dữ liệu | I2/L2/C2 | P2 | TC30 | State Transition; RBAC | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-HISTORY-02 | HISTORY | Version không đổi bản chính trước promote | I2/L2/C2 | P2 | TC31 | State Transition; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-INSIGHT-01 | INSIGHT | Dashboard và panel qua API | I2/L1/C2 | P3 | TC32 | Stateful; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-INSIGHT-02 | INSIGHT | Preset cá nhân được cách ly | I2/L1/C2 | P3 | TC33 | RBAC; Decision Table | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SERVER-01 | SERVER | Giới hạn thông tin server công khai | I2/L2/C2 | P2 | TC34 | RBAC; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SERVER-02 | SERVER | Thay setting thử rồi khôi phục | I2/L2/C2 | P2 | TC35 | State Transition; RBAC | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SCHEMA-01 | SCHEMA | Diff rỗng khi schema không đổi | I2/L2/C2 | P2 | TC36 | Contract; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SCHEMA-02 | SCHEMA | Apply thay đổi schema trong DB tạm | I2/L2/C2 | P2 | TC37 | Stateful; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-GQL-01 | GQL | GraphQL không vượt quyền theo field | I3/L2/C3 | P1 | TC38 | RBAC; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-GQL-02 | GQL | Mutation GraphQL tạo và cập nhật | I2/L2/C2 | P2 | TC39 | Stateful; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-RT-01 | RT | Subscription chỉ nhận sự kiện được phép | I3/L2/C3 | P1 | TC40 | RBAC; Stateful | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-RT-02 | RT | Đóng phiên realtime khi auth không hợp lệ | I2/L2/C2 | P2 | TC41 | Negative; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-UI-01 | UI | Đăng nhập và duy trì phiên Studio | I2/L2/C2 | P2 | TC42 | End-to-end; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-UI-02 | UI | Studio với user hạn quyền | I3/L2/C3 | P1 | TC43 | End-to-end; RBAC | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-EXT-01 | EXT | Endpoint extension có kiểm quyền | I2/L1/C2 | P3 | TC44 | RBAC; Integration | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-EXT-02 | EXT | Extension lỗi không phá endpoint lõi | I2/L1/C2 | P3 | TC45 | Negative; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SHARE-01 | SHARE | Share chỉ truy cập item được chia sẻ | I3/L2/C3 | P1 | TC46 | RBAC; Decision Table | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SHARE-02 | SHARE | Share hết hạn bị chặn | I2/L2/C2 | P2 | TC47 | Boundary Value; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-COLLAB-01 | COLLAB | Comment Unicode gắn đúng item | I2/L1/C2 | P3 | TC48 | Equivalence Partitioning; Stateful | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-COLLAB-02 | COLLAB | Notification đúng người nhận và cách ly người khác | I2/L2/C2 | P2 | TC49 | RBAC; Decision Table | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-IMPORT-01 | IMPORT | Import CSV vào collection riêng | I2/L2/C2 | P2 | TC50 | Equivalence Partitioning; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-IMPORT-02 | IMPORT | Import có field không được phép | I3/L2/C3 | P1 | TC51 | RBAC; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-OPS-01 | OPS | Cache tôn trọng thay đổi quyền | I3/L2/C3 | P1 | TC52 | RBAC; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-OPS-02 | OPS | Rate limit và phục hồi sau cửa sổ | I2/L2/C2 | P2 | TC53 | Boundary Value; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-OPTION-01 | OPTION | MCP không đọc dữ liệu ngoài policy | I3/L1/C1 | P3 | TC54 | RBAC; Contract | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-OPTION-02 | OPTION | AI success qua provider thử trong lab | I1/L1/C1 | P4 | TC55 | Integration; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SDK-01 | SDK | SDK duy trì phiên và gọi API | I2/L1/C1 | P3 | TC56 | Integration; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-SDK-02 | SDK | SDK xử lý lỗi có cấu trúc | I2/L1/C1 | P3 | TC57 | Negative; Regression | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | Reuse/delta xem mục 8 |
| SYS-UI-03 | UI | CRUD Studio trên phiên đã xác thực | I2/L2/C2 | P2 | TC58 | End-to-end; State Transition | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | derived_from TC42; verdict riêng |
| SYS-COLLAB-03 | COLLAB | Bản dịch vi/en không ghi đè locale khác | I2/L1/C2 | P3 | TC59 | RBAC; Decision Table | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | derived_from TC49; verdict riêng |
| SYS-OPTION-03 | OPTION | AI error không lộ secret và không tạo kết quả thành công | I3/L1/C1 | P3 | TC60 | Integration; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | derived_from TC55; verdict riêng |
| SYS-OPTION-04 | OPTION | Deployment success chỉ tới đích thử | I1/L1/C1 | P4 | TC61 | Integration; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | derived_from TC55; verdict riêng |
| SYS-OPTION-05 | OPTION | Deployment error không báo thành công giả | I3/L1/C1 | P3 | TC62 | Integration; Negative | Đề xuất, chưa triển khai | NOT_RUN | Chưa có | derived_from TC55; verdict riêng |

