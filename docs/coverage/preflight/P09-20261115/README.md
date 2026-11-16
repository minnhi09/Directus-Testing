# Trạng thái hiện tại — P09 COMPLETE, 15/11/2026

Sau khi người dùng thay key và giao thử lại, **license/entitlement đã hợp lệ, final preflight READY**. Xem [kết quả retry và lệnh tái lập/cleanup](license-retry/README.md), [report cuối](license-retry/preflight-ready.json), [license restoration](license-retry/license-restored.json). Seed/policy/actor đã kiểm trong namespace P09 riêng; chưa P10/campaign. Các báo cáo BLOCKED ở dưới là snapshot lịch sử.

Adapter an toàn hiện có: `python -B scripts/p09_runtime.py --namespace r06-k05-p09-20261115-audit01 --report runtime/profiles/r06-k05-p09-20261115-audit01/preflight-new.json` từ root DAMH, chọn tên output chưa tồn tại. Không dùng wrapper lab.sh/run-lab.ps1 hardcode lab cũ. Lab P09 đang giữ chạy, rollback/cleanup theo exact namespace và không --volumes; không còn created_resources=[] ở thời điểm hiện tại.

---

# Runtime resume — 15/11/2026

Engine hiện hoạt động; lab riêng namespace r06-k05-p09-20261115-audit01 đang healthy tại http://127.0.0.1:18055, Directus12.5.0. **BLOCKED_LICENSE** vì entitlement custom_permission_rules_enabled=false dù status active; chưa policy/seed. Credential mới nằm trong ignored runtime profile, không in/copy license cũ. Xem [runtime report](runtime-preflight-report.json) và [audit](runtime-audit.json). Runner help/version và tracecov0.25.2 đã kiểm; chưa campaign. Không chạy wrapper cũ vào lab này. Phần dưới giữ nguyên quy trình và snapshot lần engine chưa mở.

---

# P09 — Profile và quy trình tiếp tục

Profile: [compose.json](../../../../profiles/p09/compose.json), namespace dành riêng `r06-k05-p09-20261115-audit01`, loopback `http://127.0.0.1:18055`; DB không publish port. Ba named volume DB/uploads/extensions và network có prefix namespace, không dùng volume/mount của r06-k05 hoặc demo. Images pin đúng digest Directus12.5.0/PG16/Schemathesis4.30.0 theo manifest.

[Preflight report](preflight-report.json): **BLOCKED**, Linux engine npipe dockerDesktopLinuxEngine không truy cập được; Docker client29.7.2, Compose5.5.1. Config render exit0 dùng giá trị giả STATIC_ONLY trong temp file, không tạo env thật hay copy license. Test cách ly 4 PASS; không phải API PASS.

## Chạy lại bước đọc-only

```powershell
python -B scripts/p09_preflight.py --namespace r06-k05-p09-20261115-audit01
python -B -m unittest discover -s tests -p test_p09_preflight.py -v
```

Helper chỉ kiểm tĩnh/engine, **không tự start** và không coi engine có sẵn là lab READY. Exit2 khi runtime chưa được kiểm; không dùng exit2 như campaign FAIL. Nếu engine có lại, tiếp tục gate dưới đây trước up. Không chạy lab.sh up/seed/reset hoặc run-lab.ps1 với profile này: các wrapper đang cố định project r06-k05 và config/lab.env; LAB_RUNTIME_PROFILE chỉ đổi nơi artifact, không đổi project/network/volume.

## Gates khi Linux engine hoạt động

1. Xác định Docker context/Linux server; liệt kê containers/networks/volumes theo exact Compose project namespace. Nếu namespace đã tồn tại mà chưa chứng minh owner/labels/mounts đúng P09, dừng; không dùng namespace cũ/demo. Có quyền start lab thử, không có quyền reset hoặc dùng tài nguyên chung.
2. Kiểm 18055 còn trống; không probe API8055 chưa biết chủ sở hữu. Tạo credential **mới** trong ignored runtime/profiles/<namespace>/p09.env: P09_NAMESPACE, P09_DB_PASSWORD, P09_KEY, P09_SECRET (>=32 bytes), P09_ADMIN_PASSWORD; license hợp lệ chỉ cấp riêng ngoài report. Không copy env/license cũ hoặc dùng STATIC_ONLY làm runtime.
3. Dùng explicit compose file/project/env-file; kiểm config bằng --quiet, không in config đã interpolate secret. Chỉ pull các digest ở profile. Sau kiểm ownership mới up database/directus; lưu IDs/labels/mounts/image IDs/arch vào report sanitize, không lưu Config.Env.
4. Poll health với timeout hữu hạn, kiểm runtime version/image identity. Auth bootstrap dùng private credential mới; chỉ lưu actor ID/role, không token. License đọc entitlement custom_permission_rules_enabled theo helper hiện có scripts/lab-components.sh:509–520; thiếu entitlement => Reader policy/fixture BLOCKED, không sửa license/bypass.
5. Reuse fixture/oracle/helper định nghĩa hiện có bằng adapter project/env/runtime rõ ràng trước seed; wrapper cũ hiện không an toàn cho namespace mới. Không gọi nguyên lab.sh seed vào project cũ. Kiểm fixture map riêng, 3 category/12 article và policy published/field/write theo source, không hardcode ID hoặc coi historical PASS là hiện tại. Không chạy TC01–TC13/campaign trong P09.
6. Runner pinned có profile cli: chỉ chạy --version và run --help bằng compose run --rm --no-deps runner; không gửi request SUT. Đối chiếu --coverage-format/--coverage-report-json-path có trong help đúng image và nguồn tracecov package; hiện harness có dùng hai flag nhưng chưa chứng minh upstream/image hỗ trợ. Thiếu nguồn => schema keyword coverage NOT_MEASURED; không chặn thu operation evidence phù hợp ở phase sau.
7. Chỉ khi identity/URL/license/actor/policy/fixture/CLI gate có evidence thì bàn giao P10. Raw OAS lịch sử bất biến; chưa export OAS live trong lần BLOCKED này.

## Rollback/cleanup

Lần này created_resources=[]: không có gì để stop/delete, không thao tác lab cũ. Với lần start tương lai: ghi danh sách ID trước/sau; trước cleanup đối chiếu project label exact + damh.phase=P09 + namespace label + mount names. Chỉ stop/down với explicit file/project/env của namespace đã chứng minh; mặc định down không --volumes để giữ dữ liệu điều tra. Xóa volume chỉ sau khi có quyền cleanup, exact recorded IDs và xác nhận không thuộc lab cũ/demo. Không system prune, không xóa hàng loạt, không reset hoặc đổi port lab cũ. Restore/cleanup lỗi phải giữ FAIL/BLOCKED, không đổi business/contract verdict.

CI có thể dùng cùng profile với namespace duy nhất mỗi job, secrets riêng và loopback; chưa tạo/chạy remote CI. Dependency runtime/Reader license hiện BLOCKED; tracecov CHƯA XÁC MINH. Các trạng thái này không là N/A.
