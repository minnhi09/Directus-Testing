# Bài tập tự luyện

Hãy làm bài trước khi mở [đáp án gợi ý](dap-an.md). Khi chạy lệnh, dùng lab local, không dùng server ngoài phạm vi. Ghi `run_id`, exit code và artifact; không ghi credential.

## Bài 1 — Biến yêu cầu thành test case

Yêu cầu: “Reader chỉ đọc bài published, không thấy `internal_notes`, không được ghi.”

Viết một test case có đủ:

- ID và mục tiêu;
- precondition;
- actor/request;
- expected/oracle;
- cleanup;
- artifact cần lưu.

Sau đó giải thích vì sao một assertion duy nhất `PATCH trả 4xx` là chưa đủ.

## Bài 2 — Phân hoạch và giá trị biên

Lập bảng input cho:

1. `score` từ 0 đến 5;
2. `title` tối đa 120 ký tự;
3. `status` chỉ `draft/published`.

Mỗi bảng phải có giá trị hợp lệ thấp/cao, giữa, ngoài miền và sai kiểu. Với mỗi nhóm, nêu expected không được suy đoán cứng nếu chưa có baseline.

## Bài 3 — Đọc request Directus

Phân tích request sau:

```http
GET /items/qa_articles?filter[status][_eq]=published&fields=id,title,status&sort=-id&limit=2&offset=0
Authorization: Bearer <redacted>
```

Trả lời:

1. actor nào được suy ra trực tiếp từ request?
2. filter/sort/fields/limit/offset có vai trò gì?
3. cần dùng fixture nào để tính expected?
4. những lỗi nào có thể xảy ra dù status là `200`?

## Bài 4 — Kiểm tra schema inventory

Không sửa schema. Sau khi lab healthy, chạy export schema và trả lời:

1. admin/editor/reader/anonymous có bao nhiêu operation?
2. Vì sao inventory export không bằng campaign count?
3. liệt kê 10 method–path của campaign chính;
4. nếu Reader không có PATCH operation, scenario nên ghi gì và vì sao không gửi request?

## Bài 5 — Raw hay guided?

Có hai giả thuyết:

- H1: contract gốc có response không phù hợp runtime.
- H2: với fixture ID hợp lệ và body hợp lệ, workflow CRUD đi sâu hơn.

Chọn raw/guided cho từng giả thuyết. Liệt kê file/hash/diff cần lưu để kết quả có thể so sánh.

## Bài 6 — Thiết kế invariant PATCH

Viết pseudo-code cho invariant “PATCH chỉ score không làm mất title, status, metadata, category”.

Yêu cầu:

- snapshot trước;
- request actor phù hợp;
- expected field đổi;
- field không gửi giữ nguyên;
- read-back;
- cleanup;
- cách ghi failure.

## Bài 7 — Triage một failure

Giả sử report ghi:

```text
GET /items/qa_articles?aggregate={"foo":1}
actual: 500
controls: aggregate={} -> 200; aggregate={"count":["id"]} -> 200
```

Hãy phân loại tạm thời, liệt kê bằng chứng cần bổ sung và giải thích vì sao chưa được gọi ngay là product defect.

## Bài 8 — Replay stateful

Một case có chuỗi `POST category -> POST article -> PATCH article`, nhưng artifact chỉ lưu interaction cuối. Hãy giải thích:

1. replay nào có thể thực hiện?
2. precondition nào chưa được chứng minh?
3. report phải ghi `sequence_replayed`/scope thế nào?
4. muốn chứng minh đầy đủ cần bổ sung artifact gì?

## Bài 9 — Thực hành pilot có kiểm soát

Chạy:

```bash
./lab.sh doctor
./lab.sh up
./lab.sh seed
./lab.sh export-schema
./lab.sh test scenarios
./lab.sh test invariants
LAB_CAMPAIGN_SEEDS=101 LAB_MAX_EXAMPLES=1 LAB_MAX_TIME=30 ./lab.sh test raw
```

Ghi lại:

- các run ID;
- command nào exit khác 0;
- operation/profile/seed/budget;
- scenario/invariant summary;
- restore status;
- một kết luận được phép và một kết luận chưa được phép.

## Bài 10 — Tự bảo vệ

Trong 3 phút, không mở code, trả lời:

1. K05 khác smoke test thế nào?
2. raw và guided khác gì?
3. schema coverage có phải code coverage không?
4. vì sao không dùng schema admin cho Reader?
5. một check failure có phải một bug không?

Ghi âm hoặc viết câu trả lời, rồi đối chiếu [câu hỏi bảo vệ](cau-hoi-bao-ve.md).

