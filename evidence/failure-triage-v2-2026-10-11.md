# Triage failure Schemathesis v2 — 2026-10-11

Tài liệu này ghi lại triage bổ sung trên fixture `r06-k05-v2` sau campaign
raw/guided đầy đủ. Mục tiêu là phân biệt check failure, lỗi hợp đồng schema,
giới hạn precondition/stateful của harness và candidate lỗi sản phẩm. Báo cáo
không chuyển failure thành PASS và không đếm nhiều check failure cùng nguyên
nhân thành nhiều defect.

## Provenance

- Directus `12.5.0`, PostgreSQL `16`, fixture `r06-k05-v2`, project Compose
  `r06-k05`.
- Campaign raw: `20261011T085034Z-76481`, harness SHA
  `d14c6151bb2131f0b738921d1a3b9b5f7c979d07`, schema hash
  `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`.
- Campaign guided: `20261011T095117Z-89079`, cùng harness SHA, overlay hash
  `cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`.
- Các replay đại diện được chạy tuần tự trên HEAD harness
  `33d97c4f2e1a8c0005bba5b3c36da5f0eef1c4a0`; mỗi replay đều có restore
  fixture PASS. Artifact đầy đủ nằm trong `artifacts/runs/` và không được đưa
  vào Git.
- Các số dưới đây là số lần check failure trong ba seed, không phải số defect.

## Tổng hợp check failure v2

| Check | Tổng raw (3 seed) | Tổng guided (3 seed) |
|---|---:|---:|
| `UndefinedStatusCode` | 121 | 222 |
| `UnsupportedMethodResponse` | 6 | 6 |
| `RejectedPositiveData` | 5 | 45 |
| `UndefinedContentType` | 1 | 22 |
| `JsonSchemaError` | 0 | 35 |
| `ServerError` | 0 | 35 |
| `AcceptedNegativeData` | 0 | 10 |

Các tổng được gom từ `schemathesis-events.ndjson` của ba seed tương ứng. Bảng
không phân bổ lại theo seed khi artifact chỉ được dùng để gom nhóm; do đó không
dùng bảng này làm coverage hoặc defect count.

## Replay đại diện

| Case / replay | Operation và quan sát | Kết quả replay | Phân loại hiện tại |
|---|---|---|---|
| `Q8K5Nh` / `20261011T122512Z-124267` | Raw `GET /items/qa_articles`; response `403` do query chạm collection `directus_versions` không được actor cấp quyền, trong khi response map ghi `200,401` | Request cuối tái hiện `403`, restore PASS, exit `0` | Schema/precondition candidate; không phải bằng chứng Directus defect |
| `VbURdO` / `20261011T122519Z-124858` | Guided stateful `PATCH /items/qa_articles/{id}`; event campaign nhận `204`, replay hiện tại nhận `403` do precondition/quyền cập nhật không tái dựng được | Mismatch, restore PASS, exit `1` | Chưa kết luận; giới hạn replay stateful/precondition |
| `lwZKEo` / `20261011T122522Z-125422` | Unsupported-method probe gửi `TRACE` tới route article; Directus trả `404`, check kỳ vọng `405` | Tái hiện `404`, restore PASS, exit `0` | Contract/tool semantics candidate ngoài 10 operation chính |
| `3Ble8Q` / `20261011T122526Z-125993` | Raw GET list với query `fields/meta` không hợp lệ; Directus trả `400 INVALID_QUERY` và yêu cầu meta hợp lệ | Tái hiện `400`, restore PASS, exit `0` | Schema semantic/generator-positive candidate, không phải product defect |
| `vx21yF` / `20261011T122531Z-126570` | Raw GET list với `export=csv`; response `200`, content type `text/csv`, schema đang mô tả `application/json` | Tái hiện response và content type, restore PASS, exit `0` | Schema/contract gap cần quyết định cách biểu diễn export |
| `Z6K7ww` / `20261011T122536Z-127156` | Guided `POST /items/qa_articles`; Directus trả `200` với `data` object, response schema mô tả array | Tái hiện `200` và shape object, restore PASS, exit `0` | Schema/contract candidate; cùng nhóm với POST category đã triage trước |
| `CkqaOB` / `20261011T122539Z-127722` | Guided stateful POST category, final request malformed/generated làm Directus trả `500 INTERNAL_SERVER_ERROR` | Request cuối tái hiện `500`, restore PASS, exit `0` | Product robustness candidate + stateful limitation; chưa xác nhận defect |
| `pM4r4g` / `20261011T122542Z-128284` | Guided stateful negative PATCH category; event campaign nhận `200`, replay trực tiếp hiện tại nhận `403` | Mismatch, restore PASS, exit `1` | Chưa kết luận; không coi là negative-acceptance defect |
| `kb5gjq` / `20261011T135006Z-162769` | Guided stateful POST article với `published_at=""`; source/expected/actual `500` | `reproduced_request_only`, restore PASS, exit `1`; không có parent transition | Product robustness + schema-semantic candidate; PostgreSQL `22007`, chưa xác nhận defect |
| `F8j8Gl` / `20261011T135713Z-165099` | Guided stateful GET article với `backlink=true&export=json`; source/expected/actual `200`, body là array 12 item thay vì object `data` | `reproduced_request_only`, restore PASS, exit `1`; không có parent transition | Schema/contract candidate về export response shape; không phải product defect đã xác nhận |
| `UNKW3j` / `20261011T135951Z-166351` | Guided stateful GET article với `export=xml`; source/expected/actual `200`, content type `text/xml` ngoài schema `application/json` | `reproduced_request_only`, restore PASS, exit `1`; không có parent transition | Schema/contract candidate về export media type; cùng nhóm `vx21yF`, chưa xác nhận defect |

Các status trong bảng là kết quả của các run lịch sử trước chain hardening.
`CkqaOB` vẫn chỉ có final interaction trong artifact; `VbURdO` không có parent
chain phù hợp với precondition replay. Sau commit `baaee4b`, `pM4r4g` đã được
replay full chain ở run `20261011T131321Z-144935`; kết quả mới là mismatch
`final 200` so với negative expected `400`, restore PASS. Vì vậy không gộp
request-only, full-chain mismatch và product defect thành một kết luận.

## Quyết định triage

1. Hai POST response-shape (`Z6K7ww` và nhóm POST trước đó) được gộp thành một
   schema/contract candidate, không thành nhiều lỗi sản phẩm.
2. `vx21yF` là contract gap riêng về response export; không trộn với response
   shape JSON.
3. `Q8K5Nh` và `3Ble8Q` cho thấy input sinh ra có thể chạm semantic/query mà
   schema không mô tả đủ; không coi HTTP `403/400` tự động là lỗi Directus.
4. `lwZKEo` chỉ là unsupported-method probe; không làm tăng inventory 10
   method–path của campaign chính.
5. `CkqaOB` được giữ là candidate ưu tiên cao vì có HTTP 500, nhưng cần log/
   upstream hoặc reproducer đầy đủ trước khi phân loại `product` chính thức.
6. Candidate aggregate HTTP 500 đã có invariant regression riêng và vẫn giữ
   exit `1` trong run `20261011T134519Z-160153` dưới `bcbf219`; cùng run ghi hai control
   `200`, làm rõ failure phụ thuộc shape/giá trị aggregate. Báo cáo này không
   đổi candidate thành defect đã xác nhận.
7. `kb5gjq` tái hiện một POST array được Schemathesis đánh dấu positive nhưng
   chứa `published_at=""`; Directus chuyển giá trị rỗng xuống PostgreSQL và trả
   `22007` rồi HTTP `500`. Vì timestamp rỗng là sai ngữ nghĩa dù JSON type là
   string, finding được giữ là schema-semantic/product robustness candidate,
   không đếm thành defect đã xác nhận. Snapshot editor hiện khai báo field là
   `type: string`, `nullable: true`, `format: timestamp` nhưng không có
   `pattern`/`minLength`; POST schema nhận object hoặc array. Source Directus
   pin `4f77933bf9551cac6b289576078783e189b8f4e3` cũng ánh xạ kiểu timestamp
   thành custom OpenAPI format `timestamp`, nên đây là schema semantic gap cần
   đối chiếu contract, không phải bằng chứng đủ để kết luận upstream defect.
8. `F8j8Gl` tái hiện `GET /items/qa_articles?backlink=true&export=json` với
   HTTP `200` và body array 12 item. Schema operation vẫn kiểm tra object có
   `data`, nên `JsonSchemaError` được gộp vào schema/contract candidate về
   alternate export response shape; không đếm riêng thành product defect.
9. `UNKW3j` tái hiện `export=xml` với HTTP `200` và `text/xml; charset=utf-8`
   trong khi schema chỉ khai báo `application/json`. Đây là cùng nhóm export
   media-type contract với `vx21yF`, không phải product defect độc lập.

## Automated contract probe

Harness commit `7018107` bổ sung case `contract-schema-candidates` để đối chiếu
runtime với schema Editor đã export, không sửa raw snapshot và không nới
assertion. Lệnh `./lab.sh replay contract-schema-candidates` ở run
`20261011T130227Z-139257` kết thúc `exit 1` có chủ đích: report ghi
`schema_candidates=4`, toàn bộ dữ liệu tạm được cleanup bằng DELETE `204`.

Bốn candidate được ghi trong
`artifacts/runs/20261011T130227Z-139257/invariant-report.json`:

1. POST category trả `data` object trong khi response schema mô tả array.
2. POST article trả `data` object trong khi response schema mô tả array.
3. GET với `export=csv` trả `text/csv` trong khi schema chỉ khai báo
   `application/json`.
4. DELETE category detail trả `204` trong khi response map hiện khai báo
   `200/401/404`.

Đây là các `schema_contract_candidate`, không được đếm thành product defect.
Run này có harness SHA `701810742a87c6d210c627503aabc22940dc4abc` và source
Directus đã pin `4f77933bf9551cac6b289576078783e189b8f4e3`.

## Việc còn lại

- `kb5gjq` đã có reproducer request-only và log DB đủ để triage; nếu muốn đóng
  candidate cần quyết định contract timestamp hoặc đối chiếu upstream, không
  sửa expected thành `PASS`.
- `pM4r4g` đã có full-chain replay ở run `20261011T131321Z-144935`; các case
  như `CkqaOB` thiếu parent trong artifact vẫn phải ghi final-request-only và
  unresolved. Không được dùng replay trực tiếp hiện tại để tuyên bố full state
  cho case không có đủ chain.
- Đã đối chiếu response map/content type/POST shape với contract Directus đã
  pin bằng probe riêng; nếu tạo overlay trong tương lai thì chỉ sửa bản
  `guided`, giữ raw snapshot bất biến và lưu diff/lý do.
- Giữ nguyên exit code campaign, report và artifact hiện tại; không thêm
  skip/xfail hoặc nới assertion để làm đẹp kết quả.

Không có credential, token, mật khẩu hoặc toàn bộ request body nhạy cảm nào
được ghi trong tài liệu này.

## Replay parent chain sau commit `baaee4b`

Harness hiện replay parent chain khi event có đủ parent case, interaction và
transition mapping; ID sinh trong parent response được ánh xạ vào path/body của
request con. Run `20261011T131321Z-144935` của `pM4r4g` ghi:

- `sequence_case_ids=[mvlcIV,pM4r4g]` và `replay_scope=full_transition_chain`;
- parent `POST /items/qa_categories` trả `200`, final `PATCH` trả `200`;
- campaign negative oracle kỳ vọng non-2xx (report bắt được expected `400`),
  nên replay giữ `status=mismatch`, exit `1`, restore PASS.

Đây là full-chain replay được kiểm chứng cho case này, nhưng không tự động là
product defect: cần xác minh semantics của input negative/ID âm và contract
chính thức. Ngược lại, `CkqaOB` ở run `20261011T131350Z-145631` không có parent
case trong event artifact; harness giữ `reproduced_request_only`, final `500`,
restore PASS và exit `1`. Không được gộp hai phạm vi này thành một kết luận.

## Hardening replay sau triage

Commit `64e88f9` (`fix: scope stateful replay results`) đã sửa harness để nhận
diện cả `meta.phase.name=stateful`, không chỉ cờ `is_transition_applied`.
Replay vẫn gửi interaction cuối và restore fixture để hỗ trợ điều tra, nhưng
report không còn gọi đó là `reproduced` đầy đủ:

| Case / run sau hardening | Kết quả |
|---|---|
| `CkqaOB` / `20261011T123728Z-131951` | `reproduced_request_only`, `sequence_replayed=false`, final request `500`, restore PASS, exit `1` |
| `Q8K5Nh` / `20261011T123735Z-132524` | `reproduced`, `sequence_replayed=true`, `403`, restore PASS, exit `0` |

Các run trong bảng replay chính ở trên là bằng chứng triage đã chạy trước khi
hardening; chúng vẫn được giữ nguyên. Từ commit này, exit `1` của stateful
final-request-only là chủ ý và giúp tránh tuyên bố quá mức về khả năng tái lập.

## Đối chiếu mã nguồn Directus đã pin

Đối chiếu được thực hiện read-only trong checkout `../directus` tại release
commit `4f77933bf9551cac6b289576078783e189b8f4e3` (`12.5.0`). Worktree
upstream hiện tại đang ở commit mới hơn `d3c9a8bb0c0096148c4740ce908e76c24f2413a0`,
nhưng không dùng commit đó để kết luận baseline và không sửa upstream.

| Finding | Bằng chứng tại commit đã pin | Kết luận triage |
|---|---|---|
| POST trả object nhưng schema mô tả array | `api/src/controllers/items.ts:37-51`: body object gọi `readOne` và đặt `data` là item; body array mới gọi `readMany` | Schema/OpenAPI response-shape candidate đã được source hỗ trợ; không xác nhận lỗi sản phẩm |
| `export=csv` trả `text/csv` | `api/src/utils/validate-query.ts:34` cho phép `csv`; `api/src/middleware/respond.ts:101-104` đặt `Content-Type: text/csv` và trả `200` | Schema/contract omission đã được xác nhận trên baseline; không phải lỗi response runtime |
| DELETE detail trả `204` | `api/src/controllers/items.ts:235-250` gọi `respond`; `api/src/middleware/respond.ts:120-125` trả `204` khi không có payload | Schema response map thiếu status `204`; gộp vào nhóm schema candidate |
| `aggregate={"foo":1}` gây `500` | `validate-query.ts:34` chỉ yêu cầu aggregate là object; `extract-paths-from-query.ts:60-61` lặp qua từng value như iterable; runtime regression `20261011T134519Z-160153` tái hiện `500`, trong khi `{}` và `{"count":["id"]}` trả `200` | Product robustness candidate kèm schema omission; vẫn chưa gọi là defect chính thức |

Đối chiếu này đóng mức phân loại cho POST/export/DELETE, nhưng không làm đổi
raw snapshot, không tạo overlay mới và không thay đổi expected result của các
run đã thực hiện. Candidate aggregate vẫn cần quyết định cuối hoặc bằng chứng
upstream bổ sung trước khi chuyển sang `product defect`.

## Oracle status replay sau audit harness

Audit ngày 2026-10-11 phát hiện một lỗi phân loại trong replay: khi case nguồn
không có check failure, code cũ để `expected_status` rỗng và có thể ghi
`reproduced` dù HTTP status đã thay đổi. Đây là lỗi harness, không phải finding
Directus. Commit `a713481` sửa theo quy tắc: ưu tiên status được oracle failure
chỉ ra; nếu tất cả check nguồn đều PASS thì dùng status của interaction nguồn và
ghi thêm `source_status` trong reproducer.

| Case / run | Source/expected → actual | Kết quả | Phân loại |
|---|---|---|---|
| `tFjhQT` / `20261011T132137Z-149741` | `200/200 → 403`; chain `D3mEEJ → tFjhQT` | `mismatch`, restore PASS, exit `1` | Stateful precondition chưa tái lập; không kết luận product defect |
| `Q8K5Nh` / `20261011T132145Z-150356` | `403/403 → 403` | `reproduced`, restore PASS, exit `0` | Regression replay ổn định |

Artifact trước sửa `20261011T131957Z-148748` được giữ nguyên để truy vết nhưng
không dùng làm bằng chứng PASS cuối cho `tFjhQT`.

Recheck dưới HEAD `916152e` giữ nguyên kết quả: `tFjhQT` ở run
`20261011T132550Z-151921` là `200/200 → 403`, full-chain mismatch, restore PASS,
exit `1`; `Q8K5Nh` ở run `20261011T132604Z-152556` là `403/403 → 403`,
reproduced, restore PASS, exit `0`. Metadata của hai run ghi đúng harness SHA
`916152ec983559303ec6c69dec07456ba5c5f25f`; working tree dirty chỉ vì các file
untracked đã có trước, không phải thay đổi code chưa commit.

## Stateful chain recheck dưới HEAD `3960f55`

| Case / run | Chuỗi và kết quả | Phân loại |
|---|---|---|
| `aZmz3k` / `20261011T133817Z-157078` | `C7nkph → aZmz3k`, parent POST 200, target GET 200, source/expected/actual 200, `full_transition_chain`, restore PASS, exit `0` | Full-chain reproduction hợp lệ |
| `Ag8Csb` / `20261011T133626Z-155874` | Parent GET 200 nhưng transition source có 100 ID; snapshot replay có 3 category, không có target `298`; target không gửi, `stateful_sequence_failed`, restore PASS, exit `1` | Stateful precondition/artifact mismatch; chưa kết luận product |

Hai run ghi `harness_sha=3960f55f4bb3f5aef329a6d34c47c5fa287de5c6`. Không dùng
`Ag8Csb` làm bằng chứng Directus từ chối request vì request cuối đã được chặn
đúng khi chuỗi setup không tái lập được.
