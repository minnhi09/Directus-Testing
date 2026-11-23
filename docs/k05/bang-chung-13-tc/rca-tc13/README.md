# Một nhiệm vụ: xác minh blocker M2-TC13

Ngày16/11/2026, Asia/Bangkok. **Triage COMPLETE; defect VERIFIED_OPEN_FAIL, chưa khắc phục. M2 vẫn NOT_ACCEPTED/BLOCKED.** Không xử lý thêm12contract evidence hoặc CI trong cùng batch. Không thêm canonical test hoặc tăng execution coverage vì tái kiểm offline.

## Nguồn và cách kiểm

Đã đọc kế hoạch/P15/tiến độ/gap-register, AGENTS của harness và source repo, Git status và TC13 trong P10-20261116-02. [Verification](verification.json) ghi input/hash/image/exit; [source index](source-index.json) ghi đúng Git object SHA4f77933bf9551cac6b289576078783e189b8f4e3 cùng trích đoạn có số dòng. Không đọc source HEAD thay pin, không sửa source/checkout.

Request của P3-CONTRACT-QA_ARTICLES-OBJECT là POST object, actor Editor, không phải array/bulk. Response-93 trả200 application/json,data object,id16; response-94 GET readback bằng đúngID khớp toàn bộ JSON đã capture. Business PASS và cleanup PASS đã ghi trong report gốc. ID16 là ID lịch sử của run này, **không dùng nó gọi lab hiện tại**.

Raw editor và raw admin cùng run đều khai báo POST /items/qa_articles response200.data type=array. Đã đối chiếu hash artifact; không nhầm actor hoặc dùng guided overlay. Tái validate nguyên bytes response-93 và nguyên raw editor bằng scripts/contract_checks.py trong đúng image Schemathesis4.30.0@digest, --pull never và --network none. Không gửi request HTTP, không login/seed/restore hoặc chạm DB/lab.

[Revalidation](revalidation.json) khớp bốn kết quả gốc: not_a_server_error,status_code_conformance,content_type_conformance PASS; response_schema_conformance FAIL/JsonSchemaError. Process exit0 nghĩa phép kiểm chạy thành công và tái hiện đúng FAIL, không phải TC13 PASS. Đây là offline captured-response revalidation, không phải một lần live replay/run mới.

## Kết luận có căn cứ

- controllers/items.ts:37–52 chọn createOne/readOne với request object, createMany/readMany với request array. services/items.ts:609 trở đi xác nhận readOne trả một item.
- services/specifications.ts:220–282 xử lý các method list, request body chấp nhận object hoặc array nhưng response200.data chọn object chỉ theo singleton; collection không singleton nhận type=array, kể cả POST object.
- Raw OAS và observed response khớp hai nhánh source đó. **Lỗi hợp đồng OpenAPI được sinh cho POST object trên collection không singleton được xác nhận**, không có bằng chứng business create/readback hỏng. Không kết luận mọi API/module hoặc mọi schema đều sai, không gán defect mới cho P14 cùng pattern.

## Khắc phục và coverage

Điểm cần sửa kỹ thuật là bộ sinh specification phải diễn tả response POST object/array đúng hành vi đã thiết kế, không phải đổi request thành array để né case hoặc sửa raw snapshot. Có thể chuẩn bị regression cho generator và một baseline sản phẩm sửa lỗi có nguồn trong nhiệm vụ riêng được giao. Batch này không sửa Directus baseline, không tạo corrected overlay rồi tính nó là raw PASS, không waiver/xfail/đổi expected.

Vì bản pin và raw hiện tại vẫn có mismatch, blocker M2-TC13 **còn mở**. Đã hoàn thành việc phân loại/xác minh, chưa hoàn thành việc khắc phục mandatory FAIL. Coverage P15 giữ D13/E13/V0; E không tăng vì kiểm offline lại response cũ.12execution thiếu contract evidence và remote CI NOT_RUN giữ nguyên; không coi root-cause confirmation là nghiệm thu.

Next task đề xuất: khắc phục source sinh OAS TC13 qua phạm vi/baseline được cấp quyền riêng (source ../directus hiện chỉ đọc), rồi kiểm lại hợp đồng. Tiếp sau đó bổ sung contract evidence cho12case theo oracle/baseline tương ứng; không tự chuyển Phase hoặc thực hiện nhiệm vụ thứ hai trong batch này. Không cần/không yêu cầu xác nhận để ghi nhận FAIL thật.

Checks: offline revalidation pinned image exit0, kết quả bằng report gốc; đối chiếu source@SHA và admin/editor schema; readback bytes bằng response; hash cũ/coverage/acceptance giữ nguyên. Các kiểm tra cuối ở audit-evidence.json. Không sửa test/config/expected, không cài package, không commit/push/PR/issue/liên hệ/sub-agent. Owner đề xuất Nhân contract/generator, Lành baseline; không gán review/xác nhận của họ.
