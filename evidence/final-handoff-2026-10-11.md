# Bàn giao checkpoint cuối local — R06 + K05

Ngày ghi nhận: `2026-10-11`
Phạm vi: baseline local `r06-k05`, Directus `12.5.0`, PostgreSQL `16`,
Schemathesis `4.30.0`. Đây là kết quả quan sát được trên máy hiện tại; không
phải bằng chứng chạy trên máy thứ hai.

Phạm vi R06/K05 và đối chiếu với yêu cầu nguồn được chuẩn hóa tại
[`docs/scope-review-r06-k05.md`](../docs/scope-review-r06-k05.md). Tài liệu này
không thay thế `yeu_cau.pdf` và không làm mất các artifact failure.

## Kết luận ngắn

G1 đạt baseline kỹ thuật với findings chưa đóng. Stack, seed, schema actor,
scenario nghiệp vụ, Reader policy và pipeline raw/guided đều có bằng chứng
chạy thực tế. Không được diễn giải kết luận này thành “mọi test PASS”: invariant
recheck vẫn exit `1`, hai campaign đầy đủ vẫn `failed_or_incomplete`, và các
candidate được giữ nguyên để triage.

## Bằng chứng runtime mới nhất

| Hạng mục | Run | Kết quả thực tế |
|---|---|---|
| Doctor | `20261011T134705Z-161373` dưới `a153e99` | PASS; Directus/DB/runner sẵn sàng, license active, `custom_permission_rules_enabled=true`, digest đúng manifest |
| Doctor recheck | `20261011T141416Z-173791` dưới `8a0d042` | PASS; stack, fixture map, pinned images, authenticated health và license active; exit `0` |
| Doctor latest recheck | `20261011T142245Z-177107` dưới `9d26617` | PASS; Directus/DB/runner, fixture map, pinned image digest, authenticated health và license active; exit `0` |
| Replay status oracle | `a713481`; final recheck dưới HEAD `916152e`: `20261011T132550Z-151921`, `20261011T132604Z-152556` | Positive `tFjhQT` không còn false-positive (`200→403` là mismatch); `Q8K5Nh` `403→403` reproduced; restore PASS |
| Full-chain stateful replay | `3960f55`; `20261011T133817Z-157078`, `20261011T133626Z-155874` | `aZmz3k` full-chain reproduced; `Ag8Csb` bị dừng đúng vì precondition pool không khớp, restore PASS |
| Contract probe | `20261011T130227Z-139257` | Exit `1` có chủ đích; ghi 4 schema candidate, cleanup dữ liệu tạm PASS |
| Invariant recheck | `20261011T134626Z-160826` dưới `bcbf219` | `9 passed`, `2 failed`, `0 blocked`, exit `1` |
| Invariant latest recheck | `20261011T141918Z-175886` dưới `8a0d042` | `9 passed`, `2 failed`, `0 blocked`, exit `1`; aggregate 500 và contract candidate không đổi, không có regression mới |
| Invariant current recheck | `20261011T142618Z-178896` dưới `d186191` | `9 passed`, `2 failed`, `0 blocked`, exit `1`; aggregate 500, controls 200 và 4 contract candidate vẫn tái hiện |
| Aggregate targeted replay latest | `20261011T144640Z-184631` dưới `ddce259` | `unknown-function-shape=500`, hai control `200`; exit `1` được giữ, không mutation |
| Contract targeted replay latest | `20261011T144648Z-185062` dưới `ddce259` | Bốn schema candidate; probe tạo/xóa dữ liệu tạm và cleanup thành công; exit `1` được giữ |
| Scenario nghiệp vụ | `20261011T105231Z-104612` | S1–S6: `6 passed`, `0 failed`, `0 blocked` |
| Scenario recheck | `20261011T141418Z-174367` dưới `8a0d042` | S1–S6: `6 passed`, `0 failed`, `0 blocked`, exit `0` |
| Scenario latest recheck | `20261011T142455Z-178114` dưới `3811b44` | S1–S6: `6 passed`, `0 failed`, `0 blocked`, exit `0`; Reader và Editor oracle giữ nguyên |
| Schema latest recheck | `20261011T142815Z-179693` dưới `de078a2` | Admin/editor/reader/anonymous `14/14/6/0` operation; bốn hash khớp manifest; exit `0` |
| Smoke latest recheck | `20261011T142942Z-180458` dưới `0f7e887` | Field validation, `SET NULL`, actor login, category read và Reader published filter PASS; exit `0` |
| Raw campaign | `20261011T085034Z-76481` | Đủ seed `101/202/303`, đủ 10/10 operation, restore PASS; runner exit `1` do budget/check failure |
| Guided campaign | `20261011T095117Z-89079` | Đủ seed `101/202/303`, đủ 10/10 operation, restore PASS; runner exit `1` do budget/check failure |
| Guided timestamp replay | `20261011T135006Z-162769` dưới `a8c4a51` | `kb5gjq` source/expected/actual `500`, `reproduced_request_only`, restore PASS, exit `1`; PostgreSQL `22007` |
| Guided export replay | `20261011T135713Z-165099` dưới `778ef20` | `F8j8Gl` source/expected/actual `200`, body array 12 item ngoài schema object, `reproduced_request_only`, restore PASS, exit `1` |
| Guided XML export replay | `20261011T135951Z-166351` dưới `a0e8996` | `UNKW3j` source/expected/actual `200`, `text/xml` ngoài schema JSON, `reproduced_request_only`, restore PASS, exit `1` |
| Guided YAML export replay | `20261011T140125Z-167402` dưới `4160c92` | `R0sH5o` source/expected/actual `200`, `text/yaml` ngoài schema JSON, `reproduced_request_only`, restore PASS, exit `1` |
| Guided negative replay | `20261011T140307Z-168360` dưới `231842a` | `DhqXrn` full chain `UqHibT → DhqXrn`, source `204`, actual `403` do field `id`, restore PASS, exit `1` |
| Stateful negative setup | `20261011T140452Z-169384` dưới `6bfe3ad` | `UTk4sa` parent ID mapping mismatch, target not sent, restore PASS, exit `1` |
| Positive query semantic replay | `20261011T140814Z-170794` dưới `8bfefad` | `6IayFG` `offset` vượt safe-number, source/expected/actual `400 INVALID_QUERY`, restore PASS, exit `1` |
| Negative coercion replay | `20261011T141024Z-171863` dưới `9d71e9c` | `6THjzP` `name` integer được Directus ép thành string, source/actual `200` trái expected `400`, restore PASS, exit `1` |
| Projection schema replay | `20261011T141213Z-172805` dưới `0918739` | `QPKZ6w` projection chỉ trả `title`, schema yêu cầu `score`, `reproduced`, restore PASS, exit `0`; không phải contract PASS |

Artifact chi tiết nằm cục bộ tại `artifacts/runs/<run_id>/`; các thư mục này
được Git ignore. Run report phải được đọc cùng `metadata.json`, `run.log`,
schema hash, fixture version và trạng thái restore; không chia sẻ credential
hoặc response nhạy cảm.

## Phân loại finding

| Nhóm | Bằng chứng | Phân loại hiện tại |
|---|---|---|
| Aggregate `{"foo":1}` | Recheck `./lab.sh replay aggregate-query-robustness`, run `20261011T144640Z-184631` dưới `ddce259`; control `{}` và `{"count":["id"]}` trả 200 | Schema omission + product robustness candidate; HTTP 500 chưa phải product defect đã xác nhận |
| POST category/article trả `data` object | Contract probe và source Directus pin `4f77933bf9551cac6b289576078783e189b8f4e3` | Schema/contract candidate; không đếm thành hai defect |
| `export=csv` trả `text/csv` | Contract probe | Schema/contract content-type candidate |
| DELETE detail trả `204` | Contract probe | Schema response-map candidate |
| Guided `POST /items/qa_articles` với `published_at=""` | Replay `kb5gjq`, editor schema `string` + nullable + custom `timestamp`, Directus log và PostgreSQL SQLSTATE `22007` | Schema-semantic/product robustness candidate; chưa xác nhận product defect |
| Guided `export=json/xml/yaml` | Replay `F8j8Gl`, `UNKW3j` và `R0sH5o`; HTTP `200` trả alternate body/media type ngoài operation schema | Schema/contract alternate-export candidate; chưa xác nhận product defect |
| Accepted negative `DhqXrn` | Full-chain replay; source `204`, actual `403` với permission error trên `id` | Precondition/policy/negative-oracle mismatch; không xác nhận defect |
| Accepted negative `UTk4sa` | Parent transition không map được ID, target không gửi | Stateful artifact/precondition limitation; chưa kết luận |
| Positive query `6IayFG` | `GET /items/qa_articles` với `offset` vượt safe-number | Schema semantic/generator-positive candidate; response-map gap `400`, chưa xác nhận defect |
| Negative coercion `6THjzP` | `POST /items/qa_categories` với `name` integer trả `200`, response là string | Schema-negative/oracle semantic mismatch; chưa xác nhận defect |
| Projection `QPKZ6w` | `GET /items/qa_articles/7?fields=title,author.name` trả object thiếu `score` theo schema item | Schema/projection contract gap; reproducer exit `0` không đóng response-schema failure |
| Stateful replay | `baaee4b` + oracle fix `a713481`, final recheck `20261011T132550Z-151921` | `pM4r4g` replay đủ parent chain nhưng mismatch; `CkqaOB` không có parent nên request-only; positive chain status mismatch được giữ đúng |
| Check failures campaign | Raw/guided reports | Occurrence để triage, không phải defect count; không đổi exit code để làm đẹp |

Contract probe được triển khai ở commit `7018107` và tài liệu hóa ở commit
`01e14d1`. Report probe ghi `schema_candidates=4`, không che runtime behavior.

Recheck sau scope-review commit `ddce259` giữ nguyên hai finding có chủ đích:
aggregate run `20261011T144640Z-184631` trả `500/200/200`; contract run
`20261011T144648Z-185062` ghi bốn candidate và cleanup thành công. Cả hai
metadata đều ghi `fixture_version=r06-k05-v2` và harness SHA `ddce259...`;
working tree `dirty` chỉ vì các file local/untracked có sẵn, không phải thay đổi
runtime chưa commit.

## Tái lập an toàn

```bash
cp config/lab.env.example config/lab.env
chmod 600 config/lab.env
# điền credential và LICENSE_KEY cục bộ; không commit config/lab.env
./lab.sh doctor
./lab.sh up
./lab.sh seed
./lab.sh smoke
./lab.sh test scenarios
./lab.sh export-schema
./lab.sh test invariants
./lab.sh replay aggregate-query-robustness
./lab.sh replay contract-schema-candidates
```

`invariants` và hai replay có thể trả exit `1` đúng theo finding hiện tại. Đó
là kết quả mong đợi của regression/contract probe, không phải lý do để dùng
`|| true`, skip hoặc nới assertion. Dùng `./lab.sh down` để dừng và giữ volume;
chỉ dùng `./lab.sh reset` khi muốn xóa đúng lab `r06-k05` sau safety preflight.

## Git và giới hạn bàn giao

Branch `feat/g1-shared-interface` chưa push; replay parent-chain hardening là commit
`baaee4b`, còn oracle status fix mới nhất là `a713481`. Các checkpoint gần nhất đều do Lành commit với
`minnhi09 <lanhdtm264@gmail.com>`;
không thêm co-author vì chưa có bằng chứng đóng góp thực tế trong các thay đổi
này. Bốn file untracked có trước được bảo toàn và `mnhy/` vẫn ignored, không
được đưa vào Git.

Các việc chưa đóng không được che giấu:

- raw/guided full campaign cần triage tiếp nếu muốn phân tích hết check failure;
- aggregate HTTP 500 cần reproducer/source/upstream evidence thêm trước khi
  gọi là product defect;
- full stateful replay hiện đã có cho chain `pM4r4g`; `CkqaOB` vẫn không đủ
  parent artifact nên phải giữ `reproduced_request_only`/unresolved;
- positive stateful replay `tFjhQT` đã được kiểm tra lại sau oracle fix: source
  `200`, replay `403`, nên giữ `mismatch`/exit `1`; không dùng report cũ trước
  `a713481` để tuyên bố reproduced;
- `kb5gjq` đã tái hiện request-only `500` do timestamp rỗng (`22007`); cần
  quyết định contract/upstream để đóng candidate, không đổi expected thành
  `PASS` và không đếm finding này như defect đã xác nhận;
- không có bằng chứng review chéo hoặc chạy trên máy thứ hai trong checkpoint
  này; hai nội dung đó không còn là gate G1 nội bộ, nhưng hướng dẫn dựng máy
  sạch và peer evaluation cuối kỳ của đề bài vẫn được giữ trong tài liệu.

Kiểm tra cuối sau commit: Bash syntax, ShellCheck, Python compile, YAML parse,
`git diff --check` và high-confidence tracked secret scan đều PASS.
