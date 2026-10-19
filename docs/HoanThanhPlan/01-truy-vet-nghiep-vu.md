# Truy vết nghiệp vụ - Phase 1


**Hướng đặc tả đã được người dùng chốt:** Bám baseline Directus đã pin, không tự thêm quy tắc nghiệp vụ. Xem [đối chiếu source P1-05](01-doi-chieu-baseline-p1-05.md). Phần còn thiếu căn cứ giữ OPEN; kết quả test lịch sử không thay đổi.

Tài liệu này trình bày chuỗi yêu cầu → quy tắc → API/actor → test/oracle → evidence/gap. Bảng A-H lịch sử được giữ tại [truy vết A-H](../traceability.md); không thay bằng kết quả ngày 18/10. Không có test mới được chạy khi biên soạn.

- [Đặc tả UR/BR/AC và rủi ro](01-yeu-cau-va-dac-ta.md).
- [Review, câu hỏi mở và gap task](01-review-dac-ta.md).
- [Ma trận CSV đầy đủ nguồn/ưu tiên/rủi ro](01-traceability.csv).

Trạng thái evidence: **HISTORICAL_SAMPLE** = mẫu lịch sử chứng minh phần nêu trong oracle; **PARTIAL_EVIDENCE** = có mẫu nhưng thiếu lớp/đường kiểm hoặc oracle còn hạn chế; **CONFIG_ONLY** = có cấu hình, chưa có functional evidence trực tiếp được chọn; **FAIL_CANDIDATE** = có assertion failure/finding cần triage. Không nhãn nào là nghiệm thu toàn BR hoặc coverage thực thi 100%.

Mã S1-S6 và INV-01 đến INV-11 giữ nguyên. INV là mã trong tài liệu; report invariant dùng case_id dạng tên. SMOKE:<tên> chỉ vị trí kiểm tra đã có, không phải mã test mới. GAP-* là việc đề xuất, chưa được triển khai. Khi có Q-* chưa chốt thì không áp assertion cứng cho chi tiết đó.

| UR / BR / AC | API và actor | Kỹ thuật / test hiện có | Oracle và giới hạn | Evidence lịch sử / trạng thái | Việc thiếu / câu hỏi |
|---|---|---|---|---|---|
| UR-01;UR-02 / BR-01 / AC-01 | POST + GET detail /items/qa_articles; /items/qa_categories — Editor | Scenario/CRUD read-back / S1;INV-03;INV-04 | ID integer dương từ create và read-back bản ghi; chưa chứng minh ID không thể bị client chỉ định | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **HISTORICAL_SAMPLE** | GAP-11; Không có Q riêng |
| UR-02;UR-07 / BR-02 / AC-02 | POST/PATCH /items/qa_categories[/id] — Editor | Phân vùng + biên + required/null / INV-04 | So input name với dữ liệu đọc lại; non-null/max 80 có trong cấu hình, chưa có bộ negative/biên | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-01;GAP-13; Q-01;Q-02;Q-03 |
| UR-01;UR-07 / BR-03 / AC-03 | POST/PATCH /items/qa_articles[/id] — Editor | Phân vùng + biên + required/null / S1;INV-03;INV-04 | Title create/read-back có mẫu; null/required/max 120 cần case riêng | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-01;GAP-13; Q-01;Q-03 |
| UR-01;UR-07 / BR-04 / AC-04 | POST/PATCH /items/qa_articles[/id] — Editor | Phân vùng enum + default/state / SMOKE:check_field_validation;INV-09 | Archived với score hợp lệ có probe riêng HTTP 400; INV-09 kết hợp hai lỗi; default/omission chưa được test | [20261012T222250Z-1431](../../artifacts/runs/20261012T222250Z-1431/contract-validation.json); [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-02;GAP-13; Q-03 |
| UR-01;UR-07 / BR-05 / AC-05 | POST/PATCH /items/qa_articles[/id] — Editor | Phân vùng + biên + kiểu / SMOKE:check_field_validation;INV-03;INV-04;INV-09 | Probe score=-1 riêng HTTP 400, ca score hợp lệ có mẫu; chưa đủ biên/kiểu/null/omission | [20261012T222250Z-1431](../../artifacts/runs/20261012T222250Z-1431/contract-validation.json); [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-02;GAP-13; Q-02;Q-03 |
| UR-01;UR-07 / BR-06 / AC-06 | POST/PATCH + GET /items/qa_articles[/id] — Editor | Phân vùng/null + round-trip / INV-03;INV-04 | Payload có timestamp null, chưa có oracle round-trip timestamp đầy đủ; không lấy POST 2xx làm chứng minh mọi format | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-03; Q-04 |
| UR-01;UR-07 / BR-07 / AC-07 | POST/PATCH + GET /items/qa_articles[/id] — Editor | Phân vùng JSON/null + round-trip / INV-03;INV-04 | Có payload JSON/null, chưa so metadata trước/sau độc lập; chưa phủ các kiểu JSON | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-03; Q-05 |
| UR-01;UR-05 / BR-08 / AC-08 | POST/PATCH + GET fields=internal_notes /items/qa_articles[/id] — Editor | Round-trip + bảng quyền / INV-03;INV-04 | Payload có notes và policy cho phép; chưa có test Editor round-trip/null notes trực tiếp | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-03; Không có Q riêng |
| UR-01;UR-02;UR-07 / BR-09 / AC-09 | POST/PATCH + GET /items/qa_articles[/id] — Editor | Phân vùng ID/null + relation / INV-04;INV-08 | Category ID hợp lệ đọc lại, null sau SET NULL; invalid ID/nested/reference change chưa phủ | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-04; Q-05 |
| UR-02 / BR-10 / AC-10 | DELETE /items/qa_categories/{id}; GET /items/qa_articles/{id} — Editor | State transition + invariant / INV-08;SMOKE:check_relation_nullification | Article vẫn GET được với category=null; chưa so toàn bộ field còn lại | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222250Z-1431](../../artifacts/runs/20261012T222250Z-1431/metadata.json); **PARTIAL_EVIDENCE** | GAP-04; Không có Q riêng |
| UR-01;UR-02 / BR-11 / AC-11 | 10 operation CRUD đã chốt trên /items/qa_articles và /items/qa_categories — Editor | Positive operation acceptance / INV-04;S1 | Positive input có dữ liệu động và read-back cho 5 operation mỗi collection; không suy phủ mọi input | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **HISTORICAL_SAMPLE** | GAP-01;GAP-02;GAP-04;GAP-05; Không có Q riêng |
| UR-01 / BR-12 / AC-12 | PATCH + GET /items/qa_articles/{id} — Editor | Stateful invariant / S1;INV-03;INV-04 | Score đổi; title/category được so, chưa so mọi field nghiệp vụ không gửi | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-05;GAP-13; Q-03 |
| UR-01;UR-02 / BR-13 / AC-13 | DELETE + GET detail hai collection — Editor | State transition + negative oracle / S1;INV-03;INV-04 | GET không trả bản ghi sau DELETE có mẫu; nhánh non-2xx chưa loại trừ 5xx đầy đủ | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-07; Q-06 |
| UR-04 / BR-14 / AC-14 | GET /items/qa_categories; GET /items/qa_categories/{id} — Reader | Bảng quyền + positive acceptance / Chưa có test trực tiếp | Policy cấu hình read; schema/seed không thay functional read bằng Reader | Chỉ có nguồn cấu hình; chưa có functional evidence trực tiếp; **CONFIG_ONLY** | GAP-06; Không có Q riêng |
| UR-04 / BR-15 / AC-15 | GET /items/qa_articles; GET /items/qa_articles/{id} — Reader | Bảng quyết định row policy / S4;INV-10;SMOKE:reader_unfiltered_list | Smoke không filter kiểm sáu published; INV-10 filtered set; S4 draft detail bị nhiễu do internal_notes | [20261012T222250Z-1431](../../artifacts/runs/20261012T222250Z-1431/metadata.json); [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-06;GAP-14; Q-06 |
| UR-05 / BR-16 / AC-16 | GET list/detail + fields=internal_notes /items/qa_articles — Reader | Bảng quyết định field policy / S5;INV-10 | Published precondition rồi field cấm bị chặn/loại; chưa phủ mọi projection/nested; negative oracle còn rộng | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-07;GAP-09; Q-06 |
| UR-06 / BR-17 / AC-17 | POST/PATCH/DELETE hai collection — Reader | Bảng quyền + read-back / S6;INV-11 | PATCH article bị từ chối và read-back subset bằng Editor; các thao tác khác chưa có bằng chứng trực tiếp | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-05;GAP-06;GAP-07; Q-06 |
| UR-06 / BR-18 / AC-18 | GET list/detail; POST/PATCH/DELETE hai collection — Anonymous | Bảng quyền + negative acceptance / INV-02 | GET list hai collection bị từ chối; chưa kiểm mọi detail/write và nguyên nhân từ chối | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-06;GAP-07; Q-06 |
| UR-08 / BR-19 / AC-19 | GET /users/me — Invalid token | Phân vùng token + negative acceptance / INV-01 | Token sai trả 401 trong mẫu lịch sử; assertion non-2xx chưa loại trừ mọi 5xx | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-07;GAP-12; Q-06 |
| UR-03 / BR-20 / AC-20 | GET /items/qa_articles?filter[status][_eq]=published — Editor;Reader | Fixture oracle + phân vùng filter / S2;INV-05;INV-10 | S2 đối chiếu fixture map published; INV-05 còn lấy status/title từ GET nền | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-08; Q-07 |
| UR-03 / BR-21 / AC-21 | GET /items/qa_articles?sort=title,id&limit/offset/page — Editor | Fixture oracle + biên/phân trang / S3;INV-05 | S3 consistency từ full sorted list; INV-05 tính sort trên giá trị GET nền; có page=2/offset=3 | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-08; Q-07 |
| UR-03;UR-05 / BR-22 / AC-22 | GET /items/qa_articles?fields=... — Editor;Reader | Projection + bảng quyền / INV-05;S5;INV-10 | Đã kiểm một số field ngoài projection/cấm; chưa assert đủ mọi field requested trên mọi case | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-08;GAP-09; Q-07 |
| UR-03 / BR-23 / AC-23 | GET /items/qa_articles?search=spéciale — Editor | Fixture oracle + Unicode/search / INV-05 | Một kết quả mẫu; expected tính từ title GET nền, không suy mọi search/case/diacritics | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); **PARTIAL_EVIDENCE** | GAP-08; Q-07 |
| UR-01;UR-06;UR-07 / BR-24 / AC-24 | Rejected POST/PATCH/DELETE + read-back/row lookup — Editor invalid input;Reader;Anonymous | Invariant dữ liệu trước/sau / S6;INV-09;INV-11 | Combined invalid POST không tạo row, Reader PATCH subset không đổi; chưa phủ toàn bộ write matrix | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T222311Z-1412](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json); **PARTIAL_EVIDENCE** | GAP-02;GAP-05;GAP-06;GAP-07; Q-06 |
| UR-09 / BR-25 / AC-25 | GET /items/qa_articles?fields=&aggregate={...} — Editor | Robustness + control/replay / INV-06;REPLAY:aggregate-query-robustness | Unknown-function-shape 500; empty/count controls 200; giữ assertion không 5xx | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T185942Z-1219](../../artifacts/runs/20261012T185942Z-1219/invariant-report.json); **FAIL_CANDIDATE** | GAP-15; Q-06 |
| UR-09 / BR-26 / AC-26 | 10 CRUD operation + query/export/POST object-array theo schema — Editor;actor schema tương ứng | Schema-based/fuzzing + contract checks / INV-07;RAW/GUIDED;REPLAY:contract-schema-candidates | Status/content/schema đối chiếu snapshot; bốn biểu hiện contract candidate; không coi là bốn product defect | [20261012T185934Z-1453](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json); [20261012T185950Z-1994](../../artifacts/runs/20261012T185950Z-1994/invariant-report.json); [20261012T185958Z-355](../../artifacts/runs/20261012T185958Z-355/campaign-index.json); [20261012T190350Z-1047](../../artifacts/runs/20261012T190350Z-1047/campaign-index.json); **FAIL_CANDIDATE** | GAP-10; Q-03;Q-04;Q-05;Q-06 |

### Truy vết yêu cầu kỹ thuật của người chạy lab (UR-10)

| Yêu cầu | Nguồn/kiểm chứng | Bằng chứng hiện có | Việc tiếp theo |
|---|---|---|---|
| TR-01 - Môi trường cô lập, actor đúng, ID động | lab.sh, fixture map, preflight và request test | [Phase 0](00-hien-trang-va-baseline.md), INV-03/04 | GAP-11; không suy runtime healthy ngày 18/10 |
| TR-02 - Pin/provenance/raw bất biến | Manifest, metadata/hash/diff | [Evidence index](00-evidence-index.csv), [schema inventory](00-schema-inventory.json) | GAP-10/11; ghi giới hạn dirty tree |
| TR-03 - Snapshot/restore và dừng khi setup/restore lỗi | campaign guard và summary từng seed | [Campaign index](00-campaign-index.csv) | GAP-11; kiểm chứng tích hợp khi sửa harness |
| TR-04 - Replay đủ precondition/chain | replay report và ID mapping | [Replay cases](../replay-cases.md); Phase 0 có single-request replay | GAP-11; không gán full-chain khi chỉ replay request cuối |
| TR-05 - Bảo vệ secret/không bypass license | Quy tắc lab, config riêng, redaction/gói evidence | [Phụ thuộc và giới hạn](00-quyet-dinh-va-phu-thuoc.md) | Rà soát gói chia sẻ thật; không đọc secret để viết đặc tả |
| TR-06 - Chạy lại và bàn giao trung thực | README, dependency, report/exit và dựng mới | [README](../../README.md), Phase 0 và TR-01 đến TR-05 | GAP-11; Phase 4/9 xử lý helper ngoài repo và khả năng dựng mới |

### Ánh xạ invariant trong tài liệu với case_id thực tế

| Mã giữ nguyên | case_id trong report |
|---|---|
| INV-01 | auth-invalid-token |
| INV-02 | anonymous-denied |
| INV-03 | editor-crud |
| INV-04 | positive-operations |
| INV-05 | query-fixture |
| INV-06 | aggregate-query-robustness |
| INV-07 | contract-schema-candidates |
| INV-08 | relation-nullification |
| INV-09 | invalid-field-rejection |
| INV-10 | reader-visibility |
| INV-11 | reader-write |

Không cộng số dòng UR/BR/test/replay để tính số testcase hoặc defect. Việc mọi BR có đường truy vết chỉ chứng minh tài liệu không bỏ trống đường kiểm chứng, không chứng minh mọi lớp dữ liệu/operation đã được thực thi.

### Bổ sung khi thực hiện Phase 2

[Ma trận BR → OpenAPI → generator → oracle](02-ma-tran-rang-buoc.md), [CSV](02-ma-tran-rang-buoc.csv) giữ đủ 26 BR và cùng UR/AC/test/GAP/Q. [Danh mục case sinh](02-case-sinh-dai-dien.md) nối đến request/check/schema/hash/seed thật; [review Phase 2](02-danh-gia-openapi-va-sinh-test.md) ghi rõ phần nào còn cần triển khai Phase 3–4. Đây là truy vết thiết kế bổ sung, không nâng trạng thái evidence lịch sử.

### Bổ sung khi thực hiện Phase 3

[Truy vết BR → case có chủ đích](03-traceability.csv) giữ đủ 26 BR, cùng UR/AC/Q/GAP và test hiện có. [Thiết kế Phase 3](03-thiet-ke-test-va-coverage.md), [catalog](03-test-case-catalog.md) và [tiêu chí kết thúc](03-tieu-chi-ket-thuc.md) bổ sung precondition/input/oracle/cleanup/ưu tiên và mẫu số coverage trước chạy. Các case mới thiết kế đều NOT_RUN; không gán kết quả lịch sử sang mã P3 hoặc nâng coverage thực thi từ số dòng thiết kế.
