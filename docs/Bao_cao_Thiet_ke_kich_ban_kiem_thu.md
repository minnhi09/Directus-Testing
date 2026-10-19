# BÁO CÁO THIẾT KẾ KỊCH BẢN KIỂM THỬ

**Test Model / Test Scenarios / Test Cases**

**Dự án:** R06 Directus + K05 Kiểm thử API dựa trên schema bằng Schemathesis  
**Ngày biên soạn:** 16/10/2026  
**Đối tượng đọc:** Người mới tìm hiểu dự án và kiểm thử phần mềm.

> Báo cáo được viết dựa trên tài liệu, mã nguồn và báo cáo kiểm thử đã có trong dự án. Các kết quả thực tế được dẫn từ lần kiểm thử trên Windows ngày 13/10/2026 theo giờ Việt Nam/Thái Lan. Việc biên soạn tài liệu này không bao gồm chạy lại hệ thống hoặc kiểm thử mới.

## 1. Giới thiệu dự án

### 1.1. Hệ thống được kiểm thử là gì?

Directus là phần mềm giúp quản lý và truy cập dữ liệu. Trong dự án này, có thể hình dung hệ thống giống một kho quản lý bài viết: mỗi bài có tiêu đề, trạng thái, điểm đánh giá và chuyên mục. Một số người được phép chỉnh sửa bài; những người khác chỉ được đọc nội dung đã công bố.

Các chương trình giao tiếp với Directus qua **API**. Hiểu đơn giản, API là nơi nhận yêu cầu như “lấy danh sách bài viết”, “tạo bài mới” hoặc “sửa điểm của bài viết”, rồi trả về kết quả. Dự án kiểm tra các yêu cầu và kết quả này, thay vì thao tác bằng chuột trên giao diện trang web.

Hai nhóm dữ liệu được dùng trong thử nghiệm là:

| Tên trong chương trình | Cách hiểu thông thường | Ví dụ minh họa |
|---|---|---|
| `qa_categories` | Danh sách chuyên mục | Một chuyên mục để phân loại bài viết |
| `qa_articles` | Danh sách bài viết | Một bài có tiêu đề, trạng thái và chuyên mục |

Tiền tố `qa_` giúp nhận biết đây là dữ liệu dành cho kiểm thử.

### 1.2. Dự án muốn kiểm tra điều gì?

Dự án tập trung trả lời các câu hỏi:

- Người có quyền biên tập có tạo, đọc, sửa và xóa dữ liệu đúng không?
- Khi lọc, sắp xếp hoặc chia danh sách thành từng trang, kết quả có đúng không?
- Người chỉ có quyền đọc có xem được bài nháp, ghi chú nội bộ hoặc sửa bài không?
- Hệ thống có từ chối dữ liệu không hợp lệ và giữ nguyên dữ liệu khi từ chối không?
- Phản hồi thực tế có đúng với bản mô tả API không?
- Khi nhận yêu cầu bất thường, hệ thống có xử lý được mà không phát sinh lỗi máy chủ không?

## 2. Phân biệt Test Model, Test Scenarios và Test Cases

Ba khái niệm này là ba thành phần liên quan trong thiết kế kiểm thử. Chúng giúp đi từ việc hiểu hệ thống đến việc thực hiện kiểm tra cụ thể.

| Thành phần | Giải thích dễ hiểu | Câu hỏi cần trả lời | Ví dụ trong dự án |
|---|---|---|---|
| **Test Model — Mô hình kiểm thử** | Bản mô tả phần hệ thống cần kiểm tra, dữ liệu và quy tắc của nó | Kiểm tra hệ thống nào, ai sử dụng và được phép làm gì? | Reader chỉ đọc bài đã công bố, không được sửa bài |
| **Test Scenario — Kịch bản kiểm thử** | Một tình huống hoặc luồng sử dụng cần kiểm tra | Cần kiểm tra tình huống nào? | Reader thử sửa một bài viết |
| **Test Case — Ca kiểm thử** | Hướng dẫn kiểm tra cụ thể, gồm điều kiện, dữ liệu, bước thực hiện và kết quả mong đợi | Kiểm tra bằng cách nào và dựa vào đâu để biết đúng hay sai? | Reader gửi yêu cầu sửa điểm; hệ thống phải từ chối; Editor đọc lại để xác nhận điểm không đổi |

Mối liên hệ có thể diễn đạt như sau:

```text
Mô hình: Reader chỉ có quyền đọc
    ↓
Kịch bản: Reader thử sửa bài viết
    ↓
Ca kiểm thử: Đọc dữ liệu trước → Reader gửi yêu cầu sửa
            → Kiểm tra bị từ chối → Đọc lại và so sánh dữ liệu
```

Một kịch bản có thể cần nhiều yêu cầu API và nhiều điểm kiểm tra. Vì vậy, số kịch bản không bằng số yêu cầu gửi đi, cũng không bằng số ca do công cụ tự sinh.

## 3. Mô hình kiểm thử của dự án — Test Model

### 3.1. Thành phần và phạm vi hệ thống

Môi trường thử nghiệm gồm Directus 12.5.0, cơ sở dữ liệu PostgreSQL 16 và công cụ Schemathesis 4.30.0. Các thành phần được chạy trong môi trường Docker của dự án, với tên `r06-k05`.

- **Directus:** tiếp nhận yêu cầu và xử lý dữ liệu, quyền truy cập.
- **PostgreSQL:** lưu chuyên mục và bài viết.
- **Bộ script kiểm thử:** chuẩn bị dữ liệu, gửi yêu cầu và so sánh kết quả.
- **Schemathesis:** đọc bản mô tả API để tự sinh nhiều yêu cầu kiểm thử.

Phạm vi chính gồm năm thao tác trên mỗi nhóm dữ liệu:

| Thao tác | Phương thức API | Chuyên mục | Bài viết |
|---|---|---|---|
| Xem danh sách | `GET` | `/items/qa_categories` | `/items/qa_articles` |
| Tạo mới | `POST` | `/items/qa_categories` | `/items/qa_articles` |
| Xem một bản ghi | `GET` | `/items/qa_categories/{id}` | `/items/qa_articles/{id}` |
| Sửa một phần thông tin | `PATCH` | `/items/qa_categories/{id}` | `/items/qa_articles/{id}` |
| Xóa một bản ghi | `DELETE` | `/items/qa_categories/{id}` | `/items/qa_articles/{id}` |

`{id}` là mã của bản ghi cần thao tác. Mã này được lấy từ dữ liệu mẫu hoặc phản hồi khi tạo mới, không mặc định luôn là một con số cố định.

Như vậy, chiến dịch kiểm thử chính có **10 cặp phương thức–đường dẫn**. Kiểm thử giao diện, hiệu năng, GraphQL, WebSocket và sửa/xóa hàng loạt nằm ngoài phạm vi chính. Ngoài 10 thao tác này, ca kiểm tra token giả dùng `/users/me` để kiểm tra nhận diện người dùng.

### 3.2. Mô hình dữ liệu

Dữ liệu ban đầu, còn gọi là **fixture**, là bộ dữ liệu mẫu đã chuẩn bị trước để làm căn cứ kiểm tra. Dự án có ba chuyên mục và 12 bài viết, gồm sáu bài nháp và sáu bài đã công bố, phân bố đều theo chuyên mục.

| Thông tin | Tên trường | Quy tắc chính |
|---|---|---|
| Mã bài viết | `id` | Hệ thống tự sinh |
| Tiêu đề | `title` | Bắt buộc, tối đa 120 ký tự |
| Trạng thái | `status` | Chỉ nhận `draft` — bài nháp, hoặc `published` — đã công bố |
| Điểm đánh giá | `score` | Số nguyên từ 0 đến 5 |
| Thời điểm công bố | `published_at` | Có thể chưa có giá trị |
| Thông tin bổ sung | `metadata` | Dữ liệu JSON, có thể chưa có giá trị |
| Ghi chú nội bộ | `internal_notes` | Reader không được xem |
| Chuyên mục | `category` | Liên kết tới chuyên mục, có thể để trống |

JSON là cách biểu diễn dữ liệu bằng tên trường và giá trị. Ví dụ `{"score": 5}` có nghĩa là trường điểm có giá trị bằng 5. Giá trị `null` có nghĩa là chưa có giá trị, khác với số 0 hoặc một chuỗi rỗng.

Một chuyên mục có thể chứa nhiều bài viết. Khi xóa chuyên mục, bài viết liên quan phải được giữ lại và trường `category` chuyển thành `null`. Đây là một quy tắc quan trọng cần kiểm tra.

### 3.3. Mô hình người dùng và quyền truy cập

Trong tài liệu kỹ thuật, người hoặc vai trò thực hiện yêu cầu được gọi là **actor**.

| Actor | Cách hiểu | Quyền đối với dữ liệu thử nghiệm |
|---|---|---|
| Admin | Người quản trị môi trường | Chuẩn bị hệ thống, dữ liệu, tài khoản và kiểm tra trạng thái |
| Editor | Người biên tập | Tạo, đọc, sửa và xóa chuyên mục, bài viết |
| Reader | Người đọc | Đọc chuyên mục và bài đã công bố; không xem ghi chú nội bộ; không được ghi dữ liệu |
| Anonymous | Người chưa đăng nhập | Không được truy cập hai nhóm dữ liệu thử nghiệm |

Tài khoản Editor được dùng cho chiến dịch tự sinh yêu cầu. Admin chủ yếu phục vụ chuẩn bị và đối chiếu dữ liệu, không phải tài khoản mặc định để sinh yêu cầu kiểm thử.

### 3.4. Bản mô tả API và căn cứ đánh giá

**OpenAPI schema** là bản mô tả mà chương trình có thể đọc được: API có những đường dẫn nào, nhận tham số gì, dữ liệu đầu vào và phản hồi dự kiến ra sao. Có thể xem nó như tờ hướng dẫn sử dụng API.

Dự án xuất schema sau khi chuẩn bị dữ liệu và lưu riêng theo actor. Schemathesis sử dụng schema để sinh yêu cầu và đối chiếu phản hồi. Tuy nhiên, bản mô tả API có thể chưa thể hiện đầy đủ các quy tắc như “Reader không thấy bài nháp” hoặc “yêu cầu sửa bị từ chối không được làm thay đổi điểm”. Vì vậy, dự án bổ sung các kiểm tra nghiệp vụ viết sẵn.

Căn cứ xác định đúng/sai, còn gọi là **test oracle**, gồm:

- Bản mô tả API: đối chiếu mã phản hồi, kiểu nội dung và cấu trúc dữ liệu.
- Bộ dữ liệu mẫu: xác định bài nào phải xuất hiện khi lọc hoặc tìm kiếm.
- Ma trận quyền: xác định actor nào được phép thực hiện thao tác.
- So sánh trước/sau: xác định dữ liệu đã được sửa đúng hoặc có được giữ nguyên không.

Mô hình trong báo cáo là mô tả dữ liệu, quyền, thao tác và quy tắc. Báo cáo không coi đây là một mô hình trạng thái hình thức đầy đủ của phương pháp Model-Based Testing.

## 4. Nguyên tắc thiết kế kịch bản và ca kiểm thử

### 4.1. Kiểm tra cả thao tác được phép và thao tác bị cấm

**Ca hợp lệ** kiểm tra hệ thống có thực hiện được yêu cầu đúng hay không, ví dụ Editor tạo bài có điểm hợp lệ. **Ca không hợp lệ** kiểm tra hệ thống có từ chối yêu cầu sai hay không, ví dụ Reader sửa bài hoặc gửi điểm ngoài khoảng cho phép.

Đối với ca không hợp lệ, việc hệ thống từ chối là hành vi mong đợi. Do đó, một phản hồi báo từ chối không tự động có nghĩa là ca kiểm thử thất bại.

### 4.2. Kiểm tra dữ liệu sau thao tác

Không chỉ xem thông báo “thành công” hoặc “bị từ chối”, bộ kiểm thử còn đọc lại dữ liệu:

- Tạo bài xong phải đọc lại được bài vừa tạo.
- Sửa điểm phải thấy điểm mới và giữ nguyên tiêu đề không được yêu cầu sửa.
- Xóa bài xong không được tiếp tục đọc thấy dữ liệu bài đó.
- Reader bị từ chối sửa thì dữ liệu trước và sau phải giống nhau ở các trường được đối chiếu.

Những quy tắc cần luôn được giữ đúng được gọi là **invariant**, hiểu đơn giản là “điều luôn phải đúng”. Bộ kiểm thử đặt tên suite là invariant, nhưng suite này còn chứa cả các phép kiểm tra phản hồi API và khả năng xử lý yêu cầu bất thường.

### 4.3. Giữ điều kiện thử nghiệm có thể kiểm soát

Các ca lấy ID thực tế từ dữ liệu mẫu hoặc phản hồi tạo mới. Dữ liệu tạm được dọn sau khi thử nghiệm. Các bộ kiểm thử có ghi/xóa dữ liệu chạy tuần tự khi dùng chung cơ sở dữ liệu.

Các ca quyền Reader liên quan kiểm tra schema trước khi gửi yêu cầu. Nếu thiếu schema hoặc thao tác cần thiết không có trong schema theo quy tắc của bộ kiểm thử, ca được ghi là **BLOCKED — chưa thể thực hiện**, thay vì tự coi là đã kiểm tra quyền thành công.

## 5. Thiết kế sáu kịch bản nghiệp vụ — Test Scenarios

### 5.1. Danh sách kịch bản

| Mã | Kịch bản | Actor | Rủi ro cần phát hiện | Kết quả mong đợi |
|---|---|---|---|---|
| S1 | Tạo, đọc, sửa và xóa bài viết | Editor | Ghi sai dữ liệu, làm mất trường khác hoặc xóa không thành công | Toàn bộ luồng đúng; sửa điểm giữ nguyên tiêu đề; xóa xong không còn dữ liệu bài |
| S2 | Lọc bài theo trạng thái | Editor | Kết quả lọc thiếu bài hoặc lẫn bài nháp | Nhận đúng sáu bài đã công bố trong dữ liệu mẫu |
| S3 | Sắp xếp và chia trang | Editor | Sai thứ tự hoặc lấy sai phần dữ liệu của từng trang | Hai trang đầu khớp các phần tương ứng của danh sách đã sắp xếp |
| S4 | Reader truy cập bài nháp | Reader | Nội dung chưa công bố bị lộ | Không nhận được dữ liệu bài nháp |
| S5 | Reader yêu cầu trường ghi chú nội bộ | Reader | Thông tin riêng bị lộ | Yêu cầu bị từ chối hoặc phản hồi loại bỏ trường ghi chú nội bộ |
| S6 | Reader thử sửa bài viết | Reader, Editor đối chiếu | Người chỉ có quyền đọc thay đổi được dữ liệu | Yêu cầu sửa bị từ chối; dữ liệu đối chiếu không thay đổi |

### 5.2. Vì sao chọn các kịch bản này?

S1 kiểm tra luồng quản lý dữ liệu cơ bản. S2 và S3 kiểm tra khả năng lấy đúng dữ liệu khi danh sách được lọc hoặc chia trang. S4, S5 và S6 kiểm tra quyền ở ba góc độ khác nhau: được xem bản ghi nào, được xem trường thông tin nào và có được thay đổi dữ liệu hay không.

Sáu kịch bản này thể hiện các tình huống nghiệp vụ chính, nhưng không đại diện cho mọi chức năng hoặc mọi tổ hợp đầu vào của Directus.

## 6. Thiết kế ca kiểm thử cụ thể — Test Cases

### 6.1. Thông tin cần có trong một ca kiểm thử

| Nội dung | Ý nghĩa |
|---|---|
| Mã và tên | Nhận diện ca để tra cứu, chạy lại |
| Mục tiêu | Nêu điều muốn xác minh |
| Tiền điều kiện | Những điều phải sẵn sàng trước khi chạy |
| Actor và đầu vào | Ai thực hiện, gửi dữ liệu gì |
| Các bước | Thứ tự yêu cầu và thao tác đối chiếu |
| Kết quả mong đợi | Tiêu chí xác định ca đạt |
| Kết quả thực tế | Điều hệ thống thực sự trả về hoặc làm thay đổi |
| Trạng thái và bằng chứng | Đạt, không đạt hoặc chưa chạy được; kèm báo cáo của lần chạy |

Các mục dưới đây diễn giải sáu scenario hiện có thành mô tả ca cụ thể để người mới có thể theo dõi. Chúng giữ mã S1–S6 của dự án, không tạo thêm sáu ca tự động độc lập.

### 6.2. Ca S1 — Editor quản lý vòng đời một bài viết

**Mục tiêu:** Kiểm tra tạo, đọc, sửa, xóa và bảo toàn thông tin không được yêu cầu sửa.

**Tiền điều kiện:** Editor đăng nhập được; có chuyên mục mẫu; hệ thống truy cập được.

**Đầu vào:** Bài mới có tiêu đề riêng cho lần chạy, trạng thái `draft`, điểm `1`, chuyên mục lấy từ dữ liệu mẫu. Bài có thêm thông tin phục vụ kiểm thử như ghi chú nội bộ.

**Các bước và kết quả mong đợi:**

| Bước | Thực hiện | Kết quả mong đợi |
|---|---|---|
| 1 | Editor tạo bài bằng `POST` | Thành công và trả về ID hợp lệ |
| 2 | Đọc lại bài bằng ID vừa nhận | Tiêu đề khớp tiêu đề đã gửi |
| 3 | Gửi `PATCH` với `{"score": 5}` | Cập nhật thành công |
| 4 | Đọc lại bài | Điểm bằng 5, tiêu đề giữ nguyên |
| 5 | Xóa bài bằng `DELETE` | Xóa thành công |
| 6 | Yêu cầu đọc lại bài đã xóa | Không còn nhận được dữ liệu bài |

**Sau kiểm thử:** Bài tạm được xóa; các nhánh xử lý thất bại có cơ chế dọn dữ liệu khi phù hợp. Kết quả thao tác và thông tin dọn dữ liệu cần được kiểm tra khi điều tra ca thất bại.

### 6.3. Ca S2 — Editor lọc bài đã công bố

**Mục tiêu:** Kiểm tra bộ lọc trả đúng bản ghi.

**Tiền điều kiện:** Dữ liệu mẫu có sáu bài `published` và sáu bài `draft`; biết ID tương ứng từ bản ánh xạ dữ liệu mẫu.

**Đầu vào:** Bộ lọc `status=published`, lấy các trường `id`, `title`, `status`.

**Các bước:** Editor gửi yêu cầu lấy danh sách đã lọc; lấy tập ID trong phản hồi; đối chiếu với tập ID của sáu bài đã công bố trong dữ liệu mẫu; kiểm tra trạng thái từng bài.

**Kết quả mong đợi:** Hai tập ID giống nhau và tất cả bài trả về đều có trạng thái `published`. Chỉ kiểm tra “có sáu bài” là chưa đủ, vì sáu bài đó vẫn có thể là sai bản ghi.

### 6.4. Ca S3 — Editor sắp xếp và lấy từng trang

**Mục tiêu:** Kiểm tra danh sách chia trang giữ đúng thứ tự.

**Tiền điều kiện:** Có đủ dữ liệu bài mẫu; Editor đọc được danh sách.

**Đầu vào:** Sắp xếp theo `title,id`; mỗi trang ba bài. `id` dùng để phân định thứ tự khi tiêu đề trùng nhau.

**Các bước:**

1. Lấy danh sách đã sắp xếp đầy đủ.
2. Lấy ba bài đầu bằng `limit=3`, `offset=0`.
3. Lấy ba bài tiếp theo bằng `limit=3`, `offset=3`.
4. So sánh từng trang với phần tương ứng trong danh sách đầy đủ.

`limit` là số bản ghi tối đa cần lấy; `offset` là số bản ghi bỏ qua từ đầu danh sách.

**Kết quả mong đợi:** Trang đầu khớp ba bài đầu; trang tiếp theo khớp ba bài tiếp theo. Kiểm tra bổ sung về tham số `page=2` và đối chiếu với dữ liệu mẫu nằm trong ca `query-fixture` ở mục 7.

### 6.5. Ca S4 — Reader không đọc được bài nháp

**Mục tiêu:** Kiểm tra việc ngăn lộ nội dung chưa công bố.

**Tiền điều kiện:** Có bài nháp mẫu; Reader đăng nhập được; schema Reader có thao tác đọc chi tiết theo điều kiện của bộ kiểm thử.

**Đầu vào:** ID của bài nháp lấy từ dữ liệu mẫu. Yêu cầu hiện có chọn các trường `id,title,status,internal_notes`.

**Các bước:** Reader gửi yêu cầu đọc chi tiết bài nháp; kiểm tra phản hồi có trả dữ liệu bài hay không.

**Kết quả mong đợi:** Yêu cầu bị từ chối hoặc không trả dữ liệu bài nháp. Nếu không đáp ứng điều kiện schema, ca ghi BLOCKED.

**Giới hạn cần hiểu:** Yêu cầu hiện tại đồng thời chứa trường ghi chú bị cấm. Vì vậy, phản hồi từ chối của riêng S4 chưa tách biệt hoàn toàn nguyên nhân “bài nháp” và “trường bị cấm”. Ca `reader-visibility` bổ sung việc đối chiếu danh sách bài được phép đọc; đề xuất tách riêng yêu cầu đọc bài nháp chỉ với trường công khai được nêu ở mục 11.

### 6.6. Ca S5 — Reader không xem được ghi chú nội bộ

**Mục tiêu:** Kiểm tra quyền ở mức trường thông tin.

**Tiền điều kiện:** Có bài đã công bố; Reader có thể đọc bài này qua các trường công khai; schema phù hợp.

**Đầu vào:** ID bài đã công bố và yêu cầu chọn thêm `internal_notes`.

**Các bước:** Reader đọc bài bằng các trường công khai để xác minh quyền đọc bình thường; sau đó yêu cầu đọc cùng bài nhưng thêm trường ghi chú nội bộ; kiểm tra phản hồi.

**Kết quả mong đợi:** Lần đọc công khai thành công. Lần yêu cầu trường kín bị từ chối hoặc không chứa trường `internal_notes`. Không bắt buộc mọi cấu hình đều trả cùng một mã từ chối.

### 6.7. Ca S6 — Reader sửa bài bị từ chối và dữ liệu giữ nguyên

**Mục tiêu:** Kiểm tra yêu cầu không có quyền không gây thay đổi dữ liệu.

**Tiền điều kiện:** Có bài đã công bố; Editor và Reader đăng nhập được; schema Reader có thao tác cần thiết theo điều kiện của bộ kiểm thử.

**Đầu vào:** Điểm mới vẫn trong khoảng 0–5 nhưng khác điểm hiện tại. Cách chọn này giúp kiểm tra quyền sửa, tránh dùng một điểm sai khiến yêu cầu bị từ chối vì lý do kiểm tra dữ liệu.

**Các bước và kết quả mong đợi:**

| Bước | Thực hiện | Kết quả mong đợi |
|---|---|---|
| 1 | Editor đọc `id,title,status,score` của bài | Đọc thành công; lưu dữ liệu trước thao tác |
| 2 | Reader gửi `PATCH` thay đổi điểm | Yêu cầu bị từ chối |
| 3 | Editor đọc lại cùng các trường | Đọc thành công |
| 4 | So sánh dữ liệu trước và sau | Các trường được đối chiếu giống nhau |

Nếu chỉ thấy thông báo từ chối mà chưa đọc lại dữ liệu thì chưa đủ chứng minh mục tiêu của ca này.

## 7. Bộ 11 ca kiểm tra quy tắc và phản hồi API

Bên cạnh sáu scenario, dự án có 11 ca trong `scripts/invariants.py`. Hai bộ có phần mục tiêu trùng nhau nhưng được thực thi và báo cáo riêng; không cộng thành 17 tình huống nghiệp vụ hoàn toàn khác nhau.

Tiền điều kiện chung là môi trường truy cập được, dữ liệu mẫu đã chuẩn bị và thông tin đăng nhập phù hợp đã có. Các ca phụ thuộc schema cần schema đã xuất.

| Mã trong chương trình | Actor, đầu vào và bước chính | Kết quả mong đợi |
|---|---|---|
| `auth-invalid-token` | Gửi yêu cầu `/users/me` với token giả. Token là thông tin dùng để xác thực người gửi | Yêu cầu bị từ chối; phải có phản hồi HTTP để phân biệt với mất kết nối |
| `anonymous-denied` | Không đăng nhập; yêu cầu đọc lần lượt chuyên mục và bài viết | Cả hai yêu cầu đều bị từ chối |
| `editor-crud` | Editor tạo bài điểm 1, đọc lại, sửa điểm thành 5, đọc lại, xóa rồi đọc kiểm tra | Tạo/đọc/sửa/xóa đúng; tiêu đề không đổi khi chỉ sửa điểm; xóa xong không còn dữ liệu bài |
| `positive-operations` | Editor tạo chuyên mục và bài tạm; thực hiện đủ năm thao tác cho mỗi nhóm dữ liệu; đọc đối chiếu sau khi ghi | Cả 10 thao tác có trường hợp thành công hợp lệ; dữ liệu đọc lại đúng; dọn dữ liệu tạm |
| `query-fixture` | Editor lọc bài đã công bố, sắp xếp `title,id`, chia trang bằng `offset` và `page`, tìm từ `spéciale`, chọn các trường cần đọc | Tập ID, thứ tự và kết quả tìm kiếm khớp dữ liệu mẫu; `page=2,limit=3` tương đương `offset=3,limit=3`; chỉ có trường được yêu cầu |
| `aggregate-query-robustness` | Editor gửi yêu cầu thống kê với `{"foo":1}`, rồi đối chiếu hai yêu cầu `aggregate={}` và `{"count":["id"]}` | Đầu vào lạ không làm máy chủ trả 5xx; hai yêu cầu đối chiếu hợp lệ thành công |
| `contract-schema-candidates` | Editor tạo dữ liệu tạm, kiểm tra dạng phản hồi POST, xuất CSV và mã phản hồi khi DELETE; so sánh với schema | Ghi nhận đúng mọi chênh lệch giữa thực tế và bản mô tả; giữ trạng thái không đạt khi phát hiện chênh lệch; dọn dữ liệu tạm |
| `relation-nullification` | Editor tạo chuyên mục và bài liên quan; xóa chuyên mục; đọc lại bài | Bài vẫn tồn tại, `category=null` |
| `invalid-field-rejection` | Editor tạo bài với `status="archived"` và `score=-1`; Admin tìm lại theo tiêu đề riêng của ca | Yêu cầu bị từ chối; không tồn tại bài được tạo từ yêu cầu sai |
| `reader-visibility` | Reader đọc danh sách published bằng trường công khai; so với sáu ID mẫu; thử yêu cầu thêm `internal_notes` | Danh sách khớp các bài được phép đọc; trường kín không bị lộ; yêu cầu trường kín bị từ chối hoặc trường bị loại bỏ |
| `reader-write` | Editor đọc trước; Reader thử sửa điểm hợp lệ; Editor đọc sau | Reader bị từ chối; dữ liệu đối chiếu không đổi |

`aggregate` là yêu cầu thống kê dữ liệu, chẳng hạn đếm số bài. `foo` trong ca trên là tên lạ được dùng để kiểm tra cách hệ thống xử lý đầu vào bất thường.

Ca `invalid-field-rejection` hiện gửi cả trạng thái sai và điểm sai trong cùng yêu cầu. Ca này chứng minh tổ hợp đầu vào đó bị từ chối; chưa chứng minh riêng từng ràng buộc đã được kiểm tra độc lập.

## 8. Các ca do Schemathesis tự sinh

### 8.1. Vì sao cần tự sinh thêm ca?

Các ca viết sẵn giúp kiểm tra những tình huống đã biết. Tuy nhiên, một tham số có thể nhận nhiều kiểu dữ liệu, giá trị biên hoặc tổ hợp bất thường mà người viết chưa nghĩ tới. Schemathesis đọc OpenAPI để tạo nhiều yêu cầu nhằm mở rộng phạm vi kiểm tra.

Dự án có hai cách chạy:

| Cách chạy | Dữ liệu dùng để sinh yêu cầu | Mục đích |
|---|---|---|
| `raw` | Schema Editor được chọn đúng 10 thao tác; giữ nguyên mô tả của các thao tác đó | Kiểm tra dựa trên bản mô tả API gốc trong phạm vi đã chọn |
| `guided` | Bản sao riêng có bổ sung ví dụ hợp lệ và ID dữ liệu mẫu; bật kiểm tra chuỗi thao tác | Giúp công cụ đi sâu vào các yêu cầu dùng dữ liệu đang tồn tại và quan hệ giữa thao tác |

Kiểm tra theo chuỗi, còn gọi là **stateful testing**, có thể dùng kết quả của bước trước làm đầu vào bước sau. Ví dụ: tạo bài → lấy ID được trả về → dùng ID để đọc hoặc sửa bài.

Schema gốc và bản có bổ sung hướng dẫn được lưu tách biệt. Kết quả hai cách chạy cũng được lưu riêng.

### 8.2. Những điểm được kiểm tra tự động

- Yêu cầu không làm API trả lỗi máy chủ 5xx.
- Mã phản hồi nằm trong bản mô tả API.
- Kiểu nội dung trả về đúng mô tả, chẳng hạn JSON.
- Cấu trúc dữ liệu trả về đúng schema.
- Yêu cầu với phương thức không được hỗ trợ được xử lý phù hợp.
- Đầu vào được sinh ở nhóm hợp lệ hoặc không hợp lệ được chấp nhận/từ chối theo các kiểm tra tương ứng của công cụ.

Nhóm mã **2xx** thường biểu thị thành công; **4xx** thường liên quan yêu cầu hoặc quyền truy cập; **5xx** biểu thị lỗi phía máy chủ. Cần đọc mục tiêu từng ca: 403 có thể là đúng khi Reader thử sửa bài, nhưng là vấn đề nếu một yêu cầu được phép đáng lẽ phải thành công.

### 8.3. Cách truy vết một ca tự sinh

Một ca cần gắn được với thao tác API, actor, dữ liệu yêu cầu, phản hồi, kiểm tra bị vi phạm, phiên bản schema và mã lần chạy. Dự án lưu báo cáo cùng các thông tin cấu hình để hỗ trợ điều tra và chạy lại.

Các giá trị `101`, `202`, `303` là **seed sinh dữ liệu**: chúng giúp tái lập quá trình tạo yêu cầu. Seed này khác với bước `seed` của dự án dùng để chuẩn bị dữ liệu mẫu trong cơ sở dữ liệu.

Chạy lại một ca được gọi là **replay**. Nếu ca phụ thuộc nhiều bước, cần tái tạo cả dữ liệu và chuỗi thao tác liên quan. Chỉ gửi lại yêu cầu cuối chưa đủ chứng minh đã tái hiện toàn bộ chuỗi.

## 9. Tiêu chí đánh giá và cách lưu bằng chứng

| Trạng thái | Ý nghĩa | Ví dụ |
|---|---|---|
| PASS — Đạt | Các kiểm tra cần thiết đã chạy và phù hợp mong đợi | Reader bị từ chối sửa; dữ liệu đối chiếu không đổi |
| FAIL — Không đạt | Có kiểm tra không đáp ứng mong đợi | Yêu cầu thống kê bất thường trả 500 |
| BLOCKED — Chưa thể thực hiện | Thiếu điều kiện cần để kiểm tra | Chưa có schema cần thiết hoặc thao tác không có trong schema theo quy tắc bộ kiểm thử |
| INCOMPLETE — Chưa hoàn tất | Lần chạy chưa hoàn tất phạm vi dự kiến | Lần chạy bị ngắt; không có đủ căn cứ kết luận toàn bộ phạm vi |

Với campaign, báo cáo còn ghi lý do kết thúc như hết giới hạn thời gian `max_time`. Một lần chạy có thể đã sinh nhiều ca nhưng vẫn có kiểm tra thất bại hoặc chưa hoàn tất toàn bộ phạm vi mong muốn.

Mỗi lần chạy có thư mục riêng dưới `artifacts/runs/<run_id>/`. Bằng chứng cần giữ gồm báo cáo scenario hoặc invariant, báo cáo Schemathesis, cấu hình, schema, seed sinh dữ liệu, log và trạng thái khôi phục dữ liệu. Mật khẩu, token và license không được đưa vào báo cáo chia sẻ.

Đối với campaign, **restore PASS** có nghĩa là bước khôi phục dữ liệu mẫu đạt yêu cầu. Kết quả đó không biến các kiểm tra API thất bại thành PASS.

Một ca FAIL là dấu hiệu cần điều tra. Nguyên nhân có thể nằm ở phần mềm, bản mô tả API, bộ kiểm thử, dữ liệu hoặc môi trường. Nhiều kiểm tra thất bại có thể cùng xuất phát từ một nguyên nhân; không lấy tổng số failure làm số lỗi phần mềm đã xác nhận.

## 10. Đối chiếu thiết kế với kết quả đã có

### 10.1. Nguồn kết quả

Phần này sử dụng bằng chứng của lần dựng lại trên Windows ngày **13/10/2026**, được ghi tại [Báo cáo xác minh Windows](../evidence/windows-recheck-2026-10-13.md), đồng thời đối chiếu trực tiếp hai file báo cáo scenario và invariant còn trong workspace.

Mã lần chạy dùng giờ UTC, nên tiền tố ngày `20261012` trong run ID vẫn có thể tương ứng ngày 13/10 theo múi giờ Asia/Bangkok.

### 10.2. Kết quả sáu scenario

Nguồn: [scenario-report.json](../artifacts/runs/20261012T185849Z-1525/scenario-report.json).

| Scenario | Kết quả đã ghi nhận |
|---|---|
| S1 — Editor CRUD | PASS; tạo/đọc/sửa đạt, DELETE trả 204 |
| S2 — Lọc published | PASS; tập ID khớp sáu bài mẫu đã công bố |
| S3 — Sắp xếp/phân trang | PASS; hai trang khớp phần danh sách tương ứng |
| S4 — Reader đọc draft | PASS theo tiêu chí hiện có; phản hồi 403, không trả dữ liệu bài nháp |
| S5 — Reader đọc trường kín | PASS; yêu cầu trường kín trả 403 |
| S6 — Reader thử ghi | PASS; PATCH trả 403, dữ liệu đối chiếu giữ nguyên |

Tổng hợp của lần chạy là **6 PASS, 0 FAIL, 0 BLOCKED**. Kết quả này áp dụng cho những kiểm tra đã thực hiện, trong điều kiện của lần chạy đó.

### 10.3. Kết quả bộ invariant

Nguồn: [invariant-report.json](../artifacts/runs/20261012T185934Z-1453/invariant-report.json).

Kết quả tổng hợp là **9 PASS, 2 FAIL, 0 BLOCKED**. Hai ca không đạt là:

| Ca | Thực tế đã ghi nhận | Cách hiểu |
|---|---|---|
| `aggregate-query-robustness` | `{"foo":1}` trả 500; hai yêu cầu đối chiếu trả 200 | Dấu hiệu cần điều tra về xử lý đầu vào bất thường; chưa kết luận là lỗi sản phẩm đã xác nhận |
| `contract-schema-candidates` | Ghi nhận bốn chênh lệch liên quan dạng dữ liệu POST của hai collection, kiểu nội dung CSV và mã DELETE 204 | Chênh lệch giữa phản hồi thực tế với bản mô tả API; không tự coi là bốn lỗi sản phẩm |

Các ca còn lại trong bộ 11 ca đạt ở lần chạy được dẫn. Ví dụ: token giả trả 401; đầu vào `status="archived", score=-1` bị từ chối với 400 và không để lại bản ghi; Reader sửa bị từ chối với 403 và dữ liệu không đổi.

### 10.4. Kết quả các lần chạy tự sinh yêu cầu

Theo bằng chứng Windows, `raw` và `guided` đã chạy thử với ba seed `101`, `202`, `303`; mỗi seed thực thi 10/10 thao tác và khôi phục dữ liệu đạt. Các lần chạy vẫn ghi nhận failure và kết thúc với giới hạn thời gian, không phải toàn bộ PASS.

Ngân sách chạy thử là tối đa 10 example/operation và 60 giây/seed. Ngân sách campaign chính là 100 example/operation và 1.200 giây/profile/seed; ngân sách chính này chưa được chạy lại đầy đủ trong phiên Windows được dẫn. `max-examples` không phải tổng số yêu cầu gửi đi.

Các file trong `artifacts/` là bằng chứng cục bộ và có thể không đi kèm bản sao repository. Khi bàn giao báo cáo, cần kèm các file bằng chứng được chọn nếu người đọc cần kiểm tra kết quả gốc.

## 11. Phạm vi đã có và những điểm nên bổ sung

Thiết kế hiện có kết hợp ba lớp: mô hình dữ liệu và quyền, các kịch bản nghiệp vụ dễ theo dõi, và các ca cụ thể cùng yêu cầu do công cụ tự sinh. Các lớp này hỗ trợ nhau: công cụ mở rộng đầu vào, còn ca nghiệp vụ kiểm tra những điều schema chưa mô tả đầy đủ.

Các kết quả hiện có chưa chứng minh toàn bộ Directus không có lỗi. Đã gọi được 10/10 thao tác cũng chưa chứng minh mọi giá trị đầu vào, mọi nhánh mã và mọi tình huống sử dụng đã được kiểm tra.

Những nội dung dưới đây là **đề xuất bổ sung**, không phải các ca độc lập đã được xác minh trong báo cáo này:

| Đề xuất | Lý do |
|---|---|
| Tách yêu cầu Reader đọc bài nháp chỉ với trường công khai | Xác định rõ việc chặn là do trạng thái bài, tránh trộn với quyền trường kín |
| Kiểm tra riêng điểm sai và trạng thái sai | Xác định từng ràng buộc hoạt động độc lập, thay vì chỉ thử cả hai sai cùng lúc |
| Lập ca độc lập cho điểm -1, 0, 5, 6 và giá trị không phải số nguyên | Làm rõ kiểm tra giá trị nhỏ nhất, lớn nhất và giá trị vượt giới hạn |
| Lập ca độc lập cho tiêu đề thiếu, rỗng, 120 và 121 ký tự | Làm rõ quy tắc bắt buộc và giới hạn độ dài |
| Tiếp tục điều tra hai ca FAIL và các failure tự sinh | Phân biệt lỗi phần mềm, thiếu sót schema và vấn đề dữ liệu hoặc bộ kiểm thử |

Việc bổ sung hoặc điều chỉnh ca cần giữ lại kết quả cũ để truy vết, đồng thời xác định trước kết quả mong đợi. Không sửa tiêu chí chỉ để khớp phản hồi đang quan sát được.

## 12. Tài liệu và mã nguồn đối chiếu

1. [README — Tổng quan và cách chạy dự án](../README.md).
2. [Test model, scenario và test case hiện có](phan2/02-test-model-va-test-cases.md).
3. [Ma trận operation, scenario và invariant](test-matrix.md).
4. [Cơ sở lý thuyết và tiêu chí áp dụng](phan2/01-co-so-ly-thuyet.md).
5. [Mã chuẩn bị dữ liệu, schema và sáu scenario](../scripts/lab-components.sh): các hàm `scenario_editor_crud`, `scenario_filter_status`, `scenario_sort_pagination`, `scenario_reader_no_draft`, `scenario_reader_hidden_field`, `scenario_reader_write`.
6. [Mã bộ 11 ca invariant](../scripts/invariants.py): các hàm `case_*` và danh sách đăng ký ca trong `run()`.
7. [Bằng chứng dựng lại và kiểm thử trên Windows ngày 13/10/2026](../evidence/windows-recheck-2026-10-13.md).
8. [Báo cáo sáu scenario của lần chạy được dẫn](../artifacts/runs/20261012T185849Z-1525/scenario-report.json).
9. [Báo cáo 11 ca invariant của lần chạy được dẫn](../artifacts/runs/20261012T185934Z-1453/invariant-report.json).
