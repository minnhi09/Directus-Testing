# Kế hoạch bảo vệ cuối kỳ: slide, demo, câu hỏi dự kiến

Ngày bảo vệ và thời lượng mỗi nhóm **chưa được xác nhận** (theo [yêu cầu môn học](../../yeu_cau.pdf): theo lịch thi của nhà trường, báo cáo nộp trước một tuần). Mọi phân bổ thời gian và người trình bày dưới đây là **đề xuất** để nhóm chỉnh; chưa ai được giao. Bản slide nháp: `slide-bao-ve-k05.pptx` (tệp cục bộ, Git bỏ qua `docs/**/*.pptx`; dựng lại bằng `python scripts/build_defense_deck.py`), dựng từ báo cáo [BAO_CAO_CUOI_KY_K05.md](../BAO_CAO_CUOI_KY_K05.md); cần xem và chỉnh bằng mắt trước khi dùng.

## 1. Dàn slide (16 slide)

Mỗi slide ghi nguồn trong báo cáo để người trình bày kiểm tra lại số liệu.

| # | Nội dung | Ý chính | Nguồn |
|---|---|---|---|
| 1 | Tiêu đề | R06 Directus 12.5.0 + K05 Schemathesis 4.30.0; nhóm 11 | Đầu báo cáo |
| 2 | Vì sao chọn và phạm vi | Directus tự sinh OpenAPI nên hợp với K05; phạm vi là REST API trong OpenAPI của 3 actor, không phải "toàn bộ Directus" | A.2 |
| 3 | Hệ thống và actor | Admin (chỉ chuẩn bị), Editor 30, Reader 22, Anonymous 10 operation; fixture 3 category, 12 article | A.3, A.4 |
| 4 | Kiến trúc lab | Sơ đồ B.1: runner Schemathesis, Directus, PostgreSQL, bảo vệ trạng thái | B.1 |
| 5 | Môi trường và pin | Digest của 3 image, commit Directus `4f77933`, lệnh `doctor/up/seed/export-schema` | C.1, C.3 |
| 6 | Ba luồng nghiệp vụ | CRUD Editor, truy vấn/phân trang, quyền Reader (demo trực tiếp) | C.4 |
| 7 | Kỹ thuật K05 | Bốn pha, raw và guided, bảy check; `--max-time` đã đính chính | D.1 đến D.3 |
| 8 | "Đủ" nghĩa là gì | Mẫu số 62 cặp; tiêu chí C1–C6; không nói "100% Directus" | D.4, E.1 |
| 9 | Bộ 13 ca nghiệp vụ | 12 PASS, 1 FAIL; TC13 là chênh lệch hợp đồng `POST` (schema khai báo mảng, thực tế đối tượng) | E.2, G.1 |
| 10 | Tự động hóa | `lab.sh`, `LAB_ACTOR`, một seed làm gì, bảo vệ tác dụng phụ, định nghĩa "run hoàn tất" | F |
| 11 | Chiến dịch 18 run | 18/18 hoàn tất, restore PASS; 62/62 cặp có phản hồi; 10/10 CRUD có 2xx | G.3, G.4 |
| 12 | Coverage theo schema | operations 100% nhưng parameters 36–69%, keywords 17–48%, responses 19–26%: báo riêng, không gộp | G.5 |
| 13 | Failure và nguyên nhân gốc | 1.356 lần check thất bại, 237 nhóm, 16 nguyên nhân; 9 lỗi sản phẩm gây HTTP 500 | G.6 |
| 14 | Một lỗi minh họa | `aggregate={"foo":1}` trả 500; stack và dòng mã tại commit đã ghim | G.7 |
| 15 | Giới hạn và tái lập | Không phải coverage mã nguồn; chưa chạy trên máy thứ hai; cách chạy lại | G.9, H |
| 16 | Đóng góp và quy trình nhóm | Dữ kiện từ Git/GitHub, nói thẳng các giới hạn | [dong-gop-tu-git.md](dong-gop-tu-git.md) |

Gợi ý phân bổ (nhóm tự quyết): phần hệ thống, kiến trúc, môi trường (slide 2 đến 6); phần kỹ thuật và thiết kế (7 đến 10); phần kết quả và lỗi (11 đến 15). Phân người trình bày: **chưa chốt**.

## 2. Nguyên tắc nói số liệu

- Luôn nêu mẫu số: "62 trên 62 cặp (actor, operation)", "30 trên 30 operation của Editor".
- Tách ba con số: **31.147 request**, **1.356 lần check thất bại**, **16 nguyên nhân gốc** (9 lỗi sản phẩm). Không nói "tìm được 1.356 lỗi".
- Coverage luôn nói là **theo schema**, không phải mã nguồn.
- Kết quả 13 ca là **12 PASS, 1 FAIL**; không nới expected để ca FAIL đạt.
- Không nói "Directus không có lỗi" và không nói "đã kiểm thử 100%".

## 3. Kịch bản demo (chạy trực tiếp)

Điều kiện: Docker Desktop đang chạy, lab `r06-k05` đã `up` và `seed`, `config/lab.env` có trên máy; chạy từ thư mục `DAMH`. **Không reset DB** trước demo. Các lệnh chạy **tuần tự**, không song song.

| Bước | Lệnh | Kết quả mong đợi | Thời gian |
|---|---|---|---|
| 0. Kiểm tra | `.\scripts\run-lab.ps1 doctor` | `Doctor: PASS`, license active | vài giây (đã chạy 24/11) |
| 1. CRUD Editor | `.\scripts\run-lab.ps1 replay editor-crud` | invariant 1/1 passed, `Campaign restore: PASS` | đã chạy 24/11, chưa đo giờ |
| 2. Truy vấn | `.\scripts\run-lab.ps1 replay query-fixture` | passed (6 `published`, sort, hai trang, search `spéciale`) | chưa đo |
| 3. Quyền Reader | `.\scripts\run-lab.ps1 replay reader-visibility` rồi `replay reader-write` | passed; `internal_notes` bị 403; `PATCH` của Reader bị 403, dữ liệu không đổi | chưa đo |
| 4. Bộ 13 ca | `test scenarios` rồi `test designed --selection course` | S1–S6: 6 passed; 7 ca thiết kế: 6 passed, **1 failed (TC13)**, mã thoát 1 | S1–S6 khoảng 22 giây (24/11) |
| 5. Schemathesis | xem khối lệnh dưới | 32 ca sinh ra, 21 failure duy nhất, `termination=completed`, restore PASS, tác dụng phụ sạch | **55 giây** (đo 24/11, run `20261124T072243Z-1585`) |

```powershell
$env:LAB_ACTOR='anonymous'; $env:LAB_CAMPAIGN_SCOPE='full'; $env:LAB_CAMPAIGN_SEEDS='101'; $env:LAB_MAX_TIME='0'
.\scripts\run-lab.ps1 test raw       # mã thoát 1 là bình thường: Schemathesis tìm thấy lỗi
Remove-Item Env:LAB_ACTOR,Env:LAB_CAMPAIGN_SCOPE,Env:LAB_CAMPAIGN_SEEDS,Env:LAB_MAX_TIME
```

Một lệnh nữa nên tập để minh họa lỗi: sau khi có token Editor, gọi `GET /items/qa_articles?aggregate={"foo":1}` (mong đợi 4xx, thực tế 500). Chi tiết reproducer ở [wp7/README.md](../wp7/README.md), mục 4. **Chỉ gửi tới lab local**.

**Phương án dự phòng nếu lab không chạy (Docker lỗi, hết giờ):** dùng bằng chứng đã lưu: [bảng 62 cặp](../wp5/bang-phan-hoi-theo-cap.csv), [coverage](../wp6/coverage-theo-nhom.csv), [nhóm failure](../wp7/failure-groups.csv), [bằng chứng bộ 13 ca](../bang-chung-13-tc/README.md), và các hình trong [docs/images/bao-cao-giua-ky](../../images/bao-cao-giua-ky/). Nói rõ đó là kết quả đã chạy trước, không phải chạy lúc bảo vệ.

## 4. Danh sách kiểm tra trước buổi bảo vệ

- [ ] Chốt ngày bảo vệ, thời lượng, hạn nộp báo cáo (một tuần trước).
- [ ] Xem và chỉnh slide bằng mắt (bố cục, cỡ chữ, sơ đồ); nhóm phân người trình bày.
- [ ] Mỗi người điền [phiếu đánh giá chéo](danh-gia-cheo-mau.md); nhóm thống nhất nếu chênh lệch lớn.
- [ ] Trâm mô tả phần việc đã làm kèm bằng chứng ([dong-gop-tu-git.md](dong-gop-tu-git.md), mục 5).
- [ ] Tập demo ít nhất một lần trên máy sẽ dùng; chạy `doctor`; để Docker chạy sẵn.
- [ ] Kiểm tra không có credential, token hay license trên màn hình khi demo (che `config/lab.env`).
- [ ] Nhóm quyết định cách nêu việc dùng công cụ AI hỗ trợ ([dong-gop-tu-git.md](dong-gop-tu-git.md), mục 6).
- [ ] Nếu có thể, dựng lại từ đầu trên một máy thứ hai và ghi kết quả vào [xac-minh-clone-sach.md](xac-minh-clone-sach.md).

## 5. Câu hỏi dự kiến và hướng trả lời

Mỗi câu trả lời dựa trên báo cáo; người trả lời cần đọc lại mục nguồn.

| Câu hỏi | Hướng trả lời | Nguồn |
|---|---|---|
| Vì sao chọn K05 cho Directus? | Directus tự sinh OpenAPI theo quyền của từng actor, nên Schemathesis dùng được ngay mà không phải viết schema tay | A.1, D.1 |
| "Kiểm thử đủ" nghĩa là gì? | Định nghĩa bằng sáu tiêu chí trên mẫu số 62 cặp; không phải toàn bộ Directus và không phải coverage mã nguồn | D.4 |
| Vì sao 62 mà không phải 30? | 30 operation khác nhau, nhưng quyền khác nhau nên Editor thấy 30, Reader 22, Anonymous 10: 62 cặp | E.1 |
| Raw khác guided thế nào? | Raw dùng schema gốc, ba pha; guided thêm example và pha stateful; overlay chỉ thêm example, không sửa hợp đồng | D.2, E.4 |
| Sao không đặt `--max-time` ở campaign chính? | Với tùy chọn này Schemathesis lặp fuzzing đến hết giờ; pilot cho thấy 30 phút chỉ thêm vòng lặp, còn không đặt thì xong trong 27 giây với cùng 66 failure | D.3 |
| 1.356 lỗi à? | Không: 1.356 là số lần check thất bại; chúng quy về 237 nhóm và 16 nguyên nhân gốc, trong đó 9 là lỗi sản phẩm | G.6 |
| Lỗi nào là lỗi của Directus? | Nhóm gây HTTP 500 với đầu vào sai (ID ngoài `int4`, `aggregate` sai, `published_at` sai kiểu, NUL...) đã tái hiện và có thông điệp lỗi gốc; phần lớn failure còn lại là schema lệch hành vi thực | G.6, G.7 |
| Sao coi `204` là lỗi schema chứ không phải lỗi sản phẩm? | Directus trả `204` nhất quán cho `DELETE`; điều lệch là hợp đồng OpenAPI mô tả `200` | G.2, G.6 |
| TC13 FAIL có phải bug không? | Là chênh lệch hợp đồng đã xác nhận: schema khai báo `data` là mảng trong khi `POST` một đối tượng trả đối tượng; nghiệp vụ đạt | G.1 |
| Coverage 100% chưa? | Operations 100% (mỗi operation có request); các chiều khác thấp hơn và được báo riêng; không có "100% coverage" | G.5 |
| Sao không có lỗi bảo mật? | K05 không phải DAST; chưa đánh giá ý nghĩa bảo mật của các lỗi 500 | G.7, G.9 |
| Kết quả có tái lập được không? | Pin digest và commit, seed cố định, restore sau mỗi run; nhưng mới chạy trên một máy | H |
| Reader sửa được bài viết à? | Chỉ khi body rỗng, vì fixture cấp quyền `update` với `fields=[]`; có dữ liệu thì bị 403 | G.8 |
| Ai làm phần nào? | Dùng dữ kiện trong [dong-gop-tu-git.md](dong-gop-tu-git.md); nói thẳng giới hạn của số commit | WP9 |
| Có dùng AI không? | Trả lời theo quyết định của nhóm; thông tin có trong tài liệu đóng góp | mục 4 ở trên |
