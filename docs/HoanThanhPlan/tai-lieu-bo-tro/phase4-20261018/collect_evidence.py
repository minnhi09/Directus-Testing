"""One-off Phase 4 evidence inventory. Does not call API, Docker, or read lab.env."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def read(path):
    return json.loads(path.read_bytes())


def write(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    runs = []
    copied = []
    whitelist = {"metadata.json", "harness-inputs.json", "fixture-ids-input.json", "fixture-ids-output.json",
        "execution-config.json", "baseline-articles.json", "baseline-categories.json", "database-oracle.json",
        "preflight.json", "designed-report.json", "invariant-report.json", "scenario-report.json",
        "component-outcomes.json", "scenario-outcomes.json", "target-verification.json", "schema-manifest.json",
        "contract-validation.json"}
    for folder in sorted((ROOT / "artifacts/runs").iterdir()):
        metadata = folder / "metadata.json"
        if not metadata.exists():
            continue
        meta = read(metadata)
        if meta.get("runtime_profile") != "phase4-20261018" or meta["status"] == "running":
            continue
        entry = {k: meta.get(k) for k in ["run_id", "command", "status", "exit_code", "started_at", "finished_at", "duration_seconds", "harness_sha", "working_tree"]}
        entry["outcomes"] = read(folder / "component-outcomes.json") if (folder / "component-outcomes.json").exists() else None
        entry["recorded_response_files"] = {"python": len(list((folder / "python-http").glob("*.json"))), "bash": len(list(folder.glob("http-*.json")))}
        for name in ["designed", "invariant", "scenario"]:
            report = folder / (name + "-report.json")
            if not report.exists():
                continue
            report_data = read(report)
            cases = report_data.get("cases", report_data.get("scenarios", []))
            entry[name] = {"summary": dict(Counter(c["status"] for c in cases)), "stop_reason": report_data.get("stop_reason"), "not_run": report_data.get("selected_not_run", []), "error_type": report_data.get("error_type"), "error": report_data.get("error"), "case_ids": [c["id"] for c in cases]}
            if name == "designed":
                entry[name]["steps_by_stage"] = dict(Counter(s["stage"] for c in cases for s in c["steps"]))
        entry["replay"] = [{k: read(p).get(k) for k in ["case_id", "status", "replay_scope", "target_sent", "sequence_replayed", "source_status", "actual_status", "matched_checks", "error"]} for p in folder.glob("reproducer-schemathesis-*.json")]
        dest = HERE / "evidence" / folder.name
        dest.mkdir(parents=True, exist_ok=True)
        for path in folder.iterdir():
            if path.name not in whitelist and not (path.name.startswith("reproducer-") and path.suffix == ".json"):
                continue
            if path.stat().st_size == 0:  # unsuccessful optional DB oracle, retained in original run
                continue
            data = path.read_bytes()
            # Reports should contain actor labels and redactions, never bearer tokens.
            if re.search(rb"(?i)Bearer\s+[A-Za-z0-9_.-]{30,}", data):
                raise RuntimeError("Credential-like bearer value in selected artifact: " + str(path))
            shutil.copyfile(path, dest / path.name)
            copied.append({"source": path.relative_to(ROOT).as_posix(), "copy": (dest / path.name).relative_to(HERE).as_posix(), "sha256": sha(path)})
        runs.append(entry)
    write(HERE / "run-index.json", {"schema": 1, "runs": runs, "copies": copied, "request_count_note": "Response files and per-case steps are measured counts, not the total HTTP requests (login/setup/outer restore differ)."})
    completed = [r for r in runs if r.get("designed", {}).get("summary") == {"passed": 58} and r["exit_code"] == 0]
    repeat = {}
    if len(completed) >= 2:
        a, b = completed[-2:]
        fa, fb = [ROOT / "artifacts/runs" / r["run_id"] for r in (a, b)]
        ca, cb = [read(f / "designed-report.json")["cases"] for f in (fa, fb)]
        verdicts = lambda cases: [(c["id"], c["status"], c["verdicts"], c["cleanup_status"]) for c in cases]
        repeat = {"runs": [a["run_id"], b["run_id"]], "same_harness_inputs": read(fa / "harness-inputs.json") == read(fb / "harness-inputs.json"), "same_execution_config": read(fa / "execution-config.json") == read(fb / "execution-config.json"), "same_baseline_snapshot": all(read(fa / n) == read(fb / n) for n in ["baseline-articles.json", "baseline-categories.json"]), "same_order_and_verdicts": verdicts(ca) == verdicts(cb), "different_generated_probe_ids_expected": True, "scope": "two sequential runs on this Windows machine; does not establish statistical flake rate"}
        with (HERE.parent.parent / "04-ket-qua-case.csv").open("w", newline="", encoding="utf-8-sig") as output:
            fields = ["id", "group", "BR", "AC", "readiness", "status", "cleanup", "run_id", "artifact"]
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            by_id = {c["id"]: c for c in cb}
            for case in read(ROOT / "scripts/data/test-catalog-v1.json"):
                actual = by_id.get(case["id"], {})
                writer.writerow(dict(id=case["id"], group=case["group"], BR=case["BR"], AC=case["AC"], readiness=case["oracle_readiness"], status=actual.get("status", "NOT_RUN"), cleanup=actual.get("cleanup_status", "NOT_RUN"), run_id=b["run_id"] if actual else "", artifact=f"artifacts/runs/{b['run_id']}/case-{case['id']}.json" if actual else ""))
    write(HERE / "repeatability.json", repeat)
    historical = read(ROOT / "docs/HoanThanhPlan/00-evidence-hashes.json")["files"]
    mismatches = [x["path"] for x in historical if not (ROOT / x["path"]).exists() or sha(ROOT / x["path"]) != x["sha256"]]
    write(HERE / "historical-integrity.json", {"files_checked": len(historical), "mismatches": mismatches})
    with zipfile.ZipFile(HERE / "selected-runtime-evidence.zip", "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in copied:
            archive.write(ROOT / entry["source"], entry["source"])
        # Body artifacts of new Python runs never contain authentication responses.
        for run in runs:
            folder = ROOT / "artifacts/runs" / run["run_id"]
            for path in [*folder.glob("case-P3-*.json"), *(folder / "python-http").glob("*.json"), *folder.glob("schema-*-input.json")]:
                archive.write(path, path.relative_to(ROOT).as_posix())
    print(json.dumps({"runs": len(runs), "historical_files_unchanged": len(historical) - len(mismatches), "repeatability": repeat}, ensure_ascii=False))


if __name__ == "__main__":
    main()
