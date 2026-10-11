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

`status=reproduced` của harness ở case stateful chỉ nói request cuối được gửi
lại và cho cùng status trong lần chạy đó. Harness hiện tìm interaction cuối
trong event stream, không tự tái dựng toàn bộ `parent_id`/transition chain trước
đó. Vì vậy `CkqaOB` là bằng chứng mạnh cho candidate ở request cuối, nhưng chưa
phải reproducer đầy đủ của chuỗi stateful; `VbURdO` và `pM4r4g` phải giữ trạng
thái unresolved do mismatch.

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
   exit `1` trong run `20261011T105242Z-105524`; báo cáo này không thay đổi
   kết luận đó.

## Việc còn lại

- Nếu cần đóng các case stateful, harness phải lưu và replay chuỗi transition
  đầy đủ, hoặc phải ghi rõ chúng là final-request-only và unresolved. Không
  được dùng replay trực tiếp hiện tại để tuyên bố tái lập độc lập toàn bộ state.
- Đối chiếu response map/content type/POST shape với contract Directus đã pin;
  nếu tạo overlay thì chỉ sửa bản `guided`, giữ raw snapshot bất biến và lưu
  diff/lý do.
- Giữ nguyên exit code campaign, report và artifact hiện tại; không thêm
  skip/xfail hoặc nới assertion để làm đẹp kết quả.

Không có credential, token, mật khẩu hoặc toàn bộ request body nhạy cảm nào
được ghi trong tài liệu này.
