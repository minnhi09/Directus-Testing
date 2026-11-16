# P03 — Route/điều kiện chờ phân giải

Tất cả entry máy đọc được trong [unresolved-routes.jsonl](unresolved-routes.jsonl), revision `P03-AUTH-SYSTEM-4f77933-v1`. Đây là danh sách gap, không phải test thất bại hoặc route N/A. Không làm mất route khi schema/OAS chưa đủ.

## Sáu khai báo SEARCH chưa vừa enum P01

| Method/path nguồn | Source@SHA/dòng |
|---|---|
| `SEARCH /users` | `../directus/api/src/controllers/users.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L86` |
| `SEARCH /roles` | `../directus/api/src/controllers/roles.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L74` |
| `SEARCH /policies` | `../directus/api/src/controllers/policies.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L83` |
| `SEARCH /permissions` | `../directus/api/src/controllers/permissions.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L89` |
| `SEARCH /access` | `../directus/api/src/controllers/access.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L81` |
| `SEARCH /collections` | `../directus/api/src/controllers/collections.ts@4f77933bf9551cac6b289576078783e189b8f4e3:#L70` |

P01 `common.schema.json#/$defs/method` chưa có SEARCH. Không sửa schema hoặc ghi SEARCH thành GET trong P03. `GAP-P03-SEARCH-METHOD`/`DEC-P03-SEARCH-CONTRACT` giữ yêu cầu review revision hợp đồng, sau đó migrate đủ sáu entry; **chưa được phép khóa mẫu số chỉ bằng 113 record đã serialize**.

## Bốn entry còn lại

1. **UNRESOLVED-PROVIDER-NAMES** — factory đã lần đủ, concrete names/driver/profile/license config chưa biết; giữ template `/auth/login/{provider}`, không đọc env thật hoặc liên hệ provider. Gap PROVIDERS.
2. **UNRESOLVED-PATH-SHAPES** — hai optional pattern và hai TFA trailing-slash declaration cần review dispatch/normalization/denominator. Pattern nguồn được giữ trong sidecar; source đã giải được, runtime equivalence chưa xác minh. Gap PATH-SHAPES.
3. **Historical /auth/oauth** — có path trong admin OAS cũ, không thấy mount tương ứng ở auth/driver đã audit tại baseline. Chỉ drift candidate; extension/hook/runtime/source khác ngoài shard chưa kết luận. Gap OAS.
4. **Historical /auth/oauth/{provider}** — cùng giới hạn trên, không tạo source route hoặc alias cho `/auth/login/{provider}` để làm khớp.

`GAP-P03-OAS` còn giữ chênh lệch số operation 143 trong file OAS và 14 lưu manifest; chưa truy nguyên phạm vi/counter. Các gap runtime/scope/actor áp dụng cho shard dù không mỗi gap có một route pattern chưa parse.

Bước độc lập đã hoàn tất: mount/literal child route/source guards/profile candidates ở đúng SHA. Phần phụ thuộc còn lại: contract SEARCH được review, current full/admin/actor OAS, deployment/config/license/provider/profile và applicability/canonical merge. Không khởi động lab hoặc export API để lấp gap trong P03.

