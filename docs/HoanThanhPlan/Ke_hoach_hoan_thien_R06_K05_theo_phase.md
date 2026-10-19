# Kế hoạch R06–K05 sau khi thu gọn

**Phạm vi hiện hành ngày 19/10/2026:** thực hiện theo [lộ trình môn học](LO_TRINH_TOI_GIAN_R06_K05.md), dùng [báo cáo cuối kỳ](09-bao-cao-cuoi-ky.md) và [README chạy chương trình](../../README.md). Kế hoạch chi tiết trước điều chỉnh được giữ trong `tai-lieu-bo-tro/truoc-rut-gon-mon-hoc-20261019.zip`; không dùng các đầu việc mở rộng trong bản đó làm điều kiện bắt buộc mới.

## Công việc đã có bằng chứng

| Giai đoạn cũ | Đầu ra đã có | Cách sử dụng hiện tại |
|---|---|---|
| Phase 0–2 | Kiểm kê, đặc tả/yêu cầu, review OpenAPI và cách sinh test | Tra cứu nguồn expected và giải thích K05 |
| Phase 3–4 | Thiết kế, automation, các bộ test và hướng dẫn chạy | Chọn S1–S6 cùng bảy ca bổ sung thành bộ đại diện 13 |
| Phase 5 | Finding và phân tích nguyên nhân | Trình bày sâu POST khác OpenAPI; công bố giới hạn các vấn đề khác |
| Phase 6 | Thí nghiệm chi phí 36/9 và số đo | Dùng kết quả đã lưu, không mở thêm thí nghiệm |
| Phase 7 | Đã bỏ | Không triển khai CI/CD cho lần hoàn thiện này |
| Phase 8 | Kết quả nghiệm thu ngày 18/10 | Nguồn bằng chứng lịch sử; các ca FAIL/OPEN giữ nguyên |
| Phase 9 | Đã có báo cáo Markdown | Còn định dạng, slide/demo, gói bàn giao, đánh giá đóng góp và nộp thật |

## Điều kiện kết thúc hiện hành

- Báo cáo A–H đọc độc lập, có 13 ca đại diện với đầu vào/expected/kết quả và nguồn bằng chứng.
- Có schema tests/report/reproducer của K05; mã kiểm thử và lệnh chạy lại dùng được trong môi trường đã mô tả.
- Có kết quả và phân tích nguyên nhân đại diện, bảng chi phí cùng giới hạn.
- Hoàn tất slide/demo, mã nguồn/dependency/config mẫu, đánh giá đóng góp và việc nộp.

Không cần hoàn thành toàn danh mục 257 ca, điều tra/sửa hết finding, tái chạy campaign, dựng máy thứ hai hoặc đo line/branch coverage để đóng các đầu việc mở rộng của bản kế hoạch cũ. Các hướng mở rộng không biến thành yêu cầu giảng viên.
