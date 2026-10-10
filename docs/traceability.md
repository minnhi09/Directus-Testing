# Truy vết A–H và backlog checkpoint

Bảng này là backlog tích hợp ban đầu theo hai kế hoạch. “Đã có” chỉ nói về tệp hoặc kiểm tra đã tồn tại trong checkout hiện tại; không thay thế review chéo hay nghiệm thu G1.

| Yêu cầu | Đầu ra | Chủ sở hữu | Bằng chứng hiện có | Trạng thái |
|---|---|---|---|---|
| A — mục tiêu, actor, module, data flow | Tổng quan và data flow | Lành | [`docs/architecture.md`](architecture.md), [`docs/g0-quyet-dinh-ky-thuat.md`](g0-quyet-dinh-ky-thuat.md) | Khung đã có; cần bổ sung phân tích các luồng |
| B — kiến trúc | Sơ đồ container/component và giải thích request | Lành | [`docs/architecture.md`](architecture.md) | Đã có bản đầu; chưa review chéo |
| C — môi trường, phiên bản, seed, luồng chạy | Compose, script, README, run evidence | Lành; Trâm phần seed | [`compose.yaml`](../compose.yaml), [`lab.sh`](../lab.sh), [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md) | Stack local, fixture map và actor đã chạy; policy Reader bị license chặn; chưa kiểm tra máy khác |
| D — nguyên lý, phạm vi, pass/fail, rủi ro | Chiến lược raw/guided và phân loại | Nhân; Lành tích hợp | [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md), report pilot | Đang triage; pilot có report/coverage, raw/guided đầy đủ chưa chạy |
| E — input, precondition, expected, invariant | Fixture, ma trận actor, sáu scenario | Trâm | `runtime/fixture-ids.json`, `scenario-report.json`, [`scripts/lab-components.sh`](../scripts/lab-components.sh) | Một phần; S1–S3 đạt, S4–S6 blocked đúng khi Reader schema thiếu operation |
| F — automation/harness | Exporter, runner, test bổ trợ, replay | Nhân; Lành lớp chung | [`lab.sh`](../lab.sh), [`scripts/lab-components.sh`](../scripts/lab-components.sh), schema manifest | Một phần; export/schema-smoke chạy được, raw/guided/replay chưa bật |
| G — log, report, metrics, defect/root cause | Run metadata, report, reproducer | Nhân; Trâm kiểm oracle; Lành duyệt | `artifacts/runs/<run_id>/`, [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md) | Một phần; metadata/report/coverage có, chưa kết luận defect hoặc reproducer độc lập |
| H — pin và tái lập | Manifest, snapshot, hướng dẫn dựng lại | Lành | [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`README.md`](../README.md) | Chưa đạt G1; baseline và run máy hiện tại có, máy thứ hai chưa kiểm tra |

## Backlog theo đường phụ thuộc

| Mã | Việc | Chủ sở hữu | Điều kiện bắt đầu | Tiêu chí nghiệm thu | Phụ thuộc |
|---|---|---|---|---|---|
| G0-01 | Giữ Compose/network/volume và `doctor/up/down` | Lành | Kế hoạch được áp dụng | Project `r06-k05`, DB không publish host port, mã lỗi rõ | — |
| G0-01a | Chuẩn hóa URL, actor credential, run ID và artefact | Lành | G0-01 | `metadata.json`/`run.log` không chứa secret; fixture map có vị trí thống nhất | G0-01 |
| G0-02 | Ghi manifest và evidence không chứa secret | Lành | Image manifest tra cứu được | Tag + digest + source commit + trạng thái chạy thật | G0-01 |
| G0-03 | Seed hai collection, actor, policy và ID map | Lành triển khai tạm thời; Trâm chưa review | Stack healthy, interface G0 | Schema/fixture/ID map/editor đạt; policy Reader bị entitlement chặn, seed giữ mã lỗi | G0-01 |
| G0-04 | Sáu scenario query/quyền/invariant | Lành triển khai tạm thời; Trâm chưa review | Fixture map và actor login | S1–S3 đạt; S4–S6 blocked, không gửi request khi operation bị lọc | G0-03 |
| G0-05 | Export schema theo actor, allowlist năm operation | Lành triển khai tạm thời; Nhân chưa review | Seed phần dữ liệu đạt, OpenAPI đọc được | Schema raw 4 actor bất biến; editor pilot overlay có inventory 5 operation | G0-03 |
| G0-06 | Pilot Schemathesis `schema-smoke` | Lành triển khai tạm thời; Nhân chưa review | Export schema + credential interface | Đúng actor/URL, report/coverage/mã thoát lưu; fixture được khôi phục | G0-05 |
| G0-07 | Dựng lại và kiểm tra chéo G1 | Lành điều phối | G0-03, G0-04, G0-06 | Người khác dựng/check lại; ghi rõ máy chưa chạy | G0-04, G0-06 |

Checkpoint đã được commit tại [`1541fa1`](https://github.com/minnhi09/Directus-Testing/commit/1541fa1) và đưa lên PR [#18](https://github.com/minnhi09/Directus-Testing/pull/18) vào `main`. Các tệp `mnhy/` và `AGENTS.md` vẫn nằm ngoài Git theo quy ước của repository. PR chưa được xem là G1; còn chờ review chéo, license Reader và dựng lại trên máy độc lập.
