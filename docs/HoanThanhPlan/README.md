# Hồ sơ R06–K05

> **Bản lưu lịch sử.** Tài liệu này được viết trước khi dự án thu nhỏ về đúng phạm vi K05 (23/11/2026) và còn nhắc tới nội dung đã bỏ (bộ 170 ca v2, thí nghiệm pairwise, khung coverage/CI nhóm tự đặt) cũng như cách hiểu `max_time` đã được đính chính. **Báo cáo hiện hành:** [BAO_CAO_CUOI_KY_K05.md](../k05/BAO_CAO_CUOI_KY_K05.md); hai báo cáo cuối kỳ cũ đã bị xóa ngày 24/11/2026 (còn trong lịch sử Git). Số liệu ở đây không được dùng thay cho báo cáo hiện hành.

**Phạm vi hiện hành:** 13 ca/kịch bản đại diện + kiểm thử sinh từ OpenAPI bằng Schemathesis + phân tích lỗi + thí nghiệm chi phí 36/9. Giữ kết quả thực tế đến 18/10/2026; cập nhật cách sử dụng ngày 19/10 không phải một lượt nghiệm thu API mới.

## Đọc theo thứ tự

1. [Báo cáo cuối kỳ K05](../k05/BAO_CAO_CUOI_KY_K05.md): bản nộp theo A–H; 13 ca tại E.2, kết quả tại G.1.
2. [README chạy chương trình](../../README.md): chuẩn bị lab và hai lệnh chạy bộ đại diện.
3. [Phạm vi và việc còn lại](LO_TRINH_TOI_GIAN_R06_K05.md): những gì cần giữ và điều kiện hoàn tất.

Slide/demo, gói nộp và đánh giá đóng góp còn cần nhóm hoàn tất; không coi chỉnh sửa tài liệu là đã nộp hoặc đã bảo vệ.

## Chỉ tra cứu khi cần

- [Đặc tả chi tiết](01-yeu-cau-va-dac-ta.md), [review OpenAPI](02-danh-gia-openapi-va-sinh-test.md), [thiết kế mở rộng](03-thiet-ke-test-va-coverage.md).
- [Finding và nguyên nhân](05-finding-register.md), số đo chi phí *(tệp đã bị xóa khỏi phạm vi K05; xem lịch sử Git)*.
- [Nghiệm thu 18/10](08-bao-cao-nghiem-thu.md), [kết quả 257 ID](08-ket-qua-case.csv).
- [Hồ sơ và bằng chứng lịch sử](tai-lieu-bo-tro/README.md).

Danh mục mở rộng ghi **184 PASS, 7 FAIL, 1 OPEN, 65 NOT_RUN**; không chuyển thành kết quả của một lượt chạy 13 ca. Mẫu số coverage cũ giữ nguyên. Kế hoạch theo phase và bảng truy vết chi tiết là tài liệu tra cứu; không yêu cầu hoàn thành thêm mọi ca, mọi câu hỏi mở hay Phase 7 CI/CD.
