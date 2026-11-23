# Đáp án gợi ý và cách suy luận

Đây không phải output để chép nguyên văn. Khi kết quả chạy của bạn khác ví dụ, giữ run/artifact và giải thích khác biệt theo version, schema hash, fixture và config.

## Bài 1

Một hướng đúng:

```text
ID: S6/reader-write
Mục tiêu: Reader không làm thay đổi article.
Precondition: service healthy, fixture có article mục tiêu, Reader/Editor login,
              Reader schema cho phép probe operation theo quy tắc harness.
Steps: Editor đọc snapshot -> Reader PATCH score -> Editor đọc lại.
Expected: PATCH bị từ chối theo baseline; read-back == snapshot.
Oracle: status PATCH, deep equality bản ghi trước/sau, response/log/report.
Cleanup: không cần sửa target nếu unchanged; dọn dữ liệu tạm nếu có.
Evidence: run metadata, scenario report, response đã redaction, run_id.
```

Chỉ assertion `4xx` chưa đủ vì server có thể trả lỗi nhưng vẫn ghi side effect trước khi trả response; read-back mới kiểm tra bất biến dữ liệu.

## Bài 2

Ví dụ bảng `score`:

| Nhóm | Giá trị |
|---|---|
| Biên hợp lệ thấp | `0` |
| Hợp lệ giữa | `3` |
| Biên hợp lệ cao | `5` |
| Ngoài miền | `-1`, `6` |
| Sai kiểu | `"3"`, `3.5`, `{}` |

`title` nên có rỗng, 1, 120, 121 ký tự; `status` có `draft`, `published`, chuỗi khác, null và sai kiểu. Expected phải đối chiếu validation/schema/runtime baseline; không tự tuyên bố mọi sai kiểu phải `400` nếu chưa xác minh.

## Bài 3

Actor không suy ra được chỉ từ request nếu token đã redacted; phải biết token được cấp cho actor nào từ harness metadata. `filter` giới hạn published, `fields` là projection, `sort=-id` giảm dần theo ID, `limit=2` lấy tối đa 2, `offset=0` bắt đầu từ đầu.

Expected phải tính từ fixture map và snapshot cố định. Status `200` vẫn có thể sai nếu lọt draft, lộ field, sai thứ tự, sai số lượng, body sai schema hoặc content type sai.

## Bài 4

Inventory đã xác minh: admin `14`, editor `14`, reader `6`, anonymous `0`. Campaign chọn 10 operation trong editor schema, nên hai con số khác nhau.

10 operation là GET/POST list và GET/PATCH/DELETE detail cho `qa_articles`, cộng cùng nhóm cho `qa_categories`. Nếu Reader không có PATCH trong schema, scenario ghi `blocked` vì operation bị lọc và không gửi request có chủ đích ngoài contract export. Đó không phải bằng chứng Reader đã nhận quyền hoặc đã bị từ chối.

## Bài 5

- H1 chọn **raw**, vì cần quan sát contract gốc và không muốn example/overlay thay đổi input contract.
- H2 chọn **guided**, vì cần fixture ID/body hợp lệ và đường đi nghiệp vụ.

Phải lưu raw source bất biến, source hash, target/overlay hash, diff, profile, fixture version, operation allowlist, seed/budget và report riêng. Guided không được overwrite raw hoặc gộp kết quả vào raw.

## Bài 6

Pseudo-code tốt:

```text
before = Editor GET article with all relevant fields
assert before exists and precondition is correct
response = Editor PATCH {score: 5}
assert response is accepted by baseline
after = Editor GET same article
assert after.score == 5
for field in [title, status, metadata, category]:
    assert after[field] == before[field]
record expected/actual on failure
delete temporary article in cleanup
```

Nếu PATCH bị từ chối, invariant phải phân nhánh theo actor/oracle; không coi request denied là positive update. Không dùng ID cứng, phải lấy ID từ response/fixture map.

## Bài 7

Phân loại tạm thời: **aggregate robustness candidate**, có thể liên quan product hoặc contract, chưa phải defect đã xác minh.

Cần bổ sung actor/permission, schema hash, Directus image/version/digest, harness SHA, request tối thiểu đã redaction, response/log, fixture state, nhiều lần replay và controls. Controls cho thấy lỗi phụ thuộc shape, nhưng chưa chứng minh expectation của API là “mọi shape lạ phải non-5xx” hay schema có mô tả shape đó. Cần đối chiếu source contract và behavior baseline.

## Bài 8

Có thể replay final interaction nếu dựng được ID/precondition tương ứng, nhưng đó là `sequence_replayed=false` và `final_interaction_only`. Chưa chứng minh category/article đã được tạo bởi chuỗi nguồn, thứ tự transition và state trước PATCH.

Muốn full replay cần event/sequence artifact chứa parent requests, response IDs, dependency links, actor, fixture reset/setup và expected từng transition. Nếu parent artifact không có, ghi unresolved/limitation, không gọi full stateful reproduced.

## Bài 9

Không có một output status cố định cho mọi máy. Câu trả lời đúng phải trích run thực tế. Với trạng thái đã quan sát của repository:

- scenario final `20261011T171054Z-225602`: pass `S1–S6`;
- invariant `20261011T171247Z-226528`: exit `1`, `9 passed/2 failed/0 blocked`;
- raw/guided pilot/full campaign: failed hoặc incomplete, không gọi PASS toàn bộ.

Kết luận được phép: “pipeline đã chạy và lưu evidence; scenario đạt trong run X.” Kết luận chưa được phép: “Directus không còn lỗi” hoặc “đã đạt full coverage” khi campaign còn failure/budget chưa hoàn tất.

## Bài 10

Một câu trả lời đạt yêu cầu phải nêu được:

- smoke kiểm khả dụng cơ bản, K05 sinh/kiểm nhiều request từ OpenAPI;
- raw giữ contract, guided dùng overlay có chủ đích;
- schema coverage không phải line/branch coverage;
- schema theo actor tránh dùng quyền admin đại diện cho Reader;
- check failure cần grouping/triage, không bằng số bug.

