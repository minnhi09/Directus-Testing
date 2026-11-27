# Kết quả đã lưu

Bản rút gọn của các lượt chạy, đã bỏ giá trị bí mật. Dữ liệu thô của mỗi lượt nằm trong `artifacts/runs/` trên máy chạy và không đưa lên Git.

| Thư mục | Nội dung |
|---|---|
| `test-cases/` | 13 ca nghiệp vụ, đợt chạy ngày 16/11/2026: `scenario-report.json` (TC01 – TC06), `designed-report.json` và `case-*.json` (TC07 – TC13), thông tin lượt chạy. Kết quả 12 đạt, 1 không đạt (`TC13`) |
| `test-cases/tc13-root-cause/` | Nguyên nhân của `TC13`: trích đoạn mã nguồn Directus tại phiên bản được cố định và kết quả kiểm lại phản hồi |
| `campaign/` | 18 lượt sinh tự động ngày 24/11/2026: tóm tắt từng lượt và phản hồi của 62 tổ hợp vai trò – thao tác |
| `coverage/` | Độ bao phủ theo tài liệu API, theo thao tác, nhóm và giá trị khởi tạo |
| `failures/` | 237 nhóm sai lệch, thống kê, mẫu yêu cầu để tái hiện, kết quả gửi lại và trích nhật ký máy chủ |
| `side-effects/` | Kết quả thăm dò các thao tác có tác dụng phụ (đăng nhập, đăng xuất, nhập dữ liệu, xóa bộ nhớ đệm) |

Số liệu của một lần chạy mới có thể khác, nhất là cách chạy `guided`; so sánh theo loại sai lệch và nguyên nhân.
