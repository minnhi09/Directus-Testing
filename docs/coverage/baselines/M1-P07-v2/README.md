# P07 v2 — Inventory tham khảo và scope regression riêng

Revision v2 giữ toàn bộ 287 inventory record, 62 requirement và 312 canonical ID (315 version record gồm ba parent thiết kế lineage-only). Không xóa sản phẩm v1, không thay report/raw OAS/expected TC13.

[Quyết định nội bộ](../../decisions/G11-M1-regression-20261115.md) khóa riêng regression13; [baseline con](../M1-REGRESSION-13-v1/README.md) là scope nhóm 11. [Đối chiếu văn bản](../../../RA_SOAT_20_PHASE_R06_K05_2026-11-15.md) điều chỉnh nghĩa vụ: inventory toàn hệ thống là tham khảo; không tự buộc triển khai mọi module. Giảng viên chưa duyệt scope cụ thể của nhóm; không cần biến thiếu xác nhận cho từng module thành blocker giả của K05 đã lựa chọn có căn cứ.

## Gap kỹ thuật đã giải

- Kế hoạch trước P06 khôi phục **đúng SHA da96…**, lưu ở sources; bản 72d6… trước cập nhật phạm vi cũng được archive byte-exact. Source refs v2 chỉ đổi path tới artifact đúng hash, không giả rehash nội dung.
- 257 danh sách PC-label không là test prerequisite: giữ nguyên trong source/input_partition và [precondition-labels.json](precondition-labels.json); field test dependency không còn tham chiếu sai loại.
- Ba parent version trước tách TC42/49/55 có record lineage; không là ba ca độc lập mới hoặc kế thừa execution.
- [reference-registry.json](reference-registry.json) có 51 capability/unresolved ID chứng minh được bằng source file/hash. P08 kiểm kind/path/hash/ID thật, không tạo registry placeholder để vượt FK.
- [source-design-bindings.json](source-design-bindings.json) nối 257 request template P3 tới primary source route; legacy13 refine theo behavior hiện hữu. Không gọi đó là dispatch thực hay oracle cho module mới.
- P08 sửa requirement-group LEGACY che các route ITEM được chọn; 26 tests đạt.

[Migration](migration.json), [gap disposition](gap-disposition.json) và [audit](audit-evidence.json) lưu phạm vi sửa; [calculator output](calculator-output.json) toàn inventory tham khảo vẫn NOT_MEASURED/UNKNOWN theo subset draft của snapshot này. Không tính phần trăm toàn Directus.

## Gate còn lại

[Mapping gaps](mapping-gaps.json) giữ 55 record/9 capability chưa có candidate requirement và 38 unresolved/boundary; scope global chưa khóa. Điều này chặn tuyên bố toàn hệ thống hoàn chỉnh, **không tự chặn K05 hai collection** theo văn bản. OPEN/CONDITIONAL chưa chọn không bị sửa thành N/A hoặc mandatory.

Preflight hiện tại, license/actor/fixture/current schemas/CLI identity, execution mới/cleanup/reproducer/root cause là công việc kỹ thuật thực sự còn cần làm khi được giao P09/P10/P14. Không chạy lab ở lượt này.

[Tiến độ hiện hành](../../../../evidence/progress-2026-11-15.md). Các baseline v1 và audit P08 cũ giữ nguyên như snapshot lịch sử.
