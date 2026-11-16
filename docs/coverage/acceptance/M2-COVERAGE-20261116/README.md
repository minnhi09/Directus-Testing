# Hoàn thiện biểu diễn Coverage P01/P08 — 16/11/2026

**Nhiệm vụ coverage COMPLETE.** Bundle mới validate/calculate bằng P08 thật: **R13,D13,E13,V12 (92.3077%)**, chỉ regression13. TC13 vẫn FAIL, không vào V. Không suy coverage toàn hệ thống, không nghiệm thu SUT hoặc tự đóng CI/trace/fuzz gap.

## Nguyên nhân V0 trước đây

P10 ghi12case PASS/1FAIL. P01 execution1.0 lại đòi contract PASS hoặc NOT_APPLICABLE cho mọi execution PASS. P15 giữ contract NOT_RUN nhưng phải encode12case thành INCOMPLETE để qua schema, nên P08 V=0. Đây là điều kiện dimension áp toàn cục trong biểu diễn, vượt ngoài oracle khóa của TC01–TC12; không phải12ca chưa thực thi.

§6.2 vẫn giữ nguyên: requirement vào V khi mọi test bắt buộc mới nhất PASS; FAIL vào E, không vào V. Không đổi oracle/expected, mẫu số, DIRECT edge, test version, selection/run/execution ID hoặc công thức. Không đổi contract NOT_RUN thành PASS/N/A. Đầu ra cũ V0 giữ nguyên, tái kiểm vẫn V0 ở test tương thích.

## Revision hợp đồng và bảo vệ evidence

- Schema cũ docs/coverage/schemas/executions.schema.json **không đổi byte**. Schema execution1.1 mới ở executions.v1.1.schema.json, dùng chung common defs1.0 và chỉ thêm assertion_scope_id; bỏ điều kiện dimension universal trong riêng revision1.1.
- assertion-scopes.schema.json và bundle/assertion-scopes.json biểu diễn các dimension bắt buộc, khóa theo canonical/version/requirement và source refs của catalog/oracle cũ. BUSINESS giữ bắt buộc; CONTRACT test không được bỏ CONTRACT, AUTHORIZATION test không được bỏ AUTHORIZATION. TC13 giữ BUSINESS+CONTRACT, ca anonymous có BUSINESS+AUTHORIZATION từ verdict thật; S4–S6 vẫn được kiểm theo oracle scenario gốc, không gán thêm verdict chưa có.
- P08 dùng schema đúng version, không fallback version lạ; resolve kiểm binding baseline/scope/RTM, nguồn oracle, assertion mandatory và evidence. Một declaration scope không tự làm ca PASS. PASS còn đòi COMPLETE/healthy/tool exit/cleanup và mọi mandatory assertion PASS; business/contract FAIL không thể được giấu bằng scope. TC13 không thể đổi PASS bằng xóa contract assertion hoặc đổi contract NOT_RUN.
- [Bundle mới](bundle/) giữ original case verdict12PASS/1FAIL và toàn bộ dimension gốc. Có thêm AUTHORIZATION assertion từ P3-AUTHZ-DR-047.verdicts.authorization=passed, không tạo oracle/assertion thực thi mới. tool exit từng case vẫn là projection outcome, không giả13CLI process; S1–S6 dùng enclosing run bounds, giữ limitation thời gian. Xem [lineage](lineage.json).

Không sửa/correct raw OAS, report lịch sử, source Directus hoặc expected. Contract diagnostics offline trước đó có FAIL vẫn ở M2-REVIEW-20261116, không bị xóa; đó là chiều kiểm bổ sung trên capture cũ, không tự trở thành mandatory mới của source test. Bundle này không nhập chúng để đổi case verdict lịch sử.

## Kiểm chứng

[Validation](validation.json), [coverage output](coverage-summary.json), [missing IDs](missing-ids.json), [commands](commands.json), [audit](audit-evidence.json). Bộ test39/39 PASS:26test P08 cũ giữ nguyên,13test mới cho revision1.1. Kiểm nhiều-nhiều/alias/retry/FAIL/BLOCKED/partial schema vẫn chạy từ suite cũ. Suite mới kiểm legacy V0 bất biến, actual R/D/E/V=13/13/13/12, không đổi input, TC13 bị loại V, thiếu contract evidence hoặc scope, mất auth dimension, scope/oracle sai, hash sai, cleanup FAIL và version không hỗ trợ đều bị từ chối.

Lần tạo bundle đầu dùng nhãn PASSED/FAILED của report vào field enum PASS/FAIL gây SCHEMA_VALIDATION_FAILED; đã sửa đúng phép ánh xạ tên trạng thái, không sửa schema để chấp nhận nhãn sai hoặc đổi outcome. Diagnostic được ghi trong audit. CLI cuối validate/calculate exit0,synthetic=false. Test count không là số ca API; không gọi API, Docker/lab/campaign hoặc đọc env thật trong nhiệm vụ này.

## Tái lập offline

Tại root DAMH:

```powershell
python -B -m unittest discover -s tests -p 'test_coverage*.py' -v
python -B scripts/coverage_offline.py validate docs/coverage/acceptance/M2-COVERAGE-20261116/bundle
python -B scripts/coverage_offline.py calculate docs/coverage/acceptance/M2-COVERAGE-20261116/bundle
```

Missing verified requirement chỉ **LEGACY-TC13** vì contract FAIL. Operation hit/positive, code/schema keyword còn NOT_MEASURED: không thêm dispatch evidence giả từ title/template/response count. Không có ca selected chưa chạy;13case cùng run P10, không thêm retry hay chọn historical PASS khác.

## Bàn giao

Đã giải sai khác serialization0/13 và review12/13, không thay tiêu chí acceptance để ép đạt. M2 công việc vẫn còn trace/schema đúng actor và CI evidence; defect TC13 được báo cáo có nguồn, không bắt nhóm sửa Directus. Owner đề xuất Nhân coverage, Trâm oracle, Lành tích hợp; không gán review của họ.

Next task đề xuất: hoàn thiện per-step trace của6scenario và OAS anonymous theo baseline phù hợp; ưu tiên artifact cũ trước runtime rerun được giao. Không thực hiện nhiệm vụ đó, không chuyển Phase, commit/push/PR/issue/liên hệ/sub-agent trong batch coverage này.
