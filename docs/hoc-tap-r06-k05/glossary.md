# Thuật ngữ R06 + K05

| Thuật ngữ | Giải thích ngắn |
|---|---|
| API | Giao diện để chương trình giao tiếp với chương trình khác |
| REST | Phong cách API dùng resource, HTTP method và representation |
| Directus | Nền tảng cung cấp REST API, auth, policy và quản trị schema |
| Collection | Nhóm bản ghi, tương tự table theo cách nhìn nghiệp vụ |
| Fixture | Dữ liệu cố định dùng làm precondition/oracle |
| Actor | Danh tính chạy request: admin, editor, reader, anonymous |
| Policy/permission | Quy tắc actor được đọc/ghi operation/field nào |
| Authentication | Xác định actor là ai, thường bằng token |
| Authorization | Quyết định actor đã xác thực được làm gì |
| OpenAPI | Định dạng mô tả contract HTTP API |
| Schema | Cấu trúc/type/rule cho request hoặc response |
| Schema snapshot | Bản schema lưu tại một thời điểm để tái lập |
| Schema hash | SHA-256 nhận diện nội dung snapshot |
| Contract conformance | Mức response/request phù hợp OpenAPI |
| Schema-based testing | Sinh test dựa trên schema thay vì chỉ viết tay |
| Schemathesis | Công cụ schema-based API testing/fuzzing |
| K05 | Kỹ thuật schema-based API testing/fuzzing của đề tài |
| Operation | Cặp method–path có thể gọi trong OpenAPI |
| Allowlist | Danh sách operation được phép chạy trong campaign |
| Raw profile | Profile giữ contract gốc trong scope |
| Guided profile | Profile có overlay/example/ID để đi sâu nghiệp vụ |
| Overlay | File biến đổi riêng từ schema nguồn, có diff/hash/lý do |
| Seed | Hạt giống random để tái lập quá trình sinh |
| Budget | Giới hạn examples, thời gian, tốc độ, worker |
| Check | Assertion tự động như status/content type/response schema |
| Fuzzing | Sinh nhiều biến thể input theo strategy |
| Shrinking | Rút gọn input lỗi |
| Stateful testing | Dùng state/response request trước cho request sau |
| Scenario | Chuỗi bước kiểm tra một luồng nghiệp vụ |
| Invariant | Thuộc tính phải giữ sau thao tác/chuỗi |
| Oracle | Quy tắc quyết định pass/fail |
| Precondition | Điều kiện phải đạt trước test |
| Cleanup | Dọn dữ liệu tạm sau test |
| Read-back | Đọc lại bằng actor có quyền để kiểm side effect |
| Triage | Phân tích và phân loại finding/failure |
| Candidate | Tín hiệu cần điều tra, chưa phải defect xác minh |
| Reproducer | Hồ sơ request/sequence tối thiểu tái hiện finding |
| Replay | Chạy lại case đã lưu |
| Stateful replay | Replay cả chuỗi transition và parent state |
| Restore | Đưa fixture về snapshot trước campaign |
| Artifact | Log/report/metadata/schema/response của một run |
| Run ID | Định danh một lần thực thi |
| Harness | Mã điều phối và ghi bằng chứng kiểm thử |
| Coverage | Phạm vi operation/example/scenario đã chạy; không phải code coverage |
| Flaky | Kết quả không ổn định giữa các lần chạy cùng điều kiện |
| 401 | Thường liên quan thiếu/sai xác thực |
| 403 | Thường liên quan đã xác thực nhưng không được phép |
| 5xx | Lỗi phía server; cần triage, không tự động là product defect |

