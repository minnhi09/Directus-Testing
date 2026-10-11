# Kịch bản demo 10–15 phút

Demo chỉ chạy trên lab local đã cô lập. Không dùng server public hoặc project Docker khác.

## Precondition

```bash
./lab.sh doctor
./lab.sh up
./lab.sh seed
./lab.sh export-schema
```

Nếu `seed` dừng ở license Reader, trình bày đó là blocker đã xác minh và tiếp tục các demo Editor/anonymous đã có bằng chứng; không giả lập quyền Reader bằng Admin. Trên checkpoint local hiện tại, license đã active nên có thể demo thêm Reader published/private projection/write rejection.

## Ba luồng ổn định

1. Editor CRUD: `./lab.sh replay editor-crud`. Chỉ ra ID lấy từ response create, PATCH chỉ đổi `score`, đọc lại vẫn giữ `title`, DELETE trả success và đọc lại không còn data.
2. Query fixture: `./lab.sh replay query-fixture`. Chỉ ra filter published, sort `title,id`, projection và hai page được tính oracle từ `fixture-ids.json`.
3. Anonymous/auth: `./lab.sh replay anonymous-denied` và `./lab.sh replay auth-invalid-token`. Chỉ ra hai collection trả non-2xx, token giả không được chấp nhận, status cụ thể được giữ theo baseline.
4. Reader policy: `./lab.sh replay reader-visibility` và `./lab.sh replay reader-write`; chỉ ra published read, private projection bị từ chối và target không đổi sau PATCH bị từ chối.
5. Schemathesis finding: `./lab.sh replay aggregate-query-robustness`; chỉ ra request tối giản, HTTP 500, hai control 200, report failure và restore fixture.

## Schemathesis

Để demo nhanh mà không chạy ngân sách dài:

```bash
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test raw
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test guided
```

Mở `campaign-index.json`, `operation-inventory.json`, `metrics.json` và report. Nêu rõ đây là pilot; runner failure phải được giữ để triage. Chứng minh fixture vẫn khớp snapshot bằng dòng `Campaign restore: PASS`.

Campaign đầy đủ local hiện tại là raw `20261011T085034Z-76481` và guided `20261011T095117Z-89079`. Cả ba seed đều test 10/10 operation và restore PASS, nhưng runner kết thúc `failed` do các check phát hiện/max-time, không phải pass campaign.

## Kết thúc

```bash
./lab.sh down
```

Mặc định `down` giữ volume. Chỉ demo `./lab.sh reset` khi đã lưu artifact cần thiết và xác nhận volume có label project `r06-k05`; reset là thao tác xóa dữ liệu lab.
