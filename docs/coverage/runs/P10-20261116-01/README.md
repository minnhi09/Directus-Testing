# P10 checkpoint — 16/11/2026, Asia/Bangkok

**BLOCKED**, chưa hoàn tất P10. P09 READY ngày15/11 là lịch sử; probe hôm nay không truy cập được Docker Linux engine. Không start Docker Desktop toàn máy hoặc gọi URL8055. Không có request SUT, fixture mutation, seed/export OAS hay cleanup cần thực hiện. Không lấy số13 selection làm13 execution.

Selection con [selection-manifest.json](selection-manifest.json) giữ nguyên baseline/13 canonical-version/13 requirement/mandatory/oracle, chỉ khai báo run ID P10-20261116-01 và13 execution ID dự kiến trước chạy. Không tạo executions.jsonl giả. Baseline gốc M1-REGRESSION-13-v1 bất biến. [Run report](run-report.json) ghi tất cả NOT_RUN; coverage NOT_MEASURED. [Preflight](preflight.json) là probe thực, engine exit1; static compose render exit0.

Đã tạo scripts/p10_selection.py và5 unit checks offline: exact selection, duplicate canonical/alias, mất TC13, trùng execution ID, đổi denominator/retry policy. Selection/unit exit0; không phải test API. Check static lần1 exit1 vì link snapshot bị resolve tại thư mục lưu thay vì docs/ gốc. Sửa scripts/check_offline.py chỉ cho hai snapshot kế hoạch content-addressed, kiểm hash trước khi resolve tại vị trí gốc; không skip link hoặc sửa snapshot. Lần2 static exit0,8/8 nhóm PASS; giữ kết quả lần1.

Workflow .github/workflows/p10-integration-preflight.yml chỉ manual trên self-hosted Windows X64 label damh-p09 do nhóm provision; không có PR/fork trigger hoặc license embedded. Checkout clean=false để không xóa private profile ignored trên runner; probe xác thực fail khi thiếu private credentials/lab. Không upload env/raw HTTP. Job này **chỉ readiness**, chưa chạy regression; remote Actions NOT_RUN, chưa đăng ký/xác minh runner. Workflow static P02 giữ độc lập và không phụ thuộc Extended/license. Không commit/push để kích hoạt CI.

## Batch còn lại

1. Khi Docker Linux engine hoạt động, inventory ownership và chạy p09_runtime.py read-only với output mới; không reset/reseed fixture nếu chưa cần. P09 license/actor/fixture phải kiểm lại trước mọi mutation.
2. Nối adapter thực thi regression vào namespace P09: shell scenarios() tái dùng S1–S6; designed_cases course tái dùng7 canonical còn lại. python_suite và Runner.preflight đang hardcode project r06-k05; không sửa fixture map giả thành project cũ hoặc gọi wrapper mặc định. Cần adapter explicit project/network/actor đã kiểm và kiểm an toàn trước chạy.
3. Export OAS theo actor vào path mới riêng; giữ raw cũ. Xác minh oracle DB ordering của S3 độc lập, không lấy response làm expected. Khai báo selection mới nếu phải đổi run/execution IDs; giữ attempt BLOCKED này.
4. Chạy tuần tự, giữ business/authorization/contract/infra/cleanup riêng, TC13 FAIL nếu còn tái hiện. Snapshot/restore chỉ dữ liệu phase sở hữu; không dùng broad restore xóa dữ liệu ngoài tập sở hữu. Nối smoke regression sau khi adapter được kiểm thực; kiểm cleanup cuối và coverage bằng P08 theo evidence thật.

Chi tiết blocker/known issue ở [register](missing-known-issues.json). Phase tiếp tục **P10**, không P11/P14. Handoff và tiến độ hiện tại trỏ về checkpoint này; không sửa TC01–TC13, report/raw OAS hay sản phẩm P00–P09.
