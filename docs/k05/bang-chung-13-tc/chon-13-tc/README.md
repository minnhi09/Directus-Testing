# M1 regression13 — Scope nội bộ nhóm 11 đã khóa

**Chỉ scope thiết kế regression13 LOCKED**, theo [xác nhận trực tiếp ngày 15/11/2026](../../decisions/G11-M1-regression-20261115.md). Không ghi giảng viên đã phê duyệt subset; không coi toàn inventory/M1 chức năng đã PASS.

Giữ toàn bộ inventory 287 record và 62 requirement trong bundle; selection chỉ lấy 13 LEGACY-TC01–TC13 và 13 canonical test/version. Các requirement khác vẫn UNKNOWN, không N/A và không bị loại khỏi inventory. Năm template nguồn dùng binding qa_articles/qa_categories; denominator chính là **13 requirement**, không lấy 5 template làm 10 operation đã thực thi.

[Manifest](baseline-manifest.json), [selection](selection-manifest.json), [scope](scope.json) ghi baseline/revision/decision có nguồn. Policy PREDECLARED_EXECUTIONS, danh sách execution rỗng; trước campaign phải tạo selection version khai báo ID run/execution theo policy, không chọn tùy ý historical PASS.

[Fixture design](fixture-design.json) dẫn fixture-oracle r06-k05-v2 có nguồn; đây là **source design**, không xác nhận lab hiện tại đã seed/healthy hoặc license hợp lệ. Không đổi expected, assertion, ID nguồn hoặc report. TC13 business PASS/contract FAIL lịch sử giữ nguyên.

[Calculator](calculator-output.json) kiểm dữ liệu: R=13, D=13 có oracle/fixture source, design coverage 13/13 **chỉ trong subset**; E/V/hit/positive còn NOT_MEASURED do chưa có execution của baseline này. Không mang historical PASS/FAIL vào execution mới, không gọi thiết kế 100% là SUT 100%.

[Review 20 phase](../../../RA_SOAT_20_PHASE_R06_K05_2026-11-15.md) đề xuất K05 khả thi tận dụng P00–P08. Phạm vi K05/budget mở rộng là đề xuất kỹ thuật; regression13 đã xác nhận, không hỏi lại. P09 sẵn sàng được giao ở subset này nhưng chưa start lab trong lượt review.
