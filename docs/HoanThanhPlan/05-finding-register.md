# Phase 5 — Finding và phân tích nguyên nhân, bản rút gọn

**Ngày:** 18/10/2026. **Trạng thái:** hoàn thành P5-01…05 và P5-08 theo [phạm vi rút gọn](dieu-chinh-pham-vi-phase5-phase7.md). P5-06 đã gộp vào P5-02, P5-07 đã bỏ; Phase 7 vẫn ngoài phạm vi.

Báo cáo tái sử dụng evidence Phase 4, đọc source Directus đúng pin và kiểm tra tính nhất quán của artefact. **Không có lượt chạy API/campaign mới ở Phase 5, không sửa Directus hoặc assertion.** Hoàn thành báo cáo không có nghĩa đã sửa các finding bên dưới.

## 1. Phạm vi bằng chứng và cách đếm

Nguồn chính là invariant run `20261018T091538Z-1506`: 11 invariant, **9 PASS / 2 FAIL**, runner exit 1, restore exit 0. Hai invariant FAIL là aggregate robustness và contract-schema-candidates. Invariant thứ hai quan sát bốn mismatch, trong đó POST hai collection có chung cơ chế sinh schema nên được gom thành một nhóm.

Register chính có **4 nhóm bất thường SUT**, tất cả còn mở: một robustness candidate và ba nhóm mismatch hợp đồng đã đối chiếu runtime/schema. **Chưa gán nhóm nào thành defect nghiệp vụ Directus đã xác nhận.** Đây không phải tổng finding của mọi campaign lịch sử; check failure, invariant FAIL, nhóm finding và defect là các đơn vị khác nhau. Mã P5-Fxx là mã tổng hợp trong hồ sơ này, không biểu diễn phát hiện mới.

| ID | Nhóm / actor | Expected và actual | Phân loại, trạng thái | Evidence / cách gom trùng |
|---|---|---|---|---|
| **P5-F01** | Aggregate input bất thường; Editor, GET articles | Không 5xx khi xử lý input; `aggregate={"foo":1}` trả **500/INTERNAL_SERVER_ERROR**, empty/count control đều 200 | **Robustness candidate — OPEN**. Source cho thấy thiếu kiểm tra kiểu trước nơi dùng iterable; chưa có stack server của run 18/10 để chốt chính xác điểm throw | [Probe aggregate](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/reproducer-aggregate-query-robustness.json). Gom các lần lặp cùng payload/control, không gom mọi HTTP 500 vào đây |
| **P5-F02** | POST object; Editor, cả hai collection | Controller nhận object và trả `data` object; raw OpenAPI yêu cầu `data` array. HTTP 200 vẫn FAIL response-schema | **Schema mismatch đã đối chiếu — OPEN**, chưa sửa generator/schema | [Probe contract](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/reproducer-contract-schema-candidates.json), [replay qfqspn](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091638Z-1712/reproducer-schemathesis-qfqspn.json). Hai collection cùng nhánh generator, tính một nhóm |
| **P5-F03** | DELETE detail; Editor | Runtime xóa thành công và trả **204**; schema chỉ khai báo **200/401/404** | **Status contract mismatch đã đối chiếu — OPEN**. Không phải bằng chứng thao tác xóa sai nghiệp vụ | [Replay Z6yNal](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091711Z-433/reproducer-schemathesis-Z6yNal.json): GET producer → DELETE consumer, cùng `UndefinedStatusCode`. Không gom với POST shape |
| **P5-F04** | CSV export; Editor, GET articles | `export=csv` trả **200, text/csv**; operation schema mô tả **application/json** | **Media-type contract mismatch đã đối chiếu — OPEN**. Chưa kiểm đủ nội dung row của export | [Probe contract](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/reproducer-contract-schema-candidates.json), [body CSV](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/python-http/response-83.json). Nhiều check phát sinh từ một media-type khác biệt không làm tăng số nhóm |

Các mismatch vẫn FAIL theo raw contract dù source giải thích được hành vi. Không thêm allowlist, sửa raw schema hoặc đổi expected theo output để tạo PASS.

Các phép đối chiếu và quy tắc đếm có trong [audit finding](tai-lieu-bo-tro/phase5-20261018/finding-audit.json).

## 2. Baseline và provenance dùng cho kết luận

| Thành phần | Căn cứ của lượt chạy được dùng |
|---|---|
| Directus | 12.5.0; source pin `4f77933bf9551cac6b289576078783e189b8f4e3`; image digest `sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331` |
| Source ↔ image | [Target verification Phase 4](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/target-verification.json) ghi container image khớp config, OCI revision khớp pin, port loopback; không dùng HEAD checkout Directus làm nguồn thay thế |
| Harness | HEAD `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`, **dirty**; hash từng file tại lượt chạy có trong [harness-inputs Phase 4](tai-lieu-bo-tro/phase4-20261018/evidence/20261018T091538Z-1506/harness-inputs.json). HEAD một mình không nhận diện đủ mã chưa commit |
| Fixture và actor | `r06-k05-v2`, 3 category/12 article, ID từ map/response; Editor gửi probe. Admin phục vụ preflight/control/restore, không làm actor fuzz |
| Tool/budget | Schemathesis 4.30.0 pin; [execution-config](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/execution-config.json) và [metadata](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/metadata.json). Nhãn `admin_usage` cũ là mô tả hẹp; trace actor trong report là căn cứ chi tiết |
| Raw schema Editor | SHA-256 `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26`, [bản input nguyên vẹn](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/schema-editor-input.json) |
| Schema của hai replay Schemathesis | Guided source hash `cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`. Giữ nhãn guided; không gọi kết quả replay này là campaign raw. Response POST/DELETE liên quan khớp hợp đồng raw được đối chiếu |

[Manifest source](tai-lieu-bo-tro/phase5-20261018/baseline-source-manifest.json) ghi commit, Git blob và SHA-256 của 10 tệp lấy bằng `git show <pin>:<path>`. [Manifest evidence](tai-lieu-bo-tro/phase5-20261018/evidence-manifest.json) ghi 25 bản sao byte-identical từ artefact có sẵn. Đây là bộ nguồn cho phân tích, không phải trạng thái health hiện tại của lab.

## 3. Phân tích đại diện A — P5-F01 aggregate 500

### Request, expected và control

Ba request thực tế của cùng probe, cùng Editor và cùng fixture:

```text
GET /items/qa_articles?fields=&aggregate={"foo":1}       → 500
GET /items/qa_articles?fields=&aggregate={}              → 200, data array 12 row
GET /items/qa_articles?fields=&aggregate={"count":["id"]} → 200, data array 1 row
```

Trong HTTP thực, JSON của aggregate được URL-encode; đường dẫn và response chính xác ở [probe](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/reproducer-aggregate-query-robustness.json), [response lỗi](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/python-http/response-72.json) và hai [control empty](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/python-http/response-73.json)/[count](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/python-http/response-74.json).

Expected ở đây là invariant robustness **không trả 5xx**. Input không thuộc nghiệp vụ aggregate hợp lệ nên không đòi API thực hiện phép tính `foo`; một hướng sửa hợp lý là từ chối bằng lỗi 4xx có kiểm soát. Chưa tự đặt mã 4xx cụ thể cho bản sửa chưa tồn tại. Hai control 200 và preflight đạt loại bớt giả thuyết API/credential/fixture hỏng toàn bộ. Case cleanup PASS và [restore 0](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/component-outcomes.json) kiểm trạng thái nghiệp vụ được giữ; không suy mọi trạng thái nội bộ Directus đều bất biến.

### Source đúng pin cho biết điều gì?

1. [Aggregate parameter](tai-lieu-bo-tro/phase5-20261018/baseline-source/packages/specs/src/parameters/aggregate.yaml), dòng 7–59, mô tả object với các key count/sum/avg/min/max… và kiểu string/array cho các key đã nêu. Snapshot không đặt `additionalProperties: false` để chặn key ngoài danh sách; không phải mọi thuộc tính của object đều được ràng buộc bằng các kiểu đó.
2. [sanitize-query.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/utils/sanitize-query.ts), dòng 144–162, parse JSON rồi chỉ chuẩn hóa value kiểu string hoặc array. Với `foo: 1`, value số không được loại hoặc chuyển thành danh sách; cuối hàm dùng type assertion `as Aggregate`.
3. [validate-query.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/utils/validate-query.ts), dòng 15–35, chỉ khai báo `aggregate: Joi.object()` tại query schema, chưa nêu rule cho từng operation/value ở đây.
4. [apply-query/aggregate.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/database/run-ast/lib/apply-query/aggregate.ts), dòng 24–37, lấy `fields` từ mỗi entry; số 1 là truthy nên không bị bỏ qua bởi `if (!fields) continue`, rồi được dùng trong `for (const field of fields)`. Số không iterable: có đường phát sinh TypeError thay vì lỗi query có kiểm soát.
5. [error-handler.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/middleware/error-handler.ts), dòng 84–109, chuyển exception không phải DirectusError sang fallback 500 và che chi tiết với actor không phải Admin, phù hợp response Editor đã lưu.

**Kết luận:** có khoảng trống kiểm tra kiểu/operation của aggregate trước các nơi dùng value như iterable; đây là giải thích source có căn cứ cho candidate 500. Chưa thu được stack server gắn chính run 18/10 để xác nhận nơi throw đầu tiên. Vì vậy giữ **candidate OPEN**, không gán vị trí throw của run này chỉ từ log/ghi chú lịch sử.

**Ảnh hưởng và bước tiếp:** robustness khi nhận input bất thường; chưa có bằng chứng mất dữ liệu hoặc vượt quyền. Nếu cần xác nhận/sửa sản phẩm, replay tối giản kèm log server đúng lượt, kiểm nhánh validation và retest cả input lỗi lẫn hai control. Không cần làm bước đó chỉ để tăng số defect trong báo cáo này.

## 4. Phân tích đại diện B — P5-F02 POST response shape

Probe deterministic đã gửi Editor payload category hợp lệ, dưới max length:

```http
POST /items/qa_categories
Content-Type: application/json

{"name":"Contract candidate category 9dbebeb412296350d2317871"}
```

Actual của [response-81](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/python-http/response-81.json) có HTTP 200 và `data` object. POST article trong cùng [probe](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091538Z-1506/reproducer-contract-schema-candidates.json) cũng trả object. Raw response schema của cả hai operation yêu cầu `data.type = array`. Đây là payload/ID của lần chạy đã lưu, không phải hướng dẫn hard-code ID cho lượt mới.

**Nguyên nhân được đối chiếu trực tiếp:**

| Nhánh runtime | Nhánh sinh OpenAPI | Sai lệch phát sinh |
|---|---|---|
| [items.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/controllers/items.ts), dòng 37–52: body array → createMany/readMany; body object → createOne/readOne; cả hai bọc trong `data` | [specifications.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/services/specifications.ts), dòng 242–258: request chấp nhận object hoặc array. Nhưng dòng 263–282 chọn response `data` theo **singleton của collection**, không theo body object/array | Với collection thường, generator luôn đặt response `data` array cho POST, còn runtime có nhánh trả object |

Vì cả hai collection trong lab đều không singleton và dùng cùng generator, hai mismatch được gom thành **một nguyên nhân schema-response-shape**. Đây là phân tích nguyên nhân cụ thể đáp ứng yêu cầu RCA; không chỉ dựa vào tên check hoặc status 200.

[Replay qfqspn](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091638Z-1712/reproducer-schemathesis-qfqspn.json) của Phase 4 dùng schema nguồn guided, source/actual cùng 200 và vẫn FAIL `response_schema_conformance / JsonSchemaError`; ba check nền tảng còn lại PASS. Replay scope là **single_request**, không phải full campaign. Runner replay exit 0 nghĩa là tái hiện đúng failure; **không** nghĩa là contract PASS. [Restore exit 0](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T091638Z-1712/component-outcomes.json).

**Kết luận:** mismatch hợp đồng đã có evidence runtime + source đúng pin; trạng thái **OPEN, chưa sửa generator**. Không kết luận createOne hỏng nghiệp vụ chỉ vì response không khớp schema. Nếu sửa generator, cần mô hình hóa cả dạng object/array, retest hai loại body và giữ kết quả raw trước sửa; overlay giải thích hợp đồng phải tách riêng.

## 5. Hai nhóm contract còn lại

**P5-F03 — DELETE:** [items.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/controllers/items.ts), dòng 235–250, gọi deleteOne rồi chuyển sang middleware mà không gán payload. [respond.ts](tai-lieu-bo-tro/phase5-20261018/baseline-source/api/src/middleware/respond.ts), dòng 120–125, trả 204 khi không có payload. Trong khi [item.yaml](tai-lieu-bo-tro/phase5-20261018/baseline-source/packages/specs/src/paths/items/item.yaml), dòng 54–66, khai báo 200/401/404; generator thêm/merge 200 ở specifications.ts dòng 316–333 và không bổ sung 204. Runtime 204 là có đường xử lý rõ; response map thiếu status đó.

Replay Z6yNal đã thực hiện parent `MsrYGI` GET → DELETE, map theo identity, tái hiện đúng `UndefinedStatusCode` với 204 và restore 0. Đây là **full recorded parent chain**, không khôi phục mọi trạng thái lịch sử của campaign. Chưa sửa schema; không tính cùng một DELETE vừa là lỗi nghiệp vụ vừa là defect schema thứ hai.

**P5-F04 — export:** respond.ts dòng 101–104 chủ động đặt `text/csv`; GET trong [items.yaml](tai-lieu-bo-tro/phase5-20261018/baseline-source/packages/specs/src/paths/items/items.yaml), dòng 25–40, và generator specifications.ts dòng 263–286 mô tả response JSON. CSV của probe 18/10 xác nhận mismatch media type này. XML/YAML và alternate JSON export đã có [triage lịch sử](../../evidence/failure-triage-v2-2026-10-11.md), nhưng Phase 5 không chạy lại hoặc tính thêm chúng thành finding mới. Mismatch content type không tự chứng minh sai nội dung export; oracle đủ row chưa được nghiệm thu.

## 6. Lỗi harness/môi trường và các trường hợp không kết luận thành defect

Các mục sau giải thích tính tin cậy của phép thử, **không cộng vào bốn nhóm SUT**:

| Trường hợp | Kết luận và evidence phù hợp |
|---|---|
| Bốn ca category dùng projection của article | Lỗi thiết kế input/control; [errata](tai-lieu-bo-tro/phase4-20261018/catalog-errata.json) đổi thành `id,name`. Suite sau sửa hai lượt 58 PASS; không gọi positive control bị từ chối là lỗi API quyền |
| Token thường nhưng expected nhánh JWT | Lỗi harness chọn input xác thực sai nhánh; giữ FAIL ở run `20261018T090634Z-290`. Sau khi tạo JWT tổng hợp sai chữ ký và thêm valid control, hai lượt short PASS. Source/chi tiết trong [Phase 4](04-automation-va-tai-lap.md); không quy 401/INVALID_CREDENTIALS thành defect |
| jq path conversion, SQL metadata và DELETE control không có body | Các lỗi harness tích hợp đã được ghi và sửa trong Phase 4. Tái sử dụng [run-index](tai-lieu-bo-tro/phase4-20261018/run-index.json); không mở thêm vòng đời sửa lỗi hoặc tái tạo lỗi cho Phase 5 |
| Lab Exited 255, preflight chặn | Sự cố môi trường trong run `20261018T085927Z-1907`; chưa xác định nguyên nhân dừng. Không có target test để kết luận Directus defect; sau up, suite đủ điều kiện mới chạy |
| Hết budget có chủ đích | Run `20261018T091924Z-1822` là INCOMPLETE, cleanup/restore PASS. Không phải API FAIL và không tính là case PASS |
| Case 5Ez1Ry không có failure nguồn | [Replay](tai-lieu-bo-tro/phase5-20261018/evidence/20261018T092051Z-1565/reproducer-schemathesis-5Ez1Ry.json) chạy đủ POST array → DELETE, status đều 204 nhưng trả `no_source_failure`, exit 1, restore 0. Không có defect để tuyên bố reproduced chỉ từ status trùng nhau |

Các run historical về timestamp rỗng 500 (`kb5gjq`), accepted-negative/coercion và stateful mismatch (`DhqXrn`, `UTk4sa`, `6THjzP`…) giữ **candidate/unresolved theo [triage gốc](../../evidence/failure-triage-v2-2026-10-11.md)**. Chúng không có bằng chứng mới trong lượt này, không gộp vào aggregate chỉ vì cùng 500, cũng không nâng thành lỗi quyền/toàn vẹn đã xác nhận. Single-request replay, mismatch hoặc target chưa gửi không chứng minh lỗi stateful. Nếu đưa các trường hợp này vào kết luận nghiệm thu chính, cần kiểm lại provenance và precondition liên quan.

Các response 400/403 lịch sử có thể xuất phát từ query sai ngữ nghĩa hoặc policy đúng; TRACE nằm ngoài 10 operation chính. Không tự tính chúng là product defect chỉ vì tool đánh dấu failure. Các trường hợp cụ thể giữ phân loại và giới hạn ở triage gốc, không được tính là đã retest trong Phase 5.

## 7. Chạy lại khi cần và ảnh hưởng tới nghiệm thu

Các lệnh dưới dùng launcher đã có, credential hiện tại từ cấu hình riêng và ID động; **không được gọi trong Phase 5 này**. Precondition: đúng lab r06-k05, fixture/map/schema đã seed/export theo README, actor/entitlement hợp lệ, không có suite ghi khác đang chạy.

```powershell
$env:LAB_RUNTIME_PROFILE = 'phase4-20261018'
.\scripts\run-lab.ps1 replay aggregate-query-robustness
.\scripts\run-lab.ps1 replay contract-schema-candidates

$env:LAB_REPLAY_EVENTS = '20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson'
.\scripts\run-lab.ps1 replay qfqspn
.\scripts\run-lab.ps1 replay Z6yNal
Remove-Item Env:LAB_REPLAY_EVENTS
```

Hai invariant riêng dự kiến vẫn trả nonzero vì assertion FAIL; replay qfqspn/Z6yNal trả 0 khi khớp đúng failure nguồn. Luôn đọc report và restore riêng, không dùng `|| true` để che kết quả. Events/schema nguồn phải còn nguyên; nếu chuyển máy, dùng hướng dẫn/gói evidence ở Phase 4, không chép token cũ.

Phần báo cáo cuối kỳ có thể khẳng định: automation tìm được một input gây 500 có control, phát hiện ba nhóm lệch hợp đồng, có reproducer và một nguyên nhân generator được chỉ rõ. Chưa thể khẳng định toàn Directus đúng, mọi lỗi đã sửa, hay toàn campaign PASS. Chưa có phát hiện vượt quyền hoặc mất dữ liệu được xác nhận trong tập evidence được tổng hợp; đây không phải chứng minh an toàn cho mọi API/actor/input.

**Bàn giao Phase 6/8:** giữ bốn nhóm OPEN và exit code/check gốc; chọn thí nghiệm chi phí riêng, không chạy fuzz để tìm lại lỗi đã có chỉ nhằm tăng số liệu. Khi code/schema/fixture/oracle đổi, retest phần bị ảnh hưởng trước khi dùng evidence cũ cho nghiệm thu.

[Validation Phase 5](tai-lieu-bo-tro/phase5-20261018/validation.json) kiểm link, snapshot/source/schema/report và checksum lịch sử. Việc này nghiệm thu hồ sơ phân tích, không phải retest sản phẩm hoặc xác nhận review của thành viên khác.

## Cập nhật từ Phase 8

Bốn nhóm trên vẫn OPEN. Nghiệm thu tiếp tục tái hiện các sai lệch; có thêm projection `fields=title` khác schema required và hai mẫu 5xx probe chưa khoanh nguyên nhân. Xem [báo cáo Phase 8](08-bao-cao-nghiem-thu.md). Theo yêu cầu tối giản, báo cáo môn học tập trung hai đại diện aggregate và POST; không tự tăng số defect từ các lần sinh/shrink hoặc bắt buộc điều tra sâu mọi candidate.
