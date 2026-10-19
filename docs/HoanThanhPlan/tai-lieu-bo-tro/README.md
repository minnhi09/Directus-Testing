# Tài liệu hỗ trợ và bản sao lịch sử

> **Bản GitHub được chọn lọc ngày 19/10/2026:** chỉ công bố những bảng tổng hợp, report/reproducer, phản hồi mẫu và trích đoạn source được tài liệu dẫn trực tiếp tới. Danh sách bên dưới mô tả kho lịch sử cục bộ; các ZIP, checkpoint, raw recorder, script kiểm kê và bản sao khác không nằm trong repository. Nội dung report/source được giữ nguyên để đối chiếu hash; một phản hồi CSV lịch sử vẫn mang tên `python-http/response-83.json` theo cách bộ thu đặt tên. Không diễn giải tệp đó như JSON hợp lệ.

- `phase0-20261018/`: checkpoint.zip, manifest checksum và Git state trước Phase 0.
- `phase1-20261018/`: nguồn đầu vào, source đúng commit, bản traceability trước khi bổ sung và kết quả kiểm tra tài liệu tại từng thời điểm.
- `phase2-20261018/`: audit bốn schema actor, diff raw/guided, bảy case trích xuất sạch header xác thực, source generator đúng pin và kết quả kiểm tra tài liệu. Các JSON mới phản ánh review ngày 18/10, không phải run kiểm thử mới.
- `phase3-20261018/`: catalog thiết kế JSON, fixture oracle nguồn tĩnh, oracle library, chứng minh pair coverage, source error class đúng pin, manifest đầu vào và validation. Đây là dữ liệu thiết kế; mọi case chưa được chạy mới.
- `phase4-20261018/`: source checkpoint trước/sau, runtime reports chọn lọc, gói evidence, probe runner pin, regression output, errata và validation. Có kiểm thử API thật, khác với các phase biên soạn trước; xem báo cáo Phase 4 để biết phạm vi PASS/FAIL/NOT_RUN.
- `phase5-20261018/`: checkpoint tài liệu trước Phase 5, 10 source đúng commit/Git blob, 25 bản sao evidence Phase 4, audit finding/schema và validation. Chỉ phân tích/tái sử dụng evidence; không có API/campaign mới.
- `rut-gon-phase5-bo-phase7-20261018/`: bản trước điều chỉnh năm tài liệu, checksum và kiểm tra sau khi rút Phase 5/bỏ Phase 7. Đây là thay đổi kế hoạch, không có test/API run mới; bản lưu không dùng làm điều hướng hiện hành.
- `cong-cu-kiem-ke/`: bản sao hai script đã dùng để lập bảng kiểm kê/truy vết. Đây là script một lần phục vụ audit, chưa được nghiệm thu thành công cụ bảo trì; không chạy lại để cập nhật hồ sơ. Các đường dẫn trong script phản ánh thời điểm biên soạn.

Các bản ở đây đã được đối chiếu trùng SHA-256 với các bản sao trước đây tại `output/phase0-20261018/` và `output/phase1-20261018/`; hai thư mục output dư thừa đã được dọn. Dùng bản giữ tại đây để tra cứu; raw artifact thực nghiệm vẫn giữ nguyên.

Các manifest và bản lưu Markdown lịch sử giữ nguyên đường dẫn/nội dung lúc tạo để bảo toàn provenance; một số liên kết tương đối trong bản lưu không dùng làm điều hướng hiện hành. Đọc [mục lục hồ sơ](../README.md) và dùng [danh mục ánh xạ](../danh-muc-di-chuyen.json) để tìm bản sao trong thư mục này.

Không giải nén checkpoint đè lên checkout/DB hiện tại. Đây là checkpoint tệp, không có credential hoặc database để tự phục hồi toàn bộ hệ thống.

- `phase6-20261018/`: protocol chốt trước đo, freeze 20 tệp, source trước/sau, sáu trial query mới, bảng chi phí, audit raw/guided và replay lịch sử, evidence chọn lọc và validation. Raw NDJSON có thể chứa header nên không nằm trong gói chia sẻ; SHA/counter an toàn được lưu để đối chiếu.

- `phase8-20261018/`: checkpoint trước nghiệm thu, protocol, 17 run mới và ba run chuẩn bị, dữ liệu coverage, replay đại diện, campaign/probe audit, sự cố hiển thị do người dùng cung cấp, quyết định tối giản và gói evidence. Candidate probe unresolved được giữ metadata an toàn; không có main campaign mới hoặc thay source Directus.

- `truoc-rut-gon-mon-hoc-20261019.zip`: bản trước khi rút tài liệu/cách chọn test về phạm vi môn học. Không giải nén đè lên bản hiện hành. Đây là bản dự phòng một lần, không phải công cụ hay đầu việc nghiệm thu mới.

Phạm vi hiện hành là 13 ca/kịch bản và các bằng chứng K05/chi phí cần trình bày. Hồ sơ cũ trong thư mục này phục vụ đối chiếu, không yêu cầu nhóm đọc hoặc thực hiện lại mọi phase.
