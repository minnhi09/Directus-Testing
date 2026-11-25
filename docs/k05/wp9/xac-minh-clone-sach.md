# Kiểm tra bản clone sạch của `main`

Mục đích: trước khi bảo vệ, kiểm tra xem người khác clone repository có dựng và kiểm tra lại được phần không cần Docker hay không. **Đây không phải lần dựng lại trên một máy mới**: chạy trên chính máy phát triển, trong một thư mục tạm.

Ngày 24/11/2026. Lệnh: `git clone https://github.com/minnhi09/Directus-Testing.git` (HTTPS), commit `9c4b6d8` (`main` sau PR #27; hash này không còn vì lịch sử `main` đã được viết lại ngày 24/11/2026, cây tệp giống hệt commit tương ứng mới). Thư mục tạm đã xóa sau khi kiểm tra.

## 1. Kết quả

| Kiểm tra | Kết quả |
|---|---|
| Số file Git theo dõi | 340 |
| File bắt buộc theo README (`compose.yaml`, `lab.sh`, `config/lab.env.example`, `manifest/baseline.yaml`, `scripts/run-lab.ps1`, `scripts/setup-windows.ps1`, `scripts/lab-components.sh`, `scripts/invariants.py`, `scripts/designed_cases.py`, `scripts/replay_cases.py`, báo cáo K05, mẫu số, `README.md`) | Có đủ |
| `config/lab.env` có trong bản clone không | Không (đúng kỳ vọng: file riêng, Git bỏ qua) |
| `config/lab.env.example` | 25 khóa; ba image ghim bằng digest; bốn mật khẩu mẫu đều là giá trị giữ chỗ bắt đầu bằng `REPLACE_`, không phải mật khẩu thật |
| `python -m unittest discover -s tests -p "test_*.py"` | 36 test, OK (tại thời điểm đó; hiện còn 33 sau khi xóa test của `oracle_v2`) |
| `bash -n lab.sh` và `bash -n scripts/lab-components.sh` | Cú pháp hợp lệ |
| `docker compose --env-file config/lab.env.example ... config -q` | Thành công (cấu hình hợp lệ, không khởi động dịch vụ) |
| `python scripts/check_md_links.py` trên toàn bộ file Markdown | 100 file, **144 liên kết hỏng** tại `9c4b6d8`; sau khi xóa hai báo cáo cũ (commit `8ad67a3`, 104 file): **123** (xem mục 2) |
| Cùng kiểm tra trên báo cáo K05, README, kế hoạch K05 và `wp4` đến `wp7` | 7 file, **0 liên kết hỏng** |

## 2. Liên kết hỏng trong bản clone sạch (144 tại `9c4b6d8`, 123 sau khi xóa hai báo cáo cũ)

Trên máy phát triển, kiểm tra liên kết báo cáo 18 liên kết hỏng (WP8) vì các file `artifacts/`, `runtime/`, `tmp/` và thư mục `tai-lieu-bo-tro/` tồn tại trên đĩa. Trong bản clone sạch chúng không có, nên số liệu thật là 144:

| Nhóm | Số | Nguyên nhân | Ảnh hưởng |
|---|---:|---|---|
| Trỏ tới `artifacts/runs/...` | 110 (91 sau khi xóa hai báo cáo cũ) | Thư mục `artifacts/` bị Git bỏ qua (artifact thô của từng run) | Chủ yếu báo cáo giữa kỳ, báo cáo thiết kế và hồ sơ `HoanThanhPlan`; liên kết chỉ dùng được trên máy đã chạy lab |
| Bản sao nguyên văn `bang-chung-13-tc/` | 14 | Giữ nguyên để khớp hash, trỏ tới file đã xóa | Không sửa |
| `runtime/`, `tmp/lab-tools/`, `../../directus/` (checkout upstream), `slide_bai_giang/` | 15 (14) | Thư mục ngoài repository hoặc bị Git bỏ qua | Tài liệu cũ |
| Đường dẫn máy khác hoặc thư mục riêng | 4 | `01_ke_hoach_trien_khai_R06_K05.md` (đường dẫn Linux của máy khác), `AGENTS.md` (thư mục riêng `mnhy/`) | Không sửa |
| Trỏ tới `tai-lieu-bo-tro/` (không commit) | 1 (0) | Thư mục này được giữ không commit có chủ đích; liên kết duy nhất nằm trong báo cáo cũ đã xóa | không còn |

Kết luận: báo cáo cuối kỳ K05, README và tài liệu `docs/k05/` đọc được hoàn toàn trên bản clone sạch; **các tài liệu cũ** (báo cáo giữa kỳ, hồ sơ `HoanThanhPlan`) có liên kết tới artifact thô chỉ tồn tại trên máy chạy lab. Số liệu của chúng đã được lưu gọn trong `docs/k05/` nên báo cáo cuối kỳ không phụ thuộc vào các liên kết đó.

## 3. Chưa được kiểm tra

- Kéo image Docker theo digest, `doctor`, `up`, `seed`, `export-schema` và các bộ kiểm thử: cần `config/lab.env` có license hợp lệ và mật khẩu riêng, tôi không có và không tạo.
- `scripts/setup-windows.ps1` (tải `jq` và kiểm checksum): cần mạng; chưa chạy trong bản clone.
- Máy thứ hai, hệ điều hành khác (Linux/macOS) và Docker khác phiên bản.
- Thời gian dựng từ đầu (kéo image, seed).

## 4. Cách ghi nhận một lần dựng trên máy thứ hai

Người thực hiện (không phải máy phát triển) làm theo [README](../../../README.md) và ghi lại: hệ điều hành, phiên bản Docker, commit đã clone, lệnh nào chạy thành công hoặc lỗi, thời gian từng bước, và kết quả `test scenarios` (kỳ vọng 6 passed) và `test designed --selection course` (kỳ vọng 6 passed, 1 failed). Thêm vào cuối file này kèm tên và ngày; **không ghi thay người khác**.
