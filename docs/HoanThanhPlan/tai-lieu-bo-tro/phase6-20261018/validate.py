"""Read-only P6 artifact/document validation, with a saved result."""
from pathlib import Path
import csv
import hashlib
import json
import re
import zipfile
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DOCS = ROOT / "docs/HoanThanhPlan"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
checks = {}
errors = []

for name, archive in [("source-after-manifest.json", "source-after.zip"), ("evidence-index.json", "evidence-selected.zip")]:
    records = read(HERE / name)["files"]
    with zipfile.ZipFile(HERE / archive) as z:
        assert z.testzip() is None
        for entry in records:
            relative = entry.get("path", entry.get("copy"))
            target = ROOT / relative if "path" in entry else HERE / relative
            assert sha(target) == entry["sha256"]
            assert hashlib.sha256(z.read(relative)).hexdigest() == entry["sha256"]
            if "source" in entry:
                assert sha(ROOT / entry["source"]) == entry["sha256"]
        assert set(z.namelist()) == {e.get("path", e.get("copy")) for e in records}
    checks[archive] = {"files": len(records), "manifest_and_source_hashes": "PASS", "crc": "PASS", "sha256": sha(HERE / archive)}

old = read(DOCS / "00-evidence-hashes.json")["files"]
assert all(sha(ROOT / entry["path"]) == entry["sha256"] for entry in old)
checks["original_evidence"] = {"checked": len(old), "unchanged": len(old)}
freeze = read(HERE / "measurement-source-freeze.json")["files"]
assert all(sha(ROOT / entry["path"]) == entry["sha256"] for entry in freeze)
checks["measurement_freeze"] = {"checked": len(freeze), "unchanged": True}
before = read(HERE / "source-manifest-before.json")["files"]
assert all(sha(ROOT / entry["path"]) == entry["sha256"] for entry in before
           if entry["path"] in ["scripts/designed_cases.py", "scripts/invariants.py"])
checks["shared_oracle"] = "Phase 4 Runner and Api unchanged"

links = 0
for path in [DOCS / n for n in ["06-toi-uu-chi-phi.md", "README.md", "Ke_hoach_hoan_thien_R06_K05_theo_phase.md",
                                "dieu-chinh-pham-vi-phase5-phase7.md", "tai-lieu-bo-tro/README.md"]]:
    for destination in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if destination.startswith(("http:", "https:", "#", "mailto:")):
            continue
        destination = destination.strip("<>").split("#")[0]
        if destination:
            links += 1
            if not (path.parent / destination).exists():
                errors.append(f"Broken link {path.relative_to(ROOT)}: {destination}")
checks["local_links"] = {"checked": links, "broken": len(errors)}

with (DOCS / "06-ket-qua-case.csv").open(encoding="utf-8-sig") as stream:
    rows = list(csv.DictReader(stream))
with (DOCS / "04-ket-qua-case.csv").open(encoding="utf-8-sig") as stream:
    previous = list(csv.DictReader(stream))
assert len(rows) == 257 and sum(r["status"] == "passed" for r in rows) == 94
assert sum(r["status"] == "NOT_RUN" for r in rows) == 163
assert all(a == b for a, b in zip(previous, rows) if a["group"] != "pairwise-reference")
checks["catalog"] = {"rows": 257, "passed": 94, "not_run": 163, "new_unique_cases": 36, "other_phase4_rows_preserved": True}

for seed in [101, 202, 303]:
    summary = read(ROOT / f"artifacts/runs/20261012T190350Z-1047/guided/seed-{seed}/campaign-summary.json")
    assert summary["termination"] == "max_time" and summary["budget"]["max_time_seconds"] == 60
assert not (ROOT / "runtime/.mutation-lock").exists()
checks["runtime"] = {"mutation_lock_released": True, "replay_source_pilot_three_seeds_max_time_60": True}
checks["executed_checks"] = {"host_offline": "18 PASS", "pinned_offline": "18 PASS", "bash_syntax": "PASS",
                              "real_query_trials": "6 PASS, runner/restore 0"}
result = {"created_at": datetime.now(timezone.utc).isoformat(), "status": "PASS" if not errors else "FAIL",
          "checks": checks, "errors": errors, "scope": "P6 only; P7 removed; P8/P9 not executed; no commit/push",
          "validation_note": "Historical CSV uses UTF-8 BOM; read both CSVs with utf-8-sig. Initial ad-hoc validator was corrected without changing experiment data."}
(HERE / "validation.json").write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
print(json.dumps(result, ensure_ascii=False, indent=2))
assert not errors
