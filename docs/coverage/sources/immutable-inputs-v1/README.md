# Input lịch sử bất biến cho P08

Archive này chứa đúng115input đã được M2-COVERAGE-20261116 và P15-HTTP-20261116-01 tham chiếu:113file nguồn Directus đọc bằng `git show` tại pin4f77933bf9551cac6b289576078783e189b8f4e3, manifest DAMH lịch sử và raw admin OAS lịch sử. Tổng960910byte; không phải bản sao toàn monorepo, không có credential/private env hoặc runtime execution mới.

[Index](index.json) ghi từng kind/path/revision/hash gốc và snapshot `<sha256>.txt`. File .txt giữ byte nguyên bản, kể cả nội dung JSON hoặc source code. Hash được đối chiếu với source_ref đã có trước khi snapshot, không lấy hash mới để sửa expected. Dữ liệu đã quét credential thực/mẫu token trước khi đưa vào archive; header/copyright nguồn giữ nguyên.

Mỗi bundle sử dụng archive có thêm sidecar `input-archive.json` pin hash của index. Resolver chỉ chọn snapshot khi **kind + path + revision + sha256** trùng khai báo, sau đó vẫn kiểm size/hash/pointer/line-range và source baseline. Không có sidecar thì giữ cơ chế nguồn gốc cũ; ref không có trong index không được tự chuyển sang snapshot. Snapshot/index bị sửa, path ngoài archive, revision sai, duplicate identity hoặc private-env ref đều failure.

Điều này giải sự phụ thuộc vào `manifest/baseline.yaml` đang phát triển, `runtime/schemas/.../admin.json` bị ignore và source object chỉ có ở máy tác giả. Manifest/bundle/report/raw schema gốc không bị viết lại. Raw OAS lịch sử không được dùng thay schema đúng actor của run mới. Không suy source-present thành runtime-enabled hoặc chuyển TC13 FAIL thành PASS.

Tái lập offline từ root DAMH:

```powershell
python -B scripts/coverage_offline.py validate docs/coverage/acceptance/M2-COVERAGE-20261116/bundle
python -B scripts/coverage_offline.py calculate docs/coverage/acceptance/P15-HTTP-20261116-01/bundle
python -B scripts/offline_suite.py
```

Không cần private profile, Docker, API hay checkout Directus để kiểm các ref đã archive. Muốn kiểm ref mới ngoài index vẫn cần input/source object tương ứng; thiếu phải failure/gap, không tự fetch/checkout. Các nguồn hiện hành và nguồn lịch sử là hai mốc riêng, không ghi đè manifest main để tái lập lịch sử.
