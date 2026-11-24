# R06–K05 — Kiểm thử API Directus

Directus sinh API CRUD từ cơ sở dữ liệu. Nhóm dùng **Schemathesis và OpenAPI (K05)** để kiểm thử API của hai collection `qa_categories`, `qa_articles`, bổ sung các ca nghiệp vụ có kết quả mong đợi rõ ràng.

**Đọc và nộp:** [Báo cáo cuối kỳ K05](docs/k05/BAO_CAO_CUOI_KY_K05.md) · [Kế hoạch và tiến độ K05](docs/k05/KE_HOACH_THU_NHO_VA_BO_SUNG_K05.md) · [Yêu cầu môn học](docs/yeu_cau.pdf).

## Phạm vi chính

- 13 ca/kịch bản đại diện: 6 scenario hiện có và 7 ca bổ sung.
- CRUD hai collection, lọc/sắp xếp/phân trang, quyền Reader/Anonymous và bốn giá trị biên score.
- Một ca đối chiếu phản hồi POST với OpenAPI; bằng chứng Schemathesis sinh test và tái hiện sai lệch.

Danh sách và kết quả của 13 ca nằm ở **E.2 và G.1 trong báo cáo** (bản chạy lại ngày 24/11/2026: 12 PASS, 1 FAIL). Catalog 257 mã là thiết kế mở rộng, không phải khối lượng K05 (xem PL.1 của báo cáo). Phạm vi chiến dịch Schemathesis: 62 cặp (actor, operation) trên 30 operation.

## Chuẩn bị môi trường

Dùng Docker Desktop và Git Bash trên Windows. Phiên bản đã cố định: Directus 12.5.0, Schemathesis 4.30.0, PostgreSQL 16; tag/digest trong [manifest](manifest/baseline.yaml). API lab: `http://127.0.0.1:8055`, Docker project `r06-k05`.

Máy mới: chuẩn bị jq bằng `.\scripts\setup-windows.ps1`, sao chép `config/lab.env.example` thành `config/lab.env` rồi điền cấu hình cục bộ, gồm license hợp lệ đáp ứng policy Reader. Máy đã cấu hình giữ file thật. Xem **C.1 đến C.3 của báo cáo** để biết phiên bản, điều kiện và biến môi trường; không đưa mật khẩu/token/license thật vào gói nộp.

```powershell
.\scripts\run-lab.ps1 up
.\scripts\run-lab.ps1 doctor
.\scripts\run-lab.ps1 seed
.\scripts\run-lab.ps1 export-schema
```

Trên lab đã sẵn sàng, chỉ cần kiểm môi trường trước khi chạy. Không reset DB để demo; chạy các suite tuần tự. Linux/Git Bash dùng `./lab.sh` với cùng tham số.

## Xem OpenAPI bằng Swagger UI

Sau `seed` và `export-schema`, chạy `./lab.sh swagger up` rồi mở `http://127.0.0.1:8086`. Chọn Editor hoặc Reader, gọi `/auth/login` bằng tài khoản tương ứng, sau đó nhập `Bearer <access_token>` trong **Authorize**. Dùng `./lab.sh swagger down` để chỉ dừng giao diện. Schema gốc của Schemathesis không bị sửa. Xem [hướng dẫn Swagger UI](docs/swagger-ui.md) và [bằng chứng tích hợp](evidence/swagger-ui-integration-2026-10-19.md).

## Chạy bộ đại diện

```powershell
.\scripts\run-lab.ps1 test scenarios
.\scripts\run-lab.ps1 test designed --selection course
```

Lệnh đầu chạy S1–S6. Lệnh thứ hai chạy 7 ca bổ sung; `test designed` không có tùy chọn cũng mặc định chọn `course`. Một kịch bản có thể gửi nhiều request và thực hiện nhiều phép kiểm; tổng là 13 ca/kịch bản, không phải 13 request.

Kết quả nằm tại `artifacts/runs/<run_id>/`: đọc `scenario-report.json` hoặc `designed-report.json`, `metadata.json` và kết quả khôi phục. Ca POST đối chiếu OpenAPI đã có bằng chứng FAIL hợp đồng; nếu tái hiện sai lệch, suite vẫn trả mã lỗi. Không đổi expected hoặc bỏ ca FAIL để có báo cáo xanh.

Bộ 13 được chọn từ kết quả đã lưu ngày 18/10 và đã chạy lại ngày 24/11/2026 (báo cáo, G.1). Bộ `short` 58 ca và các lựa chọn `assertable`, `all`, `--case`, `--group` vẫn có để tra cứu/chạy có chủ đích khi cần.

## K05: chiến dịch Schemathesis

Chiến dịch đầy đủ chạy 18 run (3 actor × raw/guided × 3 seed) và kết quả được lưu gọn trong `docs/k05/` (xem [báo cáo, G.3 đến G.6](docs/k05/BAO_CAO_CUOI_KY_K05.md)). Chạy lại một cặp (actor, profile), tuần tự, không đặt `--max-time`:

```powershell
$env:LAB_ACTOR='editor'; $env:LAB_CAMPAIGN_SCOPE='full'; $env:LAB_MAX_TIME='0'
.\scripts\run-lab.ps1 test raw      # hoặc: test guided; actor: editor | reader | anonymous
```

Các bảng tổng hợp dựng lại bằng `python scripts/k05_reach_report.py`, `k05_coverage_report.py` và `k05_failure_triage.py`. Kiểm tra liên kết tài liệu: `python scripts/check_md_links.py`. Những vấn đề chưa xác minh vẫn giữ trạng thái "chưa kết luận" trong báo cáo.

Gói nộp gồm báo cáo, slide/demo, mã kiểm thử và dependency/config mẫu, schema/report/reproducer chọn lọc, cùng đánh giá đóng góp thật. Hồ sơ lịch sử của các giai đoạn trước nằm trong [mục lục HoanThanhPlan](docs/HoanThanhPlan/README.md); đó là bản lưu, không phải checklist phải làm tiếp. Không bổ sung CI/CD, quét lỗ hổng hay load test chỉ để hoàn thiện môn học.
