# Phase 8 — Kết quả nghiệm thu R06–K05

**Ngày chốt:** 18/10/2026. Phạm vi hiện hành theo [bản tối giản](LO_TRINH_TOI_GIAN_R06_K05.md). Đã thực hiện các lượt nghiệm thu; không chỉnh source Directus, schema, policy hoặc oracle để tạo PASS. Campaign chính được tái sử dụng theo lựa chọn rõ ràng của người dùng.

**Kết luận:** Có đủ bằng chứng kỹ thuật để viết báo cáo đồ án trong phạm vi công bố. **SUT còn FAIL về robustness và contract**, không kết luận toàn Directus hoặc toàn catalog PASS. Việc nghiệm thu này không thay xác nhận của giảng viên hoặc đánh giá đóng góp của nhóm.

## 1. Trạng thái P8-01 đến P8-08

| Task | Trạng thái hiện hành | Bằng chứng/giới hạn |
|---|---|---|
| P8-01 — Khóa checkpoint | Hoàn thành | [Checkpoint 28 tệp](tai-lieu-bo-tro/phase8-20261018/checkpoint-manifest.json), [archive](tai-lieu-bo-tro/phase8-20261018/acceptance-checkpoint.zip). Mã chưa commit được nhận diện bằng SHA-256; không tự tạo commit/tag |
| P8-02 — Preflight và deterministic | Hoàn thành | Doctor/seed/export; hai suite 58 ca; suite 118 ASSERTABLE; nhóm query và bốn ca bổ sung; scenario, smoke, invariant, full36 |
| P8-03 — Xử lý sai lệch trước campaign | Hoàn thành kiểm tra | Precondition đạt; cleanup/restore đạt ở các run nghiệm thu. Giữ FAIL thật và phân loại; không có lỗi harness/restore đang chặn các bước sau |
| P8-04 — Campaign | Hoàn thành theo lựa chọn tái sử dụng | Giữ hai campaign lịch sử đủ ba seed; hai probe 60 giây trên checkpoint mới được ghi riêng; không gọi probe là campaign chính |
| P8-05 — Audit artifact | Hoàn thành | [Run index](tai-lieu-bo-tro/phase8-20261018/run-index.json), [pipeline audit](tai-lieu-bo-tro/phase8-20261018/pipeline-audit.json), [bảng case](08-ket-qua-case.csv), [validation](tai-lieu-bo-tro/phase8-20261018/validation.json) |
| P8-06 — Replay finding | Hoàn thành phần đại diện theo phạm vi rút gọn | POST và DELETE tái hiện native failure; projection tái sinh thiết kế và FAIL cùng check. Điều tra/replay mọi candidate mới đã bỏ khỏi phần bắt buộc; hai mẫu 5xx probe còn unresolved |
| P8-07 — Phạm vi chưa phủ | Hoàn thành thống kê | 65 NOT_RUN, 1 OPEN; bảng BR, biên, quyền, phân vùng; không đổi các khoảng trống thành PASS |
| P8-08 — Chốt kết luận | Hoàn thành | Kết luận có giới hạn ở đầu báo cáo; finding chưa sửa vẫn OPEN; chuyển sang phần báo cáo/demo Phase 9 |

Không có task hiện bị **tool log** ghi từ chối bởi chính sách an ninh mạng. Có sự cố chặn hiển thị nội dung ở giao diện do người dùng cung cấp; [ghi nhận riêng](tai-lieu-bo-tro/phase8-20261018/interruption-record.json). Không suy từ ảnh rằng test đã PASS hoặc tiến trình Docker đã bị hủy. Log thực tế cho thấy hai probe đã hoàn tất report và restore, trả exit 1 do kết quả kiểm thử/hết ngân sách.

## 2. Checkpoint và cấu hình thật

| Thành phần | Giá trị |
|---|---|
| Directus | 12.5.0; OCI revision khớp pin `4f77933bf9551cac6b289576078783e189b8f4e3` |
| Runner | Schemathesis 4.30.0, Docker image có digest pin; Python 3.14.3, Hypothesis 6.168.5, jsonschema_rs 0.58.6 |
| DB/fixture | PostgreSQL 16; fixture v2, 3 category/12 article, 6 draft/6 published; ID từ map |
| Runtime profile | `phase8-20261018`, cùng project `r06-k05`; không phải DB thứ hai |
| Deterministic | 1 worker, 5/s trong Python, timeout 10 giây, cap 600 giây; cleanup/restore ngoài cap |
| Runtime công khai | Cache/telemetry/server rate limiter tắt; token TTL 2h; [key đã truy vấn](tai-lieu-bo-tro/phase8-20261018/public-runtime-config.json) |
| Harness | HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, working tree dirty; archive/hash nhận diện phần chưa commit |

Schema Editor giữ hash `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26`; Reader `d7dc1393eb7e01514f0f8a4d3796ab71cf1f0fe70f5c8a3da5c0ae20259b47b8`. Image digest, dependency, schema/map và ngân sách chi tiết nằm trong checkpoint/metadata, không ghi credential hoặc license value.

Archive khóa **trước các test**; sau test chỉ thu gọn tài liệu hướng dẫn/điều hướng. README mới được phân biệt trong validation; không gán hash tài liệu mới ngược cho các run cũ. Không commit/push hoặc reset volume.

## 3. Kết quả chạy mới

Tên run có tiền tố `p8-20261018-`; chi tiết 17 run trong [run-index](tai-lieu-bo-tro/phase8-20261018/run-index.json), ngoài ba run chuẩn bị doctor/seed/export.

| Lượt | Kết quả thực | Runner/restore |
|---|---|---|
| `short-r1`, `short-r2` | Mỗi lượt **58/58 PASS**; cùng thứ tự, verdict, schema, config và fixture | 0/0 |
| `assertable` | **111 PASS, 7 FAIL**, đủ 118 ca; không BLOCKED/INCOMPLETE | 1/0 |
| `query-extra` | **15 PASS, 1 OPEN**; search blank không được coi PASS | 1/0 |
| `fk-post`, `fk-patch`, `time-utc`, `time-offset` | Bốn ca PASS; FK sai bị từ chối và không đổi dữ liệu; timestamp đúng được đọc lại đúng instant | Mỗi lượt 0/0 |
| `query-full` | **36/36 PASS**, phủ 37/37 cặp; dùng làm regression, không nhập vào phép đo chi phí Phase 6 | 0/0 |
| `scenarios`, `smoke` | **6/6 scenario PASS**, smoke PASS | 0/0 |
| `invariants` | **9 PASS, 2 FAIL**: aggregate robustness và contract candidates | 1/0 |
| `replay-qfqspn` | POST 200 tái hiện `response_schema_conformance/JsonSchemaError` | 0/0 nghĩa replay tái hiện, không có nghĩa SUT đã được sửa |
| `replay-z6ynal` | GET producer → DELETE consumer 204, tái hiện `UndefinedStatusCode` | 0/0 |
| `projection-replay` | Business PASS, contract FAIL như lần đầu; tái sinh case thiết kế | 1/0 |

[Repeatability](tai-lieu-bo-tro/phase8-20261018/repeatability.json) xác minh cặp short; text probe và ID tạm có thể khác giữa run. Không phát hiện khác verdict ở các ID thiết kế chạy lặp. Hai replay Schemathesis dùng bản trích recorder đã bỏ header xác thực từ Phase 4, trên cùng máy; không tuyên bố đã thử máy mới hoặc đổi mọi fixture ID.

**Positive nghiệp vụ đạt 10/10 operation**, có read-back/absence theo thiết kế: [bảng operation](tai-lieu-bo-tro/phase8-20261018/positive-operations.csv). Điều này không xóa lỗi raw contract. Tám case contract trong bộ 118 chạy 32 native check: **26 check PASS, 6 FAIL**. Không nói mọi case đều đã chạy mọi contract check.

## 4. Những lỗi giữ lại

| Nhóm | Kết quả và ảnh hưởng |
|---|---|
| P5-F01 — aggregate | HTTP 500 với input aggregate bất thường, control hợp lệ đạt; robustness candidate OPEN, chưa chốt chính xác điểm throw |
| P5-F02 — POST object | Hai collection trả data object, raw schema yêu cầu array; business đúng nhưng contract FAIL |
| P5-F03 — DELETE | Xóa đúng nghiệp vụ, trả 204 chưa khai báo trong raw schema; replay tái hiện |
| P5-F04 — export | CSV/XML/YAML trả media type tương ứng ngoài `application/json`; giữ các biến thể trong cùng nhóm sai lệch media type |
| P8-F05 — projection | `fields=title` trả title đúng, nhưng schema item vẫn bắt buộc score; native check FAIL; đã chạy lại và đối chiếu source đúng pin |

**Hai đại diện để trình bày:** aggregate và POST object; dùng phân tích Phase 5. Projection có [audit ngắn và source pin](tai-lieu-bo-tro/phase8-20261018/projection-finding-and-replay-plan.json): generator đưa field non-null/không default/không generated vào `required`, response dùng chung component nên không phù hợp projection bỏ field đó. Không sửa required hoặc expected để làm test PASS.

Probe guided còn 27 interaction 500 được ghi: 22 POST categories và 5 GET articles. Đây là các lần sinh/shrink/lặp, **không phải 27 defect**; tool báo hai unique ServerError. Chưa cô lập nguyên nhân, chưa đồng nhất GET nhiều tham số với F01 hoặc kết luận POST là một defect độc lập. [Metadata an toàn và trạng thái unresolved](tai-lieu-bo-tro/phase8-20261018/probe-server-error-candidates.json) được giữ ở phụ lục; không mở điều tra/replay thêm theo phạm vi tối giản. Vì vậy SUT không đạt tiêu chí “không còn 5xx”.

## 5. Campaign cũ và probe mới

| Bộ | Seed/budget | Trạng thái |
|---|---|---|
| Raw `20261011T085034Z-76481` + guided `20261011T095117Z-89079` | Mỗi profile 101/202/303; 1.200 giây, max-examples 100, 1 worker, 5/s, timeout 10 | Giữ nguyên sáu report cũ: tested 10/10, runner 1, restore 0, max_time; tìm kiếm INCOMPLETE |
| Probe raw `p8-20261018-probe-raw` | Seed 101; 60 giây/max-examples 10 | Tested 10/10; generated 61; tool unique failure 22; case errored 0; runner 1/restore 0/max_time |
| Probe guided `p8-20261018-probe-guided` | Seed 101; 60 giây/max-examples 10 | Tested 10/10; generated 278; tool unique failure 32; case errored 2; runner 1/restore 0/max_time |

Người dùng đã chọn tái sử dụng campaign chính để tiết kiệm thời gian. [Impact audit](tai-lieu-bo-tro/phase8-20261018/campaign-impact-audit.json) cho thấy các hàm campaign không đổi so với input Phase 4; schema scoped của probe khớp lịch sử. Tuy nhiên source dirty lịch sử không có freeze byte đầy đủ: không gọi đó là sáu campaign đã chạy trên checkpoint Phase 8. Positive nghiệp vụ hiện tại và accepted của công cụ là hai chỉ số riêng.

`generated` không phải tổng HTTP; check failure không phải defect; `report.complete=true` không xóa trạng thái hết ngân sách. Số coverage/status theo seed giữ trong [báo cáo Phase 6](06-toi-uu-chi-phi.md) và [pipeline audit](tai-lieu-bo-tro/phase8-20261018/pipeline-audit.json). Không chạy lại campaign hoặc thay ngân sách chính.

## 6. Phạm vi còn thiếu và bàn giao

- [Catalog kết quả](08-ket-qua-case.csv): **184 PASS, 7 FAIL, 1 OPEN, 65 NOT_RUN** trên 257 ID; không cộng lặp run/replay thành ca mới.
- [Truy vết BR](08-truy-vet-ket-qua.csv): cả 26 BR có case đã thực thi; không đồng nghĩa toàn bộ 26 BR đều đúng hoặc được phủ hết. Failure contract gắn BR-11/BR-22 không tự chứng minh CRUD/projection sai nghiệp vụ.
- [Biên](tai-lieu-bo-tro/phase8-20261018/boundary-coverage.csv): 33/34 điểm PASS, `page=0` chưa chạy. [Quyền](tai-lieu-bo-tro/phase8-20261018/permission-coverage.csv): 54/69 luật có case chỉ định PASS, 15 chưa chạy qua ID đó; scenario/invariant có thêm kiểm tra field kín nhưng không tự tăng số đếm.
- [Phân vùng](tai-lieu-bo-tro/phase8-20261018/equivalence-coverage.csv): 25/48 lớp có đại diện field-focused PASS; không khẳng định đúng mọi giá trị trong lớp. Empty/blank/coercion, Unicode length, một số missing/default/nested và timestamp bất thường còn giới hạn.
- Search blank vẫn OPEN; query hữu hạn và schema coverage không phải source line/branch coverage. Replay recorded parent chain không tái lập toàn bộ trạng thái campaign.

18/18 unit test PASS trên host và image pin; các dòng FAIL giả lập trong unit log là tình huống regression được test, khác failure API thật. [Evidence index](tai-lieu-bo-tro/phase8-20261018/evidence-index.json), [gói chọn lọc](tai-lieu-bo-tro/phase8-20261018/evidence-selected.zip) và [validation](tai-lieu-bo-tro/phase8-20261018/validation.json) giữ bằng chứng đọc sau; raw NDJSON/header không đưa vào gói chia sẻ. Dữ liệu gốc và checkpoint trước thu gọn được giữ nguyên.

**Bước tiếp theo:** làm báo cáo/slide/demo và bàn giao Phase 9 theo bản tối giản. Không triển khai CI/CD hoặc bổ sung điều tra ngoài phạm vi môn học.
