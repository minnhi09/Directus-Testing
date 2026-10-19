# 02 — Test model, scenario và test case

## Mô hình kiểm thử

SUT là Directus API trong Compose project `r06-k05`, với PostgreSQL 16. Dữ liệu gồm ba category và mười hai article: sáu `draft`, sáu `published`; article có `score`, nullable `published_at`, JSON `metadata`, `internal_notes` và quan hệ nhiều–một `category`.

Actor và quyền được seed/kiểm tra trong `scripts/lab-components.sh`:

| Actor | Phạm vi |
|---|---|
| admin | bootstrap, schema và kiểm tra trạng thái |
| editor | CRUD hai collection trong lab |
| reader | đọc category/article published, bị che `internal_notes`, không ghi |
| anonymous | không đọc hai collection |

Campaign allowlist có 10 operation: `GET/POST /items/qa_categories`, `GET/PATCH/DELETE /items/qa_categories/{id}`, và năm operation tương ứng của `qa_articles`. Bulk operation, GraphQL, WebSocket và API quản trị ngoài phạm vi.

## Sáu scenario nghiệp vụ

| ID | Mục tiêu/rủi ro | Tiền đề, actor, input và bước | Expected | Actual mới | Trạng thái/run/artifact |
|---|---|---|---|---|---|
| S1 | CRUD và read-back không làm mất field | fixture; Editor; POST article, GET, PATCH score, GET, DELETE, GET | CRUD 2xx/204, ID động, sau delete không còn data | Các bước đạt | PASS — `20261012T110708Z-18415/scenario-report.json` |
| S2 | Filter không trả draft | 6 published/6 draft; Editor; filter status | đúng tập published | Đạt | PASS — cùng scenario report |
| S3 | Sort và phân trang ổn định | fixture; Editor; sort title/id, limit/offset/page | page/offset khớp oracle fixture | Đạt | PASS — cùng scenario report; invariant mới kiểm tra thêm page |
| S4 | Reader không thấy draft | Reader schema; GET articles | chỉ published | Đạt | PASS — cùng scenario report |
| S5 | Không lộ field kín | Reader; `fields=internal_notes` | non-2xx/403, không lộ dữ liệu | 403 | PASS — cùng scenario report |
| S6 | Reader không được ghi | Reader có article published; PATCH rồi Editor đọc lại | bị từ chối và target không đổi | 403, dữ liệu giữ nguyên | PASS — cùng scenario report |

## Mười một invariant

| ID | Case | Oracle chính | Actual run `20261012T110713Z-18872` | Trạng thái/artifact |
|---|---|---|---|---|
| INV-01 | `auth-invalid-token` | token giả bị từ chối | 401 | PASS |
| INV-02 | `anonymous-denied` | anonymous không đọc collection | 403 | PASS |
| INV-03 | `editor-crud` | create/read/PATCH/delete, field không cập nhật giữ nguyên | đạt | PASS |
| INV-04 | `positive-operations` | đủ 10 operation có positive acceptance | đạt | PASS |
| INV-05 | `query-fixture` | filter, sort, offset, page, search, projection khớp fixture | 6 published; page=2 và `spéciale` đều khớp | PASS |
| INV-06 | `aggregate-query-robustness` | unknown aggregate không 5xx; control 2xx | `{"foo":1}` → 500; `{}` và count → 200 | FAIL/candidate |
| INV-07 | `contract-schema-candidates` | runtime đối chiếu response/status/content type schema | 4 candidate được ghi và cleanup đạt | FAIL/candidate |
| INV-08 | `relation-nullification` | xóa category đặt article.category null | đạt | PASS |
| INV-09 | `invalid-field-rejection` | score/status sai bị từ chối, không tạo rác | POST 400, không có row | PASS |
| INV-10 | `reader-visibility` | Reader chỉ thấy published, field kín bị chặn | published 200, projection 403 | PASS |
| INV-11 | `reader-write` | Reader PATCH bị từ chối, target không đổi | PATCH 403, read-back không đổi | PASS |

Invariant report nằm trong `artifacts/runs/20261012T110713Z-18872/invariant-report.json`; summary là 9 PASS, 2 FAIL, 0 BLOCKED, exit 1. Hai FAIL được giữ nguyên, chưa tự động gọi là defect.

## Campaign và replay cases

Các case generated không được đếm như scenario mới. Mỗi campaign case phải truy được operation, seed, schema hash, check, request/response và report NDJSON. Nhóm case dùng trong triage gồm:

| Nhóm | Expected/actual cần ghi | Trạng thái case |
|---|---|---|
| Raw/guided positive và negative | status/content/schema theo report | phụ thuộc campaign mới |
| Aggregate `foo` và hai control | 500 so với control 200 | candidate deterministic |
| timestamp rỗng, export JSON/XML/YAML, projection | response runtime khác schema/semantic expectation | contract/schema candidate |
| full stateful chain và thiếu parent mapping | source/actual, chuỗi ID, `replay_scope` | reproduced hoặc mismatch theo artifact |

Case ID, run ID, source artifact và actual cuối cùng của replay đã được xác nhận:

| Test case | Mục tiêu/rủi ro | Tiền đề và actor | Expected | Actual mới | Trạng thái, run và artifact |
|---|---|---|---|---|---|
| TC-CAM-RAW-101 | Sinh request raw trên đủ allowlist | fixture `r06-k05-v2`, Editor, seed 101 | runner hoàn thành budget, không lỗi restore | 59 cases, 18 có failure, 20 unique; `max_time`, restore 0 | FAIL theo check; `20261012T112746Z-20300/raw/seed-101/` |
| TC-CAM-GUIDED-101 | Guided/stateful với ID và payload fixture | fixture, Editor, seed 101 | kiểm tra contract và stateful chain | 5.809 cases, 50 có failure, 111 errored; `max_time`, restore 0 | FAIL theo check; `20261012T122826Z-22781/guided/seed-101/` |
| TC-CAM-GUIDED-202 | Guided seed 202 | fixture, Editor, seed 202 | đạt budget đầy đủ | 3.158 cases; bị ngắt ở 645,046 giây, restore 0 | INCOMPLETE; `20261012T122826Z-22781/guided/seed-202/` |
| TC-REPLAY-DELETE | Tái hiện status DELETE 204 ngoài response map | snapshot fixture, Editor | actual giữ 204 và restore PASS | actual 204, cùng expected check failure | PASS replay (`reproduced`); run `20261012T135615Z-28334`, case `q40gXE` |
| TC-REPLAY-POST-SCHEMA | Tái hiện response POST shape | snapshot fixture, Editor | response `data` là array theo schema | actual `data` là object, status 200 | PASS replay (`reproduced` mismatch); run `20261012T135624Z-28947`, case `n2R7IY` |

Raw seed 202/303 và guided seed 303 được mô tả chi tiết trong `04-ket-qua-kiem-thu.md`; mọi generated case vẫn được truy vết qua report/NDJSON, không đếm thành scenario nghiệp vụ mới. Không dùng token trong reproducer.

