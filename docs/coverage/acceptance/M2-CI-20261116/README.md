# M2 — tích hợp CI và kiểm chứng local, 16/11/2026

**Tích hợp/local checks COMPLETE; CI remote NOT_RUN; nghiệm thu M2 còn BLOCKED.** Không commit/push/dispatch. [Quy trình chạy remote và yêu cầu runner/private profile](../../../CI_M2.md). TC13 giữ FAIL; không sửa Directus/expected/oracle hoặc tiêu chí coverage.

## Input và baseline

Đọc AGENTS.md, kế hoạch §10–11/§12.5.4/P15, handoff P15 mới nhất và các dependency P02/P09/P10 đã đối chiếu trong lượt tiếp nối. Dùng manifest M1-REGRESSION-13-v1, P10 helpers/course7 và trace/diagnostic P15 đã có; không chọn module/canonical mới.

DAMH `D:\DAMH-full-recovery-2026-10-12\DAMH`, branch `feat/g1-shared-interface`, HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, worktree DIRTY từ trước, nhiều sản phẩm phase untracked. Source pin Directus `4f77933bf9551cac6b289576078783e189b8f4e3`; checkout bên cạnh vẫn `8e140f94250834cea0a0fb6eb822cac39ed9faec`, không sửa/checkout. Image Directus12.5.0 và Schemathesis4.30.0 giữ digest trong profiles/p09/compose.json; preflight/run có metadata thực.

## Thay đổi và bằng chứng thật

- Workflow P10 hiện có gọi `scripts/ci_m2.py`, opt-in trace ngay trong một regression, nối contract diagnostic sau exit1 đã xác minh, finalizer và upload `always()`. Chỉ manual/main/repo tin cậy, quyền read, cùng concurrency group, không `continue-on-error`.
- P09 adapter cho opt-in trace khi export-schema; P10 có `--http-trace`. Interface cũ và assertion không đổi. Shim Windows jq thêm ngoại lệ `/server/` để bảo toàn API path, bên cạnh `/items/` có sẵn.
- Driver phân biệt TC13 known FAIL, assertion mới và lỗi harness/infra/evidence/cleanup; scan trước publication, đóng gói report cả lượt regression chưa hoàn tất, không upload credential/runtime/cache. 15 unit tests mới chạy offline, đã nối vào static P02.
- [Runtime readiness](runtime-readiness.json): local đúng namespace P09, version12.5.0, 24/24 checks, license active/source env, custom_permission_rules_enabled=true; private profile ignored/untracked, chỉ ghi boolean key presence, không ghi value/hash secret. Actor/policy/fixture và resource ownership được xác minh bằng preflight.
- [Remote readiness](remote-readiness.json): GitHub API đọc thật trả total_count0 workflow run; `.github/workflows` trên main trả404 ở thời điểm kiểm. Local không thấy service/process runner chuẩn. Registry/labels/version runner và GitHub secrets trên remote **CHƯA XÁC MINH**, API connector không hỗ trợ admin endpoints. Không suy “không có runner” trên toàn repository chỉ từ quan sát máy local.

Hai lượt regression local thực sự chạy, mỗi lượt đúng13 canonical, không campaign, chỉ ghi/xóa dữ liệu do suite tạo:

| Lượt | Regression | Harness/diagnostic | Cleanup |
|---|---|---|---|
| [ci01](local-20261116-ci01-summary.json) | 12PASS/1FAIL, TC13 giữ FAIL | BLOCKED: Git Bash đổi path schema thành đường dẫn Windows | PASS |
| [ci02](local-20261116-ci02-summary.json) | 12PASS/1FAIL, TC13 giữ FAIL | BLOCKED: reporter tách collection nhưng chưa bỏ query string của VERIFY | PASS |
| [ci04 continuation](local-evidence-final/ci-summary.json) | tái dùng run ci02, không chạy lại regression | đã sửa hai lỗi harness; offline diagnostic FAIL, aggregate exit1 | PASS; finalizer exit0 |

Continuation ci03 cũng được giữ tại [local-evidence](local-evidence/ci-summary.json); ci04 kiểm lại bản tích hợp sau sửa collect report/finalizer. Hai continuation chỉ có preflight/finalizer chỉ đọc và container diagnostic networknone, không chạy lại S1–S6/designed/API campaign. Không ghi đè summary/report của hai lượt lỗi.

[Diagnostic thật](local-evidence-final/contract-diagnostics.json): 17response, 68check =56PASS/12FAIL (7JsonSchemaError,5UndefinedStatusCode), cả6scenario có diagnosticFAIL. Process diagnostic exit0 không có nghĩa contractPASS. [Report13case](local-evidence-final/regression/run-report.json) và [designed7case](local-evidence-final/regression/designed-report.json) lưu TC13 businessPASS/contractFAIL; nguyên nhân sản phẩm/schema đã triage trước giữ nguyên. Không cộng check/request/retry thành testcase/defect mới.

Artifact cuối khoảng0.86MB, [index](local-evidence-final/artifact-index.json) có hash/bytes từng file: OAS4actor nguyên byte/metadata,17response HTTP, các response được designed report tham chiếu, before/after fixture, report/selection/checks và [finalizer](local-evidence-final/workflow-finalizer.json). Exact credential/bearer/token scan và hash audit trong [audit](audit-evidence.json). Không chép private profile hoặc child stdout/stderr chứa dữ liệu chưa sanitize.

## Checks, coverage và giới hạn

[Checks thực chạy](checks.json): 17unit CI,29runtime/metadata/trace guards,39coverage tests PASS; static8/8group PASS, gồm cả CI unit tests sau tích hợp. [Static cuối](static-offline-final-summary.json). Lệnh tái lập và exit semantics trong CI_M2.md.

P08 validate/calculate lại trên bundle P15-HTTP hiện có: [validation](coverage-validation.json), [coverage](coverage-summary.json). Giữ R/D/E13,V12/13; TC13 không vào V; hit/positive5/5 generic selected templates cho qa_articles, không phải10concrete pairs/toànDirectus. Không đổi execution selection để thay lịch sử bằng lượt CI local, không suy diagnosticFAIL thành PASS, không thay mandatory scope. Code/keyword coverage NOT_MEASURED; anonymous OAS không có protected qa_* vẫn là limitation, không fallback actor.

Không chạy fuzz/campaign, không sửa raw OAS/expected/Directus, không start/reset/xóa lab hoặc volume, không đổi license, không tác động lab cũ. P14 FAIL/INCOMPLETE_BUDGET và giới hạn metrics còn nguyên; chưa chạy mới trong nhiệm vụ này. Không test trên runner khác, không có remote log/artifact upload evidence. `always()` không bảo đảm thực thi khi host mất điện; finalizer thiếu evidence phải UNVERIFIED, không tự restore rộng.

## DoD, gap và next action

DoD của **nhiệm vụ tích hợp CI local** đạt: diagnostic nối được, FAIL không bị che, report/cleanup/scan/index có bằng chứng, lỗi harness tìm thấy được sửa và unit kiểm lại. DoD **CI remote/nghiệm thu M2** chưa đạt; không gọi workflow đã chạy chỉ vì file hợp lệ hoặc local rehearsal có report.

Owner đề xuất theo phân công: Lành xử lý trusted remote revision/runner/private provision và thu Actions evidence; Nhân đối chiếu contract findings/fuzz metrics, Trâm giữ oracle/fixture khi tổng hợp nghiệm thu. Đây là next action, không phải xác nhận các thành viên đã làm/review.

Người dùng cần review, đưa bộ harness/dependency cần thiết lên main, provision runner đúng labels/version/license/profile, manual dispatch workflow và cung cấp runURL/artifact. Chi tiết từng bước ở CI_M2.md; phiên này không làm thao tác Git/publish. Sau đó đối chiếu exit1 của TC13/diagnostic, cleanup/finalizer và upload thực tế; hoàn thiện acceptance record dựa trên công việc kiểm thử và giới hạn có nguồn. Không có gate “sửa Directus/all tests PASS”, không waive required evidence, không tự chuyển phase.
