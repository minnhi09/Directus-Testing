# Bộ ví dụ thiết kế P01

## Scope

Mọi record ở đây mang `data_origin: DESIGN_EXAMPLE`; ID đều thuộc namespace `EXAMPLE-`. Đây là fixture cho cấu trúc hợp đồng [1.0.0](../README.md), **không phải run, test mới, mapping TC/P3 thật hoặc kết quả Directus**. Không import vào số liệu nghiệm thu, không gán cho source/image baseline thực. Mọi count/percentage coverage = null, status = NOT_MEASURED, mẫu số UNLOCKED. Timestamp chạy, source SHA/image/hash chưa biết đều null có gap; không chèn SHA/credential giả.

## Oracle fixture

Giả sử có hai mục tiêu thiết kế A/B và hai ca canonical A/B. Oracle fixture chỉ minh họa một giá trị có thể được so expected/actual; không khẳng định hành vi sản phẩm hoặc status HTTP. Requirement A liên kết DIRECT tới hai ca; ca A liên kết DIRECT tới hai requirement. Edge requirement B → ca B là SUPPORTING và không góp coverage. Alias `EXAMPLE-TC-A` và `EXAMPLE-P3-A` cùng trỏ ca A chỉ trong fixture này; không cấp hai test độc lập. Tên alias thực chưa được đối chiếu ở P01.

## Cleanup fixture

Cleanup là một chiều có oracle/evidence riêng; ví dụ INCOMPLETE giữ contract FAIL, tool FAILED và cleanup FAIL. Đây là các giá trị **giả lập thiết kế** để chứng minh dữ liệu không làm mất FAIL; không có request, cleanup hoặc campaign thực nào được chạy. Operation evidence trong ví dụ ghi dispatch false/positive false để minh họa một response không chứng minh route đã hit. Ví dụ NOT_RUN không có evidence/timestamp. Ví dụ BLOCKED ghi legacy OPEN + thiếu oracle, không thay record lịch sử.

## Cách đọc bundle

- `baseline-manifest.json`: revision draft, mọi dữ liệu runtime null/gap; không sao chép manifest thật thành runtime mới.
- `system-inventory.jsonl`: GET list và GET detail tách biệt; một UI operation dùng protocol_operation, không giả làm REST; deploy/applicability chưa xác minh.
- `requirements.jsonl`, `test-catalog.jsonl`, `rtm-links.jsonl`: quan hệ nhiều–nhiều và alias, không đếm số dòng thành coverage.
- `executions.jsonl`: ba record NOT_RUN, INCOMPLETE/contract FAIL/cleanup FAIL, BLOCKED; đều DESIGN_EXAMPLE.
- `decisions.jsonl`: PROPOSED, approved_by null; không giả phê duyệt. `gaps.jsonl`: gap OPEN giữ mọi điều chưa xác minh.
- `selection-manifest.json`, `coverage-summary.json`: selection DRAFT chưa chọn run; metric NOT_MEASURED. Mảng rỗng không chứng minh không thiếu coverage.

Schema từng record được chọn theo tên file (thay `.json`/`.jsonl` bằng `.schema.json` ở `../schemas/`). JSONL validate từng dòng. Khi kiểm offline có thể bundle `$ref` từ `common.schema.json` trong bộ nhớ rồi dùng validator Draft 2020-12 sẵn có; không tải schema qua `$id`. Các foreign key, chuẩn hóa key, unique PK và projection RTM được kiểm ở mức fixture trong P01, không phải validator triển khai cho dữ liệu sản phẩm. Ràng buộc semantic đầy đủ nằm trong [hợp đồng](../README.md).
