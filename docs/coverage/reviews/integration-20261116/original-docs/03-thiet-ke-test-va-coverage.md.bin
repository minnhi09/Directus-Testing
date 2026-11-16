# Phase 3 — Thiết kế bộ test có chủ đích và tiêu chí kết thúc

**Phạm vi hiện hành sau thu gọn 19/10:** trình bày 13 ca/kịch bản đại diện tại E.3 của [báo cáo cuối kỳ](09-bao-cao-cuoi-ky.md). Danh mục và ma trận bên dưới là thiết kế mở rộng để tra cứu; không cần chạy hết hoặc hoàn thành mọi điểm mở để nộp môn học.

**Ngày:** 18/10/2026. **Phiên bản thiết kế:** `P3-v1`. **Phạm vi hoàn thành:** thiết kế và review tĩnh, chưa triển khai automation hoặc gửi request mới. Thực hiện bởi AI trong phiên này; không gán review cho thành viên.

Bộ thiết kế nối [đặc tả v0.2](01-yeu-cau-va-dac-ta.md) → [khoảng trống OpenAPI](02-ma-tran-rang-buoc.md) → input có chủ đích → oracle → tiêu chí dừng. Giữ baseline Directus `12.5.0`, source commit `4f77933bf9551cac6b289576078783e189b8f4e3`, Schemathesis `4.30.0`, PostgreSQL `16` và 10 operation chính. Không sửa schema, policy, harness hoặc budget thực thi.

## 1. Đọc đầu ra theo thứ tự

| Tệp | Nội dung |
|---|---|
| [Báo cáo này](03-thiet-ke-test-va-coverage.md) | Quy ước dữ liệu/oracle, phân vùng, biên, quyền, chuỗi và mô hình pairwise |
| [Danh mục case](03-test-case-catalog.md) / [CSV đầy đủ](03-test-case-catalog.csv) | Từng case có ID, actor, input, expected, trạng thái expected, tiền điều kiện, cleanup và nơi tích hợp |
| [Tiêu chí kết thúc](03-tieu-chi-ket-thuc.md) | Entry gate, pass/fail, mẫu số coverage, budget, incomplete và đủ bằng chứng |
| [Review thiết kế](03-review-thiet-ke.md) | Checklist P3-09, hạn chế được phát hiện và bàn giao Phase 4 |
| [Truy vết](03-traceability.csv) | Đủ 26 BR → test hiện hữu → case mới thiết kế; không thay trạng thái evidence cũ |
| [Inventory test hiện có](03-inventory-test-hien-co.csv) | S1–S6, INV-01…11 và ba mục smoke; nhóm trùng mục tiêu và cách tái sử dụng |
| [Phân vùng](03-phan-vung-tuong-duong.csv) / [Biên](03-gia-tri-bien.csv) | 48 lớp dữ liệu và 34 điểm biên theo operation |
| [Bảng quyền](03-bang-quyet-dinh-quyen.csv) | 69 luật khả thi, mỗi luật gắn case cụ thể |
| [36 query tham chiếu](03-query-exhaustive-36.csv) / [9 query pairwise](03-query-pairwise.csv) | Tập con trỏ lại cùng case ID; không tạo thêm chín case trùng |

Chi tiết máy đọc được nằm trong [thư mục hỗ trợ Phase 3](tai-lieu-bo-tro/phase3-20261018/), đặc biệt [catalog JSON](tai-lieu-bo-tro/phase3-20261018/test-case-catalog.json), [fixture oracle](tai-lieu-bo-tro/phase3-20261018/fixture-oracle.json), [oracle library](tai-lieu-bo-tro/phase3-20261018/oracle-library.json) và [design summary](tai-lieu-bo-tro/phase3-20261018/design-summary.json).

## 2. Số lượng và ý nghĩa

Có **257 dòng case thiết kế**: 221 ca có chủ đích ngoài thí nghiệm pairwise và 36 ca query tham chiếu. Chín ca pairwise là tập con của 36, không cộng thành 266. Đây là danh mục mở rộng theo các giá trị đầu vào cụ thể, không phải 257 case đã chạy, số HTTP request hay số ca giảng viên bắt buộc.

| Nhóm | Số case thiết kế |
|---|---:|
| name/title | 18 + 18 |
| score/status | 22 + 14 |
| published_at/metadata/internal_notes/category | 12 + 12 + 4 + 10 |
| Positive acceptance 10 operation | 10 |
| Biến thể quyền ngoài 10 ca positive được tái dùng | 59 |
| Token valid control/invalid | 2 |
| Query chức năng/query biên | 16 + 10 |
| Chuỗi dữ liệu/quan hệ | 3 |
| Aggregate robustness/control | 3 |
| Contract POST object/array, export và projection | 8 |
| Query tham chiếu hữu hạn | 36 |

Hai chiều trạng thái được tách riêng:

| Độ rõ expected | Toàn danh mục | Ngoài pairwise | Cách sử dụng |
|---|---:|---:|---|
| ASSERTABLE | 142 | 118 | Có expected cốt lõi từ đặc tả/source; vẫn phải đạt precondition trước chạy |
| CONDITIONAL | 68 | 56 | Có expected có điều kiện: cần chứng minh DB/default, collation hoặc nhánh error cụ thể |
| OPEN | 47 | 47 | Chưa đặt business verdict cứng; có thể kiểm robustness/toàn vẹn đã rõ và ghi observation riêng |

**Execution của tất cả case: NOT_RUN**, `run_id/actual_result/finding_id` để trống. CONDITIONAL không tự là BLOCKED ở thời điểm thiết kế; khi chạy thiếu điều kiện thì mới ghi BLOCKED. OPEN không được chuyển thành business PASS chỉ vì request được trả lời.

Có 106 case P0 và 151 case P1 trong toàn danh mục. Đây là ưu tiên thiết kế của nhóm để triển khai theo rủi ro, không xác suất lỗi hoặc cam kết chạy tất cả trong mỗi PR. Các ca biên score/status được ưu tiên P1 theo rủi ro validation; oracle bảo toàn dữ liệu vẫn phải áp dụng. Ca quyền/chuỗi/contract quan trọng được P0. Không chạy lặp một case chỉ vì nó xuất hiện ở nhiều BR hoặc nhiều luật quyền.

## 3. Kiểm kê, tái sử dụng và tránh trùng

Đã đối chiếu 20 mục hiện hữu: sáu scenario, 11 invariant và ba mục smoke. `positive-operations` chính là INV-04, không tính thêm thành invariant thứ 12.

| Mục tiêu trùng | Hiện có | Cách dùng khi triển khai Phase 4 |
|---|---|---|
| CRUD article | S1, INV-03, INV-04 | INV-04 làm backbone đủ 10 operation; S1 giữ demo ngắn; củng cố full field và post-delete oracle thay vì viết ba suite giống nhau |
| Reader PATCH bị cấm | S6, INV-11 | Giữ một assertion/read-back chuẩn để tái sử dụng; bổ sung POST/DELETE/category và cả draft/published |
| Category SET NULL | Smoke relation, INV-08 | Smoke vẫn là kiểm nhanh; P3-ST-03 là thiết kế chi tiết để mở rộng cùng nền tảng |
| Validation | Smoke có score=-1 riêng, archived riêng; INV-09 sai cả hai | Tái dùng probe riêng cho `P3-SCORE-POST-MINUS1` và `P3-STATUS-POST-ARCHIVED`; thêm biên/null/missing, không nói probe đôi đã kiểm độc lập từng rule |
| Query | S2/S3, INV-05 | Giữ mục tiêu; thay phần expected phụ thuộc GET nền bằng fixture spec; kiểm correctness ngoài consistency |
| Reader visibility | Smoke list không filter, S4/S5, INV-10 | Kết hợp count với exact ID set; draft detail chỉ public fields; private field thành bài thử riêng |
| Finding lịch sử | INV-06/07 và replay | Giữ FAIL/candidate gốc; control và reproducer đủ query; không đổi raw để PASS |

Mỗi case P3 là **mã thiết kế cho hành vi mong kiểm**, không tuyên bố harness hiện đã thực thi mã đó. Inventory CSV chỉ rõ mục hiện hữu và giới hạn; artifact lịch sử không được gán sang case mới mà chưa đối chiếu mức assertion.

## 4. Tiền điều kiện, dữ liệu và cleanup dùng chung

Mỗi case kế thừa các PC được ghi trong CSV/JSON. Đây là một phần bắt buộc của case, không phải lựa chọn tùy ý khi triển khai.

| Mã | Điều kiện cụ thể |
|---|---|
| PC-BASE | Đúng lab/project/network/volume; image/source/schema/fixture version; API healthy; credential actor đúng; Editor/Reader control đạt; không có suite ghi khác đồng thời. Không suy runtime healthy từ báo cáo ngày trước |
| PC-Q | Seed sạch 3 category/12 article; map mới khóa cùng run; đối chiếu đầy đủ field fixture với spec. Không có row probe/extra trước nhóm query/quyền đọc. Giá trị expected không lấy từ response của query target |
| PC-MUT | PATCH/DELETE tạo target tạm riêng bằng Editor; POST dùng chính request target để tạo row và theo dõi ID mới, không cần tạo một article thừa trước đó. Field nền hợp lệ/đúng template, target state đúng case; category reference từ map hoặc setup phụ thuộc. ID từ response/map; snapshot đủ field nghiệp vụ. Chỉ thay một input/ràng buộc chính; không mutate fixture đang dùng làm query oracle |
| PC-PERM | Editor control với cùng endpoint/ID/projection/payload hợp lệ; Reader có positive control public. Xác minh token đúng actor. Ghi thử phải đổi giá trị để tránh no-op; draft/published theo map/producer, không đoán từ ID |
| PC-CLEAN | So dữ liệu/absence **trước** cleanup; thu mọi ID mới kể cả khi request đáng lẽ bị từ chối. Xóa article trước category; xác minh cleanup hoặc restore đúng snapshot trong finally; cleanup/restore lỗi làm môi trường chưa sẵn sàng cho mutation tiếp |

Payload article chuẩn:

```json
{
  "title": "Probe ${probe_key}",
  "status": "draft",
  "score": 3,
  "published_at": null,
  "metadata": {"probe": "${probe_key}"},
  "internal_notes": "Private ${probe_key}",
  "category": "${fixture.category_alpha}"
}
```

Payload category chuẩn: `{"name":"Probe ${probe_key}"}`. `probe_key` là 24 ký tự hex đầu của SHA-256 từ run ID và case ID, có delimiter xác định; adapter kiểm không trùng trong run. Không nối nguyên run ID/case ID dài làm payload mặc định vượt max80/120. Report vẫn lưu đủ hai ID gốc để truy vết.

Placeholder trong tài liệu là biểu thức template, **không phải body cuối gửi API**. Request có body dùng JSON và token từ helper theo actor; Anonymous bỏ Authorization. Adapter phải resolve category/target/changed_score thành integer JSON, không string hoặc object `$fixture`. `target_id` do case setup hoặc map ràng buộc đúng collection/state; `changed_score` là integer trong 0–5 khác giá trị đã biết trước.

Ca biên title/name dùng đúng chuỗi ASCII chiều dài đã ghi, không nối run ID làm vượt biên. Name không có metadata marker: với POST bị từ chối, so set ID trước/sau trong phiên độc quyền để phát hiện row thừa. Article có thể thêm marker metadata đã nằm trong payload chuẩn. Không chỉ GET marker rồi kết luận không side effect nếu marker có thể bị loại.

`${absent_category_id}`: chọn một integer dương còn trống trong miền ID sau khi kiểm map và Editor list đầy đủ; xác minh absence với control cùng điều kiện, không chỉ dựa 403 của một GET. Giữ độc quyền mutation từ lúc xác minh đến request. Không dùng ID cố định/UUID/ngẫu nhiên sai kiểu để giả lập FK không tồn tại.

Field so sánh article: `id,title,status,score,published_at,metadata,internal_notes,category`; category: `id,name`. JSON deep equality theo ngữ nghĩa, text không tự trim, timestamp so instant khi đã có căn cứ. Không tuyên bố so toàn bộ DB hoặc audit/system tables từ snapshot tám field này.

Nếu request từ chối nhưng vẫn tạo/sửa dữ liệu, ghi FAIL trước khi dọn. Nếu mất response ID, lấy delta ID từ snapshot/list control để cleanup có giới hạn trong lab. Không reset giữa các bước chuỗi, không reseed giữa bước để tạo expected khớp.

## 5. Phân vùng tương đương — P3-02

Phân vùng theo **hành vi có nguồn**, không chỉ kiểu JSON. Các lớp OPEN được để riêng khỏi valid/invalid; cùng chữ “required” không gộp omission/null/empty/blank.

| Đối tượng | Lớp đã rõ và đại diện | Lớp/điều kiện còn mở | Expected và case tiêu biểu |
|---|---|---|---|
| name/title | ASCII không rỗng trong max; quá max; explicit null; missing POST | Empty/blank/Unicode count/coercion; no-op PATCH category | Nhận/read-back ca hợp lệ; từ chối đúng rule và không đổi dữ liệu. `P3-TITLE-POST-120`, `P3-NAME-PATCH-81` |
| score | Integer 0–5; dưới 0; trên 5; null; missing create có điều kiện | Float 2.5, string "3", bool true | `P3-SCORE-POST-0`, `P3-SCORE-PATCH-6`; không quy accepted coercion thành defect trước Q-02 |
| status | draft và published đều có case; archived; null; empty; omission create/update tách riêng | Bool/coercion; default cần kiểm DB overview | `P3-STATUS-POST-DEFAULT`: conditional default=draft; `P3-STATUS-PATCH-OMITTED`: giữ published |
| published_at | Null; ISO UTC/offset với oracle instant có điều kiện | Empty, malformed, thiếu offset, tập format/precision | `P3-PUBLISHED_AT-POST-EMPTY` chỉ có oracle robustness đã rõ; không tự đặt status hoặc business verdict |
| metadata | Null và object Unicode/nested không có key nghiệp vụ bắt buộc | Array/scalar round-trip theo Q-05 | Không thu hẹp JSON thành object-only; ca OPEN vẫn không được trả 5xx hoặc âm thầm hỏng field khác |
| internal_notes | Null/text Unicode chứa khoảng trắng | Chính sách field Reader theo từng projection | Editor round-trip byte text có nghĩa; Reader oracle riêng |
| category | Existing ID, null, ID không tồn tại | Nested existing/create theo Q-05 | Valid/null round-trip; FK sai không orphan, không nhầm coercion/permission với FK |

Đủ 48 dòng lớp dữ liệu trong [CSV](03-phan-vung-tuong-duong.csv). Query còn được phân theo: filter không có/draft/published; sort numeric/title; phân trang hợp miền/ngoài miền/biên 0; search known hit/no hit/blank; projection public/private/wildcard/nested. Bảng quyền ở mục 7 mô hình hóa phân lớp actor/state/projection thay vì trộn với validation field.

Một negative test giữ mọi field khác hợp BR và dùng một target/control hợp lệ. Ví dụ `score=-1` phải giữ status=draft, title/category hợp lệ; `status=archived` phải giữ score=3. Không dùng một response lỗi cho hai field để tuyên bố cả hai rule đã được kiểm.

## 6. Giá trị biên — P3-03

| Miền | Điểm biên cụ thể | Áp dụng | Expected dữ liệu |
|---|---|---|---|
| score integer [0,5] | -1,0,1,4,5,6 | POST và PATCH, 12 instance | 0/1/4/5 nhận và persist; -1/6 từ chối, POST không thêm row/PATCH không đổi target |
| name max 80 | 79,80,81 ASCII | POST và PATCH, 6 instance | 79/80 giữ nguyên; 81 bị từ chối, không truncate |
| title max 120 | 119,120,121 ASCII | POST và PATCH, 6 instance | 119/120 giữ nguyên; 121 bị từ chối, không truncate |
| limit min -1 | -2,-1,0,1 | GET, 4 instance | -2 INVALID_QUERY; -1 đủ fixture; 0 rỗng; 1 đúng row đầu theo ID oracle |
| offset min 0 | -1,0,1 với limit=3 | GET, 3 instance | -1 INVALID_QUERY; 0/1 đúng lát cắt |
| page min 0 theo schema/validation | -1,0,1 với limit=3 | GET, 3 instance | -1 INVALID_QUERY; 1 trang đầu; page=0 giữ OPEN tới khi rõ semantics, không tự coi 0 sai |

Tổng **34 điểm biên theo operation**, không phải 34 HTTP request đã chạy. [CSV biên](03-gia-tri-bien.csv) gắn từng điểm với case ID. Null/missing/coercion không phải biên số và đã có ca phân vùng riêng.

Dùng ASCII làm biên độ dài để một ký tự = một code point = một byte; không cần đoán cách DB tính Unicode để chốt các ca này. Chuỗi `e + U+0301` được thiết kế riêng thành OPEN, không lấy số grapheme hiển thị làm maxLength. Mục tiêu ca 81/121 là từ chối đúng ràng buộc và không đổi dữ liệu; lỗi 5xx không trở thành PASS chỉ vì input quá dài.

## 7. Bảng quyết định quyền — P3-04

Miền hữu hạn có **69 luật** trong [CSV](03-bang-quyet-dinh-quyen.csv), mỗi luật dẫn tới một case. Mười luật Editor chuẩn dùng lại P3-OP-01…10; 59 biến thể còn lại có case P3-AUTHZ-DR-*. Không tạo suite trùng cho mười ô đã được kiểm bởi positive acceptance.

Điều kiện và các tổ hợp khả thi:

- Actor: Editor, Reader, Anonymous; Admin làm bootstrap/control, không fuzz mặc định.
- Collection article: GET list dùng mixed dataset; detail/PATCH/DELETE dùng từng draft/published; POST dùng payload draft/published, không giả một row tồn tại trước create.
- Article GET: public, explicit private, wildcard `*`, nested một cấp `category.id/category.name`. Category GET dùng id/name. Ghi dùng payload nghiệp vụ hợp lệ.
- Category không có status và internal_notes; không tạo luật category=draft hoặc category.internal_notes sai schema rồi gọi đó là permission test.

Mỗi actor có 23 luật: article 18 (list4 + detail8 + POST2 + PATCH2 + DELETE2), category5. Tổng 3×23=69.

| Điều kiện | Hành động mong đợi | Cách tránh PASS giả |
|---|---|---|
| Editor + input/quyền đúng | CRUD/read được, field có quyền đúng | Positive acceptance + read-back đầy đủ; không chỉ request được gửi |
| Reader + categories read | Đọc list/detail đúng fixture | Reader thật, không dùng response Admin thay kết quả |
| Reader + article list public | Exact set sáu published | Không filter status để tự che policy; filter draft là case riêng phải rỗng |
| Reader + published detail public | Đọc đúng ID/field | Published positive control trước denied test |
| Reader + draft detail public | Deny theo row policy | Không đưa field private vào bài thử này |
| Reader + explicit internal_notes | Không lộ field/value; semantics deny/redact cần nguồn theo projection | Case chưa rõ nhánh giữ OPEN, không dùng OR “403 hoặc bất kỳ 2xx” để PASS |
| Reader + draft detail + private | Bị từ chối, không lộ dữ liệu; `DENY_COMBINED` | Không gán 403 thành bằng chứng riêng row-policy hay field-policy; hai bài thử cô lập vẫn bắt buộc |
| Reader + wildcard/nested category | Không lộ notes/draft, dữ liệu public/nested đúng | Expected response success phải được chốt theo baseline; conditional không thành business PASS khi nhánh chưa rõ |
| Reader + mọi POST/PATCH/DELETE chính | Deny và không side effect | Payload khác no-op; target/state tồn tại; Editor so trước/sau đủ field |
| Anonymous + mọi phép đọc/ghi trong bảng | Deny, không trả dữ liệu lab/không ghi | Không có bearer token; Editor control loại ID/payload/endpoint sai |

`403/FORBIDDEN` là expected có điều kiện theo nhánh permission/readOne của pin, không mặc định từ thông lệ HTTP. Token invalid dùng oracle riêng; API error khác nhánh phải được điều tra hoặc BLOCKED khi chưa có căn cứ. 5xx/network/body lỗi không thể PASS quyền.

Không mở rộng sang reverse relation, GraphQL, bulk PATCH/DELETE, DAST hoặc bypass license. Schema Reader vắng operation vẫn cần request chủ đích; PATCH article xuất hiện trong schema cũng không cấp quyền ghi field.

## 8. Chuỗi nghiệp vụ — P3-05

| ID | Chuỗi chính đã thiết kế | Oracle và cleanup |
|---|---|---|
| P3-ST-01 | POST category → GET → PATCH name → GET → DELETE → GET denied/not returned → GET list absence | ID động; name đúng trước/sau; loại 5xx khỏi absence; 7 bước chính |
| P3-ST-02 | POST category → POST article → GET full → PATCH score → GET full → DELETE article → GET absence → DELETE category | Tám field article; chỉ score đổi; cleanup dependency theo thứ tự; 8 bước chính |
| P3-ST-03 | POST category → POST article → GET snapshot → DELETE category → GET article → DELETE article | Article còn, category=null; toàn field khác giữ; 6 bước chính vì thêm kiểm trước xóa |

Đây là chuỗi thiết kế đầy đủ hơn ví dụ hai bước đã thấy ở Phase 2; không sửa provenance của các transition cũ. Các số bước chưa tính mọi request control/absence/cleanup bổ sung của adapter.

Request ghi bị từ chối được kiểm trong mọi ca invalid/permission mutation bằng before/after hoặc delta ID. Expected state đến từ input setup đã biết và được kiểm precondition; không tự sao response sai của setup thành chuẩn. Nếu setup tạo sai dữ liệu, dừng target case với precondition failure.

Recorder phải có producer/consumer, expression ID, ID mới, case/parent, actor và từng verdict. Deterministic orchestrator có thể triển khai chuỗi này mà không cần giả rằng Schemathesis tự suy luận được mọi liên kết. Khi replay phải tái tạo producer và remap ID; không gửi request cuối rồi ghi full-chain.

## 9. Oracle độc lập — P3-06

[Fixture oracle](tai-lieu-bo-tro/phase3-20261018/fixture-oracle.json) được trích **tĩnh từ `article_spec/category_spec` của harness**, có source hash, đủ 12 bài/3 category và field nghiệp vụ. Tệp không chép ID 1…12 hiện tại làm expected cố định. Run mới bind fixture key → ID bằng map được lưu/hash cùng seed/export.

| Phép kiểm | Nguồn expected độc lập | Điều không dùng làm nguồn chuẩn |
|---|---|---|
| Filter published/draft | Status trong spec + map key/ID; Reader còn giao với policy | Response của chính filter đang thử |
| Sort ID | Numeric ID lấy từ map mới | GET sort=id rồi lấy thứ tự của nó làm expected |
| Sort -score,id | Score spec, ID map; tie bằng numeric ID | Score/thứ tự từ GET nền chưa kiểm đúng spec |
| Sort title,id | Thứ tự prefix Alpha/Beta/Gamma, 01…04 của seed và metadata collation đã xác minh | Python sort mọi Unicode rồi coi là PostgreSQL mọi cấu hình |
| Offset/page | Cắt danh sách oracle đã tính, rồi mới so API | Chỉ so hai page với một GET sorted có thể cùng sai |
| Projection | Danh sách field request đã chốt + policy, so đủ key và giá trị | Chỉ kiểm “không có extra”, bỏ qua field cần có |
| Search spéciale/no hit | Nội dung seed các field searchable được actor phép dùng; một key beta_published_2 cho term mẫu | Mặc định search chỉ title hoặc chỉ field trong projection |
| PATCH/rejection | Payload setup chuẩn/expected đã xác minh + snapshot đủ field để đối chiếu | Cho PASS vì response non-2xx hoặc vì field score vẫn bằng trước nhưng notes/metadata đã đổi |

GET nền được phép làm **precondition/control** để xác minh runtime khớp fixture spec, không tự sinh expected từ giá trị nó trả mà chưa so nguồn. Mô hình này độc lập với output chức năng target, nhưng vẫn dùng harness làm nguồn fixture; lỗi cùng tồn tại trong cấu hình seed và spec vẫn là giới hạn cần nêu, không gọi oracle là tuyệt đối độc lập toàn hệ thống.

Source error đúng pin bổ sung: [ValueTooLong](tai-lieu-bo-tro/phase3-20261018/baseline-source/packages/errors/src/errors/value-too-long.ts), [InvalidForeignKey](tai-lieu-bo-tro/phase3-20261018/baseline-source/packages/errors/src/errors/invalid-foreign-key.ts), [NotNullViolation](tai-lieu-bo-tro/phase3-20261018/baseline-source/packages/errors/src/errors/not-null-violation.ts), [InvalidPayload](tai-lieu-bo-tro/phase3-20261018/baseline-source/packages/errors/src/errors/invalid-payload.ts); [manifest](tai-lieu-bo-tro/phase3-20261018/baseline-source-manifest.json). Các class khai báo 400, nhưng phải chứng minh request đi đúng nhánh/translator; không dùng chúng để khẳng định mọi SQL error đều đã được ánh xạ. `_nnull/_submitted` thường đi FailedValidation của source Phase 1, không dùng NotNullViolation thay mọi lỗi null.

Oracle contract luôn chạy/ghi riêng với business, authorization, robustness và precondition. DELETE 204 hoặc object POST có thể business đúng nhưng raw contract FAIL; malformed timestamp có thể business OPEN nhưng robustness FAIL do 5xx. Một nhãn tổng PASS không được xóa các kết luận thành phần.

## 10. Mô hình pairwise nhỏ — P3-07

Giữ đúng mô hình dự kiến Phase 6: Editor, GET articles, fixture sạch và không mutation.

| Yếu tố | Giá trị |
|---|---|
| Filter | Không filter; draft; published |
| Sort | id; title,id; -score,id |
| Fields | id,title; id,title,status,score |
| Pagination | limit=3&offset=3; limit=3&page=2 |

Có **36** tổ hợp Cartesian. Pagination là một yếu tố gồm hai cách mã hóa tương đương, nên không sinh cùng lúc page+offset trong mô hình. Case precedence có cả hai nằm ngoài pairwise. Không có tổ hợp Cartesian nào khác bị loại. Mọi query phải hợp lệ trong fixture/policy và collation của mô hình; nếu điều kiện title chưa đạt thì thí nghiệm runtime BLOCKED, không xóa các dòng đó để tăng coverage.

Đã tạo tĩnh tập **9 dòng**, phủ **37/37 cặp giá trị khả thi** của sáu cặp yếu tố. [JSON coverage](tai-lieu-bo-tro/phase3-20261018/pairwise-model-and-coverage.json) liệt kê từng cặp và case phủ nó, danh sách thiếu rỗng. Không dùng PICT hoặc gán tên thuật toán Allpairs cho script chọn tĩnh này.

Chín là tối thiểu trong **mô hình không có constraints loại dòng này**: cặp filter×sort có chín tổ hợp, một dòng chỉ phủ một tổ hợp đó; tập đã dựng đạt đúng chín và còn phủ các cặp khác. Đây là chứng minh về cấu trúc input, không về khả năng tìm defect.

Giảm số ca thiết kế trong miền: `(36−9)/36=75%`. **Chưa đo giảm thời gian, công sức hoặc tỷ lệ phát hiện lỗi.** Chạy đối chứng Phase 6 cần thực thi cả 36 và 9 trên cùng fixture/oracle/config, giữ run/report riêng. Nếu hai lượt độc lập thì có 45 lần gửi target query trước lặp đo, chưa tính setup/control; không gọi đó là 45 input duy nhất.

Giữ riêng ngoài pairwise: token/quyền/row-field policy, null/missing/coercion, biên độ dài/số, relation SET NULL, rollback, query invalid và aggregate robustness. Pairwise không bảo đảm tương tác từ ba yếu tố trở lên; K05 schema testing/fuzzing vẫn là kỹ thuật chính của nhóm, không tự chuyển đề tài thành K06.

## 11. Nguồn kiến thức và điều kiện kết thúc phase thiết kế

Đã đối chiếu nội dung [bài giảng hộp đen](../slide_bai_giang/2-kiem-thu-hop-den-0.pdf): trang PDF 13–17 về phân vùng, 28–29 về biên, 33–35/45 về quyết định, 46/49–56/59 về pairwise và giữ ca rủi ro cao. Trang PDF là chỉ số tệp, không dựa số trang tổng ghi trên slide. [Yêu cầu môn học](../yeu_cau.pdf), trang PDF 8, mô tả K05 là sinh request từ schema, kiểm invariant/status, lưu reproducer và thống kê lỗi. Ngưỡng số ca/coverage/budget của nhóm ở hồ sơ này không được ghi thành nguyên văn yêu cầu giảng viên; không lấy tỷ lệ tiết kiệm trong slide làm số đo của dự án.

P3-01…09 hoàn thành ở phạm vi thiết kế: inventory/trùng, phân vùng, biên, 69 luật quyền, ba chuỗi, oracle có nguồn, mô hình pairwise, tiêu chí kết thúc trước chạy và review bởi AI. [Tiêu chí kết thúc](03-tieu-chi-ket-thuc.md) phân biệt nghiệm thu tài liệu với kết quả test/campaign; [review](03-review-thiet-ke.md) nêu phần bàn giao Phase 4.

Kiểm tra tĩnh đầu ra được ghi tại [validation.json](tai-lieu-bo-tro/phase3-20261018/validation.json). Không có request API, seed/export mới, test suite mới chạy, thay đổi raw/harness hoặc commit/push trong Phase 3 này.


**Điều hướng kết quả sau thiết kế:** [Phase 4](04-automation-va-tai-lap.md) đã tích hợp/chạy subset và lưu [bảng execution riêng](04-ket-qua-case.csv). Catalog P3-v1 ở tài liệu này giữ trạng thái thiết kế tại thời điểm lập; bốn request projection category có errata rõ trong bản automation.
