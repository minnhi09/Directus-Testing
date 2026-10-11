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
| `aggregate-query-robustness` | GET query tối giản `fields=&aggregate={"foo":1}`, yêu cầu không có 5xx | Không có API response |
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
Schemathesis artifact. Trên baseline v2, run `20261011T105242Z-105524` trả
`500` và exit `1` đúng theo assertion; đây là failure cần triage, không phải
được chuyển thành pass bằng cách nới expected. Run lịch sử `20261011T080746Z-51887`
được giữ để đối chiếu trước license.

`contract-schema-candidates` là probe contract độc lập, chạy tại commit
`7018107` ở run `20261011T130227Z-139257`. Probe tạo dữ liệu tạm bằng Editor,
đối chiếu POST response shape, export `text/csv` và DELETE `204` với
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
