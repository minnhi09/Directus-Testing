# Dựng lại và kiểm thử trên Windows — 13/10/2026

## Kết luận

Directus, PostgreSQL và runner chạy được trên máy này. License người dùng
cấu hình đã active, `source=env`, `custom_permission_rules_enabled=true`.
Seed lặp lại được; smoke và sáu scenario đều PASS. Invariant có 9 PASS,
2 FAIL, 0 BLOCKED. Raw/guided đã chạy pilot trên ba seed, mỗi seed thực thi
10/10 operation và restore PASS; vẫn giữ failure/exit 1 và giới hạn thời gian.
Đây là xác minh pipeline, không phải tuyên bố toàn bộ test PASS hoặc chạy hết
ngân sách campaign chính.

Harness HEAD: `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`; working tree dirty,
chưa commit/push. Run ID dùng UTC, ngày báo cáo theo Asia/Bangkok.
Baseline giữ nguyên Directus 12.5.0, PostgreSQL 16 Alpine, Schemathesis 4.30.0
và digest trong `config/lab.env.example`/metadata. Actor fuzz là Editor,
fixture `r06-k05-v2`, một worker, rate `5/s`, request timeout 10 giây.

## Run chức năng và schema

| Lệnh | Run ID | Kết quả |
|---|---|---|
| `up` sau khi người dùng điền key | `20261012T185517Z-1801` | PASS, exit 0 |
| `seed` | `20261012T185624Z-1157` | PASS; schema/fixture/actor/policy đầy đủ |
| `seed` lặp lại | `20261012T185707Z-470` | PASS, giữ category ID 1–3 và article ID 1–12 |
| `smoke` | `20261012T185726Z-446` | PASS, validation/SET NULL/Reader published |
| `export-schema` | `20261012T185734Z-1667` | PASS, actor inventory 14/14/6/0 |
| `test scenarios` sau sửa jq wrapper | `20261012T185849Z-1525` | 6 PASS, 0 FAIL, 0 BLOCKED |
| `test invariants` | `20261012T185934Z-1453` | 9 PASS, 2 FAIL, 0 BLOCKED, exit 1 |
| `replay aggregate-query-robustness` | `20261012T185942Z-1219` | Tái hiện unknown 500, hai control 200; exit 1 |
| `replay contract-schema-candidates` | `20261012T185950Z-1994` | Bốn schema candidate, cleanup đạt; exit 1 |
| `replay j0ZjQ0` | `20261012T191034Z-777` | DELETE article 1: reproduced, restore 0, exit 0 |
| `seed` sau campaign/replay | `20261012T191100Z-757` | PASS, fixture vẫn 3 category/12 article và ID giữ nguyên |
| `doctor` cuối | `20261012T191121Z-1148` | PASS; health, digest, ACL, license active |

Schema snapshot mới nằm tại `runtime/profiles/windows-20261013-oig/schemas/r06-k05-v2/`.
Các snapshot cũ và profile trước khi license active được giữ riêng.

| Actor | Operation trong schema | SHA-256 |
|---|---:|---|
| Admin | 14 | `993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e` |
| Editor | 14 | `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26` |
| Reader | 6 | `d7dc1393eb7e01514f0f8a4d3796ab71cf1f0fe70f5c8a3da5c0ae20259b47b8` |
| Anonymous | 0 | `2070c25c68193a4a42501935974bb3045697aceb1fe072bb3461f43c0a0342b3` |

## Pilot K05 đã chạy

Ngân sách pilot: tối đa 10 examples/operation và 60 giây/seed. `max-examples`
không phải tổng số case. Raw run `20261012T185958Z-355`, guided run
`20261012T190350Z-1047`; report/NDJSON/coverage nằm trong thư mục từng seed.
Guided thực sự chạy stateful phase trên cả ba seed.

| Profile | Seed | Operation tested/covered | Case generated | Unique check failure | Restore | Kết thúc |
|---|---:|---|---:|---:|---|---|
| raw | 101 | 10/10 | 270 | 36 | PASS | max_time, exit 1 |
| raw | 202 | 10/10 | 266 | 35 | PASS | max_time, exit 1 |
| raw | 303 | 10/10 | 270 | 40 | PASS | max_time, exit 1 |
| guided | 101 | 10/10 | 276 | 32 | PASS | max_time, exit 1 |
| guided | 202 | 10/10 | 279 | 36 | PASS | max_time, exit 1 |
| guided | 303 | 10/10 | 278 | 36 | PASS | max_time, exit 1 |

Lượt bổ sung sau sửa Windows dùng seed 101, 10 examples/operation, 30 giây:

| Profile | Run | Case | Unique check failure | Operation | Restore |
|---|---|---:|---:|---|---|
| raw | `20261012T190820Z-1761` | 61 | 22 | 10/10 | PASS |
| guided | `20261012T190912Z-1225` | 134 | 26 | 10/10 | PASS |

Cả hai lượt bổ sung giữ exit 1 do failure/max_time; inventory/metrics JSON hợp
lệ, không còn lỗi `Argument list too long` và cảnh báo Hypothesis fallback.
Không cộng check failure thành số defect. Không suy schema coverage thành
line/branch coverage Directus. Ngân sách chính 100 examples và 1.200 giây mỗi
profile/seed chưa được chạy lại trong phiên Windows này.

## Sửa lỗi tương thích và dữ liệu

- `lab.sh`: kiểm tra ACL Windows, dùng `NUL` cho curl health, redact license,
  thêm runtime profile có tên được kiểm tra và ghi vào metadata.
- `scripts/lab-components.sh`: gửi JSON qua stdin để giữ UTF-8; chuyển riêng
  host bind mount khi gọi Docker trên Git Bash; đặt thư mục Hypothesis trong
  `/work/run/hypothesis`; đọc coverage lớn bằng `--slurpfile`.
- jq portable wrapper trong `../tmp/lab-tools/` dùng `-b` và ngăn MSYS tự
  chuyển `/items/...` từ JSON thành đường dẫn Windows. Lỗi này từng làm S4–S6
  bị ghi blocked dù schema mới có operation; run đó được giữ làm lịch sử,
  không dùng làm kết quả cuối.
- Seed trước sửa UTF-8 đã tạo các bản ghi mẫu bị hỏng/trùng. Chỉ dữ liệu mẫu
  do agent tạo được sửa/dọn, không reset volume. Backup trước sửa và report
  nằm tại `artifacts/runs/20261012T185232Z-fixture-encoding-repair/`; ID gốc
  được giữ và seed lặp lại/post-campaign đều xác minh dữ liệu đúng.
- Raw seed 303 và guided ba seed gặp giới hạn argv khi tạo inventory.
  Inventory/metrics được dựng lại bằng hàm đã sửa từ report/coverage gốc;
  report runner, mã thoát, schema và snapshot không bị thay đổi. Các log lỗi
  ban đầu vẫn được giữ để audit.
- Các thay đổi có sẵn của người dùng trong `scripts/invariants.py` và phần
  guard campaign trong `scripts/lab-components.sh` được bảo toàn.

## Finding còn mở

1. Aggregate `foo` trả 500 trong khi `{}` và count trả 200; giữ nhãn robustness
   candidate, chưa kết luận defect upstream.
2. Contract probe ghi POST data object trong khi schema mô tả array cho hai
   collection, CSV ngoài content type JSON và DELETE 204 ngoài response map.
   Đây là các schema/contract candidate, không tự tính thành bốn defect.
3. Failure generated/stateful khác còn cần triage theo request, precondition,
   source/version và log. Không nới assertion hoặc sửa raw schema để PASS.

## Cách chạy lại trên máy này

Mở <http://127.0.0.1:8055/admin>. Email Admin là `admin@example.com`; mật khẩu
lấy từ `ADMIN_PASSWORD` trong `config/lab.env`, giữ riêng trên máy.

Từ PowerShell tại `D:\DAMH-full-recovery-2026-10-12`:

```powershell
& .\tmp\lab-tools\run-lab.ps1 doctor
& .\tmp\lab-tools\run-lab.ps1 up
& .\tmp\lab-tools\run-lab.ps1 seed
& .\tmp\lab-tools\run-lab.ps1 smoke
& .\tmp\lab-tools\run-lab.ps1 export-schema
& .\tmp\lab-tools\run-lab.ps1 test scenarios
& .\tmp\lab-tools\run-lab.ps1 test invariants
& .\tmp\lab-tools\verify-k05.ps1
```

`verify-k05.ps1` chạy pilot 60 giây/seed; exit 1 vẫn là kết quả thật khi có
failure. `run-lab.ps1 test raw` hoặc `test guided` dùng ngân sách mặc định
trong cấu hình nếu không có override, có thể mất khoảng 20 phút mỗi seed.
Các suite ghi dữ liệu chạy tuần tự. `down` giữ volume; không chạy reset để
xử lý finding. License, password và token không đưa vào báo cáo/Git.

Người dùng đã hỗ trợ bằng việc đăng ký [Open Innovation Grant](https://directus.com/oig)
và tự copy key vào cấu hình; không còn blocker cần người dùng cung cấp thêm
để chạy lab và pipeline hiện tại.
