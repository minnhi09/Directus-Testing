# Điều kiện chạy và tiêu chí hoàn tất trong phạm vi môn học

**Cập nhật 19/10/2026 theo phạm vi thu gọn.** Bản tiêu chí chi tiết trước đây được giữ trong `tai-lieu-bo-tro/truoc-rut-gon-mon-hoc-20261019.zip`. Thay đổi này xác định công việc còn phải làm; không sửa trạng thái hoặc mẫu số kết quả đã chạy.

## Trước khi chạy

- Đúng lab, phiên bản, vai trò, schema và bộ dữ liệu mẫu; các ID lấy từ ánh xạ/phản hồi.
- Đầu vào và expected có căn cứ; ca ngoài quyền cần mẫu kiểm chứng chứng minh dữ liệu/tài khoản/đường API đang hoạt động.
- Chạy các suite ghi tuần tự, có dọn dữ liệu/khôi phục và lưu report theo run ID.

Thiếu điều kiện thì báo BLOCKED/chưa chạy được; không coi lỗi mạng hoặc cấu hình là một ca negative đạt.

## Khi đánh giá ca

| Nội dung | Điều kiện đánh giá |
|---|---|
| CRUD | Thành công đúng nghiệp vụ, đọc lại đúng dữ liệu, PATCH giữ trường không gửi, xóa đúng tài nguyên |
| Query | Đúng tập bản ghi, thứ tự và phần dữ liệu theo dữ liệu mẫu biết trước |
| Quyền | Đúng vai trò và nguyên nhân từ chối; không lộ dữ liệu; yêu cầu ghi bị từ chối không làm đổi bản ghi |
| Biên score | -1/6 bị từ chối và không tạo bài; 0/5 được lưu và đọc lại đúng |
| Hợp đồng OpenAPI | Kiểm phản hồi theo đặc tả gốc; sai lệch vẫn FAIL dù nghiệp vụ thành công |
| Khôi phục | Ghi kết quả riêng; lỗi dọn dữ liệu phải được xử lý trước lượt ghi tiếp |

Không đổi expected theo actual, nới assertion, tắt check hoặc bỏ ca FAIL để có kết quả đạt. PASS/FAIL/OPEN/NOT_RUN/BLOCKED giữ đúng ý nghĩa trong báo cáo.

## Khi hoàn tất phần kỹ thuật

1. Có đặc tả/yêu cầu và 13 ca đại diện tại E.3 của báo cáo; lựa chọn có tên `course` gồm bảy ca bổ sung cho sáu scenario.
2. Có kết quả gốc và giới hạn của các ca; khi chạy mới phải báo run ID/kết quả mới, không dùng lịch sử thay cho một lượt mới.
3. Có bằng chứng 10/10 thao tác API có ca nghiệp vụ thành công và bằng chứng Schemathesis sinh/kiểm test từ OpenAPI. Hai loại bằng chứng giữ riêng.
4. Có report/reproducer, phân tích nguyên nhân đại diện và số đo chi phí 36/9.
5. Có hướng dẫn dựng/chạy, phiên bản và gói mã/evidence chọn lọc.

Không yêu cầu toàn SUT PASS, tất cả 257 ca được chạy, mọi finding được sửa hoặc mọi chỉ số coverage đạt 100%. Các phần chưa kiểm và vấn đề còn mở vẫn phải công bố. Hoàn tất đồ án còn cần slide/demo, đánh giá đóng góp và nộp theo lịch giảng viên.
