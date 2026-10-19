# R06–K05: phạm vi môn học và việc còn lại

**Cập nhật theo yêu cầu đơn giản hóa ngày 19/10/2026.** Đây là phạm vi thực hiện hiện hành; các kế hoạch và số liệu cũ dùng tra cứu. Số ca đại diện do nhóm chọn để trình bày, không phải chỉ tiêu do giảng viên ấn định.

## 1. Những gì nhóm cần làm và giải thích được

| Đầu ra | Nội dung giữ trong phạm vi chính |
|---|---|
| A–B: hiểu hệ thống | Directus, người dùng, hai collection, quan hệ, sơ đồ và các luồng dữ liệu liên quan |
| C: hệ thống chạy được | Docker, phiên bản cố định, dữ liệu mẫu và quyền; ba luồng CRUD, truy vấn, Reader |
| D–E: phương pháp và thiết kế | K05; yêu cầu → expected → 13 ca/kịch bản tại E.3 của báo cáo; minh họa phân vùng, biên, quyền |
| F: automation | Xuất OpenAPI theo actor, Schemathesis sinh request/check; sáu scenario và bảy ca bổ sung chạy bằng mã có sẵn |
| G: kết quả và nguyên nhân | Kết quả thật, một sai lệch POST phân tích sâu; aggregate 500 là ví dụ bổ sung có giới hạn; bảng chi phí 36/9 |
| H: chạy lại | Version/tag/SHA, cấu hình mẫu, schema, dữ liệu, report và reproducer chọn lọc; ghi mức đã xác minh |
| Tổ chức và nộp | Báo cáo, slide/demo, mã kiểm thử/dependency, đánh giá đóng góp thật và hạn theo lịch giảng viên |

Giữ hai collection, 10 cặp method–path, Editor/Reader/Anonymous và Admin phục vụ thiết lập. Không sửa baseline, fixture, policy, schema gốc hoặc assertion để rút ngắn công việc.

## 2. Bộ đại diện dùng như thế nào?

Bộ chính gồm **S1–S6 và 7 ca**: `P3-ST-01`, `P3-AUTHZ-DR-047`, `P3-SCORE-POST-MINUS1`, `P3-SCORE-POST-0`, `P3-SCORE-POST-5`, `P3-SCORE-POST-6`, `P3-CONTRACT-QA_ARTICLES-OBJECT`. Tổng là 13 ca/kịch bản có ID nguồn rõ ràng. CRUD bài viết dùng S1, nên không chạy thêm chuỗi P3-ST-02 chỉ để minh họa cùng luồng.

Trên lab đã chuẩn bị đúng cấu hình/schema/dữ liệu, chạy tuần tự:

```powershell
.\scripts\run-lab.ps1 doctor
.\scripts\run-lab.ps1 test scenarios
.\scripts\run-lab.ps1 test designed --selection course
```

Đọc hai report theo từng run ID, cùng kết quả khôi phục. Một ca hợp đồng FAIL có thể đồng thời tạo/đọc dữ liệu đúng nghiệp vụ. Không xem mã thoát 0 là bằng chứng toàn Directus đúng. Lựa chọn mới đã được kiểm bằng kiểm thử bộ chọn không gọi API; không tự coi đây là lượt chạy mới của cả bộ 13.

Các kết quả gốc của bộ được trích tại E.3/G.2 trong [báo cáo](09-bao-cao-cuoi-ky.md). Bằng chứng 10/10 thao tác nghiệp vụ giữ riêng; không suy ra con số đó chỉ từ tên hai kịch bản CRUD. Dùng schema/report/reproducer đã lưu để chứng minh K05, không lấy riêng 13 ca viết có chủ đích thay cho kiểm thử sinh tự động.

## 3. Những việc dừng mở rộng

- Không yêu cầu chạy đủ 118/257 ca, phủ mọi luật quyền/lớp dữ liệu hay chốt mọi hành vi ép kiểu, Unicode và thời gian.
- Không chạy lại campaign đã xong, tăng seed/ngân sách hoặc thêm thí nghiệm chỉ để viết báo cáo.
- Không điều tra tới cùng mọi phản hồi 500, xây thêm cơ chế replay hoặc sửa mã Directus upstream.
- Không thêm CI/CD, quét lỗ hổng, load test, frontend/GraphQL hay kỹ thuật nâng cao thứ hai.
- Không tạo thêm hồ sơ/checkpoint/ma trận cho từng bước. Bản lưu và mã hỗ trợ hiện có giữ để bảo toàn bằng chứng, không là checklist mới.
- Không buộc dựng máy thứ hai khi chưa có yêu cầu; vẫn cung cấp hướng dẫn máy mới và ghi rõ chưa xác minh ở đó.

Kiểm tra quyền, giá trị sai/biên và 5xx nằm trong kiểm thử API của môn học. Các ca FAIL/OPEN và giới hạn cũ phải được công bố, không bị xóa khỏi kết quả vì thu nhỏ phạm vi trình bày.

## 4. Bốn việc còn lại

1. Định dạng báo cáo cuối kỳ từ bản Markdown; kiểm bảng, sơ đồ và các ví dụ.
2. Chuẩn bị slide ngắn và demo ba luồng; dùng evidence dự phòng có ngày rõ ràng cho K05/finding/chi phí. Nhóm tự tập và đo thời lượng.
3. Gom một gói bàn giao gồm mã kiểm thử, README/dependency, config mẫu, baseline/schema, report và reproducer cần thiết; không đưa credential/license thật.
4. Hoàn thành đánh giá đóng góp, kiểm lịch bảo vệ/hạn trước một tuần và nộp thật.

Đủ đầu ra A–H và minh chứng phương pháp là tiêu chí hoàn thành đồ án. Những failure còn mở không tự làm đồ án thất bại, nhưng phải được mô tả trung thực; điểm và nghiệm thu thuộc giảng viên.
