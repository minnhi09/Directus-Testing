# Inventory P03 — auth và API hệ thống

Revision shard: **P03-AUTH-SYSTEM-4f77933-v1**, hợp đồng record P01 **1.0.0**. Baseline source **4f77933bf9551cac6b289576078783e189b8f4e3**, sản phẩm 12.5.0 theo manifest/P00. Đây là inventory tĩnh từ object Git, **không phải runtime observation, test execution hoặc mẫu số REST đã khóa**. Xem [handoff P03](../../handoffs/P03.md), [hợp đồng P01](../../README.md).

## File và cách dùng

- [system-inventory.jsonl](system-inventory.jsonl): 113 record đúng `system-inventory.schema.json` P01; `data_origin: DERIVED` vì ghép mount/router và chuẩn hóa path từ source. `oas_state` là field P01 biểu diễn thuật ngữ “oas_presence”; không rename/thêm field vào schema cũ.
- [route-evidence.jsonl](route-evidence.jsonl): sidecar **P03_ROUTE_EVIDENCE_1**, một record theo `inventory_id`, chứa pattern/source declaration nguyên bản, permission summary, mount/handler/license conditions và đối chiếu OAS lịch sử. P01 chưa có field permission/license riêng; sidecar này là tài liệu có cấu trúc, không phải record inventory mở rộng hoặc schema version mới.
- [source-index.json](source-index.json): 44 source file @SHA, Git blob OID/SHA-256/line count; ledger đủ 115 khai báo HTTP ở 14 controller và 5 driver factory, ánh xạ record inventory hoặc entry chưa phân giải. Không copy monorepo/source body vào DAMH.
- [audit-evidence.json](audit-evidence.json): kết quả kiểm cấu trúc record/source references/ledger và fingerprint của shard; chỉ audit tài liệu/dữ liệu, không phải run test/API.
- [gaps.jsonl](gaps.jsonl), [decisions.jsonl](decisions.jsonl): 7 gap OPEN, 2 decision PROPOSED theo P01; approved_by/date null, không giả duyệt scope hoặc N/A.
- [unresolved-routes.jsonl](unresolved-routes.jsonl) và [bản đọc nhanh](unresolved-routes.md): 10 entry chờ hợp đồng/runtime/đối chiếu; giữ đủ method/path/source. SEARCH chưa vừa enum P01 được giữ ở đây, không đổi sang GET.

`source_refs` Git có path tương đối từ DAMH, revision baseline, SHA-256 byte source và fragment dòng `#Lx-Ly`. Repo Directus hiện checkout SHA khác baseline; muốn đọc lại dùng `git -C ../directus show 4f77933bf9551cac6b289576078783e189b8f4e3:api/src/...`, không mở file checkout hiện tại rồi gắn cho baseline. Source-index không chứng minh runtime hoặc feature được triển khai.

## Phạm vi và số cấu trúc

| Họ controller | Record path/variant đã biểu diễn trong shard |
|---|---:|
| `access` | 7 |
| `auth` | 18 |
| `collections` | 6 |
| `fields` | 7 |
| `license` | 11 |
| `metrics` | 1 |
| `permissions` | 10 |
| `policies` | 8 |
| `relations` | 6 |
| `roles` | 8 |
| `schema` | 3 |
| `server` | 7 |
| `settings` | 3 |
| `users` | 18 |

115 khai báo HTTP literal được audit (bao gồm 6 SEARCH); tạo 113 record theo công thức truy vết **115 − 6 SEARCH + 2 shape optional + 1 mount default-local bổ sung + 1 app ping = 113**. Một khai báo local factory được mount cả default và configured-provider; hai pattern optional cuối được biểu diễn thành hai path shape. Đây là số cấu trúc của shard, không phải 113 test, 113 route runtime đã hit, hoặc denominator toàn hệ thống. Module/actor/feature profiles có thể cần hợp nhất sau inventory/OAS/scope review. Đếm router không là đếm operation.

`deployed_state`, `applicability` và `oas_state` của **mọi** record đều **UNKNOWN**. Scope tier Core/Extended/Conditional là đề xuất từ kế hoạch mục 3–4 và tính chất route, tham chiếu DEC-P03-SCOPE; không đồng nghĩa áp dụng đã duyệt. Gap `blocking: true` chặn việc khóa baseline/đo/thực thi phụ thuộc, không phủ nhận audit source P03 đã xong. Requirement/RTM/canonical map thực chưa tạo ở P03; tái dùng catalog/helper/fixture/oracle theo P00/P01 khi P06 được giao, không tạo test ID mới từ route inventory.

Các nhóm controller khác, GraphQL query/mutation/subscription, MCP/OAuth của MCP, Studio, extension/hook tùy chỉnh và transport khác không được tuyên bố đã inventory xong; nằm ở shard P04/P05 phù hợp. REST endpoint trả SDL `/server/specs/graphql` vẫn là REST, không thành GraphQL execution coverage. Không cộng implicit HEAD/OPTIONS từ Express vào record nếu chưa có requirement áp dụng.

## Mount, quyền và điều kiện nguồn

- `GET /server/ping` nằm trực tiếp ở app.ts:320, **trước authenticate**; extractToken và rate limiters có điều kiện vẫn đứng trước. Ping không xác nhận authenticated health/license.
- Các mount còn lại thuộc P03 đi qua authenticate → mcpOAuthGuard → schema/sanitizeQuery/requestCounter/cache (app.ts:329–342). Authenticate tạo/điền accountability, không phải blanket yêu cầu user/admin; MCP OAuth sessions bị guard hạn chế khác với session thường. Không suy controller không có checkIsAdmin là public.
- CRUD Users/Roles/Policies/Permissions/Access đưa accountability vào service. `useCollection` chỉ gán collection, không tự là permission guard. Quyền actor/field/row thực chưa đo; self/share/fallback và batch body/query có thể khác hành vi nhưng không thành nhiều operation nếu cùng method/path/profile.
- `/users/me` GET có nhánh share; PATCH cần user. Track-page dùng current user guard nhưng service update last_page không truyền accountability. TFA cần current user/OTP/password tùy provider; disable user khác có admin guard. Invite/register/verify-email cần token/state/settings/profile; không gửi email hay gọi service trong audit.
- Collections/Fields/Relations mutation có service guard `accountability && admin !== true` → Forbidden. Với Collections createMany và Fields updateFields, guard của thao tác con được gọi theo từng phần tử; empty batch không đi qua per-item guard, nên không suy mọi payload trên endpoint đều bị Forbidden. Internal null/system khác HTTP anonymous. Các read dùng permission filtering/validateAccess; field system/collection-exists restrictions được giữ trong source/sidecar, không biến mọi read thành admin-only.
- Schema snapshot/diff/apply đều `checkIsAdmin`; diff/apply là mutation/snapshot DB có precondition riêng, không chạy trên lab cũ.
- Settings service singleton/upsert và payload entitlement chưa là bằng chứng actor được phép. Settings mutation là Extended đề xuất; không đổi config, owner hoặc license trong phase này.
- License phần lớn checkIsAdmin; preview chỉ public khi onboarding, sau setup cần admin. Portal/addon/resolve/activate/update/deactivate giữ dependency/side-effect UNKNOWN; audit chỉ source, không đọc hoặc chép license key.
- Metrics mount chỉ khi `METRICS_ENABLED === true`. Handler chấp nhận admin hoặc authorization scheme **Metrics** với cấu hình METRICS_TOKENS; giá trị thật không đọc. Scheme này không bị đổi thành Bearer trong dữ liệu.
- Server OAS mount khi `OPENAPI_ENABLED !== false`; SDL khi `GRAPHQL_INTROSPECTION !== false`; health khi `toBoolean(HEALTHCHECK_ENABLED) !== false`. Health service từ chối unauthenticated, admin thấy chi tiết, actor khác chỉ status. Setup chỉ khi chưa có user theo service; không dùng nó để “kiểm tra” lab.

Source cho từng điều kiện nằm ngay trong record/sidecar, gồm controller, service hoặc middleware cần thiết tại cùng SHA. Các field `mount_conditions` tách `handler_conditions`/`license_conditions`; `feature_flag` có thể ghi condition ở handler và chỉ rõ không phải mount flag. Không giả giá trị config runtime từ default/source.

## Path, provider và OAS

Giữ nguyên tên tham số source: `:pk` → `{pk}`, `:collection` → `{collection}`, `:field` → `{field}`; không cắm ID thật hoặc tên fixture đã seed. Query không vào path/key. Profile `BASELINE_UNVERIFIED` là nhãn inventory source, không cấu hình runtime đã xác minh.

`/permissions/me/:collection/:pk?` và `/server/specs/graphql/:scope?` được khai triển thành path không/có segment cuối; source pattern nguyên bản và gap PATH-SHAPES vẫn giữ. Hai TFA source path kết thúc slash được chuẩn hóa bỏ slash nhưng có variant `TRAILING_SLASH_DECLARED`; chưa khẳng định slash/non-slash dispatch tương đương. Không cộng các shape/variant thành ca test độc lập.

Đã lần từ auth.ts:34–67 tới đủ factory local/LDAP/OAuth2/OpenID/SAML. Default local POST `/auth/login` tách configured local POST `/auth/login/{provider}`. Các driver dùng chung template có variant/profile riêng, không gộp OAuth2/OpenID/SAML hoặc đếm theo số provider name thật chưa biết. Factory local có checkLocalAuthDisabled; SSO có checkSsoEnabled + entitlement/bypass. Provider names/settings/license/TFA và request thành công đều CHƯA XÁC MINH.

OAS admin lịch sử `runtime/schemas/r06-k05-v2/admin.json` có SHA-256 **993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e**, khớp manifest; kiểm trực tiếp thấy **143** method/path entry trong toàn file. Manifest ghi `schema_operation_counts.admin: 14`; phạm vi/counter/provenance khác biệt chưa truy nguyên. Không dùng số 14 hoặc 143 làm mẫu số toàn REST hiện tại.

Sidecar phân biệt exact-template trong file lịch sử, potential parameter alias (`{id}` so với tên source) và không thấy match **trong file lịch sử**. OAS refs có certainty HISTORICAL; potential alias chưa là canonical mapping. `/auth/oauth` và `/auth/oauth/{provider}` có ở artifact nhưng không tìm mount tương ứng trong auth/driver đã audit; giữ drift candidate, không dựng route source giả. Chưa có full/admin OAS hiện tại với provenance/actor/config đã xác minh nên core `oas_state: UNKNOWN` cho tất cả record; absence lịch sử không thành N/A hoặc source-only kết luận. Không export live hoặc sửa raw OAS.

Đo coverage toàn hệ thống/code/schema/runtime trong P03: **NOT_MEASURED**. Verdict test/API: **NOT_RUN**.

