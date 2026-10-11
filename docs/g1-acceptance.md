# Tiêu chí nghiệm thu G1 — R06/K05

Ngày cập nhật: 2026-10-11
Baseline: Directus `12.5.0`, PostgreSQL `16`, Schemathesis `4.30.0`, fixture
`r06-k05-v2`.

## 1. Phạm vi và nguồn yêu cầu

G1 là mốc nghiệm thu kỹ thuật nội bộ của đồ án, không phải thuật ngữ được định
nghĩa trong [`yeu_cau.pdf`](../yeu_cau.pdf). Đề bài yêu cầu nhóm:

- cung cấp README để giảng viên hoặc người khác có thể dựng và chạy lại hệ
  thống/test trên máy mới;
- có automation, log/report/metrics, phân tích failure và root cause;
- thực hiện peer-review/peer-evaluation ở giai đoạn bảo vệ cuối kỳ.

Đề bài không yêu cầu phải có một lần chạy xác minh trên máy thứ hai hoặc review
chéo giữa thành viên như điều kiện kỹ thuật của mốc G1. Hai nội dung đó được bỏ
khỏi gate G1 theo quyết định điều hành ngày 2026-10-11. Khả năng tái lập vẫn
được giữ bằng cấu hình pin, README, fixture, schema hash, metadata, artifact và
replay.

## 2. Checklist G1 hiện hành

| Tiêu chí | Bằng chứng | Trạng thái |
|---|---|---|
| Stack healthy, version/digest đúng manifest | Doctor `20261011T105225Z-104013`; latest recheck `20261011T134705Z-161373` dưới `a153e99` | Đạt |
| Seed schema/fixture/actor/policy đúng và lặp lại không nhân bản | Seed `20261011T084845Z-72361`, smoke `20261011T085023Z-75556` | Đạt |
| CRUD, query, quan hệ và phân quyền đạt oracle | Scenario `20261011T105231Z-104612`, S1–S6 | Đạt |
| Schema theo actor và inventory 10 operation | Export `20261011T085027Z-75998`, admin/editor/reader/anonymous `14/14/6/0` | Đạt |
| Raw/guided chạy độc lập, có report/coverage/restore | Raw `20261011T085034Z-76481`, guided `20261011T095117Z-89079` | Có bằng chứng; runner giữ `failed_or_incomplete` |
| Invariant và replay có precondition, expected/actual, phân loại | Invariant `20261011T105236Z-105096`; full recheck `20261011T134626Z-160826`; aggregate replay `20261011T134519Z-160153` dưới `bcbf219`; contract probe `20261011T130227Z-139257` | Đạt có finding |
| Stateful replay ghi đúng phạm vi tái lập | Hardening `64e88f9`, chain replay `baaee4b`, oracle fix `a713481`; recheck `20261011T132550Z-151921`, `20261011T133817Z-157078`, `20261011T133626Z-155874` | Có bằng chứng full-chain reproduced (`aZmz3k`), mismatch không bị đổi thành PASS (`tFjhQT`), và precondition không đủ bị dừng đúng (`Ag8Csb`); status source/expected/actual được ghi rõ |
| README, metadata và artifact không chứa secret | README, manifest, run metadata, static/secret scan | Đạt |
| Review chéo thành viên | Không còn là gate G1 | Không áp dụng |
| Dựng và xác minh trên máy thứ hai | Không còn là gate G1 | Không áp dụng |

## 3. Trạng thái thực tế

G1 hiện được ghi nhận là **đạt baseline kỹ thuật, có phát hiện chưa đóng**.
Trạng thái này không có nghĩa mọi campaign đều xanh:

- Invariant baseline có `9 passed`, `1 failed`; full recheck mới nhất
  `20261011T134626Z-160826` dưới `bcbf219` có `9 passed`, `2 failed`, `0
  blocked`. `aggregate-query-robustness` tiếp tục tái hiện HTTP
  500 với `fields=&aggregate={"foo":1}`; replay mở rộng
  `20261011T134519Z-160153` ghi hai control aggregate trả 200. Case contract
  probe ghi bốn schema candidate trong một failure có chủ đích.
- Replay bổ sung `kb5gjq` ở `20261011T135006Z-162769` tái hiện request-only
  `POST /items/qa_articles` với `published_at=""` trả HTTP `500`; log ghi
  PostgreSQL SQLSTATE `22007`. Đây là candidate schema-semantic/product
  robustness, chưa đủ căn cứ gọi là product defect và không được đổi thành
  PASS để làm đẹp kết quả.
- Replay `F8j8Gl` ở `20261011T135713Z-165099` tái hiện request-only
  `GET ...?backlink=true&export=json` với HTTP `200` và raw array 12 item
  ngoài response schema object. Đây là schema/contract candidate về alternate
  export shape, không phải product defect đã xác nhận.
- Replay `UNKW3j` ở `20261011T135951Z-166351` tái hiện `export=xml` với
  HTTP `200` và `text/xml` ngoài schema JSON; gộp với `vx21yF` thành export
  media-type candidate, không đếm thành defect độc lập.
- Replay `R0sH5o` ở `20261011T140125Z-167402` tái hiện `export=yaml` với
  HTTP `200` và `text/yaml` ngoài schema JSON; tiếp tục gộp vào export
  media-type candidate, chưa xác nhận product defect.
- Replay `DhqXrn` ở `20261011T140307Z-168360` dựng đủ chain nhưng source
  `204` và actual `403` do field `id` bị từ chối; giữ là negative
  precondition/policy mismatch, không xác nhận defect.
- Replay `UTk4sa` ở `20261011T140452Z-169384` dừng tại parent ID mapping,
  target không gửi, restore PASS; giữ là stateful artifact/precondition
  limitation, không kết luận API accepted/rejected negative data.
- Replay `6IayFG` ở `20261011T140814Z-170794` tái hiện request positive có
  `offset` vượt safe-number và HTTP `400 INVALID_QUERY`; restore PASS, exit `1`.
  Giữ là schema semantic/generator-positive candidate, không xác nhận product
  defect và không đổi expected để làm campaign xanh.
- Replay `6THjzP` ở `20261011T141024Z-171863` gửi `name` integer trong negative
  mutation; Directus trả `200` và ép response thành string, trái expected `400`,
  restore PASS, exit `1`. Giữ là schema-negative/oracle semantic mismatch,
  chưa xác nhận product defect.
- Replay `QPKZ6w` ở `20261011T141213Z-172805` tái hiện projection `title,
  author.name` trả `200` nhưng thiếu `score` theo schema item; restore PASS.
  Trạng thái replay là reproduction thành công, không phải contract PASS; giữ
  là schema/projection gap.
- Raw và guided đã chạy đủ seed `101`, `202`, `303`, đủ 10/10 operation và
  restore PASS, nhưng kết thúc `failed_or_incomplete` do check failure và
  `max_time`. Các exit code và report được giữ nguyên.
- Các failure Schemathesis được phân biệt giữa schema/contract candidate,
  harness/fixture issue, product robustness candidate, environment và
  unresolved; không đếm nhiều check failure từ một nguyên nhân thành nhiều
  defect.
- Contract probe độc lập ghi nhận bốn schema candidate (POST response shape,
  export content type và DELETE `204`) ở run `20261011T130227Z-139257`; exit
  `1` được giữ nguyên và không được diễn giải thành bốn product defect.
- Chưa có product defect Directus nào được xác nhận chính thức. Candidate HTTP
  500 cần tiếp tục đối chiếu contract/upstream nếu muốn đóng ở giai đoạn cuối.

## 4. Điều không được suy diễn

- Không đổi `failed`, `failed_or_incomplete`, `blocked` hoặc exit code của run
  chỉ để checklist G1 xanh.
- Không coi README có khả năng dựng lại là bằng chứng đã chạy trên máy khác.
- Không coi việc không có review chéo là thiếu sót G1; nếu có review hoặc peer
  evaluation thực tế ở giai đoạn cuối thì ghi đúng provenance riêng.
- Không kết luận “Directus không có lỗi” chỉ vì các scenario/invariant còn lại
  đạt.
