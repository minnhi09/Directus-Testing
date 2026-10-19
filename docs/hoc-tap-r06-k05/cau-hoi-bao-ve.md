# Bộ câu hỏi bảo vệ và khung trả lời

Hãy trả lời bằng bằng chứng của repository, không bịa thời gian, máy thứ hai, review hoặc defect. Phần “gợi ý” là các ý bắt buộc; câu trả lời thực tế nên trích file/run ID.

## Nhóm A — Phạm vi và mục tiêu

### 1. Đề tài R06 + K05 là gì?

R06 là hệ thống/API baseline Directus; K05 là schema-based API testing/fuzzing bằng Schemathesis. Trọng tâm là schema conformance, invariant nghiệp vụ, phân quyền và tái lập failure.

### 2. Ngoài phạm vi những gì?

GraphQL, WebSocket, frontend automation, load testing, nhiều DB đối chứng, Redis/S3/email và quét API quản trị không thuộc campaign chính.

### 3. Vì sao dùng Directus thay vì tự viết API?

Directus cung cấp API, auth, policy, OpenAPI và database integration; đồ án tập trung thiết kế harness/kiểm thử, không sửa upstream để tạo hành vi thuận lợi.

## Nhóm B — Dữ liệu và quyền

### 4. Fixture gồm những gì?

3 category, 12 article, chia 6 draft/6 published, phân bố theo category, có Unicode và nullable. ID tự sinh nên test dùng fixture map.

### 5. Reader khác Editor thế nào?

Editor CRUD hai collection trong phạm vi cấp; Reader đọc category và article published, không thấy `internal_notes`, không ghi; anonymous không truy cập hai collection.

### 6. Tại sao phải kiểm quyền qua API?

UI có thể ẩn nút nhưng không bảo vệ endpoint. Evidence phải là request/response với actor thật và side-effect oracle.

### 7. Vì sao Reader write cần read-back?

Status bị từ chối chưa chứng minh không có side effect. Editor read-back so sánh snapshot trước/sau.

## Nhóm C — OpenAPI và Schemathesis

### 8. Vì sao export schema theo actor?

Operation/field có thể bị lọc theo policy; schema admin không đại diện Reader/anonymous. Inventory đã xác minh `14/14/6/0`.

### 9. Campaign chính có bao nhiêu operation?

10 method–path: GET/POST list và GET/PATCH/DELETE detail cho hai collection. Không nhầm với 14 operation trong export.

### 10. Raw và guided khác nhau?

Raw giữ contract gốc; guided dùng overlay với ID/body/query guidance. Phải lưu raw bất biến, diff/hash và báo kết quả riêng.

### 11. Schemathesis kiểm gì?

Sinh request theo schema, chạy example/coverage/fuzzing/stateful tùy profile và check status, content type, response schema, 5xx cùng các check negative/positive phù hợp.

### 12. Seed có đảm bảo tái lập tuyệt đối không?

Không. Cần cùng schema hash, fixture state, image/dependency, actor/policy, budget, thứ tự và harness SHA.

### 13. `max-examples` nghĩa gì?

Giới hạn examples theo operation/strategy, không phải tổng request toàn campaign.

## Nhóm D — Oracle và failure

### 14. Schema coverage có phải code coverage không?

Không. Schema coverage nói operation/example đã được khám phá; không biết line/branch coverage của mã Directus.

### 15. Một check failure có phải một bug không?

Không. Nhiều check có thể cùng một root cause; cần grouping, shrink, replay và triage.

### 16. HTTP 500 có luôn là product defect?

Không. Có thể do input ngoài contract, schema gap, harness/fixture hoặc environment. Aggregate unknown shape hiện là candidate cần điều tra.

### 17. Các nhóm classification là gì?

Product defect; schema/contract gap; harness/fixture; environment; unresolved/chưa kết luận.

### 18. Vì sao không sửa expected để test pass?

Expected phải xuất phát từ yêu cầu và baseline đã xác minh. Sửa theo output là che failure và phá tính trung thực.

## Nhóm E — Tái lập và báo cáo

### 19. Artifact tối thiểu phải có gì?

Run ID, harness SHA, image/version/digest, fixture version/map, actor/profile, schema hash, seed/budget, timestamp/duration/status, log/report, request/response đã redaction và classification.

### 20. Stateful replay khác final-request replay thế nào?

Stateful replay dựng parent transitions và dependency; final-request chỉ gửi interaction cuối. Nếu parent artifact thiếu, phải ghi scope/limitation, không gọi full replay.

### 21. Restore pass có nghĩa gì?

Fixture đã được khôi phục theo snapshot ở mức restore oracle; không xóa hoặc phủ nhận failure trong campaign.

### 22. Tại sao report S6 từng sai?

Status PATCH bị biến read-back ghi đè. Harness đã lưu `denied_status` trước read-back và chạy lại evidence; đây là bài học về kiểm tra chính harness.

### 23. Trạng thái thực tế hiện tại là gì?

Scenario final đạt S1–S6; schema export đạt; invariants còn `9 passed/2 failed/0 blocked`; raw/guided chưa PASS toàn bộ; chưa xác nhận product defect cuối cùng.

### 24. Có thể nói đã đạt full coverage không?

Không. Có 10 operation trong scope và metrics tương ứng, nhưng coverage phải dựa trên run thực tế; timeout/failure/incomplete phải giữ nguyên trong kết luận.

### 25. Nếu được hỏi về review chéo/máy thứ hai?

Chỉ nói điều có evidence. Trạng thái hiện tại không có bằng chứng peer review hoặc chạy trên máy thứ hai; không tự tuyên bố đã có.

## Công thức trả lời an toàn

```text
Tôi kiểm tra [thuộc tính] bằng [actor/request/oracle].
Precondition là [fixture/schema/service].
Evidence ở [run_id/file].
Kết quả quan sát là [pass/fail/count].
Giới hạn là [failure/incomplete/không có bằng chứng].
Vì vậy tôi kết luận [mức chắc chắn], chưa kết luận [điều chưa đủ dữ liệu].
```

