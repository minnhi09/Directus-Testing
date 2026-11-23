# Kế hoạch commit và đẩy lên GitHub (23/11/2026)

**Trạng thái (cập nhật 23/11/2026):** **13 commit cục bộ đã tạo** trên nhánh mới `feat/k05-scope-30op` (tách từ `feat/g1-shared-interface` tại `a718047`); **chưa push**. Các mục 1–4 dưới đây là kế hoạch ban đầu; số liệu ban đầu lấy từ `git status` bằng lệnh chỉ đọc.

| # kế hoạch | Commit | Nội dung |
|---|---|---|
| 1 | `d216f26` | Mẫu số 62 cặp, script sinh, kế hoạch (5 file) |
| 2 | `dd93d9e` | Actor và phạm vi campaign, overlay guided, `k05_reach_report.py` (3 file) |
| 3 | `e069187` | Gỡ khung coverage/CI và chuỗi P09/P10/P14 (36 file) |
| 4 | `61cc553` | Gỡ thí nghiệm pairwise 36/9 (12 file) |
| 5 | `6195fc0` | Gỡ `docs/coverage`, giữ bằng chứng 13 TC (1.073 file; git nhận 34 cặp là đổi tên vì nội dung giống hệt) |
| 6 | `e9de81a` | Gỡ hồ sơ rà soát 20 phase và kế hoạch toàn hệ thống (2 file) |
| 7 | `efa0fcb` | README và truy vết (2 file) |
| 8 | `1fc059a` | Phần 1 và Phần 2 (8 file) |
| 9 | `91f835c` | Báo cáo giữa kỳ, hướng dẫn, mô tả hệ thống (14 file) |
| 10 | `59a2240` | Tài liệu học tập (13 file) |
| 11 | `a8b4437` | Báo cáo cuối kỳ hoàn chỉnh và README HoanThanhPlan (**3 file**, không phải 6 như dự kiến: chỉ có 3 file chưa theo dõi ngoài `tai-lieu-bo-tro`) |
| 13 | `31c5101` | Oracle catalog v1 (5 file) |
| 14 | `2801ad8` | Tiến độ và triage pilot tháng 10 (2 file) |

**Không commit (theo kế hoạch):** commit 12 (`docs/HoanThanhPlan/tai-lieu-bo-tro/`, tùy chọn), `docs/slide_bai_giang/` (slide của giảng viên), `scripts/invariants.py` (chỉ đổi quyền file). Tất cả 13 commit mang tên tác giả `Trương Võ Trọng Nhân` và dòng `Co-Authored-By: Claude`. 18 unit test đạt trên cây làm việc cuối.

## 1. Hiện trạng

| Mục | Giá trị |
|---|---|
| Nhánh hiện tại | `feat/g1-shared-interface`: **ahead 11, behind 1** so với `origin/feat/g1-shared-interface` (11 commit cũ chưa lên GitHub) |
| `main` cục bộ | Cũ hơn `origin/main` **107 commit** (không dùng làm gốc) |
| Remote | `origin` = `git@github.com:minnhi09/Directus-Testing.git` (SSH) |
| Thay đổi chưa commit | 3.061 mục: 1.088 file đã xóa (đang được theo dõi), 1.972 file mới chưa theo dõi, 1 file chỉ đổi quyền |
| Danh tính commit | Tên `Trương Võ Trọng Nhân`; email khớp commit cũ. Email phải là email đã gắn với tài khoản GitHub của bạn thì commit mới tính vào hồ sơ (tôi không kiểm tra được từ máy này) |

### Những điều phát hiện khi phân loại

1. **Các file v2 chưa từng được commit** (`catalog_v2_g*.py`, `admin_cases.py`, `test-catalog-v2.json`…). Xóa chúng không để lại dấu vết trong git, nên **không có commit "xóa v2"**. Đừng tạo commit rỗng để thay thế.
2. **`scripts/invariants.py` chỉ đổi quyền file** (755 → 644, do Windows), không có thay đổi nội dung. **Không stage** file này.
3. **Nhiều tài liệu quan trọng chưa từng được commit:** `docs/phan1` và `docs/phan2` (báo cáo Phần 1 và 2), các báo cáo giữa kỳ `docs/Bao_cao_*`, `docs/hoc-tap-r06-k05`, `docs/images`, `docs/HoanThanhPlan` (1.812 file), `evidence/progress-2026-10-11.md` và `pilot-triage-2026-10-11.md`. Nên commit sớm vì đây là phần nộp.
4. **Quét bí mật** (1.973 file sẽ được thêm, 40,8 MB, gồm cả nội dung 8 file zip): **không file nào chứa giá trị mật khẩu, khóa hay license lấy từ `config/lab.env`.** Sáu file khớp mẫu JWT đều là cùng một hằng số kiểm thử (`invalid_directus_jwt()` trong `scripts/invariants.py` và các bản sao lưu của nó), được ghi chú rõ là giá trị tổng hợp, chữ ký cố ý sai. Đây là báo động giả.
5. **`config/lab.env`, `runtime/`, `artifacts/runs/`, `tmp/`, `mnhy/` đã nằm trong `.gitignore`**, nên không bị commit nhầm (đã kiểm tra bằng `git check-ignore`).
6. **Không nên commit:** `docs/slide_bai_giang/` (4 file PDF, 10,7 MB, là slide bài giảng của giảng viên, không phải sản phẩm của nhóm). Cứ để chưa theo dõi; không cần thêm vào `.gitignore` nếu bạn không muốn đổi file đó.
7. `README.md` và `docs/traceability.md` có **thay đổi từ trước phiên này** (README đổi khoảng 160 dòng), cộng thêm một dòng tôi gỡ về thí nghiệm pairwise. Hãy xem `git diff README.md` trước khi commit để chắc mọi dòng là ý của bạn.

## 2. Nguyên tắc

- Mỗi commit một việc thật; thông điệp bằng tiếng Việt theo kiểu lịch sử cũ (`docs: …`, `test(...): …`, `feat(...): …`).
- **Thứ tự xếp theo phụ thuộc** để snapshot từng commit càng ít gãy càng tốt. Tôi chưa kiểm tra từng snapshot trung gian bằng cách chạy lại test; chỉ kiểm tra trạng thái cuối (18 test đạt). Các lệnh `git add` đã được thử ở chế độ `-n` (không stage): bốn commit xóa (3, 4, 5, 6) gộp lại phủ đúng **1.088 file đã xóa**, không sót và không trùng.
- Không commit rỗng, không đổi ngày, không đổi tác giả, không gộp thay đổi của người khác vào commit của mình (`AGENTS.md` mục 7).
- Trước mỗi commit: `git diff --cached --stat` để đối chiếu danh sách file; sau mỗi nhóm xóa chạy `python -m unittest discover -s tests -p "test_*.py"`.
- Commit do tôi tạo theo hệ thống sẽ kết thúc bằng dòng `Co-Authored-By: Claude …`. Nếu bạn không muốn dòng này trên GitHub của môn học, hãy tự commit bằng các lệnh bên dưới hoặc bảo tôi bỏ dòng đó.

## 3. Danh sách commit đề xuất

| # | Thông điệp dự kiến | Phạm vi (pathspec) | Ghi chú |
|---|---|---|---|
| 1 | `docs(k05): thêm mẫu số 62 cặp operation và kế hoạch thu nhỏ phạm vi` | `docs/k05/KE_HOACH_THU_NHO_VA_BO_SUNG_K05.md`, `docs/k05/KE_HOACH_COMMIT.md`, `docs/k05/mau-so-30-operation.*`, `scripts/build_k05_denominator.py` | Không gồm `docs/k05/bang-chung-13-tc/` (đi cùng commit 5) |
| 2 | `feat(lab): chọn actor và phạm vi 30 operation cho campaign raw/guided, thêm overlay guided và bảng reach` | `lab.sh`, `scripts/lab-components.sh`, `scripts/k05_reach_report.py` | Gồm cả phần gỡ lệnh `cost-query` (cùng file nên không tách được) |
| 3 | `refactor: gỡ khung coverage/CI M1–M3 và chuỗi P09/P10/P14 ngoài phạm vi K05` | 36 file đã xóa của nhóm A và B (xem lệnh bên dưới) | Gộp A và B vì phụ thuộc chéo (`ci_m2.py` gọi `p09_runtime.py`) |
| 4 | `refactor: gỡ thí nghiệm pairwise 36/9 (kỹ thuật K06)` | 12 file: `cost_query.py`, `test_cost_query.py`, hai file `query-cost-*.json`, ba file tài liệu `03-query-*`/`06-toi-uu-chi-phi`, năm file dữ liệu pairwise trong phase6 | Sau commit 3 vì `check_offline.py` (bị xóa ở commit 3) từng import `cost_query` |
| 5 | `refactor: gỡ docs/coverage, giữ bằng chứng 13 TC trong docs/k05` | Xóa 1.038 file: `docs/coverage/**` (trừ `oracles/`), `coverage_schema.ps1`, `check_coverage_examples.ps1`, `scenario_trace.py`, `test_scenario_trace.py`; thêm `docs/k05/bang-chung-13-tc/` (35 file) | Sau commit 3 vì test coverage đã bị xóa |
| 6 | `docs: gỡ hồ sơ rà soát 20 phase và kế hoạch kiểm thử toàn hệ thống` | 2 file đã commit của nhóm D | 3 file nhóm D còn lại chưa từng commit nên xóa không để lại dấu vết |
| 7 | `docs: cập nhật README và truy vết theo phạm vi K05` | `README.md`, `docs/traceability.md` | Xem `git diff` trước (thay đổi cũ của bạn) |
| 8 | `docs: thêm Phần 1 và Phần 2 (phân tích hệ thống, thiết kế test, kết quả, nguyên nhân lỗi)` | `docs/phan1/`, `docs/phan2/` | 8 file chưa từng commit |
| 9 | `docs: thêm báo cáo giữa kỳ, hướng dẫn chạy và mô tả hệ thống` | `docs/Bao_cao_*`, `docs/Huong_dan_chay_Directus_Windows.md`, `docs/Mo_ta_he_thong_*`, `docs/Ke_hoach_hoan_thien_*`, `docs/images/` | Gồm PDF/PPTX của báo cáo giữa kỳ |
| 10 | `docs: thêm tài liệu học tập và câu hỏi bảo vệ` | `docs/hoc-tap-r06-k05/` | |
| 11 | `docs: bổ sung hồ sơ HoanThanhPlan chưa được theo dõi` | `docs/HoanThanhPlan` trừ `tai-lieu-bo-tro/` (6 file chưa theo dõi; phần còn lại của thư mục đã nằm trong git từ trước) | Xem `git status` thư mục này trước khi commit |
| 12 | `docs: lưu tài liệu bổ trợ và bằng chứng chọn lọc theo từng phase` | `docs/HoanThanhPlan/tai-lieu-bo-tro/` (1.879 file, 26,1 MB, nhiều file zip) | **Tùy chọn.** Nếu repo không cần các bản lưu này, bỏ qua và để chưa theo dõi |
| 13 | `test: thêm oracle cho 66 ca catalog v1` | `scripts/oracle_v2.py`, `tests/test_oracle_v2.py`, `docs/coverage/oracles/` | Sau commit 11 vì `oracle_v2.py` đọc `docs/HoanThanhPlan/08-ket-qua-case.csv` |
| 14 | `docs: ghi nhận tiến độ và triage pilot tháng 10` | `evidence/progress-2026-10-11.md`, `evidence/pilot-triage-2026-10-11.md` | |

Về sau: **mỗi WP là một commit riêng** (WP4, WP5…), và kết quả chạy lab (bảng thống kê lỗi, reproducer, báo cáo) cũng tách riêng.

## 4. Lệnh thực hiện (chạy từng khối, kiểm tra `git diff --cached --stat` trước khi `git commit`)

```bash
# 1
git add -- docs/k05/KE_HOACH_THU_NHO_VA_BO_SUNG_K05.md docs/k05/KE_HOACH_COMMIT.md docs/k05/mau-so-30-operation.csv docs/k05/mau-so-30-operation.summary.json scripts/build_k05_denominator.py

# 2
git add -- lab.sh scripts/lab-components.sh scripts/k05_reach_report.py

# 3 (nhóm A + B: chỉ stage phần đã xóa của các file đang được theo dõi)
git add -u -- scripts/coverage_offline.py scripts/check_offline.py scripts/offline_suite.py scripts/ci_m2.py \
  tests/test_coverage_archive.py tests/test_coverage_offline.py tests/test_coverage_scoped_assertions.py tests/test_ci_m2.py tests/test_offline_suite_gate.py \
  tests/fixtures docs/CI_M2.md docs/CI_STATIC_OFFLINE.md .github/workflows \
  scripts/p09_preflight.py scripts/p09_runtime.py scripts/p10_regression.py scripts/p10_selection.py scripts/p14_pilot.py \
  scripts/capture_scenario_http.py scripts/check_scenario_contracts.py \
  tests/test_p09_preflight.py tests/test_p09_runtime.py tests/test_p10_runtime.py tests/test_p10_selection.py tests/test_p14_pilot.py tests/test_http_contract_metadata.py

# 4
git add -u -- scripts/cost_query.py tests/test_cost_query.py scripts/data/query-cost-model-v1.json scripts/data/query-cost-protocol-v1.json \
  docs/HoanThanhPlan/03-query-exhaustive-36.csv docs/HoanThanhPlan/03-query-pairwise.csv docs/HoanThanhPlan/06-toi-uu-chi-phi.md \
  docs/HoanThanhPlan/tai-lieu-bo-tro/phase6-20261018

# 5  (build_rest_denominator.py và test_rest_denominator.py chưa từng commit nên không có trong lệnh)
git add -u -- docs/coverage scripts/coverage_schema.ps1 scripts/check_coverage_examples.ps1 scripts/scenario_trace.py tests/test_scenario_trace.py
git add -- docs/k05/bang-chung-13-tc

# 6  (3 file nhóm D khác chưa từng commit nên không để lại dấu vết trong git)
git add -u -- docs/RA_SOAT_20_PHASE_R06_K05_2026-11-15.md docs/KE_HOACH_KIEM_THU_DIRECTUS_TOAN_HE_THONG.md

# 7
git add -- README.md docs/traceability.md

# 8–10
git add -- docs/phan1 docs/phan2
git add -- docs/Bao_cao_*.md docs/Bao_cao_*.pdf docs/Bao_cao_*.pptx docs/Huong_dan_chay_Directus_Windows.md \
  docs/Mo_ta_he_thong_actor_module_dependency_luong_du_lieu.md docs/Ke_hoach_hoan_thien_R06_K05_theo_phase.md docs/images
git add -- docs/hoc-tap-r06-k05

# 11–12
git add -- docs/HoanThanhPlan ':!docs/HoanThanhPlan/tai-lieu-bo-tro'
git add -- docs/HoanThanhPlan/tai-lieu-bo-tro        # tùy chọn

# 13–14
git add -- scripts/oracle_v2.py tests/test_oracle_v2.py docs/coverage/oracles
git add -- evidence/progress-2026-10-11.md evidence/pilot-triage-2026-10-11.md
```

Không stage: `scripts/invariants.py` (chỉ đổi quyền), `docs/slide_bai_giang/`.

## 5. Đẩy lên GitHub và mở PR

1. **Kiểm tra quan hệ nhánh với `origin/main` trước** (cần `git fetch` qua SSH): nhánh hiện tại đã đi bao xa so với `origin/main`, và `main` trên GitHub chứa gì mà máy bạn chưa có (107 commit). Ghi chú cũ trong repo nhắc tới "blocker SSH", chưa biết còn hay không.
2. Tạo nhánh mới từ nhánh hiện tại (ví dụ `feat/k05-scope-30op`) cho các commit của kế hoạch này; **không rebase, không force-push** (`AGENTS.md`).
3. Push nhánh, mở PR vào `main`, merge bằng merge commit. Biểu đồ đóng góp và trang Insights của GitHub thường chỉ tính commit trên **nhánh mặc định**, nên cần merge.
4. 11 commit cũ chưa push của `feat/g1-shared-interface` cũng cần lên GitHub; xử lý riêng và báo trước nếu cần merge với 1 commit phía sau.

## 6. Việc cần bạn quyết

- Có commit nhóm 12 (`tai-lieu-bo-tro`, 1.879 file, 26,1 MB) không?
- Dòng `Co-Authored-By: Claude` trong commit do tôi tạo: giữ hay bỏ?
- Tôi tạo các commit cục bộ (chưa push) theo từng bước, hay bạn tự chạy các lệnh trên?
