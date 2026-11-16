# Phase 2 — Quy tắc quản lý schema và overlay

**Áp dụng:** thiết kế tiếp theo của R06/K05. Tài liệu này không tạo/cài overlay mới; profile hiện hành giữ nguyên. Căn cứ là lựa chọn bám baseline của người dùng, AGENTS.md và [review Phase 2](02-danh-gia-openapi-va-sinh-test.md).

## 1. Phân biệt năm loại tệp

| Loại | Được làm gì | Không được gộp kết quả với |
|---|---|---|
| Actor source | Snapshot nguyên bản từ /server/specs/oas, lưu actor/fixture/export run/hash | Actor khác, schema sửa tay hoặc upstream spec generic |
| Scoped raw | Chỉ giữ 10 operation đã chốt; giữ nguyên hợp đồng/components của source | Raw cũ nếu input hash khác mà không ghi version |
| Guided | Bổ sung example/ID hợp lệ và hướng dẫn chuỗi có provenance; giữ miền hợp đồng | Raw như thể có cùng chiến lược; schema đã sửa enum/range/response |
| Contract overlay | Bản thử nghiệm sửa required/type/enum/length/range/format/status/media/shape hoặc thêm giới hạn input | Raw/guided baseline; phải có tên/hash/kết quả riêng |
| Probe/test input | Ca biên/negative/quyền cố ý, không nhất thiết hợp schema | Thay đổi hợp đồng hay bằng chứng đã chạy nếu mới là thiết kế |

Không coi một copy sửa schema tại chỗ là raw vì “Directus đáng lẽ phải sinh thế”. Contract overlay có thể hữu ích để đo ảnh hưởng hợp đồng đầy đủ, nhưng cần luận cứ và thí nghiệm riêng; không phải bước bắt buộc Phase 2 hoặc quyết định tự động triển khai.

## 2. Đối chiếu profile hiện có

Diff [raw→guided seed 101](tai-lieu-bo-tro/phase2-20261018/raw-guided-diff.json) có 11 additions:

- Sáu `.example` ID trên GET/PATCH/DELETE detail của hai collection.
- Bốn media-type `.example` cho POST/PATCH của hai collection.
- Một `x-r06-k05-guidance` lưu fixture/query focus.

Không sửa enum/min/max/required/nullable/type/response; không có explicit links mới. Các example làm thay đổi dữ liệu/hiệu quả tìm kiếm nhưng không tự thu hẹp miền hợp lệ của schema. Chưa có consumer của `query_focus` trong harness được review; không gọi nó là cơ chế giới hạn bảy query. `--phases` giữa raw và guided còn khác stateful, cần ghi khi so sánh chi phí.

## 3. Hồ sơ tối thiểu khi tạo phiên bản mới

1. Lưu source bất biến: actor, export run, fixture/policy version, ID map snapshot/hash, OAS version, image digest, source commit và trạng thái harness.
2. Ghi loại overlay, lý do, BR/Q/GAP liên quan, đường dẫn JSON Pointer, old/new và bằng chứng nguồn. Không dùng output vừa quan sát một lần để tự sửa expected.
3. Xuất tệp riêng cùng manifest input hash/output hash, tool/script version và diff. Không ghi đè source hoặc report cũ. Với guidance dùng ID, ghi rõ map/run tạo ID; không hard-code ID vào logic tái lập.
4. Kiểm invariant của loại overlay: raw chỉ đổi scope; guidance không sửa contract keyword. Nếu diff chứa enum/min/max/format/required/response hoặc xóa query/nhánh array, phân loại lại thành contract/scope change và ghi phạm vi riêng.
5. Kiểm JSON/ref và OAS validator thích hợp khi triển khai; lưu giới hạn validator. Kiểm request thực tế khi thay links/hooks; schema đọc được chưa chứng minh công cụ dùng guidance.
6. Chạy thí nghiệm riêng sau preflight; lưu profile/hash/check failure/stop reason/restore. Không thay raw failure bằng kết quả overlay PASS. Không tắt check/shrinking, thêm broad skip hoặc nuốt exit code để tạo PASS.

Các trường hợp cụ thể:

| Đề xuất thay đổi | Phân loại và điều kiện |
|---|---|
| Thêm score=3, status=draft, category ID từ map làm example | Guidance; không đồng nghĩa generator chỉ dùng các giá trị này |
| Thêm OpenAPI links response ID → path ID | Guidance về chuỗi; ghi producer object/array, expression, operationId và bằng chứng transition/replay thật |
| Đổi timestamp thành date-time | Contract overlay; cần nguồn ngữ nghĩa, đúng công cụ và so raw riêng; không tự làm để giảm failure |
| Thêm maxLength name/title, enum status, min/max score | Contract overlay có căn cứ fixture, không trộn với schema gốc; phải xét request vs response và PATCH |
| Bỏ required title/score khỏi PATCH hoặc response projection | Contract overlay; không bỏ required toàn component để sửa mọi operation cùng lúc |
| Thêm 204/403/400, object response hoặc CSV/XML/YAML | Contract overlay; nguồn pin + request/response/precondition, giới hạn đúng nhánh; không thêm mọi status cho PASS |
| Giới hạn maxItems, loại POST array, bỏ query export/aggregate | Thay contract/scope tìm kiếm; cần ghi lý do/budget và phần coverage mất; không gọi profile đó raw scope 10 hiện hành |
| Hook đổi token/actor, payload hoặc setup/reset | Thay harness có ảnh hưởng chung; triển khai trong phase được giao, giữ interface và bằng chứng; không cài hook global ở review này |

## 4. Cách kiểm liên kết và tái lập chuỗi

Không chỉ ghi “stateful=true”. Mỗi transition có case ID/parent ID, producer response status, expression chọn ID, actual ID, consumer path và checks; ghi độ dài chuỗi thực tế. `is_inferred=true` khác explicit link nhóm bổ sung. Link object dùng data.id, array dùng data[*].id với lựa chọn phần tử xác định; không coi shape object/array thay thế nhau.

Replay phải dựng lại producer, dùng ID mới và kiểm mọi precondition. Nếu chỉ replay request cuối hoặc parent map không đầy đủ, giữ nhãn single-request/không đủ chain; không gọi là full-chain. Không reset giữa các bước; cleanup cả khi fail và khôi phục campaign đúng lab.

## 5. Tiêu chí tiếp nhận phiên bản overlay

Tệp nguồn/hash được bảo toàn; diff giải thích được từng thay đổi; reviewer đọc được source và BR liên quan; input hợp schema/hợp nghiệp vụ được phân biệt; report raw còn nguyên; không có credential; status thực nghiệm và giới hạn được ghi thật. Review bởi AI không thay chữ ký hoặc duyệt của thành viên.

Nếu thay đổi baseline/policy/scope/interface/global hooks hoặc cách bỏ qua failure ngoài phần phase được người dùng giao, phải xử lý quyết định tương ứng trước khi áp dụng. Quy tắc này không yêu cầu hỏi lại cho từng thao tác tài liệu hoặc công việc đã được giao rõ ràng.
