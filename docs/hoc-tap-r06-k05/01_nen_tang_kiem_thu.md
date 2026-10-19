# Bài 1 — Nền tảng tư duy kiểm thử

## 1.1. Kiểm thử là gì?

Kiểm thử là hoạt động thu thập bằng chứng để đánh giá một hệ thống có phù hợp với yêu cầu và có hành xử an toàn trong các tình huống quan tâm hay không. Một test tốt không chỉ nói “gọi API và xem có `200`”; nó phải trả lời được:

- Đang kiểm tra thuộc tính nào?
- Trước khi chạy cần điều kiện gì?
- Input và actor nào được dùng?
- Kết quả nào là chấp nhận được?
- Dữ liệu thay đổi ra sao và phải dọn thế nào?
- Bằng chứng nằm ở đâu?

Trong dự án này, Schemathesis giúp tạo nhiều request theo schema, còn scenario/invariant giúp kiểm tra ý nghĩa nghiệp vụ mà schema không thể mô tả đầy đủ.

## 1.2. Verification và validation

- **Verification**: “Chúng ta xây đúng theo đặc tả chưa?” Ví dụ response có đúng OpenAPI, content type và status được mô tả không?
- **Validation**: “Chúng ta xây đúng thứ người dùng cần chưa?” Ví dụ Reader không nhìn thấy bài draft và `internal_notes`, dù response vẫn có thể hợp JSON.

Schema conformance thiên về verification. Quyền, tính toàn vẹn dữ liệu và invariant thiên về validation. Đồ án cần cả hai.

## 1.3. Các mức và loại kiểm thử trong lab

| Mức/loại | Câu hỏi | Ví dụ trong R06/K05 |
|---|---|---|
| Smoke | Dịch vụ có sống và đường đi cơ bản có hoạt động không? | health, login, đọc fixture |
| Functional/API | Endpoint có thực hiện đúng chức năng không? | Editor CRUD article |
| Contract/schema | Request/response có phù hợp OpenAPI không? | status, content type, response schema |
| Authorization | Actor có đúng quyền không? | Reader PATCH bị từ chối |
| Negative | Input hoặc actor không hợp lệ có bị xử lý an toàn không? | token sai, score ngoài miền |
| Regression | Lỗi đã sửa có tái xuất hiện không? | replay case từ artifact |
| Property/invariant | Quan hệ đúng vẫn giữ sau nhiều input/chuỗi không? | PATCH không làm mất field khác |

Đừng nhầm **load testing** với K05. Dự án có giới hạn tốc độ và budget để bảo vệ lab; mục tiêu là schema-based API testing/fuzzing, không đo năng lực chịu tải.

## 1.4. Test case và oracle

Một test case tối thiểu nên có:

| Trường | Ý nghĩa |
|---|---|
| ID | Tên ổn định, ví dụ `S6` |
| Mục tiêu | Thuộc tính muốn chứng minh |
| Precondition | Dữ liệu, actor, schema và service cần có |
| Input/steps | Request hoặc chuỗi request |
| Expected | Điều kiện chấp nhận, không chỉ một status nếu chưa có căn cứ |
| Oracle | Cách quyết định pass/fail: status, body, DB read-back, hash |
| Cleanup | Khôi phục hoặc xóa dữ liệu tạo tạm |
| Evidence | `run_id`, report, log, response đã làm sạch |

**Oracle** là quy tắc quyết định kết quả. Ví dụ S6 không chỉ có oracle “PATCH phải là `403`”; nó còn có oracle “Editor đọc lại phải cho thấy row không đổi”. Nếu chỉ kiểm tra status, một implementation có thể trả `403` nhưng vẫn âm thầm sửa dữ liệu.

## 1.5. Positive, negative và acceptance

- **Positive test**: input hợp lệ và actor có quyền; kỳ vọng thao tác thành công.
- **Negative test**: input, token hoặc quyền không phù hợp; kỳ vọng request bị từ chối hoặc được xử lý theo semantics đã xác minh.
- **Acceptance test**: kiểm tra một yêu cầu có ý nghĩa với người dùng, thường gồm cả side effect.

Không tự gán mọi lỗi quyền thành `401` hoặc mọi ID không tồn tại thành `404`. `401` thường liên quan xác thực; `403` thường liên quan đã xác thực nhưng không được phép. Tuy vậy, oracle cuối cùng phải dựa trên baseline Directus đã pin và evidence, không dựa vào trí nhớ.

## 1.6. Phân hoạch tương đương và giá trị biên

Với `score` là số nguyên từ `0` đến `5`:

| Nhóm | Giá trị đại diện | Mục đích |
|---|---:|---|
| Hợp lệ thấp | `0` | Biên dưới hợp lệ |
| Hợp lệ giữa | `3` | Giá trị thông thường |
| Hợp lệ cao | `5` | Biên trên hợp lệ |
| Không hợp lệ thấp | `-1` | Ngoài miền dưới |
| Không hợp lệ cao | `6` | Ngoài miền trên |
| Sai kiểu | `"3"`, `3.5`, object | Kiểm tra coercion/validation |

Với `title` tối đa 120 ký tự, nên có ranh giới rỗng, 1, 120 và 121 ký tự. Với `status`, nhóm hợp lệ là `draft/published`, nhóm không hợp lệ là chuỗi khác, null nếu field bắt buộc, hoặc kiểu không phải chuỗi. Với `published_at`, cần phân biệt `null`, timestamp hợp lệ và chuỗi timestamp không hợp lệ.

Đây là thiết kế input. Expected cụ thể vẫn phải đối chiếu schema, Directus validation và kết quả baseline.

## 1.7. Bảy nguyên tắc nên nhớ

1. Test cho thấy có lỗi, không chứng minh tuyệt đối không có lỗi.
2. Không thể kiểm thử toàn bộ mọi input; cần ưu tiên rủi ro và phân hoạch.
3. Test lặp mãi cùng một input sẽ giảm khả năng tìm lỗi mới.
4. Lỗi thường tập trung ở một số vùng: quyền, biên, chuyển trạng thái, tích hợp.
5. Không có lỗi tìm thấy không có nghĩa hệ thống phù hợp yêu cầu.
6. Test phụ thuộc bối cảnh: API CRUD, database và quyền cần oracle khác nhau.
7. “Không có lỗi” chỉ có ý nghĩa khi yêu cầu và tiêu chí được xác định trước.

## 1.8. Áp dụng vào đồ án

Cho yêu cầu “Reader chỉ đọc bài published, không đọc `internal_notes`, không ghi dữ liệu”, hãy tách thành các assertion:

1. Reader login thành công.
2. Reader đọc list published thành công.
3. Draft không xuất hiện qua filter/list hoặc detail theo semantics baseline.
4. Projection có `internal_notes` không làm lộ field đó.
5. PATCH của Reader bị từ chối theo status đã quan sát.
6. Editor đọc lại chứng minh dữ liệu mục tiêu không đổi.

Đây là cách một yêu cầu quyền trở thành testable oracle. Một file policy hoặc màn hình Studio tự nó chưa phải bằng chứng API.

## 1.9. Tự kiểm tra

- Vì sao `200` chưa đủ để kết luận create thành công?
- Vì sao cần read-back sau PATCH và sau request bị từ chối?
- `score=0` có phải input “falsy” nên loại bỏ không?
- Một response hợp JSON nhưng chứa `internal_notes` có thể vừa đúng content type vừa vi phạm yêu cầu nào?

Đọc tiếp: [Bài 2 — HTTP, REST và Directus](02_http_rest_directus.md).

