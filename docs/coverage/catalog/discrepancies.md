# P06 — Discrepancy và giới hạn reuse

Kết luận ở đây cập nhật cách đọc mục 8, không thay expected/verdict lịch sử. Nguồn cụ thể và hash ở canonical-catalog/reuse-comparisons/input-fingerprints; toàn bộ candidate so theo actor, method/path, input partition, precondition và oracle thực, không chỉ tên.

| ID | Nhận định cần làm rõ | Đối chiếu / kết luận P06 |
|---|---|---|
| DISC-P06-01 | TC51 tái dùng forbidden-field/payload/control từ P3-INTERNAL_NOTES-POST-TEXT | Candidate là Editor POST qa_articles, O-ROUNDTRIP với Unicode internal_notes. Chỉ payload/roundtrip SUPPORTING; không chứng minh Reader/import forbidden-field hoặc atomicity. Negative actor control dùng DR-036/037/039, vẫn khác import parser. |
| DISC-P06-02 | TC19 tái dùng DR-044/045 | Hai candidate là Reader POST/PATCH qa_categories, O-DENY; không phải fields/collections quản trị. Chỉ deny/read-back pattern SUPPORTING, không DIRECT cho schema permission. |
| DISC-P06-03 | Hàng gốc TC42 chứa P3-ST-02/OP-02–05 | Sau tách TC42 login/session Studio, CRUD source helper chuyển TC58. API CRUD không chứng minh login/UI; không lấy lại historical verdict. TC42 vẫn revised; TC58 delta có source candidates cụ thể. |
| DISC-P06-04 | Catalog NOT_RUN cạnh report PASS/FAIL | Là hai loại trạng thái; không đồng bộ ngược catalog. 3 report nguồn tạo observation có overlap. TC13 business passed/contract failed không bị nâng thành overall PASS. |
| DISC-P06-05 | Tổng 257 + 13 + 49 hoặc 312 registry | 13 TC legacy là alias, 6 S identity vẫn có overlap cần review. 312 là record registry, không phải tổng độc lập/coverage; selection/denominator chờ P07. |
| DISC-P06-06 | P3 nested create/invalid relation dùng cho TC24/25 | Oracle OPEN hoặc khác M2O/M2M/transaction không đủ chứng minh junction/rollback. Giữ readiness từ catalog và chỉ SUPPORTING. |
| DISC-P06-07 | Fixture/precondition/implementation có trong văn bản | P01 ID field không nhận văn bản tự do. Một precondition có chú giải giữ ở source/partition; không bịa ID hoặc fixture profile để làm schema đạt. |

Không thay phân loại 44 hàng gốc chỉ để tăng exact reuse: 16 partial, 4 revised, 24 new; new chỉ theo catalog 257, không khẳng định upstream không có test. Năm delta sau tách vẫn NOT_RUN. Không tìm được bằng chứng đủ để biến bất kỳ thiết kế mới nào thành alias toàn phần của P3.

Không tự chốt runtime behavior token TC14 từ GET users/me control; expected refresh/logout cần source/profile riêng sau này. GraphQL/WS/UI/SDK không dùng verdict REST làm acceptance. Những phần này là GAP-P06-DELTA/BINDINGS, không phải test FAIL mới.

Kế hoạch §8 đã thêm note trỏ log này và các đính chính chính. Chỉ ghi thay đổi tài liệu; không sửa runner hay source oracle.
