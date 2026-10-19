# Replay và reproducer

## Chạy replay

Replay dùng credential hiện tại từ `config/lab.env`, fixture map hiện tại và Directus đang chạy trong lab:

```bash
./lab.sh replay editor-crud
./lab.sh replay positive-operations
./lab.sh replay anonymous-denied
./lab.sh replay query-fixture
```

Không truyền token, password hoặc ID tự sinh trong command. `runtime/fixture-ids.json` là nguồn ánh xạ tên fixture → ID thật.

Với case ID do Schemathesis in trong report, dùng cùng interface:

```bash
./lab.sh replay ralwaW
```

Harness tìm case trong `schemathesis-events.ndjson`, giới hạn replay vào hai collection lab, dùng token Editor hiện tại, chụp snapshot trước request và restore sau request. Body fuzz được giải mã vào file nhị phân tạm trong artifact rồi truyền bằng `curl --data-binary @file`, nên payload chứa byte NUL không bị mất qua biến Bash. Kết quả ghi `schemathesis-case.json`, response, `reproducer-schemathesis-<case-id>.json` và status `reproduced`/`mismatch`. Reproducer ghi cả `source_status` của interaction nguồn và `expected_status`: nếu source có check failure thì expected lấy từ oracle failure; nếu mọi check đều PASS thì expected lấy từ HTTP status nguồn. Case không tìm thấy hoặc ngoài allowlist bị từ chối, không gửi request tùy ý.

## Case IDs ổn định

| Case | Chuỗi kiểm tra | Khi nào blocked |
|---|---|---|
| `auth-invalid-token` | GET `/users/me` với token giả; token phải bị từ chối | Network/precondition không có response |
| `anonymous-denied` | Anonymous GET hai collection | Network error |
| `editor-crud` | Editor create → read → PATCH → read → DELETE → read | Editor login/fixture không sẵn sàng |
| `positive-operations` | Positive create/read/PATCH/delete cho đủ 10 operation của hai collection | Editor login/fixture hoặc permission CRUD không sẵn sàng |
| `query-fixture` | Filter published, sort, projection, hai page | Fixture map không khớp dữ liệu |
| `aggregate-query-robustness` | GET query `fields=&aggregate={"foo":1}` và hai control aggregate, unknown không được 5xx, control phải 2xx | Không có API response |
| `contract-schema-candidates` | Editor POST category/article, GET export CSV và DELETE detail; đối chiếu runtime với schema | API/schema precondition không sẵn sàng |
| `relation-nullification` | Tạo category/article, xóa category, kiểm tra FK thành null | Không tạo được relation probe |
| `invalid-field-rejection` | Gửi status/score ngoài contract và kiểm tra không tạo row | Network/read-back precondition |
| `reader-visibility` | Reader đọc published và thử projection có `internal_notes` | Reader schema thiếu operation |
| `reader-write` | Reader PATCH target published, Editor kiểm tra dữ liệu không đổi | Reader schema thiếu PATCH |

`positive-operations` được kiểm tra trong invariant run `20261011T043809Z-24724`;
các replay pass trước đó gồm `editor-crud` ở run `20261011T040109Z-19973`,
`query-fixture` ở `20261011T035618Z-14109`, `auth-invalid-token` ở
`20261011T035623Z-14472`, `anonymous-denied` ở `20261011T035408Z-12774` và
Schemathesis case `ralwaW` ở run `20261011T040346Z-22406`. Đây là bằng chứng
replay local trên một baseline; không suy diễn thành xác nhận upstream hoặc
product defect nếu chưa đủ precondition.

`aggregate-query-robustness` là regression probe deterministic được version hóa
trong `scripts/invariants.py`, nên clone sạch vẫn replay được mà không cần
Schemathesis artifact. Run lịch sử `20261011T134519Z-160153` ghi unknown shape
`500`, control `aggregate={}` `200` và control `aggregate={"count":["id"]}`
`200`; targeted recheck gần nhất `20261011T163231Z-213262` xác nhận lại cùng
phân bố dưới harness `3c40339` (run `20261011T144640Z-184631` được giữ làm
lịch sử). Exit `1` được giữ đúng theo assertion. Đây là
failure cần triage, không phải được chuyển thành pass bằng cách nới expected.
Các run lịch sử `20261011T105242Z-105524` và `20261011T080746Z-51887` được giữ
để đối chiếu trước các checkpoint sau.

`contract-schema-candidates` là probe contract độc lập, chạy lịch sử tại commit
`7018107` ở run `20261011T130227Z-139257`. Targeted recheck gần nhất là
`20261011T163234Z-213685` dưới harness `3c40339` (run
`20261011T144648Z-185062` được giữ làm lịch sử). Probe tạo dữ liệu tạm bằng
Editor, đối chiếu POST response shape, export `text/csv` và DELETE `204` với
`editor.json`, sau đó cleanup thành công. Report cố ý giữ `failed` vì ghi nhận
bốn schema candidate; đây không phải kết luận bốn product defect.

Sau khi sửa replay nhị phân, case `UETNPW` (DELETE nhận 204 ngoài schema) được
replay lại ở run `20261011T073454Z-42697`, còn case `7DpEST` (PATCH với payload
NUL) được replay đúng ở run `20261011T073559Z-43850`. Lần chạy trước của
`7DpEST` ở `20261011T073501Z-43256` bị `mismatch` do harness làm mất byte NUL;
đó là lỗi harness đã sửa, không phải kết luận về Directus.

Các case guided đại diện được replay sau pilot:

- `AmXHZz` (`20261011T075613Z-48561`) và `jShXuk` (`20261011T075622Z-49153`)
  đều tái hiện response `200` có `data` object trong khi schema mô tả array;
  đây là một nhóm schema/contract candidate.
- `VllBgh` (`20261011T075632Z-49739`) tái hiện `500` trên GET query. Reproducer
  tối giản đã kiểm tra là `fields=&aggregate={"foo":1}`; log Directus ghi
  `TypeError: fields is not iterable`. Đây là candidate cần đối chiếu upstream,
  không được ghi nhận tự động thành product defect.
- `kb5gjq` (`20261011T135006Z-162769`) tái hiện `500` trên guided stateful
  `POST /items/qa_articles` với body array `[{"score":0,"title":"","category":0,"id":1186,"published_at":""}]`.
  Source/expected/actual đều `500`, `reproduced_request_only`, restore PASS,
  exit `1`. Log Directus ghi PostgreSQL `22007` do timestamp rỗng; đây là
  schema-semantic/product robustness candidate, chưa phải defect đã xác nhận.
  Snapshot editor khai báo `published_at` là `string`, `nullable: true`,
  `format: timestamp` và không có `pattern`/`minLength`; source Directus pin
  `4f77933bf9551cac6b289576078783e189b8f4e3` dùng cùng custom format mapping.
- `F8j8Gl` (`20261011T135713Z-165099`) tái hiện request-only
  `GET /items/qa_articles?backlink=true&export=json`: source/expected/actual
  `200`, response là array 12 item, trong khi schema operation yêu cầu object
  chứa `data`. Restore PASS, exit `1`; đây là schema/contract candidate cho
  alternate export shape, không phải product defect đã xác nhận.
- `UNKW3j` (`20261011T135951Z-166351`) tái hiện request-only
  `GET /items/qa_articles?export=xml&search=Directus`: source/expected/actual
  `200`, content type `text/xml; charset=utf-8` ngoài schema `application/json`.
  Restore PASS, exit `1`; đây là cùng nhóm export media-type candidate với
  `vx21yF`, không phải defect độc lập.
- `R0sH5o` (`20261011T140125Z-167402`) tái hiện request-only
  `GET /items/qa_articles?fields=*.*&limit=59189288&export=yaml&page=2`:
  source/expected/actual `200`, content type `text/yaml; charset=utf-8` ngoài
  schema `application/json`. Restore PASS, exit `1`; gộp vào export media-type
  candidate, không phải defect độc lập.
- `DhqXrn` (`20261011T140307Z-168360`) replay đủ chain `UqHibT → DhqXrn`:
  source campaign `204` nhưng actual replay `403`, Directus từ chối cập nhật
  field `id`; restore PASS, exit `1`, `full_transition_chain`. Đây là mismatch
  precondition/policy/negative oracle, không kết luận accepted-negative defect.
- `UTk4sa` (`20261011T140452Z-169384`) không gửi target PATCH: parent `vfAiah`
  trả số ID khác transition mapping, report ghi `stateful_sequence_failed`,
  target `not-sent`, restore PASS, exit `1`. Đây là stateful artifact/precondition
  limitation, không phải kết luận API chấp nhận negative data.
- `6IayFG` (`20261011T140814Z-170794`) replay request-only
  `GET /items/qa_articles` với `offset` vượt safe-number; Directus trả `400
  INVALID_QUERY`, source/expected/actual đều `400`, restore PASS, exit `1`.
  Đây là schema semantic/generator-positive candidate, không phải product
  defect; artifact không có parent chain để suy diễn full-state.
- `6THjzP` (`20261011T141024Z-171863`) replay request-only
  `POST /items/qa_categories` với `name` integer; Directus trả `200` và ép
  response `name` thành string, source/actual `200` trái expected negative
  `400`, restore PASS, exit `1`. Đây là semantic coercion/negative-oracle
  mismatch, chưa phải product defect.
- `QPKZ6w` (`20261011T141213Z-172805`) replay
  `GET /items/qa_articles/7?fields=title,author.name`; response `200` chỉ có
  `title`, schema check ghi thiếu `score`, restore PASS. Trạng thái `reproduced`
  và exit `0` chỉ xác nhận tái hiện request; đây là schema/projection contract
  gap, không phải API contract PASS.

Triage bổ sung trên campaign v2 được ghi đầy đủ tại
[`evidence/failure-triage-v2-2026-10-11.md`](../evidence/failure-triage-v2-2026-10-11.md).
Các case `Q8K5Nh`, `lwZKEo`, `3Ble8Q`, `vx21yF`, `Z6K7ww` và request cuối của
`CkqaOB` có replay request cụ thể với restore PASS. `VbURdO` và `pM4r4g` giữ
`mismatch`/unresolved vì precondition hoặc parent transition chưa đủ để kết luận.
Từ commit `baaee4b`, replay sẽ dựng parent chain khi event artifact có đủ case và
interaction liên quan; nếu không đủ, harness vẫn chỉ gửi interaction cuối và ghi
rõ phạm vi.

Từ commit `64e88f9`, harness nhận diện `meta.phase.name=stateful` và không gọi
final request-only là full reproduction. Sau commit `baaee4b`, `pM4r4g`
(`20261011T131321Z-144935`) ghi `replay_scope=full_transition_chain`,
`sequence_replayed=true`, parent `mvlcIV` HTTP 200, final PATCH HTTP 200 trong
khi campaign negative oracle kỳ vọng non-2xx; restore PASS và exit `1`.
`CkqaOB` (`20261011T131350Z-145631`) không có parent case trong artifact, nên
ghi `reproduced_request_only`, `sequence_replayed=false`, final HTTP 500,
restore PASS và exit `1`. Case non-stateful `Q8K5Nh`
(`20261011T123735Z-132524`) vẫn ghi `status=reproduced`, restore PASS và exit
`0`; sanity recheck sau chain hardening ở run `20261011T131702Z-146905` cũng
PASS với restore PASS.

### Kiểm tra oracle status của replay

Một audit positive chain phát hiện report cũ có thể để `expected_status=null` khi
case không có check failure, làm mọi status replay bị coi là `reproduced`. Commit
`a713481` sửa fallback này: status nguồn được dùng làm expected và được lưu riêng
ở `source_status`; không sửa artifact cũ hoặc nới assertion.

- `tFjhQT`, run `20261011T132550Z-151921` dưới HEAD `916152e`: chain `D3mEEJ → tFjhQT` được replay,
  source/expected `200`, actual `403`, restore PASS, status `mismatch`, exit `1`.
  Đây là sai khác precondition/stateful cần triage, không phải product defect đã
  xác nhận.
- `Q8K5Nh`, run `20261011T132604Z-152556` dưới cùng HEAD: source/expected/actual đều `403`,
  restore PASS, status `reproduced`, exit `0`.

Run `20261011T131957Z-148748` trước commit sửa vẫn được giữ như lịch sử; report
`reproduced` của `tFjhQT` trong run đó không dùng làm bằng chứng cuối vì metadata
ghi working tree dirty và bug oracle khi ấy chưa được sửa.

### Recheck stateful chain có parent tạo item

Để kiểm tra nhánh full-chain ngoài ca mismatch, `aZmz3k` được replay dưới HEAD
`3960f55` ở run `20261011T133817Z-157078`. Parent `C7nkph` là POST category
HTTP 200, target GET HTTP 200; report ghi `source_status=200`,
`expected_status=200`, `actual_status=200`, `replay_scope=full_transition_chain`,
`sequence_replayed=true`, restore PASS và exit `0`. Đây là bằng chứng full-chain
replay thành công trên baseline hiện tại.

Ca `Ag8Csb` ở run `20261011T133626Z-155874` được giữ riêng: parent GET list trả
HTTP 200 nhưng source transition có 100 ID (bao gồm `298`), trong khi fixture
snapshot hiện tại chỉ có 3 category và không có `298`. Harness ghi
`stateful_sequence_failed`, không gửi target request, restore PASS và exit `1`;
đây là thiếu precondition/stateful artifact, không phải product defect và không
được đổi thành `reproduced`.

Checkpoint Reader v2 được replay bằng `reader-visibility` ở run
`20261011T084935Z-74564` và full invariant `20261011T105236Z-105096`: request
projection hợp lệ trả sáu published fixture; request thêm `internal_notes` bị
Directus từ chối HTTP 403; Reader PATCH bị từ chối và Editor read-back không đổi.

## Artefact và phân loại

Mỗi replay ghi `metadata.json`, `run.log`, `invariant-report.json`, các response body đã chọn và `reproducer-<case>.json` khi failed/blocked. Reproducer không chứa credential; login response không ghi ra file.

Triage phải phân biệt:

- `product`: hành vi Directus trái với contract/oracle đã xác minh;
- `schema`: OpenAPI thiếu/sai contract hoặc response shape;
- `harness/fixture`: precondition, seed, oracle hoặc restore sai;
- `environment`: Docker/license/network/runtime;
- `unconfirmed`: cần replay độc lập hoặc bằng chứng thêm.

Một Schemathesis check failure không tự động là defect; phải gom theo nguyên nhân và replay trước khi kết luận.
