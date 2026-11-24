# Tài liệu hỗ trợ và bản sao lịch sử

- `phase0-20261018/`: checkpoint.zip, manifest checksum và Git state trước Phase 0.
- `phase1-20261018/`: nguồn đầu vào, source đúng commit, bản traceability trước khi bổ sung và kết quả kiểm tra tài liệu tại từng thời điểm.
- `phase2-20261018/`: audit bốn schema actor, diff raw/guided, bảy case trích xuất sạch header xác thực, source generator đúng pin và kết quả kiểm tra tài liệu. Các JSON mới phản ánh review ngày 18/10, không phải run kiểm thử mới.
- `phase3-20261018/`: catalog thiết kế JSON, fixture oracle nguồn tĩnh, oracle library, chứng minh pair coverage, source error class đúng pin, manifest đầu vào và validation. Đây là dữ liệu thiết kế; mọi case chưa được chạy mới.
- `phase4-20261018/`: source checkpoint trước/sau, runtime reports chọn lọc, gói evidence, probe runner pin, regression output, errata và validation. Có kiểm thử API thật, khác với các phase biên soạn trước; xem báo cáo Phase 4 để biết phạm vi PASS/FAIL/NOT_RUN.
- `cong-cu-kiem-ke/`: bản sao hai script đã dùng để lập bảng kiểm kê/truy vết. Đây là script một lần phục vụ audit, chưa được nghiệm thu thành công cụ bảo trì; không chạy lại để cập nhật hồ sơ. Các đường dẫn trong script phản ánh thời điểm biên soạn.

Bản sao ở đây được kiểm tra trùng SHA-256 với bản gốc tại `output/phase0-20261018/` và `output/phase1-20261018/`. Các bản gốc và raw artifact không bị di chuyển hay sửa nội dung.

Các manifest và bản lưu Markdown lịch sử giữ nguyên đường dẫn/nội dung lúc tạo để bảo toàn provenance; một số liên kết tương đối trong bản lưu không dùng làm điều hướng hiện hành. Đọc [mục lục hồ sơ](../README.md) và dùng [danh mục ánh xạ](../danh-muc-di-chuyen.json) để tìm bản sao trong thư mục này.

Không giải nén checkpoint đè lên checkout/DB hiện tại. Đây là checkpoint tệp, không có credential hoặc database để tự phục hồi toàn bộ hệ thống.
