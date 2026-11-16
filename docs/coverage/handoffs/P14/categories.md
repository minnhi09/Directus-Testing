# P14 — REST Items/category pilot — 16/11/2026 Asia/Bangkok

**Phase COMPLETE về sản phẩm pilot có budget; raw/guided verdict FAIL, completion INCOMPLETE_BUDGET.** Cả hai stop_reason=max_time; CLI complete=true là engine kết thúc có report, không chứng minh đã khám phá hết không gian. Không acceptance PASS, không đổi TC13 hoặc raw contract.

## Dependency/input và lựa chọn

Đọc AGENTS root, Git status/HEAD, kế hoạch §9/§12.5/P14, handoff P10 và checkpoint thực thi, P07 selected inventory/fixture, CLI gate P09 và source framework campaign/build/replay. Chưa có P14 handoff hoặc batch trước lượt này. P10 chứng minh CRUD/fixture đạt, TC13 contract FAIL còn OPEN; P11–P13 không mặc nhiên hoàn tất hoặc bắt buộc cho module này. Chỉ sử dụng nhóm fixture P10 đã có.

Harness D:/DAMH-full-recovery-2026-10-12/DAMH; HEAD2e44fe7558cb4e3fc12e19b7d44af2421f81ed72 DIRTY; source Directus pin4f77933bf9551cac6b289576078783e189b8f4e3 không sửa/checkout. Đối chiếu5 source route Items trong [source inventory](../../runs/P14-20261116-01/source-inventory.json), giữ source@SHA và template /items/{collection}[/{pk}], bind runtime {id} riêng, không tạo5 ID canonical mới.

Chọn category CRUD (P10 P3-ST-01) trong module Items/P07 category binding, chưa có P14 trên selection hiện hành. Không tuyên bố chưa từng chạy category trong lịch sử. Pilot cũ schema-smoke nhắm qa_articles; không lặp toàn10 operation/22 nhóm. Đây là binding fixture thử mới của module được chọn, không mở auth/admin fuzz scope. Schema/model name required string max80 và primary id integer tự tăng theo helper hiện có; category tên Unicode tái dùng fixture-oracle.json.

Tạo collection run-owned qa_sys_categories_p14_20261116_01, actor/role/policy/access/4permission riêng. Không thêm quyền vào Editor/Reader cũ. Lab P09 ownership/health/license/actor/fixture được kiểm hiện tại trước và sau; network/DB không đổi. Chỉ admin bootstrap/export/control/teardown; fuzz actor CRUD đúng collection riêng. Restore chỉ collection do run tạo, không gọi broad restore hoặc reset DB. Ba category gốc/tất cả qa_articles cũ không là target mutation.

## File và schema

Tạo scripts/p14_pilot.py và tests/test_p14_pilot.py; sửa tương thích API.call trong scripts/p09_runtime.py cho explicit method (default cũ giữ). Không sửa helper/oracle/canonical ID cũ. [Run directory](../../runs/P14-20261116-01/) gồm raw-oas nguyên byte/hash theo admin/actor, schema-raw scoped5operations giữ contract, schema-guided/diff chỉ thêm example body/id, fixture map, run config/report, report JSON/NDJSON/coverage/console đã sanitize, replay, restore, pre/post gate và audit. Chưa thêm links/stateful vì chuỗi đó không cần cho pilot examples/fuzzing; ID examples lấy từ fixture do run tạo, không hardcode ID lịch sử.

Budget đúng §9.3: seed101,1 worker,2/s,10s request,10examples/operation,60s/profile. Lời cập nhật đầu dùng budget helper cũ20/300 được sửa trước chạy; không chạy theo budget đó. CLI --version/run --help được chụp lại bằng pinned image4.30.0; flag report/coverage có thật, không cài/nâng dependency. Read-only preflight/control xong trước mutation; không raw/guided dài3seed.

## Kết quả thực và sự cố công cụ

Raw:5selected/5tested;115generated,7unique failures theo tool; exit1,60.92s,stop_reason=max_time. Guided:5/5;113generated,10unique failures theo tool; exit1,stop_reason=max_time. Các số này là generated/check records, không canonical cases/defect count hoặc số coverage toàn hệ thống. Raw có UndefinedStatusCode; guided thêm JsonSchemaError/RejectedPositiveData. 403 cho ID/quyền không hợp lệ hoặc 400 cho input vi phạm DB/policy được phân loại contract/precondition, không tự thành product defect; status204 DELETE không khai báo cũng là contract gap.

Replay đại diện: POST object hợp lệ, read-back khớp; đối chiếu response đã nhận với nguyên raw contract bằng scripts/contract_checks.py trong pinned image, network none: response_schema_conformance FAIL/JsonSchemaError (raw đòi data array, runtime object);3check khác PASS. Nối occurrence với guided console case7yF2KV và known TC13 pattern, chưa tuyên bố root cause/defect mới. Đây là regenerated representative cùng partition/operation; **không phải exact-byte st replay7yF2KV**, không replay chuỗi parent bị thiếu. NDJSON image hiện tại chỉ recorder label nên không giả có full serialized chain. Reproducer JSON/body/precondition/source schema được lưu; credential chỉ cấp lúc chạy.

Sau raw restore snapshot đã đạt, adapter gặp TypeError khi ghép đường dẫn file restore; đã giữ run-report-before-guided-resume.json, sửa lỗi rồi dựng lại cùng collection/fixture, so scoped raw/guided với snapshot cũ trước resume. Không chạy lại raw. OAS resume được lưu file riêng, không đè raw bytes lần đầu. Guided chạy một lần. Hai restore verified, replay restore verified, tất cả tài nguyên riêng được DELETE theo thứ tự ngược và post-P09 preflight đạt. Lần driver đầu exit2 vì lỗi tổng hợp; resume driver exit0 là orchestration cũ, profile exit1 luôn được giữ. Driver bàn giao đã trả1 nếu profile thất bại, không dùng orchestration0 làm suite PASS.

## Checks / DoD / gap

4 unit scope/immutability/missing-operation/resume guard PASS; static/offline, diff, secret scan, hash và pre/post safety ghi kết quả cuối ở audit-evidence.json. Raw/guided reports giữ stop_reason,max_time,failures/errors. Raw byte hash không đổi; overlay response contract nguyên vẹn. Restore từng profile verified và cleanup tài nguyên riêng verified. GET permission theo ID trả synthesized admin permission (id=null, collection khác) nên không dùng HTTP200 đó để kết luận row còn; SELECT read-only trong đúng DB P09 xác nhận0 persisted permission cho collection thử, các tài nguyên còn lại GET403/404. Lab cũ không bị start/stop/API/DB, historical TC01–TC13/report/raw OAS giữ nguyên. Không commit/push/PR/issue/publish/liên hệ/sub-agent.

DoD pilot đạt theo phạm vi có budget với FAIL/INCOMPLETE được ghi đúng; không kéo dài budget để gọi complete. Keyword/line/branch/RTM coverage **NOT_MEASURED**: file plugin coverage có thật nhưng semantics chưa được chứng minh. Formal defect count CHƯA XÁC MINH, generated cases không có canonical ID mới. Còn gap exact-byte replay/serialized event chain, stateful links chưa bật, remote CI NOT_RUN; không chặn bằng chứng deterministic representative đã có, không tự mở campaign hoặc module khác.

Batch P14/category đã xong; next action P15/M2 theo scope K05, đọc P08/P10/P14 và acceptance gates, triage known failures trước kết luận nghiệm thu. Chưa tự chuyển phase hoặc duyệt M2. Owner đề xuất Nhân theo kế hoạch, không gán review/ngày chạy cho thành viên khác.
