# Rà soát hình và bảng trong báo cáo R06 K05

Đối tượng: `BaoCaoNhom11_hoan_thien.docx` ở thư mục gốc workspace. Phạm vi kiểm kê: 9 hình và 28 bảng. Đây là đối chiếu nội dung báo cáo với mã, cấu hình và bằng chứng đã lưu; không phải một lượt kiểm thử mới hay xác nhận dịch vụ hiện đang hoạt động.

**Kết luận:** mô hình dữ liệu, quyền, dữ liệu mẫu, 13 ca đại diện, số liệu sáu seed và thí nghiệm giảm chi phí đều có căn cứ phù hợp. Cần sửa cách biểu diễn runner ở Hình 4 và làm rõ nhãn kết thúc campaign trong mục 7.5. Có một khác biệt ký tự cần chỉnh trong bảng tham số truy vấn. Các hình là sơ đồ minh họa, không phải ảnh chụp bằng chứng thực thi.

## Những điểm cần chỉnh

### 1. Hình 4 chưa phân biệt service runner và container thực thi kiểm thử

Hình đang nối `Service runner: image Schemathesis 4.30.0` tới Directus và tệp kết quả. [compose.yaml](../../compose.yaml) có service runner, nhưng lệnh của service này chỉ giữ container chờ bằng vòng lặp sleep; healthcheck kiểm phiên bản Schemathesis.

Các hàm chạy campaign và bộ ca thiết kế trong [lab-components.sh](../../scripts/lab-components.sh) dùng `docker_run --rm` để tạo container tạm từ image Schemathesis. Container này tham gia mạng lab, nhận đặc tả/mã kiểm thử và gắn thư mục kết quả từ máy chủ. Bởi vậy, không nên dùng service runner thường trực để đại diện chính xác cho nơi thực thi các lượt này.

Đề xuất sửa nút thành **“Container kiểm thử tạm thời dùng image Schemathesis 4.30.0”**; ghi mũi tên điều phối là tạo container, mũi tên lưu kết quả là ghi vào thư mục dùng chung với máy chủ. Nếu giữ service runner trong hình, tách nó thành thành phần chờ/kiểm tra công cụ. Các thành phần Directus, PostgreSQL, cổng kết nối, mạng và volume còn lại khớp cấu hình.

### 2. Mục 7.5 dùng INCOMPLETE nhưng chưa giải thích quan hệ với trạng thái gốc

Sáu lượt đều có `stop_reason=max_time`, đã thử đủ 10 operation, runner exit 1 và restore exit 0. Tuy nhiên, các tệp `campaign-summary.json` ghi `status=failed`; báo cáo Schemathesis ghi `complete=true`. Vì vậy, câu “giữ trạng thái INCOMPLETE” có thể khiến người đọc tưởng đó là trường trạng thái nguyên văn do công cụ xuất.

Có thể viết: **“Cả sáu lượt đã thử đủ 10 thao tác và kết thúc do hết ngân sách thời gian. Nhóm dùng nhãn INCOMPLETE để nhấn mạnh giới hạn này; kết quả công cụ vẫn ghi các phép kiểm thất bại, không được xem là PASS.”** Nếu cần đối chiếu trạng thái kỹ thuật, giữ một ghi chú riêng rằng trạng thái runner là failed và trường complete của công cụ không chứng minh đã kiểm hết hành vi hệ thống. Không đổi các lượt này thành PASS.

Cột **“HTTP ghi nhận”** đúng số liệu, nhưng nên chú thích là số tương tác đã lưu trong recorder, loại trùng theo mã ca và timestamp; không phải tổng mọi yêu cầu trên mạng, bao gồm đăng nhập, chuẩn bị, khôi phục và yêu cầu chưa kịp lưu khi hết giờ.

### 3. Bảng các yếu tố ở mục 7.7 dùng dấu trừ khác tham số API

Báo cáo đang ghi `−score,id` bằng dấu trừ toán học Unicode. Mô hình và chương trình dùng `-score,id` bằng dấu gạch nối ASCII. Ý nghĩa mô tả vẫn đúng, nhưng nên đổi sang **`-score,id`** để người đọc có thể sao chép đúng tham số API.

## Đối chiếu từng hình

| Hình | Nội dung | Kết quả | Căn cứ và lưu ý |
|---|---|---|---|
| 1 | Vai trò và quyền | Khớp ở mức mô hình quyền | Editor CRUD hai bảng; Reader đọc chuyên mục và bài published ở trường cho phép; không có trường ghi được cho Reader; Anonymous không được cấp quyền hai bảng. Nguồn: cấu hình policy trong lab-components.sh, kết quả S4–S6 và TC08. Hình mô tả quy tắc, không khẳng định đã thử mọi tổ hợp quyền. |
| 2 | Quan hệ chuyên mục và bài viết | Khớp | Hai bảng, ID integer tự tăng, category là khóa ngoại nullable, quan hệ một chuyên mục với 0..n bài, một bài với 0..1 chuyên mục; xóa chuyên mục dùng SET NULL. Các trường còn lại khớp khai báo schema. |
| 3 | Luồng nghiệp vụ và đối chiếu dữ liệu | Khớp ở mức sơ đồ logic | CRUD, query, quyền và xóa chuyên mục có tham chiếu đều có thiết kế/mã/bằng chứng. Phần lời đã ghi luồng thứ tư thuộc bộ mở rộng. Hình không phải sơ đồ kết nối vật lý; các mũi tên tới PostgreSQL không có nghĩa người dùng được truy cập DB trực tiếp. Có thể thêm nhãn “các thao tác đi qua Directus” để tránh hiểu nhầm. |
| 4 | Kiến trúc triển khai | Cần chỉnh | Đúng Directus 12.5.0, Schemathesis 4.30.0, PostgreSQL 16, loopback 8055, database:5432 và volume r06-k05_db_data. Cần phân biệt service runner chờ với container tạm thực thi, như mục trên. |
| 5 | Trình tự tạo và đọc lại bài | Khớp | Luồng gửi POST, kiểm quyền/dữ liệu, lưu DB, nhận HTTP 200 chứa ID, GET lại và so với đầu vào phù hợp S1 và ca thiết kế. Đây là trình tự trao đổi chính, không thể hiện mọi truy vấn SQL nội bộ. |
| 6 | Chuẩn bị fixture và kết quả mong đợi | Khớp ở mức quy trình | Kiểm/tạo schema tương thích, nạp/xác minh dữ liệu, lưu ID động, kiểm điều kiện và xuất đặc tả theo actor đều có mã tương ứng. Thứ tự trong hình là mô hình chuẩn bị, không phải bản ghi từng lệnh API nội bộ. |
| 7 | Sinh và kiểm yêu cầu từ OpenAPI | Khớp ở mức tóm tắt | Hai cấu hình giới hạn 10 operation, guided thêm ví dụ/ID/liên kết, công cụ sinh request và lưu JSON/NDJSON. Guided còn bật pha stateful, trong khi raw không bật; phần lời 4.5 đã nêu khác biệt này. Bốn loại kiểm ghi trong hình là các kiểm chính, không phải toàn bộ danh sách bảy check trong lệnh campaign. |
| 8 | Một ca kiểm thử và dọn dữ liệu | Khớp với bộ ca thiết kế | Runner.run_case kiểm snapshot, thực thi, ghi verdict, cleanup trong finally và lưu case; run_selected dừng khi cleanup lỗi hoặc blocked/incomplete. Có thể đổi chú thích thành “Quy trình một ca trong bộ ca thiết kế” để tránh áp dụng máy móc cho mọi request Schemathesis hoặc mọi scenario shell. |
| 9 | 36 tổ hợp và 9 ca pairwise | Khớp | Đã tính lại từ query-cost-model-v1.json: 36 ca đầy đủ, 9 ca được chọn; hai tập bao phủ cùng 37 cặp. Chỉ là bao phủ cặp trong mô hình hữu hạn, không phải bao phủ mã hay bảo đảm khả năng tìm mọi lỗi tương đương. |

## Đối chiếu từng bảng

Số B01–B28 dưới đây là mã kiểm kê của lần rà soát này, không phải số hiệu đã in trong Word.

| Mã | Vị trí / nội dung | Kết quả đối chiếu |
|---|---|---|
| B01 | 1.4 — Phạm vi API | Khớp: hai collection × năm cặp phương thức/đường dẫn = 10 operation. Đây là phạm vi chọn, không phải tổng mọi endpoint mà Directus xuất. |
| B02 | 2.1 — Vai trò | Khớp policy fixture và các ca quyền được trích. |
| B03 | 2.2 — Quy tắc dữ liệu | Khớp schema cấu hình: name 80, title 120, status draft/published mặc định draft, score integer 0–5, thời điểm/JSON/category nullable và SET NULL. |
| B04 | 2.5 — Module và thư viện | Khớp cấu trúc Directus và dependency Express, Knex, Joi, pg. Đây là bản tóm tắt chức năng; không phải danh sách toàn bộ dependency hoặc dịch vụ Docker. |
| B05 | 3.1 — Môi trường | Khớp manifest và target verification. PostgreSQL 16.15 được xác nhận trong database-oracle.json của lượt scenario. Không suy cấu hình phần cứng hoặc runtime hiện tại từ bảng lịch sử. |
| B06 | 3.2 — Dữ liệu mẫu | Khớp fixture và baseline: ba chuyên mục, mỗi chuyên mục hai draft/hai published; tổng 12 bài, sáu bài published. |
| B07 | 3.4 — Ba luồng đã chạy | Khớp scenario-report.json: S1 PASS với xóa 204, S2 trả [3,4,7,8,11,12], S3 hai trang, S4–S6 trả 403. |
| B08 | 4.2 — Các bước áp dụng | Khớp quy trình xuất đặc tả, giới hạn operation, sinh/kiểm và lưu bằng chứng. Phân tích nguyên nhân là bước đọc và đối chiếu sau chạy, không phải công cụ tự xác nhận mọi nguyên nhân. |
| B09 | 4.3 — Tiêu chí đánh giá | Phù hợp các kiểm nền tảng và phép kiểm nghiệp vụ bổ sung. Bảng là tiêu chí chính, không phải danh sách đầy đủ bảy check campaign. |
| B10 | 5.1 — Chọn bộ đại diện | Khớp sáu scenario và bảy ID trong COURSE_CASE_IDS; phân nhóm TC01–TC13 nhất quán. |
| B11 | TC01 | Khớp S1: tạo score=1, sửa riêng thành 5, kiểm giữ dữ liệu, xóa và đọc lại nhận 403/FORBIDDEN. |
| B12 | TC02 | Khớp S2: sáu bài published từ fixture, fields id/title/status và limit=-1. |
| B13 | TC03 | Khớp S3 và DB oracle: sort title,id, hai offset 0 và 3; thứ tự mong đợi xuất phát fixture/map và DB collation độc lập. |
| B14 | TC04 | Khớp S4: kiểm đối chứng trước, đọc draft bằng trường công khai, nhận 403. |
| B15 | TC05 | Khớp S5, bao gồm giới hạn đã ghi rõ: source chấp nhận bị từ chối hoặc không trả trường kín; bằng chứng lịch sử là 403. Không được diễn giải PASS thành chứng minh code luôn bắt buộc 403. |
| B16 | TC06 | Khớp S6: Reader sửa score bị từ chối và Editor đọc lại toàn bộ trường mục tiêu không đổi. |
| B17 | TC07 | Khớp P3-ST-01: POST/GET/PATCH/GET/DELETE/GET; mã trả 200/204/403 phù hợp từng bước, cleanup passed. |
| B18 | TC08 | Khớp P3-AUTHZ-DR-047: Editor control 200, Anonymous GET 403, authorization passed, cleanup passed. |
| B19 | 5.5 — TC09–TC12 | Khớp bốn ca score POST: −1 và 6 bị 400; 0 và 5 tạo/đọc lại đúng; cả bốn passed và cleanup passed. |
| B20 | TC13 | Khớp P3-CONTRACT-QA_ARTICLES-OBJECT: POST object score=3 trả 200; đọc lại đúng; business passed, contract failed, cleanup passed. OpenAPI gốc mô tả data array. |
| B21 | 6.1 — Mã tự động hóa | Các tệp tồn tại và nhiệm vụ khớp. Lưu ý cách triển khai runner thực tế như nhận xét Hình 4. |
| B22 | 7.2 — Kết quả 13 ca | Khớp 12 PASS, 1 FAIL theo ID từ các lượt nguồn. Báo cáo đã ghi đây là kết quả tổng hợp, chưa phải một lượt mới chạy chung 13 ca. |
| B23 | 7.3 — So sánh phản hồi và đặc tả | Khớp: tạo bài thành công HTTP 200 nhưng data object khác array của đặc tả. Không biến sai lệch hợp đồng thành kết luận mất dữ liệu. |
| B24 | 7.5 — Sáu seed raw/guided | Tất cả số liệu khớp. Đã đọc lại generated/unique_failures/errored và đếm tương tác recorder từ sáu tệp NDJSON. Cần chú thích định nghĩa HTTP ghi nhận và nhãn INCOMPLETE như phần nhận xét. |
| B25 | 7.6 — Năm nhóm bất thường | Khớp hồ sơ nghiệm thu Phase 8: aggregate, POST shape, DELETE 204, export media type, projection. Không lấy riêng register Phase 5 bốn nhóm để bác số năm, vì projection được bổ sung ở Phase 8. Các vấn đề còn OPEN; chưa phải năm lỗi nghiệp vụ đã sửa. |
| B26 | 7.7 — Các yếu tố truy vấn | Giá trị và số mức khớp mô hình; đổi ký tự −score,id thành -score,id để đúng tham số máy đọc. |
| B27 | 7.7 — Chi phí 36 so với 9 | Khớp CSV của sáu lượt và phép tính trung vị theo cặp: 75,00% số truy vấn mục tiêu; 34,18% tổng HTTP; 75,04% thời gian mục tiêu; 19,54% thời gian toàn lệnh. Các trung vị 7,200/1,797 và 26,893/21,638 giây khớp sau làm tròn. |
| B28 | 8.4 — Nguồn bằng chứng | Các đường dẫn được trích đều tồn tại. Nên bổ sung ánh xạ mã nguồn của TC09–TC13 tại bảng này nếu cần người nhận tra tệp mà không xem code; nội dung ca và kết quả tự thân đã được giải thích trong báo cáo. |

## Các số liệu đã xác minh lại

| Cấu hình | Seed | Ca sinh | Tương tác recorder không trùng | Check failure phân biệt | Ca lỗi thực thi |
|---|---:|---:|---:|---:|---:|
| Raw | 101 | 59 | 59 | 20 | 0 |
| Raw | 202 | 65 | 65 | 18 | 0 |
| Raw | 303 | 51 | 51 | 19 | 0 |
| Guided | 101 | 5770 | 5659 | 63 | 111 |
| Guided | 202 | 5864 | 5688 | 65 | 176 |
| Guided | 303 | 5894 | 5694 | 62 | 200 |

Số tương tác trên được tính từ recorder trong sự kiện ScenarioFinished, loại trùng bằng cặp mã ca/timestamp. Số này không nhất thiết bằng tổng hits trong operation-inventory, vì hai bộ đếm không có cùng phạm vi. Không sửa bảng báo cáo chỉ vì cộng hits ra số khác.

## Nguồn kiểm tra chính

- [Compose](../../compose.yaml), [manifest](../../manifest/baseline.yaml), [mã chuẩn bị và chạy](../../scripts/lab-components.sh), [bộ ca thiết kế](../../scripts/designed_cases.py), [invariant](../../scripts/invariants.py).
- [Mô hình fixture](../../scripts/data/fixture-oracle.json), [mô hình truy vấn](../../scripts/data/query-cost-model-v1.json), [giao thức thí nghiệm](../../scripts/data/query-cost-protocol-v1.json).
- [Sáu scenario](../../artifacts/runs/p8-20261018-scenarios/scenario-report.json), [DB oracle](../../artifacts/runs/p8-20261018-scenarios/database-oracle.json), [bộ ca thiết kế nguồn](../../artifacts/runs/p8-20261018-assertable/designed-report.json), [TC08 nguồn](../../artifacts/runs/p8-20261018-short-r2/case-P3-AUTHZ-DR-047.json).
- Campaign raw `artifacts/runs/20261011T085034Z-76481` và guided `artifacts/runs/20261011T095117Z-89079`, các báo cáo/metrics/NDJSON của seed 101, 202, 303.
- [Số đo chi phí](tai-lieu-bo-tro/phase6-20261018/query-trials.csv), [mức giảm từng cặp](tai-lieu-bo-tro/phase6-20261018/paired-reductions.csv), [phân tích chi phí](tai-lieu-bo-tro/phase6-20261018/query-analysis.json), [hồ sơ nghiệm thu](08-bao-cao-nghiem-thu.md).

Lần rà soát này không sửa Word, không sửa chương trình, không chạy campaign và không thay dữ liệu gốc.
