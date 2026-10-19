# Bài 6 — Scenario, invariant và harness

## 6.1. Vì sao cần lớp bổ trợ?

OpenAPI nhìn từng operation. Nghiệp vụ thường nói về **quan hệ giữa nhiều request** và **trạng thái dữ liệu**. Ví dụ “tạo xong đọc được”, “PATCH một field không làm mất field khác”, “request bị từ chối không đổi dữ liệu” không thể được chứng minh chỉ bằng response schema của một request.

- **Scenario**: chuỗi bước có mục tiêu nghiệp vụ rõ, thường dễ demo.
- **Invariant**: thuộc tính phải luôn giữ sau một thao tác/chuỗi, thường được kiểm bằng Python.
- **Harness**: mã điều phối actor, URL, token, fixture map, request, oracle, cleanup và artifact.

## 6.2. Sáu scenario giữa kỳ

| ID | Mục tiêu | Oracle chính |
|---|---|---|
| S1 | CRUD Editor | Create/read/update/delete đúng; cleanup đạt |
| S2 | Filter status | Kết quả phù hợp fixture published/draft |
| S3 | Sort + pagination | Thứ tự/trang đúng trên dữ liệu cố định |
| S4 | Reader không đọc draft | Không trả draft theo semantics baseline |
| S5 | Không lộ `internal_notes` | Projection/response Reader không lộ field kín |
| S6 | Reader ghi bị từ chối | PATCH Reader bị từ chối; Editor read-back cho thấy dữ liệu không đổi |

Lần chạy scenario cuối đã xác minh `20261011T171054Z-225602`: `S1–S6` pass; S6 ghi đúng `PATCH 403`, read-back `200`, target unchanged. Một run trung gian ghi `actual=HTTP 200` do biến trạng thái PATCH bị read-back ghi đè; đó là bằng chứng harness/report bug đã được sửa, không phải bằng chứng Reader được cấp quyền.

## 6.3. Precondition không phải hình thức

Trước scenario cần kiểm:

- service healthy;
- actor login thành công;
- schema cần operation tồn tại;
- fixture map có ID thật;
- item là draft/published đúng mục tiêu;
- không có campaign khác đang ghi DB;
- run metadata đã tạo.

Nếu Reader schema không có `PATCH /items/qa_articles/{id}`, harness ghi `blocked` vì operation bị lọc và **không gửi request có chủ đích**. “Không gửi được request” khác với “đã gửi và bị từ chối”.

## 6.4. Invariant Python

[`scripts/invariants.py`](../../scripts/invariants.py) dùng standard library và tổ chức case có precondition/actor/oracle. Các nhóm hiện có gồm:

- `auth-invalid-token`;
- `anonymous-denied`;
- `editor-crud`;
- `positive-operations`;
- `query-fixture`;
- `aggregate-query-robustness`;
- `contract-schema-candidates`;
- `relation-nullification`;
- `invalid-field-rejection`;
- `reader-visibility`;
- `reader-write`.

Ví dụ logic của `reader-write`:

```text
1. Editor đọc snapshot của target.
2. Reader gửi PATCH có chủ đích trong điều kiện operation được phép probe.
3. Assert status là non-2xx theo oracle baseline.
4. Editor đọc lại target.
5. Assert bản ghi sau == bản ghi trước.
```

Nếu chỉ kiểm `status != 2xx`, vẫn thiếu assertion side effect. Nếu chỉ read-back bằng Reader, có thể quyền Reader che mất thay đổi; dùng Editor hoặc actor có quyền đọc chuẩn để làm oracle.

## 6.5. Positive và negative oracle

| Tình huống | Không đủ | Đủ hơn |
|---|---|---|
| Create | status `2xx` | status + body + đọc lại identity/fields + cleanup |
| PATCH | status `2xx` | field đổi đúng + field không gửi vẫn giữ nguyên |
| Delete | status `2xx` | đọc lại xác minh không còn theo semantics Directus |
| Denied write | status `4xx` | status + đọc lại chứng minh dữ liệu không đổi |
| Reader visibility | body `200` | filter published + field projection + không lộ field kín |
| Invalid field | không crash | status/response hợp oracle và dữ liệu không bị thay đổi ngoài ý muốn |

## 6.6. Query oracle trên fixture cố định

Để kiểm filter/sort/pagination:

1. Từ fixture map và seed, tạo expected set trong test code.
2. Dùng filter/sort/limit/offset/page.
3. So sánh ID/title/status với expected đã tính trước.
4. Kiểm tra projection: field ngoài projection không xuất hiện hoặc bị policy loại theo semantics.
5. Không tạo expected bằng cách copy response vừa nhận rồi so với chính nó.

Fixture gồm 3 category và 12 article, chia 6 draft/6 published, phân bố theo category, có Unicode và nullable. Chính tính cố định này giúp oracle có ý nghĩa.

## 6.7. Cleanup và độc lập

Mỗi case phải:

- tạo dữ liệu với prefix/run ID rõ;
- lưu ID thật từ response;
- xóa hoặc restore trong cleanup path;
- không dựa vào item do case trước tạo;
- không hard-code ID tự sinh;
- nếu cleanup fail, ghi failure riêng và không giấu.

Campaign có snapshot/restore rộng hơn scenario. Không reset giữa các bước của stateful sequence vì sẽ phá precondition của chuỗi.

## 6.8. Chạy và đọc invariants

```bash
./lab.sh test invariants
```

Lệnh có thể trả exit `1` dù phần lớn case pass. Trạng thái cuối đã quan sát:

```text
9 passed / 2 failed / 0 blocked
```

Hai nhóm mở là aggregate unknown shape HTTP `500` và contract/schema candidates. Đây là kết quả cần triage, không được đổi expected hoặc gán tất cả thành product defect.

## 6.9. Câu hỏi tự kiểm tra

- Vì sao Reader write cần Editor read-back?
- Khi operation Reader bị lọc khỏi schema, test nên ghi `blocked` hay `passed`?
- Fixture map giải quyết vấn đề gì?
- `PATCH` thành công nhưng title biến mất là loại failure nào trước khi triage?

Đọc tiếp: [Bài 7 — Failure, metrics và replay](07_failure_metrics_replay.md).

