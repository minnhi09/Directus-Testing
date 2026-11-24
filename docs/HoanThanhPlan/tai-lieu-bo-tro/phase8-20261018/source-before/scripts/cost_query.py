#!/usr/bin/env python3
"""P6 finite query experiment; shares authentication, fixture and oracle with P4."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import os
import signal
import time
import urllib.error
import urllib.parse
from collections import Counter
from pathlib import Path

from designed_cases import (DATA, BudgetExpired, Lab, PreconditionError, Runner,
                            catalogue, data_list, load_json, same, write_json)

DOMAINS = {"filter": ["none", "draft", "published"],
           "sort": ["id", "title,id", "-score,id"],
           "fields": ["id,title", "id,title,status,score"],
           "pagination": ["limit3-offset3", "limit3-page2"]}


def pairs(rows: list[dict]) -> set[tuple]:
    return {(a, row["factors"][a], b, row["factors"][b])
            for row in rows for a, b in itertools.combinations(DOMAINS, 2)}


def validate_model(model: dict, designs: list[dict]) -> None:
    if model.get("model_id") != "QRY-PW-v1" or model.get("factors") != [
            {"name": k, "values": v} for k, v in DOMAINS.items()]:
        raise ValueError("Unexpected finite factor domains")
    rows = model["cases"]
    product = set(itertools.product(*DOMAINS.values()))
    if (len(rows) != 36 or len({r["id"] for r in rows}) != 36 or
            {tuple(r["factors"][k] for k in DOMAINS) for r in rows} != product):
        raise ValueError("Expected all 36 unique factor combinations")
    catalog = {c["id"]: c for c in designs if c["group"] == "pairwise-reference"}
    for row in rows:
        f = row["factors"]
        query = {"sort": f["sort"], "fields": f["fields"], "limit": 3}
        query.update({"offset": 3} if f["pagination"] == "limit3-offset3" else {"page": 2})
        if f["filter"] != "none":
            query["filter[status][_eq]"] = f["filter"]
        request = catalog.get(row["id"], {}).get("request_template", {})
        if (set(f) != set(DOMAINS) or type(row["pairwise"]) is not bool or
                not same(row["query"], query) or request.get("method") != "GET" or
                request.get("path") != "/items/qa_articles" or not same(request.get("query"), query)):
            raise ValueError("Query does not match finite factors / P3 catalog: " + row["id"])
    selected = [r for r in rows if r["pairwise"]]
    if len(selected) != 9 or len(pairs(rows)) != 37 or pairs(selected) != pairs(rows):
        raise ValueError("Expected 9 pairwise rows covering all 37 feasible pairs")


class MeteredOpener:
    """Count actual open attempts, including record=False logins; never store credentials."""
    def __init__(self, opener):
        self.opener = opener
        self.stage = "authentication"
        self.events: list[dict] = []

    def open(self, request, *args, **kwargs):
        event = {"stage": self.stage, "method": request.get_method(),
                 "path": urllib.parse.urlsplit(request.full_url).path, "status": None}
        self.events.append(event)
        try:
            response = self.opener.open(request, *args, **kwargs)
            event["status"] = response.status
            return response
        except urllib.error.HTTPError as error:
            event["status"] = error.code
            raise
        except (urllib.error.URLError, OSError):
            event["network_error"] = True
            raise


def execute(lab: Lab, run_dir: Path, model: dict, selection: str, protocol_sha: str) -> int:
    selected = [r for r in model["cases"] if selection == "exhaustive" or r["pairwise"]]
    meter = MeteredOpener(lab.api.opener)
    lab.api.opener = meter
    report = {"schema": 1, "protocol_id": "P6-COST-v1", "protocol_sha256": protocol_sha,
              "model_id": model["model_id"], "selection": selection, "selected": len(selected),
              "actor": "editor", "method": "GET", "path": "/items/qa_articles",
              "results": [], "status": "INCOMPLETE", "verification": "NOT_RUN",
              "target_wall_seconds": None, "error": None}
    runner = None
    started = time.perf_counter()
    target_started = None
    rc = 1
    try:
        lab.authenticate()
        lab.load_fixture()
        runner = Runner(lab, run_dir, float(os.environ.get("LAB_DETERMINISTIC_MAX_TIME", "120")))
        meter.stage = "preflight"
        runner.preflight()
        if not runner.title_order_verified:
            raise PreconditionError("Independent SQL title order is required for both sets")
        report["setup_seconds"] = time.perf_counter() - started
        meter.stage = runner.stage = "target"
        target_started = time.perf_counter()
        for row in selected:
            result = {"id": row["id"], "factors": row["factors"], "query": row["query"],
                      "verdict": "INCOMPLETE"}
            report["results"].append(result)
            response = runner.request("GET", "/items/qa_articles?" + urllib.parse.urlencode(row["query"]))
            result.update(status=response.status, api_elapsed_seconds=response.elapsed,
                          response_artifact=response.artifact)
            result["expected_ids"] = [r["id"] for r in runner.expected_query("qa_articles", row["query"], "editor")]
            result["actual_ids"] = [r.get("id") for r in data_list(response)]
            # Failures are retained; no expected value is inferred from the response.
            runner.assert_query(response, "qa_articles", row["query"], "editor")
            result["verdict"] = "PASS"
        report["target_wall_seconds"] = time.perf_counter() - target_started
        report["status"] = "PASS"
        rc = 0
    except (AssertionError, BudgetExpired, PreconditionError, RuntimeError, ValueError, OSError, KeyError) as error:
        report["error"] = type(error).__name__ + ": " + str(error)
        report["status"] = "INCOMPLETE" if isinstance(error, (BudgetExpired, PreconditionError)) else "FAIL"
        if report["results"] and report["results"][-1]["verdict"] == "INCOMPLETE" and not isinstance(error, BudgetExpired):
            report["results"][-1]["verdict"] = "FAIL"
    finally:
        if target_started is not None and report["target_wall_seconds"] is None:
            report["target_wall_seconds"] = time.perf_counter() - target_started
        verify_started = time.perf_counter()
        if runner is not None and hasattr(runner, "baseline"):
            meter.stage = runner.stage = "verification"
            runner.cleaning = True  # Only the final state guard may exceed the target budget.
            try:
                runner.assert_snapshot(runner.snapshot(), runner.baseline)
                report["verification"] = "PASS"
            except (AssertionError, RuntimeError, OSError, ValueError) as error:
                report["verification"] = "FAIL"
                report["verification_error"] = type(error).__name__ + ": " + str(error)
                report["status"] = "FAIL"
                rc = 1
        report["verification_seconds"] = time.perf_counter() - verify_started
        report["runner_wall_seconds"] = time.perf_counter() - started
        report["python_http"] = meter.events
        report["python_http_attempts"] = len(meter.events)
        report["python_http_by_stage"] = dict(Counter(e["stage"] for e in meter.events))
        report["target_attempts"] = sum(e["stage"] == "target" for e in meter.events)
        report["target_statuses"] = dict(Counter(str(e["status"]) for e in meter.events if e["stage"] == "target"))
        report["not_run"] = [r["id"] for r in selected if r["id"] not in {x["id"] for x in report["results"]}]
        report["passed_pairs"] = len(pairs([r for r in report["results"] if r["verdict"] == "PASS"]))
        report["feasible_pairs"] = len(pairs(model["cases"]))
        report["passed"] = sum(r["verdict"] == "PASS" for r in report["results"])
        write_json(run_dir / "cost-query-report.json", report)
        write_json(run_dir / "api-trace.json", lab.api.trace)
    print(f"P6 {selection}: {report['status']}, {report['passed']}/{len(selected)}, state={report['verification']}")
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set", choices=["exhaustive", "pairwise"], required=True)
    args = parser.parse_args()
    model = load_json(DATA / "query-cost-model-v1.json")
    validate_model(model, catalogue())  # Reject malformed selections before any authentication.
    protocol = DATA / "query-cost-protocol-v1.json"
    if load_json(protocol)["protocol_id"] != "P6-COST-v1":
        raise ValueError("Unexpected protocol")
    run_dir = Path(os.environ["LAB_RUN_DIR"])
    def interrupted(signum, frame):
        raise BudgetExpired("interrupted by signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    return execute(Lab(run_dir), run_dir, model, args.set, hashlib.sha256(protocol.read_bytes()).hexdigest())


if __name__ == "__main__":
    raise SystemExit(main())
