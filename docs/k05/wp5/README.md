# WP5 — chiến dịch Schemathesis đầy đủ: 18 run

Ngày 23–24/11/2026, lab local `r06-k05` (Directus 12.5.0, Schemathesis 4.30.0, PostgreSQL 16). Số liệu trong file này lấy từ `campaign-summary.json` của từng seed ([campaign-summaries.json](campaign-summaries.json)) và từ NDJSON của Schemathesis; thư mục `artifacts/runs/` bị Git bỏ qua nên file tóm tắt này là bản lưu gọn.

## 1. Kết quả chính

- **18/18 seed hoàn tất thật** (`termination: completed`, `run_complete: true`): có đủ report và coverage, restore `qa_*` PASS, kiểm tra tác dụng phụ ngoài `qa_*` báo **sạch** (mỗi seed của Editor và Reader còn tự xóa 1 thông báo do `utils/export` tạo, xem WP4).
- **62/62 cặp (actor, operation)** có request và phản hồi ghi lại. **10/10 operation CRUD của Editor có ít nhất một phản hồi 2xx.** Bảng theo từng cặp: [bang-phan-hoi-theo-cap.csv](bang-phan-hoi-theo-cap.csv) (30.589 request ghi nhận, chỉ đếm request cùng phương thức với operation).
- `status: failed` trong `campaign-summary.json` nghĩa là Schemathesis **tìm thấy lỗi** (mã thoát 1), không phải chạy dở. Số "failure duy nhất" là số nhóm Schemathesis gom lại, **không phải số defect**.

## 2. Ngân sách và cách chạy

| Tham số | Giá trị |
|---|---|
| Ma trận | 3 actor (Editor, Reader, Anonymous) × {raw, guided} × seed 101, 202, 303 |
| Phạm vi | `full`: 30 / 22 / 10 operation |
| Worker, tốc độ, timeout request | 1, 5 request/giây, 10 giây (mặc định `AGENTS.md`) |
| Ví dụ mỗi operation | 100 |
| Pha | raw: `examples,coverage,fuzzing`; guided thêm `stateful` |
| `--max-time` | **Không đặt** (`LAB_MAX_TIME=0`); trần cứng 5.400 giây mỗi seed bằng `timeout` trong container |
| Thứ tự | Tuần tự từng cặp (actor, profile), không chạy song song trên cùng DB |
| Harness | commit `c7b559f` kèm thay đổi chưa commit lúc chạy (metadata ghi `dirty`); các thay đổi đó là commit `9def78a` (`LAB_MAX_TIME=0`, `LAB_CAMPAIGN_PHASES`, `LAB_HARD_TIMEOUT`, `run_complete`) |

| Nhóm | Run | Operation | Thời gian mỗi seed | Case sinh ra | Failure duy nhất | Case lỗi chạy |
|---|---|---:|---|---:|---:|---:|
| Editor raw | `20261123T174529Z-808` | 30 | 26–27 giây | 114–117 | 64–66 | 0 |
| Reader raw | `20261123T174820Z-1596` | 22 | 22–23 giây | 95–98 | 45–48 | 0 |
| Anonymous raw | `20261123T175055Z-893` | 10 | 9 giây | 32 | 21 | 0 |
| Anonymous guided | `20261123T175314Z-1627` | 10 | 9 giây | 33 | 22 | 0 |
| Reader guided | `20261123T175522Z-1525` | 22 | 221–778 giây | 1.056–3.722 | 65–72 | 12–31 |
| Editor guided | `20261123T182014Z-67` | 30 | 1.594–1.734 giây | 7.831–8.639 | 111–114 | 257–404 |

Tổng thời gian campaign khoảng 1,8 giờ (6.588 giây), chưa kể restore và kiểm tra giữa các seed.

## 3. Đính chính về `--max-time` (quan trọng cho báo cáo)

Các campaign trước đây và các tài liệu cũ ghi `termination=max_time` và coi đó là "chưa hoàn tất / `INCOMPLETE_BUDGET`". **Cách hiểu đó không chính xác.**

- Trợ giúp CLI của Schemathesis 4.30 (`schemathesis run --help`) ghi ở `--max-time`: *"Time budget for the whole run; fuzzing and stateful testing repeat until it is spent"*. Hễ đặt `--max-time`, run luôn kéo dài đúng tới trần.
- Pilot ngày 24/11 (run `20261123T164241Z-937`, Editor raw, `--max-time 1800`): 28 giây đầu chạy đủ ba pha, sau đó engine lặp **2.254 vòng `fuzzing` mỗi vòng khoảng 0,8 giây** cho tới hết giờ, tổng chỉ 140 case. Chạy lại không có `--max-time` (run `20261123T171449Z-2031`): **27 giây**, `termination: completed`, cùng 30/30 operation và cùng 66 failure duy nhất.
- Vì thế các campaign cũ đã chạy đủ một lượt rồi chạy lặp thêm; chúng không bị cắt giữa chừng. Kết quả "đạt `max_time`" không phải bằng chứng thiếu coverage.

## 4. Tiêu chí C1–C6 (xem [kế hoạch](../KE_HOACH_THU_NHO_VA_BO_SUNG_K05.md), mục 3.2)

| Tiêu chí | Trạng thái |
|---|---|
| C1: 62/62 cặp có request và phản hồi | **Đạt** (62/62) |
| C2: 10 operation CRUD của Editor có 2xx; operation khác có request hợp lệ tới được handler | **Đạt phần CRUD (10/10)**; các cặp còn lại ở mục 5 |
| C3: cả 18 run kết thúc hoàn tất | **Đạt** (18/18, theo định nghĩa `run_complete`) |
| C4: restore sau mỗi run PASS | **Đạt** (`restore_exit_code: 0` ở cả 18 seed) |
| C5: mọi failure được gom nhóm, phân loại, có reproducer | **Chưa** (WP7) |
| C6: coverage tracecov (tham số, từ khóa, phản hồi, example) | **Chưa** (WP6); ở cả 18 seed số operation được thử bằng tổng số operation (30/30, 22/22, 10/10) |

## 5. Bảng 62 cặp (actor, operation)

Nhãn là mô tả phản hồi quan sát được, **không phải kết luận đúng/sai của Directus**.

| Nhãn | Tổng | Editor | Reader | Anonymous |
|---|---:|---:|---:|---:|
| Có phản hồi 2xx | 34 | 18 | 12 | 4 |
| Chỉ 401/403 (tới tầng xác thực/phân quyền) | 18 | 7 | 7 | 4 |
| Chỉ 4xx khác | 10 | 5 | 3 | 2 |

Các cặp không có 2xx tập trung ở `assets/{id}`, `auth/login|refresh|password/reset`, `auth/oauth*`, `DELETE` hàng loạt trên hai collection, `utils/cache/clear|import|sort`, đúng với các lý do đã ghi ở WP3 (fixture không cấp quyền đọc file, không có provider OAuth, cần token qua email, schema không mô tả body DELETE hàng loạt, `cache/clear` chỉ admin, import cần file multipart). Với `utils/sort` phản hồi 400 vẫn chưa được lý giải.

**Hai điều cần ghi nhận khi diễn giải**

1. **Reader nhận 200/204 trên `PATCH /items/qa_articles/{id}`** (19 lần, request không có body). Đã tra quyền trong lab: policy Reader có một quyền `update` cho `qa_articles` với `fields=[]` (không trường nào), nên mọi request mang dữ liệu bị 403 nhưng request rỗng không có trường nào để kiểm và được chấp nhận như thao tác không đổi gì. Điều này khớp với việc fixture cố ý cấp quyền rỗng để operation PATCH xuất hiện trong schema của Reader (cho scenario S6). Tôi chưa kết luận hành vi "update rỗng trả 2xx" của Directus là lỗi hay đúng thiết kế; để lại ở WP7.
2. **13 cặp có ít nhất một phản hồi 5xx**. Đây là số cặp, không phải số defect; cần gom theo nguyên nhân ở WP7 (trong đó có `GET /items/qa_categories` và `GET /items/qa_articles`).

## 6. Giới hạn

- Ba seed của raw gần như giống nhau (116±2 case mỗi seed cho Editor) vì chế độ chạy một lượt và `--generation-unique-inputs`; chỉ guided (có stateful) cho kết quả khác nhau rõ giữa các seed (Reader 1.056 đến 3.722 case).
- Guided của Anonymous gần như không khác raw (33 so với 32 case) vì schema Anonymous không có liên kết để stateful khai thác.
- "Case lỗi chạy" của guided Editor (257–404) và Reader (12–31) chưa được xem xét; cần kiểm trước khi kết luận.
- Đây là coverage theo schema và theo operation, **không phải** coverage mã nguồn Directus và không chứng minh Directus không có lỗi.
- Các pilot trước đó (có `--max-time`, 20 hoặc 100 ví dụ) không nằm trong số liệu trên.
