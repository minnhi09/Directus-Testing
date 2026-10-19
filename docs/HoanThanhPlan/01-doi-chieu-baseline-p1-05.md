# P1-05 - Chốt hướng đặc tả và đối chiếu source baseline

**Ngày:** 18/10/2026. **Quyết định đã nhận:** Người dùng chọn bám baseline Directus đã pin, không tự thêm quy tắc nghiệp vụ; chưa đủ căn cứ thì giữ câu hỏi mở.  
**Baseline source:** `4f77933bf9551cac6b289576078783e189b8f4e3`, kết hợp fixture/policy lab hiện có và PostgreSQL 16.  
**Phương pháp:** Đọc trực tiếp `git show <commit>:<path>`, không checkout/sửa Directus, không dùng source HEAD hiện tại thay bản pin, không chạy runtime hoặc cài dependency.

## 1. Quyết định áp dụng

| ID | Nội dung | Trạng thái |
|---|---|---|
| DEC-P1-01 | Dùng quy tắc/hành vi có nguồn của baseline và cấu hình lab đã có để xây expected | Người dùng đã chọn |
| DEC-P1-02 | Không tự thêm minLength, trim, cấm ép kiểu, workflow published-time hoặc schema JSON nghiệp vụ | Hệ quả của lựa chọn trên; không thay cấu hình |
| DEC-P1-03 | Tách business oracle, response contract và hành vi quan sát; gặp khác biệt thì giữ finding | Giữ nguyên nguyên tắc kiểm thử hiện có |
| DEC-P1-04 | Chi tiết phụ thuộc DB/driver/runtime hoặc thiếu nguồn vẫn OPEN; không xem lựa chọn baseline là xác nhận mọi expected | Người dùng đã nêu rõ trong lựa chọn |

Quyết định này giải quyết **hướng chọn yêu cầu**, không tự đóng bảy nhóm câu hỏi kỹ thuật. Không cần hỏi lại nhóm có muốn đặt quy tắc nghiệp vụ riêng trong các phase tiếp theo, trừ khi người dùng đổi hướng.

## 2. Nguồn được ghim và cách kiểm tra

Đã lưu bản sao chọn lọc 22 tệp đúng commit, nay được tập hợp tại `tai-lieu-bo-tro/phase1-20261018/baseline-source/` trong hồ sơ này; bản gốc tại `output/phase1-20261018/baseline-source/` được giữ để đối chiếu. [Manifest source](tai-lieu-bo-tro/phase1-20261018/baseline-source-manifest.json) ghi commit, Git blob, SHA-256 và đường dẫn lịch sử của từng tệp. Đây là tài liệu tham chiếu tĩnh, không phải bản build/runtime hoặc bản sao toàn repo Directus.

Các vị trí quan trọng:

- [process-payload.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/permissions/modules/process-payload/process-payload.ts), dòng 35-58, 61-81, 104-130: quyền field, required khi create, non-null, validation và payload trả về.
- [is-field-nullable.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/permissions/modules/process-payload/lib/is-field-nullable.ts), dòng 7-13: ngoại lệ cho field nullable/generated/generate special.
- [generate-joi.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/utils/shared/generate-joi.ts), dòng 279-280, 295-316, 323-329, 365-366, 383-389; [validate-payload.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/utils/shared/validate-payload.ts), dòng 57-64: luật enum/range/non-null/submitted và kết quả validation.
- [items.ts - service](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/services/items.ts), dòng 177-224, 259-263, 609-623, 797-849: đường create/update, chọn field cho SQL, readOne không có kết quả.
- [payload.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/services/payload.ts), dòng 215-280, 449-525: xử lý giá trị, JSON và timestamp.
- [items.ts - controller](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/controllers/items.ts), dòng 35-52: POST object/array và response tương ứng.
- [sanitize-query.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/utils/sanitize-query.ts), dòng 34-79, 144-173; [validate-query.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/utils/validate-query.ts), dòng 15-61: xử lý query trước validation.
- [search.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/database/run-ast/lib/apply-query/search.ts), dòng 23-35, 37-65, 78-108: chọn trường searchable, quyền và SQL tìm kiếm.

Các đoạn source cho phép suy luận có điều kiện. Chúng chưa chứng minh image đang chạy là bản build từ chính source này; giới hạn provenance image/source ở Phase 0 vẫn giữ nguyên.

## 3. Kết quả theo từng nhóm câu hỏi

### Q-01 - Chuỗi rỗng, khoảng trắng và Unicode

**Chốt được:** Cấu hình lab chỉ đặt non-null, độ dài tối đa và meta.required cho name/title; chưa có luật `_nempty`, trim hoặc minLength=1. Trong đường validation đã đọc, `_nnull` loại null và `_submitted` yêu cầu có field khi điều kiện create phù hợp; không đồng nghĩa một luật cấm chuỗi rỗng.

**Áp dụng:** Không viết expected "mọi title/name rỗng hoặc toàn khoảng trắng phải bị từ chối" chỉ từ chữ required. Không tự cắt khoảng trắng trước khi so read-back. Ca empty/blank vẫn có thể thiết kế để quan sát baseline, nhưng accepted không tự thành defect nghiệp vụ.

**Còn OPEN:** Kết quả end-to-end của từng input, cách DB/driver xử lý độ dài Unicode và chuẩn hóa; cần nguồn DB hoặc kiểm chứng baseline cụ thể. Chưa tuyên bố source review đã chứng minh mọi empty string chắc chắn trả 2xx.

### Q-02 - Ép kiểu và field thừa

**Chốt được:** Validation range dùng Joi number; enum status dùng Joi any.equal. `validatePayload` lấy lỗi từ Joi, còn `processPayload` trả payloadWithPresets, không lấy giá trị đã convert của Joi làm payload trả về. Vì vậy việc validation có thể convert để so sánh không chứng minh dữ liệu cuối cùng được chuyển kiểu theo cùng cách. ItemsService còn chọn các field trong schema trước khi đưa vào SQL.

**Áp dụng:** Không thêm chính sách "JSON string/number khác kiểu thì nhất định phải 400" khi chưa đủ nguồn. Không coi field thừa luôn phải bị từ chối; hành vi phụ thuộc quyền, validation và bước pick field. Miền dữ liệu lưu score vẫn theo integer 0-5 của lab; phân biệt hình thức request với giá trị persist/read-back.

**Còn OPEN:** Mỗi kiểu string/float/bool được nhận, đổi kiểu hay từ chối ra sao trên PostgreSQL/driver; response và error code tương ứng. Không dùng một ca name integer được nhận để khái quát mọi kiểu/field.

### Q-03 - Missing, null, default và POST/PATCH

**Chốt được từ source:**

1. Field không nullable chỉ được thêm `_submitted` khi `action === 'create'` và `field.defaultValue === null`, sau khi xét ngoại lệ generated/special.
2. Field không nullable vẫn có `_nnull`; gửi null không được coi giống omission.
3. Ở update, nhánh này không tự yêu cầu gửi mọi field non-null. ItemsService update chỉ đưa field có trong payload sau xử lý vào SQL.
4. Status trong lab có default draft. Nếu schema overview phản ánh đúng cấu hình đó, nó không thuộc nhánh bắt buộc submitted vì default null. Giá trị default khi insert còn cần đối chiếu schema DB hiện hành; source không tạo quy tắc áp default lại lên field bị bỏ qua khi PATCH.

**Áp dụng:** Tách case POST thiếu name/title/score, POST thiếu status, PATCH bỏ field, explicit null và empty. Không lấy required của OpenAPI dùng chung để kết luận PATCH phải gửi lại title/score. Expected PATCH giữ field không gửi có căn cứ source, không chỉ dựa test PASS.

**Còn OPEN:** Schema overview/DB runtime hiện tại có đúng default/nullability dự kiến không; các tổ hợp missing + preset/hook/special và error thực tế. Không tuyên bố mọi POST thiếu bất kỳ field nào đều cùng một lỗi.

### Q-04 - Timestamp

**Chốt được:** PostgreSQL dùng DateHelperDefault, kế thừa helper có `writeTimestamp = parseISO`; khi đọc timestamp, PayloadService có nhánh chuẩn hóa qua Date/toISOString. Null được xử lý riêng. Với value falsy, có đường bỏ qua xử lý ngày; không có bảo đảm tổng quát rằng mọi chuỗi sai format được chặn trước DB.

**Áp dụng:** So ý nghĩa thời điểm theo quy tắc có nguồn; không yêu cầu byte-equal chuỗi đầu vào/đầu ra hoặc tự thêm published bắt buộc có timestamp. Vẫn giữ mục tiêu robustness không 5xx; một input sai gây 5xx không được tính là negative PASS.

**Còn OPEN:** Tập format, timezone mặc định khi thiếu offset, precision và error cho từng input malformed/empty trong đúng runtime. Không suy trực tiếp mọi chuỗi rỗng sẽ đi tới cùng lỗi SQLSTATE.

Nguồn bổ trợ: [date/index.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/database/helpers/date/index.ts), [date/dialects/default.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/database/helpers/date/dialects/default.ts), [date/types.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/database/helpers/date/types.ts).

### Q-05 - JSON, relation và POST array

**Chốt được:** Không có validation schema JSON nghiệp vụ trong cấu hình metadata. PayloadService stringify object/array khi create/update; controller POST xử lý array qua createMany/readMany và object qua createOne/readOne, tạo response shape khác nhau.

**Áp dụng:** Không hạn chế metadata phải chứa object/key fixture. Contract response cho POST object phải được đối chiếu nhánh readOne, không áp array response một cách máy móc; raw schema mismatch vẫn giữ. Không thu hẹp generator object-only mà không ghi rõ phạm vi và lý do.

**Còn OPEN:** JSON scalar/string được lưu và đọc lại thế nào, nested relation permissions/transaction, array giới hạn lớn nhỏ/config. Source routing hỗ trợ array không chứng minh mọi array input hợp lệ hoặc đã được test.

### Q-06 - Status và error contract

**Chốt được theo nhánh source, không áp cho mọi lỗi:**

| Khi nhánh sau thực sự xảy ra | Error class / status từ source |
|---|---|
| ReadOne không có result | ForbiddenError / 403 |
| Collection/field permission bị từ chối qua ForbiddenError | 403 |
| Validation field/policy báo FailedValidationError | FAILED_VALIDATION / 400 |
| Query validation/sanitize báo InvalidQueryError | INVALID_QUERY / 400 |
| InvalidCredentialsError | 401 |
| InvalidTokenError | 403 |
| Error không được nhận diện/ánh xạ | Error handler có fallback 500, không được gọi là từ chối nghiệp vụ đúng |

**Áp dụng:** Không mặc định not-found là 404 hoặc mọi token sai là 401. Muốn assertion status/error cụ thể phải chứng minh request đi vào nhánh tương ứng và có precondition đúng. Mã 5xx hiện có vẫn là finding/candidate, không được đổi expected thành 500 chỉ vì baseline có nhánh fallback.

**Còn OPEN:** Nhánh thực tế của từng request/SQL error, đầy đủ error envelope/field/path và những trường hợp nhiều lỗi khác status. PostgreSQL error translator chỉ ánh xạ một tập SQLSTATE; không suy mọi lỗi DB là 400.

Nguồn: [forbidden.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/errors/src/errors/forbidden.ts), [invalid-query.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/errors/src/errors/invalid-query.ts), [failed-validation.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/validation/src/errors/failed-validation.ts), [invalid-credentials.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/errors/src/errors/invalid-credentials.ts), [invalid-token.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/packages/errors/src/errors/invalid-token.ts), [error-handler.ts](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/middleware/error-handler.ts), [postgres errors](tai-lieu-bo-tro/phase1-20261018/baseline-source/api/src/database/errors/dialects/postgres.ts).

### Q-07 - Search, sort và collation

**Chốt được:** Search lấy các field có searchable không false, không conceal, xét field permissions; không chỉ title. String/text được so bằng `LOWER(column) LIKE pattern`; field numeric/UUID có nhánh riêng khi input phù hợp. Sanitize query có xử lý trim search; chuỗi toàn khoảng trắng có nhánh khác chuỗi có nội dung.

**Áp dụng:** Ground truth của search phải xét các field baseline thực sự cho tìm và quyền actor, không chỉ field có trong projection. Với term spéciale của fixture hiện tại có thể vẫn chỉ có một title khớp; đó là trường hợp cụ thể, không phải định nghĩa API tìm theo title. Không thêm quy tắc accent-insensitive hoặc một thứ tự Unicode chung cho mọi DB.

**Còn OPEN:** Collation DB thực tế, mẫu wildcard, chuẩn hóa case/diacritics của dữ liệu ngoài mẫu, exact expected của các term mới và sort Unicode. Giữ khóa phụ ID, không dùng hai request cùng phụ thuộc một lỗi làm ground truth độc lập.

## 4. Cách cập nhật assertion ở phase sau

1. Dùng phần có source làm expected có điều kiện, ghi rõ precondition và nhánh xử lý.
2. Với phần OPEN, thu thập thêm nguồn DB/runtime và ghi observation riêng; không thêm business rule mới.
3. Giữ riêng business correctness và contract conformance. Runtime có thể phù hợp nhánh source nhưng raw OpenAPI vẫn thiếu response status/shape.
4. Nếu cần sửa assertion, làm ở Phase 3-4 với regression phù hợp; không sửa report lịch sử hay chuyển FAIL hiện có thành PASS bằng cập nhật đặc tả.

## 5. Trạng thái P1-05 sau lựa chọn của người dùng

**P1-05 hoàn thành ở mức đặc tả:** hướng baseline đã chốt, đối chiếu source đã thực hiện, phân biệt được từng lớp tình huống và ghi rõ expected/giới hạn. Tiêu chí Phase 1 cho phép câu hỏi chưa rõ được ghi mở. Chi tiết kỹ thuật chưa đủ căn cứ vẫn OPEN, được chuyển sang Phase 2–4; không phải yêu cầu người dùng nghĩ thêm quy tắc nghiệp vụ hoặc đã xác nhận các hành vi đó đúng.

Cập nhật trạng thái khi thực hiện [Phase 2](02-danh-gia-openapi-va-sinh-test.md), không thay nội dung source hoặc bằng chứng lịch sử. Chưa chạy lại API, chưa đổi baseline/policy/schema, chưa kết luận product defect mới.
