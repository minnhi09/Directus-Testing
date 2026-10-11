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

Harness tìm case trong `schemathesis-events.ndjson`, giới hạn replay vào hai collection lab, dùng token Editor hiện tại, chụp snapshot trước request và restore sau request. Body fuzz được giải mã vào file nhị phân tạm trong artifact rồi truyền bằng `curl --data-binary @file`, nên payload chứa byte NUL không bị mất qua biến Bash. Kết quả ghi `schemathesis-case.json`, response, `reproducer-schemathesis-<case-id>.json` và status `reproduced`/`mismatch`. Case không tìm thấy hoặc ngoài allowlist bị từ chối, không gửi request tùy ý.

## Case IDs ổn định

| Case | Chuỗi kiểm tra | Khi nào blocked |
|---|---|---|
| `auth-invalid-token` | GET `/users/me` với token giả; token phải bị từ chối | Network/precondition không có response |
| `anonymous-denied` | Anonymous GET hai collection | Network error |
| `editor-crud` | Editor create → read → PATCH → read → DELETE → read | Editor login/fixture không sẵn sàng |
| `positive-operations` | Positive create/read/PATCH/delete cho đủ 10 operation của hai collection | Editor login/fixture hoặc permission CRUD không sẵn sàng |
| `query-fixture` | Filter published, sort, projection, hai page | Fixture map không khớp dữ liệu |
| `aggregate-query-robustness` | GET query tối giản `fields=&aggregate={"foo":1}`, yêu cầu không có 5xx | Không có API response |
| `relation-nullification` | Tạo category/article, xóa category, kiểm tra FK thành null | Không tạo được relation probe |
| `invalid-field-rejection` | Gửi status/score ngoài contract và kiểm tra không tạo row | Network/read-back precondition |
| `reader-visibility` | Reader đọc published và thử projection có `internal_notes` | Reader schema thiếu operation |
| `reader-write` | Reader PATCH target published, Editor kiểm tra dữ liệu không đổi | Reader schema thiếu PATCH |

`positive-operations` được kiểm tra trong invariant run `20261011T043809Z-24724`;
các replay pass trước đó gồm `editor-crud` ở run `20261011T040109Z-19973`,
`query-fixture` ở `20261011T035618Z-14109`, `auth-invalid-token` ở
`20261011T035623Z-14472`, `anonymous-denied` ở `20261011T035408Z-12774` và
Schemathesis case `ralwaW` ở run `20261011T040346Z-22406`. Đây là bằng chứng
local trên một baseline, không phải kiểm tra chéo máy thứ hai.

`aggregate-query-robustness` là regression probe deterministic được version hóa
trong `scripts/invariants.py`, nên clone sạch vẫn replay được mà không cần
Schemathesis artifact. Trên baseline hiện tại, run `20261011T080746Z-51887`
trả `500` và exit `1` đúng theo assertion; đây là failure cần triage, không phải
được chuyển thành pass bằng cách nới expected.

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

## Artefact và phân loại

Mỗi replay ghi `metadata.json`, `run.log`, `invariant-report.json`, các response body đã chọn và `reproducer-<case>.json` khi failed/blocked. Reproducer không chứa credential; login response không ghi ra file.

Triage phải phân biệt:

- `product`: hành vi Directus trái với contract/oracle đã xác minh;
- `schema`: OpenAPI thiếu/sai contract hoặc response shape;
- `harness/fixture`: precondition, seed, oracle hoặc restore sai;
- `environment`: Docker/license/network/runtime;
- `unconfirmed`: cần replay độc lập hoặc bằng chứng thêm.

Một Schemathesis check failure không tự động là defect; phải gom theo nguyên nhân và replay trước khi kết luận.
