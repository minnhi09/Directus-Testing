# CI static/offline — P02

[Workflow](../.github/workflows/static-offline.yml) chỉ kiểm tĩnh/offline, không dựng lab, gọi Directus API, seed, integration hoặc fuzz. Static PASS không là API PASS, code coverage Directus hoặc acceptance. Căn cứ: kế hoạch mục 10–11 và 12.5/P02; dependency đã đối chiếu ở [handoff P02](coverage/handoffs/P02.md).

## Chạy lại tại repo DAMH

Cần Python có cú pháp >=3.10, Git, Bash và PowerShell có `Test-Json` hỗ trợ Draft 2020-12. Dùng công cụ có sẵn, không pip/npm/apt/choco install hoặc tự nâng phiên bản. Trên Windows, helper chọn Git Bash cạnh Git executable; không tự dùng WSL. Trên Linux dùng bash/pwsh có trên PATH. Phiên bản executable thực được ghi trong report; runner image có thể đổi tool version và chưa được xác minh trên remote.

```powershell
python scripts/check_offline.py
```

```bash
python3 scripts/check_offline.py
```

Mặc định tạo một thư mục mới `artifacts/runs/p02-static-<UTC timestamp>/offline-summary.json`; không dùng run lab cũ. Có thể chỉ định đường dẫn **chưa tồn tại** trong `artifacts/runs/`:

```powershell
python scripts/check_offline.py --output-dir artifacts/runs/p02-static-local-01
```

Không ghi đè output đã có. Script trả 0 khi mọi check PASS; trả 1 khi có FAIL hoặc thiếu tool (BLOCKED). Lỗi tạo/ghi report cũng trả nonzero, không che exit code. Các check độc lập tiếp tục để ghi đủ kết quả, rồi tổng hợp exit; không có blanket skip/xfail/continue-on-error. Bước upload Actions dùng `always()` và lỗi nếu không có summary. Hủy/timeout có thể ngăn report/step upload hoàn tất; không suy artifact đã được lưu nếu thiếu bằng chứng upload.

## Các checks được chọn

| Check | Phạm vi và giới hạn |
|---|---|
| Python syntax | AST parse `scripts/*.py`, `tests/*.py`, không gọi main và không tạo `.pyc` |
| JSON config/catalog | Parse `scripts/data/*.json`, P01 schema/examples JSON và từng dòng JSONL; từ chối duplicate object key và JSONL rỗng |
| Catalog/selector | Tái dùng `catalogue`, `designed_cases.main --selection course/short/assertable/all --list` và `cost_query.validate_model`. Kiểm ID không trùng, selection thuộc catalog và course giữ ca contract. Chỉ list/validate model, không chạy `cost_query.main`, Lab hay test selected |
| Bash syntax | `bash --noprofile --norc -n lab.sh` và tương tự cho `scripts/lab-components.sh`; chỉ parse, không source/chạy script hoặc đọc env |
| PowerShell/P01 | AST parse các `.ps1` ở `scripts/`, `scripts/windows/`, không gọi wrapper. [Helper](../scripts/check_coverage_examples.ps1) tái dùng cách bundle ref common local và `Test-Json` của P01 để kiểm record ví dụ; không tải `$id` qua mạng |
| Markdown local links | Newline/whitespace và tồn tại đích link local trong tài liệu này, `docs/coverage/**/*.md`. Không quét toàn report cũ, không gọi URL ngoài; chưa kiểm fragment Markdown ở check này |
| Workflow contract | `.yml` dùng cú pháp JSON, tập con YAML 1.2: parse bằng stdlib, kiểm trigger/permissions/static command/upload summary. Không cần thêm PyYAML để chạy CI. Đây chưa phải actionlint hay xác minh remote runner/action |
| Unit harness | Toàn bộ `tests/test_*.py`, gồm coverage/ref/archive, CI/ACL gate, metadata và fixture mocks; không chạy `probe_pinned_contract.py` phụ thuộc Schemathesis. Gate lỗi nếu không có test hoặc có skip/failure/error |

Driver [check_offline.py](../scripts/check_offline.py) giữ guard cho catalog. Toàn unit suite chạy qua [offline_suite.py](../scripts/offline_suite.py): chặn socket connect/DNS/bind, shell/child process khác và đọc private env thật; chỉ cho PowerShell7 chạy đúng coverage_schema.ps1 với local JSON payload để kiểm P01. Import/call ngoài phạm vi làm check lỗi. Guard là bảo vệ trước I/O vô tình, không phải sandbox cho code không tin cậy. Unit dùng tempfile/mock và input lịch sử đã archive, không cần credential/fixture runtime hay checkout Directus. [Cơ chế input bất biến](coverage/sources/immutable-inputs-v1/README.md) vẫn giữ hash/pointer gốc và TC13 FAIL.

Report là artifact **STATIC_OFFLINE_CHECKS**, ghi SHA harness, dirty state, fingerprint các file được kiểm, phiên bản tool, kết quả từng check và exit tổng. Các con số catalog/selector/unit/design-record là số cấu trúc hoặc unit harness, không cộng thành ca API/coverage hệ thống. Không upload raw log/request/response, config env, artifact lịch sử hoặc toàn bộ `artifacts/`. Unit fixture có các tình huống FAIL/INCOMPLETE giả lập để kiểm oracle; chúng không thay verdict TC01–TC13.

Local report ghi remote CI NOT_RUN. Nếu thực sự ở Actions, checker chỉ đọc các metadata không bí mật `GITHUB_ACTIONS`, `GITHUB_RUN_ID`, `GITHUB_RUN_ATTEMPT`, ghi run đang IN_PROGRESS và conclusion UNVERIFIED; kết quả toàn workflow/upload cần đối chiếu run thật sau đó, không tự nâng thành PASS trong checker.

## Workflow và dependency

Workflow chạy `push`, `pull_request`, manual `workflow_dispatch` trên `ubuntu-24.04`, timeout 10 phút, `contents: read`, checkout không lưu credential; không `pull_request_target`, secret, service/container hay job integration. Không có bước cài package, setup Python mới, Docker hoặc sửa baseline. Reuse standard-library harness; version/image Schemathesis và Directus trong manifest giữ nguyên.

Refs `actions/checkout@v6`, `actions/upload-artifact@v6` được tái dùng từ tree Directus **đúng baseline** `4f77933bf9551cac6b289576078783e189b8f4e3` (`.github/workflows/release.yml`, dòng uses; các file check/e2e/codeql chỉ tra uses liên quan). Không sao chép workflow integration upstream. Đây là pin **major tag**, chưa khóa commit bất biến của action; không tuyên bố đã xác minh tag/server/Node runtime hiện tại. Ubuntu label và Python/pwsh host cũng chưa là ảnh công cụ bất biến; script ghi tool version và fail khi thiếu, không tự nâng/cài. Muốn khóa thêm SHA/image công cụ cần nguồn và lượt giao phù hợp, không đoán SHA.

Artifact duy nhất là summary JSON, retention 14 ngày. Local report nằm trong đường dẫn Git ignore có sẵn. Remote sẽ chỉ thấy các file đã có trong commit được checkout; hiện các input/harness/P01 còn dirty/untracked, nên local kết quả không chứng minh một checkout remote sạch tương đương. Không tự stage/commit/push để làm CI chạy.

**Integration: NOT_RUN** — không có lab/license/environment gate được kiểm trong P02. Code/schema/API coverage thực: NOT_MEASURED. Remote Actions: NOT_RUN cho đến khi có run URL/ID, SHA, job conclusion và artifact upload thật. actionlint/shellcheck/Compose render, chạy contract adapter trong Schemathesis pin và validator semantic liên file/calculator P08 không nằm trong gate P02 này; thiếu tool/phạm vi được ghi ở handoff, không gọi syntax/static PASS là đã qua các kiểm đó.
