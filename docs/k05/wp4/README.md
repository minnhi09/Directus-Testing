# WP4 — thao tác có tác dụng phụ: kết quả và cách bảo vệ

Ngày 23/11/2026, lab local `r06-k05` (Directus 12.5.0). Mọi số liệu dưới đây lấy từ lần chạy thật; tôi ghi rõ chỗ nào chưa xác minh.

## 1. Thăm dò chủ động

Script `scripts/k05_side_effect_probe.py` (Python 3, thư viện chuẩn, chỉ chạy với `http://127.0.0.1:8055`, không in mật khẩu hay token, tự dọn). Kết quả đầy đủ: [probe-side-effects.json](probe-side-effects.json).

| Thao tác | Kết quả quan sát |
|---|---|
| `POST /auth/logout` với refresh token **giả** | 204, không ảnh hưởng gì |
| `POST /auth/logout` với refresh token **thật** | 204; **access token vẫn dùng được** (`/users/me` = 200); refresh token đó bị vô hiệu (401) |
| `POST /auth/refresh` với token giả | 401 |
| `POST /utils/cache/clear` | 403 với Editor, Reader, Anonymous |
| `POST /utils/import/qa_categories` bằng Editor | 200, **tạo đúng 1 dòng trong `qa_categories`**; không tạo file, người dùng nào |
| **30 lần đăng nhập sai** vào một người dùng tạm | Người dùng bị **`suspended`**; đăng nhập đúng sau đó cũng bị 401. Mọi lần sai đều trả 401 nên không thấy được ngưỡng chính xác (≤ 30; chưa xác minh con số 25 mặc định) |

**Hệ quả cho campaign**
- Token truy cập của actor không bị `logout`/`refresh` của Schemathesis làm hỏng (nó chỉ có refresh token giả).
- **Rủi ro thật:** `ADMIN_EMAIL` của lab đúng bằng `admin@example.com`, chính là email mẫu trong OpenAPI của Directus. Ở profile raw, Schemathesis gửi ví dụ này (mật khẩu sai) tới `POST /auth/login`; nếu đủ số lần sai liên tiếp, **admin bị tạm ngưng** và harness không còn khôi phục được. Các lần chạy thử trước chỉ gửi vài lần nên chưa chạm ngưỡng, nhưng campaign đầy đủ thì có thể. Tôi **không đổi** cấu hình Directus (ví dụ nâng giới hạn đăng nhập sai) vì như vậy là đổi hành vi của hệ thống được kiểm thử.

## 2. Bộ kiểm tra tác dụng phụ trong campaign

Trong `scripts/lab-components.sh`, mỗi seed của `test raw|guided`:

1. **Trước seed:** nếu không đăng nhập được (ví dụ tài khoản lab bị tạm ngưng), đặt lại tài khoản admin/editor/reader về `active` bằng SQL (chỉ ba email lab, ghi `account-recovery.json`) rồi đăng nhập lại.
2. **Chụp trạng thái ngoài `qa_*`:** số lượng và hash của 21 nhóm (roles, policies, permissions, access, files, folders, flows, operations, presets, dashboards, panels, shares, notifications, translations, versions, comments, users, collections, fields, relations, settings). `directus_activity` và `directus_revisions` **không so sánh** vì tăng theo mọi lần ghi.
3. **Sau seed** (chỉ cần token admin, không cần mọi actor đăng nhập được): so sánh, rồi
   - đặt lại trạng thái tài khoản lab nếu đổi (qua API);
   - xóa các **thông báo mới phát sinh** trong seed (xem mục 3);
   - mọi thay đổi khác **chỉ báo cáo, không tự xóa**, đánh dấu seed thất bại và **dừng các seed sau** để bảo vệ fixture.
4. Kết quả ghi vào `side-effects.json` và vào `campaign-summary.json` (`side_effects_exit_code`, `side_effects`).

## 3. Phát hiện từ các run không chen: `utils/export` tạo thông báo

Các run Editor và Reader (không chen gì) đều báo nhóm `notifications` đổi. Nguyên nhân: mỗi lần `POST /utils/export/qa_articles` (ví dụ overlay WP3) Directus tạo một dòng trong `directus_notifications` ("Your export of qa_articles failed"). Đây là tác dụng phụ hợp lệ của thao tác export. Đã thêm bước dọn: xóa đúng các thông báo mới phát sinh trong seed. Bốn thông báo do các run trước (chưa có bộ kiểm tra) để lại đã được xóa bằng tay.

## 4. Kiểm chứng

| Lần | Tình huống | Kết quả |
|---|---|---|
| 1 | Đối chứng âm: chen role lạ và tạm ngưng reader lúc campaign đang chạy | **Lỗi của bộ kiểm tra:** bước restore/audit sau seed đòi cả ba actor đăng nhập được nên bị bỏ qua khi reader bị tạm ngưng. Sửa: sau seed chỉ cần admin |
| 2 | Đối chứng âm lặp lại (reader đang bị tạm ngưng từ trước) | Trước seed: khôi phục reader qua SQL (đúng). Sau seed: phát hiện nhóm `roles` đổi (đúng) nhưng **không khôi phục được reader**. Lỗi của tôi: hàm chụp trạng thái chạy trong subshell nên danh sách trạng thái người dùng rỗng và các file `http-N.json` bị ghi đè. Sửa: không dùng subshell cho các lệnh gọi API |
| 3 | Đối chứng âm lần ba (run `20261123T145535Z-1001`) | **Đạt:** reader được khôi phục qua SQL trước seed và qua API sau seed (`suspended` → `active`), nhóm `roles` được báo là đổi, seed bị đánh dấu thất bại và dừng. Role lạ được xóa bằng tay sau đó |
| 4 | Editor guided `full`, 30 operation, không chen (run `20261123T150446Z-1304`) | Xóa 1 thông báo do export, **"sạch"** |
| 5 | Reader guided `full`, 22 operation, không chen (run `20261123T150730Z-1096`) | Xóa 1 thông báo do export, **"sạch"** |

Sau tất cả các lần: ba tài khoản lab `active`, không còn role lạ hay thông báo, fixture `qa_*` đúng 3 category và 12 article. 18 unit test vẫn đạt.

## 5. Giới hạn (chưa làm hoặc chưa xác minh)

- Ngưỡng khóa đăng nhập chính xác chưa xác định (≤ 30). Chưa kiểm chứng rằng đăng nhập thành công của harness đặt lại bộ đếm.
- Chưa kiểm tra riêng `utils/import` vào `qa_articles` và các collection khác (chỉ `qa_categories`).
- Bộ kiểm tra không phủ `directus_activity`, `directus_revisions` và thay đổi ở mức DB không đi qua API (ví dụ chỉ số sequence).
- Chỉ nhóm `notifications` và trạng thái tài khoản lab được tự khôi phục; role, file, người dùng mới... chỉ được báo cáo.
- Đường khôi phục bằng SQL chỉ chạy khi đăng nhập thất bại và chỉ đụng ba email lab; nó sửa trực tiếp bảng `directus_users`, nên ghi `account-recovery.json` để dò lại.
- `k05_side_effect_probe.py` cần Python 3 trên máy chạy (khác phần còn lại của harness chỉ cần Docker); nó là công cụ phát triển, không nằm trong luồng campaign.
