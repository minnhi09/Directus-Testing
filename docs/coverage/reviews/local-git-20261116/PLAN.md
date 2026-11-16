# Kế hoạch commit local P00–P15 — 16/11/2026

Người dùng đã cho phép commit local, không push/merge/PR. Giữ cấu hình author/committer và ngày thực, không sửa lịch sử. Các commit đóng gói thay đổi đã có; không quy tác giả nội dung từng phần từ việc đóng gói.

[File/dependency từng commit](commit-plan.json), [security review](security-review.json), [file không chọn](excluded-files.json). Kết quả thực gồm hash/files/checks/status lưu ở runtime/git-local-20261116/results.json để tránh self-reference commit hash.

| Thứ tự | Conventional Commit | Dependency | File |
|---|---|---|---|
| 01 | chore(git): preserve evidence bytes and exclude local caches | Không | 2 |
| 02 | docs: record Directus testing scope and source inputs | 1 | 51 |
| 03 | test(harness): add guarded fixture oracles and reusable case helpers | 1 | 16 |
| 04 | feat(coverage): define inventory contracts and canonical traceability | 2,3 | 410 |
| 05 | test(regression): add isolated P09 preflight and regression13 adapters | 3,4 | 9 |
| 06 | testdata(evidence): preserve regression and contract findings | 4,5 | 764 |
| 07 | feat(coverage): validate immutable inputs and run offline checks | 3,4,6 | 19 |
| 08 | test(contract): capture and diagnose actor-scoped HTTP evidence | 3,5,6,7 | 6 |
| 09 | test(rest): add bounded raw and guided contract pilot tooling | 5,8 | 2 |
| 10 | ci: gate private profiles and publish complete M2 diagnostics | 5,6,7,8,9 | 5 |
| 11 | docs: record local commit provenance and verification | 1,2,3,4,5,6,7,8,9,10 | 4 |

Helper/dataset nằm ở nhóm trước; từng nhóm có check phù hợp. Tài liệu lịch sử có link tới sản phẩm nhóm sau, nên chỉ cây cuối được gọi là đầy đủ cho static/CI. Commit không đồng nghĩa phase COMPLETE hoặc acceptance PASS.

TC13 FAIL, raw OAS, expected và report giữ nguyên; raw whitespace/blank EOF được bảo toàn cùng hash. Git attributes chỉ chuẩn hóa implementation LF. Hai PDF nguồn chính thức giống byte; ngoại lệ chính xác cho root PDF giữ source_ref gốc. Private env/license, runtime/cache/tmp, slides và ZIP chưa audit không stage. Không chạy SUT/campaign hoặc sửa Directus để commit. README.md và docs/traceability.md đang sửa ngoài scope được giữ nguyên chưa commit.

Kiểm dependency từ index phát hiện test trace dùng coverage_offline; đã đổi thứ tự hai nhóm chưa commit và giữ nguyên failed-attempt log. Không sửa expected/test hoặc lịch sử đã có.

## Kết quả trước commit hồ sơ cuối

10commit chức năng đã tạo theo author/committer cấu hình sẵn, không override ngày. Commit hồ sơ hiện tại thêm bản kê; hash của chính nó được ghi ngoài Git trong results.json sau khi commit.

| Nhóm | Hash | Message | File |
|---|---|---|---|
| 01 | 59a2af76d365a02a877262592d0c9d2dd8d55fe6 | chore(git): preserve evidence bytes and exclude local caches | 2 |
| 02 | 188f604d26f05fb7ca2dde605952144f02c0acd1 | docs: record Directus testing scope and source inputs | 51 |
| 03 | a9efb305ac0e9f69f092a78d9f40167a4927681e | test(harness): add guarded fixture oracles and reusable case helpers | 16 |
| 04 | 404b2aa3b27bdc49d1c2762e0073a81a4b69e062 | feat(coverage): define inventory contracts and canonical traceability | 410 |
| 05 | 09643acf7c0fd12eafb79a145e65115f91e2737a | test(regression): add isolated P09 preflight and regression13 adapters | 9 |
| 06 | 2c6ec0ff74059b48703f71f98d880d73c98eb61f | testdata(evidence): preserve regression and contract findings | 764 |
| 07 | a63862f8e7af5f5f86844a6ea1077467998d2950 | feat(coverage): validate immutable inputs and run offline checks | 19 |
| 08 | d6e467e4bdd12c91d4209baea2df7307c86d9fcd | test(contract): capture and diagnose actor-scoped HTTP evidence | 6 |
| 09 | b43653467ea71bc10bc5229933d8a51a69a63e97 | test(rest): add bounded raw and guided contract pilot tooling | 2 |
| 10 | e6473d9d4a777a6244253193e7db4e65f5a915df | ci: gate private profiles and publish complete M2 diagnostics | 5 |

Bản index nhóm10 đạt136/136offline và8/8static. Việc kiểm độc lập đã phát hiện thiếu dependency giữa trace và coverage trước khi commit; đã đổi thứ tự nhóm chưa commit, không sửa expected/test hoặc lịch sử. TC13FAIL/P14INCOMPLETE giữ nguyên; CI remote chưa chạy.

Chưa commit README.md/docs/traceability.md đang viết lại và các tài liệu/artefact ngoài scope trong excluded-files.json. lab.sh/invariants.py giữ mode100755 trong Git; recovery Windows vẫn báomode100644 trên filesystem với core.filemode=true. Nội dung đã commit, không thay local/global config để che khác biệt này.
