# Hợp đồng dữ liệu coverage — 1.0.0

Hợp đồng P01 triển khai đặc tả của [kế hoạch](../KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md), mục 6.1–6.8 và 7; thang risk đối chiếu thêm mục 4.1. Đầu vào môi trường có provenance trong [P00](handoffs/P00.md). Đây là hợp đồng cho dữ liệu mới; không thay `manifest/baseline.yaml`, catalog/report cũ, raw OAS hoặc interface `lab.sh`/helper. Chưa khóa inventory, canonical map, scope, mẫu số hoặc nghiệm thu toàn hệ thống.

## Định dạng, version và file

JSON Schema **Draft 2020-12**; mọi record có `schema_version: "1.0.0"` và `data_origin` = `DESIGN_EXAMPLE | OBSERVATION | DERIVED`. Version hợp đồng độc lập với inventory/catalog revision, test version, version sản phẩm và version công cụ coverage. Mẫu `schema_version: "1"` trong kế hoạch là phác thảo, không phải interface cũ được di trú. Dữ liệu lịch sử chưa chuyển sang hợp đồng này vẫn nguyên bản.

Các file JSONL chứa một object UTF-8 trên mỗi dòng không rỗng; không bọc bằng array, không comment. Schema tương ứng kiểm **mỗi record**, không phải cả stream. JSONL không tự bảo đảm unique key hoặc foreign key giữa dòng/file. Object dùng `additionalProperties: false`; mở rộng field/enum phải revision hóa hợp đồng, không âm thầm đổi nghĩa. Thay đổi không tương thích tăng major; không ghi đè schema version đã phát hành. `$id` dưới `https://damh.invalid/coverage/1.0.0/` là identifier, không phải hosting hoặc URL cần gọi.

| File dữ liệu đích theo mục 6.8 | Schema trong `schemas/` | Khóa / đích ref |
|---|---|---|
| `baseline-manifest.json` | `baseline-manifest.schema.json` | PK `baseline_id`; chỉ định inventory/catalog revision |
| `system-inventory.jsonl` | `system-inventory.schema.json` | PK `(inventory_revision, inventory_id)`; `inventory_id` cũng là operation ID cho `operation_ids` |
| `requirements.jsonl` | `requirements.schema.json` | PK `(inventory_revision, requirement_id)`; `inventory_ids` → inventory cùng revision |
| `test-catalog.jsonl` | `test-catalog.schema.json` | PK `(catalog_revision, canonical_test_id, version)`; requirement/operation refs theo revision của baseline |
| `rtm-links.jsonl` | `rtm-links.schema.json` | PK `(inventory_revision, catalog_revision, requirement_id, canonical_test_id, test_version)` |
| `executions.jsonl` | `executions.schema.json` | PK `execution_id`; unique `(run_id, baseline_id, canonical_test_id, test_version, attempt)` |
| `decisions.jsonl` | `decisions.schema.json` | PK `decision_id` |
| `gaps.jsonl` | `gaps.schema.json` | PK `gap_id` |
| `coverage-summary.json` | `coverage-summary.schema.json` | Một baseline/selection/denominator revision/unit/filter; mỗi metric giữ tập ID riêng |
| `selection-manifest.json` | `selection-manifest.schema.json` | PK `selection_id`; khóa scope và quy tắc chọn run trước campaign, đáp ứng mục 6.8 quy tắc 4 |

`common.schema.json` cung cấp `$defs`; các `$ref` tương đối chỉ trỏ file này trong cùng thư mục. Không đặt schema/helper mới vào runtime cũ. Đích `artifacts/baselines/<baseline_id>/` và `artifacts/runs/<run_id>/` là quy ước tương lai của kế hoạch, chưa tạo/export trong P01. [examples/](examples/README.md) chứa bộ thiết kế nhỏ có cùng tên file dữ liệu, tách khỏi artifact thực.

## Kiểu, enum và giá trị chưa biết

ID là string ổn định gồm chữ/số và `_.:-`, bắt đầu bằng chữ hoặc số (chấp nhận run ID lịch sử); không lấy số hàng làm khóa. `version` của TC là string ID, ví dụ `1.0.0`. Không dùng alias làm foreign key trong dữ liệu mới. SHA Git gồm 40 hex thường; SHA-256 gồm 64 hex thường; image digest có tiền tố `sha256:`. Timestamp là RFC 3339 `date-time`; ngày quyết định là `date`. Validator cần bật kiểm `format` khi triển khai. Số đếm integer không âm; percentage là number 0–100 khi đủ điều kiện.

| Trường / họ trường | Giá trị và nghĩa |
|---|---|
| `transport` | `REST`, `GRAPHQL`, `WEBSOCKET`, `UI`, `CLI`, `SCHEDULER`, `INTEGRATION`; không cộng tỷ lệ khác giao thức |
| `scope_tier` | `CORE`, `EXTENDED`, `CONDITIONAL`; độc lập risk và deploy |
| `applicability` | `APPLICABLE`, `NOT_APPLICABLE`, `UNKNOWN`; UNKNOWN giữ gap, không tự loại khỏi mẫu số |
| `deployed_state` | Chỉ `ENABLED_VERIFIED`, `DISABLED_VERIFIED`, `UNKNOWN`; source-present không chứng minh enabled |
| `oas_state` | `PRESENT`, `SOURCE_ONLY`, `OAS_ONLY`, `UNKNOWN`; sai khác phải giữ gap, không âm thầm bỏ route |
| `coverage_role` | `DIRECT` hoặc `SUPPORTING`; supporting/setup/control không tăng D/E/V |
| `automation_state` | `MANUAL`, `PLANNED`, `IMPLEMENTED`, `PARTIAL`, `UNKNOWN`; IMPLEMENTED không đồng nghĩa đã chạy/PASS |
| Risk / priority | I/L/C: integer 1–3 hoặc null; `risk_scale_ref` dẫn thang nguồn. Priority `P1`/`P2`/`P3`/`P4`/`UNKNOWN`; theo mục 4.1, không viết lại priority legacy |
| `review_state` | `DRAFT`, `REVIEWED`, `LOCKED`; khóa revision dữ liệu không chứng nhận runtime hay nghiệm thu |
| Decision / gap | Decision: `PROPOSED`, `CONFIRMED`, `REJECTED`, `SUPERSEDED`; gap: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `DEFERRED` |

`null` biểu thị giá trị chưa biết/chưa đo **ở field có cho phép null**. Không dùng `"UNKNOWN"` thay hash/count, không dùng `0` thay count chưa biết. `UNKNOWN` là enum cho một trạng thái chưa rõ; diễn giải tiếng Việt: **CHƯA XÁC MINH**. `NOT_MEASURED` là `measurement_status` của metric; các count/percentage của metric đó bắt buộc null, kèm gap. Không đặt string này vào field số. Mảng rỗng trong draft là chưa có danh sách hoàn chỉnh, không khẳng định không còn thiếu.

Trong manifest, mỗi scalar chưa xác minh = null phải có `gap_ids` và `unresolved_fields["/<field>"]` trỏ gap. Hash actor null dùng pointer `/actor_schema_hashes/<actor_id>`; trạng thái harness UNKNOWN cũng phải nêu gap. Trong requirement, thiếu source/oracle/risk thì giữ gap; không chuyển sang N/A. `owner: null` = chưa phân công; `decision_id: null` = chưa có quyết định liên quan; `feature_flag: null` = không có flag riêng trong thiết kế; `derived_from: []` = không phải fork. Những null có nghĩa không liên quan như vậy không bị dùng làm xác nhận dữ liệu runtime.

## Nguồn, evidence và ref

`source_refs`, `oracle_ref(s)`, `cleanup_ref`, `evidence_refs` dùng object chung:

- `kind`: `GIT_FILE` (path + revision Git bắt buộc), `ARTIFACT` (path + SHA-256 bắt buộc), hoặc `DESIGN` (chỉ nguồn thiết kế, không chứng minh runtime).
- `path`: đường dẫn repo/artifact đã làm sạch; `revision`: commit hoặc null; `sha256`: hash artifact hoặc null; `pointer`: fragment `#...`, JSON pointer cho OAS, hoặc null.
- `certainty`: `VERIFIED`, `HISTORICAL`, `PROPOSED`, `UNKNOWN`; UNKNOWN phải có `gap_ids`. VERIFIED chỉ đúng phạm vi fact nguồn đó chứng minh; HISTORICAL không nâng thành kết quả baseline mới.

Tất cả ref phải resolve trong bundle/revision đang dùng hoặc registry artifact/finding được dẫn nguồn; không coi chuỗi ID đúng kiểu là ref đã tồn tại. `gap_ids` → gaps; `decision_id` → decisions; `target_ids` → registry ID của bundle (baseline, inventory, requirement, canonical test, selection, module/capability, execution/run hoặc finding có registry được dẫn nguồn). `prerequisites` → canonical test cùng catalog; `derived_from` → canonical + version trong revision nguồn phải lưu; không tự copy verdict của parent. `finding_id` → registry triage được dẫn nguồn ở phase sử dụng; null khi chưa phân loại, không tự đếm FAIL thành defect.

`baseline_id` của execution/selection/summary phải resolve manifest. Test refs của RTM/selection/execution phải khớp canonical ID và version của catalog được manifest chọn. Inventory/requirement/RTM revision phải khớp manifest; summary mang cả inventory/catalog revision để tránh join sai. Module/capability ID phải xuất hiện trong inventory revision tương ứng. Run ID không phải PK execution: một run có nhiều TC/attempt. `retry_of_execution_id` trỏ attempt trước của cùng TC/version/baseline, không tạo cycle; giữ tất cả attempt và flaky, không sửa history.

Không đưa env, token, password, license key, header/cookie, request/response body thật vào schema example hoặc record metadata. Lưu ref đến evidence đã kiểm soát và làm sạch. Schema không thể phát hiện secret giấu trong string; bước review nội dung vẫn bắt buộc. P01 không đọc env thật hoặc raw log để minh họa.

## Chuẩn hóa operation và alias

REST giữ HTTP method uppercase, path bắt đầu `/`, query tách khỏi path. Chuyển tham số theo route source thành `{parameter}`; ID cụ thể của item không là key. Chuẩn hóa tên tham số nhất quán trong revision theo source; route variant giữ trường hợp khác dispatch semantics. Không tự suy số literal trong route là item ID. Không gộp GET list và GET detail; không thêm HEAD/OPTIONS vào O nếu chưa có requirement/decision áp dụng.

Khóa so sánh REST trong `operation_key`:

```text
REST|<METHOD>|<path_template>|<route_variant>|<feature_profile>
```

Non-REST có `method: null`, `path_template: null`, `protocol_operation` khác rỗng. Khóa là `<TRANSPORT>|<protocol_operation>|<route_variant>|<feature_profile>`. Không đặt ký tự `|`, CR/LF hoặc khoảng trắng đầu/cuối trong component. Chuẩn hóa GraphQL operation, WebSocket event, UI action, CLI command... trong inventory riêng, không ép thành REST. `route_variant`/`feature_profile` dùng ID `DEFAULT` khi không có phân biệt cần thiết; điều kiện khác semantics phải có key riêng. Một capability có nhiều inventory operation; operation ID là `inventory_id`, không phải `operationId` ngẫu nhiên của OAS. Collision hoặc source/OAS khác nhau phải giữ gap và quyết định, không tự gộp.

Catalog giữ một canonical/version cho cùng mục tiêu, precondition, input partition và oracle. `aliases[]` là tên thay thế đã đối chiếu, `legacy_ids[]` là khóa provenance nguồn cũ. Trong cùng catalog revision, một alias không trỏ hai canonical, không trùng canonical của ca khác, không tạo alias chain/cycle. Version mới có thể tiếp tục cùng alias cho cùng canonical. TC/P3 thực chỉ map sau P06 có evidence; P01 không cấp canonical thật hoặc đổi mã TC01–TC13. Ví dụ alias đều bắt đầu `EXAMPLE-`, không là mapping lịch sử.

## Quan hệ nhiều–nhiều và trạng thái thực thi

RTM là bảng edge, không phải ô CSV ghép chuỗi. Requirement có nhiều TC; TC có nhiều requirement. `catalog.requirement_ids` là tập projection của các edge RTM của TC (cả hai role); RTM là nguồn quyết định role, `mandatory_for_requirement` và rationale. Một cặp requirement/TC/version chỉ có một edge trong revision, không ghi hai role để cộng đôi. Chỉ edge DIRECT có oracle/source đủ mới góp D; SUPPORTING không góp D/E/V dù ca control được tái sử dụng nhiều lần.

`execution_status`, `business_verdict`, `contract_verdict` dùng `PASS | FAIL | BLOCKED | NOT_RUN | INCOMPLETE | NOT_APPLICABLE` nhưng mô tả các chiều khác nhau. Ví dụ contract FAIL đã thấy trước max_time được giữ với execution INCOMPLETE; hoặc execution FAIL + completion INCOMPLETE. Không ghi đè FAIL vì chưa hoàn tất phạm vi.

- PASS: tất cả assertion bắt buộc của ca đã đánh giá và đạt, không còn thiếu assertion, cleanup xác minh. Schema chặn PASS với completion INCOMPLETE, business/contract FAIL, cleanup FAIL/UNKNOWN; danh sách assertion phải không rỗng. Kiểm tất cả assertion theo catalog/oracle là ràng buộc semantic cần validator và evidence.
- FAIL: actual vi phạm expected có nguồn; giữ assertion/evidence, không tự gọi là lỗi Directus. BLOCKED: thiếu tiền điều kiện/oracle nên chưa đánh giá mục tiêu. NOT_RUN: chưa bắt đầu, không có timestamp/request/assertion giả. INCOMPLETE: bắt đầu nhưng chưa xong phạm vi. N/A toàn ca cần decision_id được CONFIRMED có nguồn.
- `completion_status`: `COMPLETE`, `INCOMPLETE`, `NOT_STARTED`, `UNKNOWN`; `stop_reason` giữ riêng COMPLETED/MAX_TIME/TIMEOUT/CANCELLED/PRECONDITION_FAILED/ERROR/EVIDENCE_MISSING/NOT_STARTED/NOT_APPLICABLE/UNKNOWN.
- `tool_status`: `PASSED`, `FAILED`, `ERROR`, `NOT_RUN`, `UNKNOWN`; `tool_exit_code` là integer hoặc null. Đây là status công cụ, không thay verdict assertion; campaign dừng MAX_TIME không được tự gọi PASS vì hit đủ operation.
- `cleanup_status`: `PASS`, `FAIL`, `BLOCKED`, `NOT_RUN`, `INCOMPLETE`, `NOT_REQUIRED`, `UNKNOWN`. PASS cleanup cần `cleanup_evidence_refs`; NOT_REQUIRED cần lý do có nguồn trong cleanup_ref/decision. Cleanup FAIL không làm mất business/contract FAIL, cũng không tự tạo product defect.
- `infrastructure_status`: `HEALTHY`, `DEGRADED`, `FAILED`, `UNKNOWN`; không suy healthy từ record tồn tại. Với observation đã thực thi PASS/FAIL/INCOMPLETE phải có started_at và evidence; mất finished_at phải có stop_reason/gap thích hợp. Timestamp null trong ví dụ giả lập không là lịch sử runtime.

`legacy_status` giữ nguyên giá trị gốc (ví dụ OPEN); execution plan chỉ map OPEN sang BLOCKED khi thiếu oracle, kèm notes `legacy OPEN` và gap. Không sửa report nguồn. `assertion_results` lưu requirement IDs, dimension BUSINESS/CONTRACT/AUTHORIZATION/INVARIANT, mandatory, oracle_ref, verdict, evidence, finding_id.

`operation_evidence` giữ actor/policy, `dispatch_verified`, `positive_acceptance`, read-back và request/response refs. Bool null = chưa xác minh, false = quan sát không đạt điều kiện, không đồng nghĩa UNKNOWN. Dispatch true cần request/response; positive true cần dispatch true và quyết định read-back có cần hay không. Nếu cần, read-back phải verified với evidence. Middleware deny trước route chỉ chứng minh luật quyền tương ứng; dispatch false không góp hit/positive. Positive phải có oracle nghiệp vụ, không suy từ HTTP 2xx. P08 kiểm semantic liên quan assertion và source, schema chỉ khóa cấu trúc/điều kiện cục bộ.

## Summary và quy tắc kiểm semantic đã khóa

Mỗi summary chỉ có một `unit`/selection và giữ filters, tiers, transports; metric không gộp các mẫu số khác nhau. `denominator_state: UNLOCKED` bắt buộc count null, denominator_revision null và mọi metric NOT_MEASURED. LOCKED chỉ khóa mẫu số của selection có quyết định, không chốt acceptance; unresolved UNKNOWN ảnh hưởng mẫu số thì metric liên quan vẫn NOT_MEASURED. Có thể đo subset đã khóa với filters và selection riêng, không đặt tên toàn hệ thống.

Metric gồm status, unit, `numerator_ids`, `denominator_ids`, `missing_ids`, count, percentage, gap và evidence. Khi MEASURED: count phải bằng cardinality tập ID; numerator là tập con denominator, missing là denominator trừ numerator; denominator > 0, percentage = numerator/denominator × 100. Denominator bằng 0 không sinh tỷ lệ 0 hoặc 100; giữ NOT_MEASURED + lý do. Top `numerator_ids`/`missing_ids` là union để tra cứu các metric cùng unit, không phải metric/tỷ lệ cộng gộp. `missing_reasons` nêu lý do theo target ID/gap. `excluded_ids` chỉ N/A được quyết định có nguồn, giữ `exclusion_decision_ids`; không dùng để loại FAIL/route khó kiểm.

Những ràng buộc sau **là phần bắt buộc của hợp đồng**, JSON Schema từng record không tự kiểm được; P08 triển khai validator/calculator, P01 chưa viết công cụ đó:

1. Unique PK/canonical operation key; mọi foreign key cùng baseline/revision tồn tại; alias một nghĩa, không cycle; prerequisite/derived_from/retry hợp lệ.
2. N/A cần decision CONFIRMED (approved_by/date/source có thật); PROPOSED không là phê duyệt. Null/UNKNOWN có gap đúng target/pointer; gap RESOLVED có bằng chứng, DEFERRED có quyết định.
3. RTM/catalog projection khớp; DIRECT có oracle/source đủ. Scale I/L/C và priority khớp nguồn; không chấm lại metadata legacy.
4. Normalize operation_key khớp method/path/transport/variant/profile; không query/item ID; giải quyết source-only/OAS-only hoặc giữ gap. Quy tắc tên parameter phải được khóa cùng inventory revision.
5. Assertion bắt buộc đủ, được đánh giá đúng dimension; PASS không được che mandatory FAIL/BLOCKED/NOT_RUN/INCOMPLETE, cleanup và applicability có nguồn. Evidence phải đúng actor/baseline/schema/config/fixture; DESIGN không là evidence runtime.
6. Selection phải có decision/phạm vi khóa, policy chọn run trước campaign. PREDECLARED_EXECUTIONS chỉ chọn execution_ids đã liệt kê; LATEST_ATTEMPT_IN_PREDECLARED_RUNS chọn attempt cuối theo (timestamp, attempt, execution_id) trong run_ids đã khai báo, không chọn PASS cuối tùy ý. Giữ attempt cũ và gắn flaky nếu mâu thuẫn; retry không tăng số TC. Thiếu/không phân giải được thời gian thì giữ gap/NOT_MEASURED, không đoán thứ tự.
7. D/E/V theo mục 6.2: E cần DIRECT có oracle được đánh giá (FAIL vẫn vào E; chỉ BLOCKED không vào E); V cần mọi TC mandatory được chọn đều PASS, không unresolved mandatory. D không lấy từ số alias/request. Mẫu số R chỉ gồm requirement áp dụng đã review, không phải số endpoint.
8. O là hợp REST source/OAS áp dụng đã xử lý sai khác; hit cần dispatch; positive cần nghiệp vụ/read-back. Matrix negative/auth, module mapped/touched/qualified và module có FAIL báo riêng. Không đồng nhất qualified với acceptance.
9. Count/tập/percentage và revisions của summary/metric khớp selection; count discovered/applicable/unknown/N/A đối chiếu inventory. Exclusion có quyết định; không đo khi còn unknown ảnh hưởng mẫu số. Giữ ID thiếu/không hit/chưa positive, không chỉ số tổng.
10. Code statement/line/function/branch và schema parameter/keyword/response là unit khác nhau. Khóa schema hash + pointer/location/status/media type trong registry ID tương ứng, actor/raw/guided riêng; chưa có raw data/semantics đúng tool thì NOT_MEASURED. Response keyword violated không là PASS. Generated/request setup/cleanup/failure/defect là đơn vị riêng, không thêm vào catalog/mẫu số TC.

P01 chỉ kiểm cấu trúc offline của schema và bộ ví dụ nhỏ, cùng kiểm tay/đối chiếu graph ví dụ. Không thực hiện coverage calculator, source inventory, canonical mapping thực hoặc acceptance. Xem [P01 handoff](handoffs/P01.md) cho checks đã chạy, kết quả thật và gap.
