# Bằng chứng 13 TC (trích từ `docs/coverage` trước khi xóa nhóm C)

Ngày trích: 23/11/2026. Các file dưới đây được **sao chép nguyên bản** (không sửa nội dung); hash SHA-256 của bản sao đã được đối chiếu với bản gốc trước khi ghi bảng này.

Bản gốc nằm trong bản sao lưu `backup-DAMH-truoc-thu-nho-K05-20261123.zip` và trong lịch sử Git (các file đã được theo dõi). Khung coverage/CI M1–M3 đã bị bỏ khỏi phạm vi K05; chỉ giữ phần bằng chứng của bộ 13 TC và RCA của TC13.

**Kết quả ghi trong nguồn (ngày 16/11/2026):** 12 PASS, 1 FAIL. TC13 (`P3-CONTRACT-QA_ARTICLES-OBJECT`) business PASS, contract FAIL (`response_schema_conformance`); giữ nguyên, không sửa expected. Đây là kết quả từ nguồn, tôi chưa chạy lại.

Run P10 này không có các file response thô (thư mục `python-http/`, 271 KB) và các file kiểm tra đơn vị của khung đã xóa; hai phần đó chỉ còn trong bản sao lưu.

| Thư mục | File | Nguồn gốc (trong `docs/coverage/`) | SHA-256 | Byte |
|---|---|---|---|---:|
| `chon-13-tc` | `README.md` | `baselines/M1-REGRESSION-13-v1/README.md` | `a08167b6e3b8eeb8c7985a6f54a1516509dc160c4e26cb735dd3bb8040e30c57` | 2003 |
| `chon-13-tc` | `scope.json` | `baselines/M1-REGRESSION-13-v1/scope.json` | `2961dba2c0253e13e7afe20e0ae5769c73578ba8539b57297a50d30fb573d8be` | 1074 |
| `chon-13-tc` | `selection-manifest.json` | `baselines/M1-REGRESSION-13-v1/selection-manifest.json` | `2506e9743de3ccbdeadf8162ee708809dec0b14179456123829bf7c76c36335f` | 3700 |
| `chay-p10-20261116` | `README.md` | `runs/P10-20261116-02/README.md` | `e1a89adb214bf6056e12e7d38dc2435bddf0543053016d5f27a3970d6913f58f` | 6627 |
| `chay-p10-20261116` | `run-report.json` | `runs/P10-20261116-02/run-report.json` | `632821602c248bbc181fff573317d1ca9cca8f7d7d799df010b65113008e4a2e` | 5438 |
| `chay-p10-20261116` | `designed-report.json` | `runs/P10-20261116-02/designed-report.json` | `c45d66a9031f94d39ddd7f3d5828c29c4789c61d4c49a4b18bf4b3ac10a30e7b` | 63834 |
| `chay-p10-20261116` | `scenario-report.json` | `runs/P10-20261116-02/scenario-report.json` | `f48906a7ad80f57eec9da1d5503abbcfcac304367acb75e4d6fefc9a00757929` | 1542 |
| `chay-p10-20261116` | `scenario-outcomes.json` | `runs/P10-20261116-02/scenario-outcomes.json` | `e9a4d42e79430190ccae0c80138e9e40b9a1cdd250cba14fe28ed23651654b7c` | 72 |
| `chay-p10-20261116` | `selection-manifest.json` | `runs/P10-20261116-02/selection-manifest.json` | `f50ba2fabd915e6cd9826260f6ca1a595973ad8a5776eca156eb78ac0879baa5` | 4175 |
| `chay-p10-20261116` | `runtime-metadata.json` | `runs/P10-20261116-02/runtime-metadata.json` | `82bffb4e5dc2a3a32c7856ce8bf3076996ac885f7d985faa894b184415e66936` | 1753 |
| `chay-p10-20261116` | `database-oracle.json` | `runs/P10-20261116-02/database-oracle.json` | `dfcb3eda836a35c9476991db7e3c0b4b006d8f0f71a887e096d37cfb9ebcb3d9` | 112 |
| `chay-p10-20261116` | `preflight-before.json` | `runs/P10-20261116-02/preflight-before.json` | `96de747b4e53f7e4389a477c3ee0afdf285c7e012d68a86d01b924f283153a8c` | 4162 |
| `chay-p10-20261116` | `preflight-after.json` | `runs/P10-20261116-02/preflight-after.json` | `96de747b4e53f7e4389a477c3ee0afdf285c7e012d68a86d01b924f283153a8c` | 4162 |
| `chay-p10-20261116` | `case-P3-ST-01.json` | `runs/P10-20261116-02/case-P3-ST-01.json` | `0214a4ad11ceb2bc781de7dab6a2204ed976dfcbd77e1db68f826ee2b838dd48` | 7956 |
| `chay-p10-20261116` | `case-P3-AUTHZ-DR-047.json` | `runs/P10-20261116-02/case-P3-AUTHZ-DR-047.json` | `148971aba32afa232b8da139dcb26e1be55504d6503242ea5213a510d108d13a` | 7228 |
| `chay-p10-20261116` | `case-P3-SCORE-POST-MINUS1.json` | `runs/P10-20261116-02/case-P3-SCORE-POST-MINUS1.json` | `68a18bac979703a0261c87c6cd442fddd91a0a86f81284d63958ab459229436f` | 8177 |
| `chay-p10-20261116` | `case-P3-SCORE-POST-0.json` | `runs/P10-20261116-02/case-P3-SCORE-POST-0.json` | `4bb9de0257fc17679a26e4f7c371c0bb2cd2e7e67390733c884766e14ff92fec` | 7989 |
| `chay-p10-20261116` | `case-P3-SCORE-POST-5.json` | `runs/P10-20261116-02/case-P3-SCORE-POST-5.json` | `feaada005291b68f8ff70f3f406f630f04ec73eb4630500d18d9cdfc2f2d79ae` | 7986 |
| `chay-p10-20261116` | `case-P3-SCORE-POST-6.json` | `runs/P10-20261116-02/case-P3-SCORE-POST-6.json` | `8473386e644b582e9518f4d3c1de64ba85a66fe11e82dd9b4520c86a551f82ae` | 8165 |
| `chay-p10-20261116` | `case-P3-CONTRACT-QA_ARTICLES-OBJECT.json` | `runs/P10-20261116-02/case-P3-CONTRACT-QA_ARTICLES-OBJECT.json` | `0e4b81971ffc706387ed997db9ce99f1462fb6a3199617265cea5f29b0751349` | 8596 |
| `chay-p10-20261116` | `P10.md` | `handoffs/P10.md` | `aa0df1f0e3dbc96037b4f8639ff8bf7ac491a4143d43136d5d0bf18b0063c39a` | 7912 |
| `rca-tc13` | `README.md` | `acceptance/M2-TC13-20261116/README.md` | `0853cbc5a262ad63fb13ee8da4d02034e35bc763e667db1e24b3f392e723f4f9` | 4665 |
| `rca-tc13` | `api_src_controllers_items.ts.excerpt.txt` | `acceptance/M2-TC13-20261116/api_src_controllers_items.ts.excerpt.txt` | `77e4f2be7afb436db38ac9756353b7ec17d8ff2c0b02b9eed0c8ca6a71a107ef` | 1339 |
| `rca-tc13` | `api_src_services_items.ts.excerpt.txt` | `acceptance/M2-TC13-20261116/api_src_services_items.ts.excerpt.txt` | `e29952c3ea975079256ed9c72628e2747b49e4ee4db4c419b99e8fc4f8f37a85` | 1594 |
| `rca-tc13` | `api_src_services_specifications.ts.excerpt.txt` | `acceptance/M2-TC13-20261116/api_src_services_specifications.ts.excerpt.txt` | `99a561b39b7f2abae4bcebc4ddf76100743f5ffc8e30b0b38d0d2444ff617b89` | 3061 |
| `rca-tc13` | `audit-evidence.json` | `acceptance/M2-TC13-20261116/audit-evidence.json` | `58ddd112983fcf35b27bf964b18cf2358e21a9f1efe1a65f4ed9f44ab240d8f3` | 1941 |
| `rca-tc13` | `gap-update.json` | `acceptance/M2-TC13-20261116/gap-update.json` | `5cc5f1e093b7da5a585123c1a433a815b7d10a6c6689037e063652106e9a69ec` | 762 |
| `rca-tc13` | `response-metadata.json` | `acceptance/M2-TC13-20261116/response-metadata.json` | `cb270fae5d79be8087cd13296062e152e0807b3af023775e1331ec1ff304cc6d` | 113 |
| `rca-tc13` | `revalidation.json` | `acceptance/M2-TC13-20261116/revalidation.json` | `08bcd350e52df099161ae73d97716b89648aafbaf3f1b8898a35071a3d007b6d` | 644 |
| `rca-tc13` | `source-index.json` | `acceptance/M2-TC13-20261116/source-index.json` | `0868d9da08d3c0537826ba2159ed96077e8b634e8ca6e0b89293e6d42f3bc6dd` | 912 |
| `rca-tc13` | `verification.json` | `acceptance/M2-TC13-20261116/verification.json` | `5399d2225ac26e17e10959bf816bdc8e4244d231e9bc8150450a680bdf05cb49` | 1911 |
| `contract-recheck` | `README.md` | `acceptance/M2-REVIEW-20261116/README.md` | `a1cb7e14446c7acb6eab3a8111902f11a135d2f2cc3213ca0a3b6ff1a2103dd1` | 7055 |
| `contract-recheck` | `contract-recheck.json` | `acceptance/M2-REVIEW-20261116/contract-recheck.json` | `a728104fb7fd98cee1243ae2e31b7ac598c0d42707551c2bbafcc7986fd29ee3` | 21344 |
| `contract-recheck` | `contract-recheck-exit.json` | `acceptance/M2-REVIEW-20261116/contract-recheck-exit.json` | `e2ace30a5dc5cd66e9e1fc907637edd1c5ffb5b80441957b495b9344356715ce` | 180 |
