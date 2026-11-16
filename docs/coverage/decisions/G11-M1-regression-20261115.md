# Quyết định nội bộ nhóm 11 — nguồn xác nhận trực tiếp

Ngày quyết định: 15/11/2026. Người xác nhận: người dùng trong phiên hiện tại, đại diện xác nhận kỹ thuật nội bộ nhóm 11; không suy tên/chữ ký hoặc danh tính giảng viên.

> Tôi xác nhận khóa subset M1 Regression gồm 13 alias TC01–TC13 trên qa_articles và qa_categories.
> Giữ nguyên kết quả lịch sử của TC13: business PASS, contract FAIL. Không sửa expected result hoặc xóa failure.
> Các chức năng khác của Directus vẫn phải được giữ trong System Inventory và backlog/UNKNOWN, không tự động chuyển thành NOT_APPLICABLE hoặc loại khỏi phạm vi kiểm thử toàn hệ thống.
> Đây là quyết định kỹ thuật nội bộ của nhóm 11, ngày 15/11/2026, nguồn là xác nhận trực tiếp này. Phạm vi nghiệm thu toàn hệ thống vẫn chưa được giảng viên xác nhận.
> Hãy ghi nhận quyết định, cập nhật bằng chứng và tiếp tục giải quyết các gap còn lại. Không coi toàn bộ M1 đã LOCKED nếu chưa đủ điều kiện.

Xác nhận thứ hai cùng thông điệp:

> Chưa xác nhận.
> Giảng viên yêu cầu kiểm thử toàn bộ hệ thống Directus và chứng minh độ bao phủ, nhưng chưa có quyết định cụ thể về việc bắt buộc hay loại trừ GraphQL, Data Studio, Realtime, SDK, AI/MCP và Deployments.
> Hãy tiếp tục kiểm kê đầy đủ các chức năng này, xác minh khả năng áp dụng trên phiên bản Directus đang kiểm thử và giữ những điểm chưa rõ ở trạng thái UNKNOWN hoặc gap tương ứng.
> Không tự ý đánh dấu NOT_APPLICABLE, loại khỏi mẫu số coverage hoặc coi đây là phạm vi đã được giảng viên phê duyệt.
> Tiếp tục các công việc kỹ thuật không phụ thuộc quyết định này; ghi BLOCKED đối với những đầu việc thực sự cần xác nhận phạm vi.

Đây là bản ghi thông điệp người dùng, không phải văn bản phê duyệt giảng viên, không là bằng chứng runtime hay chấp nhận defect TC13. Khóa subset requirement; policy chọn execution khai báo trước, hiện chưa có execution. Các nhóm khác không bị loại khỏi inventory.
