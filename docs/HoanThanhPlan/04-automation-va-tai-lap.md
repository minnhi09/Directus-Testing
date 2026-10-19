# Phase 4 — Automation, tính ổn định và khả năng chạy lại

**Cách chạy chính sau thu gọn 19/10:** S1–S6 và `test designed --selection course` (7 ca), tổng 13. `test designed` mặc định chọn `course`; các lệnh `--selection short` trong hồ sơ bên dưới vẫn chỉ bộ 58 ca lịch sử. Thay đổi bộ chọn chưa phải bằng chứng chạy API mới. Xem [README hiện hành](../../README.md).

**Ngày thực hiện:** 18/10/2026. **Trạng thái:** hoàn thành P4-01…09 trong phạm vi tích hợp harness và kiểm chứng suite ngắn. Không đồng nghĩa hoàn thành toàn bộ catalog, campaign cuối kỳ hoặc đóng các finding.

Hai lượt suite ngắn đều **58/58 PASS**, cleanup và restore PASS, cùng hash harness/cấu hình/snapshot đầu vào. Suite invariant lịch sử vẫn **9 PASS, 2 FAIL**; failure được giữ cho Phase 5. Xem [bảng 257 case](04-ket-qua-case.csv), [chỉ mục 23 run](tai-lieu-bo-tro/phase4-20261018/run-index.json) và [so sánh hai lượt](tai-lieu-bo-tro/phase4-20261018/repeatability.json).

## 1. Những gì đã thay đổi

| Task | Thực hiện | Điểm kiểm chứng |
|---|---|---|
| P4-01 | Đưa launcher, bootstrap jq có checksum và wrapper Git Bash vào repo; README có lệnh tại thư mục DAMH | [run-lab.ps1](../../scripts/run-lab.ps1), [setup-windows.ps1](../../scripts/setup-windows.ps1), [README](../../README.md); doctor/seed/export/suite đã chạy bằng launcher này |
| P4-02 | Thêm adapter chạy catalog P3 và oracle độc lập, dùng chung `Lab`/`Api`, credential, profile, run ID, report và fixture map | [designed_cases.py](../../scripts/designed_cases.py), [invariants.py](../../scripts/invariants.py), [catalog runtime](../../scripts/data/test-catalog-v1.json), [fixture oracle](../../scripts/data/fixture-oracle.json) |
| P4-03 | Chặn URL/port/project/image/revision sai; kiểm actor bằng login/control, schema actor/10 operation, fixture đầy đủ, field validation/default, quan hệ và Reader published | [lab.sh](../../lab.sh), `target-verification.json`, `preflight.json`, `execution-config.json` trong mỗi run tương ứng |
| P4-04 | ID từ map/response; probe riêng; kiểm đủ business field; khóa mutation chung; cleanup từng ca; snapshot/restore cuối suite Python, scenario và smoke | Ba chuỗi P3-ST-01…03, bài thử budget và bài thử khóa thực tế |
| P4-05 | Replay recorder parent chain, ánh xạ ID theo collection/identity; so đúng check và loại failure | [replay_cases.py](../../scripts/replay_cases.py), [contract_checks.py](../../scripts/contract_checks.py); ba replay Schemathesis và một replay P3 |
| P4-06 | Ghi incremental report, phần chưa chạy, readiness, verdict, trace/parent, cleanup; lưu mã thoát runner/restore riêng; source/schema/map/budget có snapshot/hash | `designed-report.json`, `component-outcomes.json`, `harness-inputs.json`, `execution-config.json`; bài thử incomplete |
| P4-07 | Siết negative: đúng status + mã lỗi, có control và kiểm không đổi dữ liệu; 5xx/network không PASS. Sort dùng seed/map và DB độc lập | 13 regression test offline; suite thật; S4 không còn lẫn row policy với private projection; S6 gửi request dù PATCH vắng schema Reader |
| P4-08 | Chạy hai lượt ngắn tuần tự, đối chiếu dữ liệu/source/config/thứ tự/verdict | Các cờ so sánh trong `repeatability.json` đều true |
| P4-09 | Kiểm cú pháp Python/Bash/PowerShell, diff, regression offline trên host và runner pin; chạy integration liên quan | [validation](tai-lieu-bo-tro/phase4-20261018/validation.json), [unit trên host](tai-lieu-bo-tro/phase4-20261018/unit-test-output.txt), [unit trong runner](tai-lieu-bo-tro/phase4-20261018/unit-test-pinned-output.txt) |

Không nâng version, đổi schema/policy/fixture nghiệp vụ, reset volume hoặc sửa checkout Directus. Chưa commit/push. Các tệp đã dirty trước Phase 4 có [checkpoint riêng](tai-lieu-bo-tro/phase4-20261018/source-manifest-before.json); nguồn bàn giao có [manifest sau sửa](tai-lieu-bo-tro/phase4-20261018/source-manifest-after.json) và [gói source không chứa credential](tai-lieu-bo-tro/phase4-20261018/phase4-source.zip).

## 2. Nền tảng và precondition thật

Lab `r06-k05`, profile file mới `phase4-20261018`, fixture `r06-k05-v2`. Các profile dùng chung DB, không phải các môi trường ghi độc lập. Image digest được giữ theo manifest: Directus 12.5.0, PostgreSQL 16, Schemathesis 4.30.0. OCI revision của container Directus khớp source pin `4f77933bf9551cac6b289576078783e189b8f4e3`; đây là bằng chứng của runtime mới, không bổ sung ngược provenance cho run lịch sử.

Run seed `20261018T064116Z-321` xác minh lại fixture hiện có, không nhân bản dữ liệu. Export `20261018T064751Z-110` giữ hash raw schema như lịch sử: Editor `bd32aa69…`, Reader `d7dc1393…`. Trong suite mới, bản map/schema dùng làm đầu vào được copy vào từng run, không chỉ trỏ tới file mutable. Metadata ghi HEAD `2e44fe7…` và working tree **dirty**; hash file mới là căn cứ nhận diện mã chưa commit.

Oracle DB đọc riêng bằng SQL cho biết PostgreSQL **16.15**, collation `en_US.utf8`, title order ID 1…12 khớp thứ tự trong seed spec. Expected của query được xây từ spec + map; không lấy kết quả GET đang thử làm chuẩn. Preflight xác minh đủ 3 category/12 article, 6 published Reader, default draft, max length, validation score/status và FK SET NULL.

Doctor cuối [`20261018T092140Z-1392`](tai-lieu-bo-tro/phase4-20261018/doctor-output.txt) PASS: health authenticated đạt; license thật `active`, entitlement custom permission rules bật. Không lưu giá trị license/credential. Một lần lab ở trạng thái Exited (255) đã bị preflight chặn (`20261018T085927Z-1907`); chạy `up` giữ volume rồi kiểm tiếp, chưa kết luận nguyên nhân môi trường.

## 3. Kết quả chạy mới

Các đường dẫn dưới đây dẫn tới bản sao report trong hồ sơ. Raw response cần thiết nằm trong [gói runtime evidence](tai-lieu-bo-tro/phase4-20261018/selected-runtime-evidence.zip); artefact gốc vẫn ở `artifacts/runs/<run_id>/`.

| Run / lệnh | Kết quả | Exit / restore |
|---|---|---|
| `20261018T090954Z-1705` — designed short | [58 PASS](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T090954Z-1705/designed-report.json), 156 giây cả wrapper | 0 / 0 |
| `20261018T091253Z-1524` — designed short lặp lại | [58 PASS](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091253Z-1524/designed-report.json), 156 giây; cùng source/config/state/order/verdict | 0 / 0 |
| `20261018T091538Z-1506` — invariants | [9 PASS, 2 FAIL](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091538Z-1506/invariant-report.json); không bỏ qua lỗi cũ | 1 / 0 |
| `20261018T091750Z-1620` — scenarios | [6 PASS](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091750Z-1620/scenario-report.json), có oracle sort độc lập | 0 / 0 |
| `20261018T091838Z-1344` — smoke | Validation score/status 400/FAILED_VALIDATION; SET NULL và Reader control PASS | 0 / 0 |
| `20261018T091924Z-1822` — ST-02 với budget 3 giây | [INCOMPLETE](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091924Z-1822/designed-report.json), dừng trong chuỗi sau mutation; cleanup và restore PASS | 1 / 0 |
| `20261018T092004Z-1365` — replay P3-ST-02 | [PASS](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T092004Z-1365/designed-report.json), tạo lại đầy đủ thiết kế với ID mới | 0 / 0 |
| `20261018T090520Z-2152` — lệnh ghi thứ hai lúc suite đang chạy | Bị khóa trước request test; owner của suite đang chạy giữ nguyên | 1; không vào runner |

Sau cặp repeat, bổ sung guard snapshot/restore cho entry `smoke` trong `lab-components.sh`, rồi kiểm riêng smoke và các lệnh replay/budget trên bản mới. Khi chốt hồ sơ, nhãn mô tả `admin_usage` được làm rõ để gồm cả control read trong invariant cũ; trace actor của các run vẫn là căn cứ chi tiết. Các module Python/catalog của cặp repeat không đổi. Manifest sau sửa ghi rõ khác biệt này; không gán hash cuối cho các run trước.

Suite 58 gồm 10 positive operation, 31 biến thể quyền, 5 query, 8 ca field, 1 invalid-token và 3 chuỗi. Có 30 ca thiết kế ASSERTABLE, 28 CONDITIONAL đã đủ control cho chính lượt chạy này. Không đổi toàn bộ các câu hỏi thiết kế thành CLOSED chỉ từ subset đó.

Bảng CSV có **58 PASS, 199 NOT_RUN** theo lượt short thứ hai; trong 221 ca ngoài pairwise còn 163 NOT_RUN. Chưa chạy 36 query reference hoặc chín pairwise ở Phase 6. Có case chạm 20/26 BR, nhưng đây là truy vết tới một số khía cạnh của BR, không phải 20 BR đã được phủ hết. Positive acceptance đạt 10/10 method–path; không phải source line/branch coverage.

## 4. Replay được kiểm đến đâu?

| Run / case | Chuỗi và kết luận thực |
|---|---|
| `20261018T091638Z-1712` / qfqspn | [single_request](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091638Z-1712/reproducer-schemathesis-qfqspn.json): POST trả 200 và tái hiện `response_schema_conformance / JsonSchemaError` |
| `20261018T091711Z-433` / Z6yNal | [full_recorded_parent_chain](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091711Z-433/reproducer-schemathesis-Z6yNal.json): GET producer → DELETE consumer, giữ transition/expression, map theo identity; 204 tái hiện `status_code_conformance / UndefinedStatusCode` |
| `20261018T092051Z-1565` / 5Ez1Ry | [no_source_failure](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T092051Z-1565/reproducer-schemathesis-5Ez1Ry.json): POST array → DELETE chạy được, source/actual cùng 204, nhưng nguồn không có check failure nên **không** gọi reproduced; exit 1, restore 0 |

ID mapping chỉ thay path ID, filter ID/FK và FK category có kiểu. Không đi khắp JSON thay mọi số, score, metadata counter hoặc limit. Producer phải có integer ID và identity duy nhất; không zip theo vị trí response. Unit test thử ID mới khác ID cũ, đảo thứ tự response, trùng identity, thiếu/cycle parent và status trùng nhưng check khác. Replay runtime trên máy này có nhiều fixture ID trùng lịch sử; chưa chứng minh chạy trên máy thứ hai với toàn bộ ID đổi.

Chuỗi parent đã ghi không đại diện toàn bộ state của campaign trước đó. Thiếu parent, mapping không chắc, schema nguồn mất, case ID nhập mơ hồ hoặc check ngoài bốn check nền tảng thì trả nonzero/chưa xác minh. P3 replay là tái sinh thiết kế, không tự nhận là replay nguyên counterexample đã shrink.

Có [ba recorder trích chọn đã bỏ header xác thực](tai-lieu-bo-tro/phase4-20261018/replay-source/provenance.json) cùng schema nguồn để giữ ngoài cache. Đây là bản dẫn xuất; các replay thật trong bảng dùng events gốc. Nếu cần bàn giao sang máy mới, copy thư mục `replay-source/guided/seed-101/` vào `artifacts/runs/portable-phase4/guided/seed-101/` rồi đặt `LAB_REPLAY_EVENTS` tương ứng; nhánh dùng bản dẫn xuất này chưa được chạy runtime trong Phase 4.

## 5. Assertion, lỗi harness đã sửa và finding giữ lại

Negative permission yêu cầu 403/FORBIDDEN, control hợp lệ, không lộ dữ liệu/không đổi trạng thái. Invalid input đã chốt yêu cầu 400 và đúng mã validation; 5xx, lỗi mạng hoặc auth sai nhánh đều không PASS. DELETE được kiểm absence theo Directus pin và list control. PATCH/SET NULL trong chuỗi P3 so đủ business field. Một số invariant lịch sử chỉ kiểm field hẹp; dùng P3-ST để chứng minh preservation đầy đủ, không diễn giải lại scope của tên invariant cũ.

Các lỗi harness/thiết kế phát hiện khi tích hợp được giữ trong run-index:

- Wrapper jq lúc đầu chặn cả chuyển POSIX file path cho jq native; seed fail. Sửa chỉ loại API `/items/` khỏi chuyển path, giữ file-path conversion; seed/export sau đó PASS.
- SQL đọc collation sai, DELETE permission control dùng `body.get` khi không có body, và report chưa bắt đủ exception của từng case. Đã sửa; bộ regression kiểm report/cleanup vẫn có khi lỗi harness xuất hiện.
- Bốn request category dùng field article khiến Editor positive control thất bại. Bản runtime sửa thành `id,name`, [errata có before/after/hash](tai-lieu-bo-tro/phase4-20261018/catalog-errata.json); catalog Phase 3 gốc giữ nguyên.
- Chuỗi token thường đi vào nhánh static-token, trả 401/INVALID_CREDENTIALS; không phải nhánh JWT của expected. Giữ FAIL ở run `20261018T090634Z-290`; dùng JWT tổng hợp `iss=directus` với chữ ký cố ý sai để kiểm 403/INVALID_TOKEN và thêm valid users/me control. Căn cứ: [is-directus-jwt.ts](tai-lieu-bo-tro/phase4-20261018/baseline-auth-source/is-directus-jwt.ts), [get-accountability-for-token.ts](tai-lieu-bo-tro/phase4-20261018/baseline-auth-source/get-accountability-for-token.ts), [jwt.ts](tai-lieu-bo-tro/phase4-20261018/baseline-auth-source/jwt.ts), đều tại source pin.
- Adapter contract cần `Response` native để giữ header và phải bắt `FailureGroup` của đúng bản Schemathesis. Probe offline xác minh bắt được schema/status/500 failure, không tự biến check failure thành runner crash.

Hai invariant FAIL vẫn cần Phase 5: aggregate shape không hợp lệ trả **500**, trong khi empty/count control đều 200; và bốn candidate hợp đồng (POST hai collection object/array, CSV content type, DELETE 204). Chưa gọi bốn mismatch thành bốn product defect; không tắt check hoặc sửa raw schema để né chúng.

[Probe runner pin](tai-lieu-bo-tro/phase4-20261018/pinned-contract-probe.json) chạy không mạng: registry sinh dữ liệu không có `timestamp`; string `not-a-date` vẫn qua response schema có format đó; nullable integer nhận null, integer không nullable bị JsonSchemaError; typeless nullable nhận scalar, mẫu oneOf nullable nhận null. Đây là các mẫu nhỏ trên 4.30.0, không chứng minh mọi kết hợp `$ref`/nullable. Không đổi timestamp raw thành date-time; oracle thời gian và câu hỏi chưa đủ nguồn vẫn được theo dõi riêng.

## 6. Chi phí và cách dùng từ bây giờ

Mỗi lượt short mất 156 giây trên máy này. Trong trace của 58 case có 695 bước HTTP, gồm 266 bước gắn nhãn cleanup; có 704 file response Python khi tính thêm preflight và 23 file response Bash cho wrapper. **Số file/step không phải tổng HTTP**: login không lưu response, setup/restore ngoài runner có chi phí riêng. Một case không tương ứng một request.

Nhóm có thể dùng `--case` hoặc `--group` cho chỉnh sửa cục bộ, rồi chạy short trước demo/tích hợp. Việc chọn subset và replay failure đã lưu giúp tránh chạy lại ba seed fuzz cho mọi thay đổi helper. Còn chi phí snapshot/cleanup lớn là số liệu đầu vào cho Phase 6; chưa tối ưu bằng cách bỏ control/cleanup hoặc chia worker ghi song song. Mức giảm 36 → 9 query của pairwise vẫn là thiết kế, chưa là tiết kiệm runtime đã đo.

Lệnh và dependency cụ thể ở [README](../../README.md). Giữ budget mặc định 600 giây, một worker, 5/s, timeout 10 giây cho deterministic/replay; cleanup/restore được phép chạy sau budget. OPEN, incomplete, failure và restore failure đều giữ nonzero. Đọc report trước khi diễn giải mã thoát.

## 7. Giới hạn và bàn giao

- Đã xác minh trên Windows hiện tại, bootstrap theo nhánh dùng executable jq cùng checksum; chưa dựng từ đầu trên máy thứ hai hoặc kiểm runtime nhánh download mạng. Linux/macOS chưa chạy lại trong Phase 4.
- Chưa chạy full catalog, fuzz campaign dài, so raw/guided/pairwise về chi phí, CI/CD hoặc nghiệm thu cuối kỳ. Chưa có số liệu line/branch coverage Directus hay flake rate thống kê.
- Export trong adapter catalog hiện chỉ kiểm output không rỗng + contract; chưa có parser đối chiếu đủ row cho mọi định dạng. Các case export P3 chưa chạy ở lượt short; không dùng adapter hiện tại để tuyên bố full business oracle của export đã nghiệm thu.
- Khóa là cơ chế trong harness trên checkout này; không chặn người sửa DB trực tiếp hoặc chạy harness ở checkout khác. Cleanup failure được thử bằng regression mock; chưa cố ý phá DB để gây restore failure thật.
- Ngắt có thể xử lý trong runner sẽ vào finally; mất điện/SIGKILL/kill Docker cưỡng bức không bảo đảm finally/restore. Khóa sót phải được điều tra, không tự xóa/reset rồi báo môi trường sạch. Khôi phục business state không hứa khôi phục sequence, audit log hoặc trạng thái nội bộ toàn Directus.
- Source/runtime evidence được giữ trong hồ sơ bằng whitelist, không có `lab.env`, license hay DB dump. [177 file evidence lịch sử](tai-lieu-bo-tro/phase4-20261018/historical-integrity.json) vẫn đúng checksum. Không tự thay kết luận G1 lịch sử thành nghiệm thu cuối kỳ hoặc xác nhận của thành viên khác.

**Điều hướng theo phạm vi mới:** [Phase 5 rút gọn: finding và phân tích nguyên nhân](05-finding-register.md) đã tổng hợp hai invariant FAIL và replay/check đã có; đọc trạng thái finding tại đó. Phase 7 đã loại khỏi phạm vi. Chỉ đóng finding khi có bằng chứng sửa và retest phù hợp.
