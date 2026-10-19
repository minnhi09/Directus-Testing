# Swagger UI cho lab Directus

Swagger UI là giao diện cục bộ để xem OpenAPI theo actor và gửi request thử. Lành phụ trách và nghiệm thu toàn bộ phần này; Codex hỗ trợ triển khai theo yêu cầu. Giao diện không thay thế campaign Schemathesis hoặc bằng chứng kiểm thử đã lưu.

## Chuẩn bị và mở giao diện

Trên máy đã có `config/lab.env` hợp lệ và Docker, chạy tuần tự:

```bash
./lab.sh up
./lab.sh seed
./lab.sh export-schema
./lab.sh swagger up
```

Trên Windows PowerShell, dùng `.\scripts\run-lab.ps1` với cùng tham số.

Mở **http://127.0.0.1:8086**; phải dùng `127.0.0.1` vì Directus chỉ cho phép đúng origin này. `./lab.sh swagger down` chỉ dừng giao diện, không dừng Directus hoặc xóa database. `./lab.sh down` dừng cả lab, vẫn giữ volume database.

Lệnh `swagger up` kiểm tra đúng project `r06-k05`, checkout sở hữu container, image Directus, cấu hình CORS đang chạy, fixture map và schema Editor/Reader đã xuất. Nếu thiếu schema, chạy lại `seed` rồi `export-schema`; nếu Directus còn chạy với cấu hình CORS cũ, áp dụng Compose mới cho riêng service `directus` rồi kiểm tra health. Cổng 8086 phải còn trống.

Compose project `r06-k05` chỉ dùng được từ một checkout tại một thời điểm. Nếu `doctor` hoặc lệnh lab báo container thuộc checkout khác, hãy dùng đúng checkout đang sở hữu lab; không chạy `up`, `down` hay `reset` từ checkout này để thay đổi lab của checkout kia. Kiểm tra này cũng áp dụng cho `swagger up|down`.

## Xem và thử API

Chọn **Editor** hoặc **Reader** trong danh sách schema. Mỗi file chứa toàn bộ endpoint Directus đã xuất cho actor đó, bao gồm một số endpoint ngoài 10 thao tác QA của campaign. Chỉ sự xuất hiện của endpoint trong Swagger không chứng minh thao tác đã được kiểm thử.

1. Mở `POST /auth/login`, nhập email và password của actor tương ứng từ cấu hình cục bộ, rồi bấm **Execute**.
2. Sao chép `data.access_token` trong response. Bấm **Authorize**, nhập `Bearer <access_token>` vào mục `Auth`, rồi xác nhận.
3. Thử `GET /items/qa_articles` hoặc `GET /items/qa_categories`. Với Editor, có thể thử CRUD trên bản ghi tạm và dọn bản ghi đó sau khi thử. Với Reader, chỉ gửi operation có trong schema Reader; không suy việc operation bị lọc khỏi schema là một ca quyền đã chạy.

Token chỉ dùng trong phiên trình duyệt; Swagger không lưu quyền qua lần tải lại. Không chép token, mật khẩu, response đăng nhập hay request chứa bí mật vào tài liệu, screenshot hoặc artefact công bố. Khi hết phiên, bấm **Logout** trong Authorize hoặc đóng tab.

## Nguồn schema và giới hạn

Nguồn gốc là `runtime/schemas/<fixture_version>/editor.json` và `reader.json`, được Directus xuất sau khi seed. `swagger up` tạo bản hiển thị tại `runtime/swagger/<fixture_version>/` và lưu `swagger-schema-manifest.json` cùng diff của từng actor trong `artifacts/runs/<run_id>/`. Bản hiển thị chỉ bổ sung yêu cầu `Auth` cho operation thiếu khai báo, ngoại trừ các endpoint đăng nhập và endpoint công khai đã xác định. Hash của file gốc được kiểm tra trước và sau; Schemathesis luôn dùng schema gốc hoặc overlay campaign riêng.

OpenAPI không mô tả hết policy, trạng thái database và quy tắc nghiệp vụ. Một request hợp schema vẫn có thể bị Directus từ chối; “Try it out” không thay thế scenario, invariant hoặc triage. Swagger UI chạy trong Compose profile `docs`, bind `127.0.0.1:8086`; trình duyệt gửi request tới Directus `127.0.0.1:8055` qua CORS chỉ cho phép origin Swagger. Validator trực tuyến và lưu token qua lần tải lại đều bị tắt.
