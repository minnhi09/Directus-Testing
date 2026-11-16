# P15 / M2 — Nghiệm thu evidence offline, 16/11/2026

**P15 COMPLETE về báo cáo; M2 NOT_ACCEPTED / gate BLOCKED.** Không có phê duyệt, waiver hoặc acceptance PASS. [Acceptance](acceptance.json), [coverage](coverage-summary.json), [missing IDs](missing-ids.json), [gap/owner](gap-register.json), [audit](audit-evidence.json).

Scope là regression13 được nhóm11 khóa nội bộ tại M1-REGRESSION-13-v1; P14/category là pilot hỗ trợ. Inventory toàn hệ thống vẫn tham khảo; P11–P13 không nằm trong đường K05 được chọn, không suy hoàn tất hoặc tự đổi N/A. Không mở rộng mẫu số, không ghi giảng viên đã phê duyệt subset.

## Kết quả

| Chỉ số | Kết quả | Giới hạn |
|---|---|---|
| Requirement có thiết kế D/R | 13/13 | Chỉ subset khóa nội bộ |
| Requirement được đánh giá E/R | 13/13 | FAIL cũng là evaluated; không là pass rate |
| Requirement verified V/R theo P01/P08 | 0/13 | 12 execution thiếu dimension contract; TC13 contract FAIL |
| Quan sát case gốc P10 | 12 PASS,1 FAIL | Không thay report gốc; TC13 business PASS/contract FAIL |
| Missing selected execution | Không thiếu13 ID | Evidence contract còn thiếu12, không đồng nghĩa mọi mandatory đã đạt |
| Hit/positive/schema keyword/code coverage | NOT_MEASURED | Không suy dispatch/readback từ title hoặc5template |
| CI | Static local PASS; regression local FAILED; remote NOT_RUN | Workflow có file không chứng minh Actions đã chạy |

## Chuẩn hóa có nguồn

[Bundle](bundle/) sao chép resolved-inputs P10 có snapshot source đúng hash; giữ baseline ID, canonical/version/RTM/denominator/approval gốc. Selection dùng đúng13 execution ID đã predeclare của P10-20261116-02; manifest copy chỉ thêm run ID tham chiếu. Không sửa bundle gốc hoặc chuyển historical run sang baseline mới.

executions.jsonl là **DERIVED từ report thật**, không phải run mới. Mỗi record dẫn source@SHA/pointer tới scenario/designed report, oracle từ RTM và cleanup evidence. S1–S6 chỉ có enclosing run timestamps, ghi rõ không phải thời gian từng ca; designed cases có timestamps riêng. tool_exit_code là chuẩn hóa outcome từng case, không giả13 CLI process; suite exit1 ở report gốc vẫn giữ. operation_evidence để rỗng vì chưa import dispatch/readback theo inventory key, không tạo metric giả.

P01 executions schema yêu cầu contract PASS hoặc NOT_APPLICABLE cho execution PASS. Report gốc12case có contract NOT_RUN, nên không thể chuẩn hóa PASS mà giữ đúng schema. **Giữ NOT_RUN**, đánh dấu execution/completion INCOMPLETE/EVIDENCE_MISSING; không đổi source case PASS, không gán NA hoặc sửa schema/tool. Vì P08 V đòi execution PASS, kết quả V=0 là mức evidence theo hợp đồng này, **không phải kết luận0 hành vi nghiệp vụ chạy đạt**. TC13 normalized FAIL, contract FAIL, business PASS. Finding ID được giữ trong gap register có nguồn; executions.finding_id=null vì P08 chưa nhận finding registry, không giả ref tồn tại.

Lần normalize đầu bị SCHEMA_VALIDATION_FAILED đúng12case; không nới validator. Sau đó FINDING_REGISTRY_NOT_SUPPLIED được giải bằng bỏ foreign key chưa được registry hỗ trợ, giữ known issue ở register/source, không xóa failure. Bundle cuối validate/calculate exit0, synthetic=false. Không dùng sample fixture làm evidence thật, không cộng alias/retry/generated examples.

## Acceptance và dependency

P08 tool/26 unit checks đã có evidence; P10 run đủ13 và cleanup snapshot khớp; P14 raw/guided giữ FAIL/max_time, restore và teardown được xác minh tại run. P15 chỉ đọc metadata/reports, không kiểm lại runtime hoặc API. P14 representative replay tái hiện JsonSchemaError, chưa exact-byte replay/parent chain. Raw CLI complete=true không đổi completion budget thành khám phá đầy đủ; generated failure không là defect count/canonical case mới.

M2 chưa đạt do TC13 mandatory FAIL, thiếu12 contract evidence theo P01 và chưa có remote CI run. P14 findings/budget và operation/keyword evidence được ghi gap riêng; không tự đặt yêu cầu mọi module/3seed dài hoặc miễn required checks. Owner chỉ **đề xuất** trong gap register, không gán review/đồng ý cho thành viên. Không hỏi phê duyệt để hợp thức hóa FAIL; việc cần tiếp theo là thu/triage evidence hợp lệ trong lượt được giao.

## Tái lập offline

Từ root DAMH:

```powershell
python -B scripts/coverage_offline.py validate docs/coverage/acceptance/M2-P15-20261116/bundle
python -B scripts/coverage_offline.py calculate docs/coverage/acceptance/M2-P15-20261116/bundle
```

[Commands](commands.json) ghi exit thực. Reference/hash/schema checks không gọi SUT hoặc tải URI schema ngoài. Không sửa test/config/expected; không cài package; một probe jsonschema cho biết host không có package đó, đã dùng PowerShell Test-Json có sẵn qua P08, không cài thêm. Không commit/push/PR/issue, campaign hoặc sub-agent. Lịch sử P00–P14/TC01–TC13/raw OAS giữ nguyên.

Batch P15 đã xong; M2 gate vẫn BLOCKED. Tiếp theo xử lý gap M2 ở phase được giao; đường K05 dự kiến P18/P19 chỉ sau đối chiếu prerequisite, chưa tự chuyển P16/P18 hoặc nghiệm thu.
