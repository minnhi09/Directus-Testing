# Kế hoạch hoàn thiện dự án R06 Directus + K05 theo từng phase

**Ngày lập:** 18/10/2026, theo múi giờ Asia/Bangkok.  
**Mục tiêu:** Hoàn thiện dự án theo yêu cầu môn Kiểm thử phần mềm, làm rõ cơ sở thiết kế test, hiệu quả kiểm thử và bằng chứng dùng khi bảo vệ.  
**Trạng thái:** Kế hoạch hiện hành; có kết quả Phase 0–4. Phase 5 rút gọn, Phase 7 loại khỏi phạm vi theo yêu cầu người dùng ngày 18/10/2026. Các phase còn lại chưa được coi là đã thực hiện.  
**Phạm vi tài liệu:** Không phân chia công việc cho từng thành viên. Việc tạo kế hoạch không bao gồm sửa code, chạy lab, campaign, commit, push hay triển khai CI.

## 1. Cách sử dụng kế hoạch

**Nơi tập hợp đầu ra:** Từ nay nội dung tạo khi thực hiện plan được lưu tại `DAMH/docs/HoanThanhPlan/`. Đọc [mục lục](README.md) để theo dõi từng phase; tài liệu nguồn và artifact kiểm thử gốc giữ ở vị trí ban đầu.

- Thực hiện theo thứ tự phụ thuộc của các phase; đánh dấu hoàn thành bằng đầu ra và bằng chứng thực tế.
- Kế thừa tài liệu, script, scenario, invariant và artifact đã có; chỉ bổ sung phần thiếu hoặc sửa phần có vấn đề.
- Các đường dẫn đầu ra mới trong dấu backtick là **tệp dự kiến**, chưa phải tệp đã tồn tại. Các liên kết Markdown dẫn tới tài liệu hiện có.
- Các mốc, số lượng và ngưỡng do kế hoạch này đề xuất phải được ghi nhận trước khi thực thi; không điều chỉnh sau khi nhìn kết quả chỉ để đạt tiêu chí.
- Ước lượng thời gian dưới đây là công sức tham khảo cho toàn dự án, không phải cam kết tiến độ hay phân công nhân sự.
- Khi phát hiện thiếu điều kiện ở phase trước, quay lại hoàn thiện đúng phần liên quan; không cần làm lại mọi bước đã có bằng chứng còn phù hợp.

### 1.1. Phân biệt nguồn yêu cầu

| Loại | Nội dung | Cách áp dụng |
|---|---|---|
| Bắt buộc theo đề bài | Phần 1, Phần 2; cấu trúc A-H; automation; log/metrics, phân tích kết quả; pin/tái lập; báo cáo và đánh giá đóng góp | Phải có đầu ra và dẫn chứng hoặc nêu rõ phần chưa đáp ứng |
| Hướng dẫn bổ sung của giảng viên, theo thông tin người dùng cung cấp | Đặc tả hệ thống, yêu cầu người dùng, sinh test từ đặc tả API Directus; tối ưu chi phí kiểm thử | Đưa vào chuỗi thiết kế test và phần đánh giá hiệu quả |
| Phạm vi và baseline nội bộ hiện có | Hai collection, bốn actor, 10 operation; raw/guided; ba seed và ngân sách đã chốt | Giữ ổn định; thay đổi phải được ghi nhận, không gọi là số lượng bắt buộc của đề bài |
| Đề xuất của kế hoạch này | Bộ ca biên đầy đủ hơn, thí nghiệm chi phí và tiêu chí đóng phase; đề xuất CI ban đầu đã bị loại | Chỉ được ghi là đã làm khi có triển khai và bằng chứng; theo phạm vi hiện hành ở mục 1.3 |

### 1.2. Những giới hạn cần giữ

- Kỹ thuật chính vẫn là **K05 Schema-Based API Testing/Fuzzing bằng Schemathesis**. Phân vùng, biên, bảng quyết định và pairwise hỗ trợ thiết kế test, không thay đề tài thành K06.
- SUT là REST API Directus với `qa_articles` và `qa_categories`; campaign chính có 10 cặp method-path.
- Không mở rộng mặc định sang frontend automation, GraphQL, WebSocket, load testing, nhiều DB hoặc API quản trị.
- Không yêu cầu sửa Directus upstream chỉ để hoàn thành đồ án QA.
- Không bắt buộc tìm được số lượng product defect cụ thể. Phải giải thích được bất thường và chứng minh phạm vi/coverage thực tế; nếu không tìm được lỗi, đối chiếu threshold đã đặt và nêu giới hạn.
- Review và peer evaluation cuối kỳ không được thay bằng xác nhận của AI. Chạy trên máy thứ hai là bằng chứng tốt nếu có, không tự biến thành yêu cầu bắt buộc mới của đề bài.

### 1.3. Phạm vi rút gọn đã chốt

Theo yêu cầu người dùng ngày 18/10/2026, **rút Phase 5 về finding/reproducer/phân tích nguyên nhân và bỏ Phase 7 (CI/CD)** để ưu tiên hoàn thành yêu cầu PDF. [Quyết định và ánh xạ task](dieu-chinh-pham-vi-phase5-phase7.md) ghi rõ phần giữ/bỏ và căn cứ trang 2–3, 8 của đề bài.

Lộ trình còn lại: **Phase 5 rút gọn → Phase 6 → Phase 8 → Phase 9**. Giữ số phase để bảo toàn ID/link; Phase 7 là **loại khỏi phạm vi**, không phải hoàn thành. Automation local/Docker, A–H, schema tests K05, phân tích kết quả, tái lập và peer evaluation vẫn cần có. Không cần workflow CI/CD để nghiệm thu theo kế hoạch này.

## 2. Điểm xuất phát và khoảng trống

Những kết quả dưới đây đến từ tài liệu và artifact đã được rà soát; không phải kết quả chạy mới ngày lập kế hoạch.

| Hạng mục | Đã có | Cần hoàn thiện |
|---|---|---|
| Môi trường | Docker, Directus 12.5.0, PostgreSQL 16, Schemathesis 4.30.0, pin image/digest | Chốt provenance dùng cho cuối kỳ; bảo đảm bản bàn giao chứa đủ công cụ cần thiết |
| Dữ liệu/quyền | Fixture ba category, 12 article; admin/editor/reader/anonymous | Gom quy tắc và nguồn của chúng thành đặc tả có thể kiểm chứng |
| Test nghiệp vụ | Sáu scenario; 11 invariant; positive acceptance cho 10 operation | Ánh xạ tới yêu cầu; bổ sung các lớp tương đương, biên và luật còn thiếu |
| Sinh test | Schema theo actor, raw/guided, stateful, replay | Bảng đánh giá schema đầy đủ đến đâu và điều gì phải kiểm tra ngoài schema |
| Kết quả Windows 13/10 | Sáu scenario PASS; invariant 9 PASS/2 FAIL/0 BLOCKED; pilot raw/guided ba seed có report và restore | Campaign chính chưa được chạy lại đầy đủ trên Windows; findings còn mở |
| Kết quả cũ | Có campaign ngân sách dài và nhiều replay | Không gộp đợt chạy, baseline, seed và ngân sách khác nhau thành một kết quả duy nhất |
| Lỗi/root cause | Có triage, source investigation, lỗi harness đã sửa, candidate schema và robustness | Gom finding/RCA đại diện, phân biệt kết luận với giả thuyết; không yêu cầu thêm hồ sơ vòng đời đầy đủ |
| Chi phí | Có budget và hai chiến lược raw/guided | Chưa có thí nghiệm được thiết kế rõ để kết luận hiệu quả chi phí |
| CI | Có automation chạy local; chưa thấy workflow CI lúc lập plan | Đã loại khỏi phạm vi hiện hành; không còn là khoảng trống bắt buộc phải bù |
| Bàn giao | Có README, tài liệu và artifact local | Một số tài liệu untracked, code Windows chưa commit; launcher phụ thuộc `tmp/lab-tools` ngoài repo |

**Điểm kỹ thuật phải đưa vào kế hoạch:** Schema Editor đã kiểm tra có kiểu `string/integer` nhưng chưa biểu diễn `title.maxLength=120`, enum `status` và miền `score=0..5`. Không được suy rằng dữ liệu hợp OpenAPI là đã hợp nghiệp vụ.

## 3. Lộ trình và thứ tự ưu tiên

| Phase | Mục tiêu | Phụ thuộc | Ước lượng công sức |
|---|---|---|---|
| 0 | Kiểm kê, giữ checkpoint demo và xác định baseline báo cáo | Bắt đầu ngay | 0,5 ngày |
| 1 | Đặc tả yêu cầu và truy vết | Phase 0 | 1-2 ngày |
| 2 | Review OpenAPI và mô hình sinh test | Phase 1 | 1 ngày |
| 3 | Thiết kế bộ test theo kỹ thuật đã học | Phase 1-2 | 1-2 ngày |
| 4 | Hoàn thiện automation và khả năng chạy lại | Phase 2-3 | 2-3 ngày |
| 5 | Báo cáo finding và RCA rút gọn | Dùng report/reproducer/source investigation phù hợp từ Phase 4 và lịch sử | Khoảng 1 buổi nếu đủ evidence; điều tra thiếu nguồn có thể phát sinh |
| 6 | Thí nghiệm tối ưu chi phí kiểm thử | Phase 3-5 | 1-2 ngày, cộng thời gian runner |
| 7 | Đã loại khỏi phạm vi: CI/CD | Không còn là phụ thuộc nghiệm thu | Không bố trí công sức |
| 8 | Đóng băng cấu hình và chạy bộ nghiệm thu cuối kỳ | Phase 1–4, Phase 5 rút gọn và kết quả Phase 6; không phụ thuộc Phase 7 | 1-2 ngày, cộng thời gian triage |
| 9 | Đóng gói, báo cáo, demo và đánh giá đóng góp | Phase 8 | 1-2 ngày |

Có thể gom báo cáo A–H và chuẩn bị gói bàn giao khi chờ phân tích finding; không chuẩn bị CI trong lộ trình này. Không chạy hai suite ghi/xóa song song trên cùng database.

**Theo lịch hiện tại:** Giữa kỳ là 20/10/2026; ngày bảo vệ cuối kỳ chưa xác nhận, báo cáo cuối kỳ nộp trước bảo vệ một tuần. Ngày 18-19/10 ưu tiên Phase 0, mô tả đúng trạng thái và ổn định demo. Phase 7 đã được loại; không cố chạy campaign dài trước giữa kỳ bằng cách thay đổi nhiều thành phần đang chạy ổn.

---

## Phase 0. Kiểm kê và giữ nền tảng đang hoạt động

**Cập nhật 18/10/2026:** Đã hoàn thành P0-01 đến P0-06 về kiểm kê và bảo toàn tệp. Xem [kết quả Phase 0](00-hien-trang-va-baseline.md), [bộ demo tham chiếu](00-bo-demo-tham-chieu.md) và [quyết định còn thiếu](00-quyet-dinh-va-phu-thuoc.md). Chưa chạy lại test hoặc xác nhận Docker/API hiện healthy; không đồng nghĩa đã hoàn thành các phase tiếp theo.

### Điều kiện bắt đầu

Có checkout và các tài liệu/artifact local hiện tại. Bước đầu chỉ cần khảo sát tĩnh; kiểm tra dịch vụ hoặc chạy demo được thực hiện ở đợt triển khai được giao sau này.

### Công việc

- [x] **P0-01 - Lập bảng nguồn bằng chứng.** Liệt kê tài liệu, run ID, baseline, fixture, profile, seed, ngân sách, tình trạng artifact và kết luận có thể dùng.
- [x] **P0-02 - Phân loại đợt chạy.** Tách lịch sử trước/sau license, campaign dài, pilot Windows và targeted replay. Ghi rõ đợt nào chỉ có giá trị lịch sử.
- [x] **P0-03 - Kiểm kê trạng thái Git.** Xác định thay đổi có sẵn, tài liệu chưa track, helper ngoài repo và artifact đang bị ignore. Chưa tự stage/commit hay thay `.gitignore`.
- [x] **P0-04 - Đối chiếu provenance.** Phân biệt commit source Directus được đọc, source baseline trong manifest, image digest thực thi, harness SHA và phần sửa chưa commit. Đánh dấu phân tích source nào chưa đối chiếu đúng bản runtime.
- [x] **P0-05 - Chọn bộ demo giữa kỳ.** Giữ ba luồng CRUD Editor, query và quyền Reader; chọn run/report đại diện, cùng hai finding đã biết và giới hạn tương ứng.
- [x] **P0-06 - Ghi các quyết định còn thiếu.** Expected của chuỗi rỗng, dữ liệu sai kiểu, query không hợp lệ; policy CI với finding mở; nơi giữ evidence bàn giao; điều kiện license/runtime khi dựng mới.

### Đầu ra dự kiến

- `docs/HoanThanhPlan/00-hien-trang-va-baseline.md`.
- Bảng evidence index: đường dẫn/run ID, version/hash, budget, trạng thái, phạm vi kết luận.
- Danh sách quyết định cần chốt và danh sách phụ thuộc ngoài repo.

### Tiêu chí hoàn thành

- Có thể chỉ ra nguồn của mọi con số dùng trong demo.
- Không dùng pilot 60 giây thay thế kết quả campaign 1.200 giây.
- Không đồng nhất G1 nội bộ với việc hoàn thành mọi yêu cầu cuối kỳ.
- Có checkpoint tham chiếu và phương án bảo toàn thay đổi hiện tại trước khi triển khai tiếp.

---

## Phase 1. Hoàn thiện yêu cầu người dùng, đặc tả và truy vết

**Cập nhật 18/10/2026:** Hoàn thành đầu ra tài liệu và review tĩnh P1-01 đến P1-08. Xem [đặc tả v0.2](01-yeu-cau-va-dac-ta.md), [review và gap task](01-review-dac-ta.md), [truy vết nghiệp vụ](01-truy-vet-nghiep-vu.md) và [ma trận CSV](01-traceability.csv). Người dùng đã chọn bám baseline Directus đã pin, không thêm quy tắc nghiệp vụ; [đối chiếu source P1-05](01-doi-chieu-baseline-p1-05.md) có căn cứ từ đúng commit. P1-05 hoàn thành ở mức đặc tả; các Q kỹ thuật còn OPEN được bàn giao Phase 2–4 theo tiêu chí cho phép ghi câu hỏi mở. Không có test mới hoặc thay đổi harness/schema/policy; đây không phải nghiệm thu runtime.

### Điều kiện bắt đầu

Phase 0 đã xác định phạm vi, nguồn bằng chứng và những quyết định chưa rõ.

### Công việc

- [x] **P1-01 - Viết mục tiêu và ranh giới hệ thống.** Mô tả Directus tổng thể, rồi giới hạn rõ hệ thống quản lý bài viết/category dùng trong lab. Không viết lại đặc tả cho toàn bộ CMS.
- [x] **P1-02 - Viết yêu cầu người dùng có mã `UR-*`.** Bao gồm CRUD Editor, đọc nội dung công khai, bảo vệ trường kín, tính đúng của truy vấn và toàn vẹn dữ liệu.
- [x] **P1-03 - Viết quy tắc hệ thống có mã `BR-*`.** Kiểu dữ liệu, miền giá trị, default, nullable, trường bắt buộc, quan hệ và policy. Mỗi quy tắc có nguồn: lab đã chốt, cấu hình, tài liệu hoặc giả định cần xác nhận.
- [x] **P1-04 - Viết tiêu chí chấp nhận.** Dùng Given/When/Then hoặc precondition/input/expected/postcondition; phải quan sát và kiểm tra tự động được khi phù hợp.
- [x] **P1-05 - Chốt các tình huống chưa rõ.** Phân biệt thiếu trường, `null`, chuỗi rỗng, khoảng trắng, sai kiểu; POST với PATCH; ID không tồn tại với không có quyền. Với status code, cần nguồn phù hợp baseline, không suy từ thông lệ chung. Hoàn thành ở mức phân loại/expected có nguồn; câu hỏi kỹ thuật thiếu căn cứ vẫn OPEN và chuyển Phase 2–4.
- [x] **P1-06 - Lập bảng rủi ro.** Đánh giá mức ảnh hưởng và khả năng gặp; ưu tiên rò rỉ dữ liệu/quyền ghi, mất dữ liệu, validation, query sai và crash. Thang điểm do nhóm đề xuất phải được giải thích.
- [x] **P1-07 - Tạo ma trận truy vết.** Ánh xạ UR → BR/tiêu chí chấp nhận → API/actor → kỹ thuật thiết kế → test ID → oracle → run/finding. Giữ nguyên mã S1-S6/INV đã có, không đổi mã chỉ để làm bảng đẹp.
- [x] **P1-08 - Review tĩnh đặc tả.** Ghi vấn đề mơ hồ, mâu thuẫn, thiếu trường hợp, thiếu nguồn expected; ghi quyết định xử lý và người review thực tế khi đã diễn ra.

### Cấu trúc một yêu cầu

| Trường | Nội dung cần ghi |
|---|---|
| ID, tên | Mã ổn định và ý nghĩa nghiệp vụ |
| Nguồn | Yêu cầu môn học, quyết định lab, tài liệu hoặc giả định |
| Actor và tiền đề | Người dùng, dữ liệu và quyền cần có |
| Luồng chính/ngoại lệ | Hành vi được yêu cầu và trường hợp bị từ chối |
| Acceptance criteria | Kết quả và trạng thái dữ liệu mong đợi |
| Rủi ro | Ảnh hưởng nếu sai, mức ưu tiên |
| Truy vết | API, test, evidence và finding liên quan |

### Đầu ra dự kiến

- `docs/HoanThanhPlan/01-yeu-cau-va-dac-ta.md`.
- `docs/HoanThanhPlan/01-review-dac-ta.md`.
- Bổ sung truy vết nghiệp vụ trong `docs/HoanThanhPlan/01-truy-vet-nghiep-vu.md` (liên kết lại từ `docs/traceability.md`), giữ đối chiếu A-H hiện có.

### Tiêu chí hoàn thành

- Mọi quy tắc quan trọng trong phạm vi có nguồn, expected và cách kiểm chứng.
- Mọi yêu cầu ưu tiên cao có test hiện hữu hoặc task bổ sung; không có khoảng trống bị bỏ qua.
- Quy tắc chưa rõ được ghi mở, không âm thầm lấy actual làm expected.
- Có thể giải thích vì sao từng scenario/invariant hiện tại tồn tại.

---

## Phase 2. Review OpenAPI và thiết kế cách sinh test

**Cập nhật 18/10/2026:** Hoàn thành review tĩnh và thiết kế P2-01 đến P2-09; xem [báo cáo Phase 2](02-danh-gia-openapi-va-sinh-test.md), [ma trận 26 BR](02-ma-tran-rang-buoc.md), [bảy case sinh thật](02-case-sinh-dai-dien.md) và [quy tắc overlay](02-quy-tac-overlay.md). Đã xác minh scope-only raw, 11 additions guided và transition thật. Các giới hạn timestamp registry/ID map lịch sử/chuỗi đủ/quyền được ghi VFY-01…05 và bàn giao Phase 3–4; không coi hoàn thành tài liệu là đã chạy test mới.

### Điều kiện bắt đầu

Có đặc tả Phase 1 và snapshot schema theo actor. Chỉ xuất snapshot mới khi thực sự triển khai và fixture/policy đã được chuẩn bị đúng.

### Công việc

- [x] **P2-01 - Chọn schema tham chiếu.** Ghi actor, fixture version, hash, run export và baseline. Seed trước khi export; schema mới có provenance riêng, không ghi đè snapshot cũ.
- [x] **P2-02 - Xác minh inventory.** Phân biệt 14 operation trong schema Editor với 10 operation campaign; giải thích các bulk operation bị loại.
- [x] **P2-03 - Đối chiếu từng ràng buộc.** Kiểm tra `required`, `nullable`, kiểu, enum, độ dài, khoảng số, format, relation, response status, content type và response shape.
- [x] **P2-04 - Ghi khoảng trống đã thấy.** `title` thiếu maxLength, `status` thiếu enum, `score` thiếu khoảng; xác định thêm ý nghĩa `format: timestamp` với đúng bản công cụ đang pin.
- [x] **P2-05 - Phân loại oracle.** Contract oracle dựa OpenAPI; business oracle dựa BR/fixture; authorization oracle dựa policy. Xác định assertion nào có thể sinh và assertion nào phải viết bổ sung.
- [x] **P2-06 - Giữ ranh giới raw/guided.** Raw chỉ scope operation; guided thêm example/ID/hướng dẫn liên kết có lý do và diff. Nếu cần sửa hợp đồng, tạo bản riêng có nguồn, không trộn với guidance hoặc kết quả raw.
- [x] **P2-07 - Mô tả chuỗi stateful.** Producer POST → ID từ response → GET/PATCH/DELETE. Xác minh liên kết thực tế, độ dài chuỗi, dữ liệu phụ thuộc và cleanup; không coi bật phase stateful là đủ chứng minh đã chạy chuỗi.
- [x] **P2-08 - Thiết kế test quyền ngoài schema.** Operation vắng khỏi Reader schema chỉ chứng minh bị lọc trong tài liệu. Các phép thử bị cấm cần request có chủ đích trong lab, expected và read-back phù hợp.
- [x] **P2-09 - Lưu test sinh đại diện.** Chọn positive, negative, biên, response mismatch và stateful; truy được schema location, seed, case ID, request, checks và artifact. Không cần chuyển mọi generated case thành bảng thủ công.

### Bảng bắt buộc trong đầu ra

| Quy tắc | Nguồn đặc tả | OpenAPI thể hiện | Generator có thể sinh gì | Test/oracle bổ sung | Kết luận |
|---|---|---|---|---|---|
| `score` là số nguyên 0-5 | BR tương ứng | Hiện có integer, thiếu min/max | Dữ liệu integer hợp schema có thể ngoài 0-5 | Ca biên và read-back theo BR | Khoảng trống hợp đồng, cần kiểm tra bổ sung |

### Đầu ra dự kiến

- `docs/HoanThanhPlan/02-danh-gia-openapi-va-sinh-test.md`.
- Sơ đồ đặc tả → schema → generator → request/chuỗi → oracle → report.
- Danh mục generated case đại diện và quy tắc quản lý overlay.

### Tiêu chí hoàn thành

- Mỗi ràng buộc có câu trả lời: schema kiểm được không, nếu không thì ai/cơ chế nào kiểm.
- Phân biệt dữ liệu hợp schema với dữ liệu hợp nghiệp vụ.
- Mọi overlay truy được nguồn và thay đổi; raw vẫn bất biến.
- Quyền cấm không bị đánh dấu đã kiểm thử chỉ vì operation vắng trong schema.

---

## Phase 3. Thiết kế bộ test có chủ đích và tiêu chí kết thúc

**Cập nhật 18/10/2026:** Hoàn thành thiết kế/review tĩnh P3-01 đến P3-09. [Báo cáo Phase 3](03-thiet-ke-test-va-coverage.md) có inventory, phân vùng, biên, quyền, chuỗi và oracle; [catalog](03-test-case-catalog.md) gồm 221 ca ngoài pairwise +36 query tham chiếu, trong đó9 là subset phủ37/37 cặp. [Tiêu chí kết thúc](03-tieu-chi-ket-thuc.md) và [review](03-review-thiet-ke.md) giữ rõ CONDITIONAL/OPEN/NOT_RUN, budget và bàn giao Phase 4. Chưa triển khai automation hoặc gửi request API mới.

### Điều kiện bắt đầu

Đặc tả đủ rõ và bảng khoảng trống OpenAPI đã có. Đây là phase thiết kế trước khi bổ sung automation.

### Công việc

- [x] **P3-01 - Kiểm kê test hiện có.** Gắn S1-S6, 11 invariant, smoke validation và positive-operations vào BR tương ứng. Xác định test trùng mục tiêu và phần chưa có test.
- [x] **P3-02 - Thiết kế phân vùng tương đương.** Ghi lớp hợp lệ/không hợp lệ, đại diện, lý do phân lớp và expected. Với negative test của một ràng buộc, giữ các trường khác hợp lệ để tránh lỗi che lấp nhau.
- [x] **P3-03 - Thiết kế giá trị biên.** Bao gồm cả nhận dữ liệu hợp lệ và từ chối dữ liệu ngoài miền; kiểm tra trạng thái dữ liệu sau request.
- [x] **P3-04 - Lập bảng quyết định quyền.** Actor × thao tác × trạng thái bản ghi × trường yêu cầu. Bao gồm GET list/detail, ghi bị cấm, nested relation/projection trong phạm vi đã chốt.
- [x] **P3-05 - Thiết kế chuỗi nghiệp vụ.** Create/read-back, PATCH giữ field, delete, relation SET NULL và request bị từ chối không thay đổi dữ liệu.
- [x] **P3-06 - Xác định oracle độc lập.** Expected đến từ đặc tả/fixture biết trước; không dùng kết quả của chính chức năng đang kiểm tra làm expected. Query sort phải có khóa phụ và quy tắc so sánh phù hợp dữ liệu/DB.
- [x] **P3-07 - Chọn mô hình pairwise nhỏ.** Dùng query đọc với dữ liệu cố định; xác định yếu tố, giá trị, constraints, tập vét cạn hữu hạn và các ca rủi ro cao giữ riêng.
- [x] **P3-08 - Chốt tiêu chí kết thúc trước khi chạy.** Tách điều kiện môi trường, pass/fail test, độ hoàn tất campaign và mức đủ bằng chứng cho báo cáo.
- [x] **P3-09 - Review test case.** Kiểm tra thiếu positive/negative, precondition không đủ, expected quá rộng, phụ thuộc dữ liệu và cleanup.

### Bộ dữ liệu cần thiết kế

| Đối tượng | Ca cần xét | Lưu ý |
|---|---|---|
| `score` | -1, 0, 1, 4, 5, 6; số thập phân; sai kiểu; null; thiếu trường | Default/coercion và POST/PATCH phải theo đặc tả, không giả định |
| `title` | Độ dài 119/120/121; thiếu, null, rỗng, khoảng trắng; Unicode | Không tự suy required đồng nghĩa với cấm chuỗi rỗng; chốt cách tính độ dài |
| `status` | draft, published, ngoài enum; null; thiếu; sai kiểu | Có kiểm tra default nếu được đặc tả |
| `category` | ID tồn tại/không tồn tại; null; xóa category đang được tham chiếu | Lấy ID động, giữ article và kiểm tra SET NULL |
| `published_at` | null, giá trị hợp lệ, rỗng, sai format | Tách khả năng phát sinh 5xx khỏi việc dữ liệu có hợp lệ hay không |
| Quyền | Reader thấy published, không thấy draft/trường kín; không ghi; anonymous bị cấm | So dữ liệu trước/sau khi ghi bị từ chối; không gán mọi lỗi là 401/404 |
| Query | filter, sort, limit, offset, page, search, fields | Có expected tập ID, thứ tự và projection từ fixture |

**Tái sử dụng đúng:** Invariant `invalid-field-rejection` hiện gửi cùng lúc status và score sai; smoke đã có probe riêng cho hai trường. Ánh xạ các probe hiện hữu trước, rồi bổ sung phần biên/độc lập còn thiếu.

### Mẫu một test case

`ID | UR/BR | mục tiêu/rủi ro | kỹ thuật | actor | precondition | input/bước | expected response | expected dữ liệu | cleanup | ưu tiên | nơi automation | run/finding`.

### Ngưỡng nghiệm thu đề xuất của nhóm

- 10/10 operation có bằng chứng positive acceptance hợp lệ, không chỉ được gửi request.
- 100% BR ưu tiên cao đã chốt có ít nhất một test và kết quả hoặc trạng thái blocked có lý do.
- Các lớp tương đương, biên và luật bắt buộc đã liệt kê đều được thực thi; số lượng mẫu số phải rõ.
- Các test quyền và toàn vẹn dữ liệu quan trọng không có failure chưa được giải thích/đánh giá ảnh hưởng.
- Pairwise đạt 100% cặp giá trị khả thi của mô hình đã chọn; không gọi đó là phủ mọi tổ hợp.
- Campaign có báo cáo từng profile/seed và trạng thái hoàn tất; không dùng ngưỡng operation 100% để suy rằng toàn bộ schema hoặc hệ thống được phủ.

Đây là ngưỡng đề xuất, không phải nội dung nguyên văn của đề bài. Nếu thiếu bằng chứng thì ghi chưa đạt; không thay mẫu số để nâng coverage.

### Đầu ra và tiêu chí hoàn thành

- `docs/HoanThanhPlan/03-thiet-ke-test-va-coverage.md` có bảng phân vùng, biên, quyết định, pairwise và case catalog.
- Ma trận test/truy vết được cập nhật; mọi case có oracle, dữ liệu và cách chạy dự kiến.
- Có tiêu chí đầu vào/đầu ra, ngân sách và danh sách rủi ro chưa phủ.

---

## Phase 4. Hoàn thiện automation, tính ổn định và khả năng chạy lại

### Điều kiện bắt đầu

Phase 2-3 đã xác định phần cần bổ sung. Các thay đổi chung về interface, fixture/policy, baseline hoặc metadata phải tuân theo quyết định dự án hiện hành.

### Công việc

- [x] **P4-01 - Tích hợp phần Windows cần thiết.** Xử lý phụ thuộc launcher/jq/helper ngoài repo thành công cụ bàn giao được hoặc dependency có hướng dẫn rõ. Không để đường dẫn `../tmp` trên máy hiện tại là điều kiện ngầm.
- [x] **P4-02 - Bổ sung test còn thiếu vào harness hiện có.** Dùng cơ chế credential, URL, actor, fixture map, run ID và report chung; tránh tạo bộ helper song song không tương thích.
- [x] **P4-03 - Bảo đảm precondition.** Đúng URL lab, actor, operation allowlist, health, fixture và schema hash; thiếu điều kiện thì fail/blocked rõ ràng.
- [x] **P4-04 - Bảo đảm dữ liệu độc lập.** Dùng ID động, tên probe phân biệt được, cleanup hoặc snapshot/restore đúng phạm vi; không reset giữa bước của chuỗi stateful.
- [x] **P4-05 - Hoàn thiện replay.** Lưu parent chain, ID mapping và các bước cần thiết. Phân biệt replay đầy đủ, request cuối, mismatch và không gửi được target.
- [x] **P4-06 - Chuẩn hóa report.** Bảo toàn mã thoát runner; tách setup failure, assertion failure, timeout/ngắt và restore failure. Lưu artifact ngay cả khi thất bại.
- [x] **P4-07 - Kiểm tra assertion.** Negative test không chỉ dựa non-2xx: đối chiếu loại lỗi thích hợp và chứng minh request đã đến đúng chức năng. Với dữ liệu sai, 5xx không được coi là từ chối hợp lệ.
- [x] **P4-08 - Kiểm tra tính lặp lại.** Chạy lại suite ngắn trên cùng điều kiện; nếu kết quả khác, điều tra state, thời gian, dữ liệu và thứ tự request, ghi flaky riêng.
- [x] **P4-09 - Kiểm tra đúng mức.** Kiểm tra cú pháp/diff; chạy case sửa đổi và tích hợp liên quan. Chưa cần chạy campaign dài cho mọi chỉnh sửa tài liệu hoặc helper nhỏ.

### Đầu ra dự kiến

- Harness tích hợp các test đã chốt; README cập nhật lệnh và dependency thực tế.
- Report của suite ngắn, replay và restore; metadata có provenance của thay đổi.
- Danh sách hạn chế stateful/Windows còn tồn tại.

### Tiêu chí hoàn thành

- Lệnh tài liệu hóa chạy được từ môi trường đáp ứng dependency, không cần helper bí mật ngoài repo.
- Các test mới truy được về case/BR và có report.
- Restore failure dừng việc ghi dữ liệu tiếp theo; không được tiếp tục như môi trường vẫn hợp lệ.
- Không nới assertion, tắt check hoặc thêm blanket skip để tạo PASS.

---

**Cập nhật 18/10/2026:** Hoàn thành P4-01…09 ở phạm vi automation và suite ngắn. [Báo cáo Phase 4](04-automation-va-tai-lap.md) có hai lượt 58/58 PASS, sáu scenario PASS, 11 invariant với 9 PASS/2 FAIL giữ nguyên, replay/check/restore thật, bài thử budget/khóa và giới hạn. [Bảng kết quả](04-ket-qua-case.csv) giữ 199/257 case NOT_RUN theo subset nghiệm chứng; chưa chạy full campaign/pairwise/CI hoặc nghiệm thu cuối kỳ.

## Phase 5. Báo cáo finding và phân tích nguyên nhân — rút gọn

**Trạng thái:** Chưa thực hiện bản rút gọn. Phạm vi đã được người dùng chốt tại [quyết định](dieu-chinh-pham-vi-phase5-phase7.md); không yêu cầu quy trình vòng đời bug đầy đủ hoặc sửa Directus upstream.

### Điều kiện bắt đầu

Có report/request/response, reproducer và metadata của finding; ưu tiên dùng evidence Phase 4 và tài liệu lịch sử còn phù hợp baseline. Chỉ xác minh lại phần thiếu hoặc đã bị ảnh hưởng bởi thay đổi liên quan.

### Công việc cần giữ

- [ ] **P5-01 - Gom bảng finding tối giản.** Mỗi nhóm có ID, loại, trạng thái, actor/baseline, expected có nguồn, actual và đường dẫn run/case/reproducer. Tái sử dụng bảng/triage cũ, không tạo nhiều hồ sơ trùng.
- [ ] **P5-02 - Gom trùng và phân loại.** Gộp nội dung P5-06 cũ vào đây: product candidate/defect đã xác nhận, schema/contract, harness/fixture, môi trường hoặc unresolved. Không cộng số check failure/seed thành số defect.
- [ ] **P5-03 - Chọn đại diện.** Tập trung aggregate 500 và một mismatch OpenAPI như POST shape hoặc DELETE 204. Lỗi harness đã sửa có thể trích ngắn nếu giúp giải thích kết quả; không bắt buộc thành hồ sơ thứ ba.
- [ ] **P5-04 - Dẫn reproducer đủ dùng.** Giữ request/chuỗi, precondition, control và kết quả replay đã có. Chỉ replay/thu nhỏ thêm khi chưa đủ căn cứ hoặc thay đổi liên quan làm evidence cũ không còn phù hợp; không chạy lại toàn campaign chỉ để lập báo cáo.
- [ ] **P5-05 - Phân tích nguyên nhân có căn cứ.** Dùng source đúng pin/provenance và log phù hợp cho đại diện; chỉ rõ đường xử lý/nguyên nhân, tách giả thuyết chưa xác nhận. Có ít nhất một phân tích nguyên nhân được hỗ trợ bằng evidence; không buộc điều tra sâu mọi biến thể trùng.
- [ ] **P5-08 - Chốt trạng thái và ảnh hưởng.** Nêu finding nào còn mở, mức ảnh hưởng tới kết luận và phần chưa thể khẳng định. Không yêu cầu đóng mọi finding để qua phase, không coi tái hiện là sửa xong.

**Task được giản lược:** P5-06 gộp vào P5-02; P5-07 (hoàn tất riêng một vòng đời lỗi harness) bỏ khỏi phạm vi bắt buộc. Giữ ID để truy vết; không đánh dấu các task đã bỏ là hoàn thành. Không bắt buộc thang severity/priority chi tiết hoặc luồng trạng thái nhiều bước.

### Đầu ra và tiêu chí hoàn thành

- Một tệp `docs/HoanThanhPlan/05-finding-register.md`, gồm bảng tổng hợp, phân tích đại diện và link evidence; không cần tách nhiều báo cáo.
- Có thống kê theo nhóm finding, expected/actual, reproducer, phân tích nguyên nhân có căn cứ và giới hạn phù hợp phần G/K05.
- Finding nghiêm trọng về 5xx/quyền/toàn vẹn trong tập nghiệm thu có phân loại hoặc unresolved kèm ảnh hưởng; không chuyển candidate thành defect chỉ để tăng số lượng.
- Ước lượng một buổi nếu evidence sẵn có đủ dùng; phần thiếu nguồn vẫn phải được xử lý hoặc công bố rõ, không bịa kết luận để kịp thời gian.

---

## Phase 6. Thiết kế và thực hiện thí nghiệm tối ưu chi phí

### Điều kiện bắt đầu

Suite và report ổn định; có quy tắc deduplicate/triage ở Phase 5. Chốt thiết kế thí nghiệm trước khi lấy kết quả.

### P6-01. Xác định câu hỏi và chi phí cần đo

- [ ] Xác định câu hỏi: guided có giúp đi sâu hơn trong cùng ngân sách không; pairwise giảm bao nhiêu ca của miền query hữu hạn; replay tiết kiệm gì khi kiểm tra hiện tượng đã biết.
- [ ] Ghi công thiết kế/triển khai, thời gian chuẩn bị, thời gian runner, request thực gửi, thời gian triage và công bảo trì. Chỉ báo cáo những gì thực sự đo được.
- [ ] Chọn đơn vị và cách ghi thời gian nhất quán; không quy đổi công sức thành tiền khi chưa có cơ sở.

### P6-02. So sánh raw và guided có kiểm soát

- [ ] Giữ cùng image, fixture/policy ban đầu, actor, allowlist, rate, worker, timeout và ngân sách; snapshot/restore trước/sau mỗi lượt.
- [ ] Dùng cùng tập seed để có các lượt đối chiếu; seed không thay thế việc kiểm soát dữ liệu và môi trường.
- [ ] Ghi rõ mục tiêu so sánh. Hai profile hiện tại khác cả guidance lẫn phase stateful, nên chỉ kết luận hiệu quả của hai chiến lược tổng thể.
- [ ] Nếu muốn đo riêng ảnh hưởng guidance, thiết kế thí nghiệm phụ với các phase giống nhau; không đổi profile chính âm thầm. Thí nghiệm phụ là tùy chọn nếu ngân sách không đủ.
- [ ] So coverage, positive acceptance, request, thời gian và finding sau triage. Không chỉ so số case generated hoặc số check failure.
- [ ] Báo cáo từng seed, trung vị/khoảng dao động phù hợp và lượt incomplete. Không suy kết luận tổng quát từ một seed.

### P6-03. Thí nghiệm pairwise trên miền query hữu hạn

Mô hình đề xuất dùng Editor, GET articles và fixture cố định; không có thao tác ghi:

| Yếu tố | Giá trị đề xuất |
|---|---|
| Filter status | Không filter; draft; published |
| Sort | `id`; `title,id`; `-score,id` |
| Fields | `id,title`; `id,title,status,score` |
| Phân trang | `limit=3&offset=3`; `limit=3&page=2` |

Miền này có `3 × 3 × 2 × 2 = 36` tổ hợp trước khi áp dụng constraints. Nếu cần thay mô hình, ghi phiên bản, miền khả thi và lý do trước khi chạy.

- [ ] Sinh danh sách 36 tổ hợp tham chiếu và tập pairwise N ca; loại tổ hợp bất khả thi theo quy tắc có giải thích.
- [ ] Kiểm tra mọi cặp giá trị khả thi xuất hiện trong tập pairwise; lưu danh sách cặp còn thiếu nếu có.
- [ ] Chạy cả hai tập với cùng oracle, fixture và cách đo. Chạy lặp nếu cần đánh giá thời gian; tách setup khỏi runner.
- [ ] Giữ các ca quyền, dữ liệu biên và tương tác rủi ro cao riêng; pairwise không thay toàn bộ suite hay đảm bảo phát hiện lỗi từ ba yếu tố trở lên.
- [ ] Chỉ dùng cách gọi "vét cạn" cho miền 36 tổ hợp đã định nghĩa, không phải mọi đầu vào API.

### P6-04. Đánh giá replay và chọn tần suất chạy

- [ ] Chọn finding đã có reproducer; đo thời gian replay xác minh hiện tượng so với chạy campaign tìm lại. Ghi hai hoạt động có mục tiêu khác nhau, replay không thay khả năng khám phá của fuzzing.
- [ ] Chọn suite nhanh cho thay đổi thường xuyên, campaign có ngân sách cho chạy theo lịch và bộ đầy đủ trước nghiệm thu.
- [ ] Quyết định mức budget và tần suất dựa trên số liệu; giữ nguyên cấu hình trước đó trong lịch sử.

### Công thức và bảng cần có

- Giảm số ca của mô hình hữu hạn: `(N_vét_cạn - N_pairwise) / N_vét_cạn × 100%`.
- Pair coverage: `số cặp khả thi đã phủ / tổng số cặp khả thi`.
- Coverage tăng thêm/phút: chênh lệch coverage được đo chia cho thời gian, phải nêu rõ loại coverage và mẫu số.
- Finding đã triage/giờ là chỉ số mô tả trong thí nghiệm, không phải bảo đảm chất lượng. Nếu không có defect xác nhận, không tính chi phí/defect bằng cách chia cho 0 hoặc thay candidate thành defect.

### Đầu ra và tiêu chí hoàn thành

- `docs/HoanThanhPlan/06-toi-uu-chi-phi.md`: câu hỏi, cấu hình, số liệu, phương pháp tính, kết luận và hạn chế.
- Có ít nhất một kết luận định lượng có dữ liệu gốc kiểm tra được; nếu chưa đủ dữ liệu thì ghi chưa thể kết luận.
- Không dùng số tiết kiệm từ ví dụ trong slide làm số liệu thực nghiệm của nhóm.
- Phân biệt giảm số ca với giảm thời gian và giảm tổng công sức.

---

## Phase 7. CI/CD — đã loại khỏi phạm vi

**Quyết định:** Bỏ Phase 7 theo yêu cầu người dùng ngày 18/10/2026. Đề bài không bắt buộc pipeline CI/CD; xem [căn cứ và phần còn giữ](dieu-chinh-pham-vi-phase5-phase7.md).

- P7-01…09 không còn là task phải thực hiện; không lập PR gate, job theo lịch, allowlist CI, secret/upload artifact trên CI hoặc demo CD.
- Không yêu cầu workflow, run CI thật hoặc tệp `07-ci-va-quality-gate.md`. Không ghi Phase 7 là đã triển khai/đã PASS.
- Giữ số phase làm tham chiếu; đi từ Phase 6 sang Phase 8. Phase 8–9 không được phụ thuộc vào kết quả CI.
- Script local/Docker, README/dependency, lưu report/reproducer, bảo toàn exit code và cleanup/restore vẫn thuộc Phase 4/8/9. Lịch sử Git/task và peer evaluation của môn học vẫn giữ.

---

## Phase 8. Đóng băng cấu hình và thực hiện nghiệm thu cuối kỳ

### Điều kiện bắt đầu

Đặc tả/test/automation đã review, báo cáo finding Phase 5 rút gọn có trạng thái rõ, kết quả chi phí Phase 6 và cấu hình/ngưỡng đánh giá đã chốt. Không yêu cầu CI hoặc đầu ra Phase 7. Thay đổi liên quan trong working tree phải được ghi nhận đầy đủ và được tích hợp đúng quy trình trước khi chọn checkpoint nghiệm thu.

### Công việc

- [ ] **P8-01 - Khóa checkpoint tham chiếu.** Ghi harness commit, source baseline, image digest, fixture/policy, schema hash, config và dependency. Git/tag chỉ thực hiện khi được giao quyền tương ứng.
- [ ] **P8-02 - Chạy preflight và deterministic suite.** Doctor, seed, smoke, export-schema, scenario, invariant/test bổ sung; đối chiếu BR và positive acceptance 10 operation.
- [ ] **P8-03 - Xử lý sai lệch trước campaign.** Precondition/restore/harness failure phải xử lý trước; không chạy tiếp để lấy số lượng test khi điều kiện không đúng.
- [ ] **P8-04 - Chạy campaign chính theo cấu hình đã chốt.** Kế hoạch nội bộ hiện có là raw/guided, seed 101/202/303, một worker, 5/s, timeout request 10 giây, tối đa 100 examples và 1.200 giây/profile/seed. Ghi mọi điều chỉnh và lý do.
- [ ] **P8-05 - Đối chiếu artifact từng lượt.** Report hiện diện, operation tested, positive acceptance, parameters/keywords/responses coverage, check failures, errors, thời gian, stop reason và restore.
- [ ] **P8-06 - Replay finding đại diện và finding nghiêm trọng mới.** Kiểm tra nguồn request/chuỗi, provenance và kết quả; cập nhật register.
- [ ] **P8-07 - Tổng hợp phạm vi chưa phủ.** BR chưa chạy, coverage thấp, stateful limitation, case blocked và failure chưa đủ căn cứ.
- [ ] **P8-08 - Chốt kết luận nghiệm thu.** Đạt/đạt có giới hạn/chưa đạt theo tiêu chí đã đặt; giải thích ảnh hưởng finding mở, không gọi toàn campaign PASS khi runner thất bại.

### Cách ghi độ hoàn tất

Tách các khía cạnh trong báo cáo:

- **Thực thi harness:** Có chạy, có report, snapshot/restore và cleanup đúng không.
- **Kết quả assertion:** PASS/FAIL/BLOCKED của case/check.
- **Mức hoàn tất tìm kiếm:** Đủ điều kiện dừng đã chốt hay bị timeout/ngắt. Report có thể được ghi hoàn chỉnh trong khi chiến dịch vẫn hết budget/chưa phủ mục tiêu.
- **Mức đủ bằng chứng:** Có đáp ứng câu hỏi nghiên cứu và yêu cầu môn học trong phạm vi công bố không.

Ngân sách runner mặc định của sáu lượt là 120 phút, chưa tính setup/restore/triage; đây không phải bảo đảm thời gian wall-clock hay bảo đảm campaign hoàn tất. Không cần chạy lại campaign không bị ảnh hưởng chỉ vì chỉnh văn bản báo cáo; phải chạy lại phần bị ảnh hưởng khi sửa code/schema/fixture/policy/oracle liên quan.

### Đầu ra và tiêu chí hoàn thành

- `docs/HoanThanhPlan/08-bao-cao-nghiem-thu.md` cùng evidence index chốt cuối kỳ.
- Không trộn số liệu pilot, campaign cũ và campaign mới mà thiếu nhãn.
- Mọi kết luận có run/hash/config; mọi finding ưu tiên cao có quyết định hoặc giới hạn được nêu rõ.
- Những lượt thiếu/ngắt được ghi đúng trạng thái; việc đạt 10/10 operation không tự xóa tình trạng incomplete.

---

## Phase 9. Đóng gói, báo cáo và chuẩn bị bảo vệ

### Điều kiện bắt đầu

Phase 8 có bộ số liệu và kết luận đủ ổn định để làm nguồn chính.

### Công việc

- [ ] **P9-01 - Gom báo cáo theo A-H.** Tái sử dụng bộ `phan1/`, `phan2/` và tài liệu hiện có; thêm nội dung đặc tả, review tĩnh, thiết kế test và chi phí vào đúng phần. Không tạo nhiều bản kết luận mâu thuẫn.
- [ ] **P9-02 - Đồng bộ trạng thái tài liệu.** Những mục "mới nhất/current" cũ phải có mốc thời gian rõ; bảo toàn lịch sử nhưng trỏ tới kết quả nghiệm thu được chọn.
- [ ] **P9-03 - Chuẩn bị gói bàn giao.** Code/harness, README, dependency, env example, manifest, schema chọn lọc, report/reproducer sạch secret và evidence index. Artifact bị ignore không mặc nhiên theo bản clone; phải có cách chuyển giao riêng đã kiểm tra.
- [ ] **P9-04 - Kiểm tra dựng mới.** Dùng thư mục/môi trường cô lập; đi theo README để kiểm tra dependency, seed, smoke, export, scenario và replay đại diện. Dùng volume riêng, không reset DB hiện hữu. Ghi đúng là máy mới, thư mục mới hay máy thứ hai tùy thực tế.
- [ ] **P9-05 - Tổng hợp quá trình làm việc.** Task/sprint, quyết định kỹ thuật, commit/PR/review và phần bàn giao thật. Đánh giá đóng góp qua nội dung công việc, không chỉ số commit; không tái tạo lịch sử giả.
- [ ] **P9-06 - Hoàn thành peer evaluation.** Ghi nhận đánh giá thực tế theo yêu cầu môn học, không thay bằng bảng phân công hay xác nhận tự động.
- [ ] **P9-07 - Soạn kịch bản bảo vệ.** Dẫn một yêu cầu xuyên suốt: UR → BR → schema và khoảng trống → test sinh/test bổ sung → kết quả → finding → replay → kết luận.
- [ ] **P9-08 - Chuẩn bị demo ngắn.** Ba luồng nghiệp vụ, một lần automation, một finding và reproducer; giải thích report thật. Campaign dài dùng artifact đã chạy, không phụ thuộc hoàn thành trong giờ báo cáo.
- [ ] **P9-09 - Tổng duyệt và nộp.** Kiểm tra link, lệnh, screenshot, thời gian demo và bản dự phòng; báo cáo nộp trước ngày bảo vệ một tuần khi lịch chính thức có.

### Câu hỏi cần tự trả lời được

1. Vì sao chọn hai collection và 10 operation; phần nào của Directus chưa được kiểm thử?
2. Yêu cầu người dùng khác OpenAPI như thế nào; ai quyết định expected result?
3. Schema thiếu min/max/enum gây ảnh hưởng gì tới sinh positive/negative test?
4. Vì sao Reader schema không có operation chưa đủ chứng minh không thể gọi API đó?
5. Vì sao 403 có thể là kết quả đúng; vì sao DELETE 204 lại gây contract failure?
6. Có bao nhiêu request, check failure, nhóm finding và defect xác nhận; chúng khác nhau thế nào?
7. Raw/guided khác những gì; thí nghiệm cho phép kết luận đến đâu?
8. Pairwise phủ mô hình nào, tiết kiệm bao nhiêu theo số đo và có thể bỏ sót gì?
9. Chi phí đã đo bao gồm thiết kế/triage hay chỉ thời gian runner?
10. Seed có đủ tái lập không; stateful replay cần gì ngoài request cuối?
11. Finding đại diện có nguyên nhân/giả thuyết và bằng chứng gì; finding nào còn mở, ảnh hưởng thế nào?
12. Người khác chạy script local/Docker, đọc report/exit code và tái hiện finding bằng README/gói evidence như thế nào?

### Đầu ra và tiêu chí hoàn thành

- Báo cáo cuối kỳ, slide/demo, README và gói evidence thống nhất.
- Có bằng chứng kiểm tra khả năng chạy lại ở mức thực tế đã thực hiện.
- Có peer evaluation và lịch sử đóng góp thật.
- Khi giảng viên chọn một kết luận bất kỳ, nhóm chỉ ra được đặc tả, test và evidence liên quan.

---

## 4. Checklist bắt đầu ngay và cách giảm phạm vi khi thiếu thời gian

### Việc nên làm trong lượt tiếp theo

- [ ] Lập evidence index và chọn checkpoint demo trước 20/10.
- [ ] Mở bảng UR/BR từ actor, fixture, policy và scenario đã có; ghi các expected chưa rõ.
- [ ] Lập bảng ba khoảng trống schema đã xác định: title/status/score.
- [ ] Ánh xạ test hiện tại, chỉ rõ thiếu biên nào và test nào đã có trong smoke.
- [ ] Chọn aggregate, một response contract mismatch và lỗi harness để làm hồ sơ đại diện.
- [ ] Lập danh sách dependency ngoài repo cần xử lý khi triển khai Phase 4.

### Nếu thiếu thời gian

Ưu tiên giữ đầy đủ yêu cầu A-H, đặc tả/truy vết, bộ test rủi ro cao, automation chạy lại được, finding có phân tích và gói evidence. Với phần tối ưu chi phí, chọn một mô hình query nhỏ có đối chứng đủ rõ trước khi mở rộng nhiều thí nghiệm. Phase 7 đã loại khỏi phạm vi: không cần dành thời gian triển khai CI/CD. Lưu artifact và chạy lại bằng local/Docker vẫn phải bảo đảm.

Có thể giảm thí nghiệm phụ tách riêng guidance/stateful, số mô hình pairwise hoặc phân tích sâu thêm nhiều candidate. Không giảm bằng cách bỏ test quyền quan trọng, bỏ qua restore failure, nới assertion, che exit code hay viết kết luận khi chưa có số liệu. Mọi thay đổi budget/ngưỡng phải ghi nhận trước lượt chạy tương ứng.

## 5. Mẫu theo dõi task và quyết định

Không phân công cá nhân trong tài liệu này. Khi đưa vào công cụ quản lý dự án, bổ sung người phụ trách theo cách nhóm thống nhất.

| Task ID | Phase | Trạng thái | Điều kiện bắt đầu/phụ thuộc | Đầu ra thực tế | Bằng chứng nghiệm thu | Vấn đề/quyết định còn mở |
|---|---|---|---|---|---|---|
| P0-01 đến P0-06 | 0 | Hoàn thành kiểm kê | Tài liệu/artifact hiện có | Báo cáo, evidence index, bộ demo, decision backlog và checkpoint tệp | [Kết quả Phase 0](00-hien-trang-va-baseline.md) | Live runtime chưa xác minh; quyết định mới giữ mở theo backlog |
| P1-01 đến P1-08 | 1 | Hoàn thành đặc tả và review tĩnh | Kết quả Phase 0, nguồn lab và lựa chọn bám baseline của người dùng | Đặc tả UR/BR/AC, rủi ro, review, truy vết và source đúng commit | [Review Phase 1](01-review-dac-ta.md) | Q-01 đến Q-07 còn phần kỹ thuật OPEN chuyển Phase 2–4; không nghiệm thu runtime |
| P2-01 đến P2-09 | 2 | Hoàn thành review và thiết kế | Đặc tả v0.2, bốn snapshot actor và artifact có nguồn | Inventory, ma trận 26 BR/6 TR, bảy case thật, diff/overlay, thiết kế stateful/quyền | [Review Phase 2](02-danh-gia-openapi-va-sinh-test.md) | VFY-01…05 bàn giao Phase 3–4; chưa sửa harness/chạy test mới |
| P3-01 đến P3-09 | 3 | Hoàn thành thiết kế và review tĩnh | Đặc tả và khoảng trống schema Phase 1–2 | Catalog257 dòng,48 phân vùng,34 biên,69 luật quyền,3 chuỗi; pairwise9/36; oracle/entry/exit | [Thiết kế Phase 3](03-thiet-ke-test-va-coverage.md), [review](03-review-thiet-ke.md) | Expected conditional/open chuyển Phase 4; execution toàn bộ NOT_RUN; chưa có chi phí runtime |
| P5-01…05, P5-08 | 5 | Chưa bắt đầu bản rút gọn | Report/reproducer và source phù hợp baseline từ Phase 4/lịch sử | Dự kiến một báo cáo finding/RCA | Chưa có đầu ra Phase 5 mới | P5-06 gộp P5-02; P5-07 bỏ yêu cầu riêng |
| P7-01…09 | 7 | Loại khỏi phạm vi theo quyết định | Không còn phụ thuộc | Không yêu cầu workflow/report CI | [Quyết định thu gọn](dieu-chinh-pham-vi-phase5-phase7.md) | Không phải hoàn thành hoặc PASS |

Trạng thái task: `Chưa bắt đầu / Đang làm / Chờ điều kiện / Chờ nghiệm thu / Hoàn thành / Gộp vào task khác / Loại khỏi phạm vi`. Mỗi task kế thừa điều kiện và đầu ra của phase; nếu có khác biệt, ghi trực tiếp ở dòng task. Task bị chờ phải nêu nguyên nhân và việc độc lập có thể tiếp tục.

Quyết định ảnh hưởng baseline, policy, fixture, scope, interface hoặc cách xử lý failure cần ghi: vấn đề, lựa chọn, căn cứ, tác động, trạng thái chốt và thời điểm áp dụng. Không coi đề xuất trong kế hoạch là quyết định đã được thông qua.

## 6. Nguồn hiện có để thực hiện

### Yêu cầu và kiến thức môn học

- [Yêu cầu môn học](../yeu_cau.pdf): phần bắt buộc, A-H, đầu ra K05, mốc giữa kỳ/cuối kỳ và peer evaluation.
- [Bài giảng nhập môn](../slide_bai_giang/slide1.pdf): mục tiêu, chi phí, quy trình và chất lượng test case; tham khảo trang PDF 23-27.
- [Bài giảng hộp đen](../slide_bai_giang/2-kiem-thu-hop-den-0.pdf): phân vùng, biên, bảng quyết định và pairwise; tham khảo trang PDF 13-19, 28-30, 33-45, từ 46 trở đi.
- [Bài giảng kiểm thử tĩnh](../slide_bai_giang/lms_presentation.pdf): phân tích yêu cầu/user story/spec, review và checklist.
- [Bài giảng hộp trắng](../slide_bai_giang/kiem_thu-hop-trang.pdf): hỗ trợ đọc luồng/nhánh khi phân tích root cause; không dùng thay số liệu coverage chưa đo.

### Nền tảng của dự án

- [README](../../README.md), [manifest baseline](../../manifest/baseline.yaml), [kiến trúc](../architecture.md).
- [Ma trận test](../test-matrix.md), [ma trận quyền](../permissions.md), [truy vết A-H](../traceability.md).
- [Báo cáo thiết kế kịch bản](../Bao_cao_Thiet_ke_kich_ban_kiem_thu.md), [báo cáo giữa kỳ](../Bao_cao_giua_ky_R06_K05.md).
- [Kết quả 12/10](../phan2/04-ket-qua-kiem-thu.md), [phân tích lỗi/root cause](../phan2/05-phan-tich-loi-va-root-cause.md), [replay cases](../replay-cases.md).
- [Bằng chứng Windows 13/10](../../evidence/windows-recheck-2026-10-13.md), [triage lịch sử](../../evidence/failure-triage-v2-2026-10-11.md).
- [Harness](../../lab.sh), [thành phần lab](../../scripts/lab-components.sh), [invariant](../../scripts/invariants.py).

Các nguồn lịch sử giữ nguyên giá trị tại thời điểm ghi nhận. Khi triển khai kế hoạch, phải kiểm tra trạng thái mới trước khi dùng chúng để khẳng định hiện trạng.
