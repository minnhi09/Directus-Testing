# Phase 0 - Bộ demo tham chiếu từ artifact hiện có

**Chọn ngày 18/10/2026.** Bộ này giúp chuẩn bị giữa kỳ 20/10. Chưa chạy lại demo trong Phase 0; chưa xác nhận Docker/API hiện khả dụng.

## 1. Cách giới thiệu đúng trạng thái

> Nhóm kiểm thử REST API của Directus trên hai collection lab, bằng OpenAPI và Schemathesis, kết hợp scenario/invariant nghiệp vụ. Artifact Windows ngày 13/10 ghi nhận sáu scenario PASS, 9 invariant PASS và 2 FAIL đang mở. Pilot raw/guided đã gửi test đến đủ 10 operation trên ba seed, nhưng vẫn có check failure/max_time. Bộ số liệu này chứng minh pipeline và giới hạn, không chứng minh toàn bộ Directus không có lỗi.

Không đọc to tất cả số liệu. Chọn một luồng, chỉ expected/actual và nguồn report; dùng finding để giải thích giá trị của K05.

## 2. Ba luồng demo chính

| Luồng | Evidence chính | Nội dung cần chỉ ra | Giới hạn cần nói |
|---|---|---|---|
| Editor CRUD | [Scenario S1](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json), [invariant editor-crud/positive-operations](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json) | Tạo, đọc, sửa, đọc lại, xóa; trường không sửa giữ nguyên; positive acceptance 5 operation mỗi collection | Scenario summary gọn; xem invariant để có status từng bước; ID động, không tái dùng ID lịch sử làm input live |
| Query | [S2/S3](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json), [query-fixture](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json) | Sáu published, sort/phân trang, page tương đương offset, search Unicode, projection | S3 so với full sorted list có giới hạn oracle; không gọi là coverage mọi query. Invariant bổ sung kiểm tra fixture và page/search |
| Quyền Reader | [S4/S5/S6](../../artifacts/runs/20261012T222311Z-1412/scenario-report.json), [reader-visibility/reader-write](../../artifacts/runs/20261012T185934Z-1453/invariant-report.json) | Draft/private projection bị chặn; Reader PATCH 403; Editor đọc lại để chứng minh dữ liệu không đổi | 403 là kết quả đúng của ca bị cấm; các schema trước OIG không thay bằng chứng quyền hiện tại |

Ba luồng cùng fixture r06-k05-v2, profile windows-20261013-oig. Metadata của suite scenario/invariant ghi actor=unspecified vì có nhiều actor trong suite; xem bước/case để xác định vai trò. Không ghi toàn suite là chạy bằng Editor chỉ để làm đầy provenance.

## 3. Hai finding để giải thích

### 3.1. Aggregate robustness candidate

Nguồn: [invariant report](../../artifacts/runs/20261012T185942Z-1219/invariant-report.json).

| Request query | Actual lịch sử |
|---|---:|
| `aggregate={"foo":1}` | 500 |
| `aggregate={}` | 200 |
| `aggregate={"count":["id"]}` | 200 |

Giải thích: Dữ liệu/query bất thường làm phát sinh 5xx trong khi control vẫn hoạt động. Giữ phân loại robustness candidate và schema omission; chưa khẳng định product defect đã xác nhận hay root cause từ source checkout mới. Run exit 1 được giữ nguyên.

### 3.2. Response contract/schema candidate

Nguồn: [contract probe](../../artifacts/runs/20261012T185950Z-1994/invariant-report.json) và [DELETE replay](../../artifacts/runs/20261012T191034Z-777/reproducer-schemathesis-j0ZjQ0.json).

- POST object trả `data` object trong khi response schema mô tả array cho hai collection.
- Export CSV có content type text/csv ngoài response map JSON.
- DELETE trả 204 ngoài các status khai báo trong schema.

Contract probe ghi bốn biểu hiện candidate; không gọi là bốn product defect. DELETE replay là single request, source/actual đều 204, status=reproduced, restore=0. Replay thành công có nghĩa tái hiện hiện tượng, không có nghĩa finding đã được sửa.

## 4. Minh họa sinh test K05

Mở [schema manifest](../../artifacts/runs/20261012T185734Z-1667/schema-manifest.json) để giải thích actor và inventory; sau đó mở [raw pilot index](../../artifacts/runs/20261012T185958Z-355/campaign-index.json) và [guided pilot index](../../artifacts/runs/20261012T190350Z-1047/campaign-index.json).

Chỉ cần nói rõ:

1. Schema Editor có 14 operation QA; campaign scope 10, loại bulk PATCH/DELETE.
2. Raw giữ contract của operation; guided thêm dữ liệu hướng dẫn và có phase stateful.
3. Mỗi profile dùng seed 101/202/303, 60 giây/seed, 10 examples; max-examples không phải tổng HTTP request.
4. Mỗi seed test đủ 10 operation, restore=0, nhưng runner=1/max_time; report có cả failure.
5. Đây là pilot, không phải campaign 1.200 giây. Không dùng số generated cases để khẳng định hiệu quả chi phí hay coverage code.

Số liệu chi tiết nằm trong [bảng Phase 0](00-hien-trang-va-baseline.md) và [campaign CSV](00-campaign-index.csv).

## 5. Lệnh dự kiến cho live demo khi runtime đã được preflight

Các lệnh dưới đây **chưa được chạy trong Phase 0**. Chạy từ workspace cha chứa DAMH và tmp, chỉ khi đúng lab và điều kiện dữ liệu/quyền đã được kiểm tra:

```powershell
& .\tmp\lab-tools\run-lab.ps1 doctor
& .\tmp\lab-tools\run-lab.ps1 replay editor-crud
& .\tmp\lab-tools\run-lab.ps1 replay query-fixture
& .\tmp\lab-tools\run-lab.ps1 replay reader-visibility
& .\tmp\lab-tools\run-lab.ps1 replay reader-write
```

Nếu muốn minh họa finding, chạy riêng từng lệnh và giữ mã thoát/report:

```powershell
& .\tmp\lab-tools\run-lab.ps1 replay aggregate-query-robustness
& .\tmp\lab-tools\run-lab.ps1 replay contract-schema-candidates
```

Doctor không đạt thì xử lý nguyên nhân hoặc chuyển sang đọc artifact; không dùng up/reset/seed như bước ứng biến mặc định. Dựng lại môi trường là công việc riêng với precondition và quyền phù hợp. Không chạy hai suite ghi dữ liệu đồng thời.

Để demo giữa kỳ gọn, dùng artifact pilot đã có; chưa cần chạy campaign dài trong giờ trình bày. Nếu dùng live pilot sau này, phải chốt budget và fixture trước, lưu run mới, không đưa kết quả nó vào bảng lịch sử cũ.

## 6. Checklist trước buổi demo

- [ ] Xác minh Docker/API thực tế; Phase 0 chưa hoàn tất bước này.
- [ ] Đúng runtime profile/fixture/schema; quyền Reader đúng, credential không lộ trên màn hình.
- [ ] Mở sẵn scenario/invariant/pilot report và metadata tương ứng.
- [ ] Chọn một luồng để giải thích test oracle, một finding để giải thích triage.
- [ ] Phân biệt case generated, HTTP request, check failure và defect.
- [ ] Nói đúng các giới hạn, chưa kết luận tối ưu chi phí khi chưa có thí nghiệm.
- [ ] Không dùng lời xác nhận review/đóng góp của người chưa thực hiện.

Nếu live demo không sẵn sàng, trình bày report đã chọn và nói rõ ngày/điều kiện chạy. Evidence dự phòng không được giả làm kết quả đang chạy trực tiếp.
