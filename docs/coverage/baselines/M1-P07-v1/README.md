# P07 / M1 — Baseline đề xuất có gap

Baseline **M1-P07-v1**, inventory **P07-INVENTORY-v1**, catalog **P07-CATALOG-v1**, schema P01 1.0.0.

**DRAFT / NOT_LOCKED**. Công việc tổng hợp P07 hoàn tất; acceptance M1 và scope giảng viên CHƯA XÁC MINH. Không có run/test mới. Không gọi 287 record hay 312 catalog record là denominator toàn hệ thống.

## Dữ liệu thống nhất

- [Manifest](baseline-manifest.json): pin source/version/digest từ manifest lịch sử; runtime image ID/arch/config/fixture/actor schema còn gap/null. Không gán historical run vào baseline mới.
- [Inventory](system-inventory.jsonl): 287 record (269 REST + 18 nhóm protocol/client), giữ ID/key/UNKNOWN, chỉ đổi inventory revision. [Lineage](inventory-lineage.jsonl) giữ shard revision và hash nguồn. Không rename P01 hoặc sửa shard cũ.
- [Capabilities](capabilities.jsonl), [unresolved](unresolved-routes.jsonl): giữ cả shared feature/non-HTTP, 38 entry unresolved/boundary từ ba shard, không coi mọi entry là HTTP operation. SEARCH/wildcard/constraint/deep provider cần review.
- [Requirements](requirements.jsonl): 49 SYS theo Appendix A/B và 13 LEGACY theo alias lịch sử. I/L/C và priority 49 SYS lấy thiết kế gốc, kiểm công thức §4.1; chưa review. Legacy không gán lại I/L/C, priority UNKNOWN có gap; P1 cũ vẫn ở source.
- [Catalog](test-catalog.jsonl), [RTM](rtm-links.jsonl): giữ 312 canonical IDs/version/alias/lineage P06, đồng bộ revision/requirement refs. 62 DIRECT dự kiến (49 design +13 legacy) và 83 SUPPORTING reuse; mandatory=false chờ scope. DIRECT thiết kế không là execution coverage.
- [Binding proposals](binding-proposals.json): requirement→route/protocol candidate theo prefix/module. **Chưa xác nhận endpoint exact cho từng test/actor**; có GAP-P07-BINDING. Không dùng các liên kết rộng này làm dispatch/hit evidence.
- [Group review](group-review.json): cả ba shard, từng capability và 22 nhóm công việc kế hoạch đã xét; không giả Directus có đúng 22 module. [App mount review](app-mount-review.json) xét 46 khai báo app use/get ở source pin. Có nhóm shell/UI/protocol, không nhân app mount thành operation. Không có nhóm literal app chưa được phân loại, nhưng child router/deep dynamic coverage vẫn còn gap.
- [Gaps](gaps.jsonl), [decisions](decisions.jsonl): 34 OPEN và 7 PROPOSED kế thừa/tạo thêm; không đóng gap tiền nhiệm hoặc giả phê duyệt. Inherited IDs giữ nguyên.
- [Input fingerprints](input-fingerprints.json), [audit evidence](audit-evidence.json): chứng cứ kiểm offline/bảo toàn. [M1 status](m1-status.json) tách phase work khỏi milestone acceptance.

Mọi requirement applicability UNKNOWN, review DRAFT và có DIRECT design hoặc gap; không chuyển Conditional thành N/A. Trường mandatory=false nghĩa chưa chọn bắt buộc, không phải quyết định loại khỏi scope.

## MVP đề xuất, subset rõ

[Selection](selection-manifest.json) DRAFT chọn đúng 13 LEGACY-TC01–TC13 và resolve alias thành 13 canonical test/version. Đây là regression subset trên qa_articles/qa_categories, 5 source template GET list/POST/GET detail/PATCH detail/DELETE detail; không thêm bulk PATCH/DELETE. Hai collection binding từng có 10 cặp method/path trong allowlist lịch sử; không tạo thêm 10 inventory IDs ở đây.

Không chọn lại P3-ST-02 cạnh alias S1 để nhân CRUD. TC13 business/contract failure vẫn giữ ở report gốc; MVP không biến finding thành PASS. Thứ tự đề xuất: xác minh profile/license Reader/fixture/oracle và scope; replay regression/candidate failure có artifact mới trong phase được giao; rồi mở các Core AUTH/RBAC/MODEL/FILES theo requirement đã duyệt. GraphQL/UI/Realtime/provider chỉ trì hoãn công việc, không tự loại khỏi inventory.

Danh sách MVP có 13 ID là thống kê selection, không phải count coverage áp dụng. [Coverage summary](coverage-summary.json) chỉ cho subset REQUIREMENT, UNLOCKED, mọi count/percentage null và metric NOT_MEASURED; numerator rỗng không nghĩa 0%. Whole-system/code/schema/protocol coverage chưa đo. Run selection UNDECIDED, retry KEEP_ALL_REPORT_FLAKY, không chọn historical PASS để nghiệm thu baseline mới.

## Gap trước khi khóa M1

GAP-P07-SCOPE: cần quyết định scope có người/ngày/nguồn; tìm trong coverage records/kế hoạch chưa có approval đủ điều kiện. Không kết luận ngoài phạm vi tìm kiếm rằng giảng viên chưa từng quyết định.

GAP-P07-RUNTIME: chưa có runtime image/config/profile/fixture/current admin+actor OAS. Không export live trong phase. GAP-P07-BINDING: route candidate phải review từng requirement/test, actor/policy và mandatory set.

GAP-P07-DEPTH: generated GraphQL fields, WS/collab messages, Studio views, dynamic tools/extensions/drivers, SDK commands và unresolved declaration chưa hoàn chỉnh. Capability có candidate requirement vẫn không chứng minh mọi operation/branch đã có oracle.

GAP-P07-ORACLE: expected nguồn còn OPEN/CONDITIONAL và thiết kế cần đối chiếu behavior source/profile; score rủi ro là đề xuất. GAP-P07-PROVENANCE: một số inherited refs trỏ hash kế hoạch trước note P06; giữ hash cũ và ghi citation gap, không thay hash frozen refs để giả đã đọc cùng version. Không dùng stale citation làm phê duyệt.

Kiểm source groups là audit đầu vào hữu hạn, không chứng nhận mọi chức năng Directus đã được đặc tả. [Audit evidence](audit-evidence.json) liệt kê missing inventory/capability mapping và citation gap. [Handoff P07](../../handoffs/P07.md) nêu DoD, checks thực và next action.

Không sửa harness/runtime/fixture/report/raw OAS, chạy unit/P02/API/lab, cài package, commit/push/PR/issue, liên hệ hoặc sub-agent.
