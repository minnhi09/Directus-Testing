# 04 — Kết quả kiểm thử, log và metrics

## Môi trường và run deterministic

Môi trường đã xác minh ngày 2026-10-12:

| Thành phần | Bằng chứng |
|---|---|
| Directus | image `12.5.0`, digest được `doctor` ghi trong metadata |
| Schemathesis | image `4.30.0` digest pinned |
| Database | PostgreSQL 16 Alpine trong network `r06-k05` |
| Docker/Compose | daemon và Compose PASS trong `20261012T110648Z-16237` |
| Fixture | `r06-k05-v2`, 3 category, 12 article, 6 draft/6 published |
| Schema | admin 14 operation, editor 14, reader 6, anonymous 0; hash ở run `20261012T110701Z-17969` |

Baseline digest được ghi trong metadata raw/guided: Directus `12.5.0@sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331`, PostgreSQL `16-alpine@sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea`, Schemathesis `4.30.0@sha256:bb9cecfc9ac4058a15fcf9b505d9d9f972e2dde7c74c4e9289a35922f4cbc0a5`. Schema scoped cho raw là `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`; guided là `cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`. Harness SHA của hai campaign là `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72`.

Các lệnh đã chạy:

| Lệnh | Run | Kết quả |
|---|---|---|
| `./lab.sh doctor` | `20261012T110648Z-16237` | PASS, health/auth/image/config |
| `./lab.sh seed` | `20261012T110652Z-16803` | PASS, fixture idempotent |
| `./lab.sh smoke` | `20261012T110657Z-17548` | PASS, validation/relation/Reader filter |
| `./lab.sh export-schema` | `20261012T110701Z-17969` | PASS, actor schema/hash |
| `./lab.sh test scenarios` | `20261012T110708Z-18415` | 6 PASS, 0 FAIL, 0 BLOCKED |
| `./lab.sh test invariants` | `20261012T110713Z-18872` | 9 PASS, 2 FAIL, 0 BLOCKED, exit 1 |

`query-fixture` mới PASS với filter/sort/projection, offset 0/3, `page=2` và search `spéciale`. Hai invariant FAIL có bằng chứng response và control; không phải lỗi môi trường.

## Campaign raw/guided

Ngân sách đã chọn và thực thi: seed `101,202,303`, 10 operation, tối đa 100 examples/operation, một worker, `5/s`, timeout 10 giây, 1.200 giây/profile/seed. Artifact campaign được lưu trong `artifacts/runs/<run_id>/<profile>/seed-<seed>/`.

Run raw mới `20261012T112746Z-20300` được chạy sau khi sửa guard restore. Run đầu `20261012T110720Z-19253` chỉ hoàn thành seed 101 vì lỗi điều khiển shell được giữ lại như bằng chứng harness; không dùng nó để tuyên bố đủ ba seed.

Bảng kết quả raw/guided được điền từ `campaign-index.json` và `campaign-summary.json` sau khi runner kết thúc:

| Profile | Seed | Operations tested | Cases/failures/errors | Stop reason | Runner | Restore | Status |
|---|---:|---:|---|---|---:|---:|---|
| raw | 101 | 10/10; 59 generated | 18 with failures; 20 unique; 0 errors | max_time | 1 | 0 | failed |
| raw | 202 | 10/10; 65 generated | 18 with failures; 18 unique; 0 errors | max_time | 1 | 0 | failed |
| raw | 303 | 10/10; 51 generated | 18 with failures; 19 unique; 0 errors | max_time | 1 | 0 | failed |
| guided | 101 | 10/10; 5.809 generated | 50 with failures; 63 unique; 111 errored | max_time | 1 | 0 | failed |
| guided | 202 | 10/10; 3.158 generated | 44 with failures; 53 unique; 107 errored | interrupted | 130 | 0 | failed/incomplete |
| guided | 303 | 10/10; 5.898 generated | 50 with failures; 62 unique; 200 errored | max_time | 1 | 0 | failed |

`guided/seed-202` chạy 645,046 giây trước khi nhận tín hiệu ngắt từ lần tạm dừng công việc; report và coverage đã được ghi, fixture restore PASS, nhưng chưa đạt ngân sách 1.200 giây nên được giữ là `INCOMPLETE`. Hai seed guided còn lại chạy đến `max_time`. Mọi seed đều test đủ 10 operation và mọi restore đều có `restore_exit_code=0`.

Nhóm failure trong report JSON:

| Profile/seed | Nhóm nổi bật (count trong report) |
|---|---|
| raw/101 | `UndefinedStatusCode` 16; `UnsupportedMethodResponse` 2; `RejectedPositiveData` 2 |
| raw/202 | `UndefinedStatusCode` 14; `UnsupportedMethodResponse` 2; `RejectedPositiveData` 1; `UndefinedContentType` 1 |
| raw/303 | `UndefinedStatusCode` 16; `UnsupportedMethodResponse` 2; `RejectedPositiveData` 1 |
| guided/101 | `UndefinedStatusCode` 30; `ServerError` 9; `JsonSchemaError` 6; `RejectedPositiveData` 8; `AcceptedNegativeData` 3; `UndefinedContentType` 5; `UnsupportedMethodResponse` 2 |
| guided/202 | `UndefinedStatusCode` 26; `JsonSchemaError` 7; `ServerError` 5; `RejectedPositiveData` 8; `AcceptedNegativeData` 2; `UndefinedContentType` 3; `UnsupportedMethodResponse` 2 |
| guided/303 | `UndefinedStatusCode` 29; `ServerError` 8; `JsonSchemaError` 7; `RejectedPositiveData` 8; `AcceptedNegativeData` 3; `UndefinedContentType` 5; `UnsupportedMethodResponse` 2 |

Các số trên là số check failure được report, không phải số defect. `ServerError` và các response 400/403/500 cần triage theo actor, precondition và request; không gộp trực tiếp thành lỗi Directus.

Coverage theo schema được đo trong `schemathesis-coverage.json` (không phải code coverage):

| Artifact | Operations | Parameters | Keywords | Responses | Response keywords reached/violated |
|---|---:|---:|---:|---:|---:|
| raw/101 | 10/10 (100%) | 28/48 (58,33%) | 67/226 (29,65%) | 8/26 (30,77%) | 110/386; violated 6 |
| raw/202 | 10/10 (100%) | 28/48 (58,33%) | 70/226 (30,97%) | 8/26 (30,77%) | 110/386; violated 11 |
| raw/303 | 10/10 (100%) | 28/48 (58,33%) | 67/226 (29,65%) | 8/26 (30,77%) | 110/386; violated 6 |
| guided/101 | 10/10 (100%) | 41/48 (85,42%) | 180/226 (79,65%) | 8/26 (30,77%) | 150/386; violated 39 |
| guided/202 | 10/10 (100%) | 40/48 (83,33%) | 170/226 (75,22%) | 8/26 (30,77%) | 150/386; violated 42 |
| guided/303 | 10/10 (100%) | 42/48 (87,50%) | 176/226 (77,88%) | 8/26 (30,77%) | 150/386; violated 37 |

Replay mới:

| Case | Source | Actual | Status | Restore |
|---|---|---|---|---:|
| `q40gXE` | raw/101, `DELETE /items/qa_articles/1`, expected 204 | 204 | `reproduced` | 0 |
| `n2R7IY` | guided/101, `POST /items/qa_articles`, expected 200 nhưng response `data` là object | 200, cùng mismatch schema | `reproduced` | 0 |

Replay reports lần lượt là `artifacts/runs/20261012T135615Z-28334/reproducer-schemathesis-q40gXE.json` và `artifacts/runs/20261012T135624Z-28947/reproducer-schemathesis-n2R7IY.json`.

Không có số liệu code coverage Directus. Coverage JSON của Schemathesis chỉ được báo cáo theo trường thực tế có trong file và không chuyển thành line/branch coverage.

## Artifact và cách đọc

Mỗi run cần đối chiếu `metadata.json`, `run.log`, `schema-manifest.json`, schema hash, `schemathesis-report.json`, `schemathesis-events.ndjson`, `schemathesis-coverage.json`, `metrics.json`, `campaign-summary.json` và `campaign-index.json`. Report hoàn tất không đồng nghĩa campaign PASS; `runner_exit_code`, `termination` và `restore_exit_code` phải được đọc cùng nhau. Artifact đầy đủ của raw nằm ở `artifacts/runs/20261012T112746Z-20300/`, guided ở `artifacts/runs/20261012T122826Z-22781/`. Run raw đầu `20261012T110720Z-19253` chỉ chạy seed 101 do lỗi điều khiển shell cũ; được giữ để audit và không dùng làm kết quả full campaign.

