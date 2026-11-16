# Điều tra BLOCKED_LICENSE — P09, 15/11/2026

## Kết luận có bằng chứng

Nguyên nhân trực tiếp là **P09 không có grant hiệu lực**: LICENSE_KEY rỗng, LICENSE_TOKEN env không có, /license source=null, invalid_reason=null và custom_permission_rules_enabled=false. Status active ở đây không phải xác nhận đã kích hoạt grant có custom rules: source baseline compute-license-status.ts, nhánh không có license nhưng còn trong giới hạn core, trả active.

Lab cũ dùng cùng pinned image nhưng hiện exited; key trong container cũ có giá trị và khớp cấu hình local cũ (chỉ so trong bộ nhớ, không in/hashing key). PUBLIC_URL cũ 8055 khác P09 18055, DB/volume tách biệt. Không khởi động lab cũ/DB cũ để truy vấn; **current entitlement/project binding lab cũ CHƯA XÁC MINH**, không dùng historical active làm current proof.

[Report sanitize](report.json) ghi so sánh; [source index @SHA](source-index.json) ghi nguồn đã đọc. Baseline source 4f77933bf9551cac6b289576078783e189b8f4e3; không sửa code Directus. Đã đối chiếu thêm manager.js trong image chạy: activation dùng project_id/public_url và new_project_id, phù hợp kết luận về binding.

## Đã kiểm tra gì

- Docker inspect chỉ lấy trường cần thiết trong bộ nhớ: key/token có hay không, equality, image/state/PUBLIC_URL; không in Config.Env hoặc credentials.
- P09 bootstrap login; admin GET /license, /server/health và /policies đều HTTP200, có policy admin_access=true. Admin access được chứng minh bằng guard/admin endpoint, không dựa field users.me.admin_access null.
- P09 /license: source=null, status active, custom rules false; không có invalid_reason. Đây không phải activation lỗi, vì chưa có grant được cấp.
- Đọc-only POST /license/preview bằng key hiện có: HTTP200, plan Open Innovation Grant, production_enabled=true, expiry/renewal không nêu. Không persist key/token trên P09, không activate/deactivate/update/resolve grant. Preview không chứng minh entitlement cụ thể hoặc quyền thêm project.
- Log 300 dòng gần nhất của cả hai container được phân loại trong bộ nhớ; không thấy thông báo activation/binding/invalid/refresh failure tương ứng. Không lưu raw log; không suy rằng không có binding chỉ vì không có lỗi.
- Một probe package-level preview riêng không thực hiện được trong context node độc lập; chỉ lưu error type, **không diễn giải thành key invalid**, vì HTTP preview có context app đã thành công.
- Project P09 có project_id. Project_id/binding cũ chưa đọc từ DB đang dừng; không clone DB/token/project ID để giả cùng project.

## Vì sao chưa áp dụng key cũ

get-license-key.ts ưu tiên env. compute-license-action.ts cho thấy thêm env key vào DB mới có thể gọi activate. manager.ts:325–346 gửi key + project_id + public_url và có thể lưu new_project_id. Vì chưa có bằng chứng key này hỗ trợ project P09 bổ sung độc lập, việc thử activate rồi “xem có được không” không bảo đảm điều kiện **không tác động lab/binding cũ**.

Không chỉnh project_id, không copy token lưu DB cũ, không thay entitlement, không bypass cơ chế license hoặc đổi expected Reader. Key được preview nhận diện không đồng nghĩa mọi tính năng được cấp hoặc multi-project được cho phép.

## Phương án hợp lệ

1. Cấp grant/key riêng hợp lệ cho project P09 có custom_permission_rules_enabled, hoặc có xác nhận có nguồn từ quản trị license/cơ chế nhà cung cấp rằng activation P09 không transfer/revoke/thay đổi project cũ.
2. Chỉ khi đủ điều kiện đó, lưu P09_LICENSE_KEY vào private ignored runtime/profiles/r06-k05-p09-20261115-audit01/p09.env tại máy; không gửi vào chat/report và không đổi config/lab.env cũ.
3. Render compose --quiet; recreate **chỉ directus của exact namespace P09**, giữ nguyên DB/volume; không reset. Login và kiểm /license source/status/invalid_reason/effective entitlement lại; ghi boolean/source thay key/token.
4. Entitlement phải true trước khi tạo Reader row filter/field restrictions theo require_custom_rules_license đang có. Sau đó mới chuẩn bị adapter fixture/policy đúng project, seed riêng/map động và kiểm health/license/actor/policy/fixture/CLI để kết thúc P09. Không chuyển P10 trước gate.
5. Nếu grant không hỗ trợ custom rules, giữ BLOCKED_LICENSE cho Reader và các oracle liên quan; không coi N/A, không sửa assertion để tạo PASS.

Không tự liên hệ nhà cung cấp hoặc dùng billing portal/update activation. Người quản lý license có thể cung cấp bằng chứng quyền dùng P09 thay vì cung cấp key trong hội thoại.

## Những việc không phụ thuộc custom permission rules

**Đã làm:** admin-authenticated health/identity/license-read, resource isolation/image version, runner CLI/help/tracecov metadata; không campaign. Static P08 reference/schema/calculator và P09 isolation unit tests có thể tiếp tục offline.

**Có thể chuẩn bị tiếp:** schema/allowlist/reproducer analysis từ raw artifact lịch sử; phân tích source/oracle; read-only preflight admin. Mọi metadata/history vẫn gắn baseline gốc.

CRUD/score/contract của Editor về mặt nghiệp vụ không phải phép kiểm Reader, nhưng hiện actor/fixture P09 chưa provision nên **chưa đủ precondition để chạy TC01–TC03/TC07/TC09–TC13**. Không tự thay Editor bằng admin hoặc seed thiếu Reader rồi gọi regression13 đạt. TC04–TC06, Reader visibility/forbidden-field/write và campaign theo profile đó vẫn BLOCKED. Đây là phân loại dependency, không phải quyền chuyển P10 hay thay scope.

## Trạng thái cuối

**BLOCKED_LICENSE**; admin/health/CLI riêng đã xác minh; Reader policy/seed NOT_RUN; runtime coverage NOT_MEASURED. Lab cũ vẫn exited, không start/stop/reset/ghi hoặc thay binding. Lab P09 giữ chạy để tiếp tục. Không sửa raw OAS/report lịch sử, không commit/push hoặc sub-agent.
