# P10 regression13 — 16/11/2026, Asia/Bangkok

**Run hoàn tất: 12 PASS, 1 FAIL; cleanup PASS.** Phase P10 hoàn thành đầu ra, khác verdict suite FAILED/exit1 và acceptance chưa đạt do TC13 contract FAIL. Không waiver, skip hoặc sửa expected. Attempt01 BLOCKED được giữ nguyên; attempt02 predeclare selection trước mutation. Không cộng alias, request, resume hoặc generated example thành ca mới.

[Selection](selection-manifest.json) giữ nguyên13 canonical/version,13 requirement và denominator của M1-REGRESSION-13-v1; chỉ đổi selection/run/execution IDs cho run mới. [Run report](run-report.json), [S1–S6](scenario-report.json), [7 designed cases](designed-report.json), [DB oracle](database-oracle.json), [runtime metadata](runtime-metadata.json), preflight-before.json/preflight-after.json và scenario-outcomes.json là evidence thực.

Engine hoạt động sau khi người dùng mở Docker. Hai container namespace r06-k05-p09-20261115-audit01 đang dừng được up lại với explicit profile/private env, giữ DB và volume. Ownership/image/mount/network/loopback được kiểm trước chạy; preflight license/actor/fixture READY. Directus12.5.0 đúng digest, Schemathesis4.30.0 đúng digest, một worker, rate5/s, timeout10s, budget600s cho designed suite; seed không áp dụng vì deterministic. Actor Editor/Reader theo selection; admin chỉ preflight/control/schema/snapshot. Không gọi API/DB hoặc start/stop lab cũ.

## Kết quả và cleanup

S1–S6 đều PASS, gồm S3 có order proof từ SELECT trực tiếp trong DB P09; không dùng output API làm expected. Course selector tái dùng đúng7 case cũ:6 PASS và P3-CONTRACT-QA_ARTICLES-OBJECT (aliasTC13) FAIL. TC13 business PASS, authorization NOT_APPLICABLE, robustness PASS; response_schema_conformance FAIL/JsonSchemaError, ba contract check còn lại PASS. POST trả object trong khi raw schema khai báo data array; không đổi raw/schema/oracle. Case JSON và python-http/ chứa evidence đã sanitize.

Shell group dùng helper scenario cũ nhưng không gọi broad campaign_restore. So sánh đầy đủ snapshot trước/sau cho cả hai collection đạt. Designed runner chỉ cho phép PATCH/DELETE ID lấy từ POST của chính run, từ chối cleanup row lạ;7 cleanup đều PASS, snapshot đầy đủ khớp trước mỗi ca. Không reset/reseed hoặc PATCH lại hàng loạt fixture. Post-preflight24 check true. Chỉ thay đổi item tạm do run tạo; negative Reader probe tới fixture bị từ chối, dữ liệu giữ nguyên.

Sau khi S1–S6 xong, adapter tổng hợp gặp lỗi decode Windows cp1252; sửa đọc UTF-8 và resume đúng attempt, **không chạy lại6 ca**. run-report-before-resume.json giữ checkpoint trước resume; run-report-before-binding.json giữ report trước bổ sung metadata canonical/version/execution ID. Bổ sung ID không đổi verdict. Không suy lỗi công cụ thành lỗi SUT. Bảy case được chạy một lần trong pinned container; runner exit1 vì contract FAIL.

Raw OAS theo admin/editor/reader được export sau preflight fixture vào thư mục mới raw-oas/, có SHA256 trong report. Không ghi đè raw OAS/baseline hoặc report cũ. Harness HEAD chỉ nhận diện commit nền vì working tree DIRTY; hash cuối của source/input/output ở audit-evidence.json. Chưa có snapshot byte source riêng tại dispatch; hash audit là revision bàn giao sau bổ sung metadata, không giả là snapshot đã ghi trước run.

## Tái lập và CI

Từ root DAMH, engine/lab P09 đã provision và preflight hợp lệ:

```powershell
python -B scripts/p10_regression.py --namespace r06-k05-p09-20261115-audit01 --run-id P10-20261116-03
```

Phải dùng run ID mới; mặc định từ chối ghi đè. --resume chỉ dùng checkpoint sau lỗi tổng hợp trước designed suite, không dùng để chạy lại run hoàn tất. Không giả project trong fixture map; Runner.preflight nhận LAB_PROJECT_NAME explicit, default legacy r06-k05 vẫn giữ. Host chỉ18055, target trong container chỉ directus:8055. Không dùng wrapper lab.sh mặc định vào P09.

.github/workflows/p10-integration-preflight.yml đã nối regression smoke thật sau preflight, manual/self-hosted damh-p09, serial, không PR/fork trigger hoặc hardcode license. Checkout clean=false bảo toàn profile ignored. Thiếu runner/private profile/lab là lỗi hạ tầng, không PASS. Upload evidence với always(); runner exit1 được giữ, không continue-on-error. Remote CI **NOT_RUN**, chưa push, chưa xác minh runner registration; không ghi kết quả local thành Actions PASS. P02 static vẫn job độc lập, không cần Extended/license.

## Reference/provenance sau tích hợp

P08 validate trực tiếp baseline cũ trả ARTIFACT_HASH_MISMATCH, vì guard project trong scripts/designed_cases.py đã đổi còn ref khóa byte cũ. Không thay hash baseline cho khớp code mới hoặc sửa baseline lịch sử. Đã khôi phục riêng byte nguồn trước thay guard, đối chiếu SHA256 chính xác0e35ca1dc0102bc452e46ca5ebf3b74051dac56ab8007e9a172eba205a3a0c1e, lưu docs/coverage/sources/p10-input-0e35ca1dc010.py. [Resolved inputs](resolved-inputs/) giữ nguyên baseline ID/design/selection/denominator/oracle, chỉ relocate ref tới snapshot bất biến có cùng hash. P08 validate bản này exit0/valid=true; log lỗi trực tiếp ở p08_validate-check.txt được giữ. Đây là snapshot thiết kế cũ có kiểm hash, không giả là source thực thi mới. Execution source adapter được ghi riêng bằng hash revision bàn giao.

Checks local:15 unit harness,10 P09 isolation,10 P10 selection/project guards PASS; static8/8 nhóm PASS; P08 validate selected baseline và diff/link/secret checks ghi exit thực trong audit. Runtime13 case được đếm riêng unit/request. Formal P08 coverage/keyword/line/branch metrics **NOT_MEASURED**, chưa chạy calculator nhập execution records P01; không gọi12/13 là coverage toàn hệ thống. Tracecov semantics CHƯA XÁC MINH. Không raw/guided/fuzz/P11/P14.

[Register](missing-known-issues.json) đóng blocker engine/adapter/schema-order trong run này; TC13 vẫn OPEN, remote CI NOT_RUN. Tiếp theo theo đường K05 đã chọn là P14 sau khi xử lý/triage prerequisite và được giao; P11–P13 tùy chọn scope. Không tự chuyển phase, nghiệm thu G1/M2/M3 hoặc commit/push.
