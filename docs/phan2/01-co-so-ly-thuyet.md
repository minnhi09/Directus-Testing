# 01 — Cơ sở lý thuyết và tiêu chí áp dụng

## Phạm vi và kỹ thuật thực tế

K05 là harness kiểm thử REST API theo schema, dùng Schemathesis `4.30.0` và OpenAPI do chính R06 xuất ra theo actor. Mã điều phối nằm ở `lab.sh` và `scripts/lab-components.sh`; các oracle nghiệp vụ nằm ở `scripts/invariants.py`. K05 không thay thế Directus và không suy ra chất lượng của Directus từ tài liệu upstream.

Phạm vi runtime được chốt cho hai collection `qa_categories` và `qa_articles`. Campaign chính chọn mười operation: GET list, POST, GET detail, PATCH detail và DELETE detail cho mỗi collection. Schema Editor được dùng cho campaign; schema Reader dùng kiểm tra quyền và projection. Schema Anonymous hiện không có operation collection.

## Schema-based API testing

OpenAPI mô tả method, path, parameter, request body, response, status và content type mà generator có thể dùng. Harness thực hiện `seed` trước `export-schema`, lưu schema theo actor và SHA-256 trong `schema-manifest.json`. `campaign_build_schema` lọc đúng mười operation từ schema nguồn; raw giữ operation contract, còn guided tạo bản overlay riêng với ID fixture và ví dụ payload hợp lệ. Schema raw không bị ghi đè.

Kiểm thử schema-based có ba lớp:

1. Generator tạo request hợp lệ, biên và không hợp lệ từ parameter/body schema.
2. Schemathesis kiểm tra `not_a_server_error`, status, content type, response schema, unsupported method, negative data rejection và positive data acceptance.
3. Harness bổ sung oracle không biểu diễn đầy đủ trong OpenAPI: fixture ID, CRUD read-back, bất biến dữ liệu, quan hệ, validation và ma trận quyền.

Một request hợp schema chỉ chứng minh nó phù hợp mô tả đầu vào. Nó không chứng minh permission, ràng buộc database, dữ liệu seed hay ý nghĩa nghiệp vụ đều đúng. Vì vậy một HTTP 400/403/500 phải được đối chiếu với precondition và schema actor trước khi gọi là lỗi sản phẩm.

## Fuzzing raw và guided

Raw campaign dùng schema Editor đã scope, seed `101/202/303`, một worker, tối đa 100 ví dụ mỗi operation, rate limit `5/s`, timeout request 10 giây và tối đa 1.200 giây mỗi profile/seed. Guided giữ contract raw và thêm ví dụ fixture, ID hợp lệ, payload POST/PATCH và bật stateful phase. Hai profile được lưu ở thư mục khác nhau để không trộn kết quả.

Seed của Schemathesis giúp tái lập quá trình sinh input, nhưng không thay thế trạng thái DB, policy, schema hash, image digest hoặc thứ tự request. Stateful failure chỉ được gọi là full-chain khi artifact có parent chain và mapping ID; nếu chỉ gửi interaction cuối thì phạm vi là `reproduced_request_only`.

## Test oracle, invariant và scenario

Oracle tự động gồm status/content type/response schema và các check acceptance của Schemathesis. Oracle nghiệp vụ trong `scripts/invariants.py` tính expected từ fixture map, không lấy chính response đang kiểm tra làm expected. Ví dụ `query-fixture` so filter/sort/page/offset/search với tập fixture biết trước; `reader-write` đọc lại target sau PATCH bị từ chối để xác nhận dữ liệu không đổi.

Sáu scenario nghiệp vụ bao phủ CRUD Editor, filter status, sort/pagination, Reader chỉ thấy bài published, cấm lộ `internal_notes` và Reader không được ghi. Mười một invariant bao phủ token, anonymous, CRUD, đủ mười operation, query, aggregate robustness, contract candidate, quan hệ SET NULL, validation và quyền Reader.

## Tiêu chí áp dụng

Kỹ thuật phù hợp khi API có OpenAPI thực tế, operation và actor có thể scope, fixture cô lập được, response có thể kiểm tra tự động và hệ thống cho phép snapshot/restore. R06 đáp ứng các điều kiện này: schema theo actor được export tại runtime, Docker network riêng, fixture idempotent và restore có so sánh snapshot.

Kỹ thuật không đủ cho line/branch coverage Directus, hiệu năng, concurrency, GraphQL, WebSocket, frontend, mọi tổ hợp query, phục hồi DB hoặc dữ liệu lớn. Schema coverage trong `schemathesis-coverage.json` chỉ là coverage theo schema/generation phase; không được báo cáo như code coverage. Campaign chạm `max_time` hoặc có check failure vẫn phải giữ exit code và được ghi `FAIL/INCOMPLETE`, không đổi thành PASS.

## Bằng chứng mã nguồn

- `DAMH/scripts/lab-components.sh`: `campaign_build_schema`, `campaign_snapshot`, `campaign_restore`, `campaign_one`, `campaign` và `replay_schemathesis_case`.
- `DAMH/scripts/invariants.py`: `Lab.case_query_fixture`, mười một case được đăng ký ở `CASE_FACTORIES` và các hàm `Case.fail/block`.
- `DAMH/config/lab.env.example`: image digest, seed, budget, worker, rate và timeout.
- `DAMH/AGENTS.md`: allowlist 10 operation, actor, fixture, budget và quy tắc không che failure.

