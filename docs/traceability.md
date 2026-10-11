# Truy vết A–H và backlog checkpoint

Bảng này là backlog tích hợp ban đầu theo hai kế hoạch. “Đã có” chỉ nói về tệp hoặc kiểm tra đã tồn tại trong checkout hiện tại; tiêu chí nghiệm thu G1 hiện hành nằm tại [`docs/g1-acceptance.md`](g1-acceptance.md).

Checkpoint hiện tại dùng baseline local `r06-k05-v2` sau khi license thật được
container nhận. Các trạng thái `blocked` trong bảng dưới đây là lịch sử trước
license; kết quả mới được ghi ở cuối tài liệu và trong
[`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md).

| Yêu cầu | Đầu ra | Chủ sở hữu | Bằng chứng hiện có | Trạng thái |
|---|---|---|---|---|
| A — mục tiêu, actor, module, data flow | Tổng quan và data flow | Lành | [`docs/architecture.md`](architecture.md), [`docs/g0-quyet-dinh-ky-thuat.md`](g0-quyet-dinh-ky-thuat.md) | Khung đã có; cần bổ sung phân tích các luồng |
| B — kiến trúc | Sơ đồ container/component và giải thích request | Lành | [`docs/architecture.md`](architecture.md) | Đã có bản đầu; không yêu cầu review chéo để đóng G1 |
| C — môi trường, phiên bản, seed, luồng chạy | Compose, script, README, run evidence | Lành thực hiện/tích hợp | [`compose.yaml`](../compose.yaml), [`lab.sh`](../lab.sh), [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md) | Checkpoint v2: stack/fixture/actor/policy và full raw/guided 3 seed đã chạy; README giữ quy trình máy sạch |
| D — nguyên lý, phạm vi, pass/fail, rủi ro | Chiến lược raw/guided và phân loại | Lành thực hiện/tích hợp; co-author chỉ khi có đóng góp thật | [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md), [`evidence/pilot-triage-2026-10-11.md`](../evidence/pilot-triage-2026-10-11.md), report full campaign | Đã có triage sơ bộ; các failure full campaign chưa là defect kết luận, cần replay/đối chiếu contract |
| E — input, precondition, expected, invariant | Fixture, ma trận actor, sáu scenario và positive operation acceptance | Lành thực hiện/tích hợp; Trâm chỉ co-author nếu có đóng góp thật | `runtime/fixture-ids.json`, `scenario-report.json`, [`scripts/lab-components.sh`](../scripts/lab-components.sh), [`scripts/invariants.py`](../scripts/invariants.py) | Checkpoint v2 S1–S6 đạt; recheck invariant `20261011T134626Z-160826` có 9 pass/2 failure, giữ nguyên aggregate và contract candidate |
| F — automation/harness | Exporter, runner, test bổ trợ, replay | Lành thực hiện/tích hợp | [`lab.sh`](../lab.sh), [`scripts/lab-components.sh`](../scripts/lab-components.sh), [`scripts/invariants.py`](../scripts/invariants.py), schema manifest | Campaign raw/guided 10 operation, full 3 seed, invariant/replay trong runner Docker và reset đã có đường chạy; runner failure được giữ nguyên |
| G — log, report, metrics, defect/root cause | Run metadata, report, reproducer | Lành thực hiện/tích hợp; co-author chỉ khi có đóng góp thật | `artifacts/runs/<run_id>/`, [`evidence/g1-implementation-2026-10-10.md`](../evidence/g1-implementation-2026-10-10.md), [`evidence/pilot-triage-2026-10-11.md`](../evidence/pilot-triage-2026-10-11.md), [`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md) | Metadata/metrics/reproducer có; contract probe `20261011T130227Z-139257` ghi bốn schema candidate, replay `kb5gjq` ghi SQLSTATE `22007` và `F8j8Gl` ghi export array ngoài schema object; findings chưa đóng không bị đổi thành defect đã xác nhận |
| H — pin và tái lập | Manifest, snapshot, hướng dẫn dựng lại | Lành thực hiện/tích hợp | [`manifest/baseline.yaml`](../manifest/baseline.yaml), [`README.md`](../README.md) | Baseline, digest, token TTL, snapshot/restore và run local có; README giữ khả năng dựng máy mới, không yêu cầu chạy máy thứ hai |

## Truy vết checkpoint v2 đã chạy

| Nhóm | Bằng chứng hiện tại | Kết luận thực tế |
|---|---|---|
| A–C | `doctor` `20261011T105225Z-104013`, latest recheck `20261011T134705Z-161373`, seed `20261011T084845Z-72361`, schema export `20261011T085027Z-75998` | Directus/DB/runner healthy; license active; schema actor v2 có 14/14/6/0 operation |
| D–E | scenarios `20261011T105231Z-104612`, full invariant recheck `20261011T134626Z-160826` | S1–S6 PASS; invariant recheck 9 PASS/2 failure/0 blocked; aggregate 500 và contract candidates vẫn giữ failure |
| F | raw `20261011T085034Z-76481`, guided `20261011T095117Z-89079` | Mỗi profile đủ 3 seed và 10/10 operation; report/coverage/restore có, runner exit 1 do budget/check |
| G | replay aggregate `20261011T134519Z-160153` dưới `bcbf219`, contract probe `20261011T130227Z-139257` | Candidate 500 tái hiện, hai control aggregate trả 200; bốn contract candidate được ghi; chưa xác nhận product defect |
| H | `manifest/baseline.yaml`, `config/lab.env.example`, default fixture v2 | Clone máy mới dùng v2 mặc định; license vẫn phải cấu hình ngoài Git; khả năng tái lập được mô tả, không ghi giả một run máy thứ hai |

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
| G0-07 | Đối chiếu checklist nghiệm thu G1 và phân loại finding | Lành | G0-03, G0-04, G0-06 | Đối chiếu run/artifact với [`docs/g1-acceptance.md`](g1-acceptance.md); không yêu cầu máy thứ hai hoặc review chéo | G0-04, G0-06 |

Các checkpoint mới trong phiên rush được commit trên nhánh hiện tại; không push hoặc rewrite remote. Các tệp `mnhy/` và các tệp local-only chưa track vẫn nằm ngoài Git. G1 hiện đạt baseline kỹ thuật với findings: Reader đã được kiểm tra, invariant recheck có 9 pass/2 failure, còn aggregate HTTP 500, contract candidates và campaign `failed_or_incomplete` được giữ nguyên để triage.
