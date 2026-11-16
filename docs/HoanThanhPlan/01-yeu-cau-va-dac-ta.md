# Phase 1 - Yêu cầu người dùng và đặc tả phạm vi R06 + K05

**Phiên bản:** 0.2, ngày 18/10/2026, Asia/Bangkok.  
**Trạng thái:** Người dùng đã chọn bám baseline Directus đã pin, không thêm quy tắc nghiệp vụ. Đặc tả đã review tĩnh bằng AI và đối chiếu source đúng commit; chưa có xác nhận peer review của thành viên hay nghiệm thu runtime mới.  
**Phạm vi công việc:** Tài liệu và truy vết; không sửa hệ thống, fixture/policy, schema hoặc test, không chạy lại lab. Kết quả test được dẫn là lịch sử, không phải nghiệm thu đặc tả mới.

## 1. Mục tiêu, ranh giới và cơ sở đặc tả

### 1.1. Mục tiêu hệ thống trong lab

Directus cung cấp backend truy cập dữ liệu SQL qua API, cùng xác thực, phân quyền, validation và quản lý quan hệ. Phạm vi lab mô phỏng quản lý chuyên mục/bài viết: Editor quản lý dữ liệu; Reader đọc bài công khai; người không có quyền không được đọc/ghi dữ liệu được bảo vệ.

R06 là hệ thống được kiểm thử. K05 là kỹ thuật kiểm thử API dựa trên schema/fuzzing; Schemathesis sử dụng OpenAPI Directus xuất ra để sinh request và kiểm tra contract. Scenario/invariant bổ sung expected nghiệp vụ không được schema mô tả đầy đủ.

Đây là yêu cầu **cho phạm vi fixture lab**, không phải bản đặc tả toàn bộ Directus hoặc yêu cầu được thu thập từ một khách hàng CMS thực tế. Các user story dưới đây là diễn giải có truy vết từ tài liệu lab, không phải phát biểu phỏng vấn người dùng.

### 1.2. Phạm vi chức năng

- Hai collection `qa_categories`, `qa_articles`; bốn actor admin, editor, reader, anonymous.
- Mỗi collection có GET list, POST, GET detail, PATCH detail, DELETE detail: tổng cộng 10 operation trong campaign.
- Query trọng tâm: fields, filter, sort, limit, offset, page, search; aggregate chỉ là probe robustness bổ trợ đã có.
- `/users/me` được dùng để kiểm tra token không hợp lệ; login, health và schema export là các bước hỗ trợ/precondition, không được cộng thành operation campaign mới.
- Chỉ POST object đơn được đặc tả đầy đủ cho các luồng nghiệp vụ ở bản này. OpenAPI cho phép cả object/array; cách sinh/kiểm tra array và giới hạn kích thước cần mô tả riêng ở Phase 2-3, không được âm thầm coi array là ngoài schema.
- Bulk PATCH/DELETE, UI/Studio automation, GraphQL, WebSocket, hiệu năng, concurrency và API quản trị không thuộc campaign chính.

| Thao tác | Categories | Articles |
|---|---|---|
| GET list | `GET /items/qa_categories` | `GET /items/qa_articles` |
| POST object | `POST /items/qa_categories` | `POST /items/qa_articles` |
| GET detail | `GET /items/qa_categories/{id}` | `GET /items/qa_articles/{id}` |
| PATCH detail | `PATCH /items/qa_categories/{id}` | `PATCH /items/qa_articles/{id}` |
| DELETE detail | `DELETE /items/qa_categories/{id}` | `DELETE /items/qa_articles/{id}` |

Trong bảng truy vết, cách viết `POST/PATCH collection[/id]` là viết gọn cho POST ở collection và PATCH ở detail như bảng trên, không phải URL gửi thực tế. `{id}` luôn lấy từ response/map phù hợp.

### 1.3. Nguồn và mức độ khẳng định

| Mã nguồn | Tài liệu/tệp | Giá trị khi xây dựng expected |
|---|---|---|
| SRC-01 | [G0](../g0-quyet-dinh-ky-thuat.md), [permissions](../permissions.md), quy tắc lab hiện có | Phạm vi và chính sách lab đã được ghi nhận; không lấy đoạn lịch sử trước license làm trạng thái hiện tại |
| SRC-02 | [lab-components.sh](../../scripts/lab-components.sh): ensure_schema, ensure_primary_id, ensure_relation | Cấu hình kiểu, nullability, độ dài, default, validation và quan hệ; cấu hình không tự chứng minh mọi response API |
| SRC-03 | Cùng tệp: ensure_permissions_and_users, ensure_policy, ensure_permission | Cấu hình actor/policy; quyền phải có test API, không chỉ xem schema |
| SRC-04 | Cùng tệp: category_spec, article_spec, seed_categories, seed_articles, write_fixture_map | Dữ liệu fixture kỳ vọng, ID động và điều kiện lặp lại seed |
| SRC-05 | [invariants.py](../../scripts/invariants.py), các hàm case_* | Oracle/assertion đang được triển khai; vẫn phải review vì assertion có thể chưa đủ mạnh |
| SRC-06 | [test matrix](../test-matrix.md), [schema Editor](../../runtime/profiles/windows-20261013-oig/schemas/r06-k05-v2/editor.json), [schema Reader](../../runtime/profiles/windows-20261013-oig/schemas/r06-k05-v2/reader.json) | Method/path và contract máy đọc được; không tự nâng schema thiếu ràng buộc thành hợp đồng nghiệp vụ đầy đủ |
| SRC-07 | [Phase 0](00-hien-trang-va-baseline.md), [selected evidence](00-selected-evidence.json) và artifact gốc | Quan sát thực thi lịch sử; dùng đối chiếu, không dùng làm nguồn duy nhất để chọn expected |
| SRC-08 | [Đối chiếu P1-05](01-doi-chieu-baseline-p1-05.md), [manifest 22 tệp source đúng commit](tai-lieu-bo-tro/phase1-20261018/baseline-source-manifest.json) | Lựa chọn baseline của người dùng và suy luận tĩnh có điều kiện từ commit 4f77933; không dùng source HEAD hiện tại thay bản pin hoặc coi đọc code là test runtime |

Hash của 20 tệp nguồn trước khi biên soạn được giữ tại [source manifest Phase 1](tai-lieu-bo-tro/phase1-20261018/source-manifest-before.json). Harness HEAD là `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, working tree có thay đổi từ trước. Không khẳng định SHA này mô tả toàn bộ working tree của các run cũ.

**Quyết định DEC-P1-01:** Bám baseline đã pin và cấu hình lab hiện có; không tự thêm minLength/trim/cấm coercion hoặc quy tắc published-time. Lựa chọn này đã được người dùng xác nhận. Chi tiết không đủ nguồn vẫn OPEN; không cần hỏi lại hướng này khi thực hiện phase tiếp theo.

Quy ước:

- **UR:** yêu cầu dưới góc nhìn người dùng; **BR:** quy tắc hệ thống/nghiệp vụ; **AC:** tiêu chí chấp nhận quan sát được; **TR:** yêu cầu kỹ thuật của bộ kiểm thử.

- **BASELINE:** quy tắc kế thừa được nguồn lab hỗ trợ, dùng làm cơ sở đặc tả.
- **OPEN:** chi tiết chưa đủ nguồn để chốt; phải giữ câu hỏi, không đặt assertion cứng hoặc tính coverage cho chi tiết đó.
- **OBSERVED:** hành vi đã thấy trong artifact; có thể phù hợp hoặc trái đặc tả, không tự động trở thành quy tắc.
- **PROPOSED:** nhiệm vụ/ngưỡng/cách thiết kế mới; chưa phải code đã có hay yêu cầu đã được phê duyệt.

## 2. Actor và ma trận quyền mục tiêu

| Actor | Mục đích | Categories | Articles | Giới hạn |
|---|---|---|---|---|
| Admin | Bootstrap, fixture/policy, health/schema/snapshot | Quyền phục vụ thiết lập lab | Quyền phục vụ thiết lập lab | Không dùng làm actor fuzz mặc định hay giả lập Reader |
| Editor | Quản lý nội dung lab | Create/read/update/delete | Create/read/update/delete, gồm draft và published | Policy không có admin/app access; không suy CRUD toàn Directus |
| Reader | Đọc dữ liệu công khai | Đọc | Chỉ đọc published, không internal_notes | Không create/update/delete trên hai collection |
| Anonymous | Người chưa xác thực | Không truy cập collection | Không truy cập collection | Không được cấp quyền qua việc thiếu token |

Quy tắc "không được ghi" là mục tiêu nghiệp vụ, không có nghĩa operation phải vắng trong OpenAPI. Reader article update hiện được cấu hình với writable fields rỗng để có thể thử PATCH có chủ đích; điều đó không cấp quyền sửa score.

Ma trận trên là mục tiêu đầy đủ. Bằng chứng hiện tại chủ yếu kiểm Reader PATCH article và anonymous GET; chưa thể đánh dấu mọi ô quyền đã được kiểm thử. Việc schema không có operation chỉ là quan sát schema.

## 3. Mô hình dữ liệu và vòng đời

### 3.1. Categories

| Trường | Đặc tả baseline | Điểm chưa được suy diễn |
|---|---|---|
| id | Integer, primary key, auto increment, non-null; ID thực tế được lấy từ response/map | Không yêu cầu ID liên tục; không chốt việc client tự gửi ID có được phép hay không |
| name | String, non-null, max_length 80, meta.required=true | Không suy non-null đồng nghĩa cấm empty/blank; cách đếm Unicode cần xác định |

### 3.2. Articles

| Trường | Đặc tả baseline | Liên quan/câu hỏi mở |
|---|---|---|
| id | Như category.id | BR-01 |
| title | String, non-null, max_length 120, meta.required=true | BR-03; Q-01 về empty/blank/Unicode |
| status | String non-null, validation draft/published, DB default draft; cấu hình lưu trữ max_length 16 | BR-04; không coi missing/null/blank là cùng một trường hợp |
| score | Integer non-null, validation 0-5, meta.required=true | BR-05; coercion của chuỗi/thập phân chưa chốt ở Q-02 |
| published_at | Timestamp nullable | BR-06; format/timezone/precision ở Q-04 |
| metadata | JSON nullable | BR-07; không có quy tắc chỉ cho object hoặc bắt buộc key nghiệp vụ |
| internal_notes | Text nullable; Editor có quyền, Reader không được thấy | BR-08, BR-16 |
| category | Integer nullable, quan hệ many-to-one đến categories | BR-09; không tự đưa nested create/update vào luồng chính |

### 3.3. Vòng đời và quy tắc không được tự thêm

- Article có status draft/published; chưa có workflow duyệt, điều kiện chuyển trạng thái hay ràng buộc published bắt buộc có published_at. Dữ liệu seed published có thời điểm không đủ để tạo quy tắc đó.
- PATCH là cập nhật một phần: những trường không gửi phải giữ nguyên trong phạm vi field nghiệp vụ đã đặc tả. Không áp default của POST hoặc required schema dùng chung một cách máy móc lên PATCH.
- Xóa category giữ article và đặt article.category về null theo SET NULL; không tự giả định cascade delete.
- Sau xóa article/category thành công, bản ghi không còn truy cập được theo semantics của baseline. Status chính xác cho lần GET sau xóa chưa được cố định thành 404.
- Fixture là ba category, 12 article, sáu draft/sáu published; dùng tên fixture và map để xác định ID, không coi ID 1-12 là điều kiện bất biến cho mọi lần dựng.
- User input không được mặc nhiên có metadata.fixture_key như seed. Seed có quy ước riêng để quản lý dữ liệu kiểm thử.

## 4. Yêu cầu người dùng

Mỗi UR dưới đây có actor, mục tiêu, luồng chính/ngoại lệ và acceptance criteria ở mục 6. Mức ưu tiên là đề xuất của đợt phân tích theo rủi ro ở mục 8, không phải độ nghiêm trọng defect đã xác nhận.

| ID | User story và mục tiêu | Tiền đề/luồng chính | Ngoại lệ và tiêu chí liên quan | Ưu tiên/rủi ro |
|---|---|---|---|---|
| UR-01 | Là Editor, tôi muốn quản lý bài viết để nội dung được lưu và cập nhật đúng | Login hợp lệ, payload/quan hệ hợp lệ; create → read → PATCH → read → delete | Dữ liệu sai/quyền sai phải được xử lý, không làm hỏng bản ghi; AC-01,03-09,11-13,24 | P0; R-03,R-05 |
| UR-02 | Là Editor, tôi muốn quản lý chuyên mục mà không mất bài viết liên quan | CRUD category; article tham chiếu category; xóa category | Giữ article và nullify quan hệ; AC-02,09-11 | P0; R-04 |
| UR-03 | Là người được phép đọc, tôi muốn lọc, sắp xếp, phân trang và chọn trường đúng | Fixture biết trước, actor và projection hợp lệ; GET query | Không vượt quyền qua query; semantics bất thường giữ mở; AC-20 đến AC-23 | P1; R-06 |
| UR-04 | Là Reader, tôi muốn chỉ đọc nội dung đã công khai và chuyên mục | Có published/draft fixture; GET list/detail và categories | Draft không lộ, quyền cấp đúng; AC-14,15 | P0; R-01 |
| UR-05 | Là người quản lý nội dung, tôi muốn ghi chú nội bộ không bị lộ cho Reader | Có published article với internal_notes; Reader đọc và thử projection | Từ chối hoặc loại field kín; kiểm tra không lộ dữ liệu; AC-08,16 | P0; R-01 |
| UR-06 | Là người quản lý dữ liệu, tôi muốn chặn thao tác ghi không được cấp quyền | Reader/anonymous, bản ghi tồn tại và payload còn lại hợp lệ | Không create/update/delete trái quyền; dữ liệu không đổi; AC-17,18,24 | P0; R-02 |
| UR-07 | Là Editor, tôi muốn dữ liệu tuân thủ cấu trúc/ràng buộc đã cấu hình | Actor hợp lệ, thử dữ liệu hợp lệ và không hợp lệ theo từng BR | Phân biệt null/missing/empty/coercion; AC-02 đến AC-09,24 | P1; R-05 |
| UR-08 | Là người quản lý hệ thống, tôi muốn token không hợp lệ không cấp quyền truy cập | API đáp ứng, token cố ý sai; GET users/me | Bị từ chối với phản hồi thích hợp; không tính 5xx là từ chối đúng; AC-19 | P0; R-02 |
| UR-09 | Là QA, tôi muốn phát hiện khác biệt API/OpenAPI và lỗi xử lý input | Schema theo actor, request/chuỗi có provenance, checks rõ ràng | Báo finding, phân loại và giữ reproducer; AC-25,26 | P0; R-07,R-08 |
| UR-10 | Là người chạy lại lab, tôi muốn kết quả kiểm thử có thể đối chiếu và tái lập | Cấu hình/dependency/fixture phù hợp, dữ liệu cô lập | Không giấu lỗi setup/restore, không lộ secret, nêu incomplete; TR-01 đến TR-06 | P0; R-09,R-10 |

Nguồn UR-01 đến UR-08: SRC-01 đến SRC-05; UR-09/10 là mục tiêu QA của lab từ SRC-01/05/06 và tài liệu tái lập, không phải chức năng mới bổ sung vào Directus.

## 5. Danh mục quy tắc hệ thống

Các BR là mục tiêu/điều kiện để so sánh kết quả, không phải tuyên bố tất cả đã được test đạt. Câu hỏi OPEN ở mục 7 giới hạn phần được khẳng định.

| ID | Quy tắc baseline và expected cốt lõi | Nguồn | UR | AC |
|---|---|---|---|---|
| BR-01 | Hai collection có ID integer non-null auto increment; tạo object hợp lệ trả ID dùng được để đọc lại | SRC-02 ensure_primary_id; SRC-05 positive-operations | UR-01,02 | AC-01 |
| BR-02 | Category.name phải đáp ứng non-null/string/max 80; luồng tạo chuẩn gửi name; không tự quy định empty/blank | SRC-02 ensure_schema; SRC-06 required name | UR-02,07 | AC-02 |
| BR-03 | Article.title phải đáp ứng non-null/string/max 120; luồng tạo chuẩn gửi title | SRC-02 ensure_schema; SRC-06 required title | UR-01,07 | AC-03 |
| BR-04 | Article.status thuộc draft/published, non-null; default được cấu hình là draft, cần kiểm chứng khi POST bỏ status | SRC-02 status_validation/default_value | UR-01,07 | AC-04 |
| BR-05 | Article.score là integer non-null trong 0-5; luồng tạo chuẩn gửi score; coercion chưa quyết định | SRC-02 score_validation; SRC-06 required score | UR-01,07 | AC-05 |
| BR-06 | Article.published_at cho phép null hoặc timestamp hợp lệ theo contract baseline cần xác minh | SRC-02 timestamp nullable; SRC-06 format timestamp | UR-01,07 | AC-06 |
| BR-07 | Article.metadata lưu JSON hoặc null, không thêm yêu cầu object/key riêng | SRC-02 JSON nullable | UR-01,07 | AC-07 |
| BR-08 | Article.internal_notes nullable; Editor được đọc/ghi field trong collection lab, Reader chịu BR-16 | SRC-02 text nullable; SRC-03 fields * / allowlist Reader | UR-01,05 | AC-08 |
| BR-09 | Category reference có thể null hoặc trỏ category tồn tại; invalid reference không được tạo dữ liệu mồ côi | SRC-02 ensure_relation; SRC-01 fixture | UR-01,02,07 | AC-09 |
| BR-10 | Xóa category đang được tham chiếu giữ article và đặt category=null | SRC-02 on_delete SET NULL; SRC-05 relation-nullification | UR-02 | AC-10 |
| BR-11 | Editor có positive acceptance cho đủ 10 operation trên hai collection với dữ liệu hợp lệ | SRC-03 CRUD fields *; SRC-05 positive-operations | UR-01,02 | AC-11 |
| BR-12 | PATCH chỉ đổi field được gửi; field nghiệp vụ khác không bị mất/đổi ngoài đặc tả | SRC-01 invariant; SRC-05 editor-crud/positive-operations; SRC-08 update payload/SQL | UR-01 | AC-12 |
| BR-13 | Sau DELETE thành công, bản ghi không được trả lại như một tài nguyên còn tồn tại | SRC-01 invariant; SRC-05 CRUD/read-back | UR-01,02 | AC-13 |
| BR-14 | Reader đọc được categories qua API, không bị giả lập bằng Admin | SRC-03 Reader categories read | UR-04 | AC-14 |
| BR-15 | Reader chỉ đọc được article published; draft không được lộ qua list/detail | SRC-03 permissions status=published; SRC-01 | UR-04 | AC-15 |
| BR-16 | Reader không nhận internal_notes, kể cả yêu cầu projection field này | SRC-03 article_fields không có internal_notes; SRC-01 | UR-05 | AC-16 |
| BR-17 | Reader không được create/update/delete hai collection; bài thử bị cấm phải gửi input còn lại hợp lệ | SRC-03 không cấp create/delete, update fields=[] cho article; SRC-01 | UR-06 | AC-17 |
| BR-18 | Anonymous không truy cập dữ liệu hai collection; đọc và ghi đều cần kiểm tra theo operation có chủ đích | SRC-01 policy; SRC-05 anonymous-denied mới chỉ kiểm GET | UR-06 | AC-18 |
| BR-19 | Token không hợp lệ không được xác thực thành actor có quyền trên endpoint kiểm tra | SRC-05 auth-invalid-token; SRC-01 luồng xác thực | UR-08 | AC-19 |
| BR-20 | Filter status hợp lệ trả đúng tập fixture theo status và quyền actor | SRC-01 query; SRC-04 fixture; SRC-05/S2 | UR-03 | AC-20 |
| BR-21 | Sort có khóa phụ ID và limit/offset/page phải trả đúng thứ tự/lát cắt theo oracle đã định nghĩa | SRC-01 query; SRC-05 query-fixture/S3 | UR-03 | AC-21 |
| BR-22 | Fields projection hợp lệ trả trường được yêu cầu/cho phép; không lộ field cấm hoặc field ngoài projection đã đặc tả | SRC-01 query; SRC-03 policy; SRC-05 query-fixture | UR-03,05 | AC-22 |
| BR-23 | Search với term đã biết trả đúng tập phù hợp trên các field searchable được phép; không chỉ title và không suy mọi semantics ngôn ngữ/diacritics | SRC-04 fixture; SRC-05 query-fixture; SRC-08 search.ts | UR-03 | AC-23 |
| BR-24 | Request ghi bị từ chối không tạo row hoặc thay đổi dữ liệu nghiệp vụ mục tiêu | SRC-01 invariant; SRC-05 invalid-field-rejection/reader-write | UR-01,06,07 | AC-24 |
| BR-25 | Probe robustness không làm API trả 5xx; control aggregate hợp lệ vẫn thành công khi precondition đạt | SRC-05 aggregate-query-robustness; SRC-06 check not_a_server_error | UR-09 | AC-25 |
| BR-26 | Response được đối chiếu status/content type/schema đã xuất đúng actor; khác biệt phải được ghi và triage, không đổi schema gốc để PASS | SRC-06 checks; SRC-05 contract-schema-candidates; SRC-01 quy tắc K05 | UR-09 | AC-26 |

## 6. Tiêu chí chấp nhận

Mỗi AC quy định tiền đề, hành động và kết quả mong đợi. Với negative test, yêu cầu có HTTP response, xác minh nguyên nhân phù hợp; network error/5xx không được tính là PASS nghiệp vụ. Mã 4xx cụ thể chỉ đặt khi có nguồn; response contract được đánh giá riêng theo BR-26.

| ID | Given - tiền đề | When - hành động/input | Then - expected và hậu điều kiện |
|---|---|---|---|
| AC-01 | Editor hợp lệ; object mới có field chuẩn, không tự chỉ định ID | POST từng collection rồi GET bằng ID trả về | 2xx, ID integer dương, đọc lại đúng bản ghi; ID không hard-code và không cần liên tục |
| AC-02 | Category payload còn lại hợp lệ | Gửi name chuẩn; thử null/thiếu/độ dài 79,80,81 theo kế hoạch test | Ca chuẩn và biên 80 được nhận; null/quá 80 bị từ chối không tạo row. Missing POST cần kiểm tra theo required contract; empty/blank/Unicode theo Q-01 |
| AC-03 | Article có score/status/category hợp lệ | Tạo title chuẩn; thử null/thiếu/119,120,121 | Ca chuẩn/120 được nhận, null/quá 120 bị từ chối không tạo row; missing theo required contract, không gộp với empty/blank |
| AC-04 | Article có title/score hợp lệ | POST draft/published/archived; POST bỏ status; PATCH không gửi status | Enum hợp lệ được lưu; archived bị từ chối; missing POST kỳ vọng default draft theo cấu hình nhưng chưa có evidence; PATCH bỏ status giữ giá trị cũ. Null/empty không phải missing |
| AC-05 | Các field còn lại hợp lệ | Gửi score -1,0,1,4,5,6; thiếu/null; thử kiểu khác ở nhóm OPEN | Miền integer 0-5 được nhận, ngoài miền/null bị từ chối không tạo row; omission theo required contract; không tự kết luận string/float được nhận là bug trước Q-02 |
| AC-06 | Editor và payload chuẩn | Gửi published_at=null hoặc timestamp hợp lệ đã chọn; thử format lỗi riêng | Ca null/chuẩn đọc lại đúng ý nghĩa thời điểm; format/timezone/precision và lỗi cụ thể theo Q-04. Không đòi raw string byte-equal khi chưa có quy tắc chuẩn hóa |
| AC-07 | Editor, payload chuẩn | Gửi metadata=null hoặc JSON có Unicode; GET lại metadata | Giá trị null/JSON giữ nguyên ý nghĩa; không bắt field tự phát sinh key fixture. Các kiểu JSON scalar/array có case riêng theo Q-05 |
| AC-08 | Editor, article hợp lệ | Ghi/đọc internal_notes hoặc null qua projection phù hợp | Lưu/đọc đúng nội dung; không dùng kết quả Editor để thay kiểm tra Reader |
| AC-09 | Có category chuẩn và một ID không tồn tại đã xác minh | Tạo/PATCH article với ID tồn tại, null, invalid ID | Liên kết hợp lệ/null đọc lại đúng; ID sai bị từ chối và không để quan hệ mồ côi. Nested object ngoài luồng chuẩn giữ Q-05 |
| AC-10 | Article đang tham chiếu category tạm | Editor xóa category, đọc lại article | Article còn tồn tại, category=null; các field article khác giữ nguyên; cleanup có kết quả |
| AC-11 | Editor, fixture và quyền đúng | Thực hiện GET list/POST/GET detail/PATCH detail/DELETE detail cho mỗi collection | Có ít nhất một positive hợp lệ cho từng operation, read-back đúng; gửi request tới operation không đủ để đạt |
| AC-12 | Biết dữ liệu article trước PATCH | PATCH một field được phép rồi GET toàn bộ field nghiệp vụ cần so | Field đó đổi đúng; những field không gửi giữ nguyên; không áp default/reset ngoài đặc tả |
| AC-13 | Editor vừa xóa bản ghi tạm thành công | GET lại cùng ID và kiểm tra dữ liệu còn tồn tại nếu cần | Không trả bản ghi còn tồn tại; response 5xx/network error không chứng minh đã xóa; không áp status 404 mặc định |
| AC-14 | Reader, categories fixture tồn tại | GET list và detail category với fields hợp lệ | 2xx và đúng fixture/field trong phạm vi quyền; không suy từ schema hoặc test Editor |
| AC-15 | Có published/draft đã biết từ fixture | Reader GET list không filter; thử filter draft; GET draft detail chỉ với field công khai; GET published detail | Đúng tập published theo từng query; không lộ draft; published đọc được. Dùng field công khai để tách nguyên nhân từ chối draft |
| AC-16 | Reader đọc được published bằng field công khai; ghi chú private có giá trị đã biết | Yêu cầu internal_notes trên list/detail trong phạm vi thiết kế | Từ chối theo semantics hợp lệ hoặc field bị loại; không lộ key/value private. Nested/wildcard cần thiết kế riêng, chưa có bằng chứng đủ |
| AC-17 | Reader; payload còn lại hợp lệ, target tồn tại | Thử POST/PATCH/DELETE có chủ đích trên hai collection | Bị từ chối vì quyền, không tạo/sửa/xóa dữ liệu; thử ghi có giá trị mới để tránh no-op |
| AC-18 | Không có bearer token; cùng fixture | Thử GET list/detail và các thao tác ghi trong phạm vi hai collection | Không đọc được dữ liệu lab, không ghi được; phân biệt permission rejection với lỗi setup/ID/schema |
| AC-19 | API hoạt động, positive auth precondition đã biết | GET users/me với token cố ý sai | Không được xác thực/truy cập thành công; lỗi hợp lệ, không 5xx. Không mở rộng thành tuyên bố đã test hết cơ chế login/token |
| AC-20 | Biết expected ID/status từ seed/map và quyền actor | GET filter status trên bộ dữ liệu đã cố định | Đúng tập ID, không sót/thừa, status đúng; expected không lấy từ chính kết quả filter |
| AC-21 | Có fixture giá trị/thứ tự chuẩn, quy tắc collation xác định | GET sort title,id; hai offset; page=2 với limit=3 | Đúng thứ tự và lát cắt, page=2 tương ứng offset=3; không chỉ so hai kết quả cùng sai |
| AC-22 | Actor và danh sách field cho phép | GET fields projection hợp lệ rồi kiểm field cấm riêng | Có đủ field được yêu cầu theo đặc tả và không có field ngoài projection/cấm; không chỉ kiểm tra số row |
| AC-23 | Fixture xác định term spéciale, searchable fields/quyền và expected ID độc lập | GET search=spéciale với projection/sort hợp lệ | Đúng tập phù hợp trên field được phép tìm, không giới hạn theo projection/title; case không match/Unicode khác là thiết kế bổ sung, semantics còn mở ở Q-07 |
| AC-24 | Có dữ liệu trước request hoặc truy vấn xác định row mới | Gửi một request ghi chắc chắn vi phạm quyền hoặc một BR dữ liệu | Bị từ chối đúng nguyên nhân, không có row mới/thay đổi field nghiệp vụ; không chấp nhận 5xx như oracle đúng |
| AC-25 | Editor, endpoint hoạt động, schema/budget đã chốt | Probe aggregate với fields rỗng và foo:1; hai control rỗng/count | Có HTTP response, probe không 5xx, control 2xx; response khác expected giữ FAIL/candidate để triage |
| AC-26 | Schema gốc theo actor và operation đã chọn | Chạy contract checks, kiểm status/content/body, probe object/array/export khi thuộc input schema | Báo mismatch có source/hash/request; contract FAIL không tự thành product defect, runtime 2xx không tự làm contract PASS |

Các dữ liệu biên trong AC là điều kiện **cần thiết kế/chạy ở Phase 3-4**, không phải test case mới đã được triển khai. Tình trạng hiện hữu nằm trong ma trận truy vết, không suy từ việc AC đã viết.

### 6.1. Yêu cầu kỹ thuật cho bộ kiểm thử

| ID | Yêu cầu kế thừa | Nguồn và tiêu chí kiểm chứng | Trạng thái Phase 1 |
|---|---|---|---|
| TR-01 | Chỉ gọi lab cô lập, actor đúng, ID từ response/map; không dùng DB dự án khác | SRC-01, lab.sh, fixture map; preflight/metadata, testcase dùng ID động | Có code/evidence lịch sử; không xác minh runtime mới |
| TR-02 | Pin baseline, lưu run ID/working tree/schema/actor/seed/budget; raw bất biến, overlay có nguồn | SRC-01/06/07; đối chiếu manifest/report/hash | Có artifact; thiếu exact working-tree hash lịch sử đã ghi ở Phase 0 |
| TR-03 | Suite ghi dữ liệu chạy tuần tự; snapshot/restore; restore/setup fail không tiếp tục mutation | SRC-01 và campaign guard; report/restore status | Có lịch sử và code; kiểm chứng bổ sung ở Phase 4/8 |
| TR-04 | Reproducer có precondition và chuỗi phụ thuộc khi cần; phân biệt request cuối/full-chain | SRC-01/05 và replay; parent map/report | Có replay, còn limitation; chưa tuyên bố mọi case full-chain |
| TR-05 | Secret ở cấu hình riêng, không đưa vào report/gói bàn giao; không bypass license | SRC-01, lab.sh, Phase 0 | Quy tắc giữ nguyên; không đọc secret để biên soạn |
| TR-06 | README/dependency/evidence đủ để người khác chạy lại, lưu failure/incomplete thật | SRC-01/07, README; kiểm tra dựng mới ở Phase 9 | Helper ngoài repo và live runtime còn hạn chế |

TR là yêu cầu harness/bàn giao, không phải chức năng nghiệp vụ Directus. CI và thí nghiệm chi phí là đề xuất ở phase sau, không được ghi thành tính năng đã có.

## 7. Những điểm OPEN và điều đã xác định được

**Cập nhật sau lựa chọn của người dùng:** Hướng bám baseline đã chốt. [Đối chiếu source P1-05](01-doi-chieu-baseline-p1-05.md) bổ sung phần có căn cứ cho cả bảy nhóm dưới đây: phân biệt required create/update, nhánh xử lý/error và search nhiều field. Các câu hỏi không bị đóng toàn bộ chỉ vì có lựa chọn baseline; phần còn OPEN là kỹ thuật cần đối chiếu thêm, không mặc định yêu cầu nhóm đặt quy tắc mới.

| ID | Điểm chưa đủ căn cứ để chốt | Phần đã xác định được từ nguồn | Liên quan | Cách giải quyết tiếp |
|---|---|---|---|---|
| Q-01 | Empty/blank/trim/đếm độ dài Unicode của name/title | Non-null, max 80/120; OpenAPI thiếu maxLength; meta.required không tự đồng nghĩa minLength=1 | D00-01; BR-02,03 | Review đúng baseline/nhu cầu lab, ghi quyết định; thiết kế input riêng, không thay schema gốc |
| Q-02 | Coercion score/name, string/float/bool; trường thừa trong payload | Kiểu cấu hình và miền score đã rõ, schema không chứng minh API có ép kiểu hay không | D00-02; BR-02,05 | Đối chiếu contract và implementation đúng bản; probe riêng khi được triển khai; không tự biến accepted-negative thành product defect |
| Q-03 | Hành vi API chính xác với missing/null/empty/default ở mỗi operation | POST schema required name hoặc title/score; status default draft ở cấu hình; PATCH giữ field bỏ qua theo BR-12 | D00-03,05; BR-02 đến BR-05,12 | Tách từng trường hợp; required của schema dùng chung PATCH phải review ở Phase 2; expected cụ thể chưa có nguồn vẫn OPEN |
| Q-04 | Tập timestamp hợp lệ, timezone, precision/chuẩn hóa và mã lỗi format sai | Nullable timestamp; schema format timestamp; không có BR published kéo theo published_at | D00-04; BR-06 | Kiểm công cụ pin hỗ trợ format thế nào; chọn oracle thời điểm có nguồn; không so raw string tùy tiện |
| Q-05 | JSON scalar/array, nested category payload và giới hạn array POST | Metadata là JSON nullable; OpenAPI có nested relation và object/array POST | BR-07,09,26 | Ghi phạm vi generator ở Phase 2 và case cần thiết; không suy object-only từ seed |
| Q-06 | Status/error contract cụ thể cho forbidden/not-found/validation/query sai | Mục tiêu không lộ/không đổi dữ liệu đã rõ; artifact có 400/403/204/500 nhưng không tự làm chuẩn | D00-04,05; BR-13,15-19,24-26 | Đối chiếu nguồn đúng baseline, giữ business và contract oracle riêng |
| Q-07 | Collation/sort, exact case/diacritic/wildcard semantics cho dữ liệu ngoài mẫu | Source pin cho thấy search nhiều searchable field theo quyền và LOWER LIKE; oracle hiện hữu vẫn phụ thuộc một phần API | BR-20-23 | Gắn expected với giá trị seed, searchable fields và collation cụ thể; không suy title-only hoặc accent-insensitive |

Đây là backlog chi tiết của các câu hỏi D00 liên quan, không đóng D00-01 đến D00-05 chỉ vì đã có tài liệu. Việc liệt kê OPEN không cản dùng các AC cốt lõi có nguồn; không được đánh dấu trường hợp OPEN là đã PASS hoặc đã xác nhận bug.

## 8. Rủi ro và ưu tiên

Thang điểm đề xuất: ảnh hưởng I=1 nhỏ, 2 sai chức năng/phân tích, 3 mất dữ liệu/lộ quyền hoặc bằng chứng không đáng tin; mức phơi nhiễm L=1 ít đường vào, 2 có nhiều điều kiện/đường vào, 3 hiện có finding hoặc phụ thuộc rộng. L là nhận định định tính, không phải xác suất hay tần suất lỗi đo được.

Điểm I×L: 6-9 cao/P0, 3-4 vừa/P1, 1-2 thấp/P2. Ưu tiên là thứ tự kiểm thử/điều tra, không đồng nghĩa product defect severity.

| ID | Rủi ro | I | L | Điểm/mức | Căn cứ và hướng kiểm soát |
|---|---|---:|---:|---|---|
| R-01 | Reader thấy draft hoặc ghi chú nội bộ | 3 | 2 | 6/P0 | Policy row/field; S4/S5/INV-10/smoke đã có mẫu nhưng còn đường chưa phủ |
| R-02 | Ghi trái quyền/token sai hoặc anonymous được truy cập | 3 | 2 | 6/P0 | S6/INV-01/02/11 chỉ phủ một số operation; cần ma trận quyền rộng hơn |
| R-03 | PATCH mất field hoặc từ chối nhưng vẫn đổi dữ liệu | 3 | 2 | 6/P0 | Invariant hiện so subset field; cần read-back đầy đủ hơn |
| R-04 | Xóa category làm mất article/sai quan hệ | 3 | 2 | 6/P0 | SET NULL có mẫu PASS, cần kiểm field article còn lại và invalid relation |
| R-05 | Input sai/default không rõ dẫn đến dữ liệu không hợp lệ | 2 | 2 | 4/P1 | Thiếu bộ biên; schema thiếu miền giá trị; thiếu source cho coercion |
| R-06 | Query trả sai tập/thứ tự/projection nhưng test vẫn PASS | 2 | 2 | 4/P1 | Expected query hiện phụ thuộc một phần API; bổ sung ground truth từ seed |
| R-07 | Input bất thường gây 5xx hoặc negative oracle nhận nhầm 5xx là đúng | 3 | 3 | 9/P0 | Aggregate 500 hiện có; một số assertion non-2xx quá rộng |
| R-08 | Schema thiếu/sai sinh nhiều false positive hoặc bỏ sót ràng buộc | 2 | 3 | 6/P0 | Các contract candidate và maxLength/enum/min/max chưa có |
| R-09 | Không tái lập/khôi phục đúng hoặc trộn run khác baseline | 3 | 2 | 6/P0 | Dirty tree, source SHA khác, helper ngoài repo, campaign incomplete |
| R-10 | Lộ credential hoặc dùng sai môi trường khi bàn giao/chạy lại | 3 | 2 | 6/P0 | Raw artifact/secret riêng, cần preflight và rà soát gói bàn giao |

Mọi BR/UR ưu tiên cao có test hoặc gap task trong [truy vết nghiệp vụ](01-truy-vet-nghiep-vu.md) và [bản CSV](01-traceability.csv). Đây là độ đầy đủ của kế hoạch truy vết, chưa phải coverage thực thi 100%.

## 9. Oracle và cách dùng bằng chứng

Ba lớp oracle không thay thế nhau:

1. **Business/authorization:** căn cứ BR, policy và fixture độc lập; ví dụ không có draft/private field và request bị cấm không đổi dữ liệu.
2. **Contract:** căn cứ đúng snapshot OpenAPI theo actor; status/content/schema mismatch vẫn được lưu dù hành vi CRUD có thể hợp lý về nghiệp vụ.
3. **Harness/precondition:** đúng môi trường, token, fixture, setup/restore và provenance; thiếu điều kiện không được chuyển thành kết luận lỗi sản phẩm.

Các điểm cần ghi đúng khi đọc bằng chứng hiện tại:

- S1-S6 dùng scenario report `20261012T222311Z-1412`; INV-01 đến INV-11 dùng invariant report `20261012T185934Z-1453`; các mã INV là ánh xạ tài liệu, report dùng case_id dạng tên.
- Smoke `20261012T222250Z-1431` kiểm Reader list **không filter status** và xác nhận sáu row đều published; INV-10 có filter published rồi so set ID. Kết hợp hai bằng chứng mạnh hơn việc chỉ dùng INV-10, nhưng chưa phủ mọi query/ID.
- S4 yêu cầu cả internal_notes trên draft nên 403 bị nhiễu bởi field permission; cần ca chỉ field công khai để kiểm riêng row policy.
- INV-05 lấy giá trị title/status từ GET nền rồi tính expected, S3 lấy full sorted list làm chuẩn phân trang. Có kiểm tra độc lập một phần nhưng chưa phải oracle hoàn toàn từ seed.
- INV-09 cố ý sai score và status cùng lúc. Smoke có hai probe riêng cho score=-1/status=archived; không nói mọi biên và từng ràng buộc đều đã phủ.
- Một số assertion hiện chấp nhận non-2xx quá rộng, có thể cho PASS khi 5xx. Artifact lịch sử có 400/403 phù hợp ví dụ cụ thể; giữ kết quả gốc nhưng ghi hạn chế test, chưa nới/chỉnh assertion ở Phase 1.
- INV-03/04/11 và relation test đọc lại subset field. Không dùng chúng để tuyên bố toàn bộ row/bảng không đổi khi chưa có so sánh tương ứng.

## 10. Điều kiện đầu vào/đầu ra và bàn giao phase tiếp theo

Đặc tả có thể dùng để bắt đầu Phase 2-3 khi:

- Mọi UR/BR có nguồn, AC và test hoặc gap task; phần OPEN được đánh dấu rõ.
- Không cần tự sửa schema gốc hoặc baseline để làm tài liệu nhất quán.
- Người thiết kế test biết ràng buộc nào có trong config/schema, oracle nào cần củng cố và evidence nào chỉ là lịch sử.

Phase 1 không phê duyệt các câu hỏi OPEN, không tuyên bố đã có review của con người, không nghiệm thu hệ thống hay các phase sau. Checklist review thực tế và các đầu việc bổ sung nằm tại [01-review-dac-ta.md](01-review-dac-ta.md).

Lựa chọn phương pháp bám baseline đã được người dùng xác nhận. P1-05 hoàn thành ở mức đặc tả; các câu hỏi cần thêm bằng chứng kỹ thuật vẫn OPEN và chuyển sang [Phase 2–4](02-danh-gia-openapi-va-sinh-test.md). Không đổi các kết quả FAIL hoặc đánh dấu case OPEN thành PASS sau lựa chọn này.
