# WP6 — coverage theo schema bằng tracecov (18 seed của WP5)

Số liệu lấy từ 18 file `schemathesis-coverage.json` của các run WP5 (ba actor × raw/guided × seed 101, 202, 303), tổng hợp bằng [scripts/k05_coverage_report.py](../../../scripts/k05_coverage_report.py). Thư mục `artifacts/runs/` bị Git bỏ qua nên các bảng CSV trong thư mục này là bản lưu gọn. Chỉ đọc file đã có, không chạy lại lab.

| File | Nội dung |
|---|---|
| [coverage-theo-seed.csv](coverage-theo-seed.csv) | 18 dòng: sáu chiều coverage của từng seed |
| [coverage-theo-nhom.csv](coverage-theo-nhom.csv) | 6 nhóm (actor, profile): min/trung bình/max của ba seed và phần hợp (union) |
| [coverage-theo-cap.csv](coverage-theo-cap.csv) | 62 cặp (actor, operation): mã phản hồi có trong schema đã/chưa gặp, mã không có trong schema đã gặp |
| [coverage-summary.json](coverage-summary.json) | Cùng số liệu nhóm ở dạng JSON |

## 1. Công cụ có thật trong bản đã pin

- `schemathesis run --help` của image `schemathesis/schemathesis:4.30.0` có nhóm *Coverage options*: `--coverage-format` (text, html, markdown, json), `--coverage-report-json-path`, `--coverage-show-missing`... Đây là tùy chọn chuẩn của 4.30.0, không cần cài thêm.
- Harness đã truyền `--coverage-format json --coverage-report-json-path /work/run/schemathesis-coverage.json` cho cả 18 seed. Mọi file đều ghi `tracecov_version: 0.25.2`, lược đồ `https://tracecov.sh/schemas/coverage-report.v1.json`. Vậy trạng thái C6 là **đo được**, không phải `NOT_MEASURED`.

## 2. Sáu chiều tracecov đo

| Chiều | Ý nghĩa |
|---|---|
| operations | operation được gửi ít nhất một request |
| parameters | tham số (query, path, header, body) được thử cả nhánh hợp lệ lẫn không hợp lệ |
| keywords | từ khóa JSON Schema (`type`, `required`, `nullable`, `enum`, `minimum`, `format`...) của tham số được thử cả hợp lệ lẫn không hợp lệ |
| examples | example có trong schema đã được dùng |
| responses | mã phản hồi **được mô tả trong schema** đã gặp ít nhất một lần |
| response_keywords | từ khóa trong schema phản hồi đã được chạm tới (reached) hoặc bị vi phạm (violated) |

**Đây là coverage theo schema OpenAPI, không phải coverage mã nguồn Directus.** "Tổng" của từng chiều là số mục trong schema theo actor đó.

## 3. Kết quả theo nhóm (trung bình ba seed, %)

| Actor / profile | operations | parameters | keywords | examples | responses | response_keywords |
|---|---:|---:|---:|---:|---:|---:|
| Editor raw (30 op) | **100** (30/30) | 51,7 (tổng 87) | 26,2 (tổng 516) | 92,6 (tổng 85) | 24,6 (15/61) | 21,6 (tổng 685) |
| Editor guided | **100** | 68,6 | 48,4 | 90,7 (tổng 86) | 24,6 | 28,9 |
| Reader raw (22 op) | **100** (22/22) | 51,4 (tổng 72) | 26,6 (tổng 428) | 93,7 (tổng 79) | 23,8 (10/42) | 21,5 (tổng 470) |
| Reader guided | **100** | 66,2 | 42,0 | 91,3 (tổng 80) | 26,2 (11/42) | 30,0 |
| Anonymous raw (10 op) | **100** (10/10) | 36,4 (tổng 11) | 17,1 (tổng 35) | 100 (tổng 9) | 18,8 (3/16) | 12,1 (tổng 132) |
| Anonymous guided | **100** | 36,4 | 17,1 | 100 (tổng 10) | 18,8 | 12,1 |

Ba seed của raw cho cùng số parameters/responses; seed chỉ làm keywords và response_keywords xê dịch nhẹ (Editor raw keywords 25,4 đến 26,6). Guided có chiều parameters cao hơn raw 15 đến 17 điểm phần trăm và keywords cao hơn 15 đến 22 điểm (Editor, Reader); guided thêm example, ID hợp lệ và pha stateful nên nhiều khả năng đây là nguyên nhân, nhưng tôi chưa tách riêng ảnh hưởng của từng yếu tố. Anonymous guided và raw giống hệt nhau (không có liên kết để stateful khai thác, đã ghi ở WP5).

**Phần hợp qua ba seed** (cột `union_*` trong `coverage-theo-nhom.csv`): từ khóa tham số Editor raw 141/516 (27,3%), Editor guided 266/516 (51,6%), Reader raw 117/428 (27,3%), Reader guided 193/428 (45,1%), Anonymous 6/35 (17,1%). Hợp không đổi nhiều so với trung bình nên việc chạy thêm seed gần như không mở rộng coverage; phần còn thiếu mang tính cấu trúc, không phải do hên xui của seed.

## 4. Các phần không tới được và lý do

Đếm trên 62 cặp (actor, operation) ([coverage-theo-cap.csv](coverage-theo-cap.csv)):

1. **Chỉ 15/61 mã phản hồi của Editor (và 3/16 của Anonymous) có trong schema được gặp.** Nguyên nhân quan sát được:
   - Directus trả `204` ở 9 cặp của Editor, 5 của Reader, 2 của Anonymous (ví dụ `DELETE /items/{collection}/{id}`, `POST /auth/logout`, `POST /auth/password/request`, `POST /utils/export/{collection}`), trong khi schema mô tả `200` hoặc không mô tả mã này. Đây là mã **không có trong schema** nên vừa làm chiều responses thấp, vừa sinh check `UndefinedStatusCode` (39 lần ở Editor raw, đã ghi ở WP5). Phân loại lỗi schema hay lỗi sản phẩm thuộc WP7.
   - Schema mô tả `401` cho nhiều operation, nhưng harness luôn gửi token hợp lệ cho Editor/Reader, nên `401` chỉ gặp ở nơi không có token (Anonymous) hoặc đăng nhập sai. Hiện `401` documented chưa gặp ở 20 cặp Editor, 12 cặp Reader, 5 cặp Anonymous.
   - Gặp `403` không có trong schema ở 15 cặp Editor, 11 cặp Reader, 2 cặp Anonymous, và `400` không có trong schema ở 19 cặp Editor, 13 cặp Reader, 3 cặp Anonymous.
   - `404` documented chưa gặp ở 8 cặp Editor, 5 cặp Reader, 2 cặp Anonymous. Có khả năng Directus kiểm tra quyền trước khi tìm ID và trả `403` thay vì `404`; tôi **chưa kiểm chứng** điều này (để WP7).
2. **33/62 cặp không gặp một mã phản hồi nào trong số mã mà schema mô tả** (chỉ gặp mã khác). Nhóm này khớp với danh sách không có 2xx ở WP5: `assets/{id}`, `auth/login|logout|password/*|oauth*`, `DELETE` hàng loạt trên hai collection, `utils/cache/clear|export|import|sort`. Lý do đã ghi ở WP3 (fixture không cấp quyền đọc file, không có provider OAuth, cần token qua email, `cache/clear` chỉ admin, import cần multipart).
3. **Từ khóa tham số chưa được thử cả hai nhánh.** Với Editor guided còn 250 từ khóa chưa đủ (phần hợp), trong đó 216 thuộc **thân request (body)** và 178 nằm dưới `/components/schemas/...`; theo loại: `type` 162, `nullable` 17, `oneOf` 15, `properties` 13, `enum` 10. Theo đường dẫn từ khóa trong báo cáo, thân `POST /items/qa_articles` do Directus xuất là `oneOf` (đối tượng hoặc mảng) và kéo cả định nghĩa `ItemsQaCategories` vào, nên một phần lớn từ khóa thuộc các nhánh này. Tôi chưa phân tích từng từ khóa để biết cái nào không thể tới; mục này là mô tả số liệu, không phải kết luận rằng chúng không tới được.
4. **Examples đạt 91–100%.** Phần thiếu (Editor raw 6/85) chưa liệt kê được từng example vì file báo cáo chỉ cho số đếm.

## 5. Điều không được suy ra từ bảng này

- Operation 100% nghĩa là mỗi operation đã nhận request (đúng với định nghĩa mẫu số 62 cặp ở WP1); **không** nghĩa là mọi tham số, mọi từ khóa hay mọi phản hồi đã được kiểm.
- Phần trăm responses thấp **không** đồng nghĩa Directus sai: một phần lớn do schema mô tả thiếu hoặc sai so với hành vi (xem mục 4.1); một phần do actor có token hợp lệ nên không bao giờ nhận `401`.
- Cột `tracecov_hits` trong `coverage-theo-cap.csv` là số đếm riêng của tracecov (tổng 77 cho Editor raw seed 101), **không** bằng số request ghi trong NDJSON và không được dùng để thay cho bảng 62 cặp ở [WP5](../wp5/README.md).
- Đây là coverage theo schema; không phải line/branch coverage của Directus và không chứng minh Directus không có lỗi.

## 6. Kết luận C6

C6 (coverage tracecov: tham số, từ khóa, phản hồi, example) **đạt phần đo và báo cáo**: đủ sáu chiều cho cả 18 seed, kèm danh sách phần chưa tới và lý do ở mục 4. Không đặt ngưỡng phần trăm nào làm điều kiện đạt vì tiêu chí của kế hoạch là đo và giải thích, không phải đạt một con số.

## 7. Tái lập

```powershell
python scripts/k05_coverage_report.py            # đọc artifacts/runs của 6 run WP5, ghi lại docs/k05/wp6/
python scripts/k05_coverage_report.py --run <run_id>   # chỉ định run khác
```
