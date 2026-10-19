# Phase 3 — Danh mục test có chủ đích v1

**Trạng thái:** tất cả là thiết kế, `execution_status=NOT_RUN`; không có kết quả API mới. [CSV đầy đủ](03-test-case-catalog.csv) và [JSON](tai-lieu-bo-tro/phase3-20261018/test-case-catalog.json) chứa UR/BR/AC, rủi ro, ưu tiên, actor, precondition, request, bước, expected response/state, cleanup, Q/GAP, nơi tích hợp và artifact dự kiến.

Đọc quy ước PC/oracle, template payload và tiêu chí kết thúc trong [báo cáo chính](03-thiet-ke-test-va-coverage.md) trước khi chuyển thành automation. `${...}` là biến phải resolve từ run/map/producer; không gửi literal placeholder lên API. `NOT_RUN` khác `OPEN`: một cái là thực thi, một cái là độ rõ expected.

`ASSERTABLE`: expected cốt lõi có nguồn, vẫn cần precondition. `CONDITIONAL`: expected có điều kiện cụ thể phải chứng minh trước. `OPEN`: chưa gán business PASS/FAIL; các check robustness/quyền/toàn vẹn đã rõ vẫn có verdict riêng. Lệnh `./lab.sh test invariants/scenarios` chỉ là entry tích hợp dự kiến; không có filter/lệnh chạy case P3 ở harness hiện tại.

## field-name (18 ca thiết kế)

### P3-NAME-POST-79 — name POST: 79

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-POST-80 — name POST: 80

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-POST-81 — name POST: 81

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-LENGTH — Mục tiêu: từ chối vì vượt max length; nhánh PG 22001→ValueTooLong là 400/VALUE_TOO_LONG nếu translator nhận diện.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Không truncate âm thầm; không tạo/sửa row. Nếu translator không ánh xạ và phát sinh 5xx: FAIL robustness, không đổi expected thành 500.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-POST-NULL — name POST: null

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":null}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-POST-EMPTY — name POST: empty

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":""}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-POST-BLANK — name POST: blank

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"   "}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-POST-NUMBER — name POST: number

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":123}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-POST-UNICODE — name POST: unicode

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"éééééééééééééééééééééééééééééééééééééééé"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-PATCH-79 — name PATCH: 79

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-PATCH-80 — name PATCH: 80

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-PATCH-81 — name PATCH: 81

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN"}}`.
- Oracle: O-LENGTH — Mục tiêu: từ chối vì vượt max length; nhánh PG 22001→ValueTooLong là 400/VALUE_TOO_LONG nếu translator nhận diện.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Không truncate âm thầm; không tạo/sửa row. Nếu translator không ánh xạ và phát sinh 5xx: FAIL robustness, không đổi expected thành 500.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-PATCH-NULL — name PATCH: null

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":null}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-NAME-PATCH-EMPTY — name PATCH: empty

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":""}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-PATCH-BLANK — name PATCH: blank

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"   "}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-PATCH-NUMBER — name PATCH: number

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":123}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-PATCH-UNICODE — name PATCH: unicode

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"éééééééééééééééééééééééééééééééééééééééé"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-POST-MISSING — POST thiếu name

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Thiếu field non-null/default=null/generated=false; không dùng empty/null thay omission.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-03; không dùng actual đầu tiên làm expected tự động.

### P3-NAME-PATCH-OMITTED — PATCH giữ name bị bỏ qua

BR-02; AC-02; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: title giữ nguyên khi PATCH score; category PATCH {} chưa chốt no-op semantics.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-03; không dùng actual đầu tiên làm expected tự động.

## field-title (18 ca thiết kế)

### P3-TITLE-POST-119 — title POST: 119

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-POST-120 — title POST: 120

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-POST-121 — title POST: 121

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-LENGTH — Mục tiêu: từ chối vì vượt max length; nhánh PG 22001→ValueTooLong là 400/VALUE_TOO_LONG nếu translator nhận diện.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Không truncate âm thầm; không tạo/sửa row. Nếu translator không ánh xạ và phát sinh 5xx: FAIL robustness, không đổi expected thành 500.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-POST-NULL — title POST: null

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":null,"status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-POST-EMPTY — title POST: empty

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-POST-BLANK — title POST: blank

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"   ","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-POST-NUMBER — title POST: number

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":123,"status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-POST-UNICODE — title POST: unicode

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"éééééééééééééééééééééééééééééééééééééééééééééééééééééééééééé","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-PATCH-119 — title PATCH: 119

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-PATCH-120 — title PATCH: 120

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-PATCH-121 — title PATCH: 121

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Giá trị biên ASCII. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-LENGTH — Mục tiêu: từ chối vì vượt max length; nhánh PG 22001→ValueTooLong là 400/VALUE_TOO_LONG nếu translator nhận diện.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Không truncate âm thầm; không tạo/sửa row. Nếu translator không ánh xạ và phát sinh 5xx: FAIL robustness, không đổi expected thành 500.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-PATCH-NULL — title PATCH: null

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":null,"status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-TITLE-PATCH-EMPTY — title PATCH: empty

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-PATCH-BLANK — title PATCH: blank

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"   ","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-PATCH-NUMBER — title PATCH: number

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":123,"status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-PATCH-UNICODE — title PATCH: unicode

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng; một yếu tố. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"éééééééééééééééééééééééééééééééééééééééééééééééééééééééééééé","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-01; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-POST-MISSING — POST thiếu title

BR-03; AC-03; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Thiếu field non-null/default=null/generated=false; không dùng empty/null thay omission.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-03; không dùng actual đầu tiên làm expected tự động.

### P3-TITLE-PATCH-OMITTED — PATCH giữ title bị bỏ qua

BR-03;BR-12; AC-03;AC-12; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":4}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: title giữ nguyên khi PATCH score; category PATCH {} chưa chốt no-op semantics.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## field-score (22 ca thiết kế)

### P3-SCORE-POST-MINUS1 — score POST -1

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":-1,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-0 — score POST 0

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":0,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-1 — score POST 1

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":1,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-4 — score POST 4

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":4,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-5 — score POST 5

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":5,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-6 — score POST 6

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":6,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-NULL — score POST null

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":null,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-POST-DECIMAL — score POST decimal

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":2.5,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-POST-STRING — score POST string

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":"3","published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-POST-BOOL — score POST bool

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":true,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-PATCH-MINUS1 — score PATCH -1

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":-1}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-0 — score PATCH 0

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":0}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-1 — score PATCH 1

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":1}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-4 — score PATCH 4

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":4}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-5 — score PATCH 5

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":5}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-6 — score PATCH 6

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":6}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-NULL — score PATCH null

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":null}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-SCORE-PATCH-DECIMAL — score PATCH decimal

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":2.5}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-PATCH-STRING — score PATCH string

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"3"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-PATCH-BOOL — score PATCH bool

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Giá trị biên; phân vùng kiểu/null. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":true}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-POST-MISSING — POST thiếu score

BR-05;BR-24; AC-05;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Theo input đã thay riêng một yếu tố; mọi field còn lại dùng payload hợp lệ/fixture spec.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-03; không dùng actual đầu tiên làm expected tự động.

### P3-SCORE-PATCH-OMITTED — PATCH giữ score bị bỏ qua

BR-05;BR-12; AC-05;AC-12; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"title":"Changed ${probe_key}"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: score của target giữ nguyên; chỉ title đổi.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## field-status (14 ca thiết kế)

### P3-STATUS-POST-DRAFT — status POST draft

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-POST-PUBLISHED — status POST published

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"published","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-POST-ARCHIVED — status POST archived

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"archived","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-POST-NULL — status POST null

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":null,"score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-POST-EMPTY — status POST empty

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-POST-BOOL — status POST bool

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":true,"score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-STATUS-PATCH-DRAFT — status PATCH draft

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":"draft"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-PATCH-PUBLISHED — status PATCH published

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":"published"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-PATCH-ARCHIVED — status PATCH archived

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":"archived"}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-PATCH-NULL — status PATCH null

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":null}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-PATCH-EMPTY — status PATCH empty

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":""}}`.
- Oracle: O-VALIDATION — 400 + errors[].extensions.code=FAILED_VALIDATION; field/path/type khớp rule đang thử khi có nguồn.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: POST không thêm ID; PATCH target và mọi field nghiệp vụ không đổi; không nhận 5xx/auth lỗi làm PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-STATUS-PATCH-BOOL — status PATCH bool

BR-04;BR-24; AC-04;AC-24; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"status":true}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ đổi status; published với published_at=null không tự là lỗi nghiệp vụ.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-02; không dùng actual đầu tiên làm expected tự động.

### P3-STATUS-POST-DEFAULT — POST bỏ status dùng default draft

BR-04; AC-04; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: DB schema overview default draft đã được xác minh trước; GET status=draft.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-03; không dùng actual đầu tiên làm expected tự động.

### P3-STATUS-PATCH-OMITTED — PATCH published giữ status khi chỉ sửa score

BR-04;BR-12; AC-04;AC-12; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":4}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Target tạm bắt đầu published; GET vẫn published, không reset draft.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## field-published_at (12 ca thiết kế)

### P3-PUBLISHED_AT-POST-NULL — published_at POST null

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-PUBLISHED_AT-PATCH-NULL — published_at PATCH null

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":null}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-PUBLISHED_AT-POST-UTC — published_at POST utc

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":"2026-10-01T08:00:00Z","metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-PATCH-UTC — published_at PATCH utc

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":"2026-10-01T08:00:00Z"}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-POST-OFFSET — published_at POST offset

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":"2026-10-01T15:00:00+07:00","metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-PATCH-OFFSET — published_at PATCH offset

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":"2026-10-01T15:00:00+07:00"}}`.
- Oracle: O-TIME — 2xx cho null/ISO chuẩn có offset; GET có null hoặc cùng instant theo parseISO/ISO source.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So instant cho giá trị giây nguyên; không so byte string, không tự áp published phải có timestamp.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-POST-EMPTY — published_at POST empty

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":"","metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROBUST — Có HTTP response không 5xx; control hợp lệ phải 2xx.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Business acceptance còn OPEN nếu chưa chốt input. 2xx không tự thành business PASS; ghi và kiểm dữ liệu phát sinh/cleanup.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-PATCH-EMPTY — published_at PATCH empty

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":""}}`.
- Oracle: O-ROBUST — Có HTTP response không 5xx; control hợp lệ phải 2xx.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Business acceptance còn OPEN nếu chưa chốt input. 2xx không tự thành business PASS; ghi và kiểm dữ liệu phát sinh/cleanup.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-POST-MALFORMED — published_at POST malformed

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":"not-a-date","metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROBUST — Có HTTP response không 5xx; control hợp lệ phải 2xx.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Business acceptance còn OPEN nếu chưa chốt input. 2xx không tự thành business PASS; ghi và kiểm dữ liệu phát sinh/cleanup.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-PATCH-MALFORMED — published_at PATCH malformed

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":"not-a-date"}}`.
- Oracle: O-ROBUST — Có HTTP response không 5xx; control hợp lệ phải 2xx.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Business acceptance còn OPEN nếu chưa chốt input. 2xx không tự thành business PASS; ghi và kiểm dữ liệu phát sinh/cleanup.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-POST-NO-OFFSET — published_at POST no-offset

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":"2026-10-01T08:00:00","metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

### P3-PUBLISHED_AT-PATCH-NO-OFFSET — published_at PATCH no-offset

BR-06; AC-06; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"published_at":"2026-10-01T08:00:00"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay published_at; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-04; không dùng actual đầu tiên làm expected tự động.

## field-metadata (12 ca thiết kế)

### P3-METADATA-POST-NULL — metadata POST null

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":null,"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-METADATA-PATCH-NULL — metadata PATCH null

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":null}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-METADATA-POST-OBJECT — metadata POST object

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"unicode":"Đà Nẵng 漢字","nested":{"ok":true}},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-METADATA-PATCH-OBJECT — metadata PATCH object

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":{"unicode":"Đà Nẵng 漢字","nested":{"ok":true}}}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-METADATA-POST-ARRAY — metadata POST array

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":[1,"Đà Nẵng",null],"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-PATCH-ARRAY — metadata PATCH array

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":[1,"Đà Nẵng",null]}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-POST-NUMBER — metadata POST number

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":3,"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-PATCH-NUMBER — metadata PATCH number

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":3}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-POST-STRING — metadata POST string

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":"JSON text","internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-PATCH-STRING — metadata PATCH string

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":"JSON text"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-POST-BOOL — metadata POST bool

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":true,"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-METADATA-PATCH-BOOL — metadata PATCH bool

BR-07; AC-07; P1; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"metadata":true}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay metadata; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

## field-internal_notes (4 ca thiết kế)

### P3-INTERNAL_NOTES-POST-NULL — internal_notes POST null

BR-08; AC-08; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":null,"category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay internal_notes; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-INTERNAL_NOTES-PATCH-NULL — internal_notes PATCH null

BR-08; AC-08; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"internal_notes":null}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay internal_notes; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-INTERNAL_NOTES-POST-TEXT — internal_notes POST text

BR-08; AC-08; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"  Ghi chú Unicode 漢字  ","category":"${fixture.category_alpha}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay internal_notes; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-INTERNAL_NOTES-PATCH-TEXT — internal_notes PATCH text

BR-08; AC-08; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"internal_notes":"  Ghi chú Unicode 漢字  "}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay internal_notes; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## field-category (10 ca thiết kế)

### P3-CATEGORY-POST-VALID — category POST valid

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_beta}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CATEGORY-PATCH-VALID — category PATCH valid

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"category":"${fixture.category_beta}"}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CATEGORY-POST-NULL — category POST null

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":null}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CATEGORY-PATCH-NULL — category PATCH null

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"category":null}}`.
- Oracle: O-ROUNDTRIP — 2xx và đọc lại đúng ý nghĩa JSON/null/text đã chọn.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: So deep equality cho JSON; không tự thêm key hoặc trim text; mọi field khác giữ nguyên khi PATCH.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CATEGORY-POST-INVALID — category POST invalid

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${absent_category_id}"}}`.
- Oracle: O-FK — 400 + INVALID_FOREIGN_KEY khi constraint FK được chạm với target/reference đúng tiền đề.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Không thêm/sửa article hoặc category, không orphan; so đủ field trước/sau.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-CATEGORY-PATCH-INVALID — category PATCH invalid

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"category":"${absent_category_id}"}}`.
- Oracle: O-FK — 400 + INVALID_FOREIGN_KEY khi constraint FK được chạm với target/reference đúng tiền đề.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Không thêm/sửa article hoặc category, không orphan; so đủ field trước/sau.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-CATEGORY-POST-NESTED-EXISTING — category POST nested-existing

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":{"id":"${fixture.category_beta}"}}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-CATEGORY-PATCH-NESTED-EXISTING — category PATCH nested-existing

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"category":{"id":"${fixture.category_beta}"}}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-CATEGORY-POST-NESTED-CREATE — category POST nested-create

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":{"name":"Nested ${probe_key}"}}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-CATEGORY-PATCH-NESTED-CREATE — category PATCH nested-create

BR-09; AC-09; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"category":{"name":"Nested ${probe_key}"}}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Chỉ thay category; invalid reference phải xác minh ID không tồn tại bằng map/control; JSON/time OPEN không áp assertion tự chọn.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

## positive-operations (10 ca thiết kế)

### P3-OP-01 — qa_articles list

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,score,published_at,metadata,category","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-OP-02 — qa_articles create

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-OP-03 — qa_articles detail

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-OP-04 — qa_articles update

BR-01;BR-11;BR-12; AC-01;AC-11;AC-12; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"},"body":{"score":4}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-OP-05 — qa_articles delete

BR-01;BR-11;BR-13; AC-01;AC-11;AC-13; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DELETE — 2xx; contract status theo raw ghi riêng nếu 204 khác 200.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET target sau xóa theo nhánh readOne 403/FORBIDDEN; list Editor xác minh ID không còn, article khác giữ nguyên.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-OP-06 — qa_categories list

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories","query":{"fields":"id,name","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-OP-07 — qa_categories create

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"Probe ${probe_key}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-OP-08 — qa_categories detail

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories/${target_id}","query":{"fields":"id,name"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-OP-09 — qa_categories update

BR-01;BR-11; AC-01;AC-11; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{"fields":"id,name"},"body":{"name":"Updated ${probe_key}"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-OP-10 — qa_categories delete

BR-01;BR-11;BR-13; AC-01;AC-11;AC-13; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_categories/${target_id}","query":{}}`.
- Oracle: O-DELETE — 2xx; contract status theo raw ghi riêng nếu 204 khác 200.
- Expected riêng: Positive input hợp BR; article create dùng draft, detail/update/delete target published/public fields, list mixed; category target tồn tại; ghi positive acceptance đúng operation.
- Dữ liệu sau request: GET target sau xóa theo nhánh readOne 403/FORBIDDEN; list Editor xác minh ID không còn, article khác giữ nguyên.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## authorization (59 ca thiết kế)

### P3-AUTHZ-DR-002 — editor qa_articles list mixed private

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,internal_notes","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-002: ALLOW; article state=mixed, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-003 — editor qa_articles list mixed wildcard

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"*","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-003: ALLOW; article state=mixed, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-004 — editor qa_articles list mixed nested-category

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,category.id,category.name","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-004: ALLOW; article state=mixed, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-005 — editor qa_articles detail draft public

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-005: ALLOW; article state=draft, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-006 — editor qa_articles detail draft private

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-006: ALLOW; article state=draft, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-007 — editor qa_articles detail draft wildcard

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-007: ALLOW; article state=draft, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-008 — editor qa_articles detail draft nested-category

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-008: ALLOW; article state=draft, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-010 — editor qa_articles detail published private

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-010: ALLOW; article state=published, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-011 — editor qa_articles detail published wildcard

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-011: ALLOW; article state=published, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-012 — editor qa_articles detail published nested-category

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-012: ALLOW; article state=published, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-014 — editor qa_articles create published business-input

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"published","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CREATE — 2xx + JSON data object có ID integer dương và field nghiệp vụ đúng.
- Expected riêng: Luật DR-014: ALLOW; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET bằng ID trả đúng payload đã định; ID lấy từ response, không yêu cầu liên tục.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-AUTHZ-DR-015 — editor qa_articles update draft business-input

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"${changed_score}"}}`.
- Oracle: O-PATCH — 2xx; với projection đầy đủ phải có data object đúng target.
- Expected riêng: Luật DR-015: ALLOW; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET đủ field nghiệp vụ: chỉ field gửi thay đổi; field không gửi bằng expected trước, không áp default lại.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-AUTHZ-DR-017 — editor qa_articles delete draft business-input

BR-11;BR-08;BR-22; AC-08;AC-11;AC-22; P0; actor `editor`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DELETE — 2xx; contract status theo raw ghi riêng nếu 204 khác 200.
- Expected riêng: Luật DR-017: ALLOW; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET target sau xóa theo nhánh readOne 403/FORBIDDEN; list Editor xác minh ID không còn, article khác giữ nguyên.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-AUTHZ-DR-024 — reader qa_articles list mixed public

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,score,published_at,metadata,category","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-024: ALLOW_PUBLISHED_NO_PRIVATE; article state=mixed, projection=public. Không article object nào được lộ internal_notes; field công khai đúng. List Reader exact set sáu published từ seed; nested category đúng tên/ID và không mở rộng article field kín..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-025 — reader qa_articles list mixed private

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,internal_notes","limit":-1}}`.
- Oracle: O-FIELD — Không lộ giá trị/private field; 403/FORBIDDEN hoặc 2xx loại field chỉ dùng sau khi đã có căn cứ cho từng dạng projection.
- Expected riêng: Luật DR-025: DENY_OR_REDACT_SOURCE_PENDING; article state=mixed, projection=private. Không article object nào được lộ internal_notes; field công khai đúng. List Reader exact set sáu published từ seed; nested category đúng tên/ID và không mở rộng article field kín..
- Dữ liệu sau request: Nếu 2xx: đúng published set/ID, không có internal_notes ở mọi article object; field công khai đúng. Không dùng OR hai nhánh tùy tiện để che thiếu nguồn.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-026 — reader qa_articles list mixed wildcard

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"*","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-026: ALLOW_PUBLISHED_NO_PRIVATE; article state=mixed, projection=wildcard. Không article object nào được lộ internal_notes; field công khai đúng. List Reader exact set sáu published từ seed; nested category đúng tên/ID và không mở rộng article field kín..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-027 — reader qa_articles list mixed nested-category

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,category.id,category.name","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-027: ALLOW_PUBLISHED_NO_PRIVATE; article state=mixed, projection=nested-category. Không article object nào được lộ internal_notes; field công khai đúng. List Reader exact set sáu published từ seed; nested category đúng tên/ID và không mở rộng article field kín..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-028 — reader qa_articles detail draft public

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-028: DENY_ROW; article state=draft, projection=public. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-029 — reader qa_articles detail draft private

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-029: DENY_COMBINED; article state=draft, projection=private. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-030 — reader qa_articles detail draft wildcard

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-030: DENY_ROW; article state=draft, projection=wildcard. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-031 — reader qa_articles detail draft nested-category

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-031: DENY_ROW; article state=draft, projection=nested-category. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-032 — reader qa_articles detail published public

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-032: ALLOW_PUBLISHED_NO_PRIVATE; article state=published, projection=public. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-033 — reader qa_articles detail published private

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-FIELD — Không lộ giá trị/private field; 403/FORBIDDEN hoặc 2xx loại field chỉ dùng sau khi đã có căn cứ cho từng dạng projection.
- Expected riêng: Luật DR-033: DENY_OR_REDACT_SOURCE_PENDING; article state=published, projection=private. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Nếu 2xx: đúng published set/ID, không có internal_notes ở mọi article object; field công khai đúng. Không dùng OR hai nhánh tùy tiện để che thiếu nguồn.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-034 — reader qa_articles detail published wildcard

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-034: ALLOW_PUBLISHED_NO_PRIVATE; article state=published, projection=wildcard. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-035 — reader qa_articles detail published nested-category

BR-15;BR-16;BR-22; AC-15;AC-16;AC-22; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-035: ALLOW_PUBLISHED_NO_PRIVATE; article state=published, projection=nested-category. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-036 — reader qa_articles create draft business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-036: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-037 — reader qa_articles create published business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"published","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-037: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-038 — reader qa_articles update draft business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"${changed_score}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-038: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-039 — reader qa_articles update published business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"${changed_score}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-039: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-040 — reader qa_articles delete draft business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-040: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-041 — reader qa_articles delete published business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-041: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-042 — reader qa_categories list not-applicable public

BR-14; AC-14; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories","query":{"fields":"id,title,status,score,published_at,metadata,category","limit":-1}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-042: ALLOW; article state=not-applicable, projection=public. Không article object nào được lộ internal_notes; field công khai đúng. List Reader exact set sáu published từ seed; nested category đúng tên/ID và không mở rộng article field kín..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-043 — reader qa_categories detail not-applicable public

BR-14; AC-14; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Luật DR-043: ALLOW; article state=not-applicable, projection=public. Không article object nào được lộ internal_notes; field công khai đúng. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTHZ-DR-044 — reader qa_categories create not-applicable business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"Probe ${probe_key}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-044: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-045 — reader qa_categories update not-applicable business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"Unauthorized ${probe_key}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-045: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-046 — reader qa_categories delete not-applicable business-input

BR-17;BR-24; AC-17;AC-24; P0; actor `reader`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_categories/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-046: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-047 — anonymous qa_articles list mixed public

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,score,published_at,metadata,category","limit":-1}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-047: DENY; article state=mixed, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-048 — anonymous qa_articles list mixed private

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,internal_notes","limit":-1}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-048: DENY; article state=mixed, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-049 — anonymous qa_articles list mixed wildcard

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"*","limit":-1}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-049: DENY; article state=mixed, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-050 — anonymous qa_articles list mixed nested-category

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,category.id,category.name","limit":-1}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-050: DENY; article state=mixed, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-051 — anonymous qa_articles detail draft public

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-051: DENY; article state=draft, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-052 — anonymous qa_articles detail draft private

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-052: DENY; article state=draft, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-053 — anonymous qa_articles detail draft wildcard

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-053: DENY; article state=draft, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-054 — anonymous qa_articles detail draft nested-category

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-054: DENY; article state=draft, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-055 — anonymous qa_articles detail published public

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-055: DENY; article state=published, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-056 — anonymous qa_articles detail published private

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,internal_notes"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-056: DENY; article state=published, projection=private. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-057 — anonymous qa_articles detail published wildcard

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"*"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-057: DENY; article state=published, projection=wildcard. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-058 — anonymous qa_articles detail published nested-category

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${target_id}","query":{"fields":"id,title,status,category.id,category.name"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-058: DENY; article state=published, projection=nested-category. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05;Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-059 — anonymous qa_articles create draft business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-059: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-060 — anonymous qa_articles create published business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"published","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-060: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-061 — anonymous qa_articles update draft business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"${changed_score}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-061: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-062 — anonymous qa_articles update published business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_articles/${target_id}","query":{},"body":{"score":"${changed_score}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-062: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-063 — anonymous qa_articles delete draft business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-063: DENY; article state=draft, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-064 — anonymous qa_articles delete published business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_articles/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-064: DENY; article state=published, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-065 — anonymous qa_categories list not-applicable public

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories","query":{"fields":"id,title,status,score,published_at,metadata,category","limit":-1}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-065: DENY; article state=not-applicable, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-066 — anonymous qa_categories detail not-applicable public

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_categories/${target_id}","query":{"fields":"id,title,status,score,published_at,metadata,category"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-066: DENY; article state=not-applicable, projection=public. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-067 — anonymous qa_categories create not-applicable business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"Probe ${probe_key}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-067: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-068 — anonymous qa_categories update not-applicable business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"PATCH","path":"/items/qa_categories/${target_id}","query":{},"body":{"name":"Unauthorized ${probe_key}"}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-068: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

### P3-AUTHZ-DR-069 — anonymous qa_categories delete not-applicable business-input

BR-18;BR-24; AC-18;AC-24; P0; actor `anonymous`; kỹ thuật: Bảng quyết định quyền. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-PERM;PC-MUT.
- Input: `{"method":"DELETE","path":"/items/qa_categories/${target_id}","query":{}}`.
- Oracle: O-DENY — 403 + FORBIDDEN theo permission/readOne branch đúng pin; phải có control actor/endpoint/input hợp lệ.
- Expected riêng: Luật DR-069: DENY; article state=not-applicable, projection=business-input. Target/state được tạo hoặc chọn đúng từ fixture; field công khai/data theo seed/payload, không lấy output target làm expected..
- Dữ liệu sau request: GET không data lab; POST không thêm ID; PATCH/DELETE không đổi target đủ field. Lỗi auth khác nhánh/setup phải BLOCKED/triage, không PASS.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

## authentication (2 ca thiết kế)

### P3-AUTH-CONTROL — Valid Editor users/me control

BR-19; AC-19; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE.
- Input: `{"method":"GET","path":"/users/me","query":{}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: 2xx; data.id và danh tính khớp actor binding của cấu hình; không lưu credential vào report.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-AUTH-INVALID — Token sai không được xác thực

BR-19; AC-19; P0; actor `invalid-token`; kỹ thuật: Phân vùng tương đương. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE; valid control cùng endpoint vừa thành công.
- Input: `{"method":"GET","path":"/users/me","query":{}}`.
- Oracle: O-AUTH — Token sai: 403/INVALID_TOKEN nếu đã xác định nhánh InvalidToken; valid control truy cập được users/me.
- Expected riêng: Token cố ý sai, không dùng token actor hợp lệ; 403/INVALID_TOKEN sau khi xác minh nhánh; không mở rộng fuzz auth subsystem.
- Dữ liệu sau request: Không suy hết auth subsystem đã được kiểm; network/5xx không là PASS.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-06; không dùng actual đầu tiên làm expected tự động.

## query (16 ca thiết kế)

### P3-QUERY-ALL — ALL

BR-20; AC-20; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,score","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Đúng 12 ID fixture, sort ID từ map; không extra row.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-DRAFT — DRAFT

BR-20; AC-20; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status","filter[status][_eq]":"draft","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Đúng sáu key _draft_ theo map.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PUBLISHED — PUBLISHED

BR-20; AC-20; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status","filter[status][_eq]":"published","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Đúng sáu key _published_ theo map.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-SORT-ID — SORT-ID

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Sắp ID numeric từ map.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-SORT-TITLE — SORT-TITLE

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":-1,"sort":"title,id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Thứ tự title từ spec Alpha01..Gamma04 sau khi xác minh collation; tie ID.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-SORT-SCORE — SORT-SCORE

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":-1,"sort":"-score,id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Sort theo (-score_spec, id_map), kiểm các nhóm tie 1/2/3/4/5.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-OFFSET3 — OFFSET3

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":3,"offset":3,"sort":"-score,id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Lát cắt [3:6] của oracle, không cắt GET nền.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PAGE2 — PAGE2

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":3,"page":2,"sort":"-score,id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Lát cắt [3:6] của cùng oracle; so thêm offset3 để kiểm consistency.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PRECEDENCE — PRECEDENCE

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,score","limit":3,"offset":0,"page":2,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: page ưu tiên offset theo parameter/source pin: oracle[3:6].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-PROJECTION2 — PROJECTION2

BR-22; AC-22; P0; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Mỗi row đủ đúng keys id,title; không thiếu field hoặc extra internal_notes.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PROJECTION4 — PROJECTION4

BR-22; AC-22; P0; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status,score","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Mỗi row đủ đúng bốn key và giá trị theo fixture.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-NESTED — NESTED

BR-09;BR-22; AC-09;AC-22; P0; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,category.id,category.name","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Expand một cấp category đúng fixture/category spec; không nested write.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-05; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-SEARCH-SPECIALE — SEARCH-SPECIALE

BR-23; AC-23; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","search":"spéciale","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Chỉ article_beta_published_2, xét cả field searchable có quyền, không chỉ title/projection.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-SEARCH-ABSENT — SEARCH-ABSENT

BR-23; AC-23; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","search":"R06K05AbsentTermZyx987","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Rỗng; term literal không wildcard và không xuất hiện trong field searchable của seed.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-SEARCH-BLANK — SEARCH-BLANK

BR-23; AC-23; P1; actor `editor`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","search":"   ","limit":-1,"sort":"id"}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: Sanitize có trim; giữ business expected OPEN tới khi xác định đủ nhánh.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-READER-FILTER-DRAFT — READER-FILTER-DRAFT

BR-15;BR-20; AC-15;AC-20; P0; actor `reader`; kỹ thuật: Phân vùng query; oracle fixture độc lập. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title,status","filter[status][_eq]":"draft","limit":-1,"sort":"id"}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Reader nhận data=[]; filter client không vượt row-policy.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

## query-boundary (10 ca thiết kế)

### P3-QUERY-LIMIT-MINUS2 — limit=-2

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":-2}}`.
- Oracle: O-QUERY-INVALID — 400 + INVALID_QUERY đúng nhánh validateQuery của pin.
- Expected riêng: 400/INVALID_QUERY; không đổi dữ liệu.
- Dữ liệu sau request: Dữ liệu không đổi; không coi mọi non-2xx là đúng.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-LIMIT-MINUS1 — limit=-1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":-1}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-LIMIT-0 — limit=0

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":0}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-LIMIT-1 — limit=1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":1}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-OFFSET-MINUS1 — offset=-1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"offset":-1}}`.
- Oracle: O-QUERY-INVALID — 400 + INVALID_QUERY đúng nhánh validateQuery của pin.
- Expected riêng: 400/INVALID_QUERY; không đổi dữ liệu.
- Dữ liệu sau request: Dữ liệu không đổi; không coi mọi non-2xx là đúng.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-OFFSET-0 — offset=0

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"offset":0}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-OFFSET-1 — offset=1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"offset":1}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PAGE-MINUS1 — page=-1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"page":-1}}`.
- Oracle: O-QUERY-INVALID — 400 + INVALID_QUERY đúng nhánh validateQuery của pin.
- Expected riêng: 400/INVALID_QUERY; không đổi dữ liệu.
- Dữ liệu sau request: Dữ liệu không đổi; không coi mọi non-2xx là đúng.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-QUERY-PAGE-0 — page=0

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **OPEN**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"page":0}}`.
- Oracle: O-OPEN — Business verdict giữ OPEN; kiểm riêng có response, không 5xx và bảo toàn dữ liệu theo BR áp dụng.
- Expected riêng: page=0 không tự giả định reject/first-page; cần resolve Q-07.
- Dữ liệu sau request: Ghi actual/snapshot/error để đối chiếu đúng source; không suy 2xx/4xx tự là bug hoặc tự làm expected.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-QUERY-PAGE-1 — page=1

BR-21; AC-21; P1; actor `editor`; kỹ thuật: Giá trị biên query. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","limit":3,"page":1}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: limit=-1: đủ12; limit=0:rỗng; limit=1:row đầu; offset=0/1:oracle[start:start+3]; page=1:oracle[0:3].
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

## stateful (3 ca thiết kế)

### P3-ST-01 — Tạo→đọc→sửa→xóa category; đủ ID động và absence

BR-01;BR-02;BR-11;BR-13; AC-01;AC-02;AC-11;AC-13; P0; actor `editor`; kỹ thuật: Chuyển trạng thái; invariant. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"CHAIN","path":"/items/qa_*","query":{}}`.
- Chuỗi: POST category object hợp lệ → C → GET C: name đúng input → PATCH C.name giá trị khác → GET C: name đổi đúng → DELETE C → GET C: 403/FORBIDDEN theo readOne → GET category list: C không còn.
- Oracle: O-CHAIN — Mỗi bước có response/check và parent/ID động, theo chuỗi ghi trong case.
- Expected riêng: Tạo→đọc→sửa→xóa category; đủ ID động và absence.
- Dữ liệu sau request: So toàn bộ field trước/sau; giữ article khi SET NULL; đủ cleanup/restore; không reset giữa bước.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-ST-02 — PATCH article giữ toàn field; xóa article trước category

BR-01;BR-09;BR-11;BR-12;BR-13; AC-01;AC-09;AC-11;AC-12;AC-13; P0; actor `editor`; kỹ thuật: Chuyển trạng thái; invariant. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"CHAIN","path":"/items/qa_*","query":{}}`.
- Chuỗi: POST category → C → POST article chuẩn với category=C → A → GET A: so đủ tám field nghiệp vụ theo payload, timestamp theo instant → PATCH A.score=4 → GET A: score=4, title/status/time/metadata/notes/category giữ → DELETE A → GET A: không còn tài nguyên theo readOne + list control → DELETE C.
- Oracle: O-CHAIN — Mỗi bước có response/check và parent/ID động, theo chuỗi ghi trong case.
- Expected riêng: PATCH article giữ toàn field; xóa article trước category.
- Dữ liệu sau request: So toàn bộ field trước/sau; giữ article khi SET NULL; đủ cleanup/restore; không reset giữa bước.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-ST-03 — SET NULL không cascade mất article; sáu bước vì thêm snapshot kiểm trước xóa

BR-09;BR-10;BR-24; AC-09;AC-10;AC-24; P0; actor `editor`; kỹ thuật: Chuyển trạng thái; invariant. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"CHAIN","path":"/items/qa_*","query":{}}`.
- Chuỗi: POST category → C → POST article tham chiếu C → A → GET A lưu expected đủ field từ payload → DELETE C → GET A: còn row, category=null, field khác bằng expected → DELETE A.
- Oracle: O-CHAIN — Mỗi bước có response/check và parent/ID động, theo chuỗi ghi trong case.
- Expected riêng: SET NULL không cascade mất article; sáu bước vì thêm snapshot kiểm trước xóa.
- Dữ liệu sau request: So toàn bộ field trước/sau; giữ article khi SET NULL; đủ cleanup/restore; không reset giữa bước.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

## robustness (3 ca thiết kế)

### P3-ROBUST-AGG-FOO — Aggregate FOO

BR-25; AC-25; P0; actor `editor`; kỹ thuật: Đoán lỗi từ finding; control tách riêng. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"","aggregate":{"foo":1}}}`.
- Oracle: O-ROBUST — Có HTTP response không 5xx; control hợp lệ phải 2xx.
- Expected riêng: Có HTTP response không 5xx; không khẳng định 2xx/4xx business khi semantics chưa chốt.
- Dữ liệu sau request: Business acceptance còn OPEN nếu chưa chốt input. 2xx không tự thành business PASS; ghi và kiểm dữ liệu phát sinh/cleanup.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-ROBUST-AGG-EMPTY — Aggregate EMPTY

BR-25; AC-25; P0; actor `editor`; kỹ thuật: Đoán lỗi từ finding; control tách riêng. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"","aggregate":{}}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Control aggregate={} với fields rỗng phải 2xx.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-ROBUST-AGG-COUNT — Aggregate COUNT

BR-25; AC-25; P0; actor `editor`; kỹ thuật: Đoán lỗi từ finding; control tách riêng. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"","aggregate":{"count":["id"]}}}`.
- Oracle: O-READ — 2xx + JSON data đúng ID/set/field đã định.
- Expected riêng: Control 2xx và count đúng12 sau PC-Q, so shape theo baseline; không đánh đồng response item schema.
- Dữ liệu sau request: Không đổi dữ liệu; ID/value expected từ seed spec + map mới hoặc producer.
- Cleanup: Không mutation; xác minh fixture không đổi.

## contract (8 ca thiết kế)

### P3-CONTRACT-QA_ARTICLES-OBJECT — qa_articles POST object

BR-11;BR-26; AC-11;AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Business: object trả data object và1ID; array hai object trả data array và2ID, đọc lại đúng input. Raw POST response data array phải ghi mismatch khi object, không sửa raw..
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CONTRACT-QA_ARTICLES-ARRAY — qa_articles POST array

BR-11;BR-26; AC-11;AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_articles","query":{},"body":[{"title":"Probe ${probe_key}","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"},{"title":"Probe ${probe_key} second","status":"draft","score":3,"published_at":null,"metadata":{"probe":"${probe_key}"},"internal_notes":"Private ${probe_key}","category":"${fixture.category_alpha}"}]}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Business: object trả data object và1ID; array hai object trả data array và2ID, đọc lại đúng input. Raw POST response data array phải ghi mismatch khi object, không sửa raw..
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CONTRACT-QA_CATEGORIES-OBJECT — qa_categories POST object

BR-11;BR-26; AC-11;AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":{"name":"Probe ${probe_key}"}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Business: object trả data object và1ID; array hai object trả data array và2ID, đọc lại đúng input. Raw POST response data array phải ghi mismatch khi object, không sửa raw..
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CONTRACT-QA_CATEGORIES-ARRAY — qa_categories POST array

BR-11;BR-26; AC-11;AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-MUT.
- Input: `{"method":"POST","path":"/items/qa_categories","query":{},"body":[{"name":"Probe ${probe_key}"},{"name":"Probe ${probe_key} second"}]}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Business: object trả data object và1ID; array hai object trả data array và2ID, đọc lại đúng input. Raw POST response data array phải ghi mismatch khi object, không sửa raw..
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: PC-CLEAN: so trạng thái trước cleanup; xóa row probe theo ID mới, article trước category; restore đúng snapshot nếu lỗi.

### P3-CONTRACT-EXPORT-CSV — Export csv

BR-26; AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","export":"csv","limit":3}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Giữ content type thực và contract verdict raw JSON riêng; response xuất đúng3row đầu theo oracle khi parse định dạng được.
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-CONTRACT-EXPORT-XML — Export xml

BR-26; AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","export":"xml","limit":3}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Giữ content type thực và contract verdict raw JSON riêng; response xuất đúng3row đầu theo oracle khi parse định dạng được.
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-CONTRACT-EXPORT-YAML — Export yaml

BR-26; AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"fields":"id,title","sort":"id","export":"yaml","limit":3}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Giữ content type thực và contract verdict raw JSON riêng; response xuất đúng3row đầu theo oracle khi parse định dạng được.
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-CONTRACT-PROJECTION — Projection title-only và required response

BR-22;BR-26; AC-22;AC-26; P0; actor `editor`; kỹ thuật: Phân vùng tương đương. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles/${fixture.article_alpha_published_1}","query":{"fields":"title"}}`.
- Oracle: O-CONTRACT — Đối chiếu đúng raw snapshot status/content/schema, giữ mismatch khi có.
- Expected riêng: Business: 2xx/data chỉ title đúng fixture; raw component required score có thể FAIL; lưu cả hai verdict.
- Dữ liệu sau request: Business/read-back ghi riêng; JSON contract success không thay full field/data presence assertion; không đổi raw/disable check.
- Cleanup: Không mutation; xác minh fixture không đổi.

## pairwise-reference (36 ca thiết kế)

### P3-PW-01 — Query model 1

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-02 — Query model 2

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-03 — Query model 3

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-04 — Query model 4

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-05 — Query model 5

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-06 — Query model 6

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-07 — Query model 7

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-08 — Query model 8

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-09 — Query model 9

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-10 — Query model 10

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-11 — Query model 11

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-12 — Query model 12

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-13 — Query model 13

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-14 — Query model 14

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-15 — Query model 15

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-16 — Query model 16

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-17 — Query model 17

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-18 — Query model 18

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-19 — Query model 19

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-20 — Query model 20

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-21 — Query model 21

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-22 — Query model 22

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-23 — Query model 23

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-24 — Query model 24

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"draft","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-25 — Query model 25

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-26 — Query model 26

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-27 — Query model 27

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-28 — Query model 28

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort id_map asc rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-29 — Query model 29

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-30 — Query model 30

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-31 — Query model 31

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-32 — Query model 32

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **CONDITIONAL**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"title,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; title_order_keys + id_map tie rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.
- Cần làm rõ: Q-07; không dùng actual đầu tiên làm expected tự động.

### P3-PW-33 — Query model 33

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-34 — Query model 34

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-35 — Query model 35

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","offset":3}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

### P3-PW-36 — Query model 36

BR-20;BR-21;BR-22; AC-20;AC-21;AC-22; P1; actor `editor`; kỹ thuật: Pairwise/exhaustive finite model. Expected: **ASSERTABLE**; thực thi: **NOT_RUN**.

- Tiền điều kiện: PC-BASE;PC-Q.
- Input: `{"method":"GET","path":"/items/qa_articles","query":{"sort":"-score,id","fields":"id,title,status,score","limit":3,"filter[status][_eq]":"published","page":2}}`.
- Oracle: O-QUERY — 2xx + data đúng thứ tự/set/lát cắt/projection từ fixture oracle.
- Expected riêng: Filter keys từ fixture; sort (-score_spec, id_map) rồi lấy [3:6]; projection đủ đúng fields; không sort lại expected bằng target response.
- Dữ liệu sau request: Không dùng sorted/filtered GET target làm expected; numeric ID từ map; sort title phải qua điều kiện collation.
- Cleanup: Không mutation; xác minh fixture không đổi.

