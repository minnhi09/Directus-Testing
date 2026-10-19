# Phase 0 - Kiểm kê hiện trạng và giữ nền tảng R06 + K05

**Ngày kiểm kê:** 18/10/2026, Asia/Bangkok.  
**Kết quả:** Hoàn thành P0-01 đến P0-06 ở mức kiểm kê, chọn bằng chứng và lưu checkpoint tệp.  
**Giới hạn:** Không chạy lại test; không xác nhận lab đang healthy tại thời điểm kiểm kê. Không sửa harness, cấu hình, schema, dữ liệu hay dịch vụ; không commit/push/tag.

## 1. Kết luận để tiếp tục dự án

Nền tảng có bằng chứng đã chạy là baseline Directus 12.5.0 + PostgreSQL 16 + Schemathesis 4.30.0, fixture `r06-k05-v2`, profile Windows `windows-20261013-oig`. Các artifact được chọn chứng minh sáu scenario PASS, positive acceptance cho 10 operation, invariant 9 PASS/2 FAIL, pilot raw/guided ba seed và replay finding.

Đây là **baseline tham chiếu từ artifact lịch sử**, không phải baseline cuối kỳ đã nghiệm thu hoặc xác nhận hệ thống đang chạy ngày 18/10. Những gì cần ưu tiên giữ nguyên trước khi triển khai tiếp:

1. Bốn tệp đang sửa từ trước: README, lab.sh, invariants.py, lab-components.sh.
2. Schema/ID map theo runtime profile; schema Reader trước/sau OIG phải tách biệt.
3. Artifact gốc và trạng thái failure/incomplete; không thay bằng số liệu tổng hợp mới.
4. Helper Windows ngoài repo và cách gọi đúng Git Bash.
5. Những khác biệt giữa source checkout, source baseline và image runtime.

## 2. Những gì đã thực hiện trong Phase 0

| Task | Kết quả | Đầu ra/bằng chứng |
|---|---|---|
| P0-01 - Nguồn bằng chứng | Đã lập danh mục toàn bộ thư mục run và chọn bộ tham chiếu | [Evidence index](00-evidence-index.csv), [trích xuất 18 run](00-selected-evidence.json) |
| P0-02 - Phân loại đợt chạy | Đã tách fixture v1/v2, Windows trước/sau OIG, campaign dài, pilot và repair thủ công | Evidence index, [campaign theo seed](00-campaign-index.csv) |
| P0-03 - Trạng thái Git | Đã ghi branch/HEAD, modified/untracked, mode và phụ thuộc ngoài repo trước khi tạo đầu ra | [Git state trước Phase 0](tai-lieu-bo-tro/phase0-20261018/git-state-before.json) |
| P0-04 - Provenance | Đã đối chiếu image digest, SHA source/harness, schema hash và working tree | Mục 4-6; [schema inventory](00-schema-inventory.json) |
| P0-05 - Bộ demo | Đã chọn ba luồng và hai finding; có nguồn cho số liệu và lệnh dự kiến | [Bộ demo tham chiếu](00-bo-demo-tham-chieu.md) |
| P0-06 - Quyết định còn thiếu | Đã ghi câu hỏi, ảnh hưởng, nơi giải quyết và điều kiện không được suy diễn | [Decision backlog](00-quyet-dinh-va-phu-thuoc.md) |

Việc chọn evidence là kết quả rà soát kỹ thuật của AI trong phiên này, không phải xác nhận review của thành viên hay phê duyệt G1/baseline mới.

## 3. Phạm vi kiểm kê và cách đọc dữ liệu

### 3.1. Quy mô

| Nhóm dữ liệu | Số lượng | Ý nghĩa |
|---|---:|---|
| Thư mục dưới artifacts/runs | 302 | Gồm cả run thử interface, môi trường và repair thủ công |
| Có metadata.json đọc được | 301 | Không đồng nghĩa có đủ report hoặc test đạt |
| Metadata status=passed | 158 | Trạng thái lệnh; không phải số chức năng đúng hay tỷ lệ chất lượng |
| Metadata status=failed | 143 | Gồm test failure, môi trường, giới hạn và phép thử từ chối |
| Không có run metadata | 1 | `20261012T185232Z-fixture-encoding-repair`; có before/repair report, không nhập vào thống kê PASS/FAIL test |
| Dòng campaign theo seed trích được từ campaign-index | 37 | Chỉ các seed có trong index; không tự tạo thêm dòng cho run thiếu index |
| Run tham chiếu được chọn | 18 | Chức năng, schema, finding, pilot và campaign lịch sử |
| Tệp evidence gốc đã ghi SHA-256 | 177 | Chọn lọc; không phải hash toàn bộ log/HTTP/NDJSON |
| Snapshot schema actor đã kiểm tra | 12 | Bốn actor ở ba vị trí runtime |

[Tóm tắt máy đọc được](00-inventory-summary.json) giữ số lượng và giới hạn kiểm kê. Bốn run cũ dùng budget dạng văn bản thay vì JSON; cột `budget_raw` giữ nguyên chuỗi này, không coi đó là bằng chứng artifact hỏng và không tự suy ngân sách số khi không parse được.

### 3.2. Phân loại theo metadata

| Nhóm | Số thư mục | Cách sử dụng |
|---|---:|---|
| Fixture v1 lịch sử | 107 | Giữ lịch sử; không dùng thay bằng chứng Reader trên v2 |
| Fixture v2, không có runtime_profile | 130 | Bằng chứng nền cũ, trong đó có campaign dài; xem provenance từng run |
| Windows profile windows-20261013 | 9 | Giai đoạn trước OIG, không thay schema/policy sau OIG |
| Windows profile windows-20261013-oig | 25 | Nguồn chính cho bộ tham chiếu Windows |
| Interface/môi trường/fixture không xác định | 30 | Không gộp thành test nghiệp vụ |
| Repair thủ công không có metadata | 1 | Chỉ làm bằng chứng xử lý fixture |

Phân loại này dựa trường metadata và tài liệu hiện có, không suy license hiện tại từ tên profile. Nhóm v2 không có profile không tự động được coi là đã chạy trên Windows. Không cộng kết quả giữa các nhóm để tạo số defect hoặc một campaign duy nhất.

### 3.3. Các tệp dữ liệu bổ trợ

- [00-evidence-index.csv](00-evidence-index.csv): mỗi thư mục một dòng; command, provenance, budget, report hiện diện và vai trò tham chiếu.
- [00-campaign-index.csv](00-campaign-index.csv): profile/seed, stop reason, runner/restore, cases/check failures, file hiện diện và kiểm tra hash schema scoped.
- [00-selected-evidence.json](00-selected-evidence.json): trích trường cần thiết từ 18 run; không phải test run mới và không thay artifact gốc.
- [00-evidence-hashes.json](00-evidence-hashes.json): hash/size/đường dẫn tệp evidence chọn lọc để đối chiếu sau này.
- [00-schema-inventory.json](00-schema-inventory.json): hash và operation `/items/qa_*` trong các snapshot; không phải tổng số endpoint hệ thống Directus.

Không sao chép HTTP body, auth header, run.log hoặc NDJSON vào các bảng trích xuất. Run.log/NDJSON gốc vẫn cần giữ cục bộ và rà soát riêng trước khi chia sẻ. Artifact cũ chứa đường dẫn `/home/...`; evidence index dùng vị trí tương ứng đang tồn tại trong workspace này, không sửa provenance gốc.

## 4. Baseline và provenance

### 4.1. Git tại lúc bắt đầu

| Thành phần | Giá trị xác minh |
|---|---|
| Harness branch | `feat/g1-shared-interface` |
| Harness HEAD | `2e44fe7558cb4e3fc12e19b7d44af2421f81ed72` |
| Tệp tracked đã sửa từ trước | 4 |
| Tệp untracked trước đầu ra Phase 0 | 49 tệp riêng lẻ; git status mặc định có thể gộp thư mục |
| Staged changes tại lúc kiểm kê | Không có |
| Source Directus checkout hiện có | `8e140f94250834cea0a0fb6eb822cac39ed9faec`, working tree sạch |
| Source baseline ghi trong manifest | `4f77933bf9551cac6b289576078783e189b8f4e3`, đối tượng commit tồn tại trong repo local |
| Source được tài liệu Phần 1 khảo sát trước đây | `d3c9a8bb0c0096148c4740ce908e76c24f2413a0` |

Các SHA source trên khác nhau. Không suy từ việc đọc source checkout hiện tại rằng đã xác nhận root cause của image đang dùng. Không checkout/reset Directus trong Phase 0. Các run Windows được chọn ghi cùng harness HEAD nhưng `working_tree=dirty`: SHA một mình chưa mô tả đầy đủ mã đã thực thi; artifact cũ không có đầy đủ hash working tree để chứng minh nó giống từng byte với bản hiện tại.

### 4.2. Thay đổi đang cần giữ

| Tệp | Diff so với HEAD | Nội dung chính đã quan sát |
|---|---|---|
| README.md | +34/-0 | Hướng dẫn và provenance Windows |
| lab.sh | +39/-5 | Runtime profile, ACL Windows, NUL health, redaction license, metadata |
| scripts/invariants.py | +28/-3 | Query page=2 và search Unicode |
| scripts/lab-components.sh | +78/-13 | UTF-8 stdin, bind mount Windows, Hypothesis storage, coverage slurpfile, campaign guard |

Git còn báo mode `100755 → 100644` ở lab.sh và invariants.py. Đây là khác biệt đang có, chưa sửa. Khi bàn giao Linux cần xử lý executable bit hoặc tài liệu hóa cách gọi `bash lab.sh`; không khẳng định clone Linux hiện tại đã chạy được bằng `./lab.sh`.

Những tài liệu Phần 1/Phần 2, slide, báo cáo giữa kỳ, evidence Windows và kế hoạch mới có phần còn untracked. Chúng tồn tại trên máy này nhưng không mặc nhiên đi theo bản clone. Danh sách đầy đủ nằm trong git-state-before.json; không tự stage chúng hoặc đổi ignore trong Phase 0.

### 4.3. Image baseline tham chiếu

Đã đối chiếu chuỗi image trong metadata các run tham chiếu với manifest và env example; ba digest trùng nhau. Chưa inspect image đang chạy ở thời điểm hiện tại.

| Thành phần | Image và digest |
|---|---|
| Directus | `docker.io/directus/directus:12.5.0@sha256:7de5d6898b955dab1672619aed590035dcade4f8d7396d913e55543e114d1331` |
| PostgreSQL | `docker.io/library/postgres:16-alpine@sha256:721873c34ceb9f8d8fc265984940dc982404c105f19ad51be9fdc5970a6080ea` |
| Schemathesis | `docker.io/schemathesis/schemathesis:4.30.0@sha256:bb9cecfc9ac4058a15fcf9b505d9d9f972e2dde7c74c4e9289a35922f4cbc0a5` |

URL lab theo cấu hình/tài liệu: host `http://127.0.0.1:8055`, runner `http://directus:8055`, Compose project `r06-k05`. Profile chỉ tách tệp runtime, không cách ly database.

## 5. Fixture và schema cần bảo toàn

Map tham chiếu: `runtime/profiles/windows-20261013-oig/fixture-ids.json`, fixture `r06-k05-v2`, seed_run_id `20261012T191100Z-757`. Tệp có ba category và 12 article, tên fixture chia sáu draft/sáu published. Đây là nội dung map, chưa phải lần đọc DB mới.

SHA-256 của map tham chiếu: `df6a38444e4d8ea6bd2f9a4bdd31772d3889b6c06316d3cbea17902b51743673`.

| Actor | Operation `/items/qa_*` trong snapshot OIG | SHA-256 |
|---|---:|---|
| Admin | 14 | `993a95d245eedb6c7991bf646aac6f6ad3169f0a3c0846ea808d96d8203b017e` |
| Editor | 14 | `bd32aa69ff3e7330030c5f25e4c98fd1441a55c4b7465de25e3f42a4465a7d26` |
| Reader | 6 | `d7dc1393eb7e01514f0f8a4d3796ab71cf1f0fe70f5c8a3da5c0ae20259b47b8` |
| Anonymous | 0 | `2070c25c68193a4a42501935974bb3045697aceb1fe072bb3461f43c0a0342b3` |

Editor có thêm bulk operation trong schema; campaign chỉ chọn 10 operation. Anonymous có 0 operation của collection lab, không có nghĩa toàn bộ OpenAPI rỗng.

Schema Reader trước OIG ở `runtime/profiles/windows-20261013/` có 2 operation QA và hash `20fbfe9a517710ac73d05622f4b158bab4ccbcd96da51ec61363268ed92683cb`. Giữ snapshot đó riêng. Vị trí runtime gốc và profile OIG có schema actor trùng hash nhưng fixture map không cùng hash; không tráo map chỉ vì schema giống nhau.

Schema campaign scoped giữ hash riêng:

- Raw: `433cb61a51957e7852374f058b7c9ca79325e65ac898e1f071abfbe4afbe474e`.
- Guided: `cc4c888d4dcc65a225215f250853b1e0385b90b7bdcd235658df3e3b27fca831`.

Hash raw scoped khác schema Editor gốc là bình thường do đã scope operation. Guided còn thêm example/ID và dùng phase khác; không gọi chúng là cùng một đầu vào thí nghiệm.

## 6. Bộ bằng chứng được chọn

Các run ID dùng UTC; các run Windows dưới đây thuộc ngày 13/10 theo Asia/Bangkok. Ngày kiểm kê là 18/10, không phải ngày chạy lại.

| Mục đích | Run ID | Nguồn kết luận | Kết luận được phép |
|---|---|---|---|
| Doctor mới nhất tìm được | `20261013T040059Z-1536` | metadata.json | Lệnh doctor lịch sử passed, exit 0; không xác nhận health hiện tại |
| Up mới nhất tìm được | `20261013T035929Z-1688` | metadata.json | Up lịch sử passed, exit 0 |
| Seed sau campaign | `20261012T191100Z-757` | metadata.json và fixture map | Seed lịch sử passed, ID map ghi run này |
| Smoke mới nhất | `20261012T222250Z-1431` | metadata.json, contract-validation.json | Passed, exit 0; probe riêng score/status đều HTTP 400 |
| Schema actor | `20261012T185734Z-1667` | schema-manifest.json, snapshot hiện có | QA operation 14/14/6/0, hash đối chiếu được |
| Scenario mới nhất | `20261012T222311Z-1412` | scenario-report.json | S1-S6 passed |
| Invariant | `20261012T185934Z-1453` | invariant-report.json | 9 passed, 2 failed, 0 blocked; positive acceptance đủ 10 operation |
| Aggregate finding | `20261012T185942Z-1219` | invariant-report.json | Unknown shape 500, hai control 200; exit 1 |
| Contract finding | `20261012T185950Z-1994` | invariant-report.json, reproducer | Bốn biểu hiện schema candidate; exit 1, không quy thành bốn product defect |
| Raw pilot Windows | `20261012T185958Z-355` | campaign-index.json | Ba seed, 60 giây/10 examples; 10/10 operation mỗi seed; restore 0, runner 1 |
| Guided pilot Windows | `20261012T190350Z-1047` | campaign-index.json | Ba seed cùng budget; stateful trong cấu hình/summary; runner vẫn failed |
| Raw sau sửa inventory | `20261012T190820Z-1761` | campaign-index.json | Seed 101, 30 giây; generated 61, unique check failures 22 |
| Guided sau sửa inventory | `20261012T190912Z-1225` | campaign-index.json | Seed 101, 30 giây; generated 134, unique check failures 26 |
| Replay DELETE | `20261012T191034Z-777` | reproducer-schemathesis-j0ZjQ0.json | Single request, actual/source 204, reproduced, restore 0 |
| Raw dài 12/10 | `20261012T112746Z-20300` | campaign-index.json | Lịch sử 1.200 giây/100 examples, ba seed; max_time/failure, restore 0 |
| Guided dài 12/10 | `20261012T122826Z-22781` | campaign-index.json | Seed 202 interrupted, runner 130; không gọi cả profile hoàn tất |
| Raw v2 11/10 | `20261011T085034Z-76481` | campaign-index.json | Lịch sử harness khác; không gộp vào Windows |
| Guided v2 11/10 | `20261011T095117Z-89079` | campaign-index.json | Lịch sử harness khác; không gộp vào Windows |

### Số liệu pilot Windows dùng khi cần minh họa K05

| Profile/seed | Generated cases | Unique check failures | Operation tested | Runner | Restore | Kết thúc |
|---|---:|---:|---|---:|---:|---|
| Raw/101 | 270 | 36 | 10/10 | 1 | 0 | max_time |
| Raw/202 | 266 | 35 | 10/10 | 1 | 0 | max_time |
| Raw/303 | 270 | 40 | 10/10 | 1 | 0 | max_time |
| Guided/101 | 276 | 32 | 10/10 | 1 | 0 | max_time |
| Guided/202 | 279 | 36 | 10/10 | 1 | 0 | max_time |
| Guided/303 | 278 | 36 | 10/10 | 1 | 0 | max_time |

Không cộng unique check failures thành defect; không coi generated cases là số HTTP request. Các report/coverage/events/summary/inventory/metrics ở từng seed của bộ pilot được xác nhận có tệp; hash schema scoped cũng đã đối chiếu. Phase 0 chưa audit lại mọi event hoặc chứng minh full-chain cho mọi lỗi stateful.

## 7. Tình trạng runtime và khả năng demo hiện tại

Đã thử một truy vấn metadata chỉ đọc: `docker ps --filter label=com.docker.compose.project=r06-k05`. Kết quả: không đọc được Docker config của tài khoản host và không kết nối được named pipe docker_engine trong ngữ cảnh thực thi hiện tại.

Do đó, **chưa xác minh runtime ngày 18/10**. Không đủ căn cứ nói Docker trên máy người dùng đã dừng; cũng không đủ căn cứ dùng doctor ngày 13/10 để nói lab đang healthy. Không khởi động Docker, gọi up/down/reset, đọc secret hay seed/fuzz để xử lý trong Phase 0.

Bộ demo hiện sẵn sàng về evidence; live demo phải có preflight tại thời điểm trình bày. Nếu runtime chưa khả dụng thì dùng artifact đã chọn và nói rõ đó là kết quả lịch sử.

## 8. Checkpoint bảo toàn và giới hạn khôi phục

Checkpoint gốc được tạo **cục bộ ngoài repo DAMH**, trước khi cập nhật kế hoạch/tài liệu Phase 0. Các liên kết dưới đây trỏ tới bản sao đã được gom vào `HoanThanhPlan/tai-lieu-bo-tro/`; bản gốc tại `output/phase0-20261018/` vẫn được giữ nguyên:

- [checkpoint.zip](tai-lieu-bo-tro/phase0-20261018/checkpoint.zip): 99 tệp, gồm tệp tracked/nonignored phù hợp, schema/fixture map và helper Windows chọn lọc.
- [checkpoint-manifest.json](tai-lieu-bo-tro/phase0-20261018/checkpoint-manifest.json): hash/size của từng tệp và hash archive.
- [git-state-before.json](tai-lieu-bo-tro/phase0-20261018/git-state-before.json): Git state, diff summary và mode trước đầu ra Phase 0.

SHA-256 archive: `5ee3e1c64812f41610dd1065a451389d6e3cba604a23f706f27552ec55a02126`.

Archive không chứa `config/lab.env`, `.git`, `mnhy`, AGENTS local, kế hoạch triển khai local ở root, raw artifacts/runs hay database/volume. Schema có thể có ví dụ credential mặc định do OpenAPI sinh; đó không phải credential runtime. Các tệp text chọn cho archive đã kiểm tra mẫu JWT/Bearer dài/private key; đây không thay thế rà soát toàn bộ nội dung trước khi công bố.

Đây là checkpoint **tệp**, không phải commit/tag, database backup hay bảo đảm dựng lại độc lập toàn bộ lab. Artifact gốc vẫn cần giữ ở workspace và credential/license vẫn phải được cấu hình riêng khi dựng lại.

### Khi cần dùng checkpoint

1. Kiểm tra SHA-256 archive và manifest.
2. Giải nén sang thư mục mới, không đè checkout/DB đang dùng.
3. Đối chiếu tệp cần lấy với manifest và working tree hiện tại; chỉ chọn phục hồi những thay đổi đã hiểu.
4. Chạy preflight/test liên quan trong đợt triển khai được giao; không coi hash trùng là test PASS.

Không có thao tác restore nào được thực hiện trong Phase 0.

## 9. Điểm chuyển tiếp sang Phase 1

Phase 0 hoàn thành việc kiểm kê và bảo toàn tệp. Có thể bắt đầu Phase 1 bằng actor/fixture/scenario hiện có và [decision backlog](00-quyet-dinh-va-phu-thuoc.md). Những quyết định chưa chốt phải được giữ mở trong đặc tả, không biến thành yêu cầu đã phê duyệt.

Chưa xác nhận live readiness; chưa hoàn thành Phase 1-9; chưa nghiệm thu campaign cuối kỳ. Không sửa nhãn PASS/FAIL hoặc quyết định kỹ thuật cũ để đóng Phase 0.

### Tài liệu đối chiếu

- [Kế hoạch theo phase](Ke_hoach_hoan_thien_R06_K05_theo_phase.md).
- [Manifest baseline](../../manifest/baseline.yaml), [README](../../README.md).
- [Evidence Windows 13/10](../../evidence/windows-recheck-2026-10-13.md), [lần dựng Windows đầu](../../evidence/local-startup-2026-10-13.md).
- [Kết quả 12/10](../phan2/04-ket-qua-kiem-thu.md), [provenance Phần 1](../phan1/04-bao-cao-xac-minh.md).
- [Demo cũ](../demo.md), [test matrix](../test-matrix.md), [permissions](../permissions.md), [replay](../replay-cases.md).

Các tài liệu cũ giữ nguyên; những từ "mới nhất/cuối cùng" trong đó có giá trị tại mốc của tài liệu. Bảng ở mục 6 là lựa chọn tham chiếu của đợt kiểm kê này.
