# Ma trận quyền và schema theo actor

## Contract mục tiêu

| Actor | `qa_categories` | `qa_articles` | Giới hạn bắt buộc |
|---|---|---|---|
| Admin bootstrap | Quản lý schema/policy và dữ liệu | Quản lý schema/policy và dữ liệu | Chỉ dùng để seed, snapshot và kiểm tra baseline; không dùng làm actor fuzz mặc định |
| Editor | CRUD trong API | CRUD trong API | Không có quyền quản trị Studio trong contract harness |
| Reader | Đọc | Chỉ đọc article `published` | Không thấy `internal_notes`, không ghi dữ liệu |
| Anonymous | Không truy cập | Không truy cập | Không có bearer token |

Reader và anonymous được đánh giá từ OpenAPI động theo accountability của từng request. Việc một operation bị lọc khỏi schema là bằng chứng schema không xuất operation đó; harness không gửi request bị cấm để suy diễn thành công quyền.

## Kết quả baseline đã quan sát

Run export `20261011T035010Z-8515` sau khi seed fixture đã lưu schema raw bất biến:

| Actor | Schema | SHA-256 | Operation `/items/qa_*` |
|---|---|---|---:|
| Admin | `runtime/schemas/r06-k05-v1/admin.json` | `993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e` | 14 |
| Editor | `runtime/schemas/r06-k05-v1/editor.json` | `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26` | 14 |
| Reader | `runtime/schemas/r06-k05-v1/reader.json` | `20fbfe9a517710ac73d05622f4b158bab4ccbcd96da51ec61363268ed92683cb` | 2 |
| Anonymous | `runtime/schemas/r06-k05-v1/anonymous.json` | `2070c25c68193a4a42501935974bb3045697aceb1fe072bb3461f43c0a0342b3` | 0 |

Editor có 14 operation vì schema Directus còn xuất bulk `PATCH`/`DELETE` ở đường dẫn list. Campaign chính chọn đúng 10 method–path đã phê duyệt và không đưa bulk operation vào allowlist.

Baseline `/license` trả `custom_permission_rules_enabled=false`. Vì vậy bước seed dừng trước khi tạo filter `status=published`, field restriction `internal_notes` và permission update cho Reader. Không đưa license key vào Git, không sửa DB trực tiếp và không dùng Admin để giả lập Reader.

Các bằng chứng đã chạy:

- Anonymous GET tới hai collection trả non-2xx trong replay `anonymous-denied`.
- Reader visibility và Reader write được ghi `blocked` vì operation article không xuất hiện trong `reader.json`; không có request forbidden được gửi.
- Editor CRUD/query và field/foreign-key validation chạy được độc lập.

## Cách mở khóa Reader

1. Cấu hình license hợp lệ bên ngoài repository theo quyền của môi trường lab.
2. Xác minh lại `/license` bằng Admin và ghi kết quả vào run metadata.
3. Dùng một lab đã reset an toàn hoặc snapshot được phê duyệt; chạy `./lab.sh seed`.
4. Xuất lại schema bằng `./lab.sh export-schema`. Nếu raw snapshot đã tồn tại mà hash thay đổi, giữ snapshot cũ và xử lý thay đổi như một baseline mới; không overwrite âm thầm.
5. Chỉ khi schema Reader có operation cần thiết mới chạy lại S4–S6 và invariant Reader.
