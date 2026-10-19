# 05 — Failure, candidate và root cause

## Quy tắc phân loại

Một check failure chỉ là quan sát. Để xác nhận product defect cần request/chuỗi, precondition, expected/actual, control phù hợp, log và phiên bản source/image. Các nhóm được dùng trong báo cáo là product candidate, contract/schema, harness/fixture, environment và unresolved. Một response có thể sinh nhiều check failure nhưng không tự thành nhiều defect.

## Findings deterministic

### Aggregate robustness — candidate chưa xác nhận

`aggregate-query-robustness` gửi ba biến thể đọc:

```text
aggregate={"foo":1}          -> HTTP 500
aggregate={}                  -> HTTP 200
aggregate={"count":["id"]}  -> HTTP 200
```

Đây là candidate robustness và có thể đồng thời là schema omission vì schema không ràng buộc đầy đủ object aggregate. Hai control 200 làm giảm khả năng lỗi toàn bộ API. Hiện chưa kết luận product defect: cần ghim đúng source/image, lấy log server sạch secret và đối chiếu xử lý aggregate trong query builder.

### Response/schema candidates

`contract-schema-candidates` ghi bốn candidate runtime/schema: POST shape, export content type/shape và DELETE 204 status. Case cố ý FAIL để bảo toàn khác biệt, cleanup probe đạt. Đây là lỗi contract/schema hoặc phạm vi response map cho tới khi xác minh spec generator và behavior Directus cùng revision.

## Campaign findings đã có artifact

Raw run `20261012T112746Z-20300` cho thấy cả ba seed đều test đủ 10 operation và kết thúc `max_time`, restore 0. Failure lặp lại nhiều nhất là `UndefinedStatusCode` cho 204/403, `UnsupportedMethodResponse` cho TRACE và một số `RejectedPositiveData`/`UndefinedContentType`. Guided run `20261012T122826Z-22781` bổ sung `ServerError`, `JsonSchemaError`, `AcceptedNegativeData` và stateful failures; seed 202 bị ngắt ở 645,046 giây nhưng report, coverage và restore đều có bằng chứng. Đây là check-level observation, không phải số defect.

Các nhóm cần phân biệt:

- `403` cho request fuzz chạm collection hệ thống hoặc permission là actor/precondition candidate, không tự là lỗi sản phẩm.
- `204` DELETE/PATCH nhưng schema chỉ khai báo 200 là response contract candidate.
- `400` với `meta`, `fields` rỗng/không hợp lệ là semantic validation hoặc generator positive-data candidate.
- TRACE trả 404 trong khi check mong đợi 405 là semantics của unsupported-method check ngoài mười operation chính.
- HTTP 500 với timestamp rỗng/aggregate lạ cần log server và control; giữ nhãn unresolved/candidate khi thiếu bằng chứng.
- Stateful replay chỉ gửi request cuối được ghi `reproduced_request_only`; parent mapping fail ghi `stateful_sequence_failed`.

Hai replay mới cung cấp bằng chứng tái hiện:

- `q40gXE` (`DELETE /items/qa_articles/1`) trả 204 đúng như source; check vẫn FAIL vì schema response map chỉ liệt kê 200/401/404. Replay `20261012T135615Z-28334` ghi `status=reproduced`, `actual_status=204`, `restore_exit_code=0`.
- `n2R7IY` (`POST /items/qa_articles`) trả 200 nhưng `data` là object trong khi schema yêu cầu array. Replay `20261012T135624Z-28947` tái hiện cùng mismatch và restore 0. Đây là contract/schema candidate; chưa đủ để quy kết Directus nếu chưa chốt ý nghĩa response single-item của lab và schema export.

Các đường dẫn source Directus cho việc khoanh vùng (không sửa trong nhiệm vụ): `directus/api/src/controllers/items.ts:19-63` tạo item rồi đọc lại single item, `:66-97` trả list với `data`, `:235-251` gọi `deleteOne` rồi middleware `respond`; `directus/api/src/utils/sanitize-query.ts:52-54,144-162` parse aggregate; `directus/api/src/utils/validate-query.ts:270-276` chuyển field selection khi có aggregate; và `directus/api/src/database/get-ast-from-query/get-ast-from-query.ts:40-70` dựng AST aggregate. Các vị trí này chứng minh đường xử lý, chưa chứng minh root cause của từng finding.

Artifact lịch sử đã có các case `kb5gjq`, `F8j8Gl`, `UNKW3j`, `R0sH5o`, `DhqXrn`, `UTk4sa`, `6IayFG`, `6THjzP` và `QPKZ6w`. Chúng được dùng làm nhóm triage, không mặc định tái hiện trong run mới.

## Harness finding đã sửa

Vòng `campaign` trước đây dùng `campaign_one ... || overall=1`, nhưng `campaign_one` bật lại `errexit` nội bộ; runner exit 1 vì check failure làm shell dừng trước seed tiếp theo dù restore PASS. Bản sửa gọi trong nhánh `if/else`, đọc `restore_exit_code`, tiếp tục khi restore bằng 0 và tạo summary `blocked` khi setup/restore thất bại. Run `20261012T112746Z-20300` đã chứng minh seed 101 runner=1/restore=0 vẫn chuyển sang seed 202.

## Root cause chưa đủ bằng chứng

Chưa đánh dấu defect Directus nào đã xác nhận chỉ từ Schemathesis. Cần giữ source commit, image digest, schema hash, fixture version và server log khi replay. Không sửa expected hoặc mã Directus để làm finding biến mất.

