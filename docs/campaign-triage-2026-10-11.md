# Triage campaign Schemathesis — 2026-10-11

Tài liệu này phân loại các kết quả campaign đã chạy trên baseline Directus
12.5.0 trong project `r06-k05`. Các con số failure là số của Schemathesis,
không phải số defect độc lập.

Các bảng đầu tài liệu ghi lại campaign lịch sử trước khi license Reader hoạt
động. Kết quả hiện hành của fixture `r06-k05-v2`, cùng tiêu chí G1 đã điều
chỉnh, nằm trong [`docs/test-matrix.md`](test-matrix.md),
[`docs/g1-acceptance.md`](g1-acceptance.md) và
[`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md).
Không dùng phần lịch sử này để suy ra Reader hiện tại còn blocked.

## Phạm vi và bằng chứng

- Raw: run `20261011T050204Z-28735`, seed `101/202/303`, 10/10 operation mỗi seed,
  lần lượt 59/65/51 case, restore đều PASS.
- Guided: run `20261011T060247Z-30882`, seed `101/202/303`, 10/10 operation mỗi seed,
  lần lượt 5.809/5.874/5.899 case, restore đều PASS.
- Raw schema hash: `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`.
- Guided overlay hash: `dc3f057aefb095c4c51ddb712de33d762176d0472f8e7af313522b0551824d7e`.
- Harness sửa license configuration: commit `c7cc8d7`.
- Harness sửa replay binary body: commit `686f4d1`.

Pilot sau hai commit trên cũng xác nhận đường chạy độc lập của hai profile:

| Profile/run | Operation | Cases | Unique failure | Errored | Restore | Kết thúc |
|---|---:|---:|---:|---:|---|---|
| raw / `20261011T074023Z-44637` | 10/10 | 47 | 15 | 0 | PASS | `max_time`, runner 1 |
| guided / `20261011T074112Z-45270` | 10/10 | 134 | 29 | 1 | PASS | `max_time`, runner 1 |

Doctor sau pilot `20261011T074209Z-45910` PASS; image digest, fixture map và
authenticated health vẫn đúng baseline.

Replay sau pilot trên HEAD `6fe1865`:

| Case/run | Request | Kết quả | Phân loại hiện tại |
|---|---|---|---|
| `AmXHZz` / `20261011T075613Z-48561` | `POST /items/qa_articles` | expected/actual `200`; `data` là object, restore PASS | Schema/contract candidate |
| `jShXuk` / `20261011T075622Z-49153` | `POST /items/qa_categories` | expected/actual `200`; `data` là object, restore PASS | Schema/contract candidate |
| `VllBgh` / `20261011T075632Z-49739` | `GET /items/qa_articles` với query aggregate/deep fuzz | expected/actual `500`, restore PASS | Product robustness candidate; kèm schema permissive |

Các reproducer nằm trong từng thư mục run tương ứng dưới
`artifacts/runs/<run_id>/`, không chứa credential. Hai case POST tái hiện cùng
một mẫu: response của Directus là một item object nhưng response schema export
cho status `200` mô tả `data` là array. Đây là lỗi/thiếu sót hợp đồng cần đối
chiếu với semantics POST object-vs-array; chưa gọi là lỗi sản phẩm.

## Phân loại theo nhóm nguyên nhân

| Nhóm | Raw | Guided | Đánh giá hiện tại |
|---|---:|---:|---|
| `UndefinedStatusCode` | 16/14/16 | 30/29/29 | Schema/contract candidate; cần đối chiếu response map và semantics Directus, chưa gọi là product defect |
| `UnsupportedMethodResponse` | 2 mỗi seed | 2 mỗi seed | Cần xác minh hành vi TRACE ngoài allowlist; chưa kết luận |
| `RejectedPositiveData` | 2/1/1 | 8/8/8 | Chưa kết luận; có thể do precondition/fixture/query sinh ra không phù hợp |
| `UndefinedContentType` | 0/1/0 | 5/5/5 | Chưa kết luận; cần replay response cụ thể |
| `ServerError` | 0 | 9/8/8 | Mức ưu tiên cao, nhưng chỉ là candidate cho đến khi replay được chuỗi stateful |
| `JsonSchemaError` | 0 | 6/10/7 | Chưa kết luận; cần phân biệt schema raw/overlay và response thực tế |
| `AcceptedNegativeData` | 0 | 3 mỗi seed | Chưa kết luận; cần kiểm tra request/validation và trạng thái fixture |

## Replay đã xác minh

### `UETNPW`

- Request: `DELETE /items/qa_articles/6`.
- Expected từ report: `204` nhưng response map raw chỉ ghi `200, 401, 404`.
- Actual replay: `204`, body rỗng.
- Artifact: `artifacts/runs/20261011T073454Z-42697/`.
- Restore: PASS.
- Kết luận: tái hiện được một contract/schema candidate. Chưa kết luận Directus
  sai; cần quyết định liệu OpenAPI phải bổ sung `204` hay semantics hiện tại đã
  được chấp nhận trong baseline.

### `7DpEST`

- Request: `PATCH /items/qa_articles/6` với body binary `AA==` chứa byte NUL.
- Lần replay đầu `20261011T073501Z-43256` bị `mismatch` vì harness đưa payload
  binary qua command substitution của Bash, làm mất byte NUL.
- Commit `686f4d1` giải mã body vào file và truyền bằng
  `curl --data-binary @file`.
- Replay sau sửa ở `20261011T073559Z-43850`: expected/actual đều `400`, restore
  PASS.
- Kết luận: lỗi thuộc harness đã được sửa; không phải product defect.

### `AmXHZz` và `jShXuk`

- `AmXHZz`: `POST /items/qa_articles` với body hợp lệ từ guided example; Directus
  tạo item và trả `200` với `data` object. Schema snapshot guided hash
  `dc3f057a...` yêu cầu array.
- `jShXuk`: cùng hiện tượng trên `POST /items/qa_categories`.
- Replay lần lượt ở `20261011T075613Z-48561` và `20261011T075622Z-49153`, cả hai
  đều `status=reproduced`, request exit `0` và restore exit `0`.
- Kết luận: gộp thành một nhóm schema/contract candidate về response shape,
  không đếm thành hai product defect độc lập.

### `VllBgh`

- Replay ở `20261011T075632Z-49739` trả `500` giống campaign và restore fixture
  PASS. Log Directus lúc `07:56:37` ghi `TypeError: fields is not iterable` tại
  `extractPathsFromQuery` trong module xử lý permission AST.
- Thu gọn trên cùng baseline cho thấy `GET /items/qa_articles?fields=&aggregate={"foo":1}`
  vẫn trả `500` với `INTERNAL_SERVER_ERROR`; các biến thể `aggregate={}` và
  `aggregate={"count":["id"]}` trả `200`.
- OpenAPI hiện mô tả `aggregate` là object có các property được biết nhưng không
  đặt `additionalProperties: false`, nên key lạ và giá trị số vẫn lọt qua schema
  JSON. Vì vậy đây là **schema omission + product robustness candidate**: schema
  cần giới hạn aggregate function, còn API không nên phát sinh 500 cho input
  được schema chấp nhận. Chưa kết luận product defect cho đến khi đối chiếu
  upstream hoặc xác nhận contract chính thức.
- Reproducer đầy đủ giữ nguyên trong
  `artifacts/runs/20261011T075632Z-49739/reproducer-schemathesis-VllBgh.json`;
  request thu gọn ở trên là bằng chứng local bổ sung, không dùng credential.
- Regression case đã được version hóa thành `aggregate-query-robustness` trong
  `scripts/invariants.py`, nên không phụ thuộc Schemathesis artifact. Run
  `20261011T080746Z-51887` trả `500`, tạo report/reproducer đã làm sạch và giữ
  exit `1` để không che candidate này.

## Chưa được kết luận

- Các `ServerError` và `JsonSchemaError` khác trong guided stateful campaign chưa
  có reproducer độc lập đủ precondition; `AmXHZz`, `jShXuk` và `VllBgh` là ba case
  đại diện đã replay được ở trên.
- Các status/content-type ngoài schema cần đối chiếu schema raw, overlay và
  hành vi đã pin trước khi tạo defect.
- Chưa có defect sản phẩm Directus nào được xác nhận chính thức; `VllBgh` là
  candidate có stack trace và reproducer tối giản, cần bước đối chiếu upstream.

## Điều kiện tiếp theo sau checkpoint v2

1. Giữ nguyên license trong `config/lab.env`, không commit giá trị; baseline v2
   đã xác minh `/license` active và Reader policy đã chạy qua API thật.
2. Triage tiếp các `ServerError`, `JsonSchemaError` và response ngoài contract
   của raw/guided; mỗi nhóm phải có precondition, expected/actual, phân loại và
   reproducer hoặc trạng thái `unresolved`.
3. Giữ invariant aggregate HTTP 500 và exit code campaign làm evidence; không
   nới assertion, blanket skip/xfail hoặc đổi trạng thái runner để làm đẹp.
4. Không cần dựng máy thứ hai hoặc review chéo thành viên để đóng G1. README và
   manifest vẫn phải duy trì khả năng người khác dựng/chạy lại; peer evaluation
   cuối kỳ của đề bài là quy trình riêng.
