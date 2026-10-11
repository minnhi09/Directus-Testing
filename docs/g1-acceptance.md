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
| Stack healthy, version/digest đúng manifest | Doctor `20261011T105225Z-104013`; recheck `20261011T130338Z-139934`, latest `20261011T131803Z-147694` | Đạt |
| Seed schema/fixture/actor/policy đúng và lặp lại không nhân bản | Seed `20261011T084845Z-72361`, smoke `20261011T085023Z-75556` | Đạt |
| CRUD, query, quan hệ và phân quyền đạt oracle | Scenario `20261011T105231Z-104612`, S1–S6 | Đạt |
| Schema theo actor và inventory 10 operation | Export `20261011T085027Z-75998`, admin/editor/reader/anonymous `14/14/6/0` | Đạt |
| Raw/guided chạy độc lập, có report/coverage/restore | Raw `20261011T085034Z-76481`, guided `20261011T095117Z-89079` | Có bằng chứng; runner giữ `failed_or_incomplete` |
| Invariant và replay có precondition, expected/actual, phân loại | Invariant `20261011T105236Z-105096`; recheck `20261011T130457Z-141013`; replay `20261011T105242Z-105524`; contract probe `20261011T130227Z-139257` | Đạt có finding |
| Stateful replay ghi đúng phạm vi tái lập | Hardening `64e88f9`, chain replay `baaee4b`, run `20261011T131321Z-144935` và final-only `20261011T131350Z-145631` | Chain có parent được replay đầy đủ và ghi mismatch; case không có parent vẫn `reproduced_request_only` |
| README, metadata và artifact không chứa secret | README, manifest, run metadata, static/secret scan | Đạt |
| Review chéo thành viên | Không còn là gate G1 | Không áp dụng |
| Dựng và xác minh trên máy thứ hai | Không còn là gate G1 | Không áp dụng |

## 3. Trạng thái thực tế

G1 hiện được ghi nhận là **đạt baseline kỹ thuật, có phát hiện chưa đóng**.
Trạng thái này không có nghĩa mọi campaign đều xanh:

- Invariant baseline có `9 passed`, `1 failed`; recheck mới nhất có `9 passed`,
  `2 failed`, `0 blocked`. `aggregate-query-robustness` tiếp tục tái hiện HTTP
  500 với `fields=&aggregate={"foo":1}`; case contract probe ghi bốn schema
  candidate trong một failure có chủ đích.
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
