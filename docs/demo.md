# Kịch bản demo và bàn giao 10–15 phút

Demo chỉ chạy trên lab local đã cô lập của repository R06 + K05. Không dùng
server public, database, volume hoặc project Docker khác.

## Mục tiêu và nguyên tắc trình bày

Demo cần chứng minh được đường đi từ Directus baseline → fixture/policy →
schema theo actor → scenario/invariant → replay K05. G1 kỹ thuật hiện tại là
baseline chạy được **có finding chưa đóng**; không trình bày là toàn bộ test đã
PASS và không đếm mỗi check failure thành một defect.

Review bởi thành viên khác và dựng lại trên máy thứ hai đã được loại khỏi cổng
G1 nội bộ theo quyết định đã cập nhật. Đây vẫn là phần đánh giá/bàn giao riêng
nếu giảng viên yêu cầu; không được nói rằng chúng đã được thực hiện khi chưa có
bằng chứng.

## Precondition

Trên máy sạch hoặc sau khi kiểm tra lab hiện tại, chạy theo thứ tự:

```bash
./lab.sh doctor
./lab.sh up
./lab.sh seed
./lab.sh smoke
./lab.sh export-schema
./lab.sh test scenarios
```

Nếu `seed` dừng ở license Reader, trình bày đó là blocker đã xác minh và tiếp
tục các demo Editor/anonymous đã có bằng chứng; không giả lập quyền Reader bằng
Admin. Checkpoint local hiện tại có license active nên có thể demo Reader
published/private projection/write rejection.

Không chạy `reset` giữa các bước của một chuỗi stateful. Nếu cần làm sạch,
lưu artifact trước, xác minh đúng Compose project/volume `r06-k05`, rồi mới
dùng `./lab.sh reset`.

## Bằng chứng runtime cuối cùng

| Hạng mục | Run gần nhất | Kết quả thực tế |
|---|---|---|
| Doctor | `20261011T165804Z-221010` | PASS, health/digest/fixture map/license active; exit `0` |
| Smoke | `20261011T165604Z-220107` | PASS, validation/SET NULL/login/Reader filter; exit `0` |
| OpenAPI actor | `20261011T171009Z-223973` | admin/editor/reader/anonymous `14/14/6/0`, hash giữ nguyên; exit `0` |
| Sáu scenario | `20261011T171054Z-225602` | S1–S6 PASS, `0 failed`, `0 blocked`; S6 PATCH `403`, read-back `200`; exit `0` |
| Demo replay preflight | `20261011T161636Z-204795` … `20261011T161658Z-207292` | 7/7 replay PASS dưới harness `3a3dff5`, fixture `r06-k05-v2` |
| Invariant | `20261011T171247Z-226528` | `9 passed`, `2 failed`, `0 blocked`; exit `1` đúng finding đã biết |

Các run trên được thực hiện dưới các harness SHA tương ứng trong metadata và được ghi tại
[`evidence/runtime-verification-2026-10-11.md`](../evidence/runtime-verification-2026-10-11.md)
và [`evidence/final-handoff-2026-10-11.md`](../evidence/final-handoff-2026-10-11.md).

## Năm luồng demo ổn định

Mỗi luồng có thể chạy độc lập sau precondition. Khi trình bày, mở report trong
thư mục run mà lệnh in ra và chỉ rõ actor, fixture, expected/actual.

| Luồng | Lệnh | Expected result cần nói rõ |
|---|---|---|
| 1. Đăng nhập và token | `./lab.sh replay auth-invalid-token` và `./lab.sh replay anonymous-denied` | Token giả bị từ chối; anonymous không truy cập hai collection. Giữ status thực tế theo baseline, không tự gán cứng `401/403`. |
| 2. Editor CRUD | `./lab.sh replay editor-crud` | Create → read → PATCH → read → DELETE → read; ID lấy từ response, field không PATCH vẫn giữ nguyên, sau delete không còn tài nguyên. |
| 3. Query fixture | `./lab.sh replay query-fixture` | Filter published, sort `title,id`, projection và hai page khớp oracle tính từ `fixture-ids.json`. |
| 4. Quan hệ category | `./lab.sh replay relation-nullification` | Article liên kết category; xóa category làm foreign key thành `null` theo policy/DB baseline; cleanup và restore PASS. |
| 5. Reader policy | `./lab.sh replay reader-visibility` và `./lab.sh replay reader-write` | Reader đọc được published, không đọc `internal_notes`, không đọc draft và PATCH bị từ chối; Editor read-back chứng minh dữ liệu không đổi. |

Ba luồng tối thiểu để demo nhanh là Editor CRUD, Query fixture và Reader
policy. Luồng 1 và 4 bổ sung xác thực và quan hệ để phủ đủ năm mục tiêu nghiệp
vụ của R06/K05.

## Schemathesis và finding có thể tái hiện

Pilot ngắn, có ngân sách rõ ràng:

```bash
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test raw
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test guided
```

Pilot có thể kết thúc với exit khác `0` do check failure; phải giữ run/log,
không dùng `|| true` và không gọi pilot là campaign đạt. Mở
`campaign-index.json`, `operation-inventory.json`, `metrics.json` và report;
đối chiếu dòng `Campaign restore: PASS` trước khi kết luận dữ liệu đã được
khôi phục.

Pilot gần nhất dưới HEAD `39093de`: raw run `20261011T164716Z-216864` có
10/10 operation, 47 case và 14 unique failure; guided run
`20261011T164757Z-217585` có 10/10 operation, 125 case và 26 unique failure.
Cả hai restore PASS nhưng exit `1` do `max_time`/check failure; chỉ dùng để
chứng minh hai profile chạy độc lập và lưu artifact.

Để trình bày một finding K05 có chủ đích:

```bash
./lab.sh replay aggregate-query-robustness
./lab.sh replay contract-schema-candidates
```

Trên baseline cuối cùng, aggregate ghi `unknown shape=500`, hai control ghi
`200`; contract probe ghi bốn schema candidate và cleanup PASS. Hai replay
được giữ exit `1`. Phân loại hiện tại là schema omission/contract candidate và
product robustness candidate cần triage, chưa phải bốn product defect đã xác
nhận.

Campaign đầy đủ local:

- raw `20261011T085034Z-76481`: 10/10 operation ở cả ba seed, restore PASS,
  runner exit `1` do check failure/max-time;
- guided `20261011T095117Z-89079`: 10/10 operation ở cả ba seed, restore PASS,
  runner exit `1` do check failure/max-time.

Đây là bằng chứng pipeline và giới hạn thực tế, không phải tuyên bố campaign
đã PASS.

## Đọc artifact và báo cáo

Sau mỗi lệnh, dùng `run_id` mà harness in ra:

```bash
RUN_ID="<run_id>"
jq . "artifacts/runs/${RUN_ID}/metadata.json"
[ ! -f "artifacts/runs/${RUN_ID}/scenario-report.json" ] || \
  jq . "artifacts/runs/${RUN_ID}/scenario-report.json"
[ ! -f "artifacts/runs/${RUN_ID}/invariant-report.json" ] || \
  jq . "artifacts/runs/${RUN_ID}/invariant-report.json"
```

Các file cần chỉ cho người xem:

- `manifest/baseline.yaml`: version, digest, fixture/schema hash và validation
  keys;
- `runtime/schemas/*.json`: schema gốc theo actor, không sửa trực tiếp;
- `runtime/fixture-ids.json`: ánh xạ tên fixture → ID tự sinh;
- `artifacts/runs/<run_id>/metadata.json`, `run.log`, report và reproducer;
- [`docs/g1-acceptance.md`](g1-acceptance.md): cổng G1 và blocker;
- [`docs/replay-cases.md`](replay-cases.md): precondition, expected/actual và
  phạm vi replay;
- [`evidence/final-handoff-2026-10-11.md`](../evidence/final-handoff-2026-10-11.md):
  bảng bàn giao cuối cùng.

Khi báo cáo finding, phân biệt `product`, `schema`, `harness/fixture`,
`environment` và `unconfirmed`; nếu một nguyên nhân sinh nhiều check failure
thì gom về một finding có căn cứ.

## Kết thúc demo

```bash
./lab.sh down
```

`down` mặc định giữ volume. Chỉ dùng `./lab.sh reset` sau khi đã lưu artifact
cần thiết và xác nhận đúng volume của project `r06-k05`; reset là thao tác xóa
dữ liệu lab. Không truyền credential/token vào command và không chia sẻ
`config/lab.env`.
