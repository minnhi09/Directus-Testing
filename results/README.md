# Kết quả đã lưu

Bản rút gọn của các lượt chạy, đã bỏ giá trị bí mật. Dữ liệu thô của mỗi lượt nằm trong `artifacts/runs/` trên máy chạy và không đưa lên Git.

| Thư mục | Nội dung |
|---|---|
| `test-cases/` | 13 ca nghiệp vụ, chạy ngày 26/11/2026: `scenario-report.json` (TC01 – TC06), `designed-report.json` và `case-*.json` (TC07 – TC13), thông tin lượt chạy. Kết quả 12 đạt, 1 không đạt (`TC13`) |
| `test-cases/tc13-root-cause/` | Nguyên nhân của `TC13` (phân tích ngày 16/11/2026): trích đoạn mã nguồn Directus tại phiên bản được cố định và kết quả kiểm lại phản hồi |
| `invariants/` | 11 phép kiểm quy tắc, chạy ngày 26/11/2026: `invariant-report.json`, yêu cầu tái hiện của hai phép không đạt. Kết quả 9 đạt, 2 không đạt (`Q06`, `Q07`) |
| `campaign/` | 18 lượt sinh tự động ngày 24/11/2026: tóm tắt từng lượt và phản hồi của 62 tổ hợp vai trò – thao tác |
| `coverage/` | Độ bao phủ theo tài liệu API, theo thao tác, nhóm và giá trị khởi tạo |
| `failures/` | 237 nhóm sai lệch, thống kê, mẫu yêu cầu để tái hiện, kết quả gửi lại và trích nhật ký máy chủ |
| `side-effects/` | Kết quả thăm dò các thao tác có tác dụng phụ (đăng nhập, đăng xuất, nhập dữ liệu, xóa bộ nhớ đệm) |

Mã lượt chạy ghi theo giờ quốc tế, nên các lượt ngày 26/11 theo giờ Việt Nam có mã bắt đầu bằng `20261125`.

## So sánh kết quả chạy lại

Chạy các lệnh trong [README](../README.md), rồi đối chiếu tệp trong `artifacts/runs/<run_id>/` với tệp đã lưu:

| Lệnh | Tệp của lượt mới | So với |
|---|---|---|
| `test scenarios` | `scenario-report.json` | `test-cases/scenario-report.json` |
| `test designed --selection course` | `designed-report.json` | `test-cases/designed-report.json` |
| `test invariants` | `invariant-report.json` | `invariants/invariant-report.json` |
| `test raw`, `test guided` | Chạy các lệnh tổng hợp với `--out` | `campaign/`, `coverage/`, `failures/` |

Tên hiển thị `Scenario S1` – `S6`, `Designed P3-…` và `Invariant …` ứng với mã `TC`, `Q` theo bảng trong README. So kết luận đạt hay không đạt của từng mã; mã bản ghi, thời gian và mã lượt chạy sẽ khác. Số liệu sinh tự động có thể khác, nhất là cách chạy `guided`; so sánh theo loại sai lệch và nguyên nhân.

## Mã nguyên nhân

Tệp trong `failures/` dùng mã `RC`, báo cáo dùng mã `L` và `SL`.

| Trong tệp | Trong báo cáo | Nguyên nhân |
|---|---|---|
| `RC02` | L1 | Tham số tổng hợp (aggregate) sai cấu trúc |
| `RC04` | L2 | Chuỗi chứa ký tự rỗng (U+0000) |
| `RC01` | L3 | Mã bản ghi vượt giới hạn số nguyên của cơ sở dữ liệu |
| `RC13` | L4 | Mã bản ghi hoặc mã liên kết sai kiểu, hoặc cực lớn |
| `RC03` | L5 | Thời điểm xuất bản sai kiểu |
| `RC12` | L6 | Danh sách gửi lên chứa phần tử rỗng (null) |
| `RC14` | L7 | Xuất CSV với trường không tồn tại |
| `RC15` | L8 | Số trang nhân số bản ghi mỗi trang vượt giới hạn số |
| `RC16` | L9 | Tham số `groupBy` đặt dấu `)` trước `(` |
| `RC05` | Hành vi mức thấp | `TRACE`, `PUT` nhận 404 thay vì 405 |
| `RC06` | SL1 | Trả mã 204 trong khi tài liệu ghi 200 |
| `RC07` | SL2 | Mã lỗi 4xx không được khai báo |
| `RC08` | SL3 | Kiểu nội dung khác mô tả |
| `RC09` | SL4 | Mô tả cấu trúc phản hồi quá cứng |
| `RC10` | SL5 | Yêu cầu đúng theo tài liệu vẫn bị từ chối |
| `RC11` | Chưa kết luận | Dữ liệu sai theo tài liệu nhưng được chấp nhận |
