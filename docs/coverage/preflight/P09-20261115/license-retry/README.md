# P09 tiếp tục sau khi người dùng thay key — 15/11/2026

**P09 COMPLETE; runtime preflight READY. BLOCKED_LICENSE đã giải.** Chỉ hoàn thành chuẩn bị môi trường; chưa chạy P10, regression13, schema smoke, fuzz/campaign hoặc nghiệm thu G1/M2/M3. Coverage thực thi vẫn NOT_MEASURED; TC13 lịch sử business PASS/contract FAIL giữ nguyên.

## Nguyên nhân và cách khôi phục

[Điều tra trước](../license-investigation/README.md) xác định P09 chưa có grant: source=null, entitlement=false dù status active. Người dùng thay LICENSE_KEY trong config/lab.env và giao thử lại. Key mới khác key trong container lab cũ đang dừng; chỉ so sánh trong bộ nhớ, không xuất key/hash/token. Đã đưa key mới vào P09_LICENSE_KEY của private profile và recreate **chỉ Directus P09**, giữ DB/container/ba volume/network. Không copy grant/token hoặc project ID từ lab cũ.

[License restored](license-restored.json): preview HTTP200, compose up directus --no-deps --wait exit0, /license source=env, status=active, invalid_reason=null, effective custom_permission_rules_enabled=true. Project ID tồn tại trong DB P09 (SELECT duy nhất, không đọc token); không chỉnh bằng tay. Không thấy lỗi binding/invalid/refresh trong 300 dòng log hiện tại đã phân loại trong bộ nhớ. API /license không xuất project_id; null trong snapshot trung gian preflight-verified.json là field không được API cung cấp, không phải bằng chứng thiếu project. Không suy trạng thái binding hiện tại của lab cũ từ sự im lặng của log.

## Lab, actor và fixture

Namespace `r06-k05-p09-20261115-audit01`, host `http://127.0.0.1:18055`, runner `http://directus:8055`; Directus runtime 12.5.0 đúng digest. [Preflight cuối](preflight-ready.json) ghi IDs, mounts, 24 assertion preflight và method/path/status đã sanitize. DB không publish; volumes/network mang exact namespace và ownership labels P09. Lab cũ vẫn exited với StartedAt/FinishedAt từ tháng 10; không start/stop/exec/đọc DB/gọi API cũ.

[Adapter](../../../../../scripts/p09_runtime.py) kiểm image/health/storage/network/loopback/ownership trước seed, không dùng wrapper lab.sh hardcode project cũ. Nó truyền interface LAB_* sẵn có cho scripts/lab-components.sh seed; không sửa helper/oracle chung. Editor/Reader dùng password mới ngẫu nhiên trong ignored private profile. File HTTP trung gian và fixture map riêng ở runtime/profiles/<namespace>/; không đưa vào report công khai.

- Seed helper chạy hai lần exit0/0; fixture map hash giống nhau `83e653e22d9cddeea3a1cb4be6ce8fb9fdfd198eec068cf8132cf3e4d57f4fa2`. GET hiện tại xác nhận đúng 3 category, 12 article, 6 draft/6 published và map khớp ID động.
- Admin/Editor/Reader login được, ID riêng và active; admin effective policy có admin_access; Editor/Reader đúng role-policy, không admin/app access. Editor có đủ cấu hình CRUD hai collection và đọc đủ 12 article.
- Reader policy lọc published, không cho internal_notes, update fields=[] theo helper hiện hữu. Read-only probe thấy đúng 6 published, không internal_notes, đọc 3 category; anonymous đọc hai collection đều403. **Chưa chạy request kiểm ghi bị từ chối hoặc regression**; đó là kiểm chứng hành vi P10, không đổi policy để mở /users cho Reader.
- Field config có title max120, status draft/published, score0..5; category nullable và relation SET NULL. Đây là kiểm cấu hình, chưa là kiểm hành vi validation/delete relation.

Lần adapter đầu đã seed thành công nhưng verifier bị KeyError vì users/me của Editor/Reader chỉ trả ID. [Snapshot lỗi](runtime-report.json) giữ nguyên. Đã sửa verifier dùng self-ID rồi admin đọc role/status, giữ nguyên quyền actor. [Snapshot trung gian](preflight-verified.json) READY; snapshot cuối ở trên dùng code hiện tại. Không diễn giải lỗi công cụ thành license/SUT FAIL hoặc sửa report cũ.

## Lệnh tái lập và checks

Đứng tại repo DAMH. Probe runtime hiện tại (chọn **tên snapshot chưa tồn tại**; adapter từ chối ghi đè):

```powershell
python -B scripts/p09_runtime.py --namespace r06-k05-p09-20261115-audit01 --report runtime/profiles/r06-k05-p09-20261115-audit01/preflight-new.json
python -B -m unittest discover -s tests -p 'test_p09*.py' -v
```

Thêm --seed chỉ khi cần kiểm seed lặp trên đúng lab P09: adapter kiểm namespace/ownership rồi gọi helper seed hai lần; không reset hoặc migrate schema không tương thích. Không chạy lab.sh/run-lab.ps1 vào profile này. Probe cũ p09_preflight.py chỉ kiểm static/engine và vẫn trả pending authenticated gates; không thay snapshot READY đã kiểm đầy đủ.

Checks lần này: seed exit0/0; final authenticated preflight exit0; 10 unit isolation/ownership checks PASS; compose config --quiet exit0; git diff --check exit0. P08 validate baseline M1-REGRESSION-13-v1 được ghi exit thực trong audit. CLI evidence được tái dùng từ runner-version.txt/runner-help.txt/runner-packages.json ở thư mục cha cùng digest: Schemathesis4.30.0, tracecov/tracecov-community0.25.2, hai flag coverage có thật. Semantics/keyword coverage vẫn NOT_MEASURED, chưa chạy campaign để suy kết quả.

## DoD, cleanup và tiếp theo

Đã đạt định danh lab/actor, URL local, isolation, health/version/license/policy/fixture, CLI help, evidence sanitize và quy trình cleanup. Không còn blocker bắt buộc P09 trong subset regression13 P07 đã khóa nội bộ; các module tham khảo UNKNOWN không bị loại/N/A. Key/grant có thể thay đổi hiệu lực theo thời gian: phải preflight lại trước run tiếp theo.

Lab P09 giữ chạy để bàn giao; không cần rollback seed vì không có mutation probe tạm, chỉ fixture chuẩn. Khi được giao dừng: đối chiếu IDs/compose.project exact và labels damh.phase/damh.namespace của ba volume/network bằng adapter trước; sau đó dùng đúng namespace/private env/compose profile:

```powershell
docker compose --project-name r06-k05-p09-20261115-audit01 --env-file runtime/profiles/r06-k05-p09-20261115-audit01/p09.env --file profiles/p09/compose.json down
```

Mặc định không --volumes; không reset, prune hoặc xóa volume lab cũ/demo. Khi cần rollback cấu hình key P09 chỉ sửa private env P09 và recreate Directus cùng namespace, chấp nhận quay lại BLOCKED_LICENSE nếu entitlement không còn; không sửa/bypass Directus.

Bước được bàn giao: **P10** theo dependency P06 + P07 subset + P09, nối P02; đọc handoff P06/P07/P09 và selection trước. P10 cần adapter execution rõ target P09, selection run/execution mới, schema theo actor và kiểm hành vi; các việc này chưa được thực hiện trong P09. Không tự chuyển phase, commit/push hoặc giả nghiệm thu.
