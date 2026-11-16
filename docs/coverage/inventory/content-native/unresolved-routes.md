# P04 — Route và ranh giới còn mở

Danh sách máy đọc: [unresolved-routes.jsonl](unresolved-routes.jsonl). Gap có nguồn, target và owner đề xuất: [gaps.jsonl](gaps.jsonl). Tất cả OPEN; owner không phải bằng chứng đã nhận việc/duyệt.

| Gap | Phần chưa xác minh / bước tiếp theo |
|---|---|
| GAP-P04-RUNTIME | Source audit does not verify deployed features, DB/schema/license/storage/provider/clock/hooks or any endpoint behavior. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-OAS | Current full/admin/actor OAS provenance not verified; historical snapshot correlation is not current presence. Keep inherited P03 counter/scope discrepancy 14 vs 143 open; no live export. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-SCOPE | Core/Extended/Conditional and capability selection proposed only; applicability remains UNKNOWN and no whole-system denominator locked. Owner đề xuất: Nhân + Lành. |
| GAP-P04-ACTOR | Static guard/service delegation recorded; effective actor/policy/field/row plus singleton/bulk/empty payload semantics unexecuted. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-SEARCH | Fifteen explicit SEARCH declarations cannot serialize with P01 method enum; retain in unresolved list, not GET aliases/N/A; same contract issue as P03. Owner đề xuất: Nhân + Lành. |
| GAP-P04-PATH-SHAPES | Optional filename, trailing slash, UUID pattern and historical parameter alias dispatch normalization must be reviewed before denominator merge. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-STORAGE | TUS_ENABLED, supportsTus driver, storage paths/backends, resumable delegate/datastore/locker/limits and asset policies unknown; no upload/download/render/runtime verification. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-FLOW-REGISTRY | Active flows, method/manual/accountability/selection/cron and dynamic operation registry not deployed/behaviorally verified; no endpoints invented for internal triggers/types. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-EXTERNAL-IO | Imports/email/background jobs/storage require controlled sinks/fixture/profile; controller/service source is not evidence of execution success or cleanup. Owner đề xuất: Nhân; Lành chốt scope/runtime. |
| GAP-P04-CAPABILITY-CONTRACT | P01 has operation inventory schema but no standalone schema for a capability without independent operation. Keep documented P04_CAPABILITY_1 sidecar as part of shard registry, not fabricated operation/TC. Future merge/tooling must consume or explicitly migrate it. Owner đề xuất: Nhân + Lành. |

15 SEARCH tường minh thuộc items, files, folders, flows, operations, activity, revisions, versions, dashboards, panels, presets, shares, comments, notifications và translations. Mỗi khai báo có method/template/source@SHA trong sidecar và ledger, chưa có inventory ID P01. Cùng vấn đề enum đã gặp ở P03; không cộng vào GET, không xóa để làm inventory có vẻ hoàn chỉnh. Đề xuất mở hợp đồng được lưu DEC-P04-SEARCH-CONTRACT, trạng thái PROPOSED; P04 không thay schema P01.

Bốn mục còn lại là NORMALIZATION_REVIEW, DELEGATED_IMPLEMENTATION_BOUNDARY, DYNAMIC_REGISTRY_BOUNDARY và RUNTIME_PROVIDER_PROFILE. Chúng không phải bốn HTTP operation mới hoặc verdict FAIL. TUS/flow/source IO đã có route/ref hoặc capability tại shard; phần dependency/runtime sâu chưa được thực thi.

Chưa có admin/actor OAS hiện tại có provenance đúng baseline. Giữ tất cả oas_state UNKNOWN; sự hiện diện/không hiện diện trong OAS lịch sử không giải quyết gap runtime hoặc quyền. Không export live trong P04.

P04 hoàn tất sản phẩm kiểm kê nguồn được giao; không chốt inventory toàn hệ thống hoặc acceptance. Bước theo thứ tự là P05; xử lý enum/capability contract và OAS/runtime cần task/phạm vi tương ứng trước khi hợp nhất mẫu số.

