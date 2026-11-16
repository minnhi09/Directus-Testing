# Rà soát M2 theo mục tiêu đồ án kiểm thử — 16/11/2026

**Không yêu cầu sửa Directus hoặc tất cả test PASS để hoàn thành công việc QA. TC13 giữ FAIL.** Báo cáo này bổ sung hiệu lực cho cách diễn giải M2; không ghi đè acceptance/coverage/report cũ hoặc giả phê duyệt giảng viên.

## Đối chiếu yêu cầu chính thức

Đọc lại yeu_cau.pdf bằng pypdf: §2.1 phần2 trang2 yêu cầu chọn core/risk module, automation, log/metrics, phát hiện lỗi hoặc chứng minh coverage rồi phân tích nguyên nhân; §3 G/H trang3 yêu cầu kết quả/phân tích/tái lập; §4 trang3 khuyến nghị scope phù hợp; K05 trang8 yêu cầu schema tests, reproducer, thống kê lỗi. Trích đoạn và SHA PDF ở official-excerpts.json. Không có điều kiện zero FAIL hoặc bắt nhóm sửa Directus trong các yêu cầu này. Tên yeu_cau(9).pdf người dùng nhắc trước chưa hiện diện; không giả hai binary cùng tên, dùng bản PDF sẵn repo đã đối chiếu nội dung với chỉ đạo người dùng.

M1/M2/M3, gate CI và Verified Coverage là cách tổ chức/đo của nhóm, không tự thành điều kiện giảng viên đòi mọi test PASS. Chỉ đạo người dùng hiện tại làm rõ mục tiêu QA; không phải waiver đổi TC13 thành PASS. Không xóa fail hoặc đổi oracle/threshold.

## Bốn trục đánh giá

| Trục | Tình trạng có nguồn | Kết luận |
|---|---|---|
| Hoàn thành công việc kiểm thử | P10 đủ13canonical, fixture/cleanup; P14 raw/guided có budget, restore/reproducer; TC13 đã RCA | Các sản phẩm này đã thực hiện, kể cả khi tìm lỗi |
| Chất lượng SUT | P10 case12PASS/1FAIL; TC13 business PASS/contract FAIL; P14 giữ FAIL/max_time | Không tuyên bố Directus đạt mọi yêu cầu hoặc ép xanh |
| Hợp lệ coverage | D/E13/13; V theo §6.2 là12/13; encoding P01/P08 cũ cho0/13 | Có sai khác mô hình serialization cần công khai, không phải bằng chứng0 hành vi đạt |
| CI/fuzzing còn thiếu | CI remote NOT_RUN; pilot1module/1seed hoàn tất budget, chưa exhaustive/3seed/full10operation trong baseline hiện tại | Không gọi workflow file là CI run; không tự bắt pilot chạy hết không gian |

M2 công việc còn **PENDING_EVIDENCE_RECONCILIATION**, chưa đóng toàn mốc vì trace/coverage encoding và CI run còn thiếu. TC13 VERIFIED_OPEN_FAIL là **kết quả nghiên cứu/defect được báo cáo**, không phải yêu cầu sửa sản phẩm để mở gate. Acceptance SUT không được tuyên bố PASS; nghiệm thu giảng viên chưa được suy diễn.

## Xác minh Verified Coverage

§6.2 định nghĩa V từ các test bắt buộc mới nhất của requirement đã chọn, có PASS; FAIL vào E nhưng không vào V. [Review theo RTM/selection](verified-coverage-review.json) giữ R13,13 execution ID của P10, DIRECT/mandatory edges, canonical/version và source case nguyên vẹn.12 requirement có test bắt buộc PASS; LEGACY-TC13 có contract FAIL nên không vào V. **V12/R13=92.3077% chỉ trong regression13**, không phải coverage toàn Directus hoặc tiêu chí buộc đạt100%.

P15 trước đã lấy điều kiện P01 execution PASS phải có contract PASS/N/A áp cho mọi ca, rồi biến12 case PASS thành evidence INCOMPLETE vì dimension contract NOT_RUN. Nhưng oracle đã khóa của TC01–TC12 là nghiệp vụ/quyền/biên, còn TC13 mới trực tiếp kiểm contract. Việc ép thêm contract dimension thành mandatory cho12ca không được chứng minh từ selection/oracle. Đây là sai khác mô hình tổng hợp, không phải12 run chưa thực hiện. Không sửa NOT_RUN thành N/A hoặc PASS, không bổ sung mandatory mới. P01 schema/tool không bị đổi trong lượt này.

Giữ nguyên coverage-summary cũ V0 với nhãn **legacy P01 serialization result**, không dùng số đó làm hiện trạng verified theo §6.2 hoặc lý do sửa SUT. File review mới là phép tính offline theo công thức/source case, không giả là output P08 hiện hành. Reconciliation serialization với scope assertion cần hoàn thiện ở nhiệm vụ tiếp theo trước khi xuất một bundle P01 chính thức mới; chưa thay artifact cũ cho đẹp số.

## Bổ sung contract evidence có thật

Đã chạy recheck_contracts.py trong đúng image Schemathesis4.30.0 đã pin, --pull never/--network none, mounts read-only. Tái dùng scripts/contract_checks.py, status/content-type/body/elapsed và schema editor/reader cùng run P10. Không gọi API, login, start lab hoặc đổi fixture. [Kết quả](contract-recheck.json), [exit/image](contract-recheck-exit.json).

23step response đã capture của6designed case được kiểm,4check/step:8check FAIL được giữ. Đây là thêm chiều contract **chẩn đoán** trên evidence cũ, không thêm6canonical case hoặc thay case/business verdict. TC13 schema mismatch còn FAIL; score0/5 và category CRUD cũng bộc lộ mismatch response shape; negative score400/status DELETE204 có thể không được OAS khai báo. Không đếm8failure thành8defect.

Không thay anonymous bằng Editor/admin: P3-AUTHZ-DR-047 thiếu raw OAS anonymous nên contract NOT_MEASURED. S1–S6 có summary nghiệp vụ nhưng chưa có per-step request/status/actor→response mapping trong public artifact; không suy trace từ thứ tự file HTTP hoặc title. Còn7case thiếu đủ contract diagnostic mapping (6scenario+anonymous), không tự coi chúng thiếu **mandatory business execution**.

## Việc tiếp theo theo dependency

1. Hoàn thiện mapping requirement → mandatory assertion dimension và serialization P01/P08 theo §6.2; kiểm âm TC13 FAIL không vào V, không đổi expected, không tự gán contract PASS/NA. Giữ cả nguồn cũ và revision mới có lineage.
2. Thu per-step trace/schema đúng actor cho7case còn thiếu khi có nhiệm vụ runtime phù hợp; ưu tiên artifact hiện có trước rerun. Không mở campaign mới hoặc gọi lab trong lượt rà soát này.
3. CI nội bộ: cần run remote thật trên context được phép, lưu exit/report/cleanup kể cả FAIL. Không push trong quyền hiện tại, không khai đã có run/runner.
4. Fuzz: giữ pilot P14 FAIL/INCOMPLETE_BUDGET, representative replay và hạn chế exact-byte replay. Full10operation/3seed hoặc module khác chỉ sau selection/budget tương ứng; không tự nâng thành nghĩa vụ mới của PDF.

Không có task sửa mã Directus trong backlog bắt buộc M2 QA. Không commit/push hoặc chuyển Phase. Bằng chứng TC13, raw OAS và report P00–P15 trước được giữ; kiểm cuối/hash ở audit-evidence.json. Owner đề xuất: Nhân coverage/contracts/fuzz, Trâm oracle/trace, Lành CI/tích hợp; không giả review/nhận việc.
