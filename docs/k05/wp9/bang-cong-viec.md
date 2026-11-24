# Bảng công việc (Kanban) của nhóm 11

Cập nhật 24/11/2026. Nguồn: [bang-cong-viec.csv](bang-cong-viec.csv) (nhập được vào GitHub Project hoặc Trello), lịch sử Git và 16 GitHub Issue đã đóng. Cột "người thực hiện" ghi theo **dữ liệu Git/GitHub**; ô ghi "chưa xác nhận" hoặc "chưa phân công" nghĩa là nhóm chưa chốt. Đây không phải đánh giá đóng góp.

## 1. Công cụ quản lý hiện có

- **GitHub Issues:** 16 issue (`#1` đến `#16`) có nhãn loại, khu vực, ưu tiên và người được giao. Cả 16 được tạo ngày 10/10/2026 và **đóng cùng lúc ngày 26/10/2026**, nên không thể hiện tiến độ theo thời gian. Không có issue nào cho công việc từ 23/11/2026.
- **GitHub Project / Trello / Jira:** **chưa có**. Yêu cầu của môn học là có công cụ quản lý (Trello, Jira hoặc GitHub Projects) từ mốc 18/9; trong repo không có bằng chứng nào về công cụ đó trước ngày 10/10/2026.
- Để tạo GitHub Project cần cấp thêm quyền cho token của `gh` (`gh auth refresh -s project`), việc này do chủ tài khoản thực hiện; sau đó nhập `bang-cong-viec.csv`. Tôi không tự cấp quyền hay tạo Project.

## 2. Đã xong (Done)

| ID | Công việc | Người thực hiện | Bằng chứng / liên kết | Ghi chú |
|---|---|---|---|---|
| SCOPE | Thu nhỏ phạm vi về K05, gỡ 170 TC v2, pairwise, khung coverage/CI và hồ sơ nội bộ | Cookie1109 (Nhân), theo lệnh duyệt từng nhóm | PR #21; docs/k05/KE_HOACH_THU_NHO_VA_BO_SUNG_K05.md, mục 4 | Bản sao lưu ngoài repo; bằng chứng 13 TC được trích sang docs/k05/bang-chung-13-tc |
| WP1 | Chốt mẫu số 62 cặp (actor, operation) từ schema export lại | Cookie1109 (Nhân) | PR #21; docs/k05/mau-so-30-operation.csv | Người dùng duyệt 30 operation ngày 23/11/2026 |
| WP2 | Chạy raw/guided theo actor (editor, reader, anonymous) | Cookie1109 (Nhân) | PR #21; lab.sh, scripts/lab-components.sh | Thay đổi giao diện dùng chung; chưa có xác nhận của Lành |
| WP3 | Overlay guided cho assets, import, export, sort, auth | Cookie1109 (Nhân) | PR #21; wp5/bang-phan-hoi-theo-cap.csv |  |
| WP4 | Bảo vệ trạng thái và tác dụng phụ ngoài qa_* | Cookie1109 (Nhân) | PR #22; docs/k05/wp4/ |  |
| WP5 | Chiến dịch 18 run (3 actor × raw/guided × 3 seed) | Cookie1109 (Nhân) | PR #23; docs/k05/wp5/ | 18/18 hoàn tất, 62/62 cặp có phản hồi |
| WP6 | Coverage tracecov | Cookie1109 (Nhân) | PR #24; docs/k05/wp6/ |  |
| WP7 | Gom nhóm failure, nguyên nhân gốc, reproducer | Cookie1109 (Nhân) | PR #25; docs/k05/wp7/ | 16 nguyên nhân gốc |
| WP8 | Báo cáo cuối kỳ K05 phần A–H | Cookie1109 (Nhân) | PR #26; docs/k05/BAO_CAO_CUOI_KY_K05.md |  |
| FIX | Gỡ 1.864 file thêm nhầm ở PR #26 | Cookie1109 (Nhân) | PR #27 | Nội dung vẫn còn trong lịch sử Git |
| B07 | Xóa hai báo cáo cuối kỳ cũ (09-bao-cao-cuoi-ky, BAO_CAO_..._HOAN_CHINH) | Cookie1109 (Nhân), theo lệnh của người dùng | PR xóa hai báo cáo cũ (24/11/2026) | Còn trong lịch sử Git |

## 3. Đang làm (Doing)

| ID | Công việc | Người thực hiện | Bằng chứng / liên kết | Ghi chú |
|---|---|---|---|---|
| WP9 | Đóng góp, bảng công việc, mẫu đánh giá chéo, kế hoạch bảo vệ | Cookie1109 (Nhân) | docs/k05/wp9/ | Slide và demo: bản nháp trong wp9 |

## 4. Việc còn lại (Backlog)

| ID | Công việc | Người thực hiện | Bằng chứng / liên kết | Ghi chú |
|---|---|---|---|---|
| B01 | Trâm mô tả và đưa vào repo phần việc đã làm (fixture, policy, scenario) | Phan Thị Bảo Trâm (chưa xác nhận) | docs/k05/wp9/dong-gop-tu-git.md, mục 5 | Git chưa có commit nào của Trâm |
| B02 | Mỗi thành viên điền đánh giá chéo | Cả ba thành viên | docs/k05/wp9/danh-gia-cheo-mau.md | Điểm do từng người tự điền |
| B03 | Xem và chỉnh slide bảo vệ, phân người trình bày | Cả nhóm | docs/k05/wp9/ke-hoach-bao-ve.md | Ngày bảo vệ chưa xác nhận |
| B04 | Tập demo (bộ 13 ca, replay, một run Schemathesis ngắn) | Cả nhóm | docs/k05/wp9/ke-hoach-bao-ve.md, mục 3 |  |
| B05 | Dựng lại từ đầu trên máy thứ hai (đủ Docker, license) và ghi kết quả | Chưa phân công | docs/k05/wp9/xac-minh-clone-sach.md | Mới kiểm tra được phần không cần Docker |
| B06 | Tạo GitHub Project (hoặc Trello) và nhập danh sách này | Chủ repo | bang-cong-viec.csv | Cần quyền project cho token gh; xem README của wp9 |
| B08 | Quyết định xóa oracle_v2.py và phần còn lại của phase6 | Nhân quyết định | kế hoạch, mục 4.4 |  |
| B09 | Gỡ hàm p10_scenarios mồ côi trong lab-components.sh | Chưa phân công | kế hoạch, mục 4.2 | File dùng chung |
| B10 | Quyết định có xóa khỏi lịch sử Git 1.864 file thêm nhầm không | Nhân quyết định | PR #27 | Cần force-push main; Lành phải reset lại bản local |
| B11 | Chốt ngày bảo vệ và hạn nộp báo cáo (1 tuần trước bảo vệ) | Cả nhóm | yeu_cau.pdf, mục 4 | Chưa biết ngày |

## 5. Lịch sử giai đoạn G0 đến G1 (16 issue đã đóng)

| Người được giao | Issue | Nội dung |
|---|---|---|
| `minnhi09` (Lành) | #1, #2, #3, #11, #12, #16 | Bàn giao G0, môi trường lab, cấu hình chung, nghiệm thu G1, kiến trúc và truy vết A–H, tích hợp cuối kỳ |
| `btram0812` (Trâm) | #4, #5, #9, #10, #15 | Fixture và seed, policy bốn actor, scenario CRUD/filter/phân trang, scenario quyền Reader, invariant mở rộng |
| `Cookie1109` (Nhân) | #6, #7, #8, #13, #14 | Phân tích OpenAPI, xuất schema theo actor, pilot Schemathesis, campaign raw/guided, chuỗi stateful và replay |

Chi tiết commit, PR và các giới hạn của dữ liệu: [dong-gop-tu-git.md](dong-gop-tu-git.md).
