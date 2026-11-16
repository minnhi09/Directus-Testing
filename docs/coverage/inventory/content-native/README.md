# P04 — Inventory nội dung và chức năng native

Revision: `P04-CONTENT-NATIVE-4f77933-v1`. Đây là kiểm kê source, không phải báo cáo test.

## Baseline và đầu vào

- Harness: `D:/DAMH-full-recovery-2026-10-12/DAMH`, HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`.
- Source: `D:/DAMH-full-recovery-2026-10-12/directus`, đọc Git object `4f77933bf9551cac6b289576078783e189b8f4e3` (Directus 12.5.0 theo [manifest](../../../../manifest/baseline.yaml)). Checkout source ở HEAD khác; không dùng HEAD đó làm baseline.
- Đã đối chiếu [P00](../../handoffs/P00.md), [P01](../../handoffs/P01.md), [quy tắc P03](../auth-system/README.md) và fingerprint các đầu vào. Không gán phê duyệt scope/runtime cho người khác.
- [Source index](source-index.json) ghi 54 file đã đọc, blob OID, SHA-256, số dòng và ledger route tại commit pin. Mọi diễn giải có `source_refs`; không sao chép source monorepo.
- [Audit evidence](audit-evidence.json) lưu kết quả kiểm cấu trúc, nguồn và dấu vân tay. Baseline/input cụ thể nằm trong [handoff P04](../../handoffs/P04.md).

## Các artifact và cách đọc

| File | Nội dung |
|---|---|
| [system-inventory.jsonl](system-inventory.jsonl) | 122 bản ghi theo schema P01 1.0.0; khóa method/path/variant/profile |
| [route-evidence.jsonl](route-evidence.jsonl) | 122 bản ghi cùng inventory ID: mount, khai báo gốc, guard/flag/license, lịch sử OAS |
| [capabilities.jsonl](capabilities.jsonl) | 46 capability có route liên quan hoặc lý do không có HTTP operation độc lập |
| [unresolved-routes.jsonl](unresolved-routes.jsonl) | 19 mục: 15 SEARCH và 4 ranh giới chuẩn hóa/dependency/profile |
| [unresolved-routes.md](unresolved-routes.md) | Giải thích gap và bước xử lý |
| [gaps.jsonl](gaps.jsonl) | 10 gap OPEN, owner đề xuất, target/source, điều kiện xử lý |
| [decisions.jsonl](decisions.jsonl) | 3 quyết định PROPOSED; chưa có người/ngày duyệt |
| [inventory-audit-coverage.json](inventory-audit-coverage.json) | Tiến độ chính đợt đọc source; không phải coverage API/test |
| [source-index.json](source-index.json) | Đối chiếu từng khai báo source với inventory/unresolved |

18 controller family của P04 đã được đọc ở baseline: items; files/folders/assets/tus; flows/operations; activity/revisions/versions; dashboards/panels/presets; shares/comments/notifications/translations; utils. Các service/guard liên quan được đọc theo entrypoint và capability, không tuyên bố đã kiểm mọi thuật toán/dependency.

Ledger có **136 khai báo HTTP tường minh**: 15 SEARCH được giữ ngoài inventory chính vì enum P01 chưa hỗ trợ; 121 khai báo còn lại tạo 122 bản ghi do GET assets có filename tùy chọn. Đây là phép đối chiếu khai báo với path shape, không phải 122 ca kiểm thử. Không trùng operation key hoặc inventory ID với shard P03.

Capability có 18 nhóm HTTP, 9 tập con HTTP, 15 tính năng dùng chung và 4 tính năng không phải HTTP. 19 capability cuối không tạo operation độc lập. Query/bulk/validation/export format/locale/operation.type không nhân số operation.

## Chuẩn hóa path, quyền và trạng thái

Giữ tên tham số nguồn: `{collection}`, `{pk}`, `{id}`, `{filename}`, `{revision}`. Không thay template bằng fixture ID. Khóa theo quy tắc P03: `REST|METHOD|path_template|route_variant|feature_profile`; không coi hai tham số khác tên là alias đã xác nhận.

- `/assets/:pk/:filename?` thành hai path shape; evidence giữ một khai báo nguồn.
- `/assets/files/` giữ thông tin slash trong evidence, variant `TRAILING_SLASH_DECLARED`; không thêm operation cho cả hai spelling.
- Flow trigger và share detail/info có UUID constraint: template `{pk}`, variant `UUID_PATTERN`; evidence trỏ hằng UUID tại source, không mất constraint.
- TUS có năm khai báo POST/PATCH/DELETE/OPTIONS/HEAD tường minh và mount phụ thuộc `TUS_ENABLED === true`. Giữ profile chưa xác minh; quyền upload metadata có thể chuyển POST từ create sang update. Không suy thêm method do thư viện hoặc implicit HEAD.
- Assets có nhánh HEAD bên trong GET handler; đây là capability/dispatch cần kiểm chứng, không sinh một HEAD operation giả.
- Permission summary chỉ mô tả middleware/guard/service tại source. Quyền actor/policy/field/row thực tế, branch singleton/bulk/payload rỗng đều CHƯA XÁC MINH. Không suy rằng mọi payload batch đều chạy cùng guard.
- Source có những nhánh hạn chế admin như generate translations và clear cache; không diễn giải thành toàn bộ utils đều admin.
- Core/Extended/Conditional là đề xuất. Mọi `applicability`, `deployed_state`, `oas_state` đều `UNKNOWN`; không chốt mẫu số.

Items query, validation, bulk, singleton và nested transaction là capability gắn route. Version query dùng lại item read; version compare/save/promote có route riêng. Activity/revision được sinh bởi mutation/event và giới hạn retention là hành vi, không tạo POST activity/revisions. Flow event filter/action, schedule và dynamic handler chain giữ capability không có endpoint riêng. Các thuật toán sâu của operation registry, extension/provider và storage driver chưa được kiểm kê hết.

Files multipart/URL import, asset transform/range/ZIP, resumable TUS, notification/share email, import stream/batch/background và export-to-file được gắn source/ref; chưa upload/download, gửi mail hay thực thi job. Respond middleware có export format trên read endpoint; không nhân một operation cho mỗi CSV/XML/JSON/YAML.

## OAS lịch sử và phần chưa kiểm kê

Snapshot admin `runtime/schemas/r06-k05-v2/admin.json` chỉ là artifact lịch sử được hash. Candidate exact, đổi tên pk/id hoặc binding collection `qa_articles/qa_categories` chỉ để đối chiếu nguồn; không chốt alias, current presence hay scope theo nó. Giữ gap P03: file có 143 method/path entry nhưng counter manifest lịch sử ghi 14 chưa rõ phạm vi. Không sửa manifest/raw OAS hoặc export live.

[Tiến độ](inventory-audit-coverage.json) chỉ có mẫu mục tiêu hữu hạn là 18 controller family của P04. `system_inventory_complete=false`, mẫu số applicable là null, coverage API/code là `NOT_MEASURED`, test là `NOT_RUN`. Chưa kiểm kê ở đây: GraphQL/WebSocket/Realtime/Studio/SDK, AI/MCP/deployments/extensions/custom loaders (P05 hoặc sau); toàn bộ dynamic type/backend implementation; cấu hình runtime, scheduler infrastructure và tác động IO thực tế.

## Hợp đồng sidecar

P01 không có schema capability độc lập, nên không sửa interface cũ hoặc bịa route. Các sidecar có version riêng để downstream phải đọc/migrate tường minh:

- `P04_CAPABILITY_1`: ID, module, representation, inventory_ids/related_inventory_ids, independent_http_operation, reason_no_independent_operation, source_refs/gap_ids và trạng thái UNKNOWN. Tính năng không HTTP dùng related IDs cho route quản lý, không gọi chúng là endpoint trigger.
- `P04_ROUTE_EVIDENCE_1`: inventory_id nối một-một; declaration/mount/constraint/guard/condition và historical OAS refs.
- `unresolved-routes.jsonl`: unresolved_id, kind, source_refs; SEARCH giữ method và template gốc. Không tự đổi SEARCH thành GET hay N/A.
- `P04_SOURCE_INDEX_1` và `P04_INVENTORY_AUDIT_PROGRESS_1`: ledger nguồn và tiến độ đọc source, không tiêu thụ như summary test.

Các schema P01, P03, TC01–TC13, report, raw OAS và harness được giữ nguyên. Không tạo RTM/catalog link từ route sang TC khi chưa có evidence cho liên kết đó.

## Kiểm tra có thể tái lập

Đọc đúng source bằng `git -C ../directus show 4f77933bf9551cac6b289576078783e189b8f4e3:api/src/controllers/items.ts`; không checkout. Dùng SHA/line range trong source index và source_refs để đối chiếu các file còn lại.

P04 đã kiểm JSON không trùng key, P01 JSON Schema cho inventory/gap/decision bằng PowerShell 7 Test-Json (resolve common defs cục bộ), tham chiếu/khóa liên shard, ledger/mount/path shapes, nguồn Git/hash/dòng và bảo toàn đầu vào. Chi tiết exit/count/fingerprint nằm trong audit evidence và handoff. Không chạy workflow P02, unit/integration/fuzz, API, export OAS hoặc lab. Remote CI không được kích hoạt.

