# Phase 6 — Thí nghiệm tối ưu chi phí kiểm thử R06 + K05

**Hoàn thành ngày 18/10/2026**, trong phạm vi thí nghiệm query mới, phân tích lại raw/guided lịch sử và đánh giá replay đã đo ở Phase 4. Phase 8–9 chưa thực hiện; Phase 7 vẫn loại khỏi phạm vi. Không đổi Directus, policy, fixture, schema gốc hoặc ngân sách campaign chính.

Kết quả chính: với miền query đã chốt, **9 ca pairwise thay cho 36 ca giảm 75% request mục tiêu**, phủ đủ **37/37 cặp giá trị**. Qua ba cặp đo, trung vị mức giảm **thời gian toàn lệnh là 19,54%**, tổng request của toàn lượt giảm **34,18%**. Cả hai tập đều PASS; chưa có bằng chứng chúng tìm lỗi hiệu quả như nhau vì thí nghiệm này không phát hiện lỗi mới.

## 1. Câu hỏi, phạm vi chi phí và bằng chứng

| Câu hỏi | Cách thực hiện | Điều có thể kết luận |
|---|---|---|
| Pairwise giảm bao nhiêu chi phí của query hữu hạn? | Chạy mới 3 cặp 36 ca/9 ca, cùng oracle và bảo vệ trạng thái | Số ca, request, thời gian trong cấu hình đã đo |
| Raw/guided khác nhau thế nào với cùng ngân sách? | Audit và phân tích lại hai campaign lịch sử, cùng ba seed | So sánh mô tả hai chiến lược tổng thể, kèm giới hạn provenance |
| Replay giúp gì cho lỗi đã biết? | Tái sử dụng run Phase 4 có thời gian và native check tái hiện | Chi phí xác minh một hiện tượng đã biết; không đo lại sức khám phá |

Chi phí đo được gồm request HTTP tới SUT, thời gian phần query, setup/verification trong Python, toàn runner và toàn lệnh PowerShell. Chi phí thiết kế, triển khai, đọc tài liệu, triage, bảo trì và công của con người **chưa được đo**. Không đổi thời gian phiên AI thành giờ công hoặc tiền; không tính chi phí/defect khi thiếu số defect đã xác nhận.

Thiết kế được lưu lúc `2026-10-18T10:07:57Z`, trước lượt đo đầu tiên: [protocol-v1.json](tai-lieu-bo-tro/phase6-20261018/protocol-v1.json). [Source freeze](tai-lieu-bo-tro/phase6-20261018/measurement-source-freeze.json) khóa 20 tệp code/data/schema/map và launcher thí nghiệm. Sáu lượt dùng cùng nội dung đã khóa; không sửa code giữa các lượt để chọn kết quả đẹp. Các sửa đổi chưa commit được lưu trong gói source và manifest; HEAD là `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, working tree dirty.

## 2. Thí nghiệm query mới: mô hình và phương pháp

### 2.1. Miền hữu hạn QRY-PW-v1

Editor gọi `GET /items/qa_articles`, trên fixture 3 category/12 article, 6 draft/6 published. Dùng ID thật từ map, không hard-code ID trong case.

| Yếu tố | Miền giá trị |
|---|---|
| Filter | Không filter; draft; published |
| Sort | `id`; `title,id`; `-score,id` |
| Fields | `id,title`; `id,title,status,score` |
| Phân trang | `limit=3&offset=3`; `limit=3&page=2` |

Có `3 × 3 × 2 × 2 = 36` tổ hợp khả thi; không loại tổ hợp nào. “Vét cạn” chỉ nói về miền này. Hai cách phân trang chủ ý tương đương về vị trí dữ liệu nhưng đi qua hai tham số API khác nhau; 36 tổ hợp không đồng nghĩa 36 kết quả nghiệp vụ khác nhau.

Tái sử dụng [36 ca Phase 3](03-query-exhaustive-36.csv) và [9 ca pairwise](03-query-pairwise.csv), ID `P3-PW-01,05,12,13,18,23,28,31,33`. Số cặp khả thi là `9+6+6+6+6+4=37`. Tập 9 phủ đủ 37 cặp, thiếu 0: [danh sách đối chiếu](tai-lieu-bo-tro/phase6-20261018/pair-coverage.json). Riêng cặp filter–sort đã cần ít nhất 9 ca, nên 9 đạt cận dưới cho mô hình này; không suy thành tối ưu mọi mô hình.

Runner kiểm tra đủ 36 tổ hợp duy nhất, query khớp factor và catalog gốc, đủ 9 ca/37 cặp **trước đăng nhập**. Đây là kỹ thuật thiết kế bổ trợ K05, không chuyển đề tài sang K06.

### 2.2. Baseline và oracle chung

| Thành phần | Cấu hình sử dụng |
|---|---|
| Directus | 12.5.0, source `4f77933bf9551cac6b289576078783e189b8f4e3` |
| Schemathesis runner | 4.30.0, dùng Python trong image đã pin |
| PostgreSQL | 16; preflight ghi phiên bản/collation và thứ tự title từ SQL |
| Runtime profile | `phase6-20261018`; Compose project `r06-k05` |
| Actor mục tiêu | Editor; Admin chỉ kiểm soát cấu hình/snapshot/restore |
| Ngân sách | 1 worker; 5 request/s trong Python; timeout 10 giây; cap runner 120 giây |
| Cache | Giữ cấu hình baseline; không flush hoặc warmup thêm; preflight chung đã đọc fixture |

Image digest đầy đủ nằm trong metadata của từng run và [evidence chọn lọc](tai-lieu-bo-tro/phase6-20261018/evidence-index.json). Doctor/seed/export PASS; thời gian metadata lần lượt 5/16/8 giây, được tính là chuẩn bị dùng chung, **không cộng lặp vào mỗi trial**. [Chi tiết chuẩn bị/kiểm tra](tai-lieu-bo-tro/phase6-20261018/preparation-and-validation.json).

Code [cost_query.py](../../scripts/cost_query.py) tái sử dụng `Lab`, `Api`, `Runner.preflight`, `expected_query` và `assert_query` của Phase 4. Expected dựa vào seed specification, map ID và thứ tự title được SQL xác nhận độc lập; so đầy đủ giá trị, ID, thứ tự và projection. Không lấy actual vừa nhận làm expected. Oracle thử nghiệm này kiểm tra HTTP 2xx, mảng dữ liệu và nghiệp vụ hữu hạn; **không tuyên bố đã chạy toàn bộ native contract checks của Schemathesis cho 135 request**.

Cả hai tập dùng cùng preflight, snapshot trước, so toàn bộ hai collection sau batch và restore chung cuối lượt. Request mục tiêu chỉ GET; **toàn job vẫn có 15 PATCH phục vụ restore**, áp dụng như nhau cho hai tập. Có khóa mutation toàn project; không chạy song song hoặc reset DB.

Thứ tự định trước là full→pairwise, pairwise→full, full→pairwise. Không ngẫu nhiên hóa, chỉ ba cặp trên một máy; đây là thống kê mô tả. Schema/map đầu vào và trạng thái fixture ban đầu giống nhau giữa sáu lượt, được analyzer kiểm tra. Không có lượt lỗi bị loại hoặc phải chạy lại.

### 2.3. Định nghĩa phép đo

- **Request mục tiêu:** số lần thực sự gọi opener ở stage target, kể cả khi lỗi HTTP. Chỉ số này không lấy từ số case thiết kế.
- **Thời gian target:** từ trước query đầu tới hết oracle query cuối, gồm chờ rate limit, truyền/đọc response, decode, ghi artifact và assertion. Không phải latency thuần của server.
- **Tổng request toàn lượt:** meter Python + meter Bash; tính cả đăng nhập không ghi response, snapshot, preflight, verification và restore. Meter chỉ lưu method/path/stage/status an toàn, không lưu credential/header/body đăng nhập. Bash đếm attempt, không suy tất cả response là 2xx chỉ từ counter.
- **Thời gian toàn lệnh:** Stopwatch quanh launcher PowerShell, gồm validation, Docker startup, setup, Python, restore và hoàn tất metadata. Lưu riêng `metadata.duration_seconds` có độ phân giải giây; không trộn nó vào bảng Stopwatch.
- Python giới hạn 5/s; lifecycle Bash giữ timeout và cơ chế hiện có, không áp thêm 5/s vào restore. Một lần gọi HTTP không đồng nghĩa một thao tác SQL.

## 3. Kết quả mới và cách tính

Đường dẫn run gốc có dạng `artifacts/runs/p6-query-20261018-r<lượt>-all|pw/`. Report/counter/timing được sao chọn lọc sang thư mục evidence hỗ trợ. [CSV tất cả trial](tai-lieu-bo-tro/phase6-20261018/query-trials.csv), [tỷ lệ theo cặp](tai-lieu-bo-tro/phase6-20261018/paired-reductions.csv), [tổng hợp JSON](tai-lieu-bo-tro/phase6-20261018/query-analysis.json).

| Lượt/thứ tự | Tập | Ca/request target | Target (giây) | Python HTTP | Bash HTTP | Tổng SUT HTTP | Toàn lệnh (giây) |
|---|---|---:|---:|---:|---:|---:|---:|
| 1, đầu | 36 ca | 36 | 7,197 | 50 | 29 | 79 | 26,893 |
| 1, sau | Pairwise | 9 | 1,794 | 23 | 29 | 52 | 21,638 |
| 2, đầu | Pairwise | 9 | 1,797 | 23 | 29 | 52 | 21,645 |
| 2, sau | 36 ca | 36 | 7,200 | 50 | 29 | 79 | 26,827 |
| 3, đầu | 36 ca | 36 | 7,200 | 50 | 29 | 79 | 27,200 |
| 3, sau | Pairwise | 9 | 1,798 | 23 | 29 | 52 | 21,438 |

Sáu lượt đều PASS, target toàn HTTP 200, oracle đúng, 37/37 cặp được thực thi và PASS mỗi lượt, state verification PASS, runner/restore exit 0. Tổng cộng **135 request target**, không phải 135 case mới: `3×36+3×9=135`, gồm **36 ID thiết kế khác nhau**.

| Chỉ số | 36 ca: trung vị [min–max] | Pairwise: trung vị [min–max] |
|---|---:|---:|
| Target (giây) | 7,200 [7,197–7,200] | 1,797 [1,794–1,798] |
| Toàn Python runner (giây) | 10,743 [10,739–10,744] | 5,343 [5,339–5,345] |
| Toàn lệnh (giây) | 26,893 [26,827–27,200] | 21,638 [21,438–21,645] |
| Tổng thời gian API target, không tính pacing (giây) | 0,196 [0,194–0,197] | 0,048 [0,046–0,049] |

Mỗi lượt có **43 request ngoài target**: 3 đăng nhập Python + 9 preflight + 2 verification + 29 lifecycle Bash. Trong 29 Bash có 6 đăng nhập, 2 snapshot đầu, 6 GET restore và 15 PATCH restore. Cùng khoản cố định này giải thích vì sao giảm ca không làm tổng chi phí giảm tương ứng.

Áp dụng `giảm % = (1 - pairwise/full) × 100` trong **từng cặp**, rồi lấy trung vị:

| Chỉ số tiết kiệm | Trung vị | Min–max theo 3 cặp |
|---|---:|---:|
| Số ca/request target | **75,00%** | 75,00–75,00% |
| Thời gian target | **75,04%** | 75,03–75,07% |
| Tổng request toàn lượt | **34,18%** | 34,18–34,18% |
| Thời gian toàn lệnh | **19,54%** | 19,31–21,18% |

Không có finding mới trong mô hình này. Chưa đo fault injection/mutation hoặc lỗi tương tác ba/bốn yếu tố; không thể nói pairwise giữ 100% khả năng tìm lỗi, bao phủ toàn API hoặc thay bộ quyền/biên/stateful. Giữ nguyên các ca này trong suite riêng. Phần lớn target wall là chờ tốc độ 5/s; không dùng kết quả để tuyên bố năng lực tải/throughput của Directus.

## 4. Raw/guided: tái sử dụng đối chứng lịch sử

Chọn **raw `20261011T085034Z-76481`** và **guided `20261011T095117Z-89079`**, ba seed 101/202/303. Không chạy lại sáu campaign 20 phút chỉ để có bảng báo cáo. [Audit điều kiện chọn](tai-lieu-bo-tro/phase6-20261018/historical-eligibility.json), [CSV sáu seed](tai-lieu-bo-tro/phase6-20261018/historical-raw-guided.csv), [audit chi tiết/schema coverage/status/accepted](tai-lieu-bo-tro/phase6-20261018/historical-raw-guided-audit.json).

Metadata ghi cùng image digest, fixture v2, Editor, 10 operation, 1 worker, 5/s, timeout 10 giây, max-examples 100, max-time 1.200 giây. Cùng HEAD lịch sử `d14c6151bb2131f0b738921d1a3b9b5f7c979d07`; cả hai dirty và **không có source freeze đầy đủ theo byte**, nên chỉ đối chứng ở mức cấu hình/trạng thái được lưu, không khẳng định cô lập nhân quả. Sáu baseline articles/categories bằng nhau và restore đều 0. Raw giữ contract; guided có example/ID/link và thêm phase stateful, nên so sánh **hai chiến lược tổng thể**. Không làm thí nghiệm phụ tách riêng guidance, nhằm giữ phạm vi gọn.

| Profile/seed | Generated case | HTTP được ghi | 2xx trong HTTP ghi (%) | Tool unique failure | Case errored | Parameter coverage | Keyword coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Raw 101 | 59 | 59 | 42,37 | 20 | 0 | 28/48 | 67/226 |
| Raw 202 | 65 | 65 | 49,23 | 18 | 0 | 28/48 | 70/226 |
| Raw 303 | 51 | 51 | 41,18 | 19 | 0 | 28/48 | 67/226 |
| Guided 101 | 5.770 | 5.659 | 26,35 | 63 | 111 | 41/48 | 180/226 |
| Guided 202 | 5.864 | 5.688 | 28,94 | 65 | 176 | 42/48 | 183/226 |
| Guided 303 | 5.894 | 5.694 | 25,59 | 62 | 200 | 42/48 | 176/226 |

Mỗi seed chạy khoảng 1.200,02–1.200,33 giây, tested 10/10 operation, response coverage 8/26 và examples coverage 12/16. **Tất cả dừng `max_time`, runner exit 1, tìm kiếm INCOMPLETE**, dù `report.complete=true` cho biết report được ghi xong. Không đánh dấu campaign PASS.

“HTTP được ghi” đếm interaction trong NDJSON bằng `(case_id,timestamp)`, tránh đếm lặp tham chiếu recorder. Đây là request được lưu bởi công cụ, **không phải toàn bộ HTTP qua mạng**, không gồm auth/setup/restore hoặc request đang dở khi dừng. `generated` có thể gồm ca errored chưa có interaction; không lấy generated làm HTTP. Không sao NDJSON có khả năng chứa header vào gói chia sẻ; chỉ xuất counter an toàn và SHA nguồn.

| Chỉ số | Raw: trung vị [min–max] | Guided: trung vị [min–max] |
|---|---:|---:|
| Recorded HTTP | 59 [51–65] | 5.688 [5.659–5.694] |
| Parameter coverage (%) | 58,33 [58,33–58,33] | 87,50 [85,42–87,50] |
| Keyword coverage (%) | 29,65 [29,65–30,97] | 79,65 [77,88–80,97] |
| 2xx trong recorded HTTP (%) | 42,37 [41,18–49,23] | 26,35 [25,59–28,94] |
| Tool unique failure | 19 [18–20] | 63 [62–65] |

Guided đạt nhiều interaction và parameter/keyword coverage hơn trong cùng budget; tuy nhiên không tăng response coverage, có errored case và tỷ lệ 2xx thấp hơn. Không thể kết luận guided “luôn tốt hơn”, tiết kiệm 99% chi phí hoặc có gấp ba defect chỉ từ các số này.

Positive acceptance cũng cần phân biệt: trường `valid_rates.*.accepted` của công cụ có ít nhất một accepted ở 10/10 operation cho cả ba raw; guided là 9/10, 10/10, 10/10. Đó là chỉ báo công cụ, chưa chứng minh input hợp đầy đủ nghiệp vụ và readback. **Bằng chứng positive nghiệp vụ 10/10 nằm ở suite thiết kế Phase 4**, không chuyển kết quả ấy thành positive acceptance của mỗi seed fuzzing. 2xx đơn thuần cũng không đủ, đặc biệt khi response sai contract như P5-F02.

Để minh họa công thức coverage/budget: chênh lệch trung vị parameter là 29,17 **điểm phần trăm**, chia 20 phút = 1,46 điểm/phút; keyword là 50,00 điểm/20 phút = 2,50 điểm/phút. Đây là chênh lệch **endpoint giữa hai chiến lược** trên cùng mẫu số, không phải tốc độ tăng tức thời, đường cong coverage hay chứng cứ đạt coverage đó sớm hơn bao lâu. Schema coverage không phải line/branch coverage source Directus.

Finding/giờ và chi phí/defect **không tính**: chưa có dedup nguyên nhân đủ cho từng cohort để chọn tử số. Bốn nhóm OPEN ở [Phase 5](05-finding-register.md) có provenance riêng, không tự gán cả bốn cho mỗi campaign này. Giữ các nhóm `ServerError`, `JsonSchemaError`, status/content-type… trong audit để truy vết, không đổi tool failure thành defect.

Run guided thay thế `20261012T122826Z-22781` được công bố riêng: seed 202 bị ngắt khoảng 645 giây, runner 130; không trộn vào cohort chính. [Chi tiết ba seed](tai-lieu-bo-tro/phase6-20261018/alternative-interrupted-cohort.json). Không giấu dữ liệu incomplete để tạo đối chứng đẹp.

## 5. Replay và tần suất chạy đề xuất

[So sánh replay](tai-lieu-bo-tro/phase6-20261018/replay-comparison.json) dùng evidence đã có, không phát sinh run replay mới:

| Hoạt động | Evidence | Thời gian metadata | Phạm vi/kết quả |
|---|---|---:|---|
| Replay `qfqspn` | `20261018T091638Z-1712` | 20 giây | Một POST Editor, tái hiện `response_schema_conformance / JsonSchemaError`, source/actual đều 200, runner/restore 0 |
| Pilot khám phá guided chứa source case | `20261012T190350Z-1047` | 229 giây cho 3 seed | 60 giây/seed, max-examples 10; có nhiều mục tiêu, dừng max_time/runner 1 |
| Suite thiết kế ngắn | `20261018T091253Z-1524` | 156 giây | 58/58 PASS, có 10 positive operation và ca quyền/biên/stateful |

Replay Python có khoảng thời gian timestamp 5 giây, còn 20 giây là cả lệnh ở độ phân giải giây. Không trộn thời gian Python với toàn pilot. Hai hoạt động replay và discovery khác mục tiêu, nên không tính “tiết kiệm 91% để tìm cùng lỗi” từ 20/229, cũng không coi 229 giây là time-to-first-failure. Finding vẫn OPEN; reproduced không có nghĩa đã sửa lỗi.

Tần suất dưới đây là **đề xuất vận hành local**, không tạo lại Phase 7 CI/CD hay tự đổi budget mặc định:

| Khi nào | Nên chạy | Lý do và ngân sách |
|---|---|---|
| Sửa tài liệu thuần túy | Kiểm tra nội dung/link | Không chạy API/campaign khi phần thực thi không bị ảnh hưởng |
| Sửa đúng một oracle/request/harness | Unit test liên quan + designed case/replay liên quan | Xác minh nhanh đúng phạm vi; replay qfqspn đã đo 20 giây |
| Thay đổi query, filter/sort/projection/pagination | `test cost-query --set pairwise` | 9 target, khoảng 21,64 giây toàn lệnh trên máy này; giữ preflight/restore |
| Đổi fixture/schema/policy/shared helper hoặc tích hợp trước demo | Suite `test designed --selection short`, scenarios và phần bị ảnh hưởng; full36 khi query đổi | Giữ bộ rủi ro cao; 58 case đã đo 156 giây; cả 36 query chỉ thêm khoảng 5 giây so với pairwise |
| Cần khám phá sau thay đổi đáng kể hoặc trước nghiệm thu | Raw và guided ba seed theo kế hoạch Phase 8 | Giữ max-time 1.200 giây/profile/seed, max-examples 100, 1 worker, 5/s, timeout 10; sáu runner budget khoảng 120 phút, chưa tính overhead/triage |

Vì full36 chỉ mất thêm khoảng 5 giây, có thể chọn full36 ở mốc tích hợp/đóng băng để nhận thêm tổ hợp. Pairwise phù hợp chạy lặp thường xuyên; lợi ích tuyệt đối ở mô hình nhỏ còn khiêm tốn. Không giảm kiểm tra quyền, biên và stateful để làm đẹp số tiết kiệm; việc ghép suite vào một lifecycle để giảm overhead là hướng tương lai, **chưa triển khai/đo**.

## 6. Chạy lại và bàn giao

Lệnh dùng chung, sau doctor/seed/export-schema của profile tương ứng:

```powershell
$env:LAB_RUNTIME_PROFILE='phase6-20261018'
$env:LAB_DETERMINISTIC_MAX_TIME='120'
& ./scripts/run-lab.ps1 test cost-query --set pairwise
& ./scripts/run-lab.ps1 test cost-query --set exhaustive
```

Linux/Git Bash dùng `./lab.sh test cost-query --set pairwise|exhaustive` với cùng biến môi trường. Không dùng đồng thời hai lệnh trên cùng project. Dùng run ID mới; launcher giữ nguyên quy tắc không ghi đè run. Xóa override budget khỏi môi trường khi xong nếu không muốn áp dụng cho lệnh deterministic khác. [Launcher sáu phép đo gốc](tai-lieu-bo-tro/phase6-20261018/run-measurements.ps1) cố ý từ chối chạy đè sáu ID cũ; muốn lặp batch phải có protocol/ID mới.

Analyzer offline: `python -X utf8 docs/HoanThanhPlan/tai-lieu-bo-tro/phase6-20261018/analyze.py`, cần raw artifact gốc tại các đường dẫn được ghi. Gói chọn lọc không chứa NDJSON/header hoặc toàn bộ corpus, vì vậy không thay thế kho raw cục bộ. [Evidence index](tai-lieu-bo-tro/phase6-20261018/evidence-index.json), [gói evidence](tai-lieu-bo-tro/phase6-20261018/evidence-selected.zip), [gói source](tai-lieu-bo-tro/phase6-20261018/source-after.zip) và [manifest source](tai-lieu-bo-tro/phase6-20261018/source-after-manifest.json) giữ phần đủ đọc kết quả và xem code sau này.

Kiểm tra offline **18/18 PASS trên host và runner pin**, gồm mất tổ hợp/cặp, query lệch mô hình, meter đếm lỗi HTTP/network mà không lưu credential, budget dở vẫn lưu report và kiểm tra trạng thái, oracle/state guard lỗi không thể PASS. Bash syntax PASS; sáu lượt API thật xác minh interface mới và restore chung. [Validation bàn giao](tai-lieu-bo-tro/phase6-20261018/validation.json) kiểm tra archive/hash/link/catalog; 177 tệp evidence gốc giữ nguyên. Không cần cài package toàn máy hoặc sửa source Directus.

[Bảng tích lũy 257 case](06-ket-qua-case.csv): **94 passed, 163 NOT_RUN** = 58 Phase 4 + 36 query Phase 6. Bảng Phase 3 và Phase 4 giữ nguyên như ảnh chụp lịch sử; bảng mới dẫn tới run/query result theo ID. Không cộng các lần lặp thành case mới, không coi 94 PASS là nghiệm thu toàn dự án. Bốn finding Phase 5 vẫn OPEN, chưa chạy full catalog hoặc campaign mới cho nghiệm thu Phase 8.

P6-01 hoàn thành thiết kế phép đo, có khai báo công chưa đo; P6-02 hoàn thành phân tích đối chứng lịch sử có giới hạn; P6-03 hoàn thành thí nghiệm mới; P6-04 hoàn thành đánh giá evidence replay và đề xuất tần suất. Bước tiếp theo của kế hoạch là **Phase 8**, sau đó Phase 9. Chưa commit/push hoặc triển khai CI/CD trong phase này.
