# Phase 0 - Quyết định còn thiếu và phụ thuộc cần giữ

**Ngày:** 18/10/2026. **Trạng thái:** Backlog kỹ thuật, không phải các quyết định đã được thông qua. Không phân công cá nhân.

**Quyết định phạm vi sau Phase 4:** [Rút Phase 5 và bỏ Phase 7](dieu-chinh-pham-vi-phase5-phase7.md). Bảng dưới giữ ảnh chụp backlog khi lập Phase 0; D00-09 (policy CI) không còn là đầu việc chặn lộ trình. Điều kiện license của D00-11 vẫn áp dụng khi dựng/chạy lab ở Phase 4/9, không yêu cầu cấu hình secret trên CI.

## 1. Các quyết định cần giải quyết

| ID | Vấn đề/câu hỏi | Căn cứ hiện có | Ảnh hưởng và hướng xử lý tiếp | Giải quyết ở |
|---|---|---|---|---|
| D00-01 | Title rỗng/khoảng trắng có hợp lệ không; độ dài Unicode được tính thế nào? | Fixture yêu cầu title non-null/max 120; OpenAPI chưa có maxLength | Tách missing/null/empty/blank; chốt expected từ nguồn phù hợp trước khi viết ca biên | Phase 1-3 |
| D00-02 | Score dạng chuỗi, thập phân, null, thiếu trường được xử lý thế nào? | BR 0-5 và integer; schema chưa có min/max; runtime có thể coercion | Phân biệt lỗi miền với lỗi kiểu; expected POST/PATCH không được suy theo một response bất kỳ | Phase 1-3 |
| D00-03 | Status thiếu, null, khác enum; POST/PATCH có default nào? | Fixture dùng draft/published và default draft; schema string chưa có enum | Ghi rõ default và hành vi thiếu trường theo operation; không áp required của POST cho mọi PATCH | Phase 1-2 |
| D00-04 | Query sai/overflow/aggregate lạ phải bị từ chối theo ngữ nghĩa nào? | Có aggregate 500/control 200 và candidate query lịch sử | Tách invalid-input, schema gap và robustness; 5xx không phải kết quả từ chối hợp lệ chỉ vì non-2xx | Phase 1, 5 |
| D00-05 | Status cho ID không tồn tại/không có quyền được xác định từ đâu? | DELETE/read-back lịch sử có 403; schema response map thiếu trường hợp | Không mặc định 401/404; ghi contract oracle và business oracle riêng, có nguồn cho expected | Phase 1-2 |
| D00-06 | Có cần hợp đồng bổ sung ngoài schema Directus không? | Thiếu maxLength/enum/min/max; guided hiện chủ yếu thêm example/ID | Trước hết bổ sung business oracle theo đặc tả; nếu sửa hợp đồng thì bản riêng có diff, không ghi đè raw/guided âm thầm | Phase 2 |
| D00-07 | Chọn source nào cho root cause cuối kỳ? | Baseline 4f77933; tài liệu cũ d3c9a8b; checkout hiện tại 8e140f9 | Đối chiếu đúng bản image/source, không dùng source hiện tại làm bằng chứng tương đương khi chưa kiểm tra | Phase 0 đã ghi nhận; xử lý ở Phase 5 |
| D00-08 | Khi nào có thể nói lab sẵn sàng live demo? | Doctor gần nhất 13/10 PASS; Docker API hiện không truy cập được | Preflight runtime trong ngữ cảnh có Docker khả dụng; không tự kết luận daemon dừng hoặc mở dịch vụ để thay đổi trạng thái trong Phase 0 | Trước live demo/Phase 4 |
| D00-09 | Chính sách CI với finding đã biết là gì? | Hai invariant FAIL, pilot runner 1 | Chốt gate stable/exploratory và quy tắc ngoại lệ có phạm vi; vẫn giữ assertion/report/exit code gốc | Phase 5, 7 |
| D00-10 | Evidence bàn giao lưu ở đâu, ai nhận được gì? | artifacts/runs và runtime bị ignore; tài liệu còn untracked | Chọn gói report/schema/reproducer sạch secret, đường dẫn/chỉ mục và cách giữ artifact gốc; không tự publish hoặc bỏ ignore | Phase 4, 9 |
| D00-11 | Điều kiện license/quyền khi dựng máy mới? | Artifact OIG cho thấy Reader policy đã chạy; config secret tồn tại, chưa đọc/kiểm chứng mới | Ghi điều kiện entitlement và cách cấu hình riêng; thiếu thì blocked thật, không dùng admin thay Reader hoặc bypass | Phase 4, 7, 9 |
| D00-12 | Helper Windows và executable bit được bàn giao thế nào? | run-lab.ps1/jq ngoài repo; mode lab.sh/invariants.py hiện 100644 | Tích hợp dependency hợp lý, xử lý mode phù hợp nền tảng; chưa sửa ở Phase 0 | Phase 4 |
| D00-13 | Ngưỡng và lịch campaign cuối kỳ được chốt ra sao? | Nội bộ có 3 seed/100 examples/1.200 giây; Windows mới chỉ có pilot và targeted run | Giữ cấu hình đã chốt hoặc ghi quyết định thay đổi trước khi chạy; không gọi số lượng nội bộ là yêu cầu bắt buộc của giảng viên | Phase 3, 6, 8 |
| D00-14 | Khi nào đưa các thay đổi hiện có vào checkpoint Git? | 4 modified, 49 untracked trước Phase 0; chưa staged | Bảo toàn snapshot đã tạo, review phần cần tích hợp; commit/push/tag chỉ trong đợt được giao quyền tương ứng | Trước checkpoint nghiệm thu |

Không cần giải quyết toàn bộ backlog để viết bản nháp Phase 1. Các mục ảnh hưởng expected phải đánh dấu chưa chốt; vẫn có thể mô tả yêu cầu rõ ràng đã có như Reader không được ghi và không lộ internal_notes.

## 2. Phụ thuộc ngoài repo và artifact bị ignore

| Phụ thuộc | Vị trí/trạng thái quan sát | Cần giữ/ghi chú |
|---|---|---|
| Windows launcher | `tmp/lab-tools/run-lab.ps1` ngoài DAMH | Đường dẫn tương đối tới DAMH; gọi `C:\Program Files\Git\bin\bash.exe`; profile mặc định windows-20261013-oig |
| jq portable | `tmp/lab-tools/jq`, `jq.exe`, `jq-sha256sum.txt` | Wrapper đặt MSYS2_ARG_CONV_EXCL cho `/items/`, gọi jq.exe với `-b`; chỉ có jq.exe mà thiếu wrapper có thể khác hành vi |
| Batch verify | `tmp/lab-tools/verify-lab.ps1`, `verify-k05.ps1` | Có seed/campaign, không phải công cụ chỉ đọc; không chạy trong Phase 0 |
| Các helper khác | check-acl.sh, check-runtime-profile.sh, expected-fixture.*, unicode-check.sh, rebuild-inventory.sh | Chưa xem tất cả là dependency bắt buộc của launcher; giữ cục bộ để điều tra/đối chiếu |
| Git Bash | `C:\Program Files\Git\bin\bash.exe` tồn tại | `bash` đầu tiên trên PATH hiện trỏ `C:\WINDOWS\system32\bash.exe`; không dùng lệnh bash chung để suy môi trường giống launcher |
| Git Bash utilities | curl, jq, sha256sum và các lệnh shell harness cần | Chưa chạy doctor hiện tại để xác nhận đầy đủ PATH/dependency |
| Docker CLI/daemon | docker.exe tồn tại; truy vấn API hiện thất bại | CLI hiện diện không chứng minh daemon khả dụng hoặc container healthy |
| Credential/license | `DAMH/config/lab.env` tồn tại, bị ignore | Không đọc/sao chép vào báo cáo/checkpoint; không coi tồn tại là credential/license còn hợp lệ |
| Raw evidence | `DAMH/artifacts/runs/`, bị ignore | Có trên workspace, không tự đi theo clone; giữ nguyên, rà soát trước chia sẻ |
| Schema/ID map | `DAMH/runtime/`, bị ignore | Có trong checkpoint tệp cục bộ; giữ riêng snapshot trước/sau OIG |
| Local instructions/private material | AGENTS.md, kế hoạch triển khai local; mnhy nếu có | Không tự đưa vào phần công bố; không đọc mnhy trong Phase 0 |
| Checkpoint mới | `output/phase0-20261018/` ngoài repo DAMH | Bản sao local của tệp, không phải DB backup hoặc bản đã publish |

## 3. Thứ tự xử lý đề xuất

1. Trong Phase 1: D00-01 đến D00-05; mô tả rõ nguồn và phần chưa chốt.
2. Trước sửa harness/chạy suite: D00-06, D00-08, D00-11, D00-12 và provenance phù hợp.
3. Trước CI/campaign nghiệm thu: D00-07, D00-09, D00-13 và checkpoint Git nếu được giao.
4. Trước bàn giao: D00-10, D00-14 cùng kiểm tra lại khả năng dựng mới.

Đây là thứ tự xử lý công việc, không phải yêu cầu xin lại quyền cho các tác vụ thông thường đã được giao. Nếu quyết định mới thay baseline, policy, fixture hoặc cách xử lý failure, cần có quyết định cụ thể theo quy tắc dự án trước khi áp dụng.

## 4. Những gì chủ động giữ nguyên

- Không nâng phiên bản Directus/Schemathesis, đổi fixture/policy hay mở rộng allowlist.
- Không sửa raw schema, expected result, mức assertion hoặc status failure.
- Không chạy seed/reset/up/down/fuzz/replay trong Phase 0.
- Không đưa credential, raw token/log/HTTP vào checkpoint chia sẻ.
- Không dùng kết quả kiểm kê làm peer review hoặc bằng chứng đóng góp của người chưa thực hiện.

Xem [báo cáo Phase 0](00-hien-trang-va-baseline.md) và [bộ demo tham chiếu](00-bo-demo-tham-chieu.md).
