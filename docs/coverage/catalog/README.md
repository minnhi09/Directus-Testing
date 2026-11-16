# P06 — Canonical map và reuse catalog

Revision P06-CANONICAL-v1; hợp đồng P01 1.0.0. Đây là audit dữ liệu thiết kế/source/report, không chạy test.

[Canonical catalog](canonical-catalog.jsonl) có 312 record đăng ký: 257 P3 ID giữ nguyên + 6 scenario identity S1–S6 + 49 thiết kế TC14–TC62. **312 không phải mẫu số ca độc lập**: chưa chứng minh equivalence mọi overlap scenario/P3, chưa selection/acceptance. Không cộng alias, request, retry hoặc examples.

[Checklist 257](catalog-257-checklist.json) có từng ID và 17 nhóm, đều có đúng một identity mapping. [Alias/reuse mapping](alias-reuse-mapping.jsonl) có 319 dòng: 257 identity, 13 alias lịch sử, 49 thiết kế hiện tại. exact-reuse ở dòng identity chỉ là tái dùng đúng định nghĩa catalog cũ, không chứng minh requirement mới đã đạt hoặc code chạy được. Partial/delta/revised/new phản ánh khác biệt thiết kế, không phải verdict test.

[Reuse comparisons](reuse-comparisons.jsonl) có 83 edge SUPPORTING với actor, request method/path/payload/query, precondition, oracle và expected thực của candidate cùng thiết kế đích. Các edge này không là alias. [RTM links](rtm-links.jsonl) theo P01 có 49 DIRECT từ thiết kế đích tới SYS requirement và 83 SUPPORTING từ nguồn cũ. DIRECT này là ý định thiết kế NOT_RUN; mandatory=false chờ P07, không phải phủ requirement bằng execution. Operation IDs và fixture bindings chưa khóa, có gap; không tự tạo requirement registry thứ hai.

[Design assessments](design-assessments.json) giữ 44 phân loại gốc (16 partial/4 revised/24 new) và 5 delta TC58–TC62. [Lineage parents](lineage-parents.json) giữ reference tới thiết kế parent trước tách, không thêm execution/case denominator. TC42v2 chỉ login Studio; TC49v2 notification; TC55v2 AI success. TC58←42, TC59←49, TC60/61/62←55. Parent version pre-split-plan-design là nhãn truy vết thiết kế cũ theo mục 8.2, không phải phiên bản execution được xuất bản.

[Historical observations](historical-observations.jsonl) chỉ trích id/status/verdict/cleanup/run_id và source pointer từ 3 report chỉ định. 182 observation gồm overlap, không phải 182 ca độc lập; không chuyển baseline/report sang phiên P06. Catalog vẫn có NOT_RUN và 47 OPEN/68 CONDITIONAL oracle (142 ASSERTABLE); các giá trị không suy ra PASS. TC13 source status failed, business passed/contract failed được giữ nguyên. Report/raw OAS cũ bất biến.

Alias giữ đúng mục 5: TC01–06→S1–S6; TC07→P3-ST-01; TC08→P3-AUTHZ-DR-047; TC09–12→score POST -1/0/5/6; TC13→P3-CONTRACT-QA_ARTICLES-OBJECT. Không đổi mã theo thứ tự E.3. S1 và P3-ST-02 cùng CRUD article vẫn không gộp: fixture/setup/oracle chuỗi chưa chứng minh trùng hoàn toàn.

[Discrepancy log](discrepancies.md) và note §8 kế hoạch sửa cách diễn giải reuse; không đổi lịch sử. [Gaps](gaps.jsonl) giữ binding/profile, delta/oracle-open, history và duplicate review. Owner là đề xuất, không giả xác nhận Nhân/Trâm/Lành.

Provenance ARTIFACT dùng hash file local vì harness dirty; không gắn HEAD cho byte chưa commit. Source version catalog-v1-<hash8> là nhãn snapshot P06; cleanup/precondition/oracle đầy đủ ở JSON pointer gốc. Trường prerequisites chỉ chứa ID hợp lệ, phần free-text vẫn có trong input_partition/source; automation UNKNOWN không đồng nghĩa source không có runner. Chỉ chưa certify implementation từng ID. Không sửa schema/harness/helper/fixture/oracle source.

[Input fingerprints](input-fingerprints.json) ghi đầu vào trước sửa; kế hoạch là file có sẵn duy nhất sửa chủ ý để thêm đính chính P06. [Audit evidence](audit-evidence.json) ghi kết quả static thực; [handoff](../handoffs/P06.md) ghi DoD/gaps/next action. API/code coverage NOT_MEASURED, test NOT_RUN, remote CI NOT_RUN; không chạy runner/P02/API/lab.
