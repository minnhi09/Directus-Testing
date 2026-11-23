# Oracle v2 cho 66 ca chưa có kết quả mong đợi — 21/11/2026

Bước 2 của [kế hoạch rút gọn](../../../KE_HOACH_RUT_GON_R06_K05.md). Catalog v1 (`scripts/data/test-catalog-v1.json`) **không bị sửa**. 66 ca có `oracle_readiness` OPEN (47) hoặc CONDITIONAL (19) nay có oracle trong [oracle-v2.json](oracle-v2.json) và kết quả trong [results.json](results.json).

**Trạng thái oracle: ĐÃ DUYỆT bởi Nhân (người chịu trách nhiệm dự án) ngày 21/11/2026**, sau khi xem kết quả chạy. Đây là quyết định của Nhân, không phải xác nhận của thầy hay của Lành. Quy tắc và dự đoán không bị đổi sau khi chạy (`generated_at_utc` giữ nguyên). Kể cả quy tắc coi tên rỗng và chỉ có khoảng trắng là hợp lệ.

## Phương pháp

1. Đọc mã Directus 12.5.0 tại commit `4f77933bf9551cac6b289576078783e189b8f4e3` (`git show`, không dùng checkout hiện tại): validate payload (`process-payload.ts`, `generate-joi.ts`), ép kiểu và ngày (`payload.ts`), dịch lỗi DB (`database/errors/*`), xử lý lỗi (`error-handler.ts`), phân trang/tìm kiếm, quyền field.
2. **Ghi oracle và dự đoán trước khi chạy**: `oracle-v2.json` sinh lúc `2026-11-21T05:41:12Z`, trước mọi lượt chạy 66 ca. Mỗi ca có `outcome` (kết quả mong đợi), `predicted` (kết quả dự đoán từ mã), `confidence` và `refs` (tệp@SHA#dòng).
3. Chạy 66 ca bằng `test designed` (`--group` cho `field-*`, `--case` cho quyền và query), rồi `scripts/oracle_v2.py evaluate` chấm từng ca và so với dự đoán.

Oracle không sao chép phản hồi quan sát được. Nó dựa trên (a) bất biến của dự án (đầu vào sai không bao giờ gây 5xx; request bị từ chối không đổi dữ liệu) và (b) mã nguồn tại SHA. Ba kiểu kết quả mong đợi: `ACCEPT` (chấp nhận, đọc lại đúng), `REJECT` (4xx, không đổi dữ liệu), `ACCEPT_OR_REJECT` (cả hai đều hợp lệ nhưng bắt buộc nhất quán: chấp nhận thì đọc lại đúng kiểu, từ chối thì 4xx và không đổi).

## Kết quả

| Chỉ số | Số lượng |
|---|---:|
| Ca được đánh giá | 66 |
| PASS theo oracle v2 | **58** |
| FAIL theo oracle v2 | **8** |
| Dự đoán từ mã khớp trạng thái HTTP thực tế | **66/66** |
| Ca bị từ chối đã kiểm "không đổi dữ liệu" (so ảnh chụp hai bảng) | 26/26 không đổi |

Kết hợp với 118 ca ASSERTABLE chạy lại trước đó: **242 PASS và 15 FAIL trên 257 ca** (không còn NOT_RUN/OPEN). Con số của 66 ca mới dựa trên oracle v2 đã được Nhân duyệt.

### Theo họ ca

| Họ | Ca | Kết quả mong đợi | Thực tế |
|---|---:|---|---|
| name/title rỗng, chỉ khoảng trắng, số 123, Unicode 80/120 ký tự (POST và PATCH) | 16 | chấp nhận, đọc lại đúng (số thành chuỗi `"123"`) | 16 PASS |
| name/title/score thiếu khi POST | 3 | 400 `FAILED_VALIDATION`, không tạo hàng | 3 PASS |
| PATCH name bỏ trống `{}` | 1 | 2xx, hàng không đổi | PASS |
| score chuỗi `"3"` | 2 | chấp nhận (đọc lại số nguyên 3) hoặc 4xx | 2 PASS (chấp nhận) |
| score boolean, status boolean | 4 | 400, không đổi | 4 PASS |
| score thập phân 2.5 | 2 | 4xx, không bao giờ 5xx | **2 FAIL (500)** |
| status mặc định khi bỏ qua | 1 | 2xx, `draft` | PASS |
| published_at UTC, offset +07:00, không offset (container UTC) | 4 | chấp nhận, cùng thời điểm 08:00Z | 4 PASS |
| published_at rỗng `""` hoặc `not-a-date` | 4 | 4xx, không bao giờ 5xx | **4 FAIL (500)** |
| metadata mảng, số, boolean | 6 | chấp nhận, đọc lại đúng | 6 PASS |
| metadata chuỗi trần `"JSON text"` | 2 | chấp nhận hoặc 4xx | **2 FAIL (500)** |
| category lồng nhau: id có sẵn, tạo mới | 4 | chấp nhận, khóa ngoại đúng | 4 PASS |
| Reader đọc `internal_notes` rõ ràng | 2 | 403 | 2 PASS |
| Reader `fields=*`, nested category | 4 | 200, chỉ bài published, không có `internal_notes` | 4 PASS |
| Anonymous mọi projection | 9 | 403 | 9 PASS |
| search toàn khoảng trắng; `page=0` | 2 | 200 rỗng; 200 trang đầu | 2 PASS |

## Tám ca FAIL: ba họ kích hoạt, cùng một cơ chế

Cả tám trả HTTP 500 `INTERNAL_SERVER_ERROR` cho actor editor. Log Directus xác nhận lỗi PostgreSQL gốc:

| Họ kích hoạt | Lỗi PostgreSQL trong log |
|---|---|
| `score = 2.5` (cột integer) | `invalid input syntax for type integer: "2.5"` |
| `published_at = ""` và `"not-a-date"` (cột timestamptz) | `invalid input syntax for type timestamp with time zone` (chuỗi rỗng và `NaN-NaN-NaNTNaN…`) |
| `metadata = "JSON text"` (cột json) | `invalid input syntax for type json` |

Cơ chế theo mã: Joi chỉ kiểm khoảng giá trị, còn `translateDatabaseError` chỉ dịch năm mã PostgreSQL (trùng khóa, ngoài phạm vi số, quá dài, null, khóa ngoại). Lỗi cú pháp giá trị (`22P02`, `22007`) không được dịch, nên rơi xuống bộ xử lý lỗi chung và thành 500, và không tạo hàng nào (transaction rollback).

**Phân loại:** ứng viên lỗi sản phẩm về độ bền (robustness), cùng họ với `P3-ROBUST-AGG-FOO` đã có. Không gán thành tám lỗi, và **chưa xác nhận là lỗi Directus**: đây là đầu vào ngoài miền schema, hành vi 500 vượt ngoài hợp đồng nhưng chưa có tài liệu Directus nói rõ phải trả 4xx. Cần reproducer và đối chiếu tài liệu trước khi kết luận.

## Lưu ý về tính trung thực

- **Bộ đánh giá được sửa hai lần sau khi thấy kết quả**, cả hai là lỗi logic phép so ảnh chụp bảng (ca PATCH có bước `setup`; ca chỉ đọc không cần so), không đổi oracle hay dự đoán. Lần sửa đầu làm kết quả xấu đi (17 FAIL), lần sau về 8 FAIL. Số cuối dùng bộ đánh giá đã sửa; kiểm 26 ca bị từ chối đều "không đổi".
- Dự đoán đạt 66/66 chỉ về **trạng thái HTTP** (mức khớp mạnh nhưng chưa kiểm hết nội dung body).
- Ca cần điều kiện (`NO-OFFSET`): container Directus có `TZ` mặc định UTC (kiểm `date +%Z` = UTC), nên oracle 08:00Z áp dụng được.
- Oracle chấp nhận `name=""` và `name="   "` là **suy từ mã** (không có luật nào từ chối). Nếu nhóm muốn coi đó là sai nghiệp vụ, đó là yêu cầu mới ngoài hành vi Directus, không phải oracle này.
- Bằng chứng chạy thô nằm ở `artifacts/runs/step2-oracle-*` (Git ignore); `results.json` là bản tổng hợp có thể commit.

## Tái tạo

```powershell
python -B scripts\oracle_v2.py emit
.\scripts\run-lab.ps1 test designed --group field-name
python -B scripts\oracle_v2.py evaluate --run-glob "artifacts/runs/step2-oracle-*"
```

Chạy lần lượt cho các nhóm `field-*` (`--group`) và từng ca quyền/query (`--case`), mỗi lượt với `LAB_RUN_ID` dạng `step2-oracle-<tên>`. `emit` ghi đè `oracle-v2.json`, đổi mốc thời gian và xóa dấu duyệt (về `PENDING_OWNER_REVIEW`); chỉ chạy lại khi cố ý tạo phiên bản oracle mới.
