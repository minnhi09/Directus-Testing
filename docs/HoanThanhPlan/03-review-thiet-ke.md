# Phase 3 — Review bộ test và bàn giao automation

**Ngày:** 18/10/2026. **Reviewer:** AI trong phiên làm việc. Không có chữ ký, review chéo hoặc xác nhận chạy mới của thành viên được suy đoán. Phương pháp: đọc đặc tả/source/assertion hiện hữu, đối chiếu catalog và kiểm dữ liệu thiết kế bằng script tĩnh.

## 1. Checklist P3-09

- [x] Giữ mã UR/BR/AC/S/INV; 26 BR có case/oracle; không tạo INV thứ 12 từ positive-operations.
- [x] Có cả positive và negative; missing/null/empty/blank/coercion không bị gộp tùy tiện.
- [x] Score -1/0/1/4/5/6, name 79/80/81, title 119/120/121 đều có POST và PATCH; có read-back/absence.
- [x] Dùng ASCII cho biên độ dài; Unicode/grapheme giữ câu hỏi riêng, không thêm rule minLength/trim.
- [x] Negative field dùng input khác hợp lệ; archived và score=-1 tách riêng, kế thừa probe smoke.
- [x] Permission matrix phân actor/state/projection; category không có trạng thái/field không tồn tại; POST không giả row cũ.
- [x] Row deny và field deny có bài thử riêng; draft+private không được gán thành chứng minh riêng một rule.
- [x] Mutation trái quyền dùng giá trị khác no-op và full business-field snapshot; GET control không thay expected.
- [x] Oracle query lấy fixture spec + map mới, không suy expected từ sorted/filtered target response.
- [x] Conditional/OPEN tách khỏi execution NOT_RUN; không cấp PASS giả hoặc bịa evidence cho case thiết kế.
- [x] Contract và business verdict riêng; giữ raw và known finding; không tắt check để qua gate.
- [x] Chuỗi dùng ID response/map, dependency và cleanup; không reset giữa bước hoặc gọi request cuối là full-chain.
- [x] Pairwise finite model có constraints rõ, full 36 và subset 9, phủ 37/37 cặp; ca rủi ro cao giữ ngoài.
- [x] Có entry/exit/stop/budget/mẫu số trước chạy; không dùng thiết kế phủ đủ làm execution coverage.
- [x] File/link/IDs/counts được kiểm; raw/harness/evidence gốc không bị thay nội dung.

## 2. Các điểm review và cách xử lý

Đây là mục review thiết kế, không phải số product defect.

| ID | Tình huống và tác động | Xử lý trong Phase 3 / phần còn lại |
|---|---|---|
| P3-REV-01 | Bộ ca rất dễ trùng S1/INV-03/INV-04 hoặc S6/INV-11 và làm số test lớn giả | Inventory 20 mục chỉ rõ nhóm trùng; canonical positive 10 dùng lại trong 10 luật Editor. Case P3 là mục tiêu assertion cần map khi tích hợp, không tự là implementation mới |
| P3-REV-02 | Dùng template marker nối thêm vào title/name 120/80 làm sai biên | Chuỗi biên ASCII có độ dài đúng; marker ở metadata hoặc snapshot ID delta, không nối thêm ký tự |
| P3-REV-03 | Buộc empty/blank/coercion là lỗi chỉ vì required | Name/title empty/blank và type conversion giữ OPEN; status empty khác vì enum có căn cứ; không thêm minLength hoặc no-coercion policy |
| P3-REV-04 | Mặc định mọi PATCH phải gửi required title/score từ component dùng chung | Case PATCH omission giữ field; no-op category PATCH{} tách OPEN. Full read-back, không áp create-required cho update |
| P3-REV-05 | Editor control/fixture ID sai khiến denied test PASS giả | PC-PERM xác minh control, ID/state/payload/actor; strict error branch và read-back. CONDITIONAL chưa đủ nhánh thì BLOCKED khi chạy |
| P3-REV-06 | Draft+private 403 bị tính như chứng minh hai quyền | Bảng 69 luật có DENY_COMBINED; vẫn bắt buộc public draft và private published riêng. Private projection chưa đủ semantics giữ OPEN |
| P3-REV-07 | Wildcard/nested có thể bị gọi hợp lệ rồi cho PASS bằng bất kỳ 403 | Ca Reader wildcard/nested conditional, expected allowed data/no private cần nguồn cụ thể; adapter phải chốt nhánh trước business verdict. Nested chỉ category một cấp |
| P3-REV-08 | Title sort/search phụ thuộc DB/collation và oracle GET nền | Fixture oracle nguồn tĩnh + ID map mới; collation/search conditional. Không tự sửa seed/collation để hợp expected hoặc xóa query title khỏi model sau chạy |
| P3-REV-09 | Từ chối vì vượt độ dài/FK có thể thành 5xx do translator chưa xử lý; hard-code 400 mà thiếu nhánh | Đã lưu class 400 đúng pin và giữ tiền đề translator; 5xx vẫn FAIL robustness. Không giả mọi SQLSTATE đều thành 400; raw error/status cần triage |
| P3-REV-10 | Published timestamp trống bị suy là lỗi workflow mới | Không có BR published kéo theo timestamp; UTC/offset conditional, malformed/empty có robustness riêng và business OPEN |
| P3-REV-11 | Chọn 9 case rồi kết luận giảm 75% chi phí hoặc chắc tìm lỗi như 36 | Chỉ kết luận giảm 75% số input trong mô hình; kiểm phủ 37 cặp tĩnh. Runtime/effort và khả năng phát hiện phải đo Phase 6 |
| P3-REV-12 | Chạy suite ghi làm thay fixture đang dùng cho query/policy | PC-MUT target tạm, nhóm read-only yêu cầu PC-Q sau cleanup/restore; không hai suite ghi song song |
| P3-REV-13 | Cleanup thất bại hoặc request tạo row dù HTTP lỗi bị bỏ qua | So delta/state trước dọn, trackID cả lúc unexpected; cleanup là verdict riêng và block mutation sau đó |
| P3-REV-14 | Biến toàn bộ catalog 257 thành cam kết mọi PR phải chạy | Tách 221 ngoài pairwise/36 reference; triển khai theo rủi ro và subset version trước chạy; full mẫu số còn được báo, không giả full coverage |
| P3-REV-15 | Nhầm template/lệnh dự kiến với API/CLI đã tồn tại | Placeholder phải resolve type; không có lệnh chạy P3 ID ở harness. Chỉ chỉ ra entry có thật test invariants/scenarios; adapter/catalog-to-report thuộc Phase 4 |

## 3. Việc cụ thể bàn giao Phase 4

| Gói | Dữ liệu đầu vào | Việc phải triển khai/kiểm chứng | Tiêu chí có bằng chứng |
|---|---|---|---|
| A — Nền tảng/oracle | PC-BASE/Q/MUT/PERM/CLEAN; fixture-oracle.json; VFY-02/TR-02 | Tích hợp vào helper/credential/run hiện có; map/schema/config/source hash riêng; seed spec kiểm độc lập | Setup sai không gửi target mutation; report có provenance, fixture delta và restore |
| B — Negative assertion | O-VALIDATION/LENGTH/FK/DENY/QUERY-INVALID và GAP-07 | Không dùng mọi non-2xx; branch/error classification; full before/after; giữ failure gốc | 5xx/network/setup lỗi không thể PASS; kiểm ca vừa sửa + tích hợp liên quan |
| C — Backbone/rủi ro cao | P3-OP-01…10, 69 luật quyền, P3-ST-01…03; GAP-04/05/06/14 | Tái dùng INV-04/S/INV hiện có; isolate row/field/write; category Reader và anonymous detail/write còn thiếu | Positive acceptance 10; denied không side effect; full chain/ID mapping/cleanup có report |
| D — Validation/round-trip | Field partitions/BVA; Q-01…05; GAP-01/02/03/13 | Tham số hóa cùng helper, không copy probe trùng; resolve conditional; OPEN chỉ observation khi chưa đủ nguồn | Đủ biên đã khóa, null/missing/default và business vs robustness tách riêng |
| E — Query | P3-QUERY*, fixture oracle; Q-07/GAP-08/09 | Expected independent, exact set/order/projection; condition collation; không tự lấy response target làm chuẩn | Sai query/field nền không thể đồng thời làm oracle và target PASS |
| F — Report/replay | Case/readiness/PC/verdict/chain; VFY-03/TR-04 | ID P3 alias với implementation, emit result và raw check riêng; lưu full chain/remap ID; hóa giải helper Windows ngoài repo | Run ID/new execution thật, exit/restore giữ nguyên, repeat suite ngắn và ghi flaky |

Không phân công thành viên trong hồ sơ này. Các gói là thứ tự tích hợp/phụ thuộc kỹ thuật, không tạo issue hoặc gửi thông báo bên ngoài. Full campaign/triage/pairwise thực nghiệm/CI vẫn thuộc các phase tương ứng, không tự thực hiện vì đã có thiết kế.

## 4. Những rủi ro/chủ đề vẫn chưa được kiểm chứng

- 47 ca còn business expected OPEN; 68 ca conditional trong toàn catalog. Các Q giữ nguyên ID; phần đã rõ vẫn có oracle, không cần chờ đóng hết câu hỏi mới triển khai phần độc lập.
- Directus image/source provenance lịch sử, ID map mutable sau pilot và harness dirty state vẫn có giới hạn đã ghi Phase 0–2. Thiết kế mới không sửa lịch sử đó.
- Chưa gửi request mới; 257 là số dòng case thiết kế. Mỗi case có thể nhiều setup/read-back/cleanup và ba chuỗi có nhiều bước.
- Chưa kiểm runner format registry/null handling VFY-01, ngữ nghĩa nested write/JSON scalar/timezone/collation trên runtime, coverage Directus source hoặc mọi đường tấn công quyền.
- POST array có ca hai object hợp lệ; không tuyên bố kiểm atomicity, partial failure của batch, maxItems hay performance. Bulk PATCH/DELETE ngoài phạm vi chính.
- Pairwise chỉ bốn yếu tố query của Editor, không thay authorization/biên/rollback, không bảo đảm lỗi từ ba yếu tố trở lên. Không có số liệu cost mới.
- Có 26/26 BR được thiết kế không đồng nghĩa mỗi lớp đầu vào hoặc trạng thái Directus đều đã được mô hình hóa. Các tính năng admin/UI/GraphQL/WebSocket/DB khác ngoài phạm vi.

## 5. Trạng thái công việc

| Task | Đầu ra thực tế |
|---|---|
| P3-01 | Inventory 20 mục + nhóm trùng và gap; giữ S/INV |
| P3-02 | 48 phân vùng field và nhóm query/policy trong báo cáo; expected rõ/conditional/OPEN |
| P3-03 | 34 điểm biên gắn case, POST/PATCH và no side effect |
| P3-04 | 69 luật quyền hữu hạn,10 reuse +59 biến thể; có nested/projection một cấp |
| P3-05 | Ba chuỗi nghiệp vụ, ID động, full field và cleanup; rejection tích hợp oracle các ca ghi |
| P3-06 | Fixture/oracle source có hash; expected query độc lập với target output |
| P3-07 | 36 reference/9 subset,37 cặp phủ đủ; constraints/lower bound/rủi ro rõ |
| P3-08 | Entry/exit/stop/budget/coverage mẫu số và mức đủ bằng chứng trước chạy |
| P3-09 | Checklist và 15 mục review thực bởi AI; [validation tĩnh](tai-lieu-bo-tro/phase3-20261018/validation.json) |

Hoàn thành thiết kế Phase 3, chưa có automation/test/API execution mới hoặc xác nhận nghiệm thu hệ thống. Khi triển khai, dùng case/BR để chọn kiểm tra phù hợp thay vì chạy campaign dài cho thay đổi chỉ sửa tài liệu.
