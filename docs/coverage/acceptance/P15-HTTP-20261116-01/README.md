# Hoàn thiện HTTP metadata S1–S6 — 16/11/2026

**Nhiệm vụ capture và kiểm chứng contract COMPLETE; không phải SUT contract PASS.** Chỉ chạy lại6scenario cần header,6business-oracle PASS,fixture trước/sau khớp; không chạy lại TC13 hoặc fuzzing. Với đúng17response mới,4check/response: **68check,56PASS/12FAIL**, không lỗi validator hoặc response chưa đo. Cả6scenario có ít nhất1contract diagnostic FAIL; không gọi chúng contract PASS.

## Tại sao cần chạy lại

Artifact P15-TRACE trước có body/status/actor nhưng không có header HTTP; không thể khôi phục Content-Type chính xác từ JSON. Harness chỉ thêm capture opt-in, không thay expected/oracle: curl ghi status, Content-Type, time_total,HTTP version,effective URL tại lúc gửi. Default trace off giữ format cũ cho các lệnh khác. Không dump Authorization/Set-Cookie hoặc toàn bộ header.

scripts/capture_scenario_http.py kiểm ownership/healthy/version/fixture của lab P09, xuất OAS theo từng actor và ghi selection **trước mutation**, gọi lại6function scenario hiện có. Chỉ S1 tạo/xóa item tạm; Reader write vẫn bị từ chối, không reset/seed/broad restore hoặc chạm lab cũ. Shared helper vẫn chính là oracle cũ; chỉ thêm metadata. Source hashes lúc capture và runtime-metadata.json ghi harness DIRTY,source pin4f77933bf9551cac6b289576078783e189b8f4e3,Directus12.5.0/image/arch/fixture và pinned runner.

## Metadata và schema binding

[Trace](trace.json)17record version2: actor,method/path,request JSON,status,response file/hash,content_type,elapsed_seconds,http_version,effective_url,recorded_at.16response có `application/json; charset=utf-8`; DELETE204 có Content-Type rỗng **được quan sát từ curl**, không gán application/json giả. Raw body204 giữ rỗng, có SHA256 như các body khác. Thời gian captured response window không được gọi là chính xác start/end function.

[Schema metadata](schema-metadata.json), raw-oas/ và schema-comparison.json: từng Editor/Reader/admin/anonymous có snapshot riêng,hash đều khớp byte capture trước. Mỗi check dùng schema của actor thực tế trên record và kiểm hash schema/body trước khi đánh giá. Anonymous được export không Authorization nhưng không có protected qa_* route; không dùng Editor thay thế, không gán contract PASS/N/A hoặc gửi thêm protected anonymous request. Schema thiếu/khác actor/hash sai/metadata thiếu không được nâng thành PASS.

## Contract verification thực

scripts/check_scenario_contracts.py tái dùng contract_checks.validate trong image Schemathesis4.30.0 đúng digest, --pull never/--network none, chỉ read-only mounts. Không phát thêm HTTP request khi revalidate. Kiểm not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance. Kết quả đầy đủ ở [contract diagnostics](contract-diagnostics.json), [tóm tắt hai chiều](dimension-summary.json).

| Scenario | Business oracle | Response | Contract diagnostic | Check FAIL |
|---|---|---:|---|---:|
| S1 | PASS | 6 | FAIL | 3 |
| S2 | PASS | 1 | FAIL | 1 |
| S3 | PASS | 2 | FAIL | 2 |
| S4 | PASS | 3 | FAIL | 3 |
| S5 | PASS | 2 | FAIL | 2 |
| S6 | PASS | 3 | FAIL | 1 |

12failure gồm7JsonSchemaError và5UndefinedStatusCode. POST object/schema array cùng pattern TC13; GET projection/selected fields có mismatch response schema cần phân tích như contract finding, không tự là business defect. DELETE204/denial403 không khai báo là contract status gap dù oracle nghiệp vụ có thể đúng. Không sửa expected status/schema cho xanh. Không đếm12check FAIL thành12defect hoặc17response thành17canonical case. Tất cả check Content-Type được thực thi với metadata thật; check không fail không chứng minh mọi phần hợp đồng đều PASS.

## Coverage và lịch sử

[Bundle](bundle/) execution1.1 giữ13canonical/version/RTM/oracle;6execution mới+7P10 giữ nguyên gồm TC13 FAIL,selection khai báo trước. [Lineage](lineage.json), validation.json, coverage-summary.json, coverage-commands.json ghi source/exit. R13,D13,E13,V12/13 không đổi vì §6.2 đang đo mandatory oracle đã khóa. Hit/positive5/5 là **5template generic binding qa_articles**, không phải10concrete pairs/toàn hệ thống.

Các execution S1–S6 trong bundle là projection business runner: contract_verdict=NOT_RUN mô tả helper gốc, không được dùng trường đó để phủ nhận việc offline diagnostic mới đã chạy và FAIL. Diagnostic có mode/evidence riêng liên kết cùng execution; **báo cáo M2 bắt buộc trình bày cả business và contract diagnostic**, không chỉ lấy V12 để nói SUT đã đạt. Không tự thêm/bỏ mandatory assertion hoặc sửa oracle/công thức để ép V. TC13 canonical vẫn FAIL. Nếu muốn đổi tập requirement/contract mandatory, cần một revision thiết kế có nguồn; không làm trong nhiệm vụ capture này.

Report/trace thiếu header trước và TC13/P10/P14 cũ giữ nguyên. Không backfill metadata vào run lịch sử. Original responses/schema/expected không sửa.

## Kiểm tra và tái lập

Preflight-before/after đạt; scenario-outcomes và verification-trace so đầy đủ baseline2collection trước/sau, không broad restore. tests/test_http_contract_metadata.py kiểm metadata thiếu/null, known-empty Content-Type, actor sai, schema/body hash sai,operation absent,version1 không được coi đủ dữ liệu,wrong target/negative time; kiểm actual17response/68check/12FAIL và Reader-schema binding. Trace/P09 isolation/coverage tests và static/diff/protected-hash/secret checks ghi kết quả cuối ở audit-evidence.json.

Khi được giao run mới (chọn ID chưa tồn tại):

```powershell
python -B scripts/capture_scenario_http.py --run-id P15-HTTP-20261116-02
```

Đây là lệnh live chỉ6scenario, cần lab P09 đúng profile/private env đã provision. Không dùng để chạy lại chỉ nhằm xanh. Revalidation offline dùng đúng image pin, network none và script check_scenario_contracts.py trên thư mục capture; thiếu package host không cài/nâng để thay image pin.

## Điều kiện còn thiếu cho CI và M2

1. **CI run thật:** workflow/code hiện còn local chưa commit/push theo quyền. Cần trusted remote revision,runner self-hosted Windows/X64/damh-p09 đã đăng ký/online được xác minh,lab test riêng và private credentials/license hợp lệ tại runner. Không sao chép secret vào artifact hoặc chạy fork code với secret.
2. Workflow hiện chỉ preflight+regression smoke; **chưa chạy capture/contract-diagnostic mới**. Nếu dùng evidence này để kiểm chứng trên CI, cần nối bước tương ứng trong nhiệm vụ CI riêng, giữ nonzero/check FAIL và artifact always; không tắt check để xanh. Không thay workflow trong batch này.
3. Phải có run URL/ID/ref/attempt/runner identity thực,report/schema/hash/request-response/cleanup đã sanitize và đủ artifact kể cả job FAIL; đối chiếu lại trạng thái job/upload. File workflow và local tests không thay được run evidence.
4. **M2 công việc QA:** source selection/oracle/reproducer/RCA/coverage có nguồn; complete evidence khác SUT PASS. TC13 và12contract diagnostics được báo cáo/nhóm nguyên nhân,không bắt sửa Directus để đóng công việc kiểm thử. Qualified metrics/SUT conformance vẫn có FAIL; không waiver hoặc đổi expected. Không tự nghiệm thu giảng viên.
5. Protected anonymous operation không có OAS nên giữ NOT_MEASURED cho schema-based contract, không coi authorization business evidence là contract evidence. Keyword/code coverage vẫn NOT_MEASURED. Fuzz P14 budget/max_time/FAIL vẫn giữ; full10operation/3seed không tự mở rộng thành nhiệm vụ bắt buộc mới.

Nhiệm vụ tiếp theo: kiểm chứng CI theo phạm vi/quyền được giao; batch này không commit/push hoặc chuyển Phase. Owner đề xuất Lành CI/tích hợp,Nhân contract/RCA,Trâm oracle; không gán review của họ.
