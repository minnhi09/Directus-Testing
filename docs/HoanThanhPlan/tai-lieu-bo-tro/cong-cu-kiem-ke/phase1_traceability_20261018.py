from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / 'DAMH'
DOC = REPO / 'docs/hoan-thien'
IV = 'artifacts/runs/20261012T185934Z-1453/invariant-report.json'
SC = 'artifacts/runs/20261012T222311Z-1412/scenario-report.json'
SM = 'artifacts/runs/20261012T222250Z-1431/contract-validation.json'
SM_META = 'artifacts/runs/20261012T222250Z-1431/metadata.json'
RAW = 'artifacts/runs/20261012T185958Z-355/campaign-index.json'
GUIDED = 'artifacts/runs/20261012T190350Z-1047/campaign-index.json'
AGG = 'artifacts/runs/20261012T185942Z-1219/invariant-report.json'
CON = 'artifacts/runs/20261012T185950Z-1994/invariant-report.json'

# Values describe existing evidence and proposed gaps; they do not create tests.
# n, UR, method/path, actor, source, tests, oracle, proof, status, gap, Q, risk, priority.
data = [
(1,'UR-01;UR-02','POST + GET detail /items/qa_articles; /items/qa_categories','Editor','SRC-02;SRC-05','S1;INV-03;INV-04','ID integer dương từ create và read-back bản ghi; chưa chứng minh ID không thể bị client chỉ định',[IV,SC],'HISTORICAL_SAMPLE','GAP-11','', 'R-03','P0'),
(2,'UR-02;UR-07','POST/PATCH /items/qa_categories[/id]','Editor','SRC-02;SRC-06','INV-04','So input name với dữ liệu đọc lại; non-null/max 80 có trong cấu hình, chưa có bộ negative/biên',[IV],'PARTIAL_EVIDENCE','GAP-01;GAP-13','Q-01;Q-02;Q-03','R-05','P1'),
(3,'UR-01;UR-07','POST/PATCH /items/qa_articles[/id]','Editor','SRC-02;SRC-06','S1;INV-03;INV-04','Title create/read-back có mẫu; null/required/max 120 cần case riêng',[IV,SC],'PARTIAL_EVIDENCE','GAP-01;GAP-13','Q-01;Q-03','R-05','P1'),
(4,'UR-01;UR-07','POST/PATCH /items/qa_articles[/id]','Editor','SRC-02','SMOKE:check_field_validation;INV-09','Archived với score hợp lệ có probe riêng HTTP 400; INV-09 kết hợp hai lỗi; default/omission chưa được test',[SM,IV],'PARTIAL_EVIDENCE','GAP-02;GAP-13','Q-03','R-05','P1'),
(5,'UR-01;UR-07','POST/PATCH /items/qa_articles[/id]','Editor','SRC-02;SRC-06','SMOKE:check_field_validation;INV-03;INV-04;INV-09','Probe score=-1 riêng HTTP 400, ca score hợp lệ có mẫu; chưa đủ biên/kiểu/null/omission',[SM,IV],'PARTIAL_EVIDENCE','GAP-02;GAP-13','Q-02;Q-03','R-05','P1'),
(6,'UR-01;UR-07','POST/PATCH + GET /items/qa_articles[/id]','Editor','SRC-02;SRC-06','INV-03;INV-04','Payload có timestamp null, chưa có oracle round-trip timestamp đầy đủ; không lấy POST 2xx làm chứng minh mọi format',[IV],'PARTIAL_EVIDENCE','GAP-03','Q-04','R-05','P1'),
(7,'UR-01;UR-07','POST/PATCH + GET /items/qa_articles[/id]','Editor','SRC-02','INV-03;INV-04','Có payload JSON/null, chưa so metadata trước/sau độc lập; chưa phủ các kiểu JSON',[IV],'PARTIAL_EVIDENCE','GAP-03','Q-05','R-05','P1'),
(8,'UR-01;UR-05','POST/PATCH + GET fields=internal_notes /items/qa_articles[/id]','Editor','SRC-02;SRC-03','INV-03;INV-04','Payload có notes và policy cho phép; chưa có test Editor round-trip/null notes trực tiếp',[IV],'PARTIAL_EVIDENCE','GAP-03','', 'R-01','P0'),
(9,'UR-01;UR-02;UR-07','POST/PATCH + GET /items/qa_articles[/id]','Editor','SRC-02;SRC-01','INV-04;INV-08','Category ID hợp lệ đọc lại, null sau SET NULL; invalid ID/nested/reference change chưa phủ',[IV],'PARTIAL_EVIDENCE','GAP-04','Q-05','R-04','P0'),
(10,'UR-02','DELETE /items/qa_categories/{id}; GET /items/qa_articles/{id}','Editor','SRC-02;SRC-05','INV-08;SMOKE:check_relation_nullification','Article vẫn GET được với category=null; chưa so toàn bộ field còn lại',[IV,SM_META],'PARTIAL_EVIDENCE','GAP-04','', 'R-04','P0'),
(11,'UR-01;UR-02','10 operation CRUD đã chốt trên /items/qa_articles và /items/qa_categories','Editor','SRC-03;SRC-05','INV-04;S1','Positive input có dữ liệu động và read-back cho 5 operation mỗi collection; không suy phủ mọi input',[IV,SC],'HISTORICAL_SAMPLE','GAP-01;GAP-02;GAP-04;GAP-05','', 'R-03','P0'),
(12,'UR-01','PATCH + GET /items/qa_articles/{id}','Editor','SRC-01;SRC-05','S1;INV-03;INV-04','Score đổi; title/category được so, chưa so mọi field nghiệp vụ không gửi',[IV,SC],'PARTIAL_EVIDENCE','GAP-05;GAP-13','Q-03','R-03','P0'),
(13,'UR-01;UR-02','DELETE + GET detail hai collection','Editor','SRC-01;SRC-05','S1;INV-03;INV-04','GET không trả bản ghi sau DELETE có mẫu; nhánh non-2xx chưa loại trừ 5xx đầy đủ',[IV,SC],'PARTIAL_EVIDENCE','GAP-07','Q-06','R-03;R-07','P0'),
(14,'UR-04','GET /items/qa_categories; GET /items/qa_categories/{id}','Reader','SRC-03','','Policy cấu hình read; schema/seed không thay functional read bằng Reader',[],'CONFIG_ONLY','GAP-06','', 'R-01','P0'),
(15,'UR-04','GET /items/qa_articles; GET /items/qa_articles/{id}','Reader','SRC-03;SRC-01','S4;INV-10;SMOKE:reader_unfiltered_list','Smoke không filter kiểm sáu published; INV-10 filtered set; S4 draft detail bị nhiễu do internal_notes',[SM_META,IV,SC],'PARTIAL_EVIDENCE','GAP-06;GAP-14','Q-06','R-01','P0'),
(16,'UR-05','GET list/detail + fields=internal_notes /items/qa_articles','Reader','SRC-03;SRC-01','S5;INV-10','Published precondition rồi field cấm bị chặn/loại; chưa phủ mọi projection/nested; negative oracle còn rộng',[IV,SC],'PARTIAL_EVIDENCE','GAP-07;GAP-09','Q-06','R-01','P0'),
(17,'UR-06','POST/PATCH/DELETE hai collection','Reader','SRC-03;SRC-01','S6;INV-11','PATCH article bị từ chối và read-back subset bằng Editor; các thao tác khác chưa có bằng chứng trực tiếp',[IV,SC],'PARTIAL_EVIDENCE','GAP-05;GAP-06;GAP-07','Q-06','R-02;R-03','P0'),
(18,'UR-06','GET list/detail; POST/PATCH/DELETE hai collection','Anonymous','SRC-01;SRC-05','INV-02','GET list hai collection bị từ chối; chưa kiểm mọi detail/write và nguyên nhân từ chối',[IV],'PARTIAL_EVIDENCE','GAP-06;GAP-07','Q-06','R-02','P0'),
(19,'UR-08','GET /users/me','Invalid token','SRC-05;SRC-01','INV-01','Token sai trả 401 trong mẫu lịch sử; assertion non-2xx chưa loại trừ mọi 5xx',[IV],'PARTIAL_EVIDENCE','GAP-07;GAP-12','Q-06','R-02;R-07','P0'),
(20,'UR-03','GET /items/qa_articles?filter[status][_eq]=published','Editor;Reader','SRC-01;SRC-04;SRC-05','S2;INV-05;INV-10','S2 đối chiếu fixture map published; INV-05 còn lấy status/title từ GET nền',[IV,SC],'PARTIAL_EVIDENCE','GAP-08','Q-07','R-06','P1'),
(21,'UR-03','GET /items/qa_articles?sort=title,id&limit/offset/page','Editor','SRC-01;SRC-05','S3;INV-05','S3 consistency từ full sorted list; INV-05 tính sort trên giá trị GET nền; có page=2/offset=3',[IV,SC],'PARTIAL_EVIDENCE','GAP-08','Q-07','R-06','P1'),
(22,'UR-03;UR-05','GET /items/qa_articles?fields=...','Editor;Reader','SRC-01;SRC-03;SRC-05','INV-05;S5;INV-10','Đã kiểm một số field ngoài projection/cấm; chưa assert đủ mọi field requested trên mọi case',[IV,SC],'PARTIAL_EVIDENCE','GAP-08;GAP-09','Q-07','R-01;R-06','P0'),
(23,'UR-03','GET /items/qa_articles?search=spéciale','Editor','SRC-04;SRC-05','INV-05','Một kết quả mẫu; expected tính từ title GET nền, không suy mọi search/case/diacritics',[IV],'PARTIAL_EVIDENCE','GAP-08','Q-07','R-06','P1'),
(24,'UR-01;UR-06;UR-07','Rejected POST/PATCH/DELETE + read-back/row lookup','Editor invalid input;Reader;Anonymous','SRC-01;SRC-05','S6;INV-09;INV-11','Combined invalid POST không tạo row, Reader PATCH subset không đổi; chưa phủ toàn bộ write matrix',[IV,SC],'PARTIAL_EVIDENCE','GAP-02;GAP-05;GAP-06;GAP-07','Q-06','R-02;R-03','P0'),
(25,'UR-09','GET /items/qa_articles?fields=&aggregate={...}','Editor','SRC-05;SRC-06','INV-06;REPLAY:aggregate-query-robustness','Unknown-function-shape 500; empty/count controls 200; giữ assertion không 5xx',[IV,AGG],'FAIL_CANDIDATE','GAP-15','Q-06','R-07','P0'),
(26,'UR-09','10 CRUD operation + query/export/POST object-array theo schema','Editor;actor schema tương ứng','SRC-06;SRC-05;SRC-01','INV-07;RAW/GUIDED;REPLAY:contract-schema-candidates','Status/content/schema đối chiếu snapshot; bốn biểu hiện contract candidate; không coi là bốn product defect',[IV,CON,RAW,GUIDED],'FAIL_CANDIDATE','GAP-10','Q-03;Q-04;Q-05;Q-06','R-08','P0'),
]
techniques = {
    1:'Scenario/CRUD read-back',2:'Phân vùng + biên + required/null',3:'Phân vùng + biên + required/null',
    4:'Phân vùng enum + default/state',5:'Phân vùng + biên + kiểu',6:'Phân vùng/null + round-trip',
    7:'Phân vùng JSON/null + round-trip',8:'Round-trip + bảng quyền',9:'Phân vùng ID/null + relation',
    10:'State transition + invariant',11:'Positive operation acceptance',12:'Stateful invariant',13:'State transition + negative oracle',
    14:'Bảng quyền + positive acceptance',15:'Bảng quyết định row policy',16:'Bảng quyết định field policy',
    17:'Bảng quyền + read-back',18:'Bảng quyền + negative acceptance',19:'Phân vùng token + negative acceptance',
    20:'Fixture oracle + phân vùng filter',21:'Fixture oracle + biên/phân trang',22:'Projection + bảng quyền',
    23:'Fixture oracle + Unicode/search',24:'Invariant dữ liệu trước/sau',25:'Robustness + control/replay',26:'Schema-based/fuzzing + contract checks',
}
rows=[]
for n,ur,api,actor,source,tests,oracle,proof,status,gap,q,risk,priority in data:
    for p in proof: assert (REPO/p).is_file(),p
    rows.append({'BR':f'BR-{n:02d}','UR':ur,'AC':f'AC-{n:02d}','priority':priority,'risk':risk,
                 'API':api,'actor':actor,'source':source,'technique':techniques[n],
                 'existing_test_refs':tests,'oracle_and_limit':oracle,'evidence_artifacts':';'.join(proof),
                 'evidence_status':status,'gap_tasks':gap,'open_questions':q})
with (DOC/'01-traceability.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def cell(value): return value.replace('|','\\|').replace('\n',' ')
section='''
## Truy vết nghiệp vụ Phase 1 - cập nhật 18/10/2026

Phần này bổ sung chuỗi yêu cầu → quy tắc → API/actor → test/oracle → evidence/gap. Các bảng A-H phía trên được giữ nguyên như checkpoint lịch sử, không thay bằng kết quả ngày 18/10. Không có test mới được chạy khi biên soạn.

- [Đặc tả UR/BR/AC và rủi ro](hoan-thien/01-yeu-cau-va-dac-ta.md).
- [Review, câu hỏi mở và gap task](hoan-thien/01-review-dac-ta.md).
- [Ma trận CSV đầy đủ nguồn/ưu tiên/rủi ro](hoan-thien/01-traceability.csv).

Trạng thái evidence: **HISTORICAL_SAMPLE** = mẫu lịch sử chứng minh phần nêu trong oracle; **PARTIAL_EVIDENCE** = có mẫu nhưng thiếu lớp/đường kiểm hoặc oracle còn hạn chế; **CONFIG_ONLY** = có cấu hình, chưa có functional evidence trực tiếp được chọn; **FAIL_CANDIDATE** = có assertion failure/finding cần triage. Không nhãn nào là nghiệm thu toàn BR hoặc coverage thực thi 100%.

Mã S1-S6 và INV-01 đến INV-11 giữ nguyên. INV là mã trong tài liệu; report invariant dùng case_id dạng tên. SMOKE:<tên> chỉ vị trí kiểm tra đã có, không phải mã test mới. GAP-* là việc đề xuất, chưa được triển khai. Khi có Q-* chưa chốt thì không áp assertion cứng cho chi tiết đó.

| UR / BR / AC | API và actor | Kỹ thuật / test hiện có | Oracle và giới hạn | Evidence lịch sử / trạng thái | Việc thiếu / câu hỏi |
|---|---|---|---|---|---|
'''
for r in rows:
    links=[]
    for p in r['evidence_artifacts'].split(';'):
        if not p:continue
        rid=p.split('/')[2]
        links.append(f'[{rid}](../{p})')
    proof='; '.join(links) if links else 'Chỉ có nguồn cấu hình; chưa có functional evidence trực tiếp'
    vals=[f"{r['UR']} / {r['BR']} / {r['AC']}",f"{r['API']} — {r['actor']}",
          f"{r['technique']} / {r['existing_test_refs'] or 'Chưa có test trực tiếp'}",r['oracle_and_limit'],
          f"{proof}; **{r['evidence_status']}**",f"{r['gap_tasks']}; {r['open_questions'] or 'Không có Q riêng'}"]
    section+='| '+' | '.join(cell(v) for v in vals)+' |\n'
section+='''
### Truy vết yêu cầu kỹ thuật của người chạy lab (UR-10)

| Yêu cầu | Nguồn/kiểm chứng | Bằng chứng hiện có | Việc tiếp theo |
|---|---|---|---|
| TR-01 - Môi trường cô lập, actor đúng, ID động | lab.sh, fixture map, preflight và request test | [Phase 0](hoan-thien/00-hien-trang-va-baseline.md), INV-03/04 | GAP-11; không suy runtime healthy ngày 18/10 |
| TR-02 - Pin/provenance/raw bất biến | Manifest, metadata/hash/diff | [Evidence index](hoan-thien/00-evidence-index.csv), [schema inventory](hoan-thien/00-schema-inventory.json) | GAP-10/11; ghi giới hạn dirty tree |
| TR-03 - Snapshot/restore và dừng khi setup/restore lỗi | campaign guard và summary từng seed | [Campaign index](hoan-thien/00-campaign-index.csv) | GAP-11; kiểm chứng tích hợp khi sửa harness |
| TR-04 - Replay đủ precondition/chain | replay report và ID mapping | [Replay cases](replay-cases.md); Phase 0 có single-request replay | GAP-11; không gán full-chain khi chỉ replay request cuối |
| TR-05 - Bảo vệ secret/không bypass license | Quy tắc lab, config riêng, redaction/gói evidence | [Phụ thuộc và giới hạn](hoan-thien/00-quyet-dinh-va-phu-thuoc.md) | Rà soát gói chia sẻ thật; không đọc secret để viết đặc tả |
| TR-06 - Chạy lại và bàn giao trung thực | README, dependency, report/exit và dựng mới | [README](../README.md), Phase 0 và TR-01 đến TR-05 | GAP-11; Phase 4/9 xử lý helper ngoài repo và khả năng dựng mới |

### Ánh xạ invariant trong tài liệu với case_id thực tế

| Mã giữ nguyên | case_id trong report |
|---|---|
| INV-01 | auth-invalid-token |
| INV-02 | anonymous-denied |
| INV-03 | editor-crud |
| INV-04 | positive-operations |
| INV-05 | query-fixture |
| INV-06 | aggregate-query-robustness |
| INV-07 | contract-schema-candidates |
| INV-08 | relation-nullification |
| INV-09 | invalid-field-rejection |
| INV-10 | reader-visibility |
| INV-11 | reader-write |

Không cộng số dòng UR/BR/test/replay để tính số testcase hoặc defect. Việc mọi BR có đường truy vết chỉ chứng minh tài liệu không bỏ trống đường kiểm chứng, không chứng minh mọi lớp dữ liệu/operation đã được thực thi.
'''
trace=REPO/'docs/traceability.md'
original=trace.read_bytes()
backup=ROOT/'output/phase1-20261018/traceability-before.md'
assert not backup.exists(), 'Do not overwrite source backup'
backup.write_bytes(original)
assert b'## Truy v' not in original.split(b'\n',1)[-1] or 'Truy vết nghiệp vụ Phase 1' not in original.decode('utf-8')
intro=('\n> Bổ sung ngày 18/10/2026: xem phần "Truy vết nghiệp vụ Phase 1" ở cuối tệp và '
       '[đặc tả v0.1](hoan-thien/01-yeu-cau-va-dac-ta.md). '
       'Các trạng thái/checkpoint A-H dưới đây giữ nguyên mốc lịch sử; không phải kết quả chạy mới.\n')
pos=original.index(b'\n')+1
updated=original[:pos]+intro.encode('utf-8')+original[pos:]+section.encode('utf-8')
trace.write_bytes(updated)
# Exact preservation of original bytes outside the new note/section.
assert updated[:pos]+updated[pos+len(intro.encode('utf-8')):-len(section.encode('utf-8'))] == original
print(json.dumps({'BR_rows':len(rows),'csv':'docs/hoan-thien/01-traceability.csv','historical_traceability_bytes_preserved':True},ensure_ascii=False))
