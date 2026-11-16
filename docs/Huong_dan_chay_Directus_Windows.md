# Chạy Directus R06–K05 trên máy Windows hiện tại

Hướng dẫn này dùng workspace `D:\DAMH-full-recovery-2026-10-12`. Stack chạy bằng Docker, không cần build mã nguồn Directus để mở hệ thống.

## 1. Mở hệ thống

Mở Docker Desktop, đợi Docker Engine sẵn sàng. Sau đó mở PowerShell và chạy:

```powershell
Set-Location 'D:\DAMH-full-recovery-2026-10-12'
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 up
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 doctor
```

`up` khởi động stack và chờ Directus healthy. `doctor` kiểm tra công cụ, cấu hình, image, health có đăng nhập và trạng thái license. Hai lệnh thành công thì mở:

- Studio: <http://127.0.0.1:8055/admin>
- API liveness: <http://127.0.0.1:8055/server/ping> (phản hồi `pong`).

Đăng nhập Studio bằng email `admin@example.com`. Mật khẩu lấy từ dòng `ADMIN_PASSWORD=` trong `DAMH/config/lab.env`, dùng phần giá trị sau dấu `=`. Giữ mật khẩu và license trên máy, không gửi vào chat.

Sau khi đăng nhập, mở phần quản lý nội dung để xem `qa_categories` (danh mục) và `qa_articles` (bài viết). Dùng Admin cho giao diện Studio; Editor/Reader trong lab là tài khoản dùng qua API.

## 2. Dữ liệu mẫu

Dữ liệu hiện có đã nằm trong volume PostgreSQL. Khi mở lại hệ thống, không cần seed lại mỗi lần.

Nếu cần khởi tạo lại bộ mẫu theo cấu hình hiện có, dùng:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 seed
```

Lệnh seed chuẩn bị collection, quyền và dữ liệu mẫu của lab. Không dùng lệnh reset để khởi động thông thường.

## 3. Dừng hệ thống

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 down
```

`down` dừng stack và giữ volume dữ liệu. Lần sau dùng lại lệnh `up`.

## 4. Xác minh lần khởi động ngày 13/10/2026

- `up`: thành công, run `20261013T035929Z-1688`.
- `doctor` sau khởi động: thành công, run `20261013T040059Z-1536`.
- Directus 12.5.0, PostgreSQL 16-alpine và runner Schemathesis 4.30.0 đều healthy.
- `/server/ping`: HTTP 200, body `pong`; `/admin`: HTTP 200.
- Health có đăng nhập thành công; license active, custom permission rules bật.
- Truy vấn chỉ đọc xác nhận 3 danh mục và 12 bài viết. Không seed/reset hoặc chạy bộ kiểm thử K05 trong lần khởi động này.

Các ghi nhận trên là kiểm tra vận hành tại thời điểm khởi động, không phải kết quả kiểm thử K05 hay bằng chứng đã thao tác giao diện Studio.

## 5. Lưu ý khi chuyển máy

Launcher và jq wrapper đang ở `tmp/lab-tools` ngoài repository DAMH. Hướng dẫn này áp dụng cho workspace hiện tại; clone riêng DAMH sang máy mới sẽ chưa có các helper đó. Quy trình Bash và cấu hình máy mới nằm trong [README](../README.md). Không sao chép hay công bố credential/license cùng mã nguồn.
