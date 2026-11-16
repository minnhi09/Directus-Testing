# Tích hợp P00–P15 với main — 16/11/2026

Nhánh local `integrate/p00-p15-20261116`, worktree riêng `../DAMH-p00-p15-integration`, giữ 11 commit P00–P15 và merge main `dfa7113d1eecf47dca15f1fad4945b75bb458d84`. Không thay checkout Directus hoặc workspace recovery. [17 resolution và 1.238 file được đối chiếu byte](conflict-resolutions.json).

11 conflict CSV/JSON có nội dung bằng nhau sau chuẩn hóa CRLF/LF: giữ byte P00–P15 để giữ hash nguồn. .gitattributes giữ toàn bộ quy tắc main và thêm byte policy của coverage; .gitignore hợp nhất hai bộ loại trừ. lab.sh giữ chức năng safety/snapshot của cả hai và Swagger/ownership của main; ba helper giữ namespace P09, Compose override và jq /server/. Không bỏ main hoặc chọn một phía toàn cây.

Raw OpenAPI, report, fixture/oracle và expected không đổi. TC13 vẫn business PASS/contract FAIL; V12/13 không phải chứng minh SUT contract PASS. [Archive ngoài Git](../../../ARCHIVES.md) ghi đúng tình trạng chưa công bố; [bản Markdown gốc và hash](archive-navigation.json) giữ nguyên byte trước chỉnh link. Tài liệu snapshot bất biến không sửa.

## Bộ file bàn giao

Dùng cây Git đã tích hợp, gồm schema/inventory/RTM/catalog/coverage/archive resolver, harness, regression/trace/contract diagnostic/pilot, test offline, profiles mẫu không secret và workflows. Không copy 2.364 file untracked hoặc runtime của workspace recovery. 39 file trước đây untracked đã được lấy từ main. README hỗ trợ dùng bản main; bản local khác vẫn được giữ nguyên ở recovery.

Liệt kê chính xác delta bàn giao với main pin:

```powershell
git diff --name-status dfa7113d1eecf47dca15f1fad4945b75bb458d84...HEAD
git log --oneline dfa7113d1eecf47dca15f1fad4945b75bb458d84..HEAD
python -B scripts/check_offline.py --output-dir artifacts/runs/integration-verification
python -B scripts/coverage_offline.py validate docs/coverage/acceptance/P15-HTTP-20261116-01/bundle
python -B scripts/coverage_offline.py calculate docs/coverage/acceptance/P15-HTTP-20261116-01/bundle
```

Giữ output/log riêng, không ghi đè evidence lịch sử. Git mode lab.sh và invariants.py giữ100755; filesystem Windows recovery có thể báo mode-only khi core.filemode=true. Checks Git dùng `-c core.filemode=false` theo từng lệnh khi cần; không đổi cấu hình chung để che thay đổi nội dung.

## Xác thực Git và CI

Remote gốc là SSH. Kiểm tra trước audit: Permission denied (publickey); SSH agent service Stopped, ssh-add exit2, không có *.pub trong thư mục SSH mặc định. Điều này không chứng minh tài khoản GitHub thiếu quyền repo hoặc không có khóa ở vị trí khác. HTTPS fetch công khai thành công chỉ chứng minh quyền đọc. Không in/lưu token, private key hoặc credential trong report.

Người vận hành tự thực hiện một trong hai cách:

- SSH: dùng khóa cá nhân hiện có hoặc tạo Ed25519 có passphrase; đăng public key vào đúng tài khoản GitHub có quyền repository; bật agent, nạp private key trên máy của mình; kiểm `ssh -T git@github.com` và quyền repo. Không đưa private key lên GitHub/Git hoặc gửi vào hội thoại.
- HTTPS: dùng Git Credential Manager với đăng nhập trình duyệt và quyền repository phù hợp; URL chỉ là `https://github.com/minnhi09/Directus-Testing.git`, không nhúng token vào URL/lệnh. Không cấu hình credential helper kiểu plaintext.

Sau khi xác thực và kiểm tra main chưa đổi, người dùng push nhánh tích hợp mới và mở PR vào main; không force-push nhánh feat cũ. Chưa thực hiện push/PR/remote merge. Static CI chạy PR; smoke chỉ manual dispatch trên trusted main sau review/merge được phép. Provision runner Windows/X64/damh-p09, private profile/ACL, fixture map, pinned jq/toolchain/lab và license entitlement tại chính runner theo [CI M2](../../../CI_M2.md). Không tự mở gate cho PR/fork. Remote run/artifact/upload/cleanup vẫn CHƯA XÁC MINH; TC13 exit1 tiếp tục được giữ.

[Kiểm chứng clone sạch commit89ab14a](verification.json):136/136 offline,8/8 static,coverage validate hợp lệ,R/D/E13,V12/13. Commit evidence tiếp theo chỉ bổ sung tài liệu; không coi đó là run SUT mới. SSH handshake không offer public key và trả exit255/publickey denied, host key không lỗi; còn cần người vận hành cấu hình khóa hoặc HTTPS Credential Manager. Kỹ thuật READY; push NOT_READY_AUTHENTICATION, CI remote NOT_RUN.
