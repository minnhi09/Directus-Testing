# Bài 5 — K05: Schema-Based API Testing với Schemathesis

## 5.1. K05 đang giải quyết vấn đề gì?

Viết thủ công vài request chỉ bao phủ một số ví dụ. API có nhiều kiểu dữ liệu, query, boundary và response shape; việc nghĩ hết bằng tay khó và dễ bỏ sót. **Schema-based testing** lấy OpenAPI làm nguồn để sinh request có cấu trúc, gửi đến API và kiểm tra response bằng các check tự động.

K05 trong đồ án không phải “bấm random vào API”. Nó là pipeline có kiểm soát:

```text
OpenAPI theo actor
    -> chọn allowlist 10 method–path
    -> raw hoặc guided schema
    -> seed + budget + worker/rate limit
    -> Schemathesis 4.30.0 runner
    -> check + event/report
    -> restore + triage + replay
```

## 5.2. Mười operation chính

Allowlist được định nghĩa trong `scripts/lab-components.sh` và phải được đối chiếu trước mỗi campaign:

```text
GET    /items/qa_articles
POST   /items/qa_articles
GET    /items/qa_articles/{id}
PATCH  /items/qa_articles/{id}
DELETE /items/qa_articles/{id}

GET    /items/qa_categories
POST   /items/qa_categories
GET    /items/qa_categories/{id}
PATCH  /items/qa_categories/{id}
DELETE /items/qa_categories/{id}
```

Không thêm bulk PATCH/DELETE vào campaign chính. `GET /server/specs/oas` là bước chuẩn bị schema, không tính vào 10 operation nghiệp vụ.

## 5.3. Raw và guided

### Raw

Raw sử dụng contract gốc trong phạm vi được chọn. Nó trả lời: “API baseline phản ứng thế nào trước dữ liệu do schema gốc mô tả?”

- Không thêm fixture ID tùy tiện.
- Không đổi response contract để tránh failure.
- Giữ source schema, hash và operation scope.
- Kết quả chỉ nói về schema/profile/seed/config đã ghi.

### Guided

Guided dùng overlay riêng để tăng khả năng đi tới state nghiệp vụ:

- fixture ID thật từ `fixture-map.json`;
- body example hợp lệ;
- query focus;
- diff từ raw source.

Guided trả lời một câu hỏi khác: “Khi cung cấp đường dẫn và dữ liệu có chủ ý, API xử lý sâu hơn ra sao?” Kết quả không được gọi là raw.

## 5.4. Các khái niệm cần phân biệt

| Khái niệm | Nghĩa |
|---|---|
| Example | Input mẫu có sẵn trong schema/fixture |
| Coverage | Chiến lược khám phá operation/branch theo tool |
| Fuzzing | Sinh nhiều biến thể input theo schema/strategy |
| Stateful | Dùng kết quả request trước làm input cho request sau |
| Check | Assertion nền tảng của Schemathesis |
| Shrinking | Rút gọn input lỗi về case nhỏ dễ đọc/replay |
| Restore | Khôi phục fixture sau campaign |
| Seed | Hạt giống ngẫu nhiên để tái lập dãy sinh |

`max-examples` là số ví dụ tối đa theo operation/strategy, không phải tổng số HTTP request. Stateful có thể tạo nhiều tương tác hơn và phụ thuộc state.

## 5.5. Check nền tảng

Campaign chọn rõ các check phù hợp:

- `not_a_server_error`: không để response 5xx đi qua mà không ghi nhận.
- `status_code_conformance`: status thuộc responses schema mô tả.
- `content_type_conformance`: media type hợp contract.
- `response_schema_conformance`: body đáp ứng schema response.
- `unsupported_method`: operation/method được scope hợp lệ.
- `negative_data_rejection`: dữ liệu được kỳ vọng invalid bị xử lý theo oracle negative.
- `positive_data_acceptance`: input hợp lệ có đường đi thành công khi precondition phù hợp.

Một request có thể tạo nhiều check failure. Hãy nhóm theo case/root cause trước khi đếm defect.

## 5.6. Budget của kế hoạch

Giá trị mặc định trong `config/lab.env.example`:

| Tham số | Giá trị |
|---|---:|
| Worker | `1` |
| Rate limit | `5/s` |
| Request timeout | `10s` |
| Max examples/operation | `100` |
| Max time/profile/seed | `1200s` |
| Campaign seeds | `101,202,303` |

Pilot học tập có thể dùng một seed, `LAB_MAX_EXAMPLES=1`, `LAB_MAX_TIME=30`, nhưng phải ghi rõ đây là pilot ngắn. Nếu hết time/budget, trạng thái là `failed_or_incomplete` hoặc chưa hoàn tất; không ghi coverage như campaign đủ.

## 5.7. Vì sao seed chưa đủ để tái lập?

Cùng seed vẫn có thể cho kết quả khác nếu thay đổi:

- schema hash;
- fixture/database state;
- Directus/image digest;
- actor/token/policy;
- thứ tự request/stateful transition;
- version harness hoặc dependency;
- budget/rate/timeout.

Vì vậy metadata phải ghi cả seed và toàn bộ dependency liên quan.

## 5.8. Restore và an toàn dữ liệu

Campaign snapshot fixture trước khi chạy, sinh request, rồi cố gắng khôi phục. Restore `PASS` chỉ nói fixture được đưa về trạng thái snapshot; nó không biến các failure trong campaign thành pass.

Không chạy hai suite ghi/xóa song song trên cùng DB nếu chưa có isolation. Không fuzz server ngoài lab. Trước khi chạy cần kiểm URL, project Compose, actor, schema allowlist và credential source.

## 5.9. Chạy một pilot có thể đọc được

```bash
./lab.sh doctor
./lab.sh up
./lab.sh seed
./lab.sh export-schema
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test raw
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test guided
```

Sau mỗi command:

1. ghi `run_id` và exit code;
2. mở `campaign-summary.json`, `schema-manifest.json`, log và events;
3. kiểm tra operation count, seed, profile, schema hash;
4. xem failure có phải cùng một case/root cause không;
5. kiểm restore và cleanup;
6. chỉ sau đó mới viết nhận xét.

Không dùng `|| true` để làm pipeline xanh. Nếu cần tiếp tục khảo sát sau một failure, chạy command kế tiếp độc lập và ghi rõ failure trước đó.

## 5.10. Đọc report như kỹ sư kiểm thử

Hãy trả lời theo thứ tự:

1. Input contract nào đã dùng?
2. Operation nào thực sự chạy, không chỉ có trong schema?
3. Có bao nhiêu case, check failure, errored, unique failure?
4. Failure được shrink chưa?
5. Server response có 5xx không?
6. Có precondition/fixture mismatch không?
7. Restore có pass không?
8. Có thể replay bằng case ID không?

“14 unique failure” không phải “14 bug”. Một response có thể vi phạm status, content type và response schema cùng lúc.

## 5.11. Câu hỏi tự kiểm tra

- Raw và guided khác nhau ở giả thuyết kiểm thử nào?
- Vì sao không được sửa raw schema để expected khớp response?
- `max-examples=100` có nghĩa tối đa 100 request toàn campaign không?
- Restore pass cho phép kết luận gì và không cho phép kết luận gì?

Đọc tiếp: [Bài 6 — Scenario, invariant và harness](06_scenario_invariant_harness.md).

