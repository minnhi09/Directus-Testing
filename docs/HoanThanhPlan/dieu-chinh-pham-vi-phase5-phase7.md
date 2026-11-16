# Điều chỉnh phạm vi: rút Phase 5, bỏ Phase 7

**Ngày:** 18/10/2026. **Trạng thái:** đã áp dụng vào kế hoạch theo yêu cầu người dùng nhằm tối ưu thời gian hoàn thiện R06 + K05. Đây là quyết định phạm vi của nhóm, không phải xác nhận nghiệm thu hoặc phê duyệt mới của giảng viên.

Đọc [kế hoạch hiện hành](Ke_hoach_hoan_thien_R06_K05_theo_phase.md). Phase 5 rút gọn đã có [báo cáo finding/RCA](05-finding-register.md), hoàn thành hồ sơ bằng evidence hiện có; các finding chưa được sửa. Phase 7 **đã loại khỏi phạm vi**, không được đánh dấu là đã triển khai thành công.

## 1. Căn cứ và những đầu ra vẫn phải giữ

[Đề bài](../yeu_cau.pdf), trang 2–3, yêu cầu mã automation chạy lại được, log/report/metrics, danh sách lỗi hoặc bất thường, phân tích nguyên nhân và cấu hình/hướng dẫn tái lập. Mục K05 ở trang 8 yêu cầu chạy schema tests, lưu reproducer và thống kê lỗi. PDF không quy định phải triển khai CI/CD, đóng mọi bug hoặc sửa mã Directus upstream.

Nhóm vẫn giữ A–H, demo ít nhất ba luồng nghiệp vụ, báo cáo/mã nguồn và đánh giá đóng góp thực tế. Đặc tả, sinh test từ OpenAPI và tối ưu chi phí là hướng dẫn bổ sung của thầy theo thông tin người dùng đã cung cấp; việc bỏ CI không loại các phần này.

## 2. Phase 5 còn những việc gì?

Tạo **một báo cáo** `05-finding-register.md`, gộp bảng finding và phần phân tích đại diện. Tái sử dụng report, reproducer và source investigation đã có ở Phase 4/tài liệu lịch sử đủ provenance.

| Phần giữ lại | Mức đủ để bàn giao |
|---|---|
| Danh sách và thống kê finding | Mỗi nhóm finding có ID, loại, trạng thái, expected/actual, baseline và link evidence. Không đếm mỗi check failure thành một defect |
| Reproducer | Dẫn request/chuỗi đã lưu; replay mới khi thiếu evidence phù hợp hoặc mã/fixture/điều kiện liên quan đã thay đổi |
| Phân tích đại diện | Ưu tiên aggregate 500 và một mismatch OpenAPI. Có ít nhất một phân tích nguyên nhân có căn cứ; phần chưa xác nhận ghi giả thuyết và giới hạn. Số đại diện này là cách thu gọn kế hoạch, không phải chỉ tiêu số bug của PDF |
| Kết luận | Tách product candidate, schema, harness/fixture, môi trường và unresolved; nêu ảnh hưởng finding mở tới báo cáo |

Không bắt buộc xây quy trình trạng thái bug nhiều bước, bảng severity/priority chi tiết cho mọi ca, hoàn tất thêm một vòng đời sửa lỗi harness hoặc điều tra source sâu cho mọi biến thể trùng. Có thể trích ngắn bằng chứng sửa lỗi harness đã có nếu giúp giải thích kết quả; không tạo lỗi mới để minh họa.

Ước lượng **một buổi làm việc** nếu evidence hiện có đủ dùng; thời gian điều tra nguyên nhân có thể phát sinh nếu nguồn còn thiếu. Không chạy lại toàn campaign chỉ để lập bảng finding.

## 3. Phase 7 được xử lý thế nào?

Loại P7-01…09 khỏi phạm vi phải thực hiện: không lập PR gate, job fuzz theo lịch, policy allowlist CI, secret trên CI, workflow upload artifact hoặc demo CD. Giữ số Phase 7 làm mốc tham chiếu để không đổi ID/link của Phase 8–9. Không yêu cầu tạo `07-ci-va-quality-gate.md`.

Automation local/Docker, giữ exit code, credential riêng, cleanup/restore và gói evidence sạch vẫn thuộc Phase 4/8/9. Người khác phải chạy lại được bằng README dù không có pipeline CI. Lịch sử Git/task và peer evaluation của môn học vẫn phải phản ánh đóng góp thật.

## 4. Lộ trình còn lại

**Cập nhật sau Phase 6:** hồ sơ finding/RCA Phase 5 và [thí nghiệm chi phí Phase 6](06-toi-uu-chi-phi.md) đã hoàn thành trong phạm vi công bố. Phase 8 nay đã chốt theo [báo cáo nghiệm thu](08-bao-cao-nghiem-thu.md) và [phạm vi tối giản](LO_TRINH_TOI_GIAN_R06_K05.md). Còn lại **Phase 9**.

- **Phase 5:** đã có báo cáo finding/RCA gọn như trên; không đóng các finding OPEN.
- **Phase 6:** đã thực hiện sáu trial query và phân tích bằng chứng lịch sử; kết quả/giới hạn ở báo cáo Phase 6. Thiết kế giữ phần đánh giá chi phí trong kế hoạch; ưu tiên mô hình query nhỏ đã thiết kế, có đối chứng và số đo thật. Không bổ sung thí nghiệm để bù cho việc bỏ Phase 7. Quyết định này không tự thay scope/budget của các lượt kiểm thử đã chốt.
- **Phase 8:** chọn checkpoint/evidence nghiệm thu, chạy phần liên quan và schema testing theo cấu hình đã chốt, đối chiếu coverage/finding/giới hạn. Không phụ thuộc CI; giữ baseline, scope và budget hiện có cho đến khi có quyết định thay đổi riêng trước chạy.
- **Phase 9:** gom báo cáo A–H, README/gói bàn giao, demo ba luồng + automation + finding/reproducer, tổng duyệt và peer evaluation thật.

Ưu tiên tái sử dụng bằng chứng còn phù hợp. Kế hoạch này không buộc chạy đủ 257 case thiết kế mới được báo cáo; phải công bố tập thực thi, các rủi ro quan trọng và phần chưa phủ. Việc có nhiều case trong catalog không thay nghĩa vụ chạy schema-based testing K05 hoặc phân tích kết quả.

## 5. Ánh xạ task và lưu lịch sử

| Task cũ | Quyết định hiện hành |
|---|---|
| P5-01 | Giữ bảng finding tối giản |
| P5-02 + P5-06 | Gộp phân loại/gom trùng vào P5-02 |
| P5-03…05 | Giữ, giới hạn vào đại diện và tái sử dụng evidence phù hợp |
| P5-07 | Bỏ yêu cầu hoàn tất riêng một vòng đời lỗi harness |
| P5-08 | Giữ trạng thái/ảnh hưởng của finding mở |
| P7-01…09 | Loại khỏi phạm vi; không tính là task đã triển khai |

[Bản trước điều chỉnh và checksum](tai-lieu-bo-tro/rut-gon-phase5-bo-phase7-20261018/source-before.json) được giữ để truy vết. Các báo cáo/run/checksum của Phase 0–4 vẫn là bằng chứng tại thời điểm thực hiện; tham chiếu CI/vòng đời lỗi trong bản lịch sử không tạo lại yêu cầu cho lộ trình hiện hành.
