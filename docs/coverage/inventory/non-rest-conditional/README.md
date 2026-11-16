# P05 — Giao thức và tính năng có điều kiện

Revision `P05-NON-REST-CONDITIONAL-4f77933-v1`, schema P01 1.0.0. Audit source tại `4f77933bf9551cac6b289576078783e189b8f4e3`; không phải runtime/test.

- [system-inventory.jsonl](system-inventory.jsonl): 52 record — 18 nhóm capability giao thức/client và 34 REST route tường minh liên quan. Nhóm protocol là mức kiểm kê capability, chưa phải danh sách mọi field/message/tool/SDK command.
- [capabilities.jsonl](capabilities.jsonl): 18 nhóm GraphQL items/system, WS REST/GraphQL/logs/collab, Studio, extension loader/endpoint/hook-operation, AI, MCP/OAuth, deployment và bốn SDK composable; nối REST ID và canonical ID P03/P04.
- [conditional-dependencies.jsonl](conditional-dependencies.jsonl): flag, settings/profile, contract, actor, sink/fixture/oracle cần có theo từng nhóm.
- [integration-crossrefs.json](integration-crossrefs.json): tái dùng storage backend, email side effect, flow operation registry từ P04; không tạo route/case mới.
- [route-evidence.jsonl](route-evidence.jsonl), [source-index.json](source-index.json): mount/declaration tại SHA pin, 36 file nguồn và 43 khai báo HTTP.
- [unresolved-routes.jsonl](unresolved-routes.jsonl): 9 khai báo chưa serialize P01: 2 SEARCH, 2 wildcard OAuth discovery, 5 UUID-constrained extension routes. Giữ nguyên pattern và ref; không tự đổi GET/N/A, không xóa route.
- [gaps.jsonl](gaps.jsonl), [decisions.jsonl](decisions.jsonl): 6 gap OPEN và scope proposal chưa duyệt.
- [input-fingerprints.json](input-fingerprints.json), [audit-evidence.json](audit-evidence.json): snapshot trước sửa và kiểm cấu trúc/source/bảo toàn.

Mọi applicability/deployed_state/oas_state là UNKNOWN. Source-present không đồng nghĩa enabled; Compose và env **mẫu** không chứng minh cấu hình hiệu lực. Không đọc env thật hoặc giá trị credential. Core/Extended/Conditional theo mục 3.2 vẫn là đề xuất.

GraphQL có scope items và system; middleware cho GET/POST, GET chỉ query. Schema tạo theo accountability, cần introspection/SDL actor riêng; REST OAS không thay schema GraphQL. WS cần WEBSOCKETS_ENABLED cùng flag từng controller/handler; PATH/AUTH và timeouts từ config, license/upgrade/actor checks tại source. Collab mới đọc entrypoint đăng ký, chưa kiểm toàn giao thức. Không mặc định SDK /websocket chính là endpoint triển khai.

Studio có shell /admin khi SERVE_APP và navigation/session/license trong app router; không coi một GET HTML là kiểm UI/module view. Extensions có loader/sandbox, endpoint động, hook/operation và management/registry routes; endpoint cụ thể phụ thuộc extension fixture chưa có. Không cài marketplace extension hoặc dựng route giả.

AI có chat/object/files router và settings loader; cần provider/model/actor/oracle/sink/budget được kiểm chứng sau. MCP có JSON-RPC initialization/tools/prompts và HTTP carrier GET/POST; không đếm tool thành REST route. OAuth env/project settings, cookie consent/CSRF, redirect/rate controls và clients admin guard riêng; public mount không đồng nghĩa mọi thao tác không cần kiểm quyền.

Deployments có REST management/project/run/cancel và webhook trước authenticate; handler xác minh provider/signature. Không giả mọi provider chạy được hoặc suy trạng thái runtime từ mount. SDK là client composable và chỉ áp dụng nếu phạm vi SUT được chốt; không nhân lại server operation/test theo SDK command/retry.

Sidecar version P05_CAPABILITY_1, P05_CONDITIONAL_DEPENDENCY_1, P05_ROUTE_EVIDENCE_1 và P05_INTEGRATION_CROSSREFS_1 là tài liệu có cấu trúc, không sửa schema P01. REST key theo P03; non-REST dùng transport + protocol_operation + variant + profile. FK liên shard được giữ, không tạo alias là ca độc lập. Không tạo catalog/RTM link test khi chưa có evidence.

Coverage API/code NOT_MEASURED; test NOT_RUN; denominator null; inventory toàn hệ thống chưa hoàn chỉnh. Chưa kiểm kê sâu: GraphQL generated fields theo actor/schema, WS/collab mọi message branch, Studio mọi view, dynamic extension/tool/driver/provider implementation và mọi SDK command. Gap depth phải được xử lý trước khi tuyên bố inventory chi tiết toàn hệ thống hoàn chỉnh.

Tái lập đọc source: `git -C ../directus show 4f77933bf9551cac6b289576078783e189b8f4e3:api/src/controllers/graphql.ts`; dùng file/hash/dòng ở source-index để đọc tiếp. Kiểm offline thực tế và giới hạn nằm trong [handoff P05](../../handoffs/P05.md). Không chạy P02 gate/test/API/OAS export/lab; không commit/push hoặc kích hoạt CI.
