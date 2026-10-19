# Phase 1 - Review tĩnh đặc tả và khoảng trống kiểm thử

**Ngày:** 18/10/2026. **Phương thức:** Đối chiếu tài liệu, cấu hình lab, code assertion và artifact lịch sử.  
**Người thực hiện:** AI trong phiên làm việc này. Không có xác nhận review/duyệt của thành viên được suy đoán hoặc gán thay.  
**Đối tượng:** [Đặc tả v0.2](01-yeu-cau-va-dac-ta.md), [truy vết nghiệp vụ](01-truy-vet-nghiep-vu.md), test hiện có và [decision backlog Phase 0](00-quyet-dinh-va-phu-thuoc.md). Bản 0.2 ghi lựa chọn bám baseline của người dùng và [đối chiếu source P1-05](01-doi-chieu-baseline-p1-05.md).

## 1. Mục tiêu và cách review

Kiểm tra yêu cầu có rõ, có nguồn và quan sát được; tìm mâu thuẫn giữa fixture/policy/OpenAPI; xác định test thực sự chứng minh điều gì. Không dùng test PASS lịch sử để phê duyệt mọi yêu cầu hoặc khẳng định không có bug.

Checklist đã thực hiện:

- [x] Phân biệt hệ thống Directus, fixture quản lý nội dung và harness K05.
- [x] Phân biệt yêu cầu môn học, quy tắc lab kế thừa, hành vi quan sát và đề xuất mới.
- [x] Có actor, ranh giới, user story, data dictionary, BR và acceptance criteria.
- [x] Tách missing/null/empty/blank/sai kiểu; không tự bổ sung minLength/trim/coercion policy.
- [x] Đối chiếu nguồn của default, required, nullable, enum/range và quan hệ.
- [x] Kiểm tra URI/actor, luồng chính/ngoại lệ, read-back và trạng thái dữ liệu.
- [x] Gắn mọi BR với test hiện có hoặc gap task; giữ S1-S6/INV-01 đến INV-11.
- [x] Phân biệt oracle nghiệp vụ, contract và precondition/harness.
- [x] Ghi rõ phần bằng chứng hiện hữu chỉ là mẫu hoặc phụ thuộc nguồn API khác.
- [x] Đánh giá rủi ro bằng thang điểm có giải thích, không bịa xác suất lỗi.
- [x] Giữ nguyên source/evidence gốc và không chạy test mới.

## 2. Kết quả review có vị trí và tác động

Các nhãn REV-* là mục review của Phase 1, không phải số product defect.

| ID | Vị trí/điểm đối chiếu | Phát hiện và tình huống | Tác động | Xử lý ở Phase 1 / bước tiếp |
|---|---|---|---|---|
| REV-01 | ensure_schema trong lab-components.sh so với ItemsQaArticles/ItemsQaCategories của schema Editor | Max 80/120, enum status và range score chưa được OpenAPI biểu diễn đầy đủ | Generator có thể tạo dữ liệu hợp schema nhưng sai BR; không đủ căn cứ gọi mọi RejectedPositiveData là product defect | Đã tách config/contract/business oracle; GAP-01/02/10, Phase 2-4 |
| REV-02 | ensure_schema status default draft; required title/score/name trong schema dùng chung | Required UI/meta, DB default và request body required không đồng nhất; PATCH có thể dùng cùng schema tham chiếu | Áp required/default sai có thể tạo negative expectation sai hoặc test PATCH không thực tế | Đã tách POST/PATCH và Q-03; GAP-13 |
| REV-03 | case_query_fixture ở invariants.py:544, gọi all_articles:288 | Expected lấy ID từ map nhưng title/status từ GET nền rồi tính filter/sort/search | Lỗi dữ liệu hoặc hành vi ở GET nền có thể làm oracle và target cùng sai; chưa hoàn toàn độc lập từ seed | Ghi đúng hạn chế trong đặc tả/truy vết; GAP-08 |
| REV-04 | scenario_sort_pagination ở lab-components.sh:1158 | Lấy full list đã sort từ API rồi cắt làm expected của hai page | Chứng minh tính nhất quán phân trang nhưng không tự chứng minh thứ tự sort đúng theo đặc tả | Không sửa kết quả S3; GAP-08 bổ sung ground truth/collation |
| REV-05 | scenario_reader_no_draft ở lab-components.sh:1188 | Draft detail được yêu cầu cả internal_notes; Reader vốn bị cấm field này | HTTP 403 có thể do field policy, chưa cô lập được row-policy draft trên detail | Ghi AC-15 dùng field công khai; GAP-14. Smoke không filter và INV-10 vẫn là bằng chứng bổ trợ, không bỏ qua chúng |
| REV-06 | case_reader_visibility:904 và smoke:920 | INV-10 chủ động filter published; smoke có request không filter và kiểm sáu published | Dùng riêng INV-10 có thể bỏ sót policy trả draft khi không filter; dùng riêng smoke chưa so đúng set ID | Đã truy vết cả hai; GAP-06/14 bổ sung exact set/query/detail phù hợp |
| REV-07 | check_field_validation:831; case_invalid_field_rejection:870 | INV-09 sai cả archived và score=-1; smoke đã có hai probe riêng | INV-09 không chứng minh riêng từng ràng buộc; smoke cũng chưa phủ miền/biên/null/omission | Không tạo lại probe trùng; GAP-01/02/13 bổ sung phần thiếu |
| REV-08 | case_auth_invalid_token, anonymous_denied, editor_crud, invalid_field_rejection, reader_visibility, reader_write và các scenario negative | Một số nhánh chấp nhận mọi non-2xx; post-delete có chỗ chỉ xét không còn data | 5xx có thể bị hiểu là từ chối đúng hoặc tài nguyên không còn; network/body thiếu có thể làm test yếu | Đặc tả AC yêu cầu lỗi thích hợp, không coi 5xx là PASS; GAP-07. Phase 1 chưa sửa assertion/historical report |
| REV-09 | case_editor_crud/positive_operations/reader_write/relation_nullification | Read-back chỉ so một số field; relation test chủ yếu kiểm category null | Có thể bỏ sót đổi metadata/notes/status hoặc field khác; chưa chứng minh toàn bộ row không đổi | Ghi giới hạn mẫu; GAP-04/05/07, không đổi lời mô tả report cũ |
| REV-10 | ensure_permissions_and_users:562 so với test hiện có | Reader categories read được cấu hình; Reader POST/DELETE/category write và nhiều anonymous operation chưa có functional evidence được chọn | Ma trận quyền mục tiêu rộng hơn số ô đã kiểm thử | Gắn CONFIG_ONLY/PARTIAL_EVIDENCE, GAP-06; không gọi schema absence là test quyền |
| REV-11 | article_spec và timestamp/JSON schemas | Seed published có timestamp, metadata thường object; không có validation buộc published có thời điểm hoặc metadata có key cố định | Từ ví dụ seed có thể vô tình tạo quy tắc nghiệp vụ không tồn tại | Đã ghi rõ không thêm quy tắc này; timestamp/JSON/nested giữ Q-04/05 |
| REV-12 | Phase 0 provenance và run metadata | Source baseline, checkout và tài liệu Phần 1 có SHA khác; run có dirty tree | Phân tích code khác bản có thể bị gán nhầm root cause hoặc tái lập hoàn toàn | Giữ nguồn/hash và TR-02/04; GAP-11 ở Phase 4-5 |
| REV-13 | Aggregate probe và contract-schema-candidates | Aggregate request còn có fields rỗng; runtime object/204 có thể hợp lý nhưng khác schema | Bỏ thành phần request khi mô tả làm reproducer thiếu chính xác; contract failure không tự là bug nghiệp vụ | AC-25 ghi fields rỗng; giữ FAIL/candidate, GAP-10/15 |

Các line number ở bảng là vị trí lúc review, function name là điểm tìm ổn định. Nguồn được ghim bằng hash trong [source manifest](tai-lieu-bo-tro/phase1-20261018/source-manifest-before.json). Không có kết luận product defect mới được xác nhận trong review này.

## 3. Backlog bổ sung để mọi yêu cầu có đường kiểm chứng

GAP-* là đầu việc đề xuất cho phase sau, không phải test ID đã triển khai. Mỗi mục có điều kiện bắt đầu, đầu ra và tiêu chí nghiệm thu; không phân công cá nhân trong tài liệu này.

| ID | Điều kiện bắt đầu/phụ thuộc | Việc và đầu ra cần tạo | Tiêu chí nghiệm thu | Phase |
|---|---|---|---|---|
| GAP-01 | BR-02/03, Q-01/03 được phân loại đủ rõ | Bộ ca name/title: non-null, required, 79/80/81 và 119/120/121; empty/blank/Unicode riêng | Mỗi lớp/biên có nguồn expected, request độc lập và không tạo row khi từ chối | 2-4 |
| GAP-02 | BR-04/05, Q-02/03 | Score 0-5/ngoài miền và status enum; tận dụng probe riêng hiện có | Không để một field sai che field khác; có positive, negative và read-back | 3-4 |
| GAP-03 | Q-04/05; định nghĩa giá trị JSON/timestamp chuẩn | Null/round-trip timestamp, metadata và internal_notes của Editor | So đúng ý nghĩa dữ liệu, không chỉ POST 2xx; không tự thêm điều kiện published-time | 2-4 |
| GAP-04 | BR-09/10; target và invalid ID được xác minh | Null/invalid reference và xóa category | Không orphan/mất article; category=null và field còn lại được so; cleanup đạt | 3-4 |
| GAP-05 | Có snapshot field nghiệp vụ đầy đủ, BR-12 | PATCH bảo toàn field không gửi; xác định omission/default | Thay đổi đúng field, các field khác so trước/sau; không chỉ title/category | 3-4 |
| GAP-06 | Ma trận actor/operation và input hợp lệ; đúng lab | Reader category read; Reader/anonymous denied CRUD còn thiếu, query/projection theo quyền | Kiểm đúng nguyên nhân từ chối, read-back/absence, ghi rõ ô chưa chạy hoặc blocked | 3-4 |
| GAP-07 | AC-13/17-19/24 và nguồn error contract | Củng cố negative/delete oracle, tránh 5xx/network/malformed body tạo PASS | Có regression về assertion phù hợp nếu sửa harness; giữ report lịch sử, không nới expected | 2-4 |
| GAP-08 | Giá trị seed và quy tắc collation/search đã xác định | Expected query từ seed/map độc lập, phân biệt consistency với correctness | Sai dữ liệu/sort ở GET nền không thể tự tạo oracle làm target PASS | 3-4 |
| GAP-09 | BR-16/22, semantics projection đã rõ | Kiểm đủ field requested, field cấm, wildcard/nested trong phạm vi cho phép | Không lộ dữ liệu, có đủ field cần có; không suy từ chỉ row count | 2-4 |
| GAP-10 | Đúng schema/source/hash, scope object/array rõ | Đối chiếu request/response required/shape/status/content; quản lý overlay riêng | Raw bất biến, mismatch được triage và giữ artifact; không tự sửa spec để xanh | 2,5 |
| GAP-11 | Source baseline và cấu hình chung đã chốt | Củng cố provenance, helper bàn giao, replay full-chain/restore | Phân biệt đúng bản code/fixture/schema; không nói single-request là full-chain | 4-5,9 |
| GAP-12 | Positive auth precondition và Q-06 | Kiểm chứng token sai không được chấp nhận nhầm qua error handling | Đúng phạm vi users/me, loại trừ 5xx/network; không mở rộng mặc định thành test toàn auth subsystem | 3-4 |
| GAP-13 | Q-02/03 có quyết định/nguồn rõ cho từng field/operation | Case missing/null/default/coercion theo POST/PATCH | Không áp required/default sai tầng; mỗi expected chưa rõ phải OPEN, không gán bug | 2-4 |
| GAP-14 | BR-15, draft/published ID và projection public | Draft detail chỉ public fields; list không filter/filter draft và exact fixture set | Cô lập row-policy khỏi field-policy; 403 có bằng chứng nguyên nhân thích hợp | 3-4 |
| GAP-15 | Có aggregate request đủ query, control, runtime/source đúng bản | Triage robustness 500 và lỗi nghiêm trọng mới | Reproducer tối giản nhưng đủ tiền đề, control/log/source và kết luận có giới hạn | 5 |

Các gap này liên kết lại P2/P3/P4/P5 trong kế hoạch; chưa tạo task/issue bên ngoài hoặc triển khai code.

## 4. Trạng thái từng công việc Phase 1

| Task | Trạng thái thực tế | Đầu ra |
|---|---|---|
| P1-01 | Hoàn thành tài liệu phạm vi | Mục 1-3 đặc tả |
| P1-02 | Hoàn thành user story có nguồn, chưa có xác nhận khách hàng/thành viên mới | 10 UR ở mục 4 |
| P1-03 | Hoàn thành danh mục quy tắc kế thừa | 26 BR và 6 TR; nguồn/mức khẳng định rõ |
| P1-04 | Hoàn thành tiêu chí chấp nhận bản 0.2 | 26 AC, có giới hạn OPEN và kiểm tra dữ liệu |
| P1-05 | Hoàn thành ở mức đặc tả: hướng baseline đã chốt, các tình huống được phân biệt, expected có nguồn và phần chưa rõ được ghi OPEN | 7 nhóm Q-01 đến Q-07 có căn cứ/giới hạn và gap task; xác minh kỹ thuật chuyển sang Phase 2–4, không coi câu hỏi OPEN là PASS |
| P1-06 | Hoàn thành đánh giá rủi ro đề xuất | 10 rủi ro, thang I/L và ưu tiên |
| P1-07 | Hoàn thành truy vết tài liệu | 26 dòng BR→UR/AC→API/actor→test/oracle/evidence/gap, CSV và docs/traceability.md |
| P1-08 | Hoàn thành review tĩnh bởi AI | Checklist, 13 mục review và 15 gap task; không phải peer review của người |

## 5. Kết luận review và phần còn phải quyết định

Bộ tài liệu đủ để tiếp tục review schema và thiết kế test cho phần BASELINE. Mọi BR có expected cốt lõi, nguồn và test hoặc đầu việc bổ sung; không có yêu cầu ưu tiên cao bị bỏ trống đường kiểm chứng.

**Hoàn thành Phase 1 ở phạm vi tài liệu và review tĩnh.** Tiêu chí phase cho phép quy tắc chưa rõ được ghi mở. Empty/blank/Unicode, coercion, omission/default theo operation, timestamp/JSON, error contract và search/collation còn các chi tiết kỹ thuật cần nguồn hoặc runtime ở Phase 2–4; không triển khai assertion cứng phụ thuộc chúng trước khi làm rõ. Đây không phải nghiệm thu runtime hoặc xác nhận mọi expected đã được kiểm chứng.

Người dùng đã chọn bám baseline, không thêm quy tắc nghiệp vụ. Phần còn thiếu được xử lý bằng tài liệu/source đúng bản và bằng chứng kỹ thuật phù hợp; không hỏi lại nhóm có muốn tự thêm rule riêng trừ khi họ đổi hướng. Probe runtime chỉ cung cấp observation; một observation đơn lẻ không tự trở thành yêu cầu.

Không sửa harness, fixture/policy, raw schema, report gốc, G1 hay lịch sử Git trong Phase 1. Cần giữ hai invariant FAIL và hạn chế của các test PASS khi báo cáo.

## 6. Cập nhật sau phản hồi của người dùng

- Đã ghi DEC-P1-01 đến DEC-P1-04 trong [đối chiếu baseline P1-05](01-doi-chieu-baseline-p1-05.md); quyết định hướng đặc tả không còn chờ xác nhận.
- Đã đọc và lưu 22 tệp đúng commit 4f77933, không checkout source khác hay chạy API.
- Source củng cố việc tách required create/update, không gán mọi token/not-found cùng status và không coi search là title-only.
- Default, timestamp, JSON/coercion và collation vẫn có phần cần nguồn DB/runtime cụ thể. Không thay quan sát lịch sử hoặc tạo yêu cầu mới để khép câu hỏi.
- Điều chỉnh trạng thái khi thực hiện Phase 2 theo phần giải thích đã gửi người dùng: P1-05 hoàn thành ở mức đặc tả; câu hỏi kỹ thuật vẫn OPEN và được bàn giao sang [review Phase 2/VFY](02-danh-gia-openapi-va-sinh-test.md). Không để toàn Phase 1 chờ vô hạn phần thực thi thuộc phase sau.
