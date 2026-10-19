# Triage pilot Schemathesis — 2026-10-11

Tài liệu này là triage kỹ thuật được chuẩn bị từ artefact đã chạy; không phải
review của Nhân/Trâm và không được ghi như xác nhận của thành viên khác. Review
chéo không phải điều kiện G1. Không dùng nó để đóng issue hay tuyên bố defect
sản phẩm khi chưa replay với precondition đúng.

## Provenance

- Run: `20261010T084748Z-98189`, `test schema-smoke`, exit `1`.
- Harness khi chạy: `1541fa119e9d06a3713ca7ce5e439f2962e5e79e`; working tree lúc
  chạy được metadata ghi là `dirty`.
- Baseline: Directus `12.5.0`, PostgreSQL `16-alpine`, Schemathesis `4.30.0`,
  digest trong [`manifest/baseline.yaml`](../manifest/baseline.yaml).
- Actor/fixture: schema editor, fixture `r06-k05-v1`, seed `101`; năm operation
  `qa_articles` được chọn bằng overlay tạm. Schema raw giữ nguyên.
- Artefact gốc: [`run.log`](../artifacts/runs/20261010T084748Z-98189/run.log),
  [`schemathesis-report.json`](../artifacts/runs/20261010T084748Z-98189/schemathesis-report.json),
  [`schemathesis-coverage.json`](../artifacts/runs/20261010T084748Z-98189/schemathesis-coverage.json).

## Kết quả đã quan sát

Pilot đã thực thi `5/5` operation, sinh `1.413` case, có `9` case chứa failure,
`11` failure riêng biệt, `0` errored và dừng vì `max-time=300s`. Snapshot article
được khôi phục thành công. Coverage operation là `5/5`; đây không phải kết luận
đã đạt coverage nghiệp vụ.

## Phân loại tạm thời

| Nhóm / case trong log | Phân loại hiện tại | Lý do và việc cần xác minh |
|---|---|---|
| `DELETE` nhận `204`, nhưng schema chỉ công bố `200/401/404` | Thiếu/sai schema, chưa phải defect API | `204 No Content` phù hợp ngữ nghĩa delete. Nhân cần đối chiếu response OpenAPI và replay bằng một ID fixture hợp lệ; không sửa raw schema trong pilot. |
| `DELETE` nhận `403` với UUID ngẫu nhiên | Chưa kết luận; tiền điều kiện/ID cần kiểm tra | Schema cho phép integer hoặc string UUID, nhưng fixture dùng ID số và actor editor. Replay với ID map và không có query phụ để tách lỗi quyền khỏi ID không tồn tại. |
| `GET list/detail` nhận `403` khi `version=site-redesign-2027` | Schema/harness thiếu tiền điều kiện | Schema chỉ khai báo `version` là string, nhưng request đòi Content Version chưa có trong fixture hoặc không được actor xem. Không coi đây là lỗi sản phẩm. |
| `GET list` nhận `400` vì `meta[0]` không hợp lệ | Schema thiếu ràng buộc ngữ nghĩa | Nhánh `Meta` dạng string trong raw schema không giới hạn giá trị, trong khi API chỉ nhận `total_count`, `filter_count` hoặc `*`. Cần ghi schema gap và tạo guided strategy có giá trị hợp lệ. |
| `GET detail` nhận `400` vì phần tử `fields` rỗng | Schema thiếu validation | `Fields.items` chỉ là `string`, không có `minLength`; runtime từ chối chuỗi rỗng. Đây là schema gap cần overlay có lý do nếu guided dùng. |
| `PATCH` nhận `403` với `fields=year(date_published)` và body cập nhật `title/score` | Chưa kết luận; request có query/field không phù hợp | Cần replay một PATCH tối thiểu với ID fixture, body hợp lệ và bỏ `fields`/dùng field hợp lệ; sau đó đối chiếu permission editor. Không đổi expected status để làm pass. |
| `PATCH` và `POST` nhận `400` với body byte `NUL` | Chưa kết luận; nghi vấn generator/request serialization | Log cho thấy body không phải JSON hợp lệ dù operation yêu cầu object/array. Cần kiểm tra case raw của Schemathesis và xác định có thật sự thỏa request schema trước khi phân loại. |

## Việc replay/triage tiếp theo

1. Lành tiếp tục xác nhận bảy nhóm trên bằng report raw, schema hash và replay
   có URL/actor đúng; ghi `expected/actual`, precondition và một phân loại duy
   nhất cho mỗi nguyên nhân.
2. Đối chiếu ID map, policy và invariant trước/sau các replay có ghi hoặc xóa;
   không dùng dữ liệu phát sinh ngẫu nhiên làm fixture chuẩn.
3. Chỉ các failure còn tái hiện với precondition hợp lệ mới được chuyển sang
   điều tra defect sản phẩm; nhóm chưa đủ bằng chứng giữ trạng thái `unresolved`.

## Giới hạn

Không thể chạy replay trong phiên này vì Docker daemon chưa khả dụng trong WSL.
Không có thay đổi assertion, blanket skip/xfail hoặc sửa schema raw để che các
failure. S4–S6 quyền Reader trong run lịch sử vẫn `blocked` do
`custom_permission_rules_enabled=false`, độc lập với triage pilot này. Checkpoint
v2 sau đó đã kiểm tra Reader qua API thật; xem runtime evidence và
[`docs/g1-acceptance.md`](../docs/g1-acceptance.md) để biết trạng thái hiện hành.

## Ghi chú G1 hiện hành

Không yêu cầu máy thứ hai hoặc review chéo để đóng G1. Raw/guided v2, invariant
aggregate và replay phải tiếp tục giữ đúng exit code, report và phân loại; không
đổi failure thành PASS chỉ vì tiêu chí G1 đã được điều chỉnh.
