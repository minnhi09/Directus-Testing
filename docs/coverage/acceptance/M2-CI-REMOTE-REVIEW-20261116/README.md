# Review trước CI remote M2 — 16/11/2026

Review COMPLETE; **chưa nghiệm thu M2**, chưa commit/push/PR/dispatch. Không sửa source Directus, expected, assertion, workflow hoặc cấu hình đang dùng. Các đề xuất Git attributes/ignore chỉ được đặt trong payload riêng để review. [Danh sách commit chính xác](commit-files.txt), [manifest/hash](commit-manifest.json), [findings](findings.json), [checks](checks.json).

## Kết quả cần xử lý

1. **Xuất bản từ main mới, không copy nguyên checkout cũ.** HEAD local `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72` trên `feat/g1-shared-interface`; GitHub main đọc thật là `dfa7113d1eecf47dca15f1fad4945b75bb458d84`, object commit này chưa có local. `origin/main` local cũng đã cũ. Main có Swagger và guard checkout ownership mà lab.sh local chưa có. Payload giữ nguyên main đối với README, lab.sh, invariants.py, traceability, Compose và manifest; chỉ thay ba helper thật sự cần thay. Không đưa hai thay đổi mode100755→100644 của checkout cũ lên PR.
2. **Bảo toàn byte khi Git checkout/stage.** `core.autocrlf=true` tại máy hiện tại; nhiều bằng chứng JSON/JSONL đang CRLF, một số snapshot/hash dùng LF. Main chỉ bảo vệ thư mục tai-lieu-bo-tro. Payload đề xuất .gitattributes giữ byte docs/evidence, LF cho source/script; giữ .gitignore main và thêm đúng hai ngoại lệ P14 events.ndjson đã scan. Không dùng renormalize hoặc sửa raw report để khớp hash. [Probe Git attributes/filter/ignore](attributes-check.json) đã kiểm bằng lệnh read-only trên export.
3. **Coverage chưa portable ở clone mới.** Static8/8 PASS, nhưng toàn118unit offline có117PASS/1ERROR: test_real_scope_13_evaluated_12_verified_tc13_excluded trả ARTIFACT_HASH_MISMATCH. Hai bundle M2-COVERAGE/P15-HTTP tham chiếu manifest lịch sử hash3cd66f… trong khi main mới hashd7065f…; đồng thời runtime/schemas/r06-k05-v2/admin.json hash993a95… không nằm trong Git. Full reference validation còn cần113 nguồn GIT_FILE đúng pin Directus. [Mismatches cụ thể](reference-mismatches.json). Không đổi hash, ghi đè manifest mới hoặc copy toàn runtime để làm test xanh. Cần snapshot input lịch sử đã sanitize và bản dẫn xuất/fixture có ref tới snapshot, giữ bản cũ bất biến; provision source object Directus đúng pin khi kiểm toàn nguồn. Đây là việc kỹ thuật còn thiếu trước nghiệm thu coverage M2; workflow smoke hiện tại không gọi full P08 validation nên không tự phát hiện gap này.
4. **Quyền private profile cần rà soát.** Metadata Docker hiện đúng P09/pin/healthy, private license khớp env container; activation/entitlement chỉ dẫn snapshot preflight có ngày, chưa gọi lại API ở lượt review này. ACL p09.env có6Allow áp dụng lên file ngoài allowlist current owner/SYSTEM/Administrators, inheritance bật. Chưa kết luận effective access của tài khoản runner chưa đăng ký. Trước provision phải giới hạn quyền thực tế cho tài khoản runner, SYSTEM/Administrators cần thiết, kiểm lại NTFS ACL; Git ignore không thay thế quyền truy cập. Chưa đổi ACL/license/lab.
5. **Metadata child report cần phân biệt.** p10_regression.py:83 luôn ghi remote_ci=NOT_RUN và worktree=DIRTY. Khi chạy Actions thật, dùng ci-summary.json chứa GITHUB_RUN_ID/SHA/ref/runner làm provenance CI; không trích riêng child field để kết luận remote chưa/chạy đạt. Cần sửa metadata cho run mới trong nhiệm vụ harness tiếp theo nếu yêu cầu từng child report tự mô tả CI; không sửa lịch sử để đổi nhãn.

Không coi TC13 FAIL là lỗi harness. Regression vẫn phải giữ12PASS/1FAIL và businessPASS/contractFAIL của TC13; diagnostic có FAIL riêng. Exit1 phản ánh assertion/contract finding; exit2 phản ánh harness/infra/evidence/cleanup lỗi. Full offline suite lỗi1 ở trên là provenance input, không phải sản phẩm Directus và không được dùng expected failure để bỏ qua.

## File cần commit

Danh sách từng file, loại ADD/MODIFY và hash nằm trong commit-files.txt/commit-manifest.json. Đây là **delta so với main đã đọc**, không phải `git status` của checkout cũ. Payload bao gồm harness/coverage P00–P15 cần để các check/link/lineage tái lập; phần lớn là artifact đã tạo trước, không phải test mới. Chỉ đẩy workflow mà bỏ dependency sẽ thiếu input.

Năm file MODIFY so với main: `.gitattributes`, `.gitignore` (đề xuất publication); `scripts/designed_cases.py` (chấp nhận namespace P09 có guard); `scripts/lab-components.sh` (trace/adapter P09); `scripts/windows/jq` (bảo toàn /server/ trong metadata). Các ADD được liệt kê đầy đủ: hai workflow, công cụ/tests mới, profile P09 không credential, schema/manifest/bundle/inventory/catalog/evidence cùng tài liệu/handoff/progress và hồ sơ review này. Những file đã giống main không nằm trong danh sách commit.

**Không commit:** private p09.env/config/lab.env, runtime, artifacts/runs local, cache/bytecode, tmp, slides/bản nháp/binary ngoài allowlist, whole Directus source; không force-add thư mục riêng mnhy. Hai raw P14 NDJSON được include bằng ngoại lệ cụ thể, giữ byte và FAIL/INCOMPLETE_BUDGET. Một pattern token trong test_ci_m2.py là literal công khai của negative unit test, đã review theo hash, không phải credential; scan giá trị credential thực0match. Không blanket bỏ scanner đối với report.

## Nhánh riêng và Pull Request

Payload đã chuẩn bị ở `D:\DAMH-full-recovery-2026-10-12\DAMH\runtime\ci-remote-review-20261116\payload`. Nó chỉ có các file trong manifest, không chứa env/cache hoặc toàn repo cũ. Các lệnh sau **dành cho người dùng**, chưa thực hiện:

```powershell
git clone -c core.autocrlf=false --branch main https://github.com/minnhi09/Directus-Testing.git D:\DAMH-M2-CI-PR
Set-Location D:\DAMH-M2-CI-PR
git rev-parse HEAD
# Phải so với base dfa7113d1eecf47dca15f1fad4945b75bb458d84 trong manifest.
# Nếu main đã đổi, đối chiếu lại các file MODIFY trước khi áp dụng payload.
git switch -c ci/m2-remote
```

Copy theo allowlist vào clone mới, giữ nguyên checkout/lab cũ:

```powershell
$ciReviewRoot = 'D:\DAMH-full-recovery-2026-10-12\DAMH\runtime\ci-remote-review-20261116'
$ciFileList = 'D:\DAMH-full-recovery-2026-10-12\DAMH\docs\coverage\acceptance\M2-CI-REMOTE-REVIEW-20261116\commit-files.txt'
$ciNewRepo = (Get-Location).Path
foreach ($ciRelativePath in Get-Content -LiteralPath $ciFileList) {
  $ciDestination = [IO.Path]::GetFullPath((Join-Path $ciNewRepo $ciRelativePath))
  if (-not $ciDestination.StartsWith($ciNewRepo + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside new clone' }
  New-Item -ItemType Directory -Path (Split-Path -Parent $ciDestination) -Force | Out-Null
  Copy-Item -LiteralPath (Join-Path (Join-Path $ciReviewRoot 'payload') $ciRelativePath) -Destination $ciDestination
}
python -B scripts/check_offline.py --output-dir artifacts/runs/pre-pr-review
git add --pathspec-from-file=$ciFileList
git diff --cached --check
git diff --cached --stat
git diff --cached -- .gitattributes .gitignore scripts/designed_cases.py scripts/lab-components.sh scripts/windows/jq
```

Review allowlist/hash và nội dung staged, không `git add .`. Giữ mode của lab.sh/invariants.py như main; hai file không được payload ghi đè. Ghi công khai gap coverage/ACL/child metadata trong PR. Nếu chỉ đưa CI lên để thu evidence, dùng PR draft và chưa ghi M2 accepted; giải gap kỹ thuật ở trên trước khi xác nhận nghiệm thu coverage.

Sau review, người dùng có thể commit/push và tạo PR `ci/m2-remote` → `main` với tiêu đề `ci: integrate M2 regression and captured contract diagnostics`. Nội dung PR: regression13/TC13 giữFAIL; diagnostic networknone; reports/cleanup/upload always; static8/8 và offline118 có1provenance error như finding; remoteCI chưa chạy; input/scope/limitations giữ nguyên. Không coi các unit fixtures là testcase Directus mới.

```powershell
git commit -m "ci: integrate M2 regression and captured contract diagnostics"
git push -u origin ci/m2-remote
```

Trên GitHub chọn **Compare & pull request**, base main, review Files changed theo manifest. PR chỉ chạy workflow **Static / offline** trên GitHub-hosted Ubuntu; file integration không có pull_request trigger và chỉ cho manual main. Không dùng pull_request_target để cấp secret cho code PR. Không đặt job integration manual-main làm required PR check nếu chưa có quy trình phù hợp; nếu protection hiện đã yêu cầu job đó, cần quản trị viên xem xét chính sách, không tự miễn check để merge. Sau merge mới dispatch integration. [GitHub quy định manual workflow phải ở default branch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

## Runner, license và secret trước dispatch

- **Settings → Actions → Runners → New self-hosted runner**: Windows x64, label `damh-p09` cùng self-hosted/Windows/X64, runner online. Version tối thiểu2.327.1 cho Node24 của [checkout v6](https://github.com/actions/checkout/blob/v6/README.md)/[upload v6](https://github.com/actions/upload-artifact/blob/v6/README.md). Đăng ký token trực tiếp theo GitHub; không đưa token vào repo/report. Phiên review không có runner service/process chuẩn tại máy local; registry runner và admin secrets API chưa kiểm được qua connector, không suy không có runner khác.
- Dùng workspace runner riêng, code trusted/clean và HEAD=GITHUB_SHA; checkout clean:false chỉ để giữ ignored profile. Không trỏ runner vào checkout làm việc đang dirty. Provision Python tương thích (local đã test3.13), pwsh/Test-Json, Git Bash `C:\Program Files\Git\bin\bash.exe`, jq1.8.2 đúng hash, Docker Linux engine và ba image digest đã pin. Job không tự cài/start/seed/pull.
- Provision P09 đúng namespace `r06-k05-p09-20261115-audit01`, network/volumes riêng và fixture/policy; URL chỉ127.0.0.1:18055, DB không publish, không demo lab. Chỉ một writer; concurrency Actions không khóa process local. Dùng P09 procedure đã review khi cần môi trường riêng mới, không sửa namespace/volume demo cũ.
- Đặt credential trong ignored `runtime/profiles/<namespace>/p09.env` và fixture-ids.json tương ứng; cấp NTFS ACL riêng đúng tài khoản chạy runner. **P09 dùng P09_LICENSE_KEY**, không tự đọc LICENSE_KEY từ config/lab.env và không dùng GitHub `secrets.*`. Không cần tạo PAT/secrets mới cho workflow hiện tại. License phải hợp lệ trên runner/project thật, active và custom_permission_rules_enabled=true; active riêng lẻ chưa đủ. Preflight runtime phải xác minh lại actor/health/version/license/policy/fixture dưới chính tài khoản runner.
- Settings Actions phải cho phép checkout/upload v6, read repo và upload artifact; runner có đường mạng tới GitHub artifact service. Dùng contents:read, persist-credentials:false như hiện tại. Không tự khai báo đã kiểm remote permission/firewall.
- Nếu chạy full P08 reference validation, provision input lịch sử/snapshot và source object Directus pin `4f77933bf9551cac6b289576078783e189b8f4e3` chỉ đọc; không checkout/nâng Directus để né lỗi. Đây là dependency bổ sung cho coverage, không phải yêu cầu sửa SUT.

## Chạy và thu evidence nghiệm thu

Sau merge và runner/profile sẵn sàng: **Actions → P10 isolated regression smoke → Run workflow → main**. Nhánh feature sẽ bị guard chặn; không yêu cầu chạy job có secrets trên PR. Giữ expected TC13 FAIL/diagnostic FAIL: job đỏ/exit1 là bằng chứng phát hiện, không tự đổi PASS.

Thu URL/run ID/attempt, SHA/ref, runner, log, artifact `m2-ci-<run-id>-<attempt>` và đối chiếu:

1. Driver có regression13, trace17response đúng actor/schema/hash; contract FAIL được lưu.
2. Finalizer thực chạy, cleanup PASS hoặc UNVERIFIED/FAIL có lý do; không reset/broad restore/lab cũ.
3. Upload always thực sự thành công, không chỉ thấy YAML: đúng thư mục public, có ci-summary, reports/selection, raw OAS, responses, diagnostic, cleanup và index SHA256; thiếu artifact làm lỗi. Retention14ngày; lưu bộ nghiệm thu đã sanitize trước hết hạn.
4. Tách exit1 của SUT/contract với exit2 harness/infra/evidence, check full coverage portability độc lập và tổng hợp M2. ci-summary.remote_CI=EXECUTED_UPLOAD_PENDING không chứng minh upload đã hoàn tất. Khi runner chết/hủy cưỡng bức, always chỉ best effort; không có bằng chứng thì UNVERIFIED.

Không yêu cầu sửa Directus hoặc tất cả test PASS. Cần đầy đủ công việc/bằng chứng hợp lệ và gap có owner. Nhiệm vụ này không chạy API/regression/fuzz/campaign hoặc chuyển phase; private license/ACL và publication vẫn chờ người vận hành. Owner đề xuất: Lành runner/PR/CI và provenance portability; Nhân/Trâm phối hợp đối chiếu nguồn/oracle theo phân công, chưa ghi họ đã review.
