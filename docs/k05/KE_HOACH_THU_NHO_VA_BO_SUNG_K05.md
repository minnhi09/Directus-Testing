# Kế hoạch thu nhỏ và bổ sung phạm vi K05 (Schema-Based API / Fuzz) cho Directus

**Ngày lập:** 23/11/2026 · **Đề tài:** R06 Directus + K05 · **Công cụ:** Schemathesis 4.30.0 · **Directus:** 12.5.0, commit `4f77933bf9551cac6b289576078783e189b8f4e3`

**Trạng thái tài liệu:** đề xuất kèm tiến độ thực tế. Mẫu số 30 operation và toàn bộ kế hoạch này do người dùng (người chịu trách nhiệm hoàn thành dự án kiểm thử) quyết định ngày 23/11/2026; người dùng xác nhận không cần Lành đồng ý. **Chưa có xác nhận của Lành** (`AGENTS.md` mục 2 có quy tắc yêu cầu việc đó cho thay đổi phạm vi operation và interface lệnh) và **chưa có xác nhận của giảng viên**.

---

## 1. Tóm tắt

Mục tiêu: chỉ giữ phần đúng với yêu cầu của `yeu_cau.pdf` (một kỹ thuật duy nhất là K05), bổ sung phần còn thiếu trong phạm vi K05, và chứng minh được rằng **mọi operation của OpenAPI trong lab đã được Schemathesis thực thi ở mọi actor có operation đó**.

Điều kế hoạch này **không** hứa: "Directus được kiểm thử 100%", "Directus không có lỗi" hay "100% code coverage". Schema coverage không phải coverage mã nguồn (`AGENTS.md` mục 6). Điều chứng minh được là **100% của một mẫu số hữu hạn đã định nghĩa rõ**, kèm bằng chứng và giới hạn công khai.

| Hạng mục | Trạng thái 23/11/2026 |
|---|---|
| Sao lưu `DAMH/` ra ngoài repo | Xong, đã kiểm zip |
| Mẫu số 62 cặp (actor, operation) | Xong (script + CSV) |
| Xóa 170 TC v2 | Xong |
| Xóa thí nghiệm pairwise 36/9 | Xong (giữ phần K05 của phase6) |
| Xóa khung coverage/CI, chuỗi P09/P10/P14, `docs/coverage`, hồ sơ nội bộ (nhóm A–D) | Xong 23/11 (xem mục 4.2) |
| Mở allowlist 30 operation, chạy Reader và Anonymous | **Chưa** |
| Chiến dịch chạy hết ngân sách, coverage tracecov, RCA lỗi 500 | **Chưa** |
| Việc quản lý nhóm theo PDF (board, đóng góp, peer evaluation, slide/demo) | **Chưa** |

---

## 2. Căn cứ: yêu cầu trong `yeu_cau.pdf`

PDF bị lỗi font khi trích xuất, nên các mục dưới đây là cấu trúc và ý chính, cần đối chiếu lại với bản gốc khi trích dẫn.

**Bắt buộc (theo PDF):**
- Chọn **một** kỹ thuật nâng cao (nhóm này: K05 Schema-Based API / Fuzz với Schemathesis), áp dụng vào hệ thống đã dựng ở Phần 1.
- Phần 1: phân tích cấu trúc, kiến trúc, luồng dữ liệu 3–5 nghiệp vụ; cài đặt chạy được; hướng dẫn cài đặt và seed.
- Phần 2: cơ sở lý thuyết, giới hạn, tiêu chí áp dụng; thiết kế test; automation; chạy, thu log/metrics; tìm defect **hoặc** chứng minh coverage; phân tích nguyên nhân.
- Đầu ra riêng của K05: **chạy schema tests, lưu reproducer, thống kê lỗi**.
- Báo cáo theo cấu trúc A–H, trong đó C cần ít nhất 3 luồng nghiệp vụ chạy được, H cần pin commit/tag và cách chạy lại trên máy mới.
- Quản lý nhóm: Git với lịch sử đóng góp đều, công cụ quản lý task, peer evaluation cuối kỳ.
- Khuyến nghị giới hạn scope; chỉ chạy trên lab local.

**PDF không yêu cầu:** số test case tối thiểu, CI/CD, kiểm thử toàn bộ Directus, sửa lỗi Directus, hay bắt buộc tìm được một số defect cụ thể.

**Nguồn ngoài PDF (chưa xác minh):** người dùng kể lại thầy nhận xét 13 test case là quá ít và muốn kiểm thử toàn bộ Directus có CI/CD. Kế hoạch này **bỏ qua** nhận xét đó theo chỉ đạo của người dùng (xem mục 8 về cách xử lý nếu nhận xét vẫn còn hiệu lực).

---

## 3. Định nghĩa "100%" (mẫu số)

### 3.1. Mẫu số đã duyệt

Mẫu số là **mọi operation có trong OpenAPI của lab, theo schema của từng actor không phải admin**. Admin không thuộc mẫu số vì không phải tài khoản fuzz và `AGENTS.md` loại việc quét API quản trị.

| Actor | Số operation trong schema |
|---|---:|
| Editor | 30 |
| Reader | 22 |
| Anonymous | 10 |
| **Cặp (actor, operation)** | **62** |
| **Operation duy nhất** | **30** |

Phân loại 30 operation duy nhất: 10 operation của chiến dịch chính cũ (CRUD hai collection `qa_articles`, `qa_categories`), 4 bulk (`PATCH` và `DELETE` trên list), 16 operation thêm (assets 1, auth 7, server 2, utils 6).

Danh sách đầy đủ: [mau-so-30-operation.csv](mau-so-30-operation.csv); tóm tắt và hash schema: [mau-so-30-operation.summary.json](mau-so-30-operation.summary.json). Sinh bằng `scripts/build_k05_denominator.py` từ ba file schema theo actor.

**Nguồn schema (cập nhật 23/11/2026, WP1 xong):** đã export lại từ lab đã pin (Directus 12.5.0, commit `4f77933…`, run `20261123T111625Z-311`). Hash **trùng hoàn toàn** bản export ngày 11/10/2026: Editor `bd32aa69…a7d26`, Reader `d7dc1393…b47b8`, Anonymous `2070c25c…342b3`, Admin `993a95d2…b017e`. Mẫu số giữ nguyên 62 cặp / 30 operation. Bản sao schema mới: `runtime/schemas/r06-k05-v2-20261123/` (thư mục `runtime/` bị Git bỏ qua).

### 3.2. Sáu tiêu chí để được nói "100% mẫu số"

| # | Tiêu chí | Cách chứng minh |
|---|---|---|
| C1 | 62/62 cặp (actor, operation) có ít nhất một request đã tới API và có phản hồi được ghi lại | Bảng kết quả theo cặp, trỏ tới NDJSON của run |
| C2 | 10 operation CRUD (Editor) có ít nhất một ca thành công hợp lệ (2xx); các operation khác có ít nhất một request hợp lệ theo schema tới được handler | Cột "ca thành công hợp lệ" trong bảng C1 |
| C3 | Cả 18 run (3 actor × raw/guided × 3 seed) kết thúc hoàn tất, không dừng vì `max_time` hay bị ngắt | `campaign-summary.json` của từng run; nếu không đạt thì **bỏ C3 và nói rõ** |
| C4 | Restore dữ liệu về baseline sau mỗi run đạt | Mã thoát restore của từng run |
| C5 | Mọi failure đều được gom nhóm, phân loại (lỗi sản phẩm / schema / harness / môi trường / chưa kết luận), mỗi nhóm có ít nhất một reproducer | Bảng thống kê lỗi (WP7) |
| C6 | Coverage tracecov (tham số, từ khóa, phản hồi, example) báo đúng số đo, kèm danh sách phần không tới được | File coverage từng run; thiếu công cụ thì ghi `NOT_MEASURED` |

### 3.3. Cảnh báo quan trọng về con số

Coverage theo operation có thể đạt 100%, nhưng coverage theo nội dung schema **không thể ép lên 100%**. Số liệu lịch sử cho thấy khoảng cách này: với chiến dịch raw seed 101 (run `20261011T085034Z-76481`, nguồn `historical-raw-guided.csv`), tham số đạt 58,3%, từ khóa 29,6%, phản hồi 30,8%, example 75%. Báo cáo phải trình bày hai loại số này **riêng**, không gộp thành một con số "100%".

### 3.4. Câu khẳng định được phép và không được phép

**Được phép:**
- "62/62 cặp (actor, operation) trong OpenAPI lab đã được Schemathesis thực thi với 3 seed, ở cả raw và guided."
- "Mọi failure được phân loại; số check fail không bằng số defect."
- "Coverage tham số/từ khóa/phản hồi/example là X%, Y%, Z%, W% (đo bằng tracecov)" — chỉ khi đo được.

**Không được phép:**
- "Directus được kiểm thử 100%" hoặc "không có lỗi".
- "100% coverage" không kèm mẫu số.
- Gộp số request, số check fail và số defect thành một con số.
- Nêu C3 (chạy hết) nếu run nào còn `max_time`.

---

## 4. Phần xóa: những gì ngoài phạm vi K05

Nguyên tắc: bản sao lưu ngoài repo đã có; xóa theo nhóm, mỗi nhóm gỡ phụ thuộc trước, chạy `python -m unittest discover -s tests -p "test_*.py"` sau mỗi nhóm; không xóa phần dùng chung khi chưa kiểm tra.

**Bản sao lưu:** `D:\DAMH-full-recovery-2026-10-12\backup-DAMH-truoc-thu-nho-K05-20261123.zip`, 243 MB, 69.558 file (gồm cả `.git`), SHA-256 `400b34ccf5302eff9693fa898a170ba19681ac73c16dc7a574cd9a4d8fab1bbf`. Chứa `config/lab.env` có mật khẩu lab: giữ trên máy, không gửi đi.

### 4.1. Đã xóa

| Nhóm | Nội dung | Gỡ phụ thuộc |
|---|---|---|
| 170 TC v2 (G0–G10) | `catalog_v2_g1…g9.py`, `build_catalog_v2.py`, `admin_cases.py`, `test-catalog-v2.json`, `tests/test_admin_cases.py`, `docs/coverage/catalog-v2/`, 37 thư mục `artifacts/runs/step4…step9*` | Gỡ nhánh `--v2` khỏi `designed_cases.py` |
| Pairwise 36/9 (K06) | `cost_query.py`, `tests/test_cost_query.py`, `query-cost-model-v1.json`, `query-cost-protocol-v1.json`, `03-query-exhaustive-36.csv`, `03-query-pairwise.csv`, `06-toi-uu-chi-phi.md`, 6 run `p6-query-*`; trong phase6: 5 file thuộc thí nghiệm và 6 thư mục `evidence/p6-query-*` | Gỡ lệnh `cost-query` khỏi `lab.sh`, `lab-components.sh`, `check_offline.py`, README |

Kiểm tra sau xóa: 136 unit test đạt.

### 4.2. Nhóm A–D: đã xóa ngày 23/11/2026

**Cập nhật tiến độ:** cả bốn nhóm dưới đây đã xóa theo từng lệnh của người dùng; bộ test còn lại (18 test) đạt, cú pháp `lab.sh` và `lab-components.sh` hợp lệ. Bảng bên dưới giữ nguyên nội dung kế hoạch ban đầu. Khác với kế hoạch:

- **Xóa thêm vì phụ thuộc:** `tests/test_http_contract_metadata.py` (import `check_scenario_contracts`, nhóm B); `scripts/coverage_schema.ps1`, `scripts/check_coverage_examples.ps1`, `scripts/scenario_trace.py`, `tests/test_scenario_trace.py` (mồ côi sau nhóm A–C); `scripts/build_rest_denominator.py` và `tests/test_rest_denominator.py` (mất dữ liệu đầu vào khi xóa `docs/coverage/inventory`). Trong `test_scenario_trace.py` đã bỏ một test đọc `coverage_offline` trước khi xóa cả file ở nhóm C.
- **Nhóm C giữ lại `docs/coverage/oracles/`** (3 file) vì `oracle_v2.py` còn ghi ra đây (mục 4.4).
- **Bằng chứng 13 TC đã trích** 34 file (208 KB) sang [bang-chung-13-tc/](bang-chung-13-tc/README.md) trước khi xóa `docs/coverage`; hash từng file đã đối chiếu với bản gốc.
- **Nhóm D:** 5 tài liệu đã xóa. Các quyết định nội bộ ghi trong `KE_HOACH_RUT_GON_R06_K05.md` và `KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md` (người duyệt, ngày duyệt, lý do rút gọn) chỉ còn trong bản sao lưu và lịch sử Git.

**Còn sót, chưa xử lý:**
- `scripts/lab-components.sh` còn hàm `p10_scenarios` và lệnh `p10-scenarios` (chỉ chạy được trong project `r06-k05-p09-*`, đã mồ côi); có thể còn mã pilot P14. Là file dùng chung, cần Lành đồng ý trước khi gỡ.
- Thư mục `.github/workflows/` rỗng (không còn workflow nào).
- Tài liệu còn trỏ tới file đã xóa: `docs/coverage/oracles/ORACLE-V2-20261121/README.md`, `evidence/progress-2026-11-15.md`, `docs/k05/bang-chung-13-tc/chon-13-tc/README.md` (bản sao nguyên văn, không sửa), và các báo cáo trong `docs/HoanThanhPlan/` (sửa trong WP8).

**Nội dung kế hoạch ban đầu của bốn nhóm:**

| Nhóm | Nội dung | Phụ thuộc cần xử lý |
|---|---|---|
| **A. Khung coverage/CI nhóm tự đặt** | `coverage_offline.py`, `check_offline.py`, `offline_suite.py`, `ci_m2.py`; `tests/test_coverage_archive.py`, `test_coverage_offline.py`, `test_coverage_scoped_assertions.py`, `test_ci_m2.py`, `test_offline_suite_gate.py`; `tests/fixtures/coverage-offline/`; `docs/CI_M2.md`, `docs/CI_STATIC_OFFLINE.md`; `.github/workflows/static-offline.yml` | `check_offline.py` do `coverage_offline.py` gọi, xóa cùng nhau. Không file nào được `lab.sh` gọi |
| **B. Chuỗi P09/P10/P14** | `p09_preflight.py`, `p09_runtime.py`, `p10_regression.py`, `p10_selection.py`, `p14_pilot.py`, `capture_scenario_http.py`, `check_scenario_contracts.py`; `tests/test_p09_*.py`, `test_p10_*.py`, `test_p14_pilot.py`; `.github/workflows/p10-integration-preflight.yml` | Chạy `grep` phụ thuộc trước. `designed_cases.py` (do `lab-components.sh` gọi) và `contract_checks.py` (do `designed_cases.py`, `replay_cases.py` dùng) **giữ**. `scenario_trace.py` chỉ còn dùng trong `capture_scenario_http.py` và `ci_m2.py`: xem xét cùng nhóm |
| **C. `docs/coverage/**`** | Toàn bộ khung M1/M2/M3, Verified Coverage, handoff P00–P19 | **Trước khi xóa phải trích riêng bằng chứng 13 TC** (run P10 ngày 16/11: 12 PASS, 1 FAIL, TC13 contract FAIL và RCA) sang một thư mục nhỏ để báo cáo trích dẫn |
| **D. Hồ sơ nội bộ và script mẫu số cũ** | `docs/RA_SOAT_20_PHASE_R06_K05_2026-11-15.md`, `docs/DANH_SACH_LO_COMMIT_2026-11-21.md`, `docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md`, `docs/KE_HOACH_RUT_GON_R06_K05.md`; `scripts/build_rest_denominator.py`, `tests/test_rest_denominator.py` | `build_rest_denominator.py` lập mẫu số cho cả hệ thống (269 route, nhóm G1–G10) của bộ v2, **không** dùng lại cho mẫu số K05 |

### 4.3. Giữ có chủ đích

| Phần | Lý do |
|---|---|
| Phase6: `historical-raw-guided.csv`, các file kiểm định lần chạy, `replay-comparison.json`, `evidence/` của 4 campaign và replay `qfqspn` | Số liệu K05, gồm bảng coverage tracecov |
| 13 TC (S1–S6 và 7 case từ catalog v1), 11 invariant | Oracle và demo ba luồng cho K05 |
| `designed_cases.py`, `invariants.py`, `replay_cases.py`, `contract_checks.py`, `lab.sh`, `lab-components.sh`, `run-lab.ps1` | Đường chạy chính |
| `docs/phan1`, `docs/phan2`, `docs/HoanThanhPlan` (phần báo cáo), `manifest/`, `compose.yaml` | Phần 1, 2 và pin phiên bản |
| `artifacts/runs/p8-20261018-query-full`, `query-extra` | Bằng chứng cho `08-ket-qua-case.csv` |

### 4.4. Chờ quyết định

| Phần | Vấn đề |
|---|---|
| Catalog v1 (257 ID) và `06-ket-qua-case.csv`, `08-ket-qua-case.csv` | Là thiết kế tay (biên, phân vùng, pairwise), không phải K05. Đề xuất: giữ làm phụ lục, **không** nêu 257 là số test case. Trong đó có 36 ca `pairwise-reference` (kỹ thuật K06) |
| `oracle_v2.py`, `tests/test_oracle_v2.py`, `docs/coverage/oracles/ORACLE-V2-20261121/`, `artifacts/runs/step1…step3*` | **Không** thuộc 170 TC v2: là oracle cho 66 ca của catalog v1. Giữ cho tới khi quyết định vai trò của catalog 257 |
| Phần còn lại của phase6 (`analyze.py`, `validate.py`, `source-*`, `evidence-index.json`) | Lẫn cả phần pairwise đã xóa; `evidence-index.json` còn liệt kê file đã xóa với hash cũ |

**Trạng thái (24/11/2026):** catalog 257 được giữ làm phụ lục PL.1 của báo cáo cuối kỳ, ghi rõ chưa chạy và không nêu là số test case. Hai dòng còn lại (`oracle_v2.py` và các file còn lại của phase6) vẫn được giữ nguyên, **chưa quyết định xóa**; việc xóa cần lệnh của người dùng.

### 4.5. Việc dọn tham chiếu sau khi xóa

Nhiều tài liệu còn nhắc file đã xóa: `09-bao-cao-cuoi-ky.md`, `BAO_CAO_CUOI_KY_R06_K05_HOAN_CHINH.md`, `08-bao-cao-nghiem-thu.md`, `README.md` của `HoanThanhPlan`, `docs/KE_HOACH_RUT_GON_R06_K05.md` (nhắc `admin_cases.py`). Sửa trong bước viết lại báo cáo (WP8), không sửa lẻ.

---

## 5. Phần thêm: những gì còn thiếu trong phạm vi K05

Ký hiệu: **[Lành]** = việc mà `AGENTS.md` mục 2 yêu cầu Lành đồng ý (thay đổi interface, operation scope). Ngày 23/11/2026 người dùng quyết định không cần xác nhận này và chịu trách nhiệm; ký hiệu giữ lại để biết đó là thay đổi trên phần dùng chung.

### WP1. Chốt mẫu số bằng schema đã export lại

- Khởi động lab đã pin, seed, export `GET /server/specs/oas` cho Editor, Reader, Anonymous (không dùng schema admin thay thế).
- Chạy lại `scripts/build_k05_denominator.py --schema-dir <thư mục mới>`; so hash với bản 11/10. Nếu số operation khác 62/30 thì cập nhật mẫu số và ghi lý do.
- **DoD:** CSV mới có hash schema của lab đã pin; ghi rõ ngày export và commit/digest.

### WP2. Mở allowlist lên 30 operation và hỗ trợ chọn actor **[Lành]**

- Hiện `lab.sh` mặc định actor Editor (`LAB_ACTOR` → `editor`) và allowlist 10 operation. Cần cho `test raw` và `test guided` nhận actor (`editor`, `reader`, `anonymous`) và đọc allowlist từ CSV mẫu số.
- Không nới check, không thêm skip/xfail; kiểm URL, actor và đúng project DB trước chạy (`AGENTS.md` mục 5).
- **DoD:** chạy được `raw` và `guided` cho từng actor; metadata run ghi đúng actor và schema hash.

**Tiến độ WP2 (23/11/2026): code và kiểm tra xong; thực hiện theo quyết định của người dùng, không có xác nhận của Lành.**

Cách dùng (qua `scripts/run-lab.ps1` trên Windows, hoặc `lab.sh` nếu máy có `jq`):

```
LAB_ACTOR=editor|reader|anonymous  LAB_CAMPAIGN_SCOPE=main10|full  ./lab.sh test raw|guided
```

Mặc định (không đặt biến) vẫn là Editor + `main10` = hành vi cũ. Reader và Anonymous chỉ chạy với `full`. Anonymous không gửi header `Authorization`. Admin không phải actor fuzz.

Thay đổi trong `lab.sh` và `scripts/lab-components.sh`:
- Chọn actor và phạm vi; `full` lấy mọi operation trong schema của actor, đối chiếu số lượng với `docs/k05/mau-so-30-operation.csv` (lệch thì dừng, không chạy).
- Overlay guided chỉ gắn example vào operation **có trong schema** (bản cũ gán thẳng vào `delete`/`post`, nên với Reader hay Anonymous sẽ tạo operation không có thật) và có bước kiểm tra tập operation của schema sau overlay đúng bằng tập mục tiêu.
- Báo cáo campaign ghi thêm `actor`, `scope`, `operation_count`.

Kiểm tra offline: với Editor + `main10`, schema raw và guided mới **giống hệt từng byte** schema do bộ lọc cũ sinh ra; với `full`, số operation đúng 30/22/10 và overlay không đổi tập operation. 18 unit test vẫn đạt.

Chạy thử trên lab local (chỉ để kiểm tra đường chạy: seed 101, `max-examples=2`, 60–120 giây, đều dừng ở `max_time`; **không phải kết quả campaign**, không dùng làm số liệu báo cáo):

| Actor / phạm vi / profile | Operation | Case sinh ra | Failure duy nhất | Restore | Run |
|---|---:|---:|---:|---|---|
| Anonymous / full / raw | 10/10 | 32 | 21 | PASS | `20261123T114647Z-1766` |
| Reader / full / raw | 22/22 | 90 | 46 | PASS | `20261123T114933Z-1943` |
| Editor / main10 / raw (mặc định cũ) | 10/10 | 58 | 20 | PASS | `20261123T115137Z-626` |
| Editor / full / raw | 30/30 | 135 | 65 | PASS | `20261123T115307Z-453` |
| Editor / full / guided | 30/30 | 548 | 78 (2 lỗi chạy) | PASS | `20261123T115530Z-377` |

Sau cả 5 lần chạy, fixture vẫn đúng baseline (3 category, 12 article: 6 draft, 6 published). Với Anonymous, không có dòng nào trong NDJSON chứa chuỗi `Authorization`.

**Quan sát để triage ở WP7 (chưa kết luận):** nhiều operation `auth` trả lỗi xác thực khi fuzz (dự kiến); Editor guided có 1 lỗi server (5xx) chưa xác định operation.

*Đính chính (WP3):* bản đầu của đoạn này ghi `GET /utils/random/string` trả `ROUTE_NOT_FOUND`. Sai: phản hồi 404 đó là của request thăm dò `TRACE` (kiểm tra phương thức không hỗ trợ); `GET` trả 200.

### WP3. Overlay guided cho operation cần dữ liệu

Giữ schema gốc bất biến; overlay tách riêng, có lý do và diff (`AGENTS.md` mục 5).

| Operation | Dữ liệu cần |
|---|---|
| `GET /assets/{id}` | File đã upload và ID thật |
| `POST /utils/import`, `/utils/import/{collection}` | File JSON hợp lệ |
| `POST /utils/export/{collection}`, `/utils/sort/{collection}` | Collection hợp lệ có dữ liệu |
| `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/password/*` | Tài khoản test và thông tin đăng nhập qua biến môi trường |
| `/auth/oauth*` | Chưa có provider cấu hình: ghi nhận kết quả thực tế, không giả lập |

- **DoD:** mỗi operation có ít nhất một request hợp lệ tới được handler, hoặc có giải thích kỹ thuật vì sao không thể (ví dụ phụ thuộc email/provider chưa cấu hình), ghi vào bảng C2.

**Tiến độ WP3: xong.** Overlay và công cụ đo xong ngày 23/11/2026; bảng C2 chính thức là bảng 62 cặp của chiến dịch đầy đủ (24/11/2026): [wp5/bang-phan-hoi-theo-cap.csv](wp5/bang-phan-hoi-theo-cap.csv) và [wp5/README.md](wp5/README.md), mục 5. 10/10 operation CRUD của Editor có 2xx; mọi cặp còn lại có request tới được handler hoặc tầng xác thực/phân quyền, và các cặp không có 2xx đều có lý do ghi nhận.

*Đã làm* (trong `scripts/lab-components.sh`, chỉ khi `LAB_CAMPAIGN_SCOPE=full` và profile guided; Editor + `main10` vẫn giống hệt từng byte bản cũ, đã kiểm lại):
- Example cho tham số `collection` (`qa_articles`/`qa_categories`) của `utils/export`, `utils/import`, `utils/sort`; body mẫu cho `export` và `sort`; ID UUID đúng định dạng cho `assets/{id}`; body mẫu cho PATCH hàng loạt (mảng item có ID fixture).
- Body `auth` (login, refresh, logout, password request/reset) dùng **giá trị bịa, không tồn tại** (`k05-probe@example.com`, mật khẩu/token giả), nên không có credential thật trong artifact. Example đặt ở **cấp property** vì Schemathesis ưu tiên example cấp property của schema Directus hơn example cấp media-type (kiểm chứng: `POST /auth/login` với body mẫu từ schema gốc bị 400, với giá trị bịa trả 401).
- Overlay chỉ thêm `example` vào operation đã có trong schema của actor; guard của WP2 vẫn kiểm tập operation không đổi.
- `scripts/k05_reach_report.py`: dựng bảng C1/C2 theo từng cặp (actor, operation) từ NDJSON của các run, ghép với file mẫu số. Chỉ đếm phản hồi của request cùng phương thức với operation (loại các phép thăm dò `TRACE`...); gán nhãn `SUCCESS_2XX`, `DENIED_401_403`, `REJECTED_4XX`, `SERVER_ERROR`, `NO_RESPONSE`, `NOT_EXECUTED` (nhãn mô tả, không phải kết luận đúng/sai của Directus).

*Kết quả chạy thử* (các run ngắn, `max-examples=2`, 120 giây; **chỉ để kiểm tra overlay, không phải số liệu campaign**): trước overlay (4 run, lẫn raw và guided) 31/62 cặp có 2xx; sau overlay (3 run guided) 33/62. Hai tập run không hoàn toàn so sánh được, nên chỉ dùng để thấy hướng thay đổi. `utils/export` chuyển từ 403 sang 2xx (Editor và Reader); `utils/sort` chuyển từ 403 sang 400 (tới được bước kiểm tra của handler); `auth/login` từ 400 (sai payload) sang 401 (tới bước xác thực). Cả 62 cặp đều có request và phản hồi.

*Các operation chưa có 2xx và lý do ghi nhận được* (từ các run ngắn; bảng chính thức đã lập lại ở WP5 và phân loại ở WP7):

| Operation | Phản hồi | Lý do |
|---|---|---|
| `GET /assets/{id}` | 403 | Fixture không cấp quyền đọc file cho actor nào; admin không phải actor fuzz |
| `POST /auth/login` | 401 | Dùng tài khoản bịa để không đưa credential vào artifact; đăng nhập thành công do harness thực hiện mỗi lần chạy (`http-*.json`) |
| `POST /auth/refresh` | 401 | Cần refresh token thật; dùng token bịa |
| `POST /auth/password/reset` | 403 | Cần token reset gửi qua email; lab không cấu hình email |
| `GET /auth/oauth`, `/auth/oauth/{provider}` | 404 | Lab không cấu hình provider OAuth |
| `DELETE /items/qa_articles`, `/items/qa_categories` (hàng loạt) | 400 | Schema không mô tả `requestBody` cho DELETE hàng loạt nên không có body để gửi (đã phân loại ở WP7: lỗi schema, nhóm RC10; thêm body vào schema là đổi hợp đồng nên không làm trong overlay) |
| `POST /utils/cache/clear` | 403 | Chỉ admin dùng được |
| `POST /utils/import`, `/utils/import/{collection}` | 400/415/403 | Cần phần file multipart; overlay không biểu diễn được nội dung file nhị phân |
| `POST /utils/sort/{collection}` | 400 | Chưa xác định nguyên nhân (nghi collection mẫu không có trường sắp xếp; chưa kiểm chứng) |
| `PATCH /items/qa_articles/{id}` (Reader) | 403 | Đúng thiết kế: Reader không được ghi (scenario S6) |

*Quan sát để triage ở WP7 (chưa kết luận):* (1) `GET /items/qa_categories` và `GET /items/qa_articles` trả HTTP 500 nhiều lần trong pha stateful của các run guided (Editor: 106 tương tác 500 ở `GET /items/qa_categories`; Reader: 126 và 6 ở hai operation list); đây là số tương tác, **không phải số defect**. (2) `POST /auth/login` với body hợp lệ theo schema (trường `otp` là chuỗi rỗng) bị 400 `INVALID_PAYLOAD` vì Directus không chấp nhận `otp` rỗng; schema không có ràng buộc `minLength` (ứng viên chênh lệch schema và triển khai).

### WP4. Xử lý thao tác có tác dụng phụ

- `auth/logout`, `auth/refresh`, `utils/cache/clear`, `utils/import`: kiểm xem token tĩnh của actor có bị ảnh hưởng không (chưa xác minh), dùng tài khoản/token riêng cho nhóm này, restore sau mỗi seed, không reset giữa các bước của chuỗi stateful.
- **DoD:** chạy nhóm này không làm hỏng token của các run khác; restore PASS.

**Tiến độ WP4 (23/11/2026): xong.** Chi tiết, bằng chứng và giới hạn: [wp4/README.md](wp4/README.md).

- **Token không bị hỏng:** `auth/logout` (giả hoặc thật) chỉ vô hiệu refresh token tương ứng; access token vẫn dùng được. `utils/cache/clear` bị chặn (403) với mọi actor không phải admin.
- **Rủi ro tìm được:** 30 lần đăng nhập sai làm người dùng bị `suspended`, và email admin của lab trùng email mẫu trong OpenAPI của Directus nên profile raw có thể làm admin bị tạm ngưng. Không đổi cấu hình Directus; thay vào đó thêm bảo vệ.
- **Bảo vệ trong `lab-components.sh`:** chụp trạng thái 21 nhóm ngoài `qa_*` trước và sau mỗi seed; tự đặt lại trạng thái tài khoản lab (API, hoặc SQL nếu admin không đăng nhập được); tự xóa thông báo do `utils/export` tạo; mọi thay đổi khác thì báo cáo, đánh dấu seed thất bại và dừng các seed sau.
- **Kiểm chứng:** ba vòng đối chứng âm (chen role lạ và tạm ngưng reader giữa chừng) và hai run sạch (Editor 30 operation, Reader 22 operation) đều ra kết quả đúng sau khi sửa hai lỗi của chính bộ kiểm tra tìm thấy lúc thử. Phát hiện thêm: mỗi lần `POST /utils/export/{collection}` tạo một dòng trong `directus_notifications`.
- Còn mở: ngưỡng khóa đăng nhập chính xác, `utils/import` ngoài `qa_categories`, và các thay đổi mức DB không đi qua API.

### WP5. Chiến dịch đầy đủ, chạy hết ngân sách

- Ma trận: 3 actor × {raw, guided} × seed 101, 202, 303 = **18 run**. Mặc định `AGENTS.md`: một worker, ~5 req/s, timeout 10 giây, 100 ví dụ fuzz/operation. Các run cũ đều dừng ở `max_time` (20 phút), nên cần đo thời gian thực của 30 operation bằng một pilot nhỏ rồi đặt ngân sách đủ để hoàn tất. Mọi thay đổi ngân sách phải ghi lại.
- Chạy tuần tự, không chạy hai suite ghi/xóa song song trên cùng DB.
- **DoD:** C3 và C4 (xem 3.2). Nếu run nào vẫn `max_time` thì ghi `INCOMPLETE_BUDGET` và loại C3 khỏi câu khẳng định.

**Tiến độ WP5 (24/11/2026): xong.** Chi tiết, bảng 18 run và bảng 62 cặp: [wp5/README.md](wp5/README.md).

- **18/18 seed hoàn tất thật** (C3, C4 đạt); 62/62 cặp có phản hồi (C1); 10/10 operation CRUD của Editor có 2xx (phần CRUD của C2). Tổng thời gian khoảng 1,8 giờ. C6 được đo ở WP6 và C5 được đóng ở WP7.
- **Đính chính quan trọng:** `--max-time` của Schemathesis làm fuzzing và stateful lặp lại cho đến hết giờ (trợ giúp CLI 4.30), nên mọi campaign cũ dừng ở `max_time` **không phải** là chưa hoàn tất. Pilot: 2.254 vòng fuzzing 0,8 giây và chỉ 140 case trong 1.800 giây; bỏ `--max-time` thì xong trong 27 giây với cùng 66 failure. Vì vậy chạy bằng `LAB_MAX_TIME=0` (mỗi pha một lượt) kèm trần cứng `LAB_HARD_TIMEOUT`; báo cáo cuối kỳ cần sửa mọi chỗ gọi `max_time` là `INCOMPLETE_BUDGET`.
- Phát hiện khi diễn giải: Reader nhận 200/204 trên `PATCH /items/qa_articles/{id}` với request rỗng vì policy Reader có quyền `update` với `fields=[]`; 13 cặp có phản hồi 5xx (chưa gom nhóm). Hai điểm này chuyển sang WP7.

### WP6. Coverage bằng tracecov

- Kiểm `schemathesis --version` và `run --help` của image đã pin (digest trong `manifest/baseline.yaml`) để xác nhận các flag coverage (`--coverage-format`, `--coverage-report-json-path`). Tài liệu cũ ghi pipeline lịch sử có tracecov 0.25.2 nhưng chưa chứng minh các flag là tùy chọn chuẩn của 4.30.0.
- Nếu có: thu file coverage mỗi run, tổng hợp theo actor và profile. Nếu không: `NOT_MEASURED`, không quy đổi từ số request.
- **DoD:** bảng coverage (tham số, từ khóa, phản hồi, example) và danh sách các phần không tới được kèm lý do.

**Kết quả (đã làm, xem [wp6/README.md](wp6/README.md)):**

- Image `schemathesis/schemathesis:4.30.0` có sẵn nhóm *Coverage options* (`--coverage-format`, `--coverage-report-json-path`); harness đã thu `schemathesis-coverage.json` ở cả 18 seed, ghi `tracecov_version: 0.25.2`. C6 là **đo được**, không phải `NOT_MEASURED`.
- Tổng hợp bằng `scripts/k05_coverage_report.py` thành ba bảng CSV (theo seed, theo nhóm, theo 62 cặp). Operations 100% ở cả 6 nhóm (30/30, 22/22, 10/10 theo actor); parameters 36–69%, keywords 17–48%, examples 91–100%, responses documented 19–26% (Editor 15/61, Reader 10–11/42, Anonymous 3/16).
- Phần chưa tới: chủ yếu mã phản hồi không có trong schema (204, 403, 400, 500) và `401` documented không gặp vì actor có token hợp lệ; từ khóa của thân request `oneOf`. Chạy thêm seed gần như không mở rộng coverage (phần hợp xấp xỉ trung bình).
- Phát hiện chuyển sang WP7: nhiều phản hồi `204` không có trong schema (schema và hành vi lệch nhau), 33/62 cặp chưa gặp mã phản hồi nào của schema.

### WP7. Triage, root cause và bảng thống kê lỗi

- Gom mọi failure của 18 run theo check, operation và nguyên nhân; phân loại năm nhóm của `AGENTS.md` mục 6; mỗi nhóm có reproducer (precondition, actor, request/chuỗi, expected, actual, version).
- **Root cause cho lỗi 500 của aggregate (finding P5-F01):** hiện `OPEN` vì chưa có stack trace của server. Replay `aggregate={"foo":1}` và lưu log Directus tại thời điểm đó.
- Một bảng duy nhất: số request, số check fail theo loại, số nhóm failure, số defect đã xác nhận; ghi rõ ba con số này khác nhau.
- **DoD:** C5.

**Kết quả (đã làm, xem [wp7/README.md](wp7/README.md)):**

- 18 seed có 31.147 request, 1.356 lần check thất bại, 237 nhóm, **16 nguyên nhân gốc** (10 sản phẩm, 5 schema, 1 chưa kết luận); không còn nhóm chưa phân loại. Ba con số được tách riêng (request, check thất bại, nhóm) và đối chiếu thêm với 932 tương tác 5xx vì Schemathesis chỉ giữ một failure mỗi operation mỗi seed.
- **Chín nguyên nhân sản phẩm đã xác nhận bằng replay và thông điệp lỗi gốc của server** (đầu vào sai gây `500` thay vì `4xx`: ID ngoài `int4` trong đường dẫn, `aggregate` sai cấu trúc, `published_at` sai kiểu, ký tự NUL, phần tử `null`, `id` sai kiểu hoặc ≥ 1e21, `export=csv` với `fields` không có thật, `page`×`limit` tràn `bigint`, `groupBy` ngoặc sai thứ tự). Giải thích 923/932 tương tác 5xx; 9 còn lại chưa tái hiện được. Finding P5-F01 (aggregate) đóng với RCA có stack và dòng mã tại commit đã pin.
- Các câu hỏi mở của WP5 và WP6 được đóng: Reader `PATCH` rỗng (cấu hình fixture `fields=[]`, không phải lỗi), ID không tồn tại trả `403` (thiết kế của Directus, schema mô tả `404`), `utils/sort` `400` (thiếu tham số bắt buộc, collection không có trường sort), case guided "lỗi chạy" (bằng đúng số case stateful không có tương tác HTTP, 18/18 seed).
- Phần lớn failure (1.103/1.356 lần check) là chênh lệch giữa schema OpenAPI Directus xuất ra và hành vi thực (mã `204`, mã lỗi 4xx, Content-Type, response schema, ràng buộc runtime).

### WP8. Viết lại báo cáo A–H theo phạm vi K05

- Bỏ nội dung đã xóa; dùng 13 TC làm oracle và demo; chuyển catalog 257 sang phụ lục.
- Mục G: bảng 62 cặp, bảng thống kê lỗi, coverage (mục 3.3), câu khẳng định theo mục 3.4. Mục H: pin phiên bản, hướng dẫn chạy lại.
- **DoD:** không còn liên kết tới file đã xóa; mọi con số có nguồn artifact.

**Kết quả (đã làm):** báo cáo mới [BAO_CAO_CUOI_KY_K05.md](BAO_CAO_CUOI_KY_K05.md) gồm phần A đến H, kết luận và phụ lục (catalog 257 ở PL.1, đính chính ở PL.3).

- Dựng từ các gói WP1 đến WP7; mọi con số có nguồn là file trong `docs/k05/` hoặc `manifest/baseline.yaml`, và run ID ghi dạng chữ (thư mục `artifacts/runs/` bị Git bỏ qua).
- **Chạy lại bộ 13 ca ngày 24/11/2026** sau khi thu nhỏ để xác nhận không hỏng gì: S1 đến S6 6 passed (run `20261124T063845Z-1883`); 7 ca thiết kế 6 passed, 1 failed (TC13, run `20261124T063913Z-1590`); 11 invariant 9 passed, 2 failed (run `20261124T064010Z-710`); replay `editor-crud` đạt; restore PASS ở mọi lần. Trùng kết quả ngày 16/11.
- Câu khẳng định theo mục 3.4: có mẫu số 62 cặp, tách số request, check thất bại, nguyên nhân; coverage theo schema báo riêng từng chiều, không gộp thành "100%".
- Liên kết: thêm `scripts/check_md_links.py` (quét 99 file Markdown Git theo dõi, kể cả anchor). Báo cáo và `README.md` sạch; 62 liên kết tới file đã xóa trong các tài liệu cũ được gỡ định dạng, 12 anchor mục lục được sửa; `HoanThanhPlan/README.md` có ghi chú "bản lưu lịch sử" trỏ tới báo cáo mới. **Còn 18 liên kết hỏng ngoài phạm vi sửa:** 14 trong bản sao nguyên văn `bang-chung-13-tc/` (giữ để khớp hash), 3 trong `01_ke_hoach_trien_khai_R06_K05.md` (đường dẫn máy khác), 1 trong `AGENTS.md` (thư mục riêng `mnhy/`).
- **Đã xóa hai báo cáo cũ (24/11/2026, theo lệnh của người dùng):** `docs/HoanThanhPlan/09-bao-cao-cuoi-ky.md` và `BAO_CAO_CUOI_KY_R06_K05_HOAN_CHINH.md` (tổng khoảng 245 KB). Các liên kết tới chúng trong `README.md` của `docs/` và `HoanThanhPlan/`, `traceability.md`, `LO_TRINH_TOI_GIAN_R06_K05.md`, `Ke_hoach_hoan_thien_R06_K05_theo_phase.md` và `03-thiet-ke-test-va-coverage.md` được trỏ sang báo cáo K05. Còn trong lịch sử Git và bản sao lưu ngoài repo.
- Tác dụng phụ ghi nhận: probe WP7 `POST` với `id=500000` làm dãy tự tăng của `qa_articles` nhảy lên (bài tạo mới từ khoảng 500.000); fixture 1 đến 12 không bị ảnh hưởng.

### WP9. Phần quản lý nhóm theo PDF (không phải test)

| Việc | Hiện trạng |
|---|---|
| Công cụ quản lý (Trello/Jira/GitHub Projects) | Có 16 GitHub Issue (tạo 10/10, đóng cùng lúc 26/10); chưa có Project/Trello; cần quyền `project` cho token `gh` (do chủ tài khoản cấp) |
| Lịch sử Git đóng góp đều | Tại `9c4b6d8`: Lành 107 commit (09/10 đến 19/10), Nhân 50 (19/10 đến 24/11), **Trâm 0**; không có commit từ 20/10 đến 15/11 |
| Peer evaluation | Có mẫu, chưa ai điền |
| Slide, demo automation, gói nộp | Slide nháp và kịch bản demo có; cần nhóm xem và chỉnh; chưa phân người trình bày |
| README chạy lại trên máy mới | Có; chưa có bằng chứng chạy trên máy thứ hai (PDF yêu cầu mô tả được, không bắt buộc đã chạy) |

Không bịa bằng chứng đóng góp hay review; chỉ ghi những gì có thật.

**Tiến độ WP9 (24/11/2026): phần tài liệu và dữ kiện xong; còn các việc chỉ nhóm làm được.** Chi tiết và bảng đối chiếu từng yêu cầu của PDF: [wp9/README.md](wp9/README.md).

- Đã làm: thống kê đóng góp từ Git/GitHub kèm giới hạn ([dong-gop-tu-git.md](wp9/dong-gop-tu-git.md)); bảng Kanban và CSV nhập được vào GitHub Project/Trello ([bang-cong-viec.md](wp9/bang-cong-viec.md)); mẫu đánh giá chéo ([danh-gia-cheo-mau.md](wp9/danh-gia-cheo-mau.md)); dàn slide, slide nháp 16 trang, kịch bản demo và câu hỏi dự kiến ([ke-hoach-bao-ve.md](wp9/ke-hoach-bao-ve.md)); kiểm tra bản clone sạch ([xac-minh-clone-sach.md](wp9/xac-minh-clone-sach.md)).
- Đã chạy thử demo bước Schemathesis (anonymous raw, một seed): 55 giây, 32 ca sinh ra, 21 failure duy nhất, restore PASS, tác dụng phụ sạch (run `20261124T072243Z-1585`).
- Phát hiện: trong bản clone sạch có **144 liên kết hỏng** ở tài liệu cũ (110 trỏ tới `artifacts/` bị Git bỏ qua); báo cáo K05, README và `docs/k05/` có 0. Con số 18 ở WP8 chỉ đúng khi có `artifacts/` và thư mục không commit trên đĩa.
- **Chưa làm (cần nhóm):** Trâm mô tả và đưa vào repo phần việc của mình; từng người điền đánh giá chéo; tạo GitHub Project/Trello; xem và chỉnh slide, phân người trình bày; chốt ngày bảo vệ và hạn nộp; dựng lại trên máy thứ hai; quyết định cách nêu việc dùng công cụ AI.
- Sự cố đã xử lý: PR #26 vô tình thêm 1.864 file của `tai-lieu-bo-tro/`; PR #27 gỡ khỏi cây theo dõi. Nội dung vẫn còn trong lịch sử Git (quyết định viết lại lịch sử còn mở).

---

## 6. Thứ tự thực hiện và phụ thuộc

```
[Xong] Sao lưu → Mẫu số 62 cặp → Xóa v2 → Xóa pairwise
   │
   ├─ Xóa còn lại (A→B→C→D)         độc lập với phần thêm; làm trước để repo gọn
   │
   └─ WP1 (export lại schema) ─┐
                               ├─ WP2 [Lành] ─ WP3 ─ WP4 ─ WP5 ─ WP6 ─ WP7 ─ WP8
        (cần Docker + lab pin)─┘                                          │
   WP9 chạy song song, hoàn tất trước hạn nộp ────────────────────────────┘
```

- Cần khởi động Docker và lab từ WP1 trở đi; `AGENTS.md` yêu cầu được giao rõ mới làm.
- Báo cáo nộp trước ngày bảo vệ một tuần; ngày bảo vệ chưa xác nhận nên chưa gán ngày cụ thể. Việc đầu tiên cần làm là xác nhận ngày này để biết ngân sách thời gian cho WP5.
- Thời gian chạy 18 run là ẩn số: chỉ ước lượng được sau pilot ở WP5.

---

## 7. Rủi ro và cách xử lý

| Rủi ro | Xử lý |
|---|---|
| Fuzz 20 operation mới làm xuất hiện thêm lỗi 500 hoặc sai schema | Là kết quả thật, giữ nguyên và phân loại; không che, không nới check |
| Thao tác auth/utils làm hỏng token hoặc dữ liệu lab | WP4: token riêng, restore sau mỗi seed |
| Run không hoàn tất dù tăng ngân sách | Đã gặp và giải quyết ở WP5: nguyên nhân là `--max-time` (lặp tới hết giờ); chạy không `--max-time`, có trần cứng. Nếu vẫn chạm trần cứng thì ghi chưa hoàn tất và bỏ C3 |
| Tracecov không có trong image 4.30.0 | WP6: `NOT_MEASURED`, vẫn báo coverage theo operation và request |
| Schema export lại khác bản 11/10 | Cập nhật mẫu số, ghi hash và lý do |
| Xóa nhầm phần dùng chung | Gỡ phụ thuộc bằng `grep`, chạy unittest sau mỗi nhóm; còn bản sao lưu |
| Ít commit của một thành viên | Không sửa lịch sử; ghi đóng góp thực tế bằng tài liệu khác nếu có (task, review, test, tài liệu) |

---

## 8. Phê duyệt cần có và quan hệ với nhận xét của thầy

- **Lành (người dùng đã quyết định không cần, 23/11/2026):** quy tắc trong `AGENTS.md` yêu cầu Lành đồng ý việc mở allowlist 10 → 30 operation và thêm actor Reader, Anonymous vào lệnh `test raw|guided`. `AGENTS.md` mục 2 liệt kê "operation scope" và "interface cấu hình/helper" vào nhóm phải có sự đồng ý của Lành. Việc xóa workflow CI và khung coverage không được liệt kê rõ, nhưng ảnh hưởng toàn nhóm nên cũng cần báo Lành trước.
- **Giảng viên:** chưa có văn bản xác nhận scope này. Nên hỏi thầy một câu: *"Phần mở rộng thầy yêu cầu là thêm endpoint cho Schemathesis (như kế hoạch này), hay thêm test chức năng ngoài K05?"*
- **Nếu nhận xét bằng lời của thầy còn hiệu lực** (13 TC quá ít, cần CI/CD): kế hoạch này vẫn khớp phần "phủ rộng" bằng cách phủ rộng operation cho Schemathesis. CI/CD và 170 TC v2 sẽ phải khôi phục từ bản sao lưu; hãy quyết định trước khi xóa các nhóm A–B ở mục 4.2.

---

## 9. Danh sách kiểm hoàn thành

- [x] WP1: schema 3 actor export từ lab pin, CSV mẫu số cập nhật (xong 23/11/2026; hash trùng bản 11/10)
- [x] WP2: `test raw|guided` chạy theo actor (xong 23/11/2026; quyết định của người dùng, không có xác nhận của Lành)
- [x] WP3: overlay guided cho assets, import, export, sort, auth (xong 23/11/2026; bảng C2 chính thức là bảng 62 cặp của WP5, xem `wp5/bang-phan-hoi-theo-cap.csv`)
- [x] WP4: nhóm thao tác có tác dụng phụ chạy an toàn (xong 23/11/2026; xem `wp4/README.md`)
- [x] WP5: 18 run, ghi trạng thái hoàn tất hoặc `INCOMPLETE_BUDGET` (xong 24/11/2026: 18/18 hoàn tất; xem `wp5/README.md`)
- [x] WP6: coverage tracecov (đo được, tracecov 0.25.2; xem `docs/k05/wp6/`)
- [x] WP7: bảng thống kê lỗi, reproducer, RCA lỗi 500 aggregate (xem `docs/k05/wp7/`)
- [x] WP8: báo cáo A–H viết lại (`docs/k05/BAO_CAO_CUOI_KY_K05.md`); liên kết hỏng còn lại chỉ ở bản sao nguyên văn và file riêng
- [ ] WP9: board, đóng góp, peer evaluation, slide và demo (tài liệu, dữ kiện, slide nháp và kịch bản demo xong 24/11/2026; **còn việc của nhóm**: bằng chứng của Trâm, điền đánh giá chéo, tạo Project, chỉnh slide; xem `wp9/README.md`)
- [x] Xóa nhóm A, B, C, D (mục 4.2) sau khi trích bằng chứng 13 TC (xong 23/11/2026)
- [x] Sáu tiêu chí C1–C6 (mục 3.2) đều có bằng chứng (xong 24/11/2026): C1, C2 (phần CRUD), C3, C4 ở `wp5/`; C5 ở `wp7/`; C6 ở `wp6/`; tổng hợp ở báo cáo, mục D.4 và G.3 đến G.6
- [x] Mọi câu khẳng định "100%" đi kèm mẫu số (xong 24/11/2026): đã rà `docs/k05/` và README; "100%" chỉ còn xuất hiện cùng mẫu số (62/62 cặp; 30/30, 22/22, 10/10 operation) hoặc trong câu phủ định; các báo cáo cũ có ghi chú "bản lưu lịch sử"

---

## Phụ lục. Tệp liên quan

| Tệp | Nội dung |
|---|---|
| [mau-so-30-operation.csv](mau-so-30-operation.csv) | 62 cặp (actor, operation), cột nhóm và phân loại |
| [mau-so-30-operation.summary.json](mau-so-30-operation.summary.json) | Hash schema, số liệu tóm tắt |
| `scripts/build_k05_denominator.py` | Sinh mẫu số từ schema theo actor, chỉ đọc file |
| `runtime/schemas/r06-k05-v2/{editor,reader,anonymous,admin}.json` | Schema export 11/10/2026 (thư mục `runtime/` bị Git bỏ qua) |
| `manifest/baseline.yaml` | Pin Directus, PostgreSQL, Schemathesis (version và digest) |
| `docs/test-matrix.md` | Kết quả chiến dịch cũ: raw 59/65/51 case, guided khoảng 5,8 nghìn case mỗi seed, đều dừng `max_time` (không phải "chưa hoàn tất": xem `wp5/README.md` mục 3) |
| `docs/HoanThanhPlan/tai-lieu-bo-tro/phase6-20261018/historical-raw-guided.csv` | Coverage và thời gian từng seed của chiến dịch cũ |
