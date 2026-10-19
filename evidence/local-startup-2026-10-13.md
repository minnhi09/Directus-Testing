# Chạy thử bản clone trên Windows — 13/10/2026

Đây là báo cáo lần chạy đầu, trước khi cấu hình license và sửa đầy đủ lỗi
Unicode/đường dẫn Windows. Kết quả mới thay thế nằm tại
[`windows-recheck-2026-10-13.md`](windows-recheck-2026-10-13.md).

Đây là lần dựng mới trên máy hiện tại, không phải kết quả các run Linux cũ.
Harness HEAD: `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, working tree dirty.
Run ID dùng UTC; ngày báo cáo theo Asia/Bangkok.

## Kết quả thực tế

| Lệnh | Run ID | Kết quả |
|---|---|---|
| `up` | `20261012T174426Z-955` | PASS, exit 0; PostgreSQL, Directus và runner healthy |
| `seed` | `20261012T174459Z-1353` | Exit 1; schema, 3 category, 12 article và actor đã tạo; Reader policy bị chặn bởi license |
| `smoke` | `20261012T174540Z-540` | Exit 1; validation score/status trả 400, quan hệ SET NULL PASS; Reader đọc article trả 403 |
| `test scenarios` | `20261012T174559Z-1178` | 3 passed, 0 failed, 3 blocked; exit 1 |
| `doctor` sau sửa Windows | `20261012T174706Z-1299` | PASS, exit 0; authenticated health đạt; entitlement custom rules false |

S1 CRUD Editor, S2 filter published và S3 sort/pagination đều PASS.
S4–S6 bị blocked do operation cần thiết không có trong schema Reader.
Không chạy campaign fuzz khi seed/policy chưa hoàn tất. Không thay assertion hoặc bypass license.

Trang `http://127.0.0.1:8055/admin` trả HTTP 200; `/server/ping` trả `pong`.
Không có trình duyệt kết nối qua công cụ UI, nên chưa xác minh giao diện bằng ảnh chụp.
Ứng dụng được giữ chạy để người dùng mở trực tiếp.

## Cấu hình và thay đổi cục bộ

- Tạo `config/lab.env` từ example với credential ngẫu nhiên, không in vào log; Git ignore file này. `LICENSE_KEY` để trống.
- File credential chỉ cấp quyền Windows cho tài khoản hiện tại.
- Tải đúng ba image theo tag/digest có sẵn trong `config/lab.env.example`.
- Bổ sung kiểm tra ACL Windows trong `lab.sh`, giữ kiểm tra mode Unix.
- Dùng `NUL` cho curl config trên Windows để authenticated health không lỗi do `/dev/null`.
- jq portable nằm tại `../tmp/lab-tools/`, checksum đã đối chiếu bản phát hành chính thức từ [jq](https://jqlang.org/download/). Wrapper dùng `-b` để giữ LF trên Git Bash.
- Không sửa các thay đổi có sẵn trong `scripts/invariants.py` và `scripts/lab-components.sh`; chưa commit/push.

## Mở và chạy lại trên máy này

Mở <http://127.0.0.1:8055/admin>. Email là `admin@example.com`;
mật khẩu là giá trị `ADMIN_PASSWORD` trong `config/lab.env` (giữ riêng trên máy).

Từ PowerShell tại thư mục workspace:

```powershell
& .\tmp\lab-tools\run-lab.ps1 doctor
& .\tmp\lab-tools\run-lab.ps1 up
& .\tmp\lab-tools\run-lab.ps1 test scenarios
& .\tmp\lab-tools\run-lab.ps1 down
```

`down` giữ dữ liệu lab. Muốn hoàn tất Reader cần license Directus hợp lệ có
`custom_permission_rules_enabled=true`, cấu hình cục bộ rồi chạy `up`, `seed`.
Snapshot OpenAPI cũ được giữ nguyên; không dùng chúng để khẳng định schema
runtime của lần dựng mới.
