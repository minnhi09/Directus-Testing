# Phase 2 — Danh mục test sinh đại diện

**Ngày chọn mẫu:** 18/10/2026. Bảy mẫu dưới đây được trích từ artifact đã chạy, không tạo request/test result mới. Actor là Editor, fixture version `r06-k05-v2`, Schemathesis `4.30.0`. Đây là mẫu giải thích phương pháp sinh và oracle, không phải bộ regression đã triển khai hoặc thống kê mọi defect.

[JSON trích xuất đã bỏ header xác thực](tai-lieu-bo-tro/phase2-20261018/selected-generated-cases.json) lưu seed, case ID, schema hash, file/line/SHA-256 nguồn, request, generation metadata, checks, status/content type, response summary/hash và parent cho chuỗi. Giữ request đầy đủ trong JSON; response chỉ trích shape/ID để hạn chế sao chép raw. NDJSON gốc vẫn là nguồn request/response đầy đủ khi cần tái dựng.

`GEN-*` là mã danh mục tài liệu mới; `case_id` là mã thật của công cụ. Không gán GEN-* thành case đã viết bằng tay hoặc xác nhận review của thành viên. `positive/negative` dưới đây là nhãn generation của công cụ, không tự là verdict nghiệp vụ.

## 1. Nguồn schema và run

| Profile | Run nguồn | Schema hash |
|---|---|---|
| Raw, seed 303 của GEN-03 | `20261012T185958Z-355` | `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e` |
| Guided, seed 101 của GEN-01/02/04/05/06; seed 303 của GEN-07 | `20261012T190350Z-1047` | `cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831` |

Hash được tính từ từng schema thật ở thư mục seed, không chỉ chép manifest. Schema nguồn Editor là `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26`. Các pilot giới hạn budget; không dùng mẫu này để tuyên bố campaign chính hoàn tất. ID map hiện tại đã được seed lại sau pilot; xem giới hạn provenance trong [báo cáo Phase 2](02-danh-gia-openapi-va-sinh-test.md).

## 2. Bảy case được chọn

| Mã | Nhóm đại diện | Seed / case ID / phase | Request chính | Actual và check liên quan | Ý nghĩa, giới hạn |
|---|---|---|---|---|---|
| GEN-01 | Positive có response hợp contract | 101 / `MsrYGI` / stateful | GET articles, `deep={}` | 200 JSON; bảy check được recorder ghi success | data array có 11 ID; fixture đã biến đổi trong campaign, không dùng count 11 làm expected seed hoặc bằng chứng BR-20 |
| GEN-02 | Negative do syntax fuzzing | 101 / `vMx2xh` / fuzzing | POST articles, body byte NUL, media type JSON | 400; negative_data_rejection success; status_code_conformance failure | Input không phải JSON hợp lệ được từ chối, nhưng raw schema không liệt kê 400; hai oracle có kết luận khác nhau |
| GEN-03 | Input chứa giá trị biên schema | 303 / `pL46PA` / fuzzing, positive | GET articles, export=yaml, backlink=false, limit=-1, meta=* | 200 text/yaml; content_type_conformance failure | `limit=-1` bằng minimum của schema; còn query khác nên không phải ca biên được cô lập hoặc bằng chứng đã kiểm đủ BR-21 |
| GEN-04 | Response shape mismatch | 101 / `qfqspn` / examples, positive | POST article object theo example guided | 200 JSON, data object ID=13; response_schema_conformance failure | Snapshot mô tả data array. Tách contract mismatch khỏi việc object create thành công; không tự tính là lỗi CRUD |
| GEN-05 | Stateful GET producer → DELETE consumer | 101 / `Z6yNal`, parent `MsrYGI` / stateful | GET list lấy ID → DELETE articles/7 | 200→204; consumer status_code_conformance failure | Có parent/transition thật, expression response ID; chưa có GET sau DELETE để chứng minh BR-13 đầy đủ |
| GEN-06 | Stateful POST array producer → DELETE consumer | 101 / `5Ez1Ry`, parent `EerNvl` / stateful | POST categories array → DELETE categories/6545 | 200→204; recorder consumer không chứa status_code_conformance và các check ghi nhận đều success | Có chuyển ID từ create thật; không gọi đây là mọi contract check PASS hoặc chuỗi CRUD đủ bốn loại thao tác |
| GEN-07 | Giới hạn custom timestamp | 303 / `mmMmLr` / fuzzing, positive | POST article array có published_at chuỗi rỗng | 400; recorder chỉ có năm check success, không ghi hai check acceptance-positive/status-conformance cho case này | Chứng minh nhãn positive của generator chưa bảo đảm hợp timestamp/BR. Payload còn field khác có thể sai nên không quy nguyên nhân 400 riêng cho timestamp |

## 3. Truy vết schema location và artifact

Pointer dưới đây theo schema trong thư mục seed; `/` trong tên path/media type được escape theo JSON Pointer thành `~1`.

| Mã | Schema location/check source | NDJSON gốc và dòng |
|---|---|---|
| GEN-01 | `#/paths/~1items~1qa_articles/get/parameters` → `#/components/parameters/Deep`; response `…/get/responses/200/content/application~1json/schema` | [guided seed 101](../../artifacts/runs/20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson), dòng 162 |
| GEN-02 | `#/paths/~1items~1qa_articles/post/requestBody/content/application~1json/schema`; mutation syntax_fuzzing, pointer rỗng ở body | [guided seed 101](../../artifacts/runs/20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson), dòng 62 |
| GEN-03 | `#/components/parameters/Limit/schema/minimum=-1`; `#/components/parameters/Export`; response GET list chỉ application/json | [raw seed 303](../../artifacts/runs/20261012T185958Z-355/raw/seed-303/schemathesis-events.ndjson), dòng 692 |
| GEN-04 | `#/paths/~1items~1qa_articles/post/requestBody/content/application~1json/example`; `…/responses/200/content/application~1json/schema/properties/data/type=array` | [guided seed 101](../../artifacts/runs/20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson), dòng 14 |
| GEN-05 | Consumer `#/paths/~1items~1qa_articles~1{id}/delete`; transition `$response.body#/data/*/id` từ GET response | [guided seed 101](../../artifacts/runs/20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson), dòng 162, cả parent và consumer |
| GEN-06 | Producer `#/paths/~1items~1qa_categories/post`; consumer `#/paths/~1items~1qa_categories~1{id}/delete`; `$response.body#/data/*/id` | [guided seed 101](../../artifacts/runs/20261012T190350Z-1047/guided/seed-101/schemathesis-events.ndjson), dòng 180, cả parent và consumer |
| GEN-07 | `#/components/schemas/ItemsQaArticles/properties/published_at/format=timestamp`; request qua oneOf POST | [guided seed 303](../../artifacts/runs/20261012T190350Z-1047/guided/seed-303/schemathesis-events.ndjson), dòng 122 |

Các schema location được đối chiếu từ request/check/component, không giả làm tất cả pointer này đều do recorder ghi trực tiếp. JSON giữ metadata gốc để phân biệt. Dòng NDJSON đếm từ 1; cùng một ScenarioFinished chứa được nhiều case.

## 4. Đọc hai ví dụ khi báo cáo

GEN-04 cho phép dẫn từ UR-01 → BR-11/26 → schema POST → example của guided → case `qfqspn` → data object khác data array → finding contract candidate. Payload:

```json
{
  "title": "Guided Schemathesis article",
  "status": "draft",
  "score": 3,
  "published_at": null,
  "metadata": {"source": "guided", "fixture_version": "r06-k05-v2"},
  "internal_notes": "guided probe",
  "category": 1
}
```

`category=1` là giá trị lịch sử của case này. Triển khai/replay phải lấy map/producer của run mới; không chép số 1 thành fixture ID cố định. Controller đúng pin có nhánh object/readOne và array/readMany; vì vậy phải xem xét lỗi/thiếu sót schema trước khi kết luận Directus CRUD hỏng. Raw failure vẫn giữ nguyên.

GEN-05 cho phép giải thích stateful bằng bằng chứng cụ thể:

```text
MsrYGI: GET /items/qa_articles?deep={} → 200
  response data[*].id có ID 7
  transition is_inferred=true; is_transition_applied=true
Z6yNal: DELETE /items/qa_articles/7 → 204
```

Consumer có `parent_id=MsrYGI`; đây là chuỗi phụ thuộc hai request thật. Chưa phải bằng chứng một chuỗi POST→GET→PATCH→DELETE. Cần giữ response ID mới khi replay và không reset giữa hai bước.

## 5. Mẫu còn cần thiết kế/triển khai ở Phase 3–4

GEN-03 là mẫu **chứa biên** do fuzzing sinh, không phải ca do boundary coverage của công cụ được xác nhận. Trong coverage phase của hai pilot seed 101 đã xem, không có metadata ca biên số tương ứng để gọi là suite boundary đầy đủ. Không đổi nhãn một case ngẫu nhiên thành “đã test biên score/title”.

Bổ sung ca có kiểm soát: score -1/0/1/4/5/6; title 119/120/121 và name 79/80/81; query limit -2/-1/0/1, offset/page -1/0/1; các ca missing/null/empty tách riêng. Nguồn expected theo Phase 1/Q tương ứng, payload còn lại hợp lệ, có read-back. Đây là thiết kế, chưa có kết quả chạy.

Khi chọn thêm mẫu, giữ cả ví dụ thành công và thất bại; không chỉ chọn failure đẹp để trình bày. Không tính tổng dòng trong danh mục này thành tổng số test campaign hoặc số defect. Header Authorization/Cookie bị loại khỏi trích xuất; không dùng lại token lịch sử từ artifact gốc khi replay.
