# Bài 8 — Thực hành tổng hợp và bảo vệ

## 8.1. Mục tiêu cuối khóa

Sau tám bài, bạn phải tự giải thích được chuỗi sau mà không đọc thuộc lệnh:

```text
Yêu cầu R06/K05
  -> risk + oracle
  -> fixture/actor/policy
  -> Directus + PostgreSQL
  -> schema theo actor
  -> raw/guided Schemathesis
  -> scenario/invariant
  -> artifact/metrics
  -> triage/replay
  -> kết luận có giới hạn
```

Nếu chỉ có thể nói “Schemathesis chạy và có report” nhưng không nói được actor, schema hash, precondition và classification, phần K05 chưa được hiểu đầy đủ.

## 8.2. Kịch bản tự demo 15 phút

### Phút 0–2: đặt vấn đề

Nói rõ Directus là REST API, K05 là schema-based API testing/fuzzing, mục tiêu là schema conformance + invariant nghiệp vụ + quyền + reproducibility. Nêu ngoài phạm vi: GraphQL, frontend, load test, nhiều DB đối chứng.

### Phút 2–5: kiến trúc và baseline

Mở [`docs/architecture.md`](../../docs/architecture.md), chỉ ra `lab.sh`, Directus, PostgreSQL, runner, artifacts. Nêu version/digest từ config/manifest, không đọc secret.

### Phút 5–8: fixture và quyền

Mở [`docs/permissions.md`](../../docs/permissions.md) và fixture map của một run. Giải thích 3 category, 12 article, 6 draft/6 published, Unicode/null và bốn actor.

### Phút 8–11: ba luồng ổn định

Chạy hoặc mở evidence cho:

1. Editor CRUD;
2. query filter/sort/pagination/projection;
3. Reader visibility/write denial.

Nhấn mạnh S6: PATCH Reader `403`, read-back Editor `200`, dữ liệu không đổi.

### Phút 11–13: OpenAPI và K05

Mở schema manifest: actor counts `14/14/6/0`, campaign allowlist `10`. Giải thích raw giữ contract, guided dùng overlay riêng; seed/budget/restore.

### Phút 13–15: failure trung thực

Nêu invariants `9 passed / 2 failed / 0 blocked`, raw/guided chưa PASS toàn bộ, aggregate `500` và schema candidates còn mở. Phân biệt candidate với defect đã xác minh; mở một artifact/reproducer nếu được hỏi.

## 8.3. Cách trả lời khi bị hỏi “đã hoàn thành chưa?”

Không trả lời một từ. Dùng cấu trúc:

1. **Đã hoàn thành**: stack, seed, schema theo actor, scenario, artifact và interface đã chạy được.
2. **Đã quan sát**: nêu run ID, exit/status và số pass/fail thật.
3. **Chưa hoàn tất**: raw/guided full campaign còn failed/incomplete; invariants còn 2 failure; chưa có peer review/máy thứ hai trong evidence.
4. **Không kết luận**: chưa xác nhận product defect nếu thiếu triage.
5. **Bước tiếp theo**: replay/triage case cụ thể, không đổi expected để làm đẹp.

## 8.4. Checklist trước demo

- [ ] `./lab.sh doctor` pass trong môi trường hiện tại.
- [ ] Đúng Compose project và API URL local.
- [ ] Không có credential trong terminal capture/report.
- [ ] Có schema hash và fixture map của run trình bày.
- [ ] Biết scenario nào là final evidence, run trung gian nào không dùng làm kết luận.
- [ ] Biết raw/guided status thật.
- [ ] Có cách mở log/report/reproducer.
- [ ] Phân biệt requirement giảng viên, quyết định nhóm, đề xuất và observation.
- [ ] Không tuyên bố review chéo/máy thứ hai nếu không có bằng chứng.

## 8.5. Câu hỏi phản biện thường gặp

**“Tại sao không dùng schema admin cho mọi actor?”**

Vì schema có thể bị lọc bởi quyền; dùng admin sẽ làm sai phạm vi Reader/anonymous. Phải export riêng và ghi inventory `14/14/6/0`.

**“Tại sao test pass mà campaign vẫn fail?”**

Scenario/invariant và Schemathesis trả lời các thuộc tính khác nhau. Campaign có check failure hoặc timeout thì không thể gọi PASS toàn bộ chỉ vì smoke pass.

**“500 có phải bug không?”**

Là candidate cần tái hiện và phân biệt harness/fixture/schema/environment. Phải kiểm controls, source contract và version pin.

**“Tại sao không gửi PATCH Reader nếu operation không có trong schema?”**

Đó là request có chủ đích ngoài contract export; quy tắc harness yêu cầu ghi blocked, không giả vờ đã kiểm quyền bằng một operation bị lọc.

**“Guided có làm sai nghiên cứu không?”**

Không nếu raw bất biến, overlay lưu riêng, có diff/hash/lý do và kết quả báo riêng. Guided trả lời giả thuyết khác raw.

## 8.6. Nhật ký học tập cá nhân

Sau mỗi buổi, ghi vào một file riêng ngoài Git:

```text
Ngày:
Bài đã học:
Khái niệm tôi đã hiểu:
Lệnh đã chạy + run_id:
Điều còn mơ hồ:
Một câu tôi có thể tự giải thích:
Một việc cần làm lại:
```

Thước đo tốt nhất là tự dựng lại từ máy sạch và tự giải thích một failure bằng precondition/expected/actual, không phải số trang đã đọc.

