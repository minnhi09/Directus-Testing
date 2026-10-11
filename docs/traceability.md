# Truy vết A–H và backlog checkpoint

Bảng này là backlog tích hợp ban đầu theo hai kế hoạch. “Đã có” chỉ nói về tệp hoặc kiểm tra đã tồn tại trong checkout hiện tại; không thay thế review chéo hay nghiệm thu G1.

| Yêu cầu | Đầu ra | Chủ sở hữu | Bằng chứng hiện có | Trạng thái |
|---|---|---|---|---|
| A — mục tiêu, actor, module, data flow | Tổng quan và data flow | Lành | [`docs/architecture.md`](architecture.md), [`docs/g0-quyet-dinh-ky-thuat.md`](g0-quyet-dinh-ky-thuat.md) | Khung đã có; cần bổ sung phân tích các luồng |
| B — kiến trúc | Sơ đồ container/component và giải thích request | Lành | [`docs/architecture.md`](architecture.md) | Đã có bản đầu; chưa review chéo |
| C — môi trường, phiên bản, seed, luồng chạy | Compose, script, README, run evidence | Lành thực hiện/tích hợp | [`compose.yaml`](../compose.yaml), [`lab.sh`](../lab.sh), [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md) | Stack local, fixture map, actor và full raw/guided 3 seed đã chạy; policy Reader bị license chặn; chưa kiểm tra máy khác |
| D — nguyên lý, phạm vi, pass/fail, rủi ro | Chiến lược raw/guided và phân loại | Lành thực hiện/tích hợp; co-author chỉ khi có đóng góp thật | [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md), [`evidence/pilot-triage-2026-10-11.md`](../evidence/pilot-triage-2026-10-11.md), report full campaign | Đã có triage sơ bộ; các failure full campaign chưa là defect kết luận, cần replay/đối chiếu contract |
| E — input, precondition, expected, invariant | Fixture, ma trận actor, sáu scenario và positive operation acceptance | Lành thực hiện/tích hợp; Trâm chỉ co-author nếu có đóng góp thật | `runtime/fixture-ids.json`, `scenario-report.json`, [`scripts/lab-components.sh`](../scripts/lab-components.sh), [`scripts/invariants.py`](../scripts/invariants.py) | S1–S3 và invariant không phụ thuộc Reader đạt; positive probe đạt 10/10 operation; S4–S6/Reader blocked đúng khi schema thiếu operation |
| F — automation/harness | Exporter, runner, test bổ trợ, replay | Lành thực hiện/tích hợp | [`lab.sh`](../lab.sh), [`scripts/lab-components.sh`](../scripts/lab-components.sh), [`scripts/invariants.py`](../scripts/invariants.py), schema manifest | Campaign raw/guided 10 operation, full 3 seed, invariant/replay trong runner Docker và reset đã có đường chạy; runner failure được giữ nguyên |
| G — log, report, metrics, defect/root cause | Run metadata, report, reproducer | Lành thực hiện/tích hợp; co-author chỉ khi có đóng góp thật | `artifacts/runs/<run_id>/`, [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md), [`evidence/pilot-triage-2026-10-11.md`](../evidence/pilot-triage-2026-10-11.md), [`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md) | Metadata/metrics/reproducer có; full campaign có phát hiện để triage, chưa kết luận defect hoặc kiểm tra chéo độc lập |
| H — pin và tái lập | Manifest, snapshot, hướng dẫn dựng lại | Lành thực hiện/tích hợp | [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`README.md`](../README.md) | Baseline, digest, token TTL, snapshot/restore và run máy hiện tại có; chưa đạt G1 vì license Reader và máy thứ hai chưa kiểm tra |

## Backlog theo đường phụ thuộc

| Mã | Việc | Chủ sở hữu | Điều kiện bắt đầu | Tiêu chí nghiệm thu | Phụ thuộc |
|---|---|---|---|---|---|
| G0-01 | Giữ Compose/network/volume và `doctor/up/down` | Lành | Kế hoạch được áp dụng | Project `r06-k05`, DB không publish host port, mã lỗi rõ | — |
| G0-01a | Chuẩn hóa URL, actor credential, run ID và artefact | Lành | G0-01 | `metadata.json`/`run.log` không chứa secret; fixture map có vị trí thống nhất | G0-01 |
| G0-02 | Ghi manifest và evidence không chứa secret | Lành | Image manifest tra cứu được | Tag + digest + source commit + trạng thái chạy thật | G0-01 |
| G0-03 | Seed hai collection, actor, policy và ID map | Lành thực hiện/tích hợp; Trâm chỉ co-author nếu có đóng góp thật | Stack healthy, interface G0 | Schema/fixture/ID map/editor đạt; policy Reader bị entitlement chặn, seed giữ mã lỗi | G0-01 |
| G0-04 | Sáu scenario query/quyền/invariant | Lành thực hiện/tích hợp; Trâm chỉ co-author nếu có đóng góp thật | Fixture map và actor login | S1–S3 đạt; S4–S6 blocked, không gửi request khi operation bị lọc | G0-03 |
| G0-05 | Export schema theo actor, allowlist năm operation | Lành thực hiện/tích hợp; Nhân chỉ co-author nếu có đóng góp thật | Seed phần dữ liệu đạt, OpenAPI đọc được | Schema raw 4 actor bất biến; editor overlay có inventory 10 operation | G0-03 |
| G0-06 | Campaign Schemathesis raw/guided | Lành triển khai/tích hợp; co-author chỉ khi có đóng góp thật | Export schema + credential interface | Đúng actor/URL, 10 operation, report/coverage/mã thoát lưu; fixture được khôi phục sau cả ba seed | G0-05 |
| G0-07 | Dựng lại và kiểm tra chéo G1 | Lành điều phối | G0-03, G0-04, G0-06 | Người khác dựng/check lại; ghi rõ máy chưa chạy | G0-04, G0-06 |

Các checkpoint mới trong phiên rush được commit trên nhánh hiện tại; không push hoặc rewrite remote. Các tệp `mnhy/` và `AGENTS.md` vẫn nằm ngoài Git theo quy ước của repository. Chưa xem là G1; còn chờ license Reader, review chéo và dựng lại trên máy độc lập.
