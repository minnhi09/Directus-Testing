# Trạng thái cập nhật theo văn bản — 15/11/2026

Validator/calculator hiện có 26 tests; `calculate docs/coverage/baselines/M1-REGRESSION-13-v1` hợp lệ dữ liệu, R/D=13 nhưng execution coverage NOT_MEASURED. Scope này do nhóm 11 xác nhận, không phải giảng viên duyệt riêng. Các module khác giữ reference/UNKNOWN, không tự thành nghĩa vụ automation. Xem [review 20 phase](../../../RA_SOAT_20_PHASE_R06_K05_2026-11-15.md) và [tiến độ](../../../../evidence/progress-2026-11-15.md). Output/diagnostic P08 cũ vẫn nguyên trạng.

---

# Cập nhật resolver và baseline — 15/11/2026

Kết quả hiện tại: **26 tests offline PASS**; `python -B scripts/coverage_offline.py calculate docs/coverage/baselines/M1-P07-v2` trả exit 0 nhưng coverage NOT_MEASURED. [V2](../../baselines/M1-P07-v2/README.md) giữ DRAFT/BLOCKED chờ scope. Reference registry tùy chọn dùng format P08_REFERENCE_REGISTRY_1, chỉ chấp nhận CAPABILITY/UNRESOLVED có ARTIFACT hash và ID thực trong shard `docs/coverage/inventory/*.jsonl`; không đăng ký ID tùy ý để vượt FK. Prerequisite PC-label được tách khỏi test dependency trong revision dữ liệu, không nới validator. Filter module requirement không che route thuộc module khác đã được chọn. Các output P08 v1 bên dưới giữ nguyên như bằng chứng lịch sử.

---

# P08 — Validator và calculator offline

Chỉ đọc bundle P01, không gọi Directus. [CLI](../../../../scripts/coverage_offline.py) dùng Python stdlib, tái dùng strict JSON reader P02; [schema bridge](../../../../scripts/coverage_schema.ps1) dùng PowerShell 7 Test-Json đã có trên máy, resolve common defs cục bộ. Không fetch schema URI hoặc tự cài dependency. Thiếu pwsh trả failure có mã rõ.

## Lệnh tái lập

Tại root DAMH:

```powershell
python -B scripts/coverage_offline.py validate docs/coverage/baselines/M1-P07-v1
python -B scripts/coverage_offline.py calculate tests/fixtures/coverage-offline --sample
python -B -m unittest discover -s tests -p test_coverage_offline.py -v
python -B scripts/coverage_offline.py inspect-history docs/HoanThanhPlan/tai-lieu-bo-tro/phase8-20261018/evidence/p8-20261018-assertable/designed-report.json
```

validate/calculate trả 0 khi schema và semantic/reference kiểm được; trả 1 khi lỗi. Không bỏ qua reference lỗi để xuất tỷ lệ. inspect-history chỉ trích metadata verdict nguyên trạng, không convert execution hoặc gắn baseline mới. CLI không ghi file input; stdout là JSON, diagnostic không in record value/secret.

P07 hiện schema hợp lệ nhưng strict resolve trả **PREREQUISITE_TEST_MISSING / exit 1**: prerequisite PC-* chưa là canonical test registry; tiếp theo còn lineage parent version/sidecar target và stale citation được handoff P07 ghi. Đây là gap đầu vào thật, không sửa frozen baseline trong P08. [Diagnostic](P07-validation.json) không phải coverage-summary hoặc API FAIL. Chỉ dừng việc tính coverage cho bundle lỗi; fixture độc lập vẫn kiểm được calculator.

## Hợp đồng công cụ

Bundle có baseline-manifest.json, selection-manifest.json, system-inventory/requirements/test-catalog/rtm-links/gaps/decisions.jsonl và executions.jsonl tùy có. Dùng nguyên schema P01, strict JSON duplicate/non-finite checks; schema lỗi/reference lỗi fail. Sidecar P03–P07 không tự trở thành registry chuẩn. Finding registry chưa có adapter nên finding_id khác null trả FINDING_REGISTRY_NOT_SUPPLIED; không bịa finding.

Resolve alias về canonical/version trong bộ nhớ, giữ input bất biến. Kiểm unique registry/edge/assertion/attempt, FK/revision/projection, prerequisite/lineage cycle, retry parent tăng attempt cùng run/test/version, N/A và selection LOCKED phải có quyết định đủ provenance. Artifact hash/JSON pointer/line range và Git object pin đọc local; từ chối ref ngoài repo, env/key và network schema. Source ref chỉ chứng minh bytes tồn tại, không chứng minh oracle business đầy đủ; phần review oracle vẫn cần người/source/profile.

Chỉ DIRECT góp D/E/V. D cần requirement oracle, test oracle và fixture profile có nguồn đủ trong bundle. E cần assertion PASS/FAIL có oracle/evidence đúng requirement; BLOCKED hoặc gửi request đơn thuần không góp E. V cần mọi test DIRECT bắt buộc được chọn mới nhất PASS, assertion bắt buộc theo requirement đã đánh giá PASS, completion/cleanup/infra/tool đủ; FAIL hiện hữu không bị MAX_TIME hoặc cleanup ghi đè. Danh sách assertion bắt buộc có trong execution phải được đối chiếu catalog/oracle khi tạo evidence, tool không tự chứng minh assertion bị bỏ sót chưa từng được khai báo.

R chỉ từ requirement APPLICABLE đã REVIEWED/LOCKED của selection/tầng/module; scope UNKNOWN hoặc denominator chưa LOCKED => NOT_MEASURED. Không có execution đánh giá được (kể cả chỉ BLOCKED) => execution/verified NOT_MEASURED; không sinh 0% giả. Empty denominator cũng NOT_MEASURED.

O là các REST inventory APPLICABLE trong subset selection đã khóa/tầng/module/transport. Key REST phải khớp method/template/variant/profile; không sinh alias path mới, không gộp list/detail. Bundle inventory có nhiệm vụ hợp source/OAS đã review; calculator không đoán union/alias từ live API. Hit cần dispatch + request/response refs; middleware-denied không hit. Positive cần business PASS + assertion có nguồn và read-back theo operation evidence; contract FAIL vẫn giữ riêng. Không tự suy 2xx thành positive.

Run selection PREDECLARED_EXECUTIONS chọn đúng ID được khai báo; nhiều execution cùng test/version không tự chọn PASS. LATEST_ATTEMPT_IN_PREDECLARED_RUNS chọn theo started_at quy về UTC rồi attempt; tie mơ hồ fail. Giữ mọi attempt và xuất flaky/disagreement, không sửa history. Run ID trong manifest có thể đã khai báo mà chưa có execution; khi đó NOT_MEASURED. UNDECIDED không chọn execution để tính.

Output **P08_OFFLINE_SET_REPORT_1** là report chẩn đoán/tập ID của công cụ; không rename hay ghi đè P01 coverage-summary. Có R/D/E/V/O, missing ID, selected execution, source/OAS-only và phân bố verdict/cleanup/infra. Specification usability, authorization-rule matrix, module qualification và code/schema coverage chưa có đầu vào chuẩn đã review nên giữ NOT_MEASURED; không dùng partial/violated/generated examples làm PASS. Không giả một flag OAS PRESENT là contract đủ dùng.

## Đối chiếu tay và bằng chứng

[Fixture](../../../../tests/fixtures/coverage-offline/README.md) toàn DESIGN_EXAMPLE. Người duyệt/timestamps/verdict/evidence ở fixture chỉ là dữ liệu tổng hợp. `--sample` bắt buộc mọi record là DESIGN_EXAMPLE; real mode từ chối sample. Không chuyển sample sang lịch sử.

| Tập/metric | Kết quả kiểm tay trên sample |
|---|---|
| R / D | A,B,C / A,B,C |
| E | A,B; FAIL có assertion đánh giá được tính, C BLOCKED không tính |
| V | B; A có mandatory contract/business FAIL trên test thứ hai, C chưa chạy |
| O | LIST,DETAIL |
| Hit / positive | LIST / LIST; DETAIL source-only và missing |
| SUPPORTING | A→C không biến C thành E/V |
| Alias | SAMPLE-ALIAS-A và canonical A chỉ là một test |

[Sample output](sample-output.json) ghi synthetic=true/data_origin=DESIGN_EXAMPLE. [21 unit checks](../../../../tests/test_coverage_offline.py) kiểm thêm latest retry/UTC/tie constraints, alias collision, FK/schema failure, middleware deny, cleanup/infra và không execution. [Command checks](command-checks.json) ghi exit thật, gồm negative schema/reference CLI. [Legacy inspection](legacy-inspection.json) đọc report thật, TC13 vẫn business passed/contract failed/status failed, converted_executions=0.

[Input fingerprints](input-fingerprints.json) và [audit](audit-evidence.json) giữ bằng chứng bảo toàn 125 đầu vào. [Handoff P08](../../handoffs/P08.md) tách trạng thái hoàn tất công cụ, verdict unit và coverage SUT. Không chạy lab, API, campaign hoặc remote CI.
