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

## Triage v2 trên campaign hiện hành

Sau campaign v2 đã chạy license thật, tám case đại diện được replay tuần tự để
phân loại sâu hơn. Bảng tổng hợp và run ID đầy đủ nằm tại
[`evidence/failure-triage-v2-2026-10-11.md`](../evidence/failure-triage-v2-2026-10-11.md).
Raw có 121 `UndefinedStatusCode`, 6 `UnsupportedMethodResponse`, 5
`RejectedPositiveData` và 1 `UndefinedContentType`; guided có 222
`UndefinedStatusCode`, 45 `RejectedPositiveData`, 35 `JsonSchemaError`, 35
`ServerError`, 22 `UndefinedContentType`, 10 `AcceptedNegativeData` và 6
`UnsupportedMethodResponse`. Đây là check occurrence, không phải defect count.

`Q8K5Nh`, `3Ble8Q`, `vx21yF`, `Z6K7ww`, `lwZKEo` và request cuối của `CkqaOB`
đều có quan sát replay cụ thể, restore PASS. `VbURdO` vẫn mismatch do
precondition/query khác campaign. Sau hardening chain, `pM4r4g` đã replay được
parent `mvlcIV` và final PATCH trong cùng chuỗi; runtime final `200` vẫn trái
negative oracle nên giữ mismatch/exit `1`, chưa gọi là product defect.
`CkqaOB` không có parent case trong artifact nên vẫn là final-request-only
candidate.

Recheck thêm `kb5gjq` ở run `20261011T135006Z-162769`: guided stateful POST
`/items/qa_articles` với body array tối giản có `published_at=""` được replay
request-only, source/expected/actual đều `500`, restore PASS và exit `1`. Log
Directus ghi PostgreSQL SQLSTATE `22007` (`invalid input syntax for type timestamp
with time zone: ""`). Đây là candidate robustness/schema-semantic vì generator
đã coi request là positive nhưng giá trị timestamp rỗng không hợp lệ về ngữ
nghĩa; snapshot editor chỉ mô tả `type: string`, `nullable: true`, custom
`format: timestamp` và không có `pattern`/`minLength`; chưa kết luận product
defect.

Replay bổ sung `F8j8Gl` ở run `20261011T135713Z-165099` tái hiện
`GET /items/qa_articles?backlink=true&export=json` với source/expected/actual
`200`, restore PASS và exit `1`; body thực tế là array 12 item còn response
schema của operation yêu cầu object có `data`. Đây là schema/contract candidate
về alternate export shape; artifact không có parent transition nên chỉ ghi
`reproduced_request_only`.

Replay `UNKW3j` ở run `20261011T135951Z-166351` tái hiện
`GET /items/qa_articles?export=xml&search=Directus` với source/expected/actual
`200`, content type `text/xml; charset=utf-8`, restore PASS và exit `1`. Đây là
cùng nhóm export media-type contract với `vx21yF`, không phải product defect
độc lập; artifact cũng không có parent transition.

Replay `R0sH5o` ở run `20261011T140125Z-167402` tái hiện
`GET /items/qa_articles?...&export=yaml&page=2` với source/expected/actual
`200`, content type `text/yaml; charset=utf-8`, restore PASS và exit `1`. Đây
là cùng nhóm export media-type candidate với CSV/XML, không phải product defect
độc lập; artifact không có parent transition.

Replay `DhqXrn` ở run `20261011T140307Z-168360` đã dựng đủ chain
`UqHibT → DhqXrn`: campaign source `204`, còn replay hiện tại `403` vì Directus
từ chối cập nhật field `id`; restore PASS và exit `1`. Đây là mismatch về
precondition/policy/negative oracle, không coi là accepted-negative defect và
không có mutation còn sót sau restore.

Replay `UTk4sa` ở run `20261011T140452Z-169384` dừng tại parent `vfAiah` vì số
ID trả về không khớp transition mapping; PATCH target không được gửi, restore
PASS và exit `1`. Đây là stateful artifact/precondition limitation, không được
đếm là accepted-negative defect.

Sau triage, commit `64e88f9` đã harden replay scope: stateful case chỉ được ghi
`reproduced_request_only` khi chỉ gửi final interaction. Commit `baaee4b` bổ
sung parent-chain replay và ID mapping từ response parent. Run
`20261011T131321Z-144935` xác nhận `pM4r4g` replay đủ chain và restore PASS;
run `20261011T131350Z-145631` xác nhận `CkqaOB` không có chain nên vẫn
final-request-only. Case non-stateful `Q8K5Nh` vẫn PASS; sanity recheck sau
commit ở run `20261011T131702Z-146905` cũng restore PASS.

### Oracle status replay sau audit harness

Audit một positive stateful case phát hiện logic cũ để trống expected status khi
không có check failure. Commit `a713481` sửa logic để dùng status của interaction
nguồn làm expected trong trường hợp đó và ghi thêm `source_status` vào
reproducer. Run `20261011T132137Z-149741` của `tFjhQT` ghi nguồn/expected `200`
nhưng replay `403`, nên giữ `mismatch`/exit `1` dù parent chain và restore đều
đạt. Đây là bằng chứng precondition/stateful chưa tái lập được, không phải lý do
đổi kết luận thành product defect. Regression `Q8K5Nh` ở run
`20261011T132604Z-152556` dưới HEAD `916152e` giữ `403→403`, `reproduced`,
restore PASS và exit `0`; run `20261011T132550Z-151921` của `tFjhQT` cũng là
recheck dưới HEAD hiện hành và giữ mismatch.

Recheck thêm một parent chain có mutation: `aZmz3k` ở run
`20261011T133817Z-157078` replay đủ `C7nkph → aZmz3k`, source/expected/actual
`200`, restore PASS, exit `0`; đây là full-chain reproduction hợp lệ. Ngược lại,
`Ag8Csb` ở run `20261011T133626Z-155874` bị `stateful_sequence_failed` vì source
parent pool có 100 ID còn fixture hiện tại có 3, target ID `298` không tồn tại
trong snapshot; final request không được gửi và finding được phân loại là
precondition/stateful artifact, không phải product defect.

Đối chiếu source release `4f77933bf9551cac6b289576078783e189b8f4e3` đã làm rõ
thêm ba nhóm contract: POST object/array, export `csv` và DELETE `204` đều phù
hợp với runtime Directus nhưng bị mô tả thiếu hoặc sai trong OpenAPI snapshot.
Riêng aggregate `{"foo":1}` có đường dẫn source dẫn tới lỗi lặp value không
iterable và vẫn giữ là product robustness candidate, chưa xác nhận defect.
Chi tiết line-level nằm trong phần source comparison của
[`evidence/failure-triage-v2-2026-10-11.md`](../evidence/failure-triage-v2-2026-10-11.md).

## Phân loại theo nhóm nguyên nhân

| Nhóm | Raw | Guided | Đánh giá hiện tại |
|---|---:|---:|---|
| `UndefinedStatusCode` | 16/14/16 | 30/29/29 | Schema/contract candidate; cần đối chiếu response map và semantics Directus, chưa gọi là product defect |
| `UnsupportedMethodResponse` | 2 mỗi seed | 2 mỗi seed | Cần xác minh hành vi TRACE ngoài allowlist; chưa kết luận |
| `RejectedPositiveData` | 2/1/1 | 8/8/8 | Chưa kết luận; có thể do precondition/fixture/query sinh ra không phù hợp |
| `UndefinedContentType` | 0/1/0 | 5/5/5 | `vx21yF`/`UNKW3j`/`R0sH5o` tái hiện export CSV/XML/YAML ngoài schema JSON; giữ là export contract candidate |
| `ServerError` | 0 | 9/8/8 | `kb5gjq` đã replay request-only và tái hiện 500; vẫn là candidate robustness/schema-semantic, không phải defect đã xác nhận |
| `JsonSchemaError` | 0 | 6/10/7 | Chưa kết luận; cần phân biệt schema raw/overlay và response thực tế |
| `AcceptedNegativeData` | 0 | 3 mỗi seed | `DhqXrn` full-chain replay trả `403` thay source `204`; `UTk4sa` target không gửi do ID mapping; giữ mismatch/precondition, chưa kết luận defect |

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
  `aggregate={"count":["id"]}` trả `200`. Regression replay mới
  `20261011T134519Z-160153` chạy lại cả ba variant và ghi đúng phân bố này
  dưới harness commit `bcbf219`.
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
  `20261011T134519Z-160153` trả unknown shape `500`, hai control `200`, tạo
  report/reproducer đã làm sạch và giữ exit `1` để không che candidate này.

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
