# Bài 4 — OpenAPI và schema theo actor

## 4.1. Schema là hợp đồng, không phải toàn bộ hệ thống

OpenAPI mô tả các operation, parameter, request body, response, media type và một phần validation. Nó giúp Schemathesis biết request nào có thể sinh và response nào được coi là phù hợp contract.

Schema không tự mô tả đầy đủ:

- dữ liệu hiện có trong database;
- quan hệ giữa nhiều request;
- dữ liệu nào là draft/published theo nghiệp vụ;
- mọi rule policy động;
- invariant “PATCH một field không làm mất field khác”;
- side effect hoặc cleanup.

Vì vậy, schema conformance và scenario/invariant là hai lớp bổ sung, không thay thế nhau.

## 4.2. Vì sao phải export theo actor?

Directus có thể lọc operation/field theo quyền. Một schema admin không thể đại diện cho Reader. Lần export đã xác minh trong lab ghi nhận:

| Actor | Số operation trong schema |
|---|---:|
| Admin | 14 |
| Editor | 14 |
| Reader | 6 |
| Anonymous | 0 |

Con số này là **inventory export**, không phải số operation campaign chính. Campaign chính chọn 10 method–path của Editor:

| Collection | List | Detail |
|---|---|---|
| `qa_articles` | `GET`, `POST` | `GET`, `PATCH`, `DELETE` |
| `qa_categories` | `GET`, `POST` | `GET`, `PATCH`, `DELETE` |

Tổng là `5 + 5 = 10`. Reader chỉ có 6 operation không có nghĩa Reader đã được gửi PATCH để chứng minh cấm; nếu operation không có trong schema Reader, harness phải ghi bị block do operation bị lọc.

## 4.3. Raw schema và bất biến

Luồng đúng:

1. Seed schema/permission/fixture.
2. Đăng nhập từng actor.
3. Gọi `GET /server/specs/oas` với token của actor.
4. Kiểm OpenAPI hợp lệ.
5. Lưu canonical snapshot theo actor và `sha256`.
6. Không overwrite raw snapshot nếu hash đổi mà chưa có lý do.

`raw` phải giữ nội dung contract gốc trong phạm vi 10 operation. Nếu cần giới hạn operation hoặc thêm dữ liệu hướng dẫn, tạo file overlay riêng, kèm source hash, target hash, diff và lý do.

## 4.4. Guided overlay

Guided không được sửa âm thầm raw. Trong harness hiện tại, overlay guided:

- giới hạn paths/methods về 10 operation được duyệt;
- thêm example ID hợp lệ từ fixture map;
- thêm example body hợp lệ cho POST/PATCH;
- ghi query focus `fields`, `filter`, `sort`, `limit`, `offset`, `page`, `search`;
- giữ raw source và diff.

Mục tiêu là tăng reachability vào nghiệp vụ, không biến một response không phù hợp thành hợp lệ. Kết quả guided phải được báo riêng, không gộp vào raw.

## 4.5. Hash dùng để làm gì?

Hash giúp phát hiện contract đầu vào đã đổi:

```text
schema_hash = SHA-256(canonical-schema.json)
```

Nếu cùng một case replay nhưng schema hash khác, chưa thể nói đó là regression cùng điều kiện. Metadata phải ghi source schema, profile, actor và hash. Hash không chứng minh schema đúng; nó chỉ chứng minh file nào đã được dùng.

## 4.6. Đọc một operation

Khi học OpenAPI, hãy tìm các thành phần:

```yaml
paths:
  /items/qa_articles/{id}:
    patch:
      parameters:
        - name: id
          in: path
          required: true
      requestBody:
        content:
          application/json:
            schema: ...
      responses:
        '200':
          content:
            application/json:
              schema: ...
```

Đừng chỉ đọc `responses['200']`. Cần xem parameter bắt buộc, allowed methods, request shape, nullable/type, content type, response shape và security/policy context.

## 4.7. Liên hệ với failure thực tế

Một số finding của campaign/invariant được phân loại candidate vì contract và runtime chưa thống nhất hoàn toàn, ví dụ:

- POST object/array shape;
- media type/shape của export CSV, XML, YAML;
- DELETE detail trả `204` so với schema;
- projection có thể làm thiếu field response schema yêu cầu;
- query aggregate shape không được schema mô tả đủ.

Đây là lý do phải lưu request/response, schema hash, version và source comparison. Không nhìn một check failure rồi kết luận ngay “Directus lỗi”.

## 4.8. Thực hành export

```bash
./lab.sh up
./lab.sh seed
./lab.sh export-schema
```

Sau đó tìm run mới nhất và kiểm:

1. Có `schema-admin.json`, `schema-editor.json`, `schema-reader.json` và anonymous record không?
2. `schema-manifest.json` ghi hash/count/operation không?
3. Editor có đúng inventory 14 export và campaign allowlist 10 không?
4. Raw snapshot có bị overwrite bất ngờ không?

Không in `config/lab.env`; chỉ xem metadata đã redaction.

## 4.9. Câu hỏi tự kiểm tra

- Vì sao schema Reader có 6 operation mà campaign chính vẫn có 10?
- Khi nào một overlay là hợp lệ về phương pháp?
- Schema nói response có `score` nhưng query `fields` loại `score`; cần điều tra những lớp nào?
- Hash thay đổi có tự động là defect không?

Đọc tiếp: [Bài 5 — K05 và Schemathesis](05_k05_schemathesis.md).

