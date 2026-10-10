# Evidence G0 — shared interface and lab runtime — 2026-10-10

Đây là bằng chứng cho phần giao diện dùng chung của Lành và lần kiểm tra lại
lab sau khi Docker Desktop khả dụng. Credential, token và response nhạy cảm
không được ghi vào tệp này.

## Baseline và provenance

- Repository: nhánh `main`, harness base commit `a2693f6154753cca2f1d2eb3d84e3a831a42bbf0`.
- Working tree còn thay đổi chưa commit của phần giao diện chung; không tuyên bố
  SHA cho các thay đổi chưa commit.
- Docker Server `29.8.1`; Docker Compose `v5.5.1`.
- Image Directus, PostgreSQL và Schemathesis được kiểm tra theo digest trong
  [`manifest/baseline.yaml`](../manifest/baseline.yaml).

## Lệnh và kết quả

| Lệnh/artefact | Kết quả quan sát |
|---|---|
| `bash -n lab.sh` | Đạt |
| ShellCheck `lab.sh` | Đạt, không còn cảnh báo mức warning |
| `git diff --check` | Đạt |
| `./lab.sh doctor` | Exit `0`; run `20261010T053843Z-44725`; Docker/Compose, config, compose render, image digest và API liveness đạt |
| `./lab.sh doctor` sau khi bổ sung auth check | Exit `0`; run `20261010T054547Z-46801`; `/server/health` trả HTTP `200` với admin accountability, token không được ghi |
| `./lab.sh up` | Exit `0`; run `20261010T053700Z-41993`; database và Directus healthy |
| `GET http://127.0.0.1:8055/server/ping` | HTTP `200` |
| `docker compose ... ps` | `r06-k05-database-1` healthy; `r06-k05-directus-1` healthy |
| `./lab.sh test schema-smoke` | Chưa triển khai, exit `2`; run `final-schema-smoke`; metadata vẫn được lưu và giữ đúng mã lỗi |

Mỗi run được lưu cục bộ dưới `artifacts/runs/<run_id>/` với
`metadata.json`/`run.log`; thư mục này bị Git ignore. `runtime/fixture-ids.json`
chưa có vì seed chưa được triển khai.

## Giới hạn

- Credential `editor`/`reader`, fixture, policy, schema snapshot, scenario và
  Schemathesis pilot chưa được bàn giao; chưa có cơ sở tuyên bố G1.
- Lần kiểm tra đầu trong phiên bị chặn vì Docker Desktop đang dừng; sau đó đã
  khởi động Docker Desktop bằng CLI chính thức và kiểm tra lại thành công.
- Health/liveness của stack đã được xác nhận trên máy này; chưa phải bằng chứng
  tái lập trên máy thứ hai.
