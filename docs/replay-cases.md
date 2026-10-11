# Replay và reproducer

## Chạy replay

Replay dùng credential hiện tại từ `config/lab.env`, fixture map hiện tại và Directus đang chạy trong lab:

```bash
./lab.sh replay editor-crud
./lab.sh replay anonymous-denied
./lab.sh replay query-fixture
```

Không truyền token, password hoặc ID tự sinh trong command. `runtime/fixture-ids.json` là nguồn ánh xạ tên fixture → ID thật.

Với case ID do Schemathesis in trong report, dùng cùng interface:

```bash
./lab.sh replay ralwaW
```

Harness tìm case trong `schemathesis-events.ndjson`, giới hạn replay vào hai collection lab, dùng token Editor hiện tại, chụp snapshot trước request và restore sau request. Kết quả ghi `schemathesis-case.json`, response, `reproducer-schemathesis-<case-id>.json` và status `reproduced`/`mismatch`. Case không tìm thấy hoặc ngoài allowlist bị từ chối, không gửi request tùy ý.

## Case IDs ổn định

| Case | Chuỗi kiểm tra | Khi nào blocked |
|---|---|---|
| `auth-invalid-token` | GET `/users/me` với token giả; token phải bị từ chối | Network/precondition không có response |
| `anonymous-denied` | Anonymous GET hai collection | Network error |
| `editor-crud` | Editor create → read → PATCH → read → DELETE → read | Editor login/fixture không sẵn sàng |
| `query-fixture` | Filter published, sort, projection, hai page | Fixture map không khớp dữ liệu |
| `relation-nullification` | Tạo category/article, xóa category, kiểm tra FK thành null | Không tạo được relation probe |
| `invalid-field-rejection` | Gửi status/score ngoài contract và kiểm tra không tạo row | Network/read-back precondition |
| `reader-visibility` | Reader đọc published và thử projection có `internal_notes` | Reader schema thiếu operation |
| `reader-write` | Reader PATCH target published, Editor kiểm tra dữ liệu không đổi | Reader schema thiếu PATCH |

Các replay pass mới nhất: `editor-crud` ở run `20261011T040109Z-19973`, `query-fixture` ở `20261011T035618Z-14109`, `auth-invalid-token` ở `20261011T035623Z-14472`, `anonymous-denied` ở `20261011T035408Z-12774` và Schemathesis case `ralwaW` ở run `20261011T040346Z-22406`. Đây là bằng chứng local trên một baseline, không phải kiểm tra chéo máy thứ hai.

## Artefact và phân loại

Mỗi replay ghi `metadata.json`, `run.log`, `invariant-report.json`, các response body đã chọn và `reproducer-<case>.json` khi failed/blocked. Reproducer không chứa credential; login response không ghi ra file.

Triage phải phân biệt:

- `product`: hành vi Directus trái với contract/oracle đã xác minh;
- `schema`: OpenAPI thiếu/sai contract hoặc response shape;
- `harness/fixture`: precondition, seed, oracle hoặc restore sai;
- `environment`: Docker/license/network/runtime;
- `unconfirmed`: cần replay độc lập hoặc bằng chứng thêm.

Một Schemathesis check failure không tự động là defect; phải gom theo nguyên nhân và replay trước khi kết luận.
