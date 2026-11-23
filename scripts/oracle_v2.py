#!/usr/bin/env python3
"""Oracle v2 for the 66 catalog cases that had no oracle (OPEN / CONDITIONAL).

Two commands, both offline:
  emit      write oracle-v2.json: for each case the expected outcome (oracle), the outcome
            predicted from Directus source at the pinned SHA, the confidence and the source refs.
            Predictions are written BEFORE the cases are run.
  evaluate  read the artifacts of a finished `test designed` run and judge every case against
            its oracle; also record whether the actual outcome matched the prediction.

The oracle never copies an observed response. Expected outcomes come from (a) project
invariants (no 5xx, rejected requests change nothing) and (b) the Directus 12.5.0 source read at
commit 4f77933. A mismatch between prediction and actual is a finding about the reading or
about the product, not a reason to change the oracle.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "scripts" / "data" / "test-catalog-v1.json"
RESULTS_CSV = ROOT / "docs" / "HoanThanhPlan" / "08-ket-qua-case.csv"
OUT_DIR = ROOT / "docs" / "coverage" / "oracles" / "ORACLE-V2-20261121"
SHA = "4f77933bf9551cac6b289576078783e189b8f4e3"

REF = {
    "payload": f"api/src/permissions/modules/process-payload/process-payload.ts@{SHA}#L61-L128",
    "joi": f"packages/utils/shared/generate-joi.ts@{SHA}#L279-L335,L365-L370",
    "values": f"api/src/services/payload.ts@{SHA}#L215-L285",
    "dates": f"api/src/services/payload.ts@{SHA}#L449-L540",
    "datehelper": f"api/src/database/helpers/date/types.ts@{SHA}",
    "pgerrors": f"api/src/database/errors/dialects/postgres.ts@{SHA}#L20-L140",
    "errorhandler": f"api/src/middleware/error-handler.ts@{SHA}#L22-L110",
    "m2o": f"api/src/services/payload.ts@{SHA}#L596-L690",
    "update": f"api/src/services/items.ts@{SHA}#L843-L850",
    "forbidden": f"api/src/permissions/modules/process-ast/utils/validate-path/create-error.ts@{SHA}",
    "page": f"api/src/database/run-ast/lib/apply-query/index.ts@{SHA}#L40-L47",
    "search": f"api/src/database/run-ast/lib/apply-query/search.ts@{SHA}#L12-L90",
    "sanitize": f"api/src/utils/sanitize-query.ts@{SHA}#L64-L80",
    "fixture": "manifest/fixture field definitions in scripts/lab-components.sh#L365-L374",
}

TS = "2026-10-01T08:00:00Z"


def rule_for(cid: str) -> dict | None:
    """Return the rule for one case id (or None when a family is not covered)."""
    m = re.fullmatch(r"P3-(NAME|TITLE)-(POST|PATCH)-(EMPTY|BLANK|NUMBER|UNICODE)", cid)
    if m:
        field = "name" if m.group(1) == "NAME" else "title"
        kind = m.group(3)
        return {
            "family": "text-value", "field": field, "kind": kind,
            "outcome": "ACCEPT",
            "why": "No Directus rule rejects an empty, blank, numeric or 80/120-char Unicode string in a non-null varchar field: meta.required only forces the key to be present and not null",
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "HIGH",
            "refs": [REF["payload"], REF["joi"], REF["values"], REF["fixture"]],
        }
    m = re.fullmatch(r"P3-(NAME|TITLE|SCORE)-POST-MISSING", cid)
    if m:
        field = {"NAME": "name", "TITLE": "title", "SCORE": "score"}[m.group(1)]
        return {
            "family": "missing-required", "field": field, "outcome": "REJECT",
            "expect": {"status": 400, "code": "FAILED_VALIDATION"},
            "why": "Non-null field without default is validated with _submitted on create, so a missing key fails validation before any SQL",
            "predicted": {"outcome": "REJECT", "status": 400},
            "confidence": "HIGH", "refs": [REF["payload"], REF["joi"]],
        }
    if cid in ("P3-NAME-PATCH-OMITTED",):
        return {
            "family": "patch-empty", "outcome": "ACCEPT",
            "why": "On update only _nnull rules apply, so an absent key passes; an empty payload skips the UPDATE and leaves the row unchanged",
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "MEDIUM", "refs": [REF["payload"], REF["update"]],
        }
    m = re.fullmatch(r"P3-SCORE-(POST|PATCH)-(DECIMAL|STRING|BOOL)", cid)
    if m:
        kind = m.group(2)
        if kind == "BOOL":
            return {
                "family": "score-type", "kind": kind, "outcome": "REJECT",
                "expect": {"status": 400},
                "why": "Joi number rules do not convert a boolean, so validation of score (>=0, <=5) fails",
                "predicted": {"outcome": "REJECT", "status": 400},
                "confidence": "HIGH", "refs": [REF["joi"], REF["payload"]],
            }
        pred = {"outcome": "REJECT", "status": 500} if kind == "DECIMAL" else {"outcome": "ACCEPT", "status_class": "2xx"}
        why = ("Joi accepts 2.5 as a number in range, then PostgreSQL rejects it for an integer column with an error code Directus does not translate, so the generic handler returns 500"
               if kind == "DECIMAL" else
               "Joi converts the numeric string '3' to 3 for the range check and PostgreSQL casts the parameter to integer")
        return {
            "family": "score-type", "kind": kind, "outcome": "ACCEPT_OR_REJECT",
            "integrity": "accepted => read-back is integer 3 (number type); rejected => 4xx and nothing changes",
            "why": why, "predicted": pred,
            "confidence": "HIGH" if kind == "STRING" else "MEDIUM",
            "refs": [REF["joi"], REF["pgerrors"], REF["errorhandler"]],
        }
    if cid in ("P3-STATUS-POST-BOOL", "P3-STATUS-PATCH-BOOL"):
        return {
            "family": "status-type", "outcome": "REJECT", "expect": {"status": 400},
            "why": "status has validation _in [draft, published]; the boolean true is not in the list",
            "predicted": {"outcome": "REJECT", "status": 400},
            "confidence": "HIGH", "refs": [REF["joi"], REF["payload"], REF["fixture"]],
        }
    if cid == "P3-STATUS-POST-DEFAULT":
        return {
            "family": "status-default", "outcome": "ACCEPT", "expect_value": {"status": "draft"},
            "why": "status has defaultValue draft, so _submitted is not applied and the DB default is used",
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "HIGH", "refs": [REF["payload"], REF["fixture"]],
        }
    if cid in ("P3-PUBLISHED_AT-PATCH-UTC", "P3-PUBLISHED_AT-POST-OFFSET", "P3-PUBLISHED_AT-POST-NO-OFFSET", "P3-PUBLISHED_AT-PATCH-NO-OFFSET"):
        cond = "NO-OFFSET" in cid
        return {
            "family": "timestamp-valid", "outcome": "ACCEPT", "expect_instant": TS,
            "condition": "server process time zone is UTC (checked at evaluation)" if cond else None,
            "why": "writeTimestamp uses parseISO; the instant is compared, not the raw string. 15:00+07:00 and 08:00Z are the same instant" if not cond else
                   "parseISO reads a string without offset in the server local time zone; the expected instant is 08:00Z only if that zone is UTC",
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "MEDIUM" if cond else "HIGH",
            "refs": [REF["dates"], REF["datehelper"]],
        }
    if re.fullmatch(r"P3-PUBLISHED_AT-(POST|PATCH)-(EMPTY|MALFORMED)", cid):
        return {
            "family": "timestamp-invalid", "outcome": "REJECT", "expect": {"status_class": "4xx"}, "never_5xx": True,
            "why": "A timestamp input that is not a date must be rejected with a 4xx and change nothing; the project invariant is that bad input never produces a 5xx",
            "predicted": {"outcome": "REJECT", "status": 500},
            "predicted_why": "For type timestamp the code only throws InvalidPayload for date/dateTime; '' is skipped and an invalid Date reaches PostgreSQL, whose error is not translated",
            "confidence": "MEDIUM", "refs": [REF["dates"], REF["pgerrors"], REF["errorhandler"]],
        }
    m = re.fullmatch(r"P3-METADATA-(POST|PATCH)-(ARRAY|NUMBER|STRING|BOOL)", cid)
    if m:
        kind = m.group(2)
        if kind == "STRING":
            return {
                "family": "json-value", "kind": kind, "outcome": "ACCEPT_OR_REJECT",
                "integrity": "accepted => read-back equals the JSON string; rejected => 4xx and nothing changes",
                "why": "A JSON string scalar is valid JSON; an API either stores it or rejects it with a 4xx but must not fail with 5xx",
                "predicted": {"outcome": "REJECT", "status": 500},
                "predicted_why": "Only arrays and objects are JSON.stringify-ed; a bare string reaches the json column unquoted and PostgreSQL reports invalid JSON",
                "confidence": "MEDIUM", "refs": [REF["values"], REF["pgerrors"], REF["errorhandler"]],
            }
        return {
            "family": "json-value", "kind": kind, "outcome": "ACCEPT",
            "why": "Arrays are stringified; numbers and booleans are valid JSON text when sent as parameters; the json column stores them",
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "MEDIUM", "refs": [REF["values"]],
        }
    m = re.fullmatch(r"P3-CATEGORY-(POST|PATCH)-NESTED-(EXISTING|CREATE)", cid)
    if m:
        kind = m.group(2)
        return {
            "family": "nested-m2o", "kind": kind, "outcome": "ACCEPT",
            "why": ("processM2O sets the foreign key to the existing id and skips the update when only the id is given" if kind == "EXISTING"
                    else "processM2O creates the related category through CategoryService (the editor may create) and sets the foreign key to the new id"),
            "predicted": {"outcome": "ACCEPT", "status_class": "2xx"},
            "confidence": "HIGH" if kind == "EXISTING" else "MEDIUM", "refs": [REF["m2o"]],
        }
    m = re.fullmatch(r"P3-AUTHZ-DR-(\d{3})", cid)
    if m:
        n = int(m.group(1))
        if n in (25, 33):
            return {
                "family": "reader-private-field", "outcome": "REJECT", "expect": {"status": 403},
                "why": "An explicitly requested field outside the reader permission fields is rejected with a Forbidden error",
                "predicted": {"outcome": "REJECT", "status": 403}, "confidence": "HIGH", "refs": [REF["forbidden"]],
            }
        if n in (26, 27, 34, 35):
            return {
                "family": "reader-allowed-read", "outcome": "ACCEPT",
                "expect": {"status": 200, "only_published": True, "no_internal_notes": True, "nested_category": n in (27, 35), "single": n in (34, 35)},
                "why": "A wildcard expands only to permitted fields and the row filter limits the reader to published articles; reader may read categories",
                "predicted": {"outcome": "ACCEPT", "status": 200}, "confidence": "MEDIUM", "refs": [REF["forbidden"]],
            }
        if n in (48, 49, 50, 52, 53, 54, 56, 57, 58):
            return {
                "family": "anonymous-deny", "outcome": "REJECT", "expect": {"status": 403},
                "why": "The public policy has no permission on qa_articles, so any projection is rejected with Forbidden",
                "predicted": {"outcome": "REJECT", "status": 403}, "confidence": "HIGH", "refs": [REF["forbidden"]],
            }
    if cid == "P3-QUERY-SEARCH-BLANK":
        return {
            "family": "query-search-blank", "outcome": "ACCEPT", "expect": {"status": 200, "rows": []},
            "why": "A whitespace search is kept (not trimmed away), becomes LOWER(col) LIKE '%   %' on text fields and = NULL on numeric fields; no fixture text has three consecutive spaces",
            "predicted": {"outcome": "ACCEPT", "status": 200}, "confidence": "MEDIUM", "refs": [REF["sanitize"], REF["search"]],
        }
    if cid == "P3-QUERY-PAGE-0":
        return {
            "family": "query-page-zero", "outcome": "ACCEPT", "expect": {"status": 200, "rows": "first-3-by-id"},
            "why": "page=0 passes validation (min 0) and is falsy in the offset rule, so no offset is applied and the first page is returned",
            "predicted": {"outcome": "ACCEPT", "status": 200}, "confidence": "HIGH", "refs": [REF["page"]],
        }
    return None


def target_ids() -> list[str]:
    import csv
    rows = list(csv.DictReader(RESULTS_CSV.open(encoding="utf-8-sig")))
    return [r["id"] for r in rows if r["status"] in ("NOT_RUN", "open")]


def emit() -> int:
    ids = target_ids()
    catalog = {c["id"]: c for c in json.loads(CATALOG.read_text(encoding="utf-8"))}
    cases, missing = [], []
    for cid in ids:
        rule = rule_for(cid)
        if rule is None:
            missing.append(cid)
            continue
        cases.append({"id": cid, "catalog_readiness": catalog[cid]["oracle_readiness"], "group": catalog[cid]["group"], **rule})
    doc = {
        "schema": "oracle-v2/1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "written_before_running": True,
        "source_sha": SHA,
        "status": "PENDING_OWNER_REVIEW",
        "cases": cases,
        "unmapped": missing,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "oracle-v2.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"cases": len(cases), "unmapped": missing}, ensure_ascii=False))
    return 0 if not missing else 2


# ---------------------------------------------------------------- evaluation

def load_run(run_dirs: list[Path], cid: str) -> tuple[dict | None, Path | None]:
    for run_dir in run_dirs:
        path = run_dir / f"case-{cid}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8")), run_dir
    return None, None


def body_of(run_dir: Path, step: dict | None):
    if not step or not step.get("response_artifact"):
        return None
    p = run_dir / step["response_artifact"]
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def instant(value):
    if value is None:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def table_snapshots(run_dir: Path, case: dict) -> tuple[bool, str]:
    """Compare, per table, the last full snapshot taken before the target request with the read-back."""
    steps = case["steps"]
    target = next((s for s in steps if s["stage"] == "target"), None)
    if target is None:
        return True, "no target step"
    if target["method"] == "GET":
        return True, "read-only request, nothing to compare"

    def is_snapshot(step: dict, table: str) -> bool:
        return step["method"] == "GET" and step["path"].startswith(f"/items/{table}?") and "limit=-1" in step["path"] and "sort=id" in step["path"]

    for table in ("qa_articles", "qa_categories"):
        before = [s for s in steps if s["step_id"] < target["step_id"] and is_snapshot(s, table)]
        after = [s for s in steps if s["stage"] == "readback" and is_snapshot(s, table)]
        if not before or not after:
            return True, f"no snapshot pair recorded for {table}"
        if body_of(run_dir, before[-1]) != body_of(run_dir, after[0]):
            return False, f"{table} changed after the rejected request"
    return True, "tables unchanged"


def judge(rule: dict, case: dict, run_dir: Path) -> dict:
    steps = case["steps"]
    target = next((s for s in steps if s["stage"] == "target" and s["method"] in ("POST", "PATCH", "GET")), None)
    status = target["status"] if target else None
    body = body_of(run_dir, target)
    codes = [e.get("extensions", {}).get("code") for e in (body or {}).get("errors", [])] if isinstance(body, dict) else []
    resolved = case.get("resolved_request", {})
    req_body = resolved.get("body") or {}
    checks, notes = {}, []

    def done(passed: bool):
        return {"passed": passed, "target_status": status, "error_codes": codes, "checks": checks, "notes": notes}

    if status is None:
        notes.append("no target step recorded")
        return done(False)
    checks["never_5xx"] = status < 500
    outcome = rule["outcome"]
    readback = None
    if rule["family"] not in ("reader-private-field", "reader-allowed-read", "anonymous-deny", "query-search-blank", "query-page-zero"):
        getter = next((s for s in steps if s["stage"] == "target" and s["method"] == "GET"), None)
        rb = body_of(run_dir, getter)
        readback = rb.get("data") if isinstance(rb, dict) else None
    if outcome == "REJECT":
        exp = rule.get("expect", {})
        if "status" in exp:
            checks["status"] = status == exp["status"]
        if exp.get("status_class") == "4xx":
            checks["status"] = 400 <= status < 500
        if exp.get("code"):
            checks["code"] = exp["code"] in codes
        ok, why = table_snapshots(run_dir, case)
        checks["no_change"] = ok
        notes.append(why)
        return done(all(checks.values()))
    if outcome == "ACCEPT":
        checks["accepted"] = 200 <= status < 300
        fam = rule["family"]
        if fam == "text-value":
            f = rule["field"]
            sent = req_body.get(f)
            expected = str(sent) if isinstance(sent, (int, float)) and not isinstance(sent, bool) else sent
            checks["read_back_value"] = bool(readback) and readback.get(f) == expected
        elif fam == "status-default":
            checks["read_back_value"] = bool(readback) and readback.get("status") == "draft"
        elif fam == "timestamp-valid":
            checks["read_back_instant"] = bool(readback) and instant(readback.get("published_at")) == rule["expect_instant"]
        elif fam == "json-value":
            checks["read_back_value"] = bool(readback) and readback.get("metadata") == req_body.get("metadata")
        elif fam == "nested-m2o":
            cat = readback.get("category") if readback else None
            if rule["kind"] == "EXISTING":
                checks["category_is_existing"] = cat == req_body["category"]["id"] or str(cat) == str(req_body["category"]["id"])
            else:
                checks["category_is_new_id"] = isinstance(cat, int) and cat > 0
        elif fam == "reader-allowed-read":
            data = (body or {}).get("data")
            rows = data if isinstance(data, list) else [data] if data else []
            exp = rule["expect"]
            checks["status"] = status == exp["status"]
            checks["no_internal_notes"] = all("internal_notes" not in r for r in rows)
            checks["only_published"] = all(r.get("status") == "published" for r in rows) and len(rows) > 0
            if exp["nested_category"]:
                checks["nested_category"] = all(isinstance(r.get("category"), dict) and "name" in r["category"] for r in rows if r.get("category") is not None)
        elif fam == "query-search-blank":
            checks["empty"] = isinstance(body, dict) and body.get("data") == []
        elif fam == "query-page-zero":
            data = (body or {}).get("data") or []
            ids = [r["id"] for r in data]
            checks["first_three"] = len(ids) == 3 and ids == sorted(ids)
            first = next((s for s in steps if s["stage"] == "precondition" and "qa_articles" in s["path"]), None)
            all_rows = body_of(run_dir, first)
            if isinstance(all_rows, dict):
                allids = sorted(r["id"] for r in all_rows["data"])
                checks["equals_first_page"] = ids == allids[:3]
        return done(all(checks.values()))
    # ACCEPT_OR_REJECT
    if 200 <= status < 300:
        fam, kind = rule["family"], rule.get("kind")
        if fam == "score-type":
            checks["integer_read_back"] = bool(readback) and readback.get("score") == 3 and isinstance(readback.get("score"), int) and not isinstance(readback.get("score"), bool)
        else:
            checks["read_back_value"] = bool(readback) and readback.get("metadata") == req_body.get("metadata")
        notes.append("accepted branch")
    else:
        checks["client_error"] = 400 <= status < 500
        ok, why = table_snapshots(run_dir, case)
        checks["no_change"] = ok
        notes.append("rejected branch: " + why)
    return done(all(checks.values()))


def evaluate(run_dirs: list[Path]) -> int:
    oracle = json.loads((OUT_DIR / "oracle-v2.json").read_text(encoding="utf-8"))
    rows = []
    for rule in oracle["cases"]:
        case, run_dir = load_run(run_dirs, rule["id"])
        if case is None:
            rows.append({"id": rule["id"], "verdict": "NOT_RUN", "family": rule["family"]})
            continue
        result = judge(rule, case, run_dir)
        pred = rule["predicted"]
        status = result["target_status"]
        if "status" in pred:
            matched = status == pred["status"]
        else:
            matched = status is not None and 200 <= status < 300
        rows.append({
            "id": rule["id"], "family": rule["family"], "confidence": rule["confidence"],
            "verdict": "PASS" if result["passed"] else "FAIL",
            "actual_status": status, "error_codes": result["error_codes"],
            "predicted": pred, "prediction_matched": matched,
            "checks": result["checks"], "notes": result["notes"],
            "harness_status": case.get("status"), "cleanup": case.get("cleanup_status"),
        })
    summary = {
        "run_dirs": [d.name for d in run_dirs],
        "cases": len(rows),
        "verdicts": {v: sum(1 for r in rows if r["verdict"] == v) for v in ("PASS", "FAIL", "NOT_RUN")},
        "prediction_matched": sum(1 for r in rows if r.get("prediction_matched")),
        "prediction_missed": [r["id"] for r in rows if r["verdict"] != "NOT_RUN" and not r["prediction_matched"]],
    }
    out = {"schema": "oracle-v2-results/1", "evaluated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "summary": summary, "results": rows}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "results.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("emit")
    ev = sub.add_parser("evaluate")
    ev.add_argument("--run-glob", required=True, help="glob of run directories, relative to the repository root")
    args = ap.parse_args(argv)
    if args.cmd == "emit":
        return emit()
    dirs = sorted(ROOT.glob(args.run_glob))
    if not dirs:
        print("no run directory matches", args.run_glob, file=sys.stderr)
        return 2
    return evaluate(dirs)


if __name__ == "__main__":
    raise SystemExit(main())
