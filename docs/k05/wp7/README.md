# WP7 — gom nhóm, phân loại và root cause của failure (C5)

Nguồn: NDJSON và `campaign-summary.json` của 18 seed WP5, gom bằng [scripts/k05_failure_triage.py](../../../scripts/k05_failure_triage.py); nguyên nhân gốc xác nhận bằng replay trên lab local `r06-k05` (Directus 12.5.0, commit `4f77933`, Schemathesis 4.30.0) bằng [scripts/k05_wp7_replay.py](../../../scripts/k05_wp7_replay.py), có đối chiếu mã nguồn tại đúng commit đã pin.

| File | Nội dung |
|---|---|
| [failure-groups.csv](failure-groups.csv) | 237 nhóm: nguyên nhân gốc, loại, actor, operation, check, mã phản hồi, số lần, profile, seed |
| [failure-stats.json](failure-stats.json) | Ba con số (request, check fail, nhóm), thống kê theo seed, actor, nguyên nhân; thống kê 932 tương tác 5xx |
| [group-exemplars.json](group-exemplars.json) | Mỗi nhóm một request/phản hồi mẫu (đã bỏ header Authorization) |
| [replay-results.json](replay-results.json) | 67 probe có chủ đích, 15 thông điệp lỗi gốc do admin nhận được, xác nhận `qa_*` trở lại như cũ |
| [server-log-excerpt.txt](server-log-excerpt.txt) | Trích log server (loại lỗi và khung stack) của các phản hồi 500 khi replay |

## 1. Kết quả

- **C5 đạt**: 1.356 lần check thất bại của 18 seed được gom thành 237 nhóm; **mọi nhóm đều có nguyên nhân gốc và loại phân loại** (không còn nhóm chưa phân loại) và mỗi nguyên nhân có reproducer (mục 4).
- Có **16 nguyên nhân gốc**: 10 thuộc sản phẩm (RC01 đến RC05, RC12 đến RC16), 5 thuộc schema (RC06 đến RC10), 1 chưa kết luận (RC11). Không nhóm failure nào thuộc harness, fixture hay môi trường.
- **Chín nguyên nhân sản phẩm đã được xác nhận bằng replay và thông điệp lỗi gốc phía server**: đầu vào sai từ client làm Directus trả `500` thay vì `4xx` (RC01 đến RC04, RC12 đến RC16). Chúng giải thích **923 trong 932 tương tác 5xx** (99,0%) của 18 seed; 9 tương tác còn lại chưa tái hiện được (mục 6). Đây cũng là toàn bộ 13 cặp có phản hồi 5xx ở WP5 và đóng finding P5-F01 (aggregate).
- RC05 (TRACE trả `404`) là hành vi sản phẩm mức thấp, chưa rõ có chủ ý hay không.

## 2. Các con số khác nhau (không được đánh đồng)

| Đại lượng | Giá trị | Nghĩa |
|---|---:|---|
| Request ghi trong NDJSON | 31.147 | tương tác HTTP thực sự được gửi (WP5 ghi 30.589 vì chỉ đếm request cùng phương thức với operation) |
| Lần check được chạy | 177.096 | mỗi request chạy nhiều check |
| **Lần check thất bại** | **1.356** | một request có thể thất bại nhiều check |
| "Failure duy nhất" do Schemathesis gom | 1.011 (cộng 18 seed) | cách gom riêng của công cụ, trùng lặp giữa các seed |
| **Nhóm failure (mục 3)** | **237** | gom theo actor, operation, check, mã phản hồi, nguyên nhân |
| **Tương tác có phản hồi 5xx** | **932** | trong đó chỉ **31** lần được Schemathesis ghi thành check `ServerError` (xem giới hạn) |
| **Nguyên nhân gốc** | **16** (10 sản phẩm, 5 schema, 1 chưa kết luận) | mức độ phân biệt của phân loại |

Các bảng này **không** nói Directus chỉ có 10 lỗi: chỉ có các lỗi mà schema Directus xuất ra và bộ sinh dữ liệu của Schemathesis chạm tới trong ngân sách WP5.

Theo nhóm chạy (request / lần check thất bại): Editor raw 347 / 251, Editor guided 23.840 / 457, Reader raw 289 / 194, Reader guided 6.476 / 292, Anonymous raw 96 / 81, Anonymous guided 99 / 81.

## 3. Bảng nguyên nhân gốc

"Lần check" và "nhóm" là số trong `failure-groups.csv`. "Tương tác 5xx" là số tương tác ghi trong NDJSON có phản hồi 5xx và thuộc nguyên nhân đó (`server_error_interactions` trong `failure-stats.json`).

| Mã | Loại | Nguyên nhân | Lần check | Nhóm | Tương tác 5xx |
|---|---|---|---:|---:|---:|
| RC01 | **Sản phẩm** | ID ngoài khoảng `int4` (> 2.147.483.647 hoặc < −2.147.483.648) trong đường dẫn: lỗi DB không được dịch, trả `500` (GET/PATCH/DELETE theo ID) | 28 | 14 | 78 |
| RC02 | **Sản phẩm** | `aggregate` sai cấu trúc (giá trị không phải mảng/chuỗi, hoặc không phải JSON): `TypeError`, trả `500` | 24 | 8 | 695 |
| RC03 | **Sản phẩm** | `published_at` không phải ngày giờ (`false`, `true`, `"abc"`, số): lỗi PostgreSQL 22007 không được dịch, trả `500` | 4 | 2 | 11 |
| RC04 | **Sản phẩm** | Chuỗi chứa ký tự NUL (U+0000), ở body hoặc `search=a%00b`: lỗi PostgreSQL 22021 không được dịch, trả `500` | 6 | 2 | 94 |
| RC12 | **Sản phẩm** | Phần tử `null` trong mảng body của `POST`: `TypeError: Cannot read properties of null (reading 'id')` | 0 | 0 | 4 |
| RC13 | **Sản phẩm** | `id` hoặc khóa ngoại sai kiểu (`true`, `""`, `"abc"`, mảng) hoặc số ≥ 1e21 (JavaScript viết dạng mũ): lỗi PostgreSQL 22P02 không được dịch | 0 | 0 | 36 |
| RC14 | **Sản phẩm** | `export=csv` kèm `fields` trỏ tới đường dẫn không có thật (`sections.item:headings.title`) | 0 | 0 | 3 |
| RC15 | **Sản phẩm** | `page` × `limit` vượt giới hạn `bigint` (`value "15787825890584429000" is out of range for type bigint`) | 0 | 0 | 1 |
| RC16 | **Sản phẩm** | `groupBy` có `)` đặt trước `(` (ví dụ `a)b(`): `TypeError: Cannot read properties of null (reading '1')` | 0 | 0 | 1 |
| RC05 | Sản phẩm (mức thấp) | Phương thức không hỗ trợ (TRACE, PUT) trả `404 ROUTE_NOT_FOUND` thay vì `405` | 180 | 30 | không áp dụng |
| RC06 | Schema | Schema mô tả `200` nhưng Directus trả `204 No Content` | 134 | 16 | không áp dụng |
| RC07 | Schema | Schema không mô tả các mã lỗi 4xx mà Directus trả (400, 401, 403, 404, 415...) | 653 | 75 | không áp dụng |
| RC08 | Schema | `Content-Type` khác schema (`/server/ping` trả `text/html`; `export=csv\|xml\|yaml`) | 51 | 15 | không áp dụng |
| RC09 | Schema | Schema phản hồi quá cứng: `fields` làm đổi hình dữ liệu, `POST` trả đối tượng thay vì mảng, `export=json` trả mảng trần | 43 | 26 | không áp dụng |
| RC10 | Schema | Request hợp lệ theo schema nhưng bị từ chối: ràng buộc runtime không có trong schema (`otp` rỗng, thiếu `refresh_token`, multipart, thiếu `item`/`to`) | 222 | 42 | không áp dụng |
| RC11 | Chưa kết luận | Dữ liệu hoặc tham số sai nhưng được chấp nhận (tham số lạ bị bỏ qua; `PATCH` chỉ có `{id}`) | 11 | 7 | không áp dụng |
| (chưa tái hiện) | Chưa kết luận | 9 tương tác 5xx của `GET /items/qa_categories`: 1 có `fields` chứa ký tự điều khiển, 8 có `offset` rất lớn kèm `export=xml&page=2`; replay nguyên văn (kể cả `offset=181036343237512&export=xml&page=2`) trả `200` | 0 | 0 | 9 |

Tổng lần check theo loại: schema 1.103, sản phẩm 242, chưa kết luận 11. Các phản hồi `500` cũng làm kích hoạt thêm check `UndefinedStatusCode`; những lần này được tính vào cùng nguyên nhân với `ServerError` (RC01 đến RC04), không tính vào RC07. RC12 đến RC16 không có nhóm failure nào vì Schemathesis chỉ giữ một failure `ServerError` cho mỗi operation trong một seed; các nguyên nhân này lộ ra khi đếm trực tiếp 932 tương tác 5xx.

**Vì sao RC06 đến RC10 là lỗi schema chứ không phải lỗi sản phẩm:** schema OpenAPI do `GET /server/specs/oas` của Directus sinh ra chỉ mô tả một phần hành vi (chủ yếu `200` và vài mã lỗi). Việc Directus trả `204` cho `DELETE`, trả `403` khi thiếu quyền, hay từ chối `otp: ""` là hành vi nhất quán của máy chủ; điều lệch là **tài liệu hợp đồng**. Đây là nhận định theo đối chiếu hành vi (bằng chứng ở mục 5), không phải kết luận rằng Directus phải sửa schema.

## 4. Reproducer

Điều kiện chung: lab `r06-k05` đã `up` và seed (3 category, 12 article, id 1 đến 12); `$EDITOR_TOKEN`, `$READER_TOKEN`, `$ADMIN_TOKEN` lấy bằng `POST /auth/login` với tài khoản trong `config/lab.env` (không ghi vào tài liệu). Máy chủ `http://127.0.0.1:8055`. Phiên bản: Directus 12.5.0, commit `4f77933`. Mọi thông điệp "admin thấy" có trong `replay-results.json` (`admin_evidence`).

| Mã | Actor | Request | Mong đợi | Thực tế |
|---|---|---|---|---|
| RC01 | editor, reader | `GET /items/qa_articles/9999999999` (cũng `PATCH`, `DELETE`) | `4xx`. Đối chiếu: cùng giá trị trong body của `POST` được trả `400 VALUE_OUT_OF_RANGE`; ID `2147483647` trả `403` | `500`; admin thấy `value "9999999999" is out of range for type integer` |
| RC02 | editor, reader | `GET /items/qa_articles?aggregate={"foo":1}` (cũng `aggregate=abc`) | `400 INVALID_QUERY`. Đối chiếu: `aggregate=[]` trả `400 "aggregate" must be of type object` | `500`; admin thấy `fields is not iterable` (với `abc`: `Cannot assign to read only property '0' of string 'abc'`) |
| RC03 | editor | `POST /items/qa_articles` body `{"title":"x","score":1,"published_at":false}` (cũng `true`, `"abc"`, `123`; `PATCH` cũng bị) | `400`. Đối chiếu: `"2026-11-24T00:00:00Z"` trả `200` | `500`; admin thấy `invalid input syntax for type timestamp with time zone: "false"` |
| RC04 | editor | `POST /items/qa_categories` body `{"name":"a\u0000b"}`; hoặc `GET /items/qa_categories?search=a%00b` | `400`. Đối chiếu: `\u0019` và `%08` được `200` | `500`; admin thấy `invalid byte sequence for encoding "UTF8": 0x00` |
| RC12 | editor | `POST /items/qa_categories` body `[null]` | `400` | `500`; admin thấy `Cannot read properties of null (reading 'id')` |
| RC13 | editor | `POST /items/qa_categories` body `{"name":"x","id":true}` (cũng `""`, `1e21`); `POST /items/qa_articles` với `"category":{"id":"abc"}` | `400`. Đối chiếu: `id` = `100000000000000000000` (1e20, còn dạng số nguyên) trả `400 VALUE_OUT_OF_RANGE` | `500`; admin thấy `invalid input syntax for type integer: "true"` / `"1e+21"` / `"abc"` |
| RC14 | editor | `GET /items/qa_articles?fields=sections.item:headings.title&export=csv` | `4xx` hoặc CSV. Đối chiếu: `export=csv` không có `fields` trả `200` | `500`; admin thấy `Data should not be empty or the "fields" option should be included` |
| RC15 | editor | `GET /items/qa_articles?limit=897434&page=17592186044417` | `4xx`. Đối chiếu: `limit=100&page=1000000` trả `200` | `500`; admin thấy `value "15787825890584429000" is out of range for type bigint` |
| RC16 | editor | `GET /items/qa_articles?groupBy=a)b(` | `400`. Đối chiếu: `groupBy=year(published_at)` trả `200`; `groupBy=a(b` trả `400` | `500`; admin thấy `Cannot read properties of null (reading '1')` |
| RC05 | editor | `TRACE /items/qa_articles` hoặc `PUT /items/qa_articles/1` | `405 Method Not Allowed` (Schemathesis kỳ vọng cho phương thức không liệt kê) | `404 ROUTE_NOT_FOUND` cả với đường dẫn tồn tại |
| RC06 | editor | `DELETE /items/qa_articles/{id}` của một bài có thật | schema mô tả `200` | `204` không có body |
| RC07 | editor | `GET /items/qa_articles/999999` | schema mô tả `404` | `403 FORBIDDEN` (kể cả admin; xem mục 5.2) |
| RC08 | editor | `GET /server/ping`; `GET /items/qa_articles?export=csv` | schema mô tả `application/text` và `application/json` | `text/html`; `text/csv` |
| RC09 | editor | `GET /items/qa_articles/7?fields=title,author.name` | schema phản hồi yêu cầu `score` và các trường bắt buộc | `data` chỉ có `title` (nhóm mẫu trong `group-exemplars.json`) |
| RC10 | editor | `POST /auth/login` body `{"email":"…","password":"…","mode":"json","otp":""}` | schema chấp nhận | `400 INVALID_PAYLOAD` (`otp` không được rỗng) |
| RC11 | editor | `PATCH /items/qa_articles/{id}?fields=false` body `{"id": …}` | `4xx` (check `negative_data_rejection`) | `200`/`204` |

Reproducer của RC06 đến RC11 dựa trên request mẫu của từng nhóm (`group-exemplars.json`) và đối chiếu hành vi, không phải replay riêng cho từng operation. Replay tự khôi phục: `qa_*` trở lại 3 category và 12 article (`state_restored: true`).

## 5. Nguyên nhân gốc của các lỗi sản phẩm và các quan sát khác

### 5.1 Lỗi cơ sở dữ liệu không được dịch, `TypeError` không được chặn

Tại commit đã pin, `api/src/database/errors/dialects/postgres.ts` (hàm `extractError`) chỉ chuyển lỗi PostgreSQL thành lỗi Directus cho năm mã: `23505` (trùng khóa), `22003` (số ngoài khoảng), `22001` (quá dài), `23502` (null), `23503` (khóa ngoại). Mã khác rơi vào nhánh `default` và thành `500`. Log server khi replay ghi đúng các mã `22003`, `22007` (RC03), `22021` (RC04), và `22P02` (RC13) là những mã không được dịch.

- **RC01.** `translateDatabaseError` chỉ được gọi ở hai nơi trong `api/src/services/items.ts`: câu `INSERT` của `createOne` (dòng 273) và câu ghi của `updateMany` (dòng 849). Vì vậy khi **ghi** body có `id` ngoài `int4`, lỗi `22003` được dịch thành `400 VALUE_OUT_OF_RANGE` (replay xác nhận). Khi ID ngoài `int4` nằm **trong đường dẫn**, lỗi phát sinh ở các câu `SELECT` (đọc theo ID, và kiểm tra quyền trước khi sửa/xóa: log ghi `select 1 as "id" from "qa_articles" where ("qa_articles"."id" in ($1))`) và ở `deleteMany`, không đi qua bước dịch, nên thành `500`. Cùng một lỗi `22003` cho hai kết quả khác nhau tùy đường xử lý.
- **RC13.** Số nguyên từ 1e21 trở lên được JavaScript viết dạng mũ (`"1e+21"`), nên PostgreSQL báo `22P02` (cú pháp) thay vì `22003`; đây là lý do `id` = `100000000000000000000` ra `400` còn `1e21` ra `500`. Cùng nhóm: `id` hoặc `category.id` sai kiểu.
- **RC03, RC04** (`22007`, `22021`) và **RC15** (`bigint` tràn ở `offset`) cũng là lỗi DB không được dịch. RC04 xảy ra cả khi NUL nằm trong `search` của query string.
- **RC02.** `sanitizeAggregate` (`api/src/utils/sanitize-query.ts`, dòng 144 đến 164) chỉ chuyển giá trị kiểu chuỗi và mảng; giá trị khác (số `1`) giữ nguyên, rồi `extractPathsFromQuery` (`api/src/permissions/modules/process-ast/utils/extract-paths-from-query.ts`, dòng 59 đến 61) lặp `for (const field of fields)` và gặp `TypeError: fields is not iterable`. Với `aggregate=abc`, `parseJSON` thất bại, `aggregate` vẫn là chuỗi, và phép gán `aggregate[operation] = …` trên chuỗi gây `TypeError`.
- **RC12, RC16** là `TypeError` do giả định đầu vào hợp lệ (phần tử body khác `null`; `groupBy` có ngoặc cân đối); **RC14** là lỗi của bộ xuất CSV khi `fields` không cho cột nào. Tôi chưa đọc mã tương ứng của ba nguyên nhân này; kết luận dựa trên thông điệp lỗi gốc của admin.

Khung stack ghi trong log server khi replay: `extractPathsFromQuery`, `extractFieldsFromQuery`, `fieldMapFromAst`, `processAst`, `ItemsService.readByQuery` (RC02), `sanitizeAggregate`, `sanitizeQuery` (`aggregate=abc`) và `DatabaseError` từ `pg-protocol` (RC01, RC03, RC04, RC13, RC15). Xem [server-log-excerpt.txt](server-log-excerpt.txt). Admin nhận thông điệp lỗi gốc trong thân `500` (có cả câu SQL), còn editor và reader chỉ nhận `An unexpected error occurred.`.

**Mức độ:** dữ liệu không bị hỏng (lỗi xảy ra trước hoặc trong lúc ghi, giao dịch bị hủy; kiểm tra `qa_*` sau replay không đổi); ảnh hưởng là máy chủ trả `500` cho đầu vào sai mà người gọi có quyền gửi. Tôi xếp mức trung bình về độ bền vững (robustness), chưa đánh giá ý nghĩa bảo mật.

### 5.2 Các quan sát đóng các câu hỏi mở của WP5 và WP6

| Quan sát | Kết luận | Bằng chứng |
|---|---|---|
| Reader nhận `200`/`204` trên `PATCH /items/qa_articles/{id}` | **Hành vi theo cấu hình fixture, không phải lỗi sản phẩm.** Policy Reader có quyền `update` với `fields=[]`: `PATCH {}` trả `204`, `PATCH {"title":…}` trả `403`; Editor `PATCH {}` trả `200` | replay nhóm H5 |
| ID không tồn tại bị `403` thay vì `404` | **Xác nhận** (giả thuyết của WP6): `GET`/`DELETE`/`PATCH` trên ID `999999` trả `403` kể cả khi dùng admin. Đây là cách Directus không để lộ việc một ID có tồn tại hay không; schema lại mô tả `404` nên là RC07 (schema) | replay nhóm H1 |
| `utils/sort` luôn `400` | Request tới được handler nhưng thiếu `item`/`to` bắt buộc, và `qa_articles` không có trường sắp xếp (`Collection "qa_articles" doesn't have a sort field`); schema không mô tả hai điều này (RC10). Không phải lỗi sản phẩm | replay nhóm H6 |
| "Case lỗi chạy" của guided (Editor 257 đến 404, Reader 12 đến 31) | Mỗi seed, số này **bằng đúng** số case của kịch bản stateful đã sinh mà không có tương tác HTTP nào (18/18 seed khớp, tổng 1.069). Không có lỗi kết nối hay lỗi vận hành; `errors` của report rỗng. Nguyên nhân Schemathesis không gửi những case này chưa xác định, nhưng không liên quan tới phản hồi của Directus | `cases_without_response` trong `failure-stats.json` |
| `GET /items/qa_articles?fields=sections.item:headings.title` trả `200` với danh sách khóa chính | **Chưa kết luận.** Trường quan hệ `sections` không tồn tại nhưng không bị từ chối (trong khi `year(date_published)` bị `403`). Có thể thiếu kiểm tra; chưa đủ bằng chứng để gọi là lỗi. Cùng tham số này kết hợp `export=csv` thì gây RC14 | replay nhóm H3, H8 |

## 6. Giới hạn

- **Schemathesis chỉ giữ một failure cho mỗi (operation, loại, thông điệp) trong một seed**, nên 237 nhóm che mất sự đa dạng: 31 check `ServerError` đại diện cho 932 tương tác 5xx và chỉ thấy bốn trong chín nguyên nhân sản phẩm. Vì vậy tôi đếm thêm trực tiếp trên 932 tương tác. Số nhóm 237 phụ thuộc cách chuẩn hóa thông điệp (thay số bằng `<n>`); số nguyên nhân gốc thì không.
- **Phân loại 5xx dựa trên quy tắc suy từ chính request** (ID trong đường dẫn, `aggregate`, NUL, kiểu của `published_at` và `id`, `groupBy`, `page`×`limit`, `export=csv`+`fields`). Mỗi quy tắc đã được xác nhận bằng một probe riêng, nhưng quy tắc theo thứ tự ưu tiên: một request chứa hai nguyên nhân được gán cho nguyên nhân đứng trước. Tập quy tắc có kiểm thử đơn vị trong `tests/test_failure_triage.py`.
- **9 tương tác 5xx chưa được lý giải** (cả 9 là `GET /items/qa_categories` trong guided: 1 với `fields` chứa ký tự điều khiển, 8 với `offset` rất lớn, `export=xml` và `page=2`; replay nguyên văn trên lab sạch trả `200`). Có thể phụ thuộc trạng thái của bảng lúc đó (các run guided đã tạo thêm nhiều dòng); chưa kiểm chứng.
- Chỉ xác nhận nguyên nhân cho các nhóm mà request mẫu và replay tái hiện được. RC05 đến RC11 dựa trên đối chiếu hành vi và request mẫu của từng nhóm, chưa có reproducer riêng cho từng operation.
- Phân loại "schema" nghĩa là hợp đồng OpenAPI không khớp hành vi quan sát được; không có nghĩa tài liệu chính thức của Directus nói khác.
- RC05 có thể là thiết kế của Express/Directus; RC11 có thể là chủ ý (Directus bỏ qua tham số truy vấn lạ).
- Chưa có người thứ hai tái hiện các reproducer; chỉ có lần replay trên lab này.
- Các phát hiện sản phẩm chưa được báo cho Directus upstream và chưa kiểm tra xem phiên bản mới hơn có sửa chưa.
- Probe `POST` với `id=500000` (nhóm H4) làm dãy tự tăng của `qa_articles` nhảy lên, nên bài tạo mới sau đó có ID từ khoảng 500.000 (ví dụ 500.014 trong run `20261124T063913Z-1590`). Fixture (ID 1 đến 12) không bị ảnh hưởng và không test nào giả định ID tạo mới.

## 7. Tái lập

```powershell
python scripts/k05_failure_triage.py          # đọc artifacts/runs của 6 run WP5, ghi lại failure-*.json/csv
.\scripts\run-lab.ps1 up
python scripts/k05_wp7_replay.py              # replay có chủ đích (chỉ loopback), ghi replay-results.json
python -m unittest discover -s tests -p "test_*.py"
```
