# Coverage portable và private profile CI — 16/11/2026

Nhiệm vụ kỹ thuật coverage/ACL đã xử lý; **CI remote và nghiệm thu M2 chưa thực hiện**. [Checks](checks.json), [audit](audit-evidence.json), [commit allowlist mới](commit-files.txt), [manifest/hash](commit-manifest.json). Không sửa Directus, expected/oracle hoặc kết quả TC13; không commit/push/PR/merge/chuyển phase.

Kết quả bản cuối: **136/136 unit offline,0failure/error/skip; static8/8** ở cả workspace và Git index checkout. Trên checkout không có runtime/Directus sibling, P08 validate/calculate exit0 và output bằng workspace, R/D/E13,V12/13. [Static sạch](clean-static-summary.json), [coverage sạch](clean-coverage-summary.json). Đây là kiểm harness/dữ liệu offline; TC13 và diagnostic của SUT giữ FAIL như lịch sử.

## Nguyên nhân và sửa liên kết bằng chứng

Lỗi1/118 trước đó là lỗi provenance của harness, không phải TC13: bundle lịch sử dùng `manifest/baseline.yaml` đang thay đổi trên main và raw admin OAS trong ignored runtime; source refs Directus cũng dựa vào object chỉ có trên máy tác giả. [Review trước sửa](../M2-CI-REMOTE-REVIEW-20261116/README.md) giữ nguyên kết quả117PASS/1ERROR.

[Immutable input archive](../../sources/immutable-inputs-v1/README.md) chứa115snapshot nguyên byte (960910byte):113file Directus đọc đúng pin4f77933bf9551cac6b289576078783e189b8f4e3, manifest lịch sử hash3cd66f… và admin OAS lịch sử hash993a95…. Không sao chép toàn monorepo hoặc credential. Mỗi snapshot đã khớp hash trong source_ref có trước và được scan trước khi lưu.

Chỉ thêm `input-archive.json` bên cạnh hai bundle M2-COVERAGE/P15-HTTP. Record/schema/selection/RTM/expected/report/raw gốc không bị viết lại. Sidecar pin hash index; resolver chọn đúng kind/path/revision/sha256, sau đó vẫn kiểm size/hash/pointer/line-range và baseline. Không có sidecar thì giữ cơ chế cũ; không có fallback ngầm để bỏ lỗi. Snapshot/index bị sửa, path escape, wrong revision, duplicate identity, private-env ref hoặc missing evidence đều failure. Các ref mới ngoài archive vẫn cần nguồn thật tương ứng.

P08 [validate](coverage-validation.json)/[calculate](coverage-summary.json) chạy lại exit0, resolve115identity; R/D/E13,V12/13 giữ nguyên. TC13 vẫn FAIL, contract NOT_RUN của12case không bị gán PASS, diagnostic FAIL giữ nguyên; hit/positive5/5 vẫn là generic selected templates, keyword/code/schema coverage chưa đo vẫn NOT_MEASURED. Không đẩy manifest main mới lùi về lịch sử để làm hash khớp.

## Offline CI và tái lập sạch

`scripts/offline_suite.py` chạy toàn `test_*.py` và chặn socket/DNS/bind, shell, đọc env thật; chỉ cho PowerShell7 chạy đúng coverage_schema.ps1 với payload JSON local. Đã nối vào nhóm unit_harness của static P02, giữ8nhóm check. Bộ test kiểm lại lỗi gốc và thêm kiểm âm archive/tamper/pointer/private-path, ACL và thứ tự source trust trước credential. Không skip/xfail/continue-on-error hoặc đổi expected.

Bản thử guard đầu tiên nhận sai dạng commandline Windows, làm4schema-test ERROR; giữ ở workspace-suite-attempt01.txt. Đã sửa parsing argv/serialized commandline và thêm kiểm âm/kiểm tương thích. Các file workspace-suite*.json là checkpoint trung gian; checks.json và static summary cuối là kết quả bản cuối. Toàn log unit là fixture offline, không phải execution mới của Directus.

Kiểm sạch: clone GitHub main vào ignored thư mục riêng với core.autocrlf=false, xác minh CLEAN trước overlay. Áp đúng candidate/policy byte, stage **chỉ trong clone thử**, rồi `git checkout-index` vào thư mục trống; không tạo commit. Checkout từ index không có runtime/profile hoặc sibling Directus. Chạy toàn offline suite/static và P08 trên checkout đó, kiểm archive hash và main manifest/Swagger/mode executable được giữ. [Bằng chứng checkout](clean-reproduction.json). Candidate chưa commit nên không gọi đây là clean committed candidate hoặc GitHub Actions run; không sửa index/branch checkout làm việc của người dùng.

Git attributes nhận CR-at-EOL của evidence mà không chuyển byte. Full git diff --check còn có whitespace/blank-EOF vốn nằm trong input/source excerpt lịch sử; không trim các file có hash/pointer để xanh. Kiểm whitespace implementation riêng trên scripts/tests/.github/profiles và kiểm integrity của input độc lập; số cảnh báo raw và exit thật nằm trong clean-reproduction.json. Đây là kiểm định dạng Git, không phải skip test/contract check.

Manifest ghi cả workspace_sha256 và hash publication cho implementation cần CRLF→LF theo Git attributes. Chỉ áp dụng lên source/tests/workflow/profile, không áp lên docs/evidence/scripts-data/test-fixtures. Oracle/data và snapshot không đổi; hash publication phải khớp byte đi qua checkout-index.

## ACL/license

Đã kiểm metadata ownership của lab P09 trước khi sửa ACL. [Trước](acl-before.json): namespace directory và p09.env mỗi target có6Allow ngoài current account/SYSTEM/Administrators, inheritance bật. `private_profile_acl.ps1 -Mode Harden` chỉ đổi DACL thư mục P09, p09.env và file backup mới do tác vụ tạo; không đọc byte credential, không sửa nội dung key/license, không reset DB/volume/lab cũ. [Sau](acl-after.json):0broad Allow, inheritance tắt, current identity mở file được. [CI permission gate](ci-profile-gate.json). ACL backup chứa DACL, nằm ignored trong runtime/security và không đưa vào payload/artifact công khai.

Đã thử Harden→Check→Restore trên namespace/file **synthetic** do tác vụ tạo, đối chiếu nội dung không đổi rồi xóa đúng file/thư mục fixture: [evidence](acl-restore-fixture.json). Restore về ACL cũ rộng trả exit2 vì check bảo mật phải báo BLOCKED, không phải khôi phục thất bại.

CI driver/finalizer remote kiểm repo/ref/SHA và source clean trước khi chạy ACL helper; tiếp đến profile ignored/untracked và quyền riêng trước khi đọc credentials. Profile tracked/broad hoặc source dirty chặn exit2, chưa gọi SUT. Finalizer workflow đã thêm --remote để kiểm cùng trust boundary. Script ACL không chạy tự động Harden trong CI.

License không thay giá trị hoặc project binding; chỉ kiểm key cấu hình đúng profile P09 và khớp container bằng boolean trong bộ nhớ. Activation/entitlement mới trên runner sẽ do preflight thực xác minh, không suy active local bằng remote-ready. Không cần thêm PAT/GitHub secrets cho workflow hiện dùng profile riêng; không in key/token hoặc hash secret. Runner đăng ký/identity/permissions/settings và remote upload vẫn chưa được xác minh.

### Kiểm profile trên đúng tài khoản runner

```powershell
pwsh -NoProfile -File scripts/private_profile_acl.ps1 -Mode Check -Namespace r06-k05-p09-20261115-audit01
```

Nếu cần provision quyền trên runner mới, chạy bằng tài khoản tương ứng hoặc cung cấp RunnerSid đã xác minh, dùng BackupPath **chưa tồn tại** dưới runtime/security:

```powershell
pwsh -NoProfile -File scripts/private_profile_acl.ps1 -Mode Harden -Namespace r06-k05-p09-20261115-audit01 -BackupPath <absolute-repo-path>\runtime\security\p09-acl-before-new-runner.json
```

Rollback DACL khi cần (không tự chạy trên lab hiện tại): Mode Restore cùng Namespace/BackupPath. Backup thực của lần harden local là `runtime/security/p09-ci-20261116-before.json`. ACL gate vẫn phải kiểm lại, vì restore có thể đưa quyền rộng trở lại. Không thay ACL của config/lab.env hoặc thư mục lab cũ. Phạm vi kiểm là file/namespace, không phải chứng nhận an toàn toàn máy/runner.

## Publication và next action

Danh sách file mới thay thế allowlist review trước: commit-files.txt/commit-manifest.json. Payload chỉ theo delta so với main clone đã kiểm; gồm source/sidecar/snapshot/tests mới và toàn bộ dependency/evidence đã chọn, không có runtime/env/cache. Giữ .gitattributes đề xuất để docs/evidence nguyên byte và source LF, giữ .gitignore main với đúng hai ngoại lệ P14 NDJSON sanitize. Không renormalize/xóa sản phẩm cũ. Clone test xác minh **266blob** của main;367 là tổng tree entries trong review trước, không phải số blob/file — bản này hiệu chỉnh cách gọi số đó, không sửa evidence cũ.

Người dùng tiếp theo: clone main mới sang repo làm PR, tạo nhánh ci/m2-remote, so base SHA với manifest, copy đúng payload cập nhật, review/stage theo allowlist và tạo PR khi sẵn sàng. [Quy trình GitHub](../M2-CI-REMOTE-REVIEW-20261116/README.md) vẫn áp dụng thứ tự PR static→merge→manual main; dùng manifest/payload mới ở `runtime/ci-blockers-20261116/payload`, không dùng payload cũ. Sau merge, provision runner Windows/X64/damh-p09, đúng private profile/license và ACL của account runner; dispatch P10 isolated regression smoke trên main và lưu URL/SHA/runner/log/artifact, kiểm finalizer/upload thật dù exit1.

Các biến và allowlist mới cho vòng copy của hướng dẫn PR:

```powershell
$ciReviewRoot = 'D:\DAMH-full-recovery-2026-10-12\DAMH\runtime\ci-blockers-20261116'
$ciFileList = 'D:\DAMH-full-recovery-2026-10-12\DAMH\docs\coverage\acceptance\M2-CI-BLOCKERS-20261116\commit-files.txt'
# Thay đúng hai biến cũ trước khi dùng vòng copy; không copy toàn checkout DAMH.
```

Sau copy/stage, kiểm `git diff --cached --check -- scripts tests .github profiles` và full diff của raw có hash; giữ các raw whitespace đã ghi nhận. Chạy `python -B scripts/check_offline.py --output-dir artifacts/runs/pre-pr-new` để kiểm toàn suite, không chỉ test_ci_m2. Payload có metadata/code chưa commit nên cần review và commit trên nhánh mới; phiên này không làm bước đó.

DoD kỹ thuật của nhiệm vụ: lỗi coverage liên kết được khắc phục không đổi oracle; hash/negative tests đầy đủ, toàn suite chạy offline, tái lập sạch không đòi private input/source checkout, ACL local và gate trước secrets đạt; allowlist/evidence cập nhật. M2 còn chờ CI remote, preflight/license dưới actual runner và review evidence/defect/limits; không yêu cầu sửa Directus hoặc zeroFAIL. Child P10 hardcode remote_ci=NOT_RUN còn là limitation metadata; dùng aggregate ci-summary có GitHub context và kiểm run thật, không chỉnh report lịch sử. P14 FAIL/INCOMPLETE_BUDGET và các metric chưa đo giữ nguyên. Owner bước vận hành đề xuất Lành, chưa ghi người khác đã xác nhận/review.
