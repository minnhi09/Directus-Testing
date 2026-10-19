# R06–K05 — Kiểm thử API Directus

Directus sinh API CRUD từ cơ sở dữ liệu. Nhóm dùng **Schemathesis và OpenAPI (K05)** để kiểm thử API của hai collection `qa_categories`, `qa_articles`, bổ sung các ca nghiệp vụ có kết quả mong đợi rõ ràng.

**Đọc và nộp:** [Báo cáo cuối kỳ](docs/HoanThanhPlan/09-bao-cao-cuoi-ky.md) · [Phạm vi và việc còn lại](docs/HoanThanhPlan/LO_TRINH_TOI_GIAN_R06_K05.md) · [Yêu cầu môn học](docs/yeu_cau.pdf).

## Phạm vi chính

- 13 ca/kịch bản đại diện: 6 scenario hiện có và 7 ca bổ sung.
- CRUD hai collection, lọc/sắp xếp/phân trang, quyền Reader/Anonymous và bốn giá trị biên score.
- Một ca đối chiếu phản hồi POST với OpenAPI; bằng chứng Schemathesis sinh test và tái hiện sai lệch.
- Thí nghiệm chi phí đã đo: 36 truy vấn so với 9 ca pairwise.

Danh sách và kết quả gốc của 13 ca nằm ở **E.3/G.2 trong báo cáo**. Bảng 118/257 ca và ma trận chi tiết là hồ sơ mở rộng, không phải khối lượng cần hoàn thành thêm. Giữ riêng bằng chứng 10/10 thao tác API có ca nghiệp vụ thành công.

## Chuẩn bị môi trường

Dùng Docker Desktop và Git Bash trên Windows. Phiên bản đã cố định: Directus 12.5.0, Schemathesis 4.30.0, PostgreSQL 16; tag/digest trong [manifest](manifest/baseline.yaml). API lab: `http://127.0.0.1:8055`, Docker project `r06-k05`.

Máy mới: chuẩn bị jq bằng `.\scripts\setup-windows.ps1`, sao chép `config/lab.env.example` thành `config/lab.env` rồi điền cấu hình cục bộ, gồm license hợp lệ đáp ứng policy Reader. Máy đã cấu hình giữ file thật. Xem **C.2 của báo cáo** để biết điều kiện và biến môi trường; không đưa mật khẩu/token/license thật vào gói nộp.

```powershell
.\scripts\run-lab.ps1 up
.\scripts\run-lab.ps1 doctor
.\scripts\run-lab.ps1 seed
.\scripts\run-lab.ps1 export-schema
```

Trên lab đã sẵn sàng, chỉ cần kiểm môi trường trước khi chạy. Không reset DB để demo; chạy các suite tuần tự. Linux/Git Bash dùng `./lab.sh` với cùng tham số.

## Chạy bộ đại diện

```powershell
.\scripts\run-lab.ps1 test scenarios
.\scripts\run-lab.ps1 test designed --selection course
```

Lệnh đầu chạy S1–S6. Lệnh thứ hai chạy 7 ca bổ sung; `test designed` không có tùy chọn cũng mặc định chọn `course`. Một kịch bản có thể gửi nhiều request và thực hiện nhiều phép kiểm; tổng là 13 ca/kịch bản, không phải 13 request.

Kết quả nằm tại `artifacts/runs/<run_id>/`: đọc `scenario-report.json` hoặc `designed-report.json`, `metadata.json` và kết quả khôi phục. Ca POST đối chiếu OpenAPI đã có bằng chứng FAIL hợp đồng; nếu tái hiện sai lệch, suite vẫn trả mã lỗi. Không đổi expected hoặc bỏ ca FAIL để có báo cáo xanh.

Bộ 13 được chọn từ kết quả đã lưu ngày 18/10; thay đổi lựa chọn không phải bằng chứng đã chạy mới cả bộ. Bộ `short` 58 ca và các lựa chọn `assertable`, `all`, `--case`, `--group` vẫn có để tra cứu/chạy có chủ đích khi cần.

## K05, chi phí và bàn giao

Campaign raw/guided lịch sử, schema, report và reproducer đã có; dùng chúng để giải thích cách sinh test và phát hiện sai lệch. Không cần chạy lại campaign dài. Chỉ xem 1–2 finding đại diện và bảng 36/9 khi báo cáo chi phí; những vấn đề chưa xác minh vẫn giữ OPEN.

Gói nộp gồm báo cáo, slide/demo, mã kiểm thử và dependency/config mẫu, schema/report/reproducer chọn lọc, cùng đánh giá đóng góp thật. Hồ sơ chi tiết nằm trong [mục lục](docs/HoanThanhPlan/README.md); các bản lưu không phải checklist phải làm tiếp. Không bổ sung CI/CD, quét lỗ hổng, load test hoặc điều tra mọi bất thường chỉ để hoàn thiện môn học.
