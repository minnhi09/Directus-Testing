# WP9 — phần quản lý nhóm, đóng góp, đánh giá chéo, slide và demo

Phần này đáp ứng các yêu cầu **không phải kiểm thử** của [yêu cầu môn học](../../../yeu_cau.pdf): công cụ quản lý công việc, lịch sử Git, đánh giá chéo, slide và demo, README chạy lại. Ngày 24/11/2026. Mọi việc cần chính thành viên thực hiện (điền đánh giá, mô tả phần việc, quyết định cách nêu công cụ AI) **chưa được làm hộ**.

| File | Nội dung |
|---|---|
| [dong-gop-tu-git.md](dong-gop-tu-git.md), [git-contribution.json](git-contribution.json) | Dữ kiện đóng góp từ Git và GitHub, giới hạn của số liệu, phần của Trâm, công cụ hỗ trợ |
| [bang-cong-viec.md](bang-cong-viec.md), [bang-cong-viec.csv](bang-cong-viec.csv) | Bảng Kanban WP1 đến WP9 và việc còn lại; CSV để nhập vào GitHub Project hoặc Trello |
| [danh-gia-cheo-mau.md](danh-gia-cheo-mau.md) | Mẫu đánh giá chéo, **chưa điền** |
| [ke-hoach-bao-ve.md](ke-hoach-bao-ve.md), `slide-bao-ve-k05.pptx`, [scripts/build_defense_deck.py](../../../scripts/build_defense_deck.py) | Dàn slide, kịch bản demo (đã tập một phần), câu hỏi dự kiến; slide nháp là tệp cục bộ (Git bỏ qua `docs/**/*.pptx`), dựng bằng script |
| [xac-minh-clone-sach.md](xac-minh-clone-sach.md) | Kiểm tra bản clone sạch của `main`, phần chưa kiểm tra được |
| [scripts/k05_git_contrib.py](../../../scripts/k05_git_contrib.py) | Script thống kê đóng góp từ Git |

## Đối chiếu yêu cầu của môn học

| Yêu cầu (trang của PDF) | Trạng thái | Bằng chứng và ghi chú |
|---|---|---|
| Nhóm 3 đến 5 sinh viên (tr. 2) | Đạt | 3 thành viên (`AGENTS.md`, mục 3) |
| Chọn 1 repo và 1 kỹ thuật; ghi commit SHA/tag (tr. 3, mốc 18/9) | Đạt | R06 Directus + K05; tag `v12.5.0`, commit `4f77933bf9551cac6b289576078783e189b8f4e3` ([manifest](../../../manifest/baseline.yaml)). Repo không có bằng chứng về ngày đăng ký |
| Công cụ quản lý công việc từ mốc 18/9 (tr. 3, 5) | **Chưa đủ** | Có 16 GitHub Issue tạo 10/10 và đóng cùng lúc 26/10; chưa có GitHub Project/Trello/Jira; không có issue cho việc từ 23/11 |
| Phần 1: đọc hiểu mã nguồn, kiến trúc, luồng dữ liệu 3 đến 5 nghiệp vụ, cài đặt, tài liệu cài đặt (tr. 1) | Đạt (với giới hạn) | Báo cáo K05 phần A đến C; README. Luồng dữ liệu chi tiết nằm ở báo cáo giữa kỳ (mục 6) |
| Phần 2: cơ sở lý thuyết, kịch bản, mã tự động, chạy, log, lỗi, nguyên nhân gốc (tr. 2) | Đạt | Báo cáo phần D đến G; `docs/k05/wp4` đến `wp7` |
| Báo cáo cấu trúc A đến H (tr. 2 đến 3) | Đạt | [BAO_CAO_CUOI_KY_K05.md](../BAO_CAO_CUOI_KY_K05.md) |
| Phần B: ít nhất một sơ đồ kiến trúc component/container và 3 đến 5 module liên quan (tr. 2) | Đạt (module nêu ngắn) | B.1 (sơ đồ), B.2, B.3 |
| Phần C: bằng chứng hệ thống chạy và ít nhất 3 luồng nghiệp vụ (tr. 2) | Đạt | C.4; bộ 13 ca chạy lại 24/11/2026 |
| Phần F: mã chạy lại tự động và README có lệnh, dependency (tr. 2) | Đạt | README; `lab.sh`; chưa chứng minh trên máy thứ hai |
| Phần G: log, metrics, lỗi, nguyên nhân (tr. 3) | Đạt | G.3 đến G.8 |
| Phần H: pin commit/tag, lưu cấu hình, cách chạy lại trên máy mới (tr. 3) | Đạt (chưa kiểm chứng máy mới) | H; [xac-minh-clone-sach.md](xac-minh-clone-sach.md) |
| Lịch sử Git cho thấy các thành viên tham gia đều đặn (tr. 4) | **Không đạt cho Trâm; yếu về đều đặn** | Trâm 0 commit; 97/107 commit của Lành trong một ngày; không có commit từ 20/10 đến 15/11 ([dong-gop-tu-git.md](dong-gop-tu-git.md)) |
| Slide gọn, trình bày tự tin, phối hợp tốt (tr. 4) | Bản nháp | `slide-bao-ve-k05.pptx` (tệp cục bộ, Git bỏ qua `docs/**/*.pptx`; dựng lại bằng `python scripts/build_defense_deck.py`) cần nhóm xem và chỉnh; chưa phân người trình bày |
| Demo chạy script automation khi bảo vệ (tr. 3) | Sẵn sàng, cần tập | [ke-hoach-bao-ve.md](ke-hoach-bao-ve.md), mục 3 (bước 5 đã chạy thử, 55 giây) |
| Đánh giá chéo cuối kỳ (tr. 3, 4) | Có mẫu, **chưa điền** | [danh-gia-cheo-mau.md](danh-gia-cheo-mau.md) |
| Báo cáo nộp trước bảo vệ một tuần (tr. 3) | **Chưa xác định** | Ngày bảo vệ chưa biết |

## Việc cần chính nhóm làm

1. Chốt ngày bảo vệ và hạn nộp báo cáo.
2. Trâm mô tả phần việc và đưa vào repo bằng commit của mình nếu có ([dong-gop-tu-git.md](dong-gop-tu-git.md), mục 5).
3. Từng người điền phiếu đánh giá chéo.
4. Tạo công cụ quản lý công việc: cấp quyền `project` cho token `gh` (`gh auth refresh -s project`, do chủ tài khoản làm) rồi nhập [bang-cong-viec.csv](bang-cong-viec.csv), hoặc dùng Trello; ghi rõ ngày tạo, **không lùi ngày**.
5. Xem và chỉnh slide; tập demo; quyết định cách nêu việc dùng công cụ AI hỗ trợ.
6. Nếu có thể, dựng lại từ đầu trên máy thứ hai và ghi kết quả.
