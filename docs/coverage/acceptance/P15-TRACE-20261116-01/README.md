# Bổ sung trace S1–S6 và OAS anonymous — 16/11/2026

**Nhiệm vụ COMPLETE trong phạm vi capture/kiểm chứng trace và schema đúng actor.** S1–S6 chạy lại một lần,6PASS,exit0; TC13 không chạy lại, vẫn giữ FAIL từ P10. Không ghi trace mới thành evidence lịch sử P10. Remote CI vẫn NOT_RUN; không tự nghiệm thu M2 hoặc chuyển Phase.

## Vì sao cần run mới

Đã kiểm artifact P10/harness theo handoff P15: các HTTP body cũ còn ở private runtime nhưng thiếu mapping method/path/status/actor theo scenario; không suy mapping từ số file hoặc thứ tự source. Bật trace opt-in trong api_request của shared helper, gán nhãn S1–S6 tại call site cũ và dùng lại toàn bộ oracle/fixture/cleanup. Không đổi expected/result hoặc source Directus. Default trace off giữ interface cũ; p09 adapter nhận trace/run_id explicit, kiểm ownership/image/healthy trước gọi helper.

[Selection](selection-manifest.json) được ghi **trước run scenario**:6execution mới S1–S6,7execution còn lại giữ P10-20261116-02; policy PREDECLARED_EXECUTIONS, không chọn historical PASS khác để né FAIL. Không thêm canonical ID/test version. Lab exact namespace r06-k05-p09-20261115-audit01,host18055,private credentials qua environment, không wrapper mặc định trỏ lab cũ. Preflight-before/after và source-hashes.json ghi bằng chứng hiện tại; không start/reset/seed hoặc gọi lab cũ.

## Trace đã kiểm

[Trace](trace.json) có17HTTP record cho6scenario, mỗi record có scenario,method,path,actor,request JSON,status,curl exit,time,response ref/hash. Chỉ ghi actor label, không ghi token/header/cookie. response body cùng record được copy vào http/ sau kiểm; không trộn HTTP file cũ. Thời gian là thời điểm ghi response, không giả duration/start chính xác của function. Setup/control/export/verify không được cộng thành ca độc lập.

S1 tạo item tạm, GET readback đúng payload/ID, PATCHscore rồi GET giữ các field khác, DELETE204 và GET403/FORBIDDEN sau DELETE. S2 query trả đúng6published ID từ baseline snapshot; S3 có DB order oracle, S4/S5/S6 giữ oracle Reader/negative và readback. [Scenario report](scenario-report.json)6PASS; runner-outcome.json exit0. [Verification trace](verification-trace.json) và baseline-articles/categories xác nhận đầy đủ2collection trước/sau khớp; scenario-outcomes.json khẳng định không broad restore. Chỉ xóa item S1 do run tạo; request Reader ghi vào fixture bị từ chối, baseline không đổi.

Trace không capture Content-Type HTTP gốc, nên không gán content-type/response-schema check PASS cho6scenario từ việc JSON parse thành công. Đây là trace/operation/behavior evidence, **contract_verdict vẫn NOT_RUN** nếu chưa có kiểm tương ứng. DELETE204 body rỗng được giữ nguyên, không sửa thành JSON hoặc lỗi parse.

## Schema anonymous đúng actor

[Schema metadata](schema-metadata.json): anonymous GET /server/specs/oas HTTP200 **không Authorization**, raw bytes/hash ở raw-oas/anonymous.json. Raw editor/reader/admin xuất riêng; cả3khớp byte với P10 (schema-comparison-to-P10.json). Không lấy admin/editor làm anonymous, không mutate public policy để hiện route.

Anonymous OAS hợp lệ3.0.1 nhưng không chứa GET /items/qa_articles hoặc các route qa_*. [Evidence](anonymous-contract-evidence.json) giữ **OPERATION_NOT_IN_ANONYMOUS_OAS / contract NOT_MEASURED**. Đây là kết quả quan sát, không phải export bị thiếu hoặc PASS/N/A. Không gửi thêm protected anonymous request ngoài schema. P10 P3-AUTHZ-DR-047 business PASS giữ nguyên, không gắn snapshot mới như OAS đã có ở run cũ. Việc endpoint bị lọc không thay thế assertion quyền; old authorization evidence và schema availability là hai chiều riêng.

## Coverage có căn cứ

[Bundle](bundle/) là revision execution1.1 dựa M2-COVERAGE trước, đổi đúng6execution theo selection đã khai báo, giữ7case P10 gồm TC13. [Lineage](lineage.json), [validation](validation.json), [calculator](coverage-summary.json) và audit-evidence.json.

R13,D13,E13,V12/13 không đổi. Đã bổ sung5unique operation-evidence records:4templateCRUD từ S1 và GETlist từ S2, status/body/readback được đối chiếu trực tiếp. Reader403 không được tính dispatch/positive. P08 hit/positive **5/5 trong5generic method–path template đã chọn**, binding qa_articles; **không phải10concrete collection operations**, không coverage toàn Directus. Denominator/template IDs/RTM/oracle không bị đổi. Không cộng17HTTP hoặc6rerun thành canonical test mới. Original history vẫn ở bundle/report cũ.

## Kiểm tra / bàn giao

Offline trace tests gồm integrity/hash, unknown actor, thiếu scenario, network0 không làm denialPASS, traversal/missing response, body204 hợp lệ/empty200 lỗi và anonymous schema không fallback; kiểm thực bundle TC13 còn FAIL và denials không dispatch. P09 isolation tests và P08 validate/calculate cùng static/diff/protected-hash/secret checks có kết quả thực trong audit. Không sửa Directus, oracle/expected, không cài/nâng dependency hoặc sửa lab demo.

Đường kiểm lại (offline):

```powershell
python -B -m unittest discover -s tests -p test_scenario_trace.py -v
python -B scripts/coverage_offline.py validate docs/coverage/acceptance/P15-TRACE-20261116-01/bundle
python -B scripts/coverage_offline.py calculate docs/coverage/acceptance/P15-TRACE-20261116-01/bundle
```

Tồn đọng: contract protected anonymous không có trong OAS nên không đo từ schema đó; không bịa contract để lấp gap. Nếu cần response-contract diagnostic đầy đủ cho6scenario phải capture Content-Type tại thời điểm gửi trong nhiệm vụ riêng; không infer từ body. CI remote chưa có run thật là công việc kế tiếp, cần context/quyền phù hợp; không push trong batch này. Keyword/code coverage vẫn NOT_MEASURED. Không tự chuyển Phase, commit/push/PR/issue/liên hệ/sub-agent. Owner đề xuất Trâm trace/oracle, Nhân contract/schema, Lành CI; không giả review.
