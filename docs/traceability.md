# Truy vết A–H và backlog checkpoint

Bảng này là backlog tích hợp ban đầu theo hai kế hoạch. “Đã có” chỉ nói về tệp hoặc kiểm tra đã tồn tại trong checkout hiện tại; không thay thế review chéo hay nghiệm thu G1.

| Yêu cầu | Đầu ra | Chủ sở hữu | Bằng chứng hiện có | Trạng thái |
|---|---|---|---|---|
| A — mục tiêu, actor, module, data flow | Tổng quan và data flow | Lành | [`docs/architecture.md`](architecture.md), [`docs/g0-quyet-dinh-ky-thuat.md`](g0-quyet-dinh-ky-thuat.md) | Khung đã có; cần bổ sung phân tích các luồng |
| B — kiến trúc | Sơ đồ container/component và giải thích request | Lành | [`docs/architecture.md`](architecture.md) | Đã có bản đầu; chưa review chéo |
| C — môi trường, phiên bản, seed, luồng chạy | Compose, script, README, run evidence | Lành; Trâm phần seed | [`compose.yaml`](../compose.yaml), [`lab.sh`](../lab.sh), [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`evidence/g0-2026-10-09.md`](../evidence/g0-2026-10-09.md) | Stack/admin health đã chạy; seed và demo chưa có |
| D — nguyên lý, phạm vi, pass/fail, rủi ro | Chiến lược raw/guided và phân loại | Nhân; Lành tích hợp | Giao diện profile trong G0; chưa có campaign report | Chưa bắt đầu |
| E — input, precondition, expected, invariant | Fixture, ma trận actor, sáu scenario | Trâm | Contract fixture trong G0; chưa có seed/scenario | Chưa bắt đầu |
| F — automation/harness | Exporter, runner, test bổ trợ, replay | Nhân; Lành lớp chung | `lab.sh` có interface; profile chưa triển khai | Đang chờ seed/schema |
| G — log, report, metrics, defect/root cause | Run metadata, report, reproducer | Nhân; Trâm kiểm oracle; Lành duyệt | Quy định metadata trong README/G0 | Chưa có kết quả |
| H — pin và tái lập | Manifest, snapshot, hướng dẫn dựng lại | Lành | [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`README.md`](../README.md) | Máy hiện tại đã kiểm tra; máy thứ hai chưa kiểm tra |

## Backlog theo đường phụ thuộc

| Mã | Việc | Chủ sở hữu | Điều kiện bắt đầu | Tiêu chí nghiệm thu | Phụ thuộc |
|---|---|---|---|---|---|
| G0-01 | Giữ Compose/network/volume và `doctor/up/down` | Lành | Kế hoạch được áp dụng | Project `r06-k05`, DB không publish host port, mã lỗi rõ | — |
| G0-02 | Ghi manifest và evidence không chứa secret | Lành | Image manifest tra cứu được | Tag + digest + source commit + trạng thái chạy thật | G0-01 |
| G0-03 | Seed hai collection, actor, policy và ID map | Trâm | Stack healthy, interface G0 | Seed lặp lại không nhân bản, mismatch báo lỗi | G0-01 |
| G0-04 | Sáu scenario query/quyền/invariant | Trâm | Seed và policy đạt precondition | Expected/actual và dữ liệu trước/sau được ghi | G0-03 |
| G0-05 | Export schema theo actor, allowlist năm operation | Nhân | Seed đạt, OpenAPI đọc được | Schema gốc bất biến, operation inventory có bằng chứng | G0-03 |
| G0-06 | Pilot Schemathesis `schema-smoke` | Nhân | Export schema + credential interface | Đúng actor/URL, report và mã thoát được lưu | G0-05 |
| G0-07 | Dựng lại và kiểm tra chéo G1 | Lành điều phối | G0-03, G0-04, G0-06 | Người khác dựng/check lại; ghi rõ máy chưa chạy | G0-04, G0-06 |

Chưa tạo nhánh, commit, PR hoặc tag trong checkpoint này. Các tệp `mnhy/` và `AGENTS.md` vẫn nằm ngoài Git theo quy ước của repository.
