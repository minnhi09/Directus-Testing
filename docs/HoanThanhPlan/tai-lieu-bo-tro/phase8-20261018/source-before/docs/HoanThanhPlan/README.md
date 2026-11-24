# Hồ sơ hoàn thiện plan R06 + K05

Thư mục này tập hợp nội dung được tạo khi thực hiện kế hoạch hoàn thiện dự án. Từ các phase tiếp theo, tài liệu đầu ra mới tiếp tục được lưu tại đây, dùng tiền tố `00-`, `01-`, `02-`... để nhận biết phase.

**Cập nhật:** 18/10/2026. Đã hoàn thành Phase 0 kiểm kê, Phase 1 đặc tả, Phase 2 review OpenAPI, Phase 3 thiết kế test/tiêu chí kết thúc và Phase 4 automation/tái lập. Phase 4 đã tích hợp automation và chạy runtime thật: hai suite ngắn 58/58 PASS; invariant giữ 2 FAIL để triage. Chưa nghiệm thu cuối kỳ.

**Phạm vi hiện hành:** [Rút Phase 5, bỏ Phase 7](dieu-chinh-pham-vi-phase5-phase7.md) theo yêu cầu người dùng. Phase 6 đã hoàn thành thí nghiệm và phân tích chi phí. Lộ trình còn lại: Phase 8 → Phase 9. Phase 5 rút gọn nay có [báo cáo finding/RCA](05-finding-register.md); hoàn thành hồ sơ không có nghĩa đã sửa finding.

## 1. Nên đọc theo thứ tự nào?

1. [Kế hoạch tổng thể](Ke_hoach_hoan_thien_R06_K05_theo_phase.md): mục tiêu, công việc, phụ thuộc và tiêu chí hoàn thành từng phase.
2. [Hiện trạng và baseline](00-hien-trang-va-baseline.md): dự án đang có gì, nguồn bằng chứng nào được chọn và giới hạn hiện tại.
3. [Yêu cầu người dùng và đặc tả v0.2](01-yeu-cau-va-dac-ta.md): actor, dữ liệu, UR/BR/AC, rủi ro và câu hỏi còn mở.
4. [Truy vết nghiệp vụ](01-truy-vet-nghiep-vu.md): từ yêu cầu đến test, oracle, artifact và đầu việc cần bổ sung.
5. [Review đặc tả](01-review-dac-ta.md): các hạn chế của tài liệu/test hiện tại và gap task cho phase sau.
6. [Đối chiếu baseline P1-05](01-doi-chieu-baseline-p1-05.md): phần đã có căn cứ từ source đúng commit sau khi người dùng chọn bám baseline.
7. [Review OpenAPI và thiết kế sinh test](02-danh-gia-openapi-va-sinh-test.md): inventory, khoảng trống schema, oracle, stateful, quyền và đầu vào Phase 3–4.
8. [Ma trận 26 BR](02-ma-tran-rang-buoc.md), [bảy case sinh đại diện](02-case-sinh-dai-dien.md) và [quy tắc overlay](02-quy-tac-overlay.md): tra chi tiết khi thiết kế test/bảo vệ.
9. [Thiết kế test và coverage Phase 3](03-thiet-ke-test-va-coverage.md), [catalog](03-test-case-catalog.md), [tiêu chí kết thúc](03-tieu-chi-ket-thuc.md) và [review](03-review-thiet-ke.md): bộ input có chủ đích và điều kiện đánh giá trước khi triển khai automation.

10. [Automation và tái lập Phase 4](04-automation-va-tai-lap.md): code đã tích hợp, run thật, replay, budget/restore, lỗi harness và finding; [bảng kết quả 257 case](04-ket-qua-case.csv).

11. [Finding và phân tích nguyên nhân Phase 5](05-finding-register.md): register gọn, hai phân tích đại diện, nhóm contract/harness và các kết luận còn mở.

12. [Tối ưu chi phí Phase 6](06-toi-uu-chi-phi.md): sáu trial query thật, đối chiếu raw/guided và replay lịch sử; giảm 75% target nhưng trung vị 19,54% thời gian toàn lệnh.

## 2. Nội dung theo phase

| Phase | Nội dung đã tập hợp | Tình trạng |
|---|---|---|
| 0 | [Báo cáo hiện trạng](00-hien-trang-va-baseline.md), [bộ demo](00-bo-demo-tham-chieu.md), [quyết định/phụ thuộc](00-quyet-dinh-va-phu-thuoc.md) | Hoàn thành kiểm kê và checkpoint tệp; chưa xác minh runtime mới |
| 1 | [Đặc tả](01-yeu-cau-va-dac-ta.md), [truy vết](01-truy-vet-nghiep-vu.md), [review](01-review-dac-ta.md), [đối chiếu source](01-doi-chieu-baseline-p1-05.md) | Hoàn thành mức đặc tả/review; P1-05 đã chốt hướng và phân loại, Q kỹ thuật OPEN chuyển phase sau |
| 2 | [Review OpenAPI](02-danh-gia-openapi-va-sinh-test.md), [ma trận BR](02-ma-tran-rang-buoc.md), [case sinh](02-case-sinh-dai-dien.md), [overlay](02-quy-tac-overlay.md) | Hoàn thành review/thiết kế; phần triển khai và VFY-01…05 bàn giao Phase 3–4 |
| 3 | [Thiết kế](03-thiet-ke-test-va-coverage.md), [catalog](03-test-case-catalog.md), [entry/exit](03-tieu-chi-ket-thuc.md), [review](03-review-thiet-ke.md) | Hoàn thành thiết kế/review; các case đều NOT_RUN, conditional/open được bàn giao Phase 4 |
| 4 | [Automation/tái lập](04-automation-va-tai-lap.md), [kết quả](04-ket-qua-case.csv), [run-index](tai-lieu-bo-tro/phase4-20261018/run-index.json) | Hoàn thành tích hợp và suite ngắn; hai lượt 58 PASS, 6 scenario PASS; invariant 9 PASS/2 FAIL giữ để triage; chưa full catalog/campaign |
| 5 | [Finding/RCA rút gọn](05-finding-register.md), [phạm vi](dieu-chinh-pham-vi-phase5-phase7.md) | Hoàn thành hồ sơ: 4 nhóm SUT OPEN, source đúng pin, evidence Phase 4; không có test run mới |
| 6 | [Báo cáo chi phí](06-toi-uu-chi-phi.md), [kết quả tích lũy](06-ket-qua-case.csv), [trial CSV](tai-lieu-bo-tro/phase6-20261018/query-trials.csv) | Hoàn thành: 6/6 trial PASS, 37/37 cặp; raw/guided và replay phân tích lại có giới hạn; chưa nghiệm thu toàn dự án |
| 7 | CI/CD | Đã loại khỏi phạm vi theo quyết định; không tính là hoàn thành |
| 8-9 | Nghiệm thu, báo cáo và bàn giao | Chưa thực hiện; không phụ thuộc CI |

## 3. Bảng dữ liệu chi tiết

| Tệp | Dùng để làm gì? |
|---|---|
| [00-evidence-index.csv](00-evidence-index.csv) | Tra 302 thư mục artifact, provenance, budget và report hiện diện |
| [00-campaign-index.csv](00-campaign-index.csv) | Tra campaign theo profile/seed, stop reason, runner/restore và số liệu |
| [00-selected-evidence.json](00-selected-evidence.json) | Trích xuất thông tin cần thiết của 18 run tham chiếu |
| [00-evidence-hashes.json](00-evidence-hashes.json) | SHA-256 của 177 tệp evidence gốc được chọn |
| [00-schema-inventory.json](00-schema-inventory.json) | Các snapshot schema và operation QA tương ứng |
| [00-inventory-summary.json](00-inventory-summary.json) | Số lượng/tình trạng tổng hợp của lần kiểm kê |
| [01-traceability.csv](01-traceability.csv) | Bản bảng của 26 quy tắc và đường kiểm chứng |
| [02-operation-inventory.csv](02-operation-inventory.csv) | 34 operation QA của bốn actor; đánh dấu 10 operation campaign Editor và phần bulk bị loại |
| [02-ma-tran-rang-buoc.csv](02-ma-tran-rang-buoc.csv) | 26 BR với schema location, khả năng sinh, oracle bổ sung và Q/GAP/test kế thừa |
| [03-test-case-catalog.csv](03-test-case-catalog.csv) | 257 dòng thiết kế gồm 221 ca ngoài pairwise và36 query tham chiếu; expected/PC/cleanup/readiness/NOT_RUN rõ |
| [03-traceability.csv](03-traceability.csv) | 26 BR với case thiết kế, test hiện có, Q/GAP và trạng thái chưa chạy mới |
| [03-inventory-test-hien-co.csv](03-inventory-test-hien-co.csv) | 20 mục S/INV/smoke và cách tái sử dụng, tránh trùng |
| [03-phan-vung-tuong-duong.csv](03-phan-vung-tuong-duong.csv) / [03-gia-tri-bien.csv](03-gia-tri-bien.csv) | 48 lớp field và34 điểm biên có case ID |
| [03-bang-quyet-dinh-quyen.csv](03-bang-quyet-dinh-quyen.csv) | 69 luật actor/operation/state/projection khả thi và case tương ứng |
| [03-query-exhaustive-36.csv](03-query-exhaustive-36.csv) / [03-query-pairwise.csv](03-query-pairwise.csv) | Full36 và subset9, cùng case ID; phủ37 cặp cấu trúc; bản thiết kế lịch sử, kết quả chạy mới xem Phase 6 |

CSV/JSON là bảng đối chiếu chi tiết; nên đọc tài liệu Markdown trước để hiểu ý nghĩa và giới hạn của số liệu.

## 4. Checkpoint, source và tài liệu hỗ trợ

Các bản sao hỗ trợ được gom vào [tai-lieu-bo-tro](tai-lieu-bo-tro/README.md):

- [Checkpoint Phase 0](tai-lieu-bo-tro/phase0-20261018/checkpoint.zip), [manifest](tai-lieu-bo-tro/phase0-20261018/checkpoint-manifest.json) và [Git state trước Phase 0](tai-lieu-bo-tro/phase0-20261018/git-state-before.json).
- [Nguồn đầu vào Phase 1](tai-lieu-bo-tro/phase1-20261018/source-manifest-before.json), [manifest source baseline](tai-lieu-bo-tro/phase1-20261018/baseline-source-manifest.json), các tệp source chọn lọc được liên kết từ báo cáo P1-05.
- [Kết quả kiểm tra tài liệu Phase 1](tai-lieu-bo-tro/phase1-20261018/validation.json) và [kiểm tra sau đối chiếu baseline](tai-lieu-bo-tro/phase1-20261018/validation-baseline-update.json).
- [Audit schema Phase 2](tai-lieu-bo-tro/phase2-20261018/schema-review.json), [diff raw/guided](tai-lieu-bo-tro/phase2-20261018/raw-guided-diff.json), [case trích xuất](tai-lieu-bo-tro/phase2-20261018/selected-generated-cases.json), [manifest nguồn](tai-lieu-bo-tro/phase2-20261018/source-manifest-before.json) và [kiểm tra tài liệu](tai-lieu-bo-tro/phase2-20261018/validation.json).
- [Tổng hợp thiết kế Phase 3](tai-lieu-bo-tro/phase3-20261018/design-summary.json), [fixture oracle](tai-lieu-bo-tro/phase3-20261018/fixture-oracle.json), [oracle library](tai-lieu-bo-tro/phase3-20261018/oracle-library.json), [pair coverage](tai-lieu-bo-tro/phase3-20261018/pairwise-model-and-coverage.json), [manifest đầu vào](tai-lieu-bo-tro/phase3-20261018/source-manifest-before.json) và [validation tĩnh](tai-lieu-bo-tro/phase3-20261018/validation.json).

Checkpoint là bản sao tệp, không phải database backup. Các bản hỗ trợ giữ nguyên nội dung/checksum của bản gốc; manifest lịch sử có thể còn ghi đường dẫn tại thời điểm tạo. [Danh mục di chuyển và bản sao](danh-muc-di-chuyen.json) ánh xạ vị trí cũ sang vị trí trong thư mục này.

Artifact kiểm thử gốc vẫn nằm tại `DAMH/artifacts/runs/`, schema/ID map gốc tại `DAMH/runtime/`. Tài liệu nguồn, bài giảng và [truy vết A-H lịch sử](../traceability.md) giữ nguyên vị trí; các tài liệu trong hồ sơ này liên kết đến chúng khi cần. Chỉ sao chép thư mục HoanThanhPlan sẽ chưa bao gồm toàn bộ raw artifact hoặc DB.

- [Hồ sơ Phase 4](04-automation-va-tai-lap.md), [source manifest sau sửa](tai-lieu-bo-tro/phase4-20261018/source-manifest-after.json), [gói source](tai-lieu-bo-tro/phase4-20261018/phase4-source.zip), [gói runtime evidence](tai-lieu-bo-tro/phase4-20261018/selected-runtime-evidence.zip) và [validation](tai-lieu-bo-tro/phase4-20261018/validation.json).

## 5. Quy ước khi tiếp tục hoàn thiện plan

- Lưu nội dung mới vào `DAMH/docs/HoanThanhPlan/`; cập nhật mục lục và trạng thái phase trong cùng lượt làm việc.
- Giữ mã UR/BR/AC/test ổn định và liên kết tới nguồn; phân biệt kết quả lịch sử với run mới.
- Bám baseline Directus đã pin, không tự thêm quy tắc nghiệp vụ; chi tiết chưa đủ căn cứ tiếp tục OPEN.
- Giữ nguồn, raw schema, report và checkpoint lịch sử; không sửa checksum/provenance để biểu diễn kết quả mới.
- Không đưa credential, private key hoặc database dump vào hồ sơ đọc chung; nội dung gom ở đây chưa đồng nghĩa đã commit/publish.

- [Hồ sơ Phase 6](tai-lieu-bo-tro/phase6-20261018/evidence-index.json): protocol/source freeze, sáu trial, phân tích lịch sử, gói source/evidence và validation. [Bảng case tích lũy](06-ket-qua-case.csv): 94 passed, 163 NOT_RUN; không ghi đè bảng lịch sử Phase 3–4.
