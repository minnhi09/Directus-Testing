"""Aggregate actual P8 results without turning native failures into passes."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DOCS = ROOT / "docs/HoanThanhPlan"
RUNS = ROOT / "artifacts/runs"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def csv_read(path):
    with path.open(encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write(name, data):
    (HERE / name).write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def csv_write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def aggregate():
    catalog = read(ROOT / "scripts/data/test-catalog-v1.json")
    designs = {c["id"]: c for c in catalog}
    latest, executions, runs = {}, [], []
    for label in ["short-r1", "short-r2", "assertable", "query-extra", "fk-post", "fk-patch", "time-utc", "time-offset"]:
        rid = "p8-20261018-" + label
        base = RUNS / rid
        report = read(base / "designed-report.json")
        outcome = read(base / "component-outcomes.json")
        assert report["execution_complete"] and not report["selected_not_run"]
        assert outcome["restore_exit_code"] == 0
        assert all(c["cleanup_status"] == "passed" for c in report["cases"])
        runs.append({"run_id": rid, "type": "designed", "selection": label,
                     "summary": report["summary"], "outcomes": outcome,
                     "seconds": read(base / "metadata.json")["duration_seconds"]})
        for c in report["cases"]:
            record = {"id": c["id"], "status": c["status"], "cleanup": c["cleanup_status"], "run_id": rid,
                      "artifact": f"artifacts/runs/{rid}/case-{c['id']}.json", "verdicts": c["verdicts"],
                      "reason": c.get("reason", ""), "error_type": c.get("error_type", ""),
                      "contract_checks": c.get("contract_checks", [])}
            latest[c["id"]] = record
            executions.append(record)
    a, b = [read(RUNS / ("p8-20261018-" + n) / "designed-report.json") for n in ["short-r1", "short-r2"]]
    repeat = {"ordered_case_ids_equal": [c["id"] for c in a["cases"]] == [c["id"] for c in b["cases"]],
              "verdicts_equal": [(c["status"], c["verdicts"], c["cleanup_status"]) for c in a["cases"]] ==
                                [(c["status"], c["verdicts"], c["cleanup_status"]) for c in b["cases"]]}
    for name in ["fixture-ids-input.json", "schema-editor-input.json", "schema-reader-input.json", "execution-config.json"]:
        repeat[name + "_equal"] = (RUNS / "p8-20261018-short-r1" / name).read_bytes() == (RUNS / "p8-20261018-short-r2" / name).read_bytes()
    for name in ["baseline-articles.json", "baseline-categories.json"]:
        repeat[name + "_equal"] = sorted(read(RUNS / "p8-20261018-short-r1" / name)["data"], key=lambda x: x["id"]) == sorted(read(RUNS / "p8-20261018-short-r2" / name)["data"], key=lambda x: x["id"])
    repeat["note"] = "Same code/templates/order/budget/fixture; temporary probe text and generated IDs may differ by run ID."
    assert all(v for v in repeat.values())
    write("repeatability.json", repeat)

    rid = "p8-20261018-query-full"
    q = read(RUNS / rid / "cost-query-report.json")
    assert q["status"] == q["verification"] == "PASS" and q["passed"] == 36 and q["passed_pairs"] == 37
    assert read(RUNS / rid / "component-outcomes.json")["restore_exit_code"] == 0
    for c in q["results"]:
        latest[c["id"]] = {"id": c["id"], "status": "passed", "cleanup": "passed", "run_id": rid,
                            "artifact": f"artifacts/runs/{rid}/cost-query-report.json", "verdicts": {"business": "passed"}, "reason": ""}
    rows = []
    for c in catalog:
        result = latest.get(c["id"], {})
        rows.append({"id": c["id"], "group": c["group"], "BR": c["BR"], "AC": c["AC"],
                     "priority": c["priority"], "readiness": c["oracle_readiness"], "status": result.get("status", "NOT_RUN"),
                     "cleanup": result.get("cleanup", "NOT_RUN"), "run_id": result.get("run_id", ""),
                     "artifact": result.get("artifact", ""), "verdicts": json.dumps(result.get("verdicts", {}), sort_keys=True),
                     "reason": result.get("reason", "")})
    csv_write(DOCS / "08-ket-qua-case.csv", rows)
    disagreements = {id_: sorted({r["status"] for r in executions if r["id"] == id_})
                     for id_ in latest if len({r["status"] for r in executions if r["id"] == id_}) > 1}
    write("executions.json", {"runs": runs, "individual_executions_including_repeats": executions,
                              "status_disagreements_across_overlapping_designs": disagreements,
                              "latest_statuses": dict(Counter(r["status"] for r in rows)),
                              "unique_executed": len(latest), "catalog": len(rows)})

    br_rows = []
    for br in csv_read(DOCS / "03-traceability.csv"):
        ids = br["designed_case_ids"].split(";")
        counts = Counter(latest.get(i, {}).get("status", "NOT_RUN") for i in ids)
        br_rows.append({"BR": br["BR"], "priority": br["priority"], "designed_cases": len(ids),
                        "passed": counts["passed"], "failed": counts["failed"], "open": counts["open"],
                        "blocked": counts["blocked"], "not_run": counts["NOT_RUN"],
                        "assessment": "HAS_CASE_FAILURE" if counts["failed"] else "PARTIAL_EXECUTION" if counts["NOT_RUN"] else "HAS_OPEN" if counts["open"] else "HAS_BLOCKED" if counts["blocked"] else "ALL_MAPPED_CASES_PASSED",
                        "failure_dimensions": json.dumps(dict(Counter(k for i in ids for k, v in latest.get(i, {}).get("verdicts", {}).items() if v == "failed")), sort_keys=True),
                        "passed_ids": ";".join(i for i in ids if latest.get(i, {}).get("status") == "passed"),
                        "failed_ids": ";".join(i for i in ids if latest.get(i, {}).get("status") == "failed"),
                        "not_run_ids": ";".join(i for i in ids if i not in latest)})
    csv_write(DOCS / "08-truy-vet-ket-qua.csv", br_rows)

    for source, output, key in [("03-gia-tri-bien.csv", "boundary-coverage.csv", "case_id"),
                                ("03-bang-quyet-dinh-quyen.csv", "permission-coverage.csv", "case_id")]:
        result = []
        for row in csv_read(DOCS / source):
            actual = latest.get(row[key], {})
            result.append({**row, "P8_status": actual.get("status", "NOT_RUN"), "P8_run": actual.get("run_id", ""),
                           "P8_artifact": actual.get("artifact", "")})
        csv_write(HERE / output, result)

    # Explicit conservative links from each original partition to its field-focused
    # design cases. A passed representative is not proof of the whole input class.
    patterns = {
        "name": {"in-range": r"-(79|80)$", "over-max": r"-81$", "missing-create": r"-POST-MISSING$", "explicit-null": r"-NULL$", "empty": r"-EMPTY$", "blank": r"-BLANK$", "wrong-type": r"-NUMBER$", "unicode-length": r"-UNICODE$"},
        "title": {"in-range": r"-(119|120)$", "over-max": r"-121$", "missing-create": r"-POST-MISSING$", "explicit-null": r"-NULL$", "empty": r"-EMPTY$", "blank": r"-BLANK$", "wrong-type": r"-NUMBER$", "unicode-length": r"-UNICODE$"},
        "score": {"integer-in-range": r"-(0|1|4|5)$", "below": r"-MINUS1$", "above": r"-6$", "null": r"-NULL$", "missing-create": r"-POST-MISSING$", "coercion": r"-(DECIMAL|STRING|BOOL)$"},
        "status": {"enum": r"-(DRAFT|PUBLISHED)$", "outside": r"-ARCHIVED$", "null": r"-NULL$", "missing-create": r"-POST-DEFAULT$", "omitted-update": r"-PATCH-OMITTED$", "empty": r"-EMPTY$", "coercion": r"-BOOL$"},
        "published_at": {"null": r"-NULL$", "utc": r"-UTC$", "offset": r"-(POST|PATCH)-OFFSET$", "empty": r"-EMPTY$", "malformed": r"-MALFORMED$", "no-offset": r"-NO-OFFSET$"},
        "metadata": {k.lower(): "-" + k + "$" for k in ["NULL", "OBJECT", "ARRAY", "NUMBER", "STRING", "BOOL"]},
        "internal_notes": {"null": r"-NULL$", "text": r"-TEXT$"},
        "category": {"valid": r"-VALID$", "null": r"-NULL$", "invalid": r"-INVALID$", "nested-existing": r"-NESTED-EXISTING$", "nested-create": r"-NESTED-CREATE$"}}
    partitions = []
    for row in csv_read(DOCS / "03-phan-vung-tuong-duong.csv"):
        pattern = patterns[row["field"]][row["class_definition"]]
        ids = [c["id"] for c in catalog if c["group"] == "field-" + row["field"] and re.search(pattern, c["id"])]
        assert ids, row["partition_id"]
        states = Counter(latest.get(i, {}).get("status", "NOT_RUN") for i in ids)
        partitions.append({**row, "mapped_cases": ";".join(ids), "passed_representatives": states["passed"],
                           "failed_representatives": states["failed"], "not_run_representatives": states["NOT_RUN"],
                           "scope": "field-focused representative cases only; not exhaustive class correctness"})
    csv_write(HERE / "equivalence-coverage.csv", partitions)

    positive = []
    for c in catalog:
        if c["group"] != "positive-operations":
            continue
        actual = latest.get(c["id"], {})
        request = c["request_template"]
        positive.append({"id": c["id"], "method": request["method"], "path_template": request["path"],
                         "status": actual.get("status", "NOT_RUN"), "cleanup": actual.get("cleanup", "NOT_RUN"),
                         "run_id": actual.get("run_id", ""), "artifact": actual.get("artifact", ""),
                         "qualification": "business positive/read-back per designed oracle, not blanket raw-contract PASS"})
    assert len(positive) == 10
    csv_write(HERE / "positive-operations.csv", positive)
    write("coverage-summary.json", {"catalog_statuses": dict(Counter(r["status"] for r in rows)),
          "BR": {"total": 26, "with_execution": sum(r["passed"] + r["failed"] > 0 for r in br_rows),
                 "with_failure": [r["BR"] for r in br_rows if r["failed"]],
                 "all_mapped_passed": [r["BR"] for r in br_rows if r["assessment"] == "ALL_MAPPED_CASES_PASSED"]},
          "boundary": dict(Counter(r["P8_status"] for r in csv_read(HERE / "boundary-coverage.csv"))),
          "permission": dict(Counter(r["P8_status"] for r in csv_read(HERE / "permission-coverage.csv"))),
          "equivalence": {"total": len(partitions), "with_passed_representative": sum(r["passed_representatives"] > 0 for r in partitions),
                          "with_failed_representative": sum(r["failed_representatives"] > 0 for r in partitions)},
          "positive_operations_passed": sum(r["status"] == "passed" for r in positive)})


if __name__ == "__main__":
    aggregate()
    print("P8 actual result tables regenerated.")
