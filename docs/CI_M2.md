# Chạy CI M2 trên lab P09 cách ly

Cập nhật16/11/2026: [blocker coverage/ACL và danh sách commit mới](coverage/acceptance/M2-CI-BLOCKERS-20261116/README.md). Static CI hiện chạy toàn offline suite; coverage dùng sidecar input archive có pin hash, không đổi dữ liệu lịch sử. Driver và finalizer remote kiểm trusted source/SHA trước khi chạy helper ACL hoặc đọc credentials. Các checkpoint CI trước còn giữ làm lịch sử.

Private profile cần cả namespace directory và p09.env có ACL riêng cho đúng tài khoản chạy runner/SYSTEM/Administrators. Kiểm tra bằng `pwsh -NoProfile -File scripts/private_profile_acl.ps1 -Mode Check -Namespace r06-k05-p09-20261115-audit01`; không đạt thì driver BLOCKED_PRIVATE_ACL/exit2 trước khi đọc secret hoặc gọi preflight. Operator có thể dùng Mode Harden với BackupPath mới dưới runtime/security để giới hạn đúng hai target và lưu DACL rollback; không sửa nội dung credential/license hoặc ACL lab khác. [Quy trình và giới hạn](coverage/acceptance/M2-CI-BLOCKERS-20261116/README.md).

Ngày kiểm chứng local: 16/11/2026. [Bằng chứng và giới hạn](coverage/acceptance/M2-CI-20261116/README.md). Chưa chạy GitHub Actions remote; các lệnh dưới là hướng dẫn tái lập, không phải log remote.

Workflow hiện có: [.github/workflows/p10-integration-preflight.yml](../.github/workflows/p10-integration-preflight.yml). Chỉ nhận `workflow_dispatch` trên `main` của `minnhi09/Directus-Testing`, dùng runner `self-hosted`, `Windows`, `X64`, `damh-p09`. Static/offline vẫn độc lập trong [workflow P02](../.github/workflows/static-offline.yml); không đợi license/Extended.

## Điều kiện trước lần chạy remote

1. Người quản trị đưa bộ harness/workflow đã review cùng các dependency P00–P15 cần dùng lên `main`. Hiện nhiều file là untracked; chỉ đẩy workflow hoặc một script sẽ thiếu dependency. Review scripts/data, helper, profiles/p09/compose.json, manifest selection và các schema/baseline/report/fixture offline mà checks tham chiếu. Không đưa config/lab.env, runtime, p09.env, credential, cache hoặc toàn workspace lên Git. Trong nhiệm vụ này chưa commit/push/merge.
2. Đăng ký/bật runner riêng cho code tin cậy, đủ bốn label trên. Tài khoản chạy runner phải đọc được private profile, chạy Python/Git Bash/pwsh/Git/Docker Linux engine và truy cập lab loopback. Không dùng workspace làm việc đang dirty để đăng ký runner. Code dưới scripts/profiles/.github, lab.sh, tests, baseline/schema coverage và snapshot P15-HTTP tham chiếu phải đã commit, không có file untracked ngoài bytecode; HEAD phải bằng GITHUB_SHA. Driver sẽ chặn trước regression nếu không đạt.
3. Runner có phiên bản ít nhất **2.327.1** để dùng Node24 của actions hiện có; kiểm tra trạng thái online và version thật. Xem [checkout v6](https://github.com/actions/checkout/blob/v6/README.md) và [upload-artifact v6](https://github.com/actions/upload-artifact/blob/v6/README.md). Workflow không chạy authenticated Git bên trong Docker container action.
4. Provision lab P09 và private profile bằng quy trình P09 đã review: `runtime/profiles/r06-k05-p09-20261115-audit01/p09.env`, fixture map tương ứng, jq1.8.2 đúng hash và Git Bash tại đường dẫn adapter yêu cầu. Lab phải thuộc đúng namespace này, image pin/volume/network riêng, API chỉ `http://127.0.0.1:18055`, không publish DB. Pipeline này **không start/seed/reset/pull**. Nếu là máy khác, phải chuẩn bị lab riêng và license hợp lệ cho máy/project đó; license active trên máy hiện tại không chứng minh entitlement ở runner khác.
5. Private profile phải ignored và untracked, chỉ tài khoản runner/người quản trị cần thiết được đọc. Cần credential của admin/editor/reader, DB/key/secret và license phù hợp profile; không sao chép giá trị vào Actions log hoặc report. Workflow dùng profile riêng đã provision trên runner, không đọc GitHub `secrets.*` để tạo lab. GitHub token mặc định chỉ `contents:read`; checkout không persist credential. Chưa có quyền/công cụ kiểm chứng registry runner hoặc GitHub secrets từ phiên này; không suy chúng đã cấu hình.
6. Không chạy thao tác ghi local hoặc workflow khác trên cùng lab. Concurrency group `p10-isolated-lab`, không cancel lượt đang chạy, tuần tự hai suite trong cùng regression. Group Actions không khóa các process bên ngoài; người vận hành phải dành riêng lab trong thời gian chạy. Kiểm tra firewall cho upload artifact trên runner theo [hướng dẫn action](https://github.com/actions/upload-artifact/blob/v6/README.md).

## Lệnh local tương ứng

Chạy từ root DAMH; mỗi lần dùng key mới. Không cài thêm dependency hoặc đổi image để bỏ qua lỗi.

```powershell
python -B scripts/check_offline.py --output-dir artifacts/runs/m2-static-<key>
python -B -m unittest discover -s tests -p test_ci_m2.py -v
python -B scripts/ci_m2.py --key <key> --preflight-only
```

Lượt thực thi regression có ghi/xóa **chỉ dữ liệu do suite tạo**, phải qua preflight/license/actor/fixture trước. Thực thi hai lệnh cuối bằng try/finally khi thao tác thủ công; GitHub workflow đã khai báo bước finalizer và upload `always()`:

```powershell
try {
  python -B scripts/ci_m2.py --key <run-key>
  $testCode = $LASTEXITCODE
} finally {
  python -B scripts/ci_m2.py --key <run-key> --finalize
  $cleanupCode = $LASTEXITCODE
}
# Đọc cả $testCode và $cleanupCode; không đổi exit 1 thành PASS.
```

Driver khai báo 13 canonical theo manifest trước run, gọi P10 với `--http-trace` để capture OAS bốn actor và S1–S6 ngay trong cùng regression, không gọi thêm một lượt capture scenario. TC13 được giữ nguyên oracle và contract FAIL. Sau regression hoàn tất/cleanup đạt, diagnostic chạy trên response đã capture, trong Schemathesis4.30.0 đúng digest với `--network none`. Contract diagnostic process exit0 chỉ chứng minh tool xử lý xong; phải đọc verdict từng check.

Lượt local đã có regression/trace nhưng reporter bị lỗi có thể tiếp tục bằng `--key <new-key> --replay-key <old-key>`. Đây là continuation evidence local, không chạy lại regression, không được dùng để tuyên bố CI remote đã chạy. Source summary/hash và exit của regression gốc được giữ riêng; không ghi đè lượt cũ. `--remote` không cho phép chế độ này.

## Kết quả và artifact

| Điều kiện | Exit driver | Ý nghĩa |
|---|---|---|
| Có TC13/contract diagnostic FAIL, evidence đầy đủ, cleanup PASS | 1 | SUT/contract findings được giữ; job đỏ, không phải harness PASS giả |
| Harness/tool/export/evidence lỗi, preflight không đạt, cleanup chưa xác minh | 2 | BLOCKED/infrastructure hoặc harness; không gọi là lỗi sản phẩm |
| Tất cả assertion/diagnostic đạt, cleanup PASS | 0 | Chỉ subset của run; không suy coverage toàn Directus |

Known issue chỉ nhận diện TC13 khi business PASS và contract FAIL. Business failure mới không được gán vào known TC13. Diagnostic có schema/status failure riêng, không gộp số check FAIL thành số defect. Giữ report hai chiều; không `continue-on-error`, skip test hoặc đổi expected để xanh.

Upload duy nhất `artifacts/runs/m2-ci/<key>/public/`, gồm summary/provenance, preflight, report/selection 13 canonical, raw OAS theo actor, trace17response có metadata/hash, raw response tham chiếu của designed cases, diagnostic, baseline/verification và cleanup/finalizer, cùng index SHA256. Retention14ngày, thiếu file làm upload lỗi. Không upload runtime/private profile hoặc cache; child stdout/stderr không công bố vì có nguy cơ chứa credential. Log an toàn của driver ghi trạng thái/exit riêng, chi tiết assertion nằm trong report.

Toàn staging được quét giá trị credential thực trong bộ nhớ và mẫu bearer/token/cookie trước khi copy. Gặp bí mật thì chặn toàn publication; không sửa/redact raw schema để che lỗi. Lưu báo lỗi an toàn và exit2. Scan là một lớp bảo vệ, vẫn phải review artifact trước chia sẻ. Lượt local cuối kiểm hash index, không có credential match.

Finalizer là kiểm tra chỉ đọc, không reset/broad restore và không tác động lab cũ. Nếu runner bị kill/mất điện hoặc thiếu report cleanup thì ghi UNVERIFIED, chặn reuse lab qua preflight tiếp theo và cần người vận hành xử lý đúng ID do run tạo. `always()` là best effort khi nền tảng còn chạy, không bảo đảm cleanup/upload khi host chết. Xem [GitHub expressions](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions).

## Việc người dùng cần thực hiện để có evidence remote

Sau khi review/provision các điều kiện trên, đưa bộ file cần thiết lên `main` theo quy trình Git của nhóm. Vào **Actions → P10 isolated regression smoke → Run workflow → main**. Chưa thực hiện bước này trong phiên. Lưu URL/run ID, attempt, commit SHA/ref, runner, log và artifact `m2-ci-<run-id>-<attempt>`; xác nhận finalizer/upload thực sự chạy dù driver exit1.

Đừng chỉ nhìn badge xanh/đỏ: expected hiện tại là TC13 FAIL và contract diagnostic FAIL được báo công khai; harness/cleanup/upload phải có evidence riêng. M2 công việc còn BLOCKED bởi CI remote/trusted revision/runner và tổng hợp nghiệm thu có căn cứ; không có yêu cầu sửa Directus hoặc tất cả test phải PASS. Fuzzing còn `INCOMPLETE_BUDGET`/keyword `NOT_MEASURED` được giữ từ P14; nhiệm vụ CI này không chạy campaign hoặc tự đổi tiêu chí nghiệm thu.
