"""Recompute P6 measurements from immutable artifacts; export only safe counters."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import itertools
import json
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RUNS = ROOT / "artifacts/runs"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def table(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def spread(values):
    return {"median": statistics.median(values), "min": min(values), "max": max(values)}


def query():
    protocol = read(HERE / "protocol-v1.json")
    freeze = read(HERE / "measurement-source-freeze.json")
    assert all(sha(ROOT / e["path"]) == e["sha256"] for e in freeze["files"])
    rows = []
    for rid in protocol["primary_experiment"]["planned_run_ids"]:
        base = RUNS / rid
        report = read(base / "cost-query-report.json")
        outcomes = read(base / "component-outcomes.json")
        timing = read(base / "invocation-timing.json")
        shell = [json.loads(line) for line in (base / "shell-http.ndjson").read_text().splitlines()]
        meta = read(base / "metadata.json")
        assert report["status"] == report["verification"] == "PASS"
        assert outcomes["runner_exit_code"] == outcomes["restore_exit_code"] == timing["exit_code"] == 0
        assert report["passed_pairs"] == 37 and not report["not_run"]
        assert meta["actor"] == "editor" and meta["runtime_profile"] == "phase6-20261018"
        assert report["protocol_sha256"] == sha(HERE / "protocol-v1.json")
        target_count = 36 if report["selection"] == "exhaustive" else 9
        assert report["selected"] == report["passed"] == report["target_attempts"] == target_count
        assert report["target_statuses"] == {"200": target_count}
        rows.append({"run_id": rid, "round": int(rid.split('-r')[1].split('-')[0]),
                     "set": report["selection"], "target_requests": target_count,
                     "target_seconds": report["target_wall_seconds"],
                     "target_api_seconds_sum": sum(r["api_elapsed_seconds"] for r in report["results"]),
                     "python_http_attempts": report["python_http_attempts"], "shell_http_attempts": len(shell),
                     "total_sut_http_attempts": report["python_http_attempts"] + len(shell),
                     "setup_seconds": report["setup_seconds"], "verification_seconds": report["verification_seconds"],
                     "runner_seconds": report["runner_wall_seconds"], "invocation_seconds": timing["elapsed_seconds"],
                     "metadata_seconds": meta["duration_seconds"], "passed": report["passed"],
                     "pairs": report["passed_pairs"], "restore_exit_code": outcomes["restore_exit_code"]})
    for name in ["fixture-ids-input.json", "schema-editor-input.json", "schema-reader-input.json"]:
        assert len({sha(RUNS / r["run_id"] / name) for r in rows}) == 1
    for name in ["baseline-articles.json", "baseline-categories.json"]:
        snapshots = [sorted(read(RUNS / r["run_id"] / name)["data"], key=lambda x: x["id"]) for r in rows]
        assert all(s == snapshots[0] for s in snapshots)
    table("query-trials.csv", rows)
    paired = []
    for round_ in range(1, 4):
        a = next(r for r in rows if r["round"] == round_ and r["set"] == "exhaustive")
        b = next(r for r in rows if r["round"] == round_ and r["set"] == "pairwise")
        paired.append({"round": round_, **{key + "_reduction_percent": (1 - b[key] / a[key]) * 100 for key in
                      ["target_requests", "target_seconds", "total_sut_http_attempts", "invocation_seconds"]}})
    table("paired-reductions.csv", paired)
    result = {"all_six_passed": True, "source_freeze_verified": True,
              "identical_inputs_and_baselines": True, "target_requests_total": sum(r["target_requests"] for r in rows),
              "unique_catalog_cases": 36, "by_set": {}, "paired_reductions": {}}
    for selected in ["exhaustive", "pairwise"]:
        group = [r for r in rows if r["set"] == selected]
        result["by_set"][selected] = {key: spread([r[key] for r in group]) for key in
            ["target_requests", "target_seconds", "target_api_seconds_sum", "total_sut_http_attempts", "runner_seconds", "invocation_seconds"]}
    for key in paired[0]:
        if key != "round":
            result["paired_reductions"][key] = spread([r[key] for r in paired])
    write("query-analysis.json", result)
    model = read(ROOT / "scripts/data/query-cost-model-v1.json")
    combinations = lambda rows: {(a, r["factors"][a], b, r["factors"][b]) for r in rows
                                  for a, b in itertools.combinations([f["name"] for f in model["factors"]], 2)}
    feasible = combinations(model["cases"])
    pairwise = combinations([r for r in model["cases"] if r["pairwise"]])
    write("pair-coverage.json", {"feasible": sorted(feasible), "pairwise_covered": sorted(pairwise),
                                 "missing_pairs": sorted(feasible - pairwise),
                                 "cases_pairwise": [r["id"] for r in model["cases"] if r["pairwise"]]})
    return rows, result


def historical():
    rows, details = [], []
    for profile, rid in [("raw", "20261011T085034Z-76481"), ("guided", "20261011T095117Z-89079")]:
        meta = read(RUNS / rid / "metadata.json")
        for seed in [101, 202, 303]:
            base = RUNS / rid / profile / f"seed-{seed}"
            report = read(base / "schemathesis-report.json")
            coverage = read(base / "schemathesis-coverage.json")["summary"]
            summary = read(base / "campaign-summary.json")
            events = base / "schemathesis-events.ndjson"
            # Never export headers, bodies or arbitrary generated paths. Recorder references
            # may repeat; identify a recorded interaction by case ID + request timestamp.
            seen, statuses, phases = set(), Counter(), Counter()
            references = 0
            for line in events.open(encoding="utf-8"):
                event = json.loads(line).get("ScenarioFinished", {})
                for key, interaction in (event.get("recorder") or {}).get("interactions", {}).items():
                    references += 1
                    identity = (key, interaction.get("timestamp"))
                    if identity in seen:
                        continue
                    seen.add(identity)
                    statuses[str((interaction.get("response") or {}).get("status_code"))] += 1
                    phases[event.get("phase")] += 1
            accepted = sum(n for code, n in statuses.items() if code.isdigit() and 200 <= int(code) < 300)
            cases = report["test_cases"]
            row = {"run_id": rid, "profile": profile, "seed": seed, "runner_seconds": report["running_time"],
                   "stop_reason": report["stop_reason"], "runner_exit_code": summary["runner_exit_code"],
                   "restore_exit_code": summary["restore_exit_code"], "tested_operations": report["operations"]["tested"],
                   "generated_cases": cases["generated"], "unique_check_failures": cases["unique_failures"],
                   "cases_errored": cases["errored"], "recorded_http_interactions": len(seen),
                   "recorded_2xx": accepted, "recorded_2xx_percent": accepted / len(seen) * 100,
                   "parameter_coverage_percent": coverage["parameters"]["percent"],
                   "keyword_coverage_percent": coverage["keywords"]["percent"],
                   "response_coverage_percent": coverage["responses"]["percent"],
                   "examples_coverage_percent": coverage["examples"]["percent"]}
            rows.append(row)
            details.append({**row, "harness_sha": meta["harness_sha"], "working_tree": meta["working_tree"],
                            "schema_sha256": summary["schema_sha256"], "budget": summary["budget"],
                            "coverage_summary": coverage, "failure_types": report["failures"],
                            "valid_rates_tool_only": report.get("valid_rates"),
                            "recorded_statuses": dict(statuses), "recorded_interactions_by_phase": dict(phases),
                            "recorder_references": references, "recorded_unique_interactions": len(seen),
                            "source_files": [{"path": str((base / name).relative_to(ROOT).as_posix()),
                                              "sha256": sha(base / name)} for name in
                                             ["campaign-summary.json", "schemathesis-report.json", "schemathesis-coverage.json",
                                              "schemathesis-events.ndjson", "baseline-articles.json", "baseline-categories.json"]]})
    table("historical-raw-guided.csv", rows)
    write("historical-raw-guided-audit.json", {"post_hoc": True,
          "interaction_metric": "unique persisted recorder interactions by (case ID, timestamp), not all wire requests incl auth/setup/restore or in-flight requests at timeout",
          "defects_per_hour": None, "reason": "No per-cohort root-cause deduplication sufficient for a qualified defect numerator",
          "cohort": details, "by_profile": {p: {k: spread([r[k] for r in rows if r["profile"] == p]) for k in
             ["runner_seconds", "generated_cases", "unique_check_failures", "recorded_http_interactions", "recorded_2xx_percent",
              "parameter_coverage_percent", "keyword_coverage_percent", "response_coverage_percent"]} for p in ["raw", "guided"]}})
    alternative = []
    for seed in [101, 202, 303]:
        base = RUNS / "20261012T122826Z-22781/guided" / f"seed-{seed}"
        s = read(base / "campaign-summary.json")
        alternative.append({"seed": seed, "termination": s["termination"], "runner_exit_code": s["runner_exit_code"],
                            "restore_exit_code": s["restore_exit_code"], "runner_seconds": s["schemathesis"]["running_time"]})
    write("alternative-interrupted-cohort.json", {"run_id": "20261012T122826Z-22781", "included_in_primary": False,
                                                  "reason": "seed 202 interrupted, budget not executed equally", "campaigns": alternative})


if __name__ == "__main__":
    query()
    historical()
    print("P6 analysis regenerated; all six trial assertions passed.")
