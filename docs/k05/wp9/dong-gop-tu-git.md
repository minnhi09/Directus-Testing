# Đóng góp của thành viên theo dữ liệu Git và GitHub

Dữ liệu lấy từ `origin/main` tại commit `696e061` (24/11/2026, sau khi viết lại lịch sử), bằng [scripts/k05_git_contrib.py](../../../scripts/k05_git_contrib.py); kết quả đầy đủ: [git-contribution.json](git-contribution.json). Issue, PR và người được giao lấy từ GitHub (`gh api`) cùng ngày. Tài liệu chỉ ghi **dữ kiện**; nhận xét về mức đóng góp là việc của đánh giá chéo ([danh-gia-cheo-mau.md](danh-gia-cheo-mau.md)).

## 1. Cách đọc (quan trọng)

- **Số commit và số dòng không phải thước đo đóng góp.** Có commit nhỏ và commit lớn; có tài liệu sinh bằng công cụ, file sao chép và dữ liệu sinh tự động; nhiều việc không để lại commit (phân tích, kiểm tra, họp nhóm, review). Vì số dòng bị chi phối bởi các file JSON/CSV sinh tự động (và bởi hai commit thêm rồi gỡ nhầm 1.864 file ở PR #26 và #27), **tài liệu này không dùng số dòng**.
- Các tên tác giả khác nhau trong Git được gộp theo người: `minnhi09`, `Đinh Thị Mai Lành`, `Dinh Thi Mai Lanh` là một người; `Trương Võ Trọng Nhân`, `Truong Vo Trong Nhan` là một người (GitHub `Cookie1109`). Việc gộp dựa trên tên tác giả và phân công trong `AGENTS.md`; chưa xác nhận với từng người.
- Lịch sử `main` đã được viết lại **hai lần**: ngày 23/11/2026 để bỏ dòng đồng tác giả khỏi 17 commit, và ngày 24/11/2026 để xóa hẳn 1.864 file thêm nhầm ở PR #26 (commit gỡ ở PR #27 vì thế không còn trong lịch sử). Tác giả, nội dung và ngày của các commit còn lại không đổi; mã hash của các commit sau PR #25 đã đổi.

## 2. Commit trên `main`

| Thành viên | GitHub | Commit (không tính merge) | Số ngày có commit | Khoảng thời gian |
|---|---|---:|---:|---|
| Đinh Thị Mai Lành | `minnhi09` | 107 | 5 | 09/10 đến 19/10/2026 |
| Trương Võ Trọng Nhân | `Cookie1109` | 55 | 4 | 19/10 đến 24/11/2026 |
| Phan Thị Bảo Trâm | `btram0812` | **0** | 0 | không có |

Tổng: 162 commit không merge và 16 merge commit (178 đối tượng commit trên `main` tại `696e061`). Merge commit không được tính vào bảng (Lành 5, Nhân 11).

Phân bố theo ngày (commit không merge): Lành 2 (09/10), 3 (10/10), **97 (11/10)**, 3 (12/10), 2 (19/10); Nhân 5 (19/10), 13 (16/11), 18 (23/11), 19 (24/11). Hai nhận xét khách quan: (i) lịch sử tập trung vào ít ngày, 97 trong 107 commit của Lành nằm trong một ngày (11/10); (ii) không có commit nào từ 20/10 đến 15/11 và Git không cho thấy hoạt động của thành viên nào trong khoảng đó.

## 3. Pull request

| PR | Người tạo | Nội dung | Ngày merge |
|---|---|---|---|
| 17, 18 | `minnhi09` | Giao diện chung của lab và pilot | 10/10 |
| 19 | `minnhi09` | Tích hợp Swagger UI theo actor | 19/10 |
| 20 | `Cookie1109` | Bộ kiểm thử tự động và đánh giá độ bao phủ | 16/11 |
| 21 | `Cookie1109` | Thu nhỏ về K05, mẫu số, chiến dịch theo actor (WP1 đến WP3) | 23/11 |
| 22 | `Cookie1109` | WP4: tác dụng phụ ngoài `qa_*` | 23/11 |
| 23 | `Cookie1109` | WP5: chiến dịch 18 run | 24/11 |
| 24 | `Cookie1109` | WP6: coverage tracecov | 24/11 |
| 25 | `Cookie1109` | WP7: phân loại failure và nguyên nhân gốc | 24/11 |
| 26 | `Cookie1109` | WP8: báo cáo cuối kỳ K05 | 24/11 |
| 27 | `Cookie1109` | Gỡ file thêm nhầm ở PR #26 (commit này không còn trong lịch sử `main` sau khi viết lại) | 24/11 |
| 28 | `Cookie1109` | WP9: hồ sơ quản lý nhóm | 24/11 |
| 29 | `Cookie1109` | Xóa hai báo cáo cuối kỳ cũ | 24/11 |

Không PR nào do `btram0812` tạo. Không có review ghi nhận trên GitHub ở PR #20 (đã kiểm). Mọi PR được merge bằng merge commit.

## 4. Issue và người được giao

Có 16 issue (`#1` đến `#16`), tạo cùng ngày 10/10/2026, **đóng cùng ngày 26/10/2026 và cùng bởi `minnhi09`**. Nhãn theo loại, khu vực, ưu tiên.

| Người được giao | Issue | Nội dung chính |
|---|---|---|
| `minnhi09` (Lành) | #1, #2, #3, #11, #12, #16 | Bàn giao G0, môi trường lab, cấu hình chung, nghiệm thu G1, kiến trúc và truy vết A–H, tích hợp cuối kỳ |
| `btram0812` (Trâm) | #4, #5, #9, #10, #15 | Fixture và seed, policy bốn actor, scenario CRUD/filter/phân trang, scenario quyền Reader, invariant mở rộng |
| `Cookie1109` (Nhân) | #6, #7, #8, #13, #14 | Phân tích OpenAPI, xuất schema theo actor, pilot Schemathesis, campaign raw/guided, chuỗi stateful và replay |

Nhận xét khách quan: 16 issue cùng được đóng một lần nên **không phản ánh tiến độ theo thời gian**; không có issue nào cho công việc từ 23/11 (WP1 đến WP9); không có GitHub Project (token `gh` hiện thiếu quyền `read:project`, chưa kiểm tra được).

## 5. Phần của Trâm

- Được giao 5 issue (fixture và seed, policy, hai nhóm scenario, invariant mở rộng) và là collaborator của repository.
- Git **không có commit hay PR nào mang tên Trâm**. Điều này **không** có nghĩa Trâm không làm việc; có thể công việc được thực hiện rồi đưa vào repo qua tài khoản khác, hoặc chưa được ghi lại.
- Hiện không có bằng chứng nào trong repo cho phép gán phần việc cụ thể cho Trâm (không có file ghi tác giả, review hay biên bản). Mã fixture/seed và scenario nằm trong `scripts/lab-components.sh`, `scripts/designed_cases.py`, `scripts/invariants.py`, nhưng commit của chúng mang tên Lành hoặc Nhân.
- Việc cần làm trước bảo vệ (do nhóm quyết định): (a) Trâm tự mô tả phần mình đã làm kèm bằng chứng (file, ngày, nơi lưu), và nhóm đối chiếu; (b) nếu phần việc còn thật sự do Trâm thực hiện ở máy riêng, đưa vào repo bằng commit mang tên Trâm; (c) không ghi nhận đóng góp thay cho Trâm nếu chưa có bằng chứng. Tôi không suy đoán thay nhóm.

## 6. Công cụ hỗ trợ

Các thay đổi của WP1 đến WP9 (23 đến 24/11/2026) trên `main` được tạo trong các phiên làm việc của Nhân có sử dụng Claude Code (công cụ lập trình có trợ giúp AI) để hỗ trợ viết mã, tài liệu và chạy kiểm thử; Nhân duyệt từng quyết định phạm vi và chịu trách nhiệm về kết quả. Chưa xác minh việc dùng công cụ này với các commit trước ngày 23/11. Git không phân biệt được commit có hay không có sự hỗ trợ của công cụ. Nhóm cần quyết định cách nêu thông tin này với giảng viên.

## 7. Điều chưa đo được

Review chéo giữa thành viên, thời gian họp và phân tích, đóng góp không để lại commit, và phần việc của Trâm (mục 5) đều chưa có số liệu.
