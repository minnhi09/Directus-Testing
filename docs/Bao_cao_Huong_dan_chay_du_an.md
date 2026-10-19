# BÁO CÁO HƯỚNG DẪN CHẠY DỰ ÁN

**Dự án R06 Directus + K05 Kiểm thử API bằng Schemathesis**

**Ngày biên soạn:** 16/10/2026  
**Đối tượng đọc:** Người mới, chưa biết cấu trúc và cách sử dụng dự án.  
**Môi trường hướng dẫn chính:** Windows, PowerShell và Docker Desktop tại workspace `D:\DAMH-full-recovery-2026-10-12`.

> Các lệnh được đối chiếu với mã và cấu hình hiện có. Bằng chứng chạy thực tế được tham chiếu từ ngày 13/10/2026; khi viết tài liệu này không khởi động dịch vụ hoặc chạy lại bộ kiểm thử. Trạng thái dịch vụ ở thời điểm người đọc thực hiện cần được kiểm tra bằng các bước bên dưới.

## 1. Dự án này dùng để làm gì?

Dự án có hai phần phối hợp với nhau:

- **Directus:** phần mềm quản lý dữ liệu, trong thử nghiệm này gồm chuyên mục và bài viết. Người dùng có thể mở trang quản trị để xem dữ liệu.
- **Bộ kiểm thử K05:** các chương trình gửi yêu cầu đến Directus để kiểm tra việc tạo, đọc, sửa, xóa, lọc dữ liệu và phân quyền. Schemathesis là công cụ tự tạo thêm nhiều yêu cầu dựa trên bản mô tả API.

API có thể hiểu là nơi chương trình gửi yêu cầu như “lấy danh sách bài viết” hoặc “sửa điểm của bài viết”. Directus xử lý yêu cầu và trả lại kết quả.

Dự án chạy bằng Docker. Docker chuẩn bị các môi trường có sẵn cho Directus, cơ sở dữ liệu PostgreSQL và công cụ kiểm thử. Người chạy theo hướng dẫn này không cần tự build mã nguồn Directus hay cài riêng Node.js, Python hoặc PostgreSQL trên Windows.

### Nên bắt đầu ở đâu?

| Nhu cầu | Phần cần đọc |
|---|---|
| Máy đã được cấu hình, chỉ muốn mở dự án và xem dữ liệu | Mục 2–4 |
| Lần đầu chuẩn bị môi trường Windows | Mục 2, mục 5, sau đó quay lại mục 3–4 |
| Muốn chạy kiểm thử và xem báo cáo | Mục 6–8 |
| Muốn dừng và mở lại lần sau | Mục 9 |
| Gặp lỗi | Mục 10 |
| Chuyển dự án sang máy khác | Mục 11 |

## 2. Nhận biết thư mục và cửa sổ chạy lệnh

### 2.1. Cấu trúc đang dùng trên máy này

```text
D:\DAMH-full-recovery-2026-10-12\
├── DAMH\
│   ├── lab.sh                    Chương trình điều phối các lệnh của dự án
│   ├── compose.yaml              Mô tả các thành phần chạy bằng Docker
│   ├── config\
│   │   ├── lab.env.example       Mẫu cấu hình để tham khảo
│   │   └── lab.env               Cấu hình riêng trên máy
│   ├── scripts\                  Mã chuẩn bị dữ liệu và kiểm thử
│   ├── runtime\                  Thông tin dữ liệu mẫu và bản mô tả API
│   ├── artifacts\runs\           Báo cáo, log của từng lần chạy
│   └── docs\                     Tài liệu
├── tmp\lab-tools\
│   ├── run-lab.ps1               Bộ gọi lệnh từ PowerShell
│   ├── jq                       Tệp hỗ trợ xử lý JSON trên Git Bash
│   └── jq.exe                    Chương trình jq
└── directus\                     Mã nguồn tham khảo của Directus
```

`config/lab.env`, `runtime/` và báo cáo trong `artifacts/` là dữ liệu cục bộ, có thể chưa có khi nhận một bản sao mã nguồn mới. Chúng được tạo hoặc chuẩn bị trong quá trình thiết lập.

Thư mục `directus` dùng để tham khảo mã nguồn; các lệnh trong hướng dẫn chính chạy bộ Docker ở thư mục `DAMH`.

### 2.2. Mở PowerShell và chọn đúng thư mục

Mở menu Start, tìm **Windows PowerShell** và mở ứng dụng. Các bước sử dụng thông thường không yêu cầu mặc định mở bằng quyền quản trị.

Nhập dòng sau và nhấn Enter:

```powershell
Set-Location 'D:\DAMH-full-recovery-2026-10-12'
```

Trong các mục hướng dẫn Windows bên dưới, đường dẫn bắt đầu bằng `.\` được tính từ thư mục này. Nếu đóng cửa sổ rồi mở lại, hãy chạy lại lệnh chọn thư mục trước khi tiếp tục.

Kiểm tra các tệp quan trọng bằng:

```powershell
Test-Path '.\DAMH\lab.sh'
Test-Path '.\DAMH\compose.yaml'
Test-Path '.\tmp\lab-tools\run-lab.ps1'
Test-Path '.\tmp\lab-tools\jq'
Test-Path '.\tmp\lab-tools\jq.exe'
Test-Path 'C:\Program Files\Git\bin\bash.exe'
```

Mỗi dòng cần trả về `True`. `False` nghĩa là không tìm thấy tệp tại vị trí đang kiểm tra. Khi đó, xem lại thư mục hoặc bước chuẩn bị ở mục 5.

### 2.3. Cách đọc một lệnh chạy dự án

Ví dụ:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 up
```

Phần cuối `up` là tên công việc cần thực hiện. `run-lab.ps1` gọi Git Bash để chạy `DAMH/lab.sh` với đúng các tệp hỗ trợ Windows. `-ExecutionPolicy Bypass` chỉ áp dụng cho tiến trình PowerShell được mở bằng lệnh này; hướng dẫn không yêu cầu đổi chính sách chạy script của toàn máy.

Sao chép phần lệnh bên trong khung, không sao chép các dấu đánh dấu khung Markdown.

## 3. Mở nhanh hệ thống đã được cấu hình

Phần này dành cho máy đã có Docker, các tệp hỗ trợ và `DAMH/config/lab.env` hợp lệ. Nếu đây là lần đầu thiết lập, thực hiện mục 5 trước.

### Bước 1 — Mở Docker Desktop

Mở Docker Desktop từ menu Start, chờ Docker Engine sẵn sàng. Dự án sử dụng Linux containers.

### Bước 2 — Mở PowerShell tại workspace

```powershell
Set-Location 'D:\DAMH-full-recovery-2026-10-12'
```

### Bước 3 — Khởi động dự án

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 up
```

Lệnh này khởi động cơ sở dữ liệu, Directus và môi trường công cụ kiểm thử, rồi chờ các thành phần đạt trạng thái sẵn sàng. Lần đầu có thể mất lâu hơn vì Docker cần tải image — gói môi trường chạy có sẵn.

Chờ lệnh kết thúc trước khi nhập lệnh tiếp theo. Khi lệnh báo lỗi, xử lý nguyên nhân ở mục 10 trước khi chuyển sang kiểm thử.

### Bước 4 — Kiểm tra môi trường

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 doctor
```

`doctor` kiểm tra công cụ, cấu hình, image, kết nối và trạng thái hệ thống. Các dòng `OK` biểu thị nội dung kiểm tra đạt; dòng `FAIL` cần được đọc và xử lý.

Sau mỗi lệnh, có thể kiểm tra mã kết thúc ngay bằng:

```powershell
$LASTEXITCODE
```

Thông thường, `0` nghĩa là lệnh hoàn thành thành công. Giá trị khác `0` cần được giải thích theo loại lệnh; với kiểm thử, nó có thể do một kiểm tra không đạt, không chỉ do không khởi động được hệ thống.

`doctor` có thể có các dòng `INFO` về license hoặc tài khoản. Hãy đọc cả nội dung đó; riêng việc `doctor` thành công chưa chứng minh bộ kiểm thử quyền Reader đã chạy đạt.

### Bước 5 — Mở Directus

Mở trình duyệt và nhập:

**Trang quản trị:** <http://127.0.0.1:8055/admin>

Địa chỉ `127.0.0.1` có nghĩa là máy đang sử dụng. Trang này chỉ truy cập được trên máy đang chạy Docker với cấu hình mặc định của dự án.

Có thể kiểm tra API đang trả lời tại:

**Đường dẫn ping:** <http://127.0.0.1:8055/server/ping>

Kết quả mong đợi là `pong`. Kết quả này chứng minh API có phản hồi, chưa chứng minh toàn bộ dữ liệu và quyền đều đúng.

## 4. Đăng nhập và xem dữ liệu

### 4.1. Tài khoản đăng nhập

Mở tệp `DAMH/config/lab.env` bằng trình soạn thảo trên máy và xem:

- `ADMIN_EMAIL`: email quản trị; mẫu cấu hình dùng `admin@example.com`.
- `ADMIN_PASSWORD`: mật khẩu quản trị đã được cấu hình.

Khi đăng nhập, dùng phần giá trị sau dấu `=`, không nhập cả tên biến. Không đưa mật khẩu hoặc toàn bộ tệp cấu hình vào ảnh chụp, báo cáo hoặc nơi chia sẻ.

Nếu cơ sở dữ liệu đã có từ trước, tài khoản Admin được tạo ở lần khởi tạo trước đó. Chỉ sửa `ADMIN_PASSWORD` trong tệp cấu hình không đồng nghĩa mật khẩu của tài khoản đã lưu trong cơ sở dữ liệu được đổi theo.

### 4.2. Dữ liệu cần nhìn thấy

Sau khi đăng nhập, vào phần quản lý nội dung và tìm:

| Nhóm dữ liệu | Ý nghĩa | Bộ dữ liệu mẫu ban đầu |
|---|---|---|
| `qa_categories` | Chuyên mục | 3 bản ghi |
| `qa_articles` | Bài viết | 12 bản ghi: 6 bài nháp và 6 bài đã công bố |

`draft` là bài nháp; `published` là bài đã công bố.

Dùng Admin để truy cập giao diện quản trị. Editor và Reader trong cấu hình của lab là tài khoản phục vụ kiểm thử qua API, không phải tài khoản được cấp quyền dùng Studio.

### 4.3. Nếu chưa có dữ liệu mẫu

Nếu đây là lần chuẩn bị mới và cấu hình đã hoàn tất, chạy bước `seed` ở mục 6.1. Nếu dữ liệu đã có từ lần trước, việc mở lại hệ thống thông thường không yêu cầu seed lại.

Bộ kiểm thử dựa trên các giá trị mẫu đã biết. Khi muốn chạy kiểm thử tái lập, nên giữ dữ liệu mẫu đúng như thiết kế; các thay đổi thủ công có thể làm ca kiểm thử thất bại do điều kiện ban đầu không còn đúng.

## 5. Thiết lập lần đầu trên Windows

### 5.1. Chuẩn bị công cụ

| Công cụ | Vai trò | Cách chuẩn bị |
|---|---|---|
| Docker Desktop | Chạy Directus, PostgreSQL và môi trường kiểm thử | Cài theo [hướng dẫn Docker chính thức cho Windows](https://docs.docker.com/desktop/setup/install/windows-install/), hoàn tất yêu cầu hệ thống và mở ứng dụng |
| Git for Windows | Cung cấp Git Bash để chạy script `.sh` | Cài từ [trang Git dành cho Windows](https://git-scm.com/install/windows); launcher hiện dùng `C:\Program Files\Git\bin\bash.exe` |
| jq và wrapper Windows | Đọc, xử lý dữ liệu JSON trong các script | Bộ workspace hiện có `tmp/lab-tools/jq` và `jq.exe`; nguồn jq chính thức tại [trang tải jq](https://jqlang.org/download/) |
| Trình duyệt | Mở Directus Studio | Dùng trình duyệt có trên máy |

Wrapper `jq` đi kèm dự án xử lý một số khác biệt về đường dẫn và xuống dòng trên Git Bash. Chỉ có `jq.exe` chưa đủ để coi cấu hình Windows tương đương workspace này.

Sau khi cài công cụ, mở lại PowerShell. Có thể kiểm tra Docker bằng:

```powershell
docker version
docker compose version
```

`docker version` cần kết nối được cả phía Client và Server. Nếu chỉ thấy Client rồi báo không kết nối được Server, mở Docker Desktop và chờ Engine sẵn sàng.

### 5.2. Chuẩn bị bộ mã và tệp hỗ trợ

Đặt `DAMH` và `tmp/lab-tools` theo cấu trúc ở mục 2, rồi chạy các lệnh `Test-Path` để xác nhận.

Các tệp hỗ trợ Windows đang nằm ngoài repository `DAMH`. Nếu chỉ clone riêng `DAMH`, đường dẫn `tmp/lab-tools/run-lab.ps1` có thể không tồn tại. Khi đó, cần nhận thêm bộ hỗ trợ Windows của workspace từ người bàn giao, hoặc dùng môi trường Bash độc lập ở mục 11. Không giả định mọi bản clone đều có các tệp cục bộ này.

### 5.3. Tạo tệp cấu hình khi chưa có

Từ PowerShell tại workspace, dùng đoạn sau. Đoạn lệnh chỉ sao chép mẫu khi chưa có cấu hình, tránh ghi đè cấu hình đang dùng:

```powershell
if (-not (Test-Path -LiteralPath '.\DAMH\config\lab.env')) {
    Copy-Item -LiteralPath '.\DAMH\config\lab.env.example' -Destination '.\DAMH\config\lab.env'
}
```

Sau đó mở `DAMH/config/lab.env` bằng trình soạn thảo và thay các giá trị bắt đầu bằng `REPLACE_` bằng giá trị riêng trên máy.

| Biến | Ý nghĩa và cách điền |
|---|---|
| `DB_PASSWORD` | Mật khẩu riêng cho cơ sở dữ liệu của lab |
| `DIRECTUS_KEY` | Khóa cấu hình riêng cho ứng dụng |
| `DIRECTUS_SECRET` | Chuỗi bí mật ngẫu nhiên; mẫu dự án yêu cầu ít nhất 32 byte |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Tài khoản quản trị dùng lúc khởi tạo cơ sở dữ liệu mới |
| `EDITOR_EMAIL`, `EDITOR_PASSWORD` | Tài khoản biên tập dùng qua API |
| `READER_EMAIL`, `READER_PASSWORD` | Tài khoản chỉ đọc dùng qua API |
| `LICENSE_KEY` | Khóa Directus hợp lệ để dùng chính sách Reader tùy chỉnh của lab; nếu chưa có thì để giá trị rỗng |

Với người mới, có thể dùng trình quản lý mật khẩu để tạo và lưu các chuỗi ngẫu nhiên; giá trị gồm chữ và số giúp tránh nhầm cách biểu diễn ký tự đặc biệt trong tệp cấu hình. Không dùng nguyên chữ `REPLACE_...` làm mật khẩu thật.

Giữ các giá trị image, tên cơ sở dữ liệu và URL theo mẫu. Bản dự án đang dùng Directus **12.5.0**, PostgreSQL **16-alpine** và Schemathesis **4.30.0**, có mã định danh image cụ thể trong `lab.env.example`.

Các URL mặc định là:

```dotenv
API_URL=http://127.0.0.1:8055
RUNNER_API_URL=http://directus:8055
```

URL thứ nhất dùng từ máy Windows; URL thứ hai dùng giữa các thành phần trong mạng Docker. Hai địa chỉ có vai trò khác nhau, không thay bằng nhau.

### 5.4. Quyền đọc tệp cấu hình trên Windows

Bộ chạy kiểm tra quyền truy cập của `config/lab.env`. Nếu quyền quá rộng, lệnh có thể dừng với thông báo yêu cầu ACL riêng tư. ACL có thể hiểu là danh sách tài khoản được phép đọc hoặc sửa tệp.

Khi cần chỉnh, mở **Properties → Security → Advanced** của đúng tệp `DAMH/config/lab.env`. Giữ quyền cho tài khoản Windows đang chạy dự án; các nhóm hệ thống `SYSTEM` và `Administrators` cũng được bộ kiểm tra chấp nhận. Nếu tệp đang kế thừa quyền đọc cho nhóm khác, tắt kế thừa cho riêng tệp rồi điều chỉnh các mục quyền đó.

Chỉ chỉnh tệp cấu hình này, không đổi quyền cả ổ đĩa hoặc thư mục dự án. Trên Windows, bộ chạy kiểm tra ACL; chạy `chmod` trong Git Bash không thay thế được bước kiểm tra này.

### 5.5. License và kiểm thử Reader

Chính sách của lab yêu cầu Reader chỉ thấy bài đã công bố và không thấy trường nội bộ. Cấu hình Directus được kiểm thử sử dụng tính năng `custom_permission_rules_enabled` cho phần này.

Nếu có khóa hợp lệ, điền vào `LICENSE_KEY`, lưu tệp rồi chạy `up` để ứng dụng nhận cấu hình. Dùng `doctor` để xem trạng thái license đã được rút gọn, không cần in khóa ra màn hình.

Nếu chưa có license phù hợp, Directus có thể vẫn mở được, nhưng bước `seed` và các kiểm tra Reader có thể chưa hoàn tất hoặc bị chặn. Đây là hai mức kết quả khác nhau: **mở được ứng dụng** và **sẵn sàng chạy đủ kiểm thử**. Không coi phần bị chặn là đã đạt.

### 5.6. Tải môi trường chạy và khởi động

Khi cấu hình đã lưu và Docker Engine sẵn sàng, từ workspace chạy:

```powershell
docker compose --env-file .\DAMH\config\lab.env --project-name r06-k05 -f .\DAMH\compose.yaml pull
```

Lệnh tải các image đã ghi trong cấu hình. Cần có Internet nếu máy chưa có sẵn image.

Sau khi tải thành công, chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 up
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 doctor
```

Chạy từng lệnh, đọc kết quả rồi mới chuyển bước. Nếu trước đó dùng `doctor` khi chưa tải image hoặc chưa khởi động dịch vụ, một số kiểm tra có thể chưa đạt; hãy kiểm tra lại sau bước này.

## 6. Chuẩn bị dữ liệu và chạy kiểm thử cơ bản

Thực hiện các bước dưới đây theo thứ tự. Với lần chuẩn bị đầu, cần `seed` thành công trước khi coi dữ liệu và quyền đã sẵn sàng.

### 6.1. Tạo dữ liệu mẫu — `seed`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 seed
```

Lệnh chuẩn bị hai nhóm dữ liệu, ba chuyên mục, 12 bài viết, tài khoản Editor/Reader và các quyền liên quan. Nó cũng ghi thông tin ánh xạ giữa tên bản ghi mẫu và ID thật.

Kết quả hoàn tất mong đợi có dòng:

```text
Seed: PASS (3 categories, 12 articles, 6 draft, 6 published)
```

Seed được thiết kế để nhận diện dữ liệu mẫu đã có và không nhân bản khi trạng thái tương thích. Nếu dữ liệu hoặc cấu trúc không tương thích, lệnh có thể dừng và báo lỗi; không xem seed là công cụ tự sửa mọi thay đổi thủ công.

### 6.2. Kiểm tra nhanh — `smoke`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 smoke
```

Smoke là bộ kiểm tra nhanh để phát hiện vấn đề cơ bản: đăng nhập actor, đọc dữ liệu, ràng buộc trường, quan hệ giữa chuyên mục và bài viết, quyền đọc của Reader.

Lệnh này có tạo/xóa dữ liệu kiểm tra tạm, không chỉ đọc trạng thái dịch vụ. Chờ lệnh hoàn tất và xem kết quả trước khi tiếp tục.

### 6.3. Xuất bản mô tả API — `export-schema`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 export-schema
```

Schema là bản mô tả để chương trình biết API có thao tác nào, nhận dữ liệu gì và trả về dạng nào. Bộ kiểm thử cần bản mô tả được xuất từ đúng hệ thống, dữ liệu và actor đang dùng.

Launcher Windows mặc định dùng profile `windows-20261013-oig`, nên các tệp runtime được lưu dưới:

```text
DAMH/runtime/profiles/windows-20261013-oig/
```

Schema được lưu tiếp trong `schemas/r06-k05-v2/` với cấu hình hiện tại. Khi không sử dụng profile, đường dẫn mặc định của `lab.sh` là `runtime/`.

Profile tách nơi lưu tệp runtime, không tạo cơ sở dữ liệu riêng. Các profile vẫn có thể cùng thao tác trên dữ liệu Docker của lab.

Nếu đổi license hoặc điều kiện xuất schema, cần giữ snapshot cũ và dùng profile phù hợp; không ghi đè bằng cách xóa tệp cũ chỉ để lệnh chạy tiếp. Tham khảo quy tắc snapshot trong [README](../README.md).

### 6.4. Chạy sáu kịch bản — `test scenarios`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 test scenarios
```

Bộ này kiểm tra sáu tình huống:

1. Editor tạo, đọc, sửa và xóa bài viết.
2. Lọc bài theo trạng thái đã công bố.
3. Sắp xếp và chia danh sách thành từng trang.
4. Reader không đọc được bài nháp.
5. Reader không xem được ghi chú nội bộ.
6. Reader sửa bị từ chối và dữ liệu đối chiếu không đổi.

Kết quả mong đợi khi các điều kiện đầy đủ và tất cả kiểm tra đạt là `6 passed`, `0 failed`, `0 blocked`. Đây là tiêu chí để đối chiếu lần chạy, không phải lời khẳng định mọi máy đều sẽ đạt ngay.

### 6.5. Chạy các kiểm tra bổ sung — `test invariants`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 test invariants
```

Invariant có thể hiểu là quy tắc cần luôn được giữ đúng, ví dụ sửa một trường không làm mất trường khác. Bộ hiện có 11 ca, kiểm tra thêm token giả, người chưa đăng nhập, đủ 10 thao tác API, truy vấn, quan hệ dữ liệu và sự khớp nhau giữa phản hồi với schema.

Trong bằng chứng Windows ngày 13/10/2026, bộ này ghi **9 PASS, 2 FAIL, 0 BLOCKED**. Hai ca FAIL liên quan yêu cầu thống kê bất thường trả 500 và chênh lệch giữa phản hồi thực tế với schema. Vì vậy, mã kết thúc `1` của bộ này có thể là kết quả kiểm thử thực sự, không đồng nghĩa Docker chưa chạy được.

Chi tiết các ca và giới hạn được giải thích trong [Báo cáo thiết kế kịch bản kiểm thử](Bao_cao_Thiet_ke_kich_ban_kiem_thu.md).

## 7. Chạy kiểm thử tự sinh yêu cầu và chạy lại một ca

### 7.1. Phân biệt hai chế độ

| Chế độ | Cách hiểu |
|---|---|
| `raw` | Sinh yêu cầu từ bản mô tả API đã chọn đúng phạm vi 10 thao tác |
| `guided` | Bổ sung ví dụ và ID mẫu hợp lệ; kiểm tra thêm các chuỗi thao tác liên quan |

Các bộ này có thể tạo, sửa và xóa dữ liệu trong quá trình thử, rồi khôi phục bộ dữ liệu đã lưu. Chạy tuần tự trên lab; không mở hai cửa sổ để chạy hai bộ có ghi dữ liệu đồng thời.

Chỉ chạy sau khi môi trường, dữ liệu và các điều kiện trước kiểm thử đã được kiểm tra. Nếu khôi phục dữ liệu báo lỗi, xử lý lỗi đó trước khi chạy bộ tiếp theo.

### 7.2. Chạy thử ngắn trước

Đoạn PowerShell dưới đây chạy `raw` với một seed, tối đa 10 example mỗi thao tác và giới hạn runner 60 giây. Nó giữ lại các thiết lập môi trường trước đó và khôi phục sau khi chạy:

```powershell
$savedPilotSeeds = $env:LAB_CAMPAIGN_SEEDS
$savedPilotExamples = $env:LAB_MAX_EXAMPLES
$savedPilotTime = $env:LAB_MAX_TIME

try {
    $env:LAB_CAMPAIGN_SEEDS = '101'
    $env:LAB_MAX_EXAMPLES = '10'
    $env:LAB_MAX_TIME = '60'

    powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 test raw
    $pilotExitCode = $LASTEXITCODE
    Write-Output "Ma ket thuc pilot: $pilotExitCode"
}
finally {
    $env:LAB_CAMPAIGN_SEEDS = $savedPilotSeeds
    $env:LAB_MAX_EXAMPLES = $savedPilotExamples
    $env:LAB_MAX_TIME = $savedPilotTime
}
```

Sau khi đọc kết quả và xác nhận khôi phục dữ liệu đạt, có thể chạy thử `guided` bằng cùng đoạn lệnh, thay `test raw` bằng `test guided`.

Seed `101` trong đoạn này là số giúp tái lập quá trình sinh yêu cầu. Nó khác với lệnh `seed` ở mục 6.1 dùng để chuẩn bị dữ liệu mẫu.

Giới hạn 60 giây áp dụng cho runner của lượt chạy; tổng thời gian thực tế còn có các bước chuẩn bị, lưu báo cáo và khôi phục. Số example cũng không bằng tổng số yêu cầu được gửi.

### 7.3. Chạy theo ngân sách mặc định

Khi sẵn sàng chạy lâu hơn, dùng:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 test raw
```

Đọc báo cáo và trạng thái khôi phục trước khi chạy tiếp:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 test guided
```

Khi không có biến môi trường ghi đè và giữ cấu hình mẫu, mỗi chế độ dùng ba seed `101,202,303`, tối đa 100 example/operation và giới hạn 1.200 giây mỗi chế độ/seed. Một chế độ có thể dùng khoảng 60 phút ngân sách runner cho ba seed, cộng thời gian chuẩn bị và khôi phục. Không cần chạy toàn bộ phần này chỉ để mở giao diện Directus.

### 7.4. Chạy lại một ca cụ thể — `replay`

Ví dụ chạy lại luồng CRUD của Editor:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 replay editor-crud
```

Hoặc kiểm tra lại việc Reader thử sửa dữ liệu:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 replay reader-write
```

Các ca có tên ổn định này dùng điều kiện và dữ liệu mẫu hiện tại. Với ID do Schemathesis sinh, cần giữ báo cáo nguồn và dữ liệu liên quan; không phải chỉ nhớ ID là luôn chạy lại được. Xem [hướng dẫn replay](replay-cases.md) khi cần điều tra sâu.

## 8. Xem kết quả và hiểu đúng trạng thái

### 8.1. Báo cáo nằm ở đâu?

Mỗi lệnh tạo một thư mục riêng và thông báo đường dẫn khi chạy. Mở File Explorer rồi đi đến:

```text
D:\DAMH-full-recovery-2026-10-12\DAMH\artifacts\runs\
```

Bên trong là các thư mục có mã lần chạy, gọi là **run ID**. Ưu tiên tìm đúng run ID được in ở lần vừa chạy, tránh đọc nhầm báo cáo cũ.

| Tệp hoặc thư mục | Nội dung |
|---|---|
| `run.log` | Diễn biến và thông báo của lệnh |
| `metadata.json` | Thông tin lần chạy, lệnh, cấu hình và mã kết thúc |
| `scenario-report.json` | Kết quả sáu scenario |
| `invariant-report.json` | Kết quả các ca invariant |
| `raw/seed-101/` hoặc `guided/seed-101/` | Báo cáo của chế độ và seed tương ứng khi chạy campaign |
| `campaign-summary.json`, `campaign-index.json`, `metrics.json` | Tổng hợp campaign và số liệu; vị trí cụ thể tùy cấp thư mục của lần chạy |

Không phải mọi loại lệnh đều tạo đủ các tệp trong bảng. Ví dụ `up` không tạo `scenario-report.json`.

JSON là định dạng dữ liệu gồm tên trường và giá trị. Có thể mở bằng VS Code hoặc trình soạn thảo văn bản để đọc. Các từ `passed`, `failed`, `blocked`, `expected`, `actual` lần lượt là đạt, không đạt, bị chặn, mong đợi và thực tế.

### 8.2. Hiểu các kết quả thường gặp

| Kết quả | Ý nghĩa |
|---|---|
| `PASS` hoặc `passed` | Kiểm tra đã chạy và đáp ứng tiêu chí |
| `FAIL` hoặc `failed` | Có kiểm tra không đáp ứng tiêu chí; cần đọc nguyên nhân |
| `BLOCKED` hoặc `blocked` | Chưa đủ điều kiện để thực hiện kiểm tra |
| `INCOMPLETE` | Lần chạy chưa hoàn tất phạm vi dự kiến |
| `max_time` | Đã chạm giới hạn thời gian của lượt runner |
| Restore PASS hoặc mã restore bằng 0 | Bước khôi phục dữ liệu đạt; không có nghĩa mọi kiểm tra API đạt |

Một yêu cầu bị trả 403 có thể là kết quả đúng khi đang kiểm tra Reader không được sửa. Ngược lại, lỗi 500 khi thử đầu vào bất thường là dấu hiệu cần điều tra. Phải đối chiếu mục tiêu ca kiểm thử trước khi kết luận.

Một lần sinh nhiều case hoặc thực thi 10/10 thao tác chưa chứng minh đã kiểm tra mọi đầu vào và mọi dòng mã. Số failure cũng không tự động bằng số lỗi phần mềm đã xác nhận.

### 8.3. Kết quả tham khảo đã có

Theo [bằng chứng dựng lại Windows ngày 13/10/2026](../evidence/windows-recheck-2026-10-13.md): seed, smoke và sáu scenario đạt; invariant có 9 đạt và 2 không đạt. Raw/guided đã chạy thử trên ba seed, thực thi 10/10 thao tác và khôi phục dữ liệu đạt, nhưng vẫn có failure và giới hạn thời gian.

Theo [ghi nhận mở hệ thống ngày 13/10/2026](Huong_dan_chay_Directus_Windows.md), `up` và `doctor` hoàn thành, `/server/ping` trả `pong`, trang `/admin` phản hồi và dữ liệu có ba chuyên mục, 12 bài viết. Đây là bằng chứng tại thời điểm đã ghi, không thay thế kết quả của lần người đọc đang chạy.

## 9. Dừng và mở lại hệ thống

### 9.1. Dừng sau khi sử dụng

Nếu có kiểm thử đang chạy, chờ lệnh hoàn tất và xem trạng thái khôi phục trước khi dừng dịch vụ.

Từ PowerShell tại workspace, chạy:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 down
```

Lệnh `down` dừng bộ dịch vụ và giữ phần lưu trữ dữ liệu của PostgreSQL, gọi là **volume**. Mở lại bằng `up` sẽ dùng lại dữ liệu đã lưu.

### 9.2. Mở lại vào lần sau

Mở Docker Desktop, chọn đúng thư mục rồi chạy:

```powershell
Set-Location 'D:\DAMH-full-recovery-2026-10-12'
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 up
powershell -NoProfile -ExecutionPolicy Bypass -File .\tmp\lab-tools\run-lab.ps1 doctor
```

Sau đó mở <http://127.0.0.1:8055/admin>. Thông thường không cần tạo lại cấu hình hay dữ liệu mẫu.

### 9.3. Phân biệt `down` với `reset`

`reset` xóa dữ liệu lab để làm lại môi trường. Đây không phải lệnh dùng để mở hoặc tắt hệ thống hằng ngày. Hướng dẫn thao tác thông thường chỉ sử dụng `up` và `down`; khi cần làm lại dữ liệu, phải xác định rõ dữ liệu cần giữ trước khi dùng chức năng reset.

## 10. Các lỗi thường gặp và cách kiểm tra

| Hiện tượng | Nguyên nhân cần kiểm tra | Cách xử lý |
|---|---|---|
| Không tìm thấy `run-lab.ps1` | Chọn sai thư mục hoặc thiếu bộ hỗ trợ Windows | Chạy lại `Set-Location`, kiểm tra cấu trúc ở mục 2 |
| Không tìm thấy `C:\Program Files\Git\bin\bash.exe` | Git chưa cài hoặc được cài ở vị trí khác | Kiểm tra Git; nếu dùng vị trí khác, người duy trì cần chỉnh `$bashPath` trong launcher cho đúng |
| Docker không kết nối được Server | Docker Desktop chưa mở hoặc Engine chưa sẵn sàng | Mở Docker Desktop, chờ rồi kiểm tra `docker version` |
| Không có `docker compose` | Chưa có Compose phù hợp trong môi trường đang dùng | Kiểm tra cài đặt Docker Desktop và mở lại terminal |
| Báo thiếu `config/lab.env` | Chưa tạo cấu hình | Thực hiện mục 5.3 |
| Báo cấu hình còn `REPLACE_...` | Chưa thay giá trị mẫu | Điền giá trị riêng rồi lưu tệp |
| Báo quyền cấu hình không riêng tư | ACL cho phép tài khoản/nhóm ngoài phạm vi bộ chạy chấp nhận | Điều chỉnh quyền của riêng `lab.env` theo mục 5.4 |
| Báo thiếu `jq` hoặc lỗi đường dẫn `/items/...` trên Windows | Không dùng bộ hỗ trợ jq đúng của workspace | Dùng launcher và giữ cả `jq` lẫn `jq.exe` trong `tmp/lab-tools` |
| Cổng 8055 đang được sử dụng | Có ứng dụng hoặc môi trường khác dùng cổng đó | Xác định ứng dụng đang giữ cổng; chỉ dừng ứng dụng khi biết rõ nó thuộc việc mình đang làm. Không tự đổi URL vì script kiểm tra các URL lab mặc định |
| `/admin` không mở được | Dịch vụ chưa healthy hoặc đã dừng | Chạy `up`, đọc lỗi và kiểm tra trạng thái dịch vụ bên dưới |
| Đăng nhập Admin thất bại | Sai thông tin hoặc mật khẩu DB đã có khác với tệp vừa chỉnh | Dùng thông tin của lần khởi tạo trước; không coi sửa tệp env là thao tác đổi mật khẩu tài khoản đã tồn tại |
| Đăng nhập Editor/Reader vào Studio bị từ chối | Hai tài khoản lab phục vụ API | Dùng Admin cho Studio |
| Seed/Reader bị chặn bởi license | Tính năng custom permission rules chưa bật | Kiểm tra license phù hợp và `doctor`; giữ trạng thái chưa hoàn tất nếu chưa đáp ứng |
| Export schema báo khác snapshot đã có | Điều kiện schema, quyền hoặc license đã thay đổi | Giữ snapshot cũ; đối chiếu cấu hình/profile trước khi xuất lại theo README |
| Kiểm thử báo dữ liệu mẫu không khớp | Có thay đổi dữ liệu, ID hoặc dùng sai profile | Đối chiếu dữ liệu và profile của lần seed; không xóa dữ liệu để bỏ qua lỗi |
| `test invariants` trả mã 1 | Có ca FAIL hoặc lỗi điều kiện thực thi | Đọc `invariant-report.json` và `run.log`; đối chiếu hai finding đã biết, đồng thời kiểm tra có lỗi mới không |
| Raw/guided có failure hoặc `max_time` | Runner đã ghi nhận vi phạm hoặc chạm budget | Giữ báo cáo và phân tích; không đổi kết quả thành PASS |

Để xem trạng thái Docker của đúng dự án từ workspace:

```powershell
docker compose --env-file .\DAMH\config\lab.env --project-name r06-k05 -f .\DAMH\compose.yaml ps
```

Để đọc các dòng log gần nhất khi cần điều tra khởi động:

```powershell
docker compose --env-file .\DAMH\config\lab.env --project-name r06-k05 -f .\DAMH\compose.yaml logs --tail 80 directus database
```

Nếu cần nhờ người khác hỗ trợ, ghi tên lệnh, thông báo lỗi và run ID. Kiểm tra, che các giá trị riêng trước khi gửi đoạn log; không gửi toàn bộ `lab.env`.

## 11. Chạy trên máy khác hoặc môi trường Bash

### 11.1. Chuyển sang máy Windows khác

Người nhận cần có mã dự án cùng các thay đổi Windows đang được sử dụng, Docker Desktop, Git Bash và bộ hỗ trợ `tmp/lab-tools`. Tạo cấu hình riêng trên máy nhận; cấu hình chứa mật khẩu và license không phải tệp cần công bố cùng mã nguồn.

Launcher tìm thư mục `DAMH` tương đối từ vị trí `tmp/lab-tools`, nên hai thư mục cần giữ quan hệ như mục 2. Đường dẫn Git Bash trong launcher hiện là cố định; nếu cài Git ở nơi khác thì cần điều chỉnh cho đúng.

Docker volume trên máy cũ không tự xuất hiện khi sao chép mã nguồn. Máy mới cần khởi tạo dữ liệu bằng quy trình thiết lập. Các schema runtime, ID map và báo cáo cũ cũng không mặc nhiên có trong bản clone.

Kết quả đạt trên máy cũ không thay thế việc chạy và ghi lại kết quả trên máy mới.

### 11.2. Dùng Bash độc lập, ví dụ trên Linux

Phần này là đường chạy qua `lab.sh`, dành cho môi trường đã có Bash, Docker Engine/Compose, `curl` và `jq`. Các thao tác dưới đây không dùng launcher PowerShell. Nếu chạy bằng Git Bash trên Windows, vẫn cần xử lý các khác biệt Windows đã nêu, không mặc định môi trường đó giống Linux.

Tại thư mục `DAMH`, tạo cấu hình nếu chưa có:

```bash
if [ ! -f config/lab.env ]; then
    cp config/lab.env.example config/lab.env
fi
chmod 600 config/lab.env
```

Điền các giá trị riêng trong `config/lab.env` theo mục 5.3 trước khi chạy tiếp. Sau đó thực hiện từng lệnh, kiểm tra kết quả trước khi sang lệnh kế tiếp:

```bash
docker compose --env-file config/lab.env --project-name r06-k05 -f compose.yaml pull
bash lab.sh up
bash lab.sh doctor
bash lab.sh seed
bash lab.sh smoke
bash lab.sh export-schema
bash lab.sh test scenarios
bash lab.sh test invariants
```

Khi hoàn tất:

```bash
bash lab.sh down
```

Đường chạy Bash được đối chiếu từ giao diện lệnh của dự án. Tài liệu này không ghi nhận một lần dựng mới trên máy Linux khác.

## 12. Bảng tra nhanh lệnh

Bảng ghi phần công việc đặt sau `run-lab.ps1` trên Windows hoặc sau `bash lab.sh` trong môi trường Bash phù hợp.

| Công việc | Ý nghĩa | Khi sử dụng |
|---|---|---|
| `up` | Khởi động môi trường Docker | Mỗi lần cần mở dự án |
| `doctor` | Kiểm tra môi trường và cấu hình | Sau khi mở hoặc khi điều tra lỗi |
| `seed` | Chuẩn bị dữ liệu mẫu và quyền | Lần đầu hoặc khi cần kiểm tra lại điều kiện dữ liệu mẫu |
| `smoke` | Kiểm tra nhanh chức năng cơ bản | Sau khi chuẩn bị dữ liệu |
| `export-schema` | Xuất bản mô tả API theo actor | Sau seed, trước kiểm thử phụ thuộc schema |
| `test scenarios` | Chạy sáu kịch bản nghiệp vụ | Kiểm tra luồng dữ liệu, truy vấn và quyền |
| `test invariants` | Chạy 11 ca quy tắc/phản hồi bổ sung | Kiểm tra sâu hơn và đối chiếu finding |
| `test raw` | Sinh yêu cầu từ schema gốc đã chọn phạm vi | Khi sẵn sàng chạy campaign |
| `test guided` | Sinh yêu cầu có ví dụ, ID và chuỗi liên quan | Sau khi dữ liệu và khôi phục đã được kiểm tra |
| `replay editor-crud` | Chạy lại một ca có tên ổn định | Kiểm tra riêng luồng CRUD |
| `down` | Dừng dịch vụ, giữ dữ liệu | Sau khi sử dụng |

## 13. Tài liệu đối chiếu

1. [README — Cấu hình, giao diện lệnh và cách tái lập](../README.md).
2. [Hướng dẫn mở Directus trên Windows hiện tại](Huong_dan_chay_Directus_Windows.md).
3. [Bằng chứng dựng lại Windows ngày 13/10/2026](../evidence/windows-recheck-2026-10-13.md).
4. [Cấu hình mẫu của dự án](../config/lab.env.example).
5. [Mô tả dịch vụ Docker](../compose.yaml).
6. [Chương trình điều phối lab](../lab.sh).
7. [Launcher PowerShell của workspace hiện tại](../../tmp/lab-tools/run-lab.ps1).
8. [Báo cáo thiết kế kịch bản kiểm thử](Bao_cao_Thiet_ke_kich_ban_kiem_thu.md).
