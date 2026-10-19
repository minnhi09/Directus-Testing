# 06 — Đối chiếu yêu cầu Phần 2

| Yêu cầu | Bằng chứng đã có | Trạng thái | Phần còn phải cập nhật |
|---|---|---|---|
| 1. Cơ sở lý thuyết, giới hạn, tiêu chí áp dụng | `01-co-so-ly-thuyet.md`; source `lab.sh`, `scripts/lab-components.sh`, `scripts/invariants.py`; AGENTS kỹ thuật | Đáp ứng | Không có code coverage Directus; giới hạn được ghi rõ |
| 2. Test Model, Scenarios, Test Cases | `02-test-model-va-test-cases.md`; 6 scenario, 11 invariant, 10 operation, actor/fixture matrix, campaign/replay cases | Đáp ứng | Guided seed 202 là incomplete nên không gọi toàn bộ profile là PASS |
| 3. Automation và thực thi | `03-trien-khai-automation.md`; cú pháp PASS; doctor/seed/smoke/export/scenario/invariant; raw/guided/replay đã chạy | Đáp ứng có giới hạn | Campaign có check failure; guided seed 202 bị ngắt nhưng restore PASS |
| 4. Log/metrics, phân tích kết quả/root cause | `04-ket-qua-kiem-thu.md`, `05-phan-tich-loi-va-root-cause.md`; report/coverage/NDJSON, restore, failure groups, hai replay | Đáp ứng có giới hạn | Chưa xác nhận product defect/root cause; không suy ra line/branch coverage |

Các giới hạn đã biết: không có line/branch coverage Directus, chưa chạy máy thứ hai, không kiểm thử hiệu năng/concurrency/DB recovery, và guided stateful có thể không replay được nếu parent mapping không đủ. Những mục này không được báo cáo là đã xác minh.

