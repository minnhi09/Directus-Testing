# R06–K05 — Kiểm thử API Directus

Directus tự sinh API thêm, đọc, sửa, xóa dữ liệu từ cơ sở dữ liệu. Nhóm 11 kiểm thử API này bằng kỹ thuật **K05 – kiểm thử API dựa trên tài liệu OpenAPI và fuzzing**, dùng công cụ **Schemathesis**, kết hợp các ca nghiệp vụ có kết quả mong đợi rõ ràng.

Báo cáo cuối kỳ được nộp riêng dưới dạng tệp Word; README này dùng cùng mã `TC`, `Q` với báo cáo đó.

## Phạm vi và kết quả

Đối tượng chính là hai bộ dữ liệu `qa_categories`, `qa_articles` với ba vai trò Editor, Reader và Anonymous (khách chưa đăng nhập). Phạm vi sinh kiểm thử tự động gồm 30 thao tác API, tương ứng 62 tổ hợp vai trò – thao tác.

| Phần kiểm thử | Nội dung | Kết quả |
|---|---|---|
| `TC01` – `TC13` | 13 ca nghiệp vụ: thêm/đọc/sửa/xóa, lọc, sắp xếp, phân trang, quyền, giá trị biên của `score`, đối chiếu phản hồi với OpenAPI | 12 đạt, 1 không đạt (`TC13`) — chạy lại ngày 26/11/2026 |
| `Q01` – `Q11` | 11 phép kiểm các quy tắc phải luôn đúng | 9 đạt, 2 không đạt (`Q06`, `Q07`) — chạy lại ngày 26/11/2026 |
| Sinh tự động | 3 vai trò × 2 cách chạy × 3 giá trị khởi tạo | Hoàn tất 18/18 lượt, 31.147 yêu cầu — ngày 24/11/2026 |

Nguyên nhân của các ca không đạt được phân tích trong báo cáo. Không đổi kết quả mong đợi hoặc bỏ ca không đạt để có báo cáo toàn đạt.

## Cấu trúc kho mã

```text
Directus-Testing/
├─ compose.yaml            Khai báo các thành phần chạy bằng Docker
├─ lab.sh                  Chương trình điều phối (được gọi qua PowerShell)
├─ config/lab.env.example  Tệp cấu hình mẫu
├─ manifest/baseline.yaml  Phiên bản và thiết lập kiểm thử được cố định
├─ scripts/
│  ├─ run-lab.ps1          Lệnh chính trên Windows
│  ├─ lab-components.sh    Dữ liệu mẫu, 6 kịch bản, chạy Schemathesis
│  ├─ designed_cases.py    Các ca TC07 – TC13
│  ├─ invariants.py        11 phép kiểm quy tắc
│  ├─ replay_cases.py      Chạy lại một số tình huống
│  ├─ contract_checks.py   So phản hồi với tài liệu API
│  ├─ k05_*.py             Tổng hợp độ bao phủ, phân loại sai lệch
│  └─ data/                Dữ liệu mẫu, danh mục ca, 62 tổ hợp vai trò – thao tác
├─ tests/                  Kiểm thử cho chính chương trình kiểm thử
└─ results/                Kết quả đã lưu
```

## Yêu cầu môi trường

| Phần mềm | Phiên bản | Dùng để |
|---|---|---|
| Windows và PowerShell | — | Gõ lệnh điều khiển môi trường và chạy kiểm thử |
| Docker Desktop (kèm Docker Compose) | Đã chạy với Docker Engine 29.7.2 | Chạy Directus, PostgreSQL và Schemathesis |
| Git for Windows (kèm Git Bash) | — | Tải mã và chạy các bước tự động |
| Python 3 | Chỉ dùng thư viện chuẩn | Chỉ cần khi tổng hợp số liệu và chạy kiểm thử đơn vị |

Docker tự tải đúng phiên bản đã cố định: Directus 12.5.0, Schemathesis 4.30.0, PostgreSQL 16 (tag và digest ở [manifest](manifest/baseline.yaml)).

## Cài đặt và khởi động

Gõ các lệnh trong PowerShell. Trên máy mới:

```powershell
git clone https://github.com/minnhi09/Directus-Testing
cd Directus-Testing
Copy-Item config\lab.env.example config\lab.env
```

Mở `config/lab.env` và thay mọi giá trị `REPLACE_*`: mật khẩu cơ sở dữ liệu, hai khóa bảo mật của Directus và mật khẩu của các tài khoản. `LICENSE_KEY` phải là khóa bản quyền Directus hợp lệ, cho phép tạo quy tắc quyền riêng cho Reader. Tệp này chỉ lưu trên máy chạy; không đưa mật khẩu, mã truy cập hay khóa thật lên Git hoặc vào bài nộp. Máy đã cấu hình thì giữ tệp đang dùng, không chép đè.

Nếu Windows không cho chạy tệp `.ps1`, gõ lệnh sau trước; thiết lập chỉ có hiệu lực trong cửa sổ PowerShell đang mở:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Sau đó chạy lần lượt:

```powershell
.\scripts\setup-windows.ps1          # tải công cụ phụ trợ jq
.\scripts\run-lab.ps1 up             # khởi động Directus và cơ sở dữ liệu
.\scripts\run-lab.ps1 doctor         # kiểm tra môi trường, phiên bản, khóa bản quyền
.\scripts\run-lab.ps1 seed           # tạo bảng, dữ liệu mẫu (3 chuyên mục, 12 bài), tài khoản, quyền
.\scripts\run-lab.ps1 export-schema  # xuất tài liệu OpenAPI của từng vai trò
```

API chạy tại `http://127.0.0.1:8055`, Docker project `r06-k05`. Linux hoặc Git Bash dùng `./lab.sh` với cùng tham số. Chạy các bộ kiểm thử lần lượt, không chạy song song trên cùng cơ sở dữ liệu.

## Chạy 13 ca và 11 phép kiểm

```powershell
.\scripts\run-lab.ps1 test scenarios                    # TC01 – TC06
.\scripts\run-lab.ps1 test designed --selection course  # TC07 – TC13
.\scripts\run-lab.ps1 test invariants                   # Q01 – Q11
```

Lệnh trả mã thoát 1 khi có ca không đạt. Một ca có thể gửi nhiều yêu cầu, nên 13 ca không có nghĩa là 13 yêu cầu. `test designed` không kèm tùy chọn cũng chọn `course`; các lựa chọn `short`, `assertable`, `all`, `--case`, `--group` chỉ để tra cứu, không thuộc bộ 13 ca.

Khi chạy, chương trình in tên riêng của từng ca và phép kiểm:

| Mã trong báo cáo | Tên hiển thị khi chạy |
|---|---|
| `TC01` – `TC06` | `Scenario S1` – `Scenario S6` (theo đúng thứ tự) |
| `TC07` | `Designed P3-ST-01` |
| `TC08` | `Designed P3-AUTHZ-DR-047` |
| `TC09` | `Designed P3-SCORE-POST-MINUS1` |
| `TC10` | `Designed P3-SCORE-POST-0` |
| `TC11` | `Designed P3-SCORE-POST-5` |
| `TC12` | `Designed P3-SCORE-POST-6` |
| `TC13` | `Designed P3-CONTRACT-QA_ARTICLES-OBJECT` |
| `Q01` | `Invariant auth-invalid-token` |
| `Q02` | `Invariant anonymous-denied` |
| `Q03` | `Invariant editor-crud` |
| `Q04` | `Invariant positive-operations` |
| `Q05` | `Invariant query-fixture` |
| `Q06` | `Invariant aggregate-query-robustness` |
| `Q07` | `Invariant contract-schema-candidates` |
| `Q08` | `Invariant relation-nullification` |
| `Q09` | `Invariant invalid-field-rejection` |
| `Q10` | `Invariant reader-visibility` |
| `Q11` | `Invariant reader-write` |

Có thể chạy lại riêng một tình huống bằng `.\scripts\run-lab.ps1 replay editor-crud` (còn có `query-fixture`, `reader-visibility`, `reader-write`).

## Chạy sinh kiểm thử tự động (Schemathesis)

Có hai cách chạy: `raw` (cơ bản, dùng tài liệu OpenAPI nguyên bản) và `guided` (có hướng dẫn, bổ sung ví dụ vào tài liệu). Đặt bốn biến dưới đây trong PowerShell (được ưu tiên hơn tệp cấu hình), rồi chạy hai cách. Làm lại tương tự với `reader` và `anonymous`:

```powershell
$env:LAB_ACTOR='editor'
$env:LAB_CAMPAIGN_SCOPE='full'
$env:LAB_MAX_TIME='0'
$env:LAB_HARD_TIMEOUT='5400'
.\scripts\run-lab.ps1 test raw
.\scripts\run-lab.ps1 test guided
```

Mỗi lệnh chạy ba giá trị khởi tạo 101, 202, 303; đủ ba vai trò là 18 lượt, mất khoảng 1 giờ 50 phút trong đợt chạy ngày 24/11/2026. `LAB_MAX_TIME=0` không đặt giới hạn tổng thời gian cho công cụ; `LAB_HARD_TIMEOUT=5400` dừng cứng một lượt sau 5.400 giây để tránh treo. Số yêu cầu của cách có hướng dẫn có thể khác nhiều giữa các lần chạy, nên so sánh theo loại sai lệch và nguyên nhân.

## Xem và tổng hợp kết quả

Mỗi lượt chạy được lưu trong `artifacts/runs/<run_id>/`: đọc `scenario-report.json`, `designed-report.json` hoặc `invariant-report.json`, cùng `metadata.json`, nhật ký và kết quả khôi phục dữ liệu. Một lượt kiểm không đạt chưa phải là một lỗi riêng; nhiều lượt có thể cùng một nguyên nhân.

Tổng hợp số liệu của các lượt sinh tự động (thay `<run_id>` bằng tên thư mục kết quả; chỉ định đầu ra riêng để không ghi đè số liệu đã lưu):

```powershell
python scripts/k05_reach_report.py <run_id> --out <tệp>
python scripts/k05_coverage_report.py --run <run_id> --out <thư mục>
python scripts/k05_failure_triage.py --run <run_id> --out <thư mục>
python scripts/k05_wp7_replay.py   # gửi lại 67 yêu cầu thăm dò lỗi
```

Số liệu và bằng chứng đã lưu nằm trong thư mục [results](results/README.md). Những vấn đề chưa xác minh vẫn giữ trạng thái "chưa kết luận".

## Kiểm thử cho chính chương trình kiểm thử

Gồm 33 kiểm thử đơn vị, không cần khởi động Directus:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

## Xem OpenAPI bằng Swagger UI

Sau `seed` và `export-schema`, chạy `./lab.sh swagger up` rồi mở `http://127.0.0.1:8086`. Chọn Editor hoặc Reader, gọi `/auth/login` bằng tài khoản tương ứng, sau đó nhập `Bearer <access_token>` trong **Authorize**. Dùng `./lab.sh swagger down` để chỉ dừng giao diện. Schema gốc của Schemathesis không bị sửa.
