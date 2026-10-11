# Triage campaign Schemathesis — 2026-10-11

Tài liệu này phân loại các kết quả campaign đã chạy trên baseline Directus
12.5.0 trong project `r06-k05`. Các con số failure là số của Schemathesis,
không phải số defect độc lập.

## Phạm vi và bằng chứng

- Raw: run `20261011T050204Z-28735`, seed `101/202/303`, 10/10 operation mỗi seed,
  lần lượt 59/65/51 case, restore đều PASS.
- Guided: run `20261011T060247Z-30882`, seed `101/202/303`, 10/10 operation mỗi seed,
  lần lượt 5.809/5.874/5.899 case, restore đều PASS.
- Raw schema hash: `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`.
- Guided overlay hash: `dc3f057aefb095c4c51ddb712de33d762176d0472f8e7af313522b0551824d7e`.
- Harness sửa license configuration: commit `c7cc8d7`.
- Harness sửa replay binary body: commit `686f4d1`.

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

## Chưa được kết luận

- Các `ServerError` và `JsonSchemaError` trong guided stateful campaign chưa có
  reproducer độc lập đủ precondition.
- Các status/content-type ngoài schema cần đối chiếu schema raw, overlay và
  hành vi đã pin trước khi tạo defect.
- Không có defect sản phẩm Directus nào được xác nhận trong checkpoint này.

## Điều kiện tiếp theo

1. Đặt license hợp lệ vào `config/lab.env` bằng `LICENSE_KEY`, không commit giá trị.
2. Recreate stack, xác minh `/license` có `custom_permission_rules_enabled` được
   bật, rồi chạy lại `seed` và export schema actor.
3. Chỉ khi Reader schema có operation article mới chạy S4–S6 và Reader invariants.
4. Dựng lại lab trên máy thứ hai và ghi review thực tế; không dùng bằng chứng
   local này để tuyên bố G1.
