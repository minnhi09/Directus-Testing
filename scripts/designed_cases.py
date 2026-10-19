#!/usr/bin/env python3
"""Execute P3-v1 designs through the shared Lab / Api, with explicit oracles.

OPEN cases remain business-open; raw contract failures are never suppressed.
Run in the pinned runner image through lab.sh, not against an arbitrary URL.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import signal
import sys
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from invariants import ApiResponse, Lab, error_codes, invalid_directus_jwt, rejected, utc_now

DATA = Path(__file__).parent / "data"
ARTICLE_FIELDS = "id,title,status,score,published_at,metadata,internal_notes,category"
PUBLIC_FIELDS = "id,title,status,score,published_at,metadata,category"
FIELDS = {"qa_articles": ARTICLE_FIELDS, "qa_categories": "id,name"}
COURSE_CASE_IDS = {
    "P3-ST-01", "P3-AUTHZ-DR-047", "P3-SCORE-POST-MINUS1",
    "P3-SCORE-POST-0", "P3-SCORE-POST-5", "P3-SCORE-POST-6",
    "P3-CONTRACT-QA_ARTICLES-OBJECT",
}


class PreconditionError(RuntimeError):
    pass


class BudgetExpired(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def same(left: Any, right: Any) -> bool:
    return json.dumps(left, ensure_ascii=False, sort_keys=True) == json.dumps(right, ensure_ascii=False, sort_keys=True)


def instant(value: Any) -> Any:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks offset")
    return parsed.astimezone(timezone.utc).isoformat()


def normalized(row: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(row)
    if "published_at" in result:
        result["published_at"] = instant(result["published_at"])
    return result


def data_object(response: ApiResponse) -> dict[str, Any]:
    data = response.body.get("data") if isinstance(response.body, dict) else None
    if not 200 <= response.status < 300 or not isinstance(data, dict):
        raise AssertionError(f"Expected 2xx JSON data object, got HTTP {response.status}")
    return data


def data_list(response: ApiResponse) -> list[dict[str, Any]]:
    data = response.body.get("data") if isinstance(response.body, dict) else None
    if not 200 <= response.status < 300 or not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise AssertionError(f"Expected 2xx JSON data array, got HTTP {response.status}")
    return data


def catalogue() -> list[dict[str, Any]]:
    return load_json(DATA / "test-catalog-v1.json")


def select_cases(designs: list[dict[str, Any]], selection: str, case_id: str | None, group: str | None) -> list[dict[str, Any]]:
    if case_id:
        result = [c for c in designs if c["id"] == case_id]
    elif group:
        result = [c for c in designs if c["group"] == group]
    elif selection == "course":
        # Seven cases supplement the six existing scenarios: thirteen in total.
        result = [c for c in designs if c["id"] in COURSE_CASE_IDS]
        if {c["id"] for c in result} != COURSE_CASE_IDS or len(result) != len(COURSE_CASE_IDS):
            raise ValueError("Course selection requires all seven distinct case IDs")
    elif selection == "all":
        # Pairwise execution is the separate Phase 6 experiment, not a silent budget expansion here.
        result = [c for c in designs if c["group"] != "pairwise-reference"]
    elif selection == "assertable":
        result = [c for c in designs if c["group"] != "pairwise-reference" and c["oracle_readiness"] == "ASSERTABLE"]
    else:
        ids = {"P3-ST-01", "P3-ST-02", "P3-ST-03", "P3-SCORE-POST-MINUS1", "P3-SCORE-PATCH-6",
               "P3-SCORE-POST-0", "P3-SCORE-POST-5", "P3-TITLE-POST-120", "P3-NAME-POST-80",
               "P3-STATUS-POST-ARCHIVED", "P3-STATUS-PATCH-OMITTED", "P3-AUTH-INVALID",
               "P3-QUERY-DRAFT", "P3-QUERY-PUBLISHED", "P3-QUERY-SORT-SCORE", "P3-QUERY-PROJECTION2",
               "P3-QUERY-READER-FILTER-DRAFT"}
        for c in designs:
            if c["group"] == "positive-operations":
                ids.add(c["id"])
            if c["group"] == "authorization":
                req = c["request_template"]
                if (c["actor"] == "reader" and (c["oracle"] == "O-DENY" or c["oracle_readiness"] == "ASSERTABLE")):
                    ids.add(c["id"])
                if c["actor"] == "anonymous" and "private" not in c["title"] and "wildcard" not in c["title"] and "nested-category" not in c["title"]:
                    ids.add(c["id"])
        result = [c for c in designs if c["id"] in ids]
    if not result:
        raise ValueError("No catalog case matched selection")
    return result


class Runner:
    def __init__(self, lab: Lab, run_dir: Path, max_time: float = 600.0) -> None:
        self.lab = lab
        self.api = lab.api
        self.run_dir = run_dir
        self.spec = load_json(DATA / "fixture-oracle.json")
        self.map = lab.fixture_map["fixtures"]
        self.expected: dict[str, list[dict[str, Any]]] = {"qa_articles": [], "qa_categories": []}
        for category in self.spec["categories"]:
            self.expected["qa_categories"].append({"id": self.map["qa_categories"][category["fixture_key"]], "name": category["name"]})
        for article in self.spec["articles"]:
            row = {k: copy.deepcopy(v) for k, v in article.items() if k not in {"fixture_key", "id_ref", "category_ref"}}
            row["id"] = self.map["qa_articles"][article["fixture_key"]]
            row["category"] = self.resolve(article["category_ref"], {})
            self.expected["qa_articles"].append(row)
        self.deadline = time.monotonic() + max_time
        if max_time <= 0:
            raise PreconditionError("LAB_DETERMINISTIC_MAX_TIME must be positive")
        self.max_time = max_time
        self.cleaning = False
        self.title_order_verified = False
        self.database_oracle: dict[str, Any] = {}
        self.stage = "precondition"
        self.result: dict[str, Any] | None = None
        self.last_request_time = 0.0
        rate = os.environ.get("LAB_RATE_LIMIT", "5/s")
        if not re.fullmatch(r"[1-9][0-9]*/s", rate):
            raise PreconditionError("Deterministic runner supports rate limit N/s")
        self.interval = 1 / int(rate[:-2])
        self.api.before_request = self.guard_budget

    def guard_budget(self) -> None:
        if not self.cleaning and time.monotonic() >= self.deadline:
            raise BudgetExpired("deterministic suite max-time reached; cleanup still runs")
        wait = self.interval - (time.monotonic() - self.last_request_time)
        if wait > 0:
            time.sleep(wait)
        self.last_request_time = time.monotonic()

    def resolve(self, value: Any, bindings: dict[str, Any]) -> Any:
        if isinstance(value, dict):
            return {k: self.resolve(v, bindings) for k, v in value.items()}
        if isinstance(value, list):
            return [self.resolve(v, bindings) for v in value]
        if not isinstance(value, str):
            return value
        def lookup(key: str) -> Any:
            if key.startswith("fixture."):
                fixture_key = key[8:]
                collection = "qa_categories" if fixture_key.startswith("category_") else "qa_articles"
                return self.map[collection][fixture_key]
            if key not in bindings:
                raise PreconditionError("Missing template binding: " + key)
            return bindings[key]
        full = re.fullmatch(r"\$\{([^}]+)\}", value)
        if full:
            return lookup(full.group(1))
        return re.sub(r"\$\{([^}]+)\}", lambda m: str(lookup(m.group(1))), value)

    def request(self, method: str, path: str, actor: str = "editor", body: Any = None) -> ApiResponse:
        tokens = {"editor": self.lab.editor_token, "reader": self.lab.reader_token, "admin": self.lab.admin_token,
                  "anonymous": "", "invalid-token": invalid_directus_jwt()}
        before = len(self.api.trace)
        response = self.api.request(method, path, tokens[actor], body)
        if self.result is not None and len(self.api.trace) > before:
            step = copy.deepcopy(self.api.trace[-1])
            step.update({"step_id": len(self.result["steps"]) + 1, "actor": actor, "stage": self.stage})
            step["parent_step_id"] = step["step_id"] - 1 if step["step_id"] > 1 else None
            self.result["steps"].append(step)
        if response.status == 0:
            exception = PreconditionError if self.stage in {"precondition", "control", "setup"} else AssertionError
            raise exception("No HTTP response; network error is not an expected rejection")
        return response

    def rows(self, collection: str, actor: str = "editor") -> list[dict[str, Any]]:
        fields = PUBLIC_FIELDS if collection == "qa_articles" and actor == "reader" else FIELDS[collection]
        path = f"/items/{collection}?" + urllib.parse.urlencode({"fields": fields, "limit": -1, "sort": "id"})
        return data_list(self.request("GET", path, actor))

    def snapshot(self) -> dict[str, list[dict[str, Any]]]:
        return {coll: self.rows(coll) for coll in FIELDS}

    @staticmethod
    def canonical(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted([normalized(r) for r in rows], key=lambda r: r["id"])

    def assert_snapshot(self, actual: dict[str, list[dict[str, Any]]], expected: dict[str, list[dict[str, Any]]]) -> None:
        for coll in FIELDS:
            if not same(self.canonical(actual[coll]), self.canonical(expected[coll])):
                raise AssertionError("Business fields / ID set changed: " + coll)

    def preflight(self) -> None:
        if self.lab.fixture_map.get("project") != "r06-k05" or self.lab.fixture_map.get("fixture_version") != "r06-k05-v2":
            raise PreconditionError("Wrong fixture map project/version")
        if not self.lab.editor_schema or not self.lab.reader_schema:
            raise PreconditionError("Export Editor and Reader schemas before running tests")
        if not (self.lab.editor_schema.get("openapi") == self.lab.reader_schema.get("openapi") == "3.0.1"):
            raise PreconditionError("Expected OAS 3.0.1 actor snapshots")
        for coll in FIELDS:
            for path, methods in [("/items/" + coll, ["get", "post"]), ("/items/" + coll + "/{id}", ["get", "patch", "delete"])]:
                if not all(m in self.lab.editor_schema.get("paths", {}).get(path, {}) for m in methods):
                    raise PreconditionError("Editor schema lacks a main operation")
        try:
            self.assert_snapshot(self.snapshot(), self.expected)
        except AssertionError as error:
            raise PreconditionError(str(error)) from error
        self.field_config: dict[str, dict[str, Any]] = {}
        for coll in FIELDS:
            fields = data_list(self.request("GET", "/fields/" + coll, "admin"))
            self.field_config[coll] = {f["field"]: f for f in fields}
        for coll, field_, maximum in [("qa_categories", "name", 80), ("qa_articles", "title", 120)]:
            conf = self.field_config[coll].get(field_, {}).get("schema") or {}
            if conf.get("is_nullable") is not False or conf.get("max_length") != maximum:
                raise PreconditionError("Fixture field nullability/length mismatch: " + field_)
        status = self.field_config["qa_articles"].get("status", {}).get("schema") or {}
        if str(status.get("default_value", "")).strip("'\"") != "draft":
            raise PreconditionError("Cannot confirm status default draft from field schema")
        for field_, validation in [("score", {"score": {"_gte": 0, "_lte": 5}}), ("status", {"status": {"_in": ["draft", "published"]}})]:
            if not same((self.field_config["qa_articles"][field_].get("meta") or {}).get("validation"), validation):
                raise PreconditionError("Fixture validation changed: " + field_)
        db_path = self.run_dir / "database-oracle.json"
        if db_path.exists() and db_path.stat().st_size:
            self.database_oracle = load_json(db_path)
            expected_ids = [self.map["qa_articles"][key] for key in self.spec["title_order_keys"]]
            self.title_order_verified = self.database_oracle.get("title_ids") == expected_ids
        relations = data_list(self.request("GET", "/relations/qa_articles", "admin"))
        if not any(r.get("field") == "category" and r.get("related_collection") == "qa_categories"
                   and (r.get("schema") or {}).get("on_delete") == "SET NULL" for r in relations):
            raise PreconditionError("Expected category foreign key with ON DELETE SET NULL")
        expected_reader = [{k: v for k, v in row.items() if k != "internal_notes"} for row in self.expected["qa_articles"] if row["status"] == "published"]
        actual_reader = self.rows("qa_articles", "reader")
        if not same(self.canonical(actual_reader), self.canonical(expected_reader)):
            raise PreconditionError("Reader positive control / published fixture differs")
        if not same(self.canonical(self.rows("qa_categories", "reader")), self.canonical(self.expected["qa_categories"])):
            raise PreconditionError("Reader categories positive control differs")
        self.baseline = self.snapshot()
        write_json(self.run_dir / "preflight.json", {"status": "passed", "fixture_version": "r06-k05-v2",
                   "map_sha256": hashlib.sha256(json.dumps(self.lab.fixture_map, sort_keys=True).encode()).hexdigest(),
                   "database_oracle": self.database_oracle, "title_order_verified": self.title_order_verified,
                   "catalog_sha256": hashlib.sha256((DATA / "test-catalog-v1.json").read_bytes()).hexdigest()})

    def base_article(self, probe: str, status: str = "draft") -> dict[str, Any]:
        return {"title": "Probe " + probe, "status": status, "score": 3, "published_at": None,
                "metadata": {"probe": probe}, "internal_notes": "Private " + probe,
                "category": self.map["qa_categories"]["category_alpha"]}

    def create(self, coll: str, body: dict[str, Any]) -> dict[str, Any]:
        row = data_object(self.request("POST", "/items/" + coll, body=body))
        if type(row.get("id")) is not int or row["id"] <= 0:
            raise AssertionError("Create lacks positive integer ID")
        for k, v in body.items():
            actual = row.get(k)
            matches = same(instant(actual), instant(v)) if k == "published_at" else same(actual, v)
            if not matches:
                raise AssertionError("Setup/producer did not persist expected field " + k)
        return row

    def read(self, coll: str, item_id: int, actor: str = "editor") -> dict[str, Any]:
        fields = PUBLIC_FIELDS if coll == "qa_articles" and actor == "reader" else FIELDS[coll]
        return data_object(self.request("GET", f"/items/{coll}/{item_id}?fields={fields}", actor))

    def absence(self, coll: str, item_id: int) -> None:
        response = self.request("GET", f"/items/{coll}/{item_id}?fields=id")
        if not rejected(response, 403, {"FORBIDDEN"}):
            raise AssertionError("Deleted/nonexistent resource must follow pinned readOne FORBIDDEN, never 5xx/network")
        if any(r["id"] == item_id for r in self.rows(coll)):
            raise AssertionError("Deleted ID still present in list control")

    def cleanup(self, before: dict[str, list[dict[str, Any]]]) -> None:
        self.cleaning = True
        self.stage = "cleanup"
        try:
            current = self.snapshot()
            for coll in ["qa_articles", "qa_categories"]:
                baseline_ids = {r["id"] for r in before[coll]}
                for row in current[coll]:
                    if row["id"] not in baseline_ids:
                        response = self.request("DELETE", f'/items/{coll}/{row["id"]}')
                        if not 200 <= response.status < 300:
                            raise AssertionError("Cleanup DELETE failed: " + coll)
            # Do not silently repair changed fixtures here: stop the suite, let the shared outer restore act.
            self.assert_snapshot(self.snapshot(), before)
        finally:
            self.cleaning = False

    def no_side_effect(self, before: dict[str, list[dict[str, Any]]]) -> None:
        self.stage = "readback"
        self.assert_snapshot(self.snapshot(), before)

    def expected_query(self, coll: str, query: dict[str, Any], actor: str) -> list[dict[str, Any]]:
        rows = copy.deepcopy(self.expected[coll])
        if coll == "qa_articles" and actor == "reader":
            rows = [r for r in rows if r["status"] == "published"]
        if "filter[status][_eq]" in query:
            rows = [r for r in rows if r.get("status") == query["filter[status][_eq]"]]
        if "filter[id][_eq]" in query:
            rows = [r for r in rows if r["id"] == int(query["filter[id][_eq]"])]
        if "search" in query:
            term = str(query["search"]).lower()
            # Model is deliberately only the two literal terms in the reviewed fixture, never a general DB collation emulator.
            if term not in {"spéciale", "r06k05absenttermzyx987"}:
                raise PreconditionError("Search term has no independent baseline oracle")
            searchable = ["title", "status"] + (["internal_notes"] if actor == "editor" else [])
            rows = [r for r in rows if any(term in str(r.get(f, "")).lower() for f in searchable)]
        sort = query.get("sort", "id")
        if sort == "title,id" and not self.title_order_verified:
            raise PreconditionError("Title order needs independent database/collation verification")
        if sort == "-score,id":
            rows.sort(key=lambda r: (-r["score"], r["id"]))
        elif sort == "title,id":
            rows.sort(key=lambda r: (r["title"][:8], r["id"]))
        elif sort == "id":
            rows.sort(key=lambda r: r["id"])
        else:
            raise PreconditionError("Sort not in finite oracle model")
        limit = int(query.get("limit", 100))
        offset = (int(query["page"]) - 1) * limit if "page" in query else int(query.get("offset", 0))
        if offset < 0:
            raise PreconditionError("page=0 semantics remains OPEN")
        rows = rows[offset:] if limit == -1 else rows[offset:offset + limit]
        fields = query.get("fields", FIELDS[coll]).split(",")
        result = []
        for row in rows:
            selected = {f: row[f] for f in fields if "." not in f and f in row}
            nested = [f for f in fields if f.startswith("category.")]
            if nested:
                category = next((r for r in self.expected["qa_categories"] if r["id"] == row.get("category")), None)
                selected["category"] = {f.split(".")[1]: category[f.split(".")[1]] for f in nested} if category else None
            result.append(selected)
        return result

    def assert_query(self, response: ApiResponse, coll: str, query: dict[str, Any], actor: str) -> None:
        actual = data_list(response)
        expected = self.expected_query(coll, query, actor)
        if not same([normalized(r) for r in actual], [normalized(r) for r in expected]):
            raise AssertionError("Query differs from independent seed/map oracle (IDs, values, order or projection)")

    def contract(self, response: ApiResponse, method: str, path: str) -> None:
        from contract_checks import validate
        canonical = re.sub(r"/(\d+)(?=\?|$)", "/{id}", path.split("?")[0])
        match = re.search(r"/(\d+)(?=\?|$)", path)
        checks = validate(self.lab.editor_schema, method, canonical, response,
                          path_parameters={"id": int(match.group(1))} if match else None)
        assert self.result is not None
        self.result["contract_checks"] = checks
        if any(c["status"] in {"failed", "error"} for c in checks):
            self.result["verdicts"]["contract"] = "failed"
        else:
            self.result["verdicts"]["contract"] = "passed"

    def stateful(self, design: dict[str, Any], probe: str) -> None:
        self.stage = "producer"
        category = self.create("qa_categories", {"name": "Chain " + probe})
        c_id = category["id"]
        assert self.result is not None
        self.result["bindings"]["created_category_id"] = c_id
        if design["id"] == "P3-ST-01":
            if not same(self.read("qa_categories", c_id), category):
                raise AssertionError("Category read-back differs")
            self.stage = "transition"
            changed = {"id": c_id, "name": "Changed " + probe}
            data_object(self.request("PATCH", f"/items/qa_categories/{c_id}", body={"name": changed["name"]}))
            if not same(self.read("qa_categories", c_id), changed):
                raise AssertionError("Category PATCH changed wrong fields")
            response = self.request("DELETE", f"/items/qa_categories/{c_id}")
            if not 200 <= response.status < 300:
                raise AssertionError("Category DELETE failed")
            self.absence("qa_categories", c_id)
        else:
            body = self.base_article(probe)
            body["category"] = c_id
            article = self.create("qa_articles", body)
            a_id = article["id"]
            self.result["bindings"]["created_article_id"] = a_id
            if not same(normalized(self.read("qa_articles", a_id)), normalized(article)):
                raise AssertionError("Article pre-transition read-back differs")
            self.stage = "transition"
            if design["id"] == "P3-ST-02":
                data_object(self.request("PATCH", f"/items/qa_articles/{a_id}", body={"score": 4}))
                expected = {**article, "score": 4}
                if not same(normalized(self.read("qa_articles", a_id)), normalized(expected)):
                    raise AssertionError("PATCH failed full field preservation")
                response = self.request("DELETE", f"/items/qa_articles/{a_id}")
                if not 200 <= response.status < 300:
                    raise AssertionError("Article DELETE failed")
                self.absence("qa_articles", a_id)
                response = self.request("DELETE", f"/items/qa_categories/{c_id}")
                if not 200 <= response.status < 300:
                    raise AssertionError("Category DELETE failed")
            else:
                response = self.request("DELETE", f"/items/qa_categories/{c_id}")
                if not 200 <= response.status < 300:
                    raise AssertionError("Category DELETE failed")
                expected = {**article, "category": None}
                if not same(normalized(self.read("qa_articles", a_id)), normalized(expected)):
                    raise AssertionError("SET NULL lost article or changed unrelated fields")
                response = self.request("DELETE", f"/items/qa_articles/{a_id}")
                if not 200 <= response.status < 300:
                    raise AssertionError("Article cleanup DELETE failed")
        self.result["replay_scope"] = "full_designed_sequence"

    def execute(self, design: dict[str, Any], before: dict[str, list[dict[str, Any]]], probe: str) -> None:
        request = copy.deepcopy(design["request_template"])
        method = request["method"]
        actor = design["actor"]
        bindings: dict[str, Any] = {"probe_key": probe, "run_id": os.environ.get("LAB_RUN_ID", "local"), "case_id": design["id"]}
        if design["group"] == "stateful":
            self.stateful(design, probe)
            return
        coll = "qa_categories" if request["path"].startswith("/items/qa_categories") else "qa_articles"
        path_template = request["path"]
        target_before = None
        if "${target_id}" in path_template:
            state = "published" if design["group"] == "positive-operations" or " published " in design["title"] or design["id"] == "P3-STATUS-PATCH-OMITTED" else "draft"
            if method in {"PATCH", "DELETE"}:
                self.stage = "setup"
                target_before = self.create(coll, self.base_article(probe, state) if coll == "qa_articles" else {"name": "Probe " + probe})
                bindings["target_id"] = target_before["id"]
            else:
                key = "category_alpha" if coll == "qa_categories" else "article_alpha_" + state + "_1"
                bindings["target_id"] = self.map[coll][key]
                target_before = next(r for r in self.expected[coll] if r["id"] == bindings["target_id"])
        if target_before is not None and coll == "qa_articles":
            bindings["changed_score"] = (target_before["score"] + 1) % 6
        bindings.setdefault("changed_score", 4)
        occupied = {r["id"] for r in before["qa_categories"]}
        absent = 1
        while absent in occupied:
            absent += 1
        if absent >= 2**31:
            raise PreconditionError("No safe absent category ID in integer domain")
        bindings["absent_category_id"] = absent
        request = self.resolve(request, bindings)
        body = request.get("body")
        path = request["path"]
        query = request.get("query", {})
        if path == "/users/me":
            query["fields"] = "id"
        if design["group"] == "positive-operations" and method == "GET" and not path.endswith(str(bindings.get("target_id", "<none>"))):
            query.setdefault("sort", "id")
        full_path = path + ("?" + urllib.parse.urlencode({k: json.dumps(v, separators=(",", ":")) if isinstance(v, (dict, list)) else v for k, v in query.items()}, doseq=True) if query else "")
        assert self.result is not None
        self.result["bindings"].update(bindings)
        self.result["resolved_request"] = self.api.scrub(request)
        target_snapshot = self.snapshot() if method in {"POST", "PATCH", "DELETE"} else before
        if actor in {"reader", "anonymous"}:
            self.stage = "control"
            if method == "GET":
                control = self.request(method, full_path, "editor")
                if not 200 <= control.status < 300:
                    raise PreconditionError("Editor control failed on permission target")
            else:
                # A separate control object: prove the payload is valid without mutating the deny target.
                control_body = self.base_article(probe + "c", str((body or {}).get("status", "draft"))) if coll == "qa_articles" else {"name": "Control " + probe}
                if method == "POST":
                    self.create(coll, body)
                elif method == "PATCH":
                    control_row = self.create(coll, control_body)
                    if not 200 <= self.request("PATCH", f'/items/{coll}/{control_row["id"]}', body=body).status < 300:
                        raise PreconditionError("Editor PATCH control payload invalid")
                else:
                    control_row = self.create(coll, control_body)
                    if not 200 <= self.request("DELETE", f'/items/{coll}/{control_row["id"]}').status < 300:
                        raise PreconditionError("Editor DELETE control failed")
                # Control-created rows belong to cleanup, but are not side effects of the target request.
                target_snapshot = self.snapshot()
        if design["oracle"] == "O-AUTH":
            self.stage = "control"
            if not data_object(self.request("GET", "/users/me?fields=id", "editor")).get("id"):
                raise PreconditionError("Valid users/me token control failed")
        self.stage = "target"
        response = self.request(method, full_path, actor, body)
        self.result["target_response"] = {"status": response.status, "body_summary": {"error_codes": sorted(error_codes(response))}, "artifact": response.artifact}
        if response.status >= 500:
            self.result["verdicts"]["robustness"] = "failed"
            raise AssertionError("API returned 5xx, never a valid negative PASS")
        self.result["verdicts"]["robustness"] = "passed"
        oracle = design["oracle"]
        if oracle == "O-CONTRACT":
            self.contract(response, method, path)
            if method == "POST":
                data = response.body.get("data") if isinstance(response.body, dict) else None
                rows = data if isinstance(data, list) else [data]
                expected_items = body if isinstance(body, list) else [body]
                if not 200 <= response.status < 300 or len(rows) != len(expected_items) or any(not isinstance(r, dict) or type(r.get("id")) is not int for r in rows):
                    raise AssertionError("POST business response shape/count/ID differs")
                for row, expected in zip(rows, expected_items):
                    actual = self.read(coll, row["id"])
                    if any(not same(normalized({k: actual[k]}), normalized({k: v})) for k, v in expected.items()):
                        raise AssertionError("POST object/array read-back differs")
            elif query.get("export"):
                if response.status != 200 or not response.raw:
                    raise AssertionError("Export did not return nonempty successful output")
            else:
                actual = data_object(response)
                expected = self.expected_query(coll, {"fields": "title", "filter[id][_eq]": self.map[coll]["article_alpha_published_1"]}, actor)[0]
                if not same(actual, expected):
                    raise AssertionError("Projected business object differs")
            return
        if oracle in {"O-VALIDATION", "O-FK", "O-QUERY-INVALID"}:
            codes = {"O-VALIDATION": {"FAILED_VALIDATION"}, "O-FK": {"INVALID_FOREIGN_KEY"}, "O-QUERY-INVALID": {"INVALID_QUERY"}}[oracle]
            if not rejected(response, 400, codes):
                raise AssertionError("Expected 400 with exact rule error, got " + str(response.status) + ": " + ",".join(error_codes(response)))
            if method != "GET":
                self.no_side_effect(target_snapshot)
            return
        if oracle == "O-LENGTH":
            if not rejected(response, 400, {"VALUE_TOO_LONG"}):
                raise AssertionError("Overlength was not rejected by the pinned VALUE_TOO_LONG branch")
            self.no_side_effect(target_snapshot)
            return
        if oracle == "O-DENY":
            if not rejected(response, 403, {"FORBIDDEN"}):
                raise AssertionError("Permission target did not return 403/FORBIDDEN")
            self.no_side_effect(target_snapshot)
            self.result["verdicts"]["authorization"] = "passed"
            return
        if oracle == "O-AUTH":
            if not rejected(response, 403, {"INVALID_TOKEN"}):
                raise AssertionError("Invalid token was not rejected through INVALID_TOKEN")
            self.result["verdicts"]["authorization"] = "passed"
            return
        if oracle in {"O-OPEN", "O-FIELD", "O-ROBUST"}:
            if actor == "reader" and "internal_notes" in json.dumps(response.body):
                # Only inspect article data, not an error message naming the forbidden field.
                data = response.body.get("data") if isinstance(response.body, dict) else None
                if data is not None and "internal_notes" in json.dumps(data):
                    raise AssertionError("Reader response exposed internal_notes")
            if method in {"PATCH", "POST"} and response.status >= 400:
                self.no_side_effect(target_snapshot)
            if method in {"POST", "PATCH"} and 200 <= response.status < 300:
                data = data_object(response)
                item_id = bindings.get("target_id") if method == "PATCH" else data.get("id")
                if type(item_id) is not int:
                    raise AssertionError("Accepted observation lacks target ID for read-back")
                actual = self.read(coll, item_id)
                focus = design["group"].removeprefix("field-")
                known = target_before if method == "PATCH" else body
                if known:
                    for field_, value in known.items():
                        if field_ != focus and not same(normalized({field_: actual.get(field_)}), normalized({field_: value})):
                            raise AssertionError("Observation changed an unrelated known field: " + field_)
                self.result["observed_readback"] = self.api.scrub(actual)
            self.result["verdicts"]["business"] = "not_applicable" if design["group"] == "robustness" else "open"
            self.result["observed"] = {"status": response.status, "error_codes": sorted(error_codes(response))}
            return
        if design["id"] == "P3-AUTH-CONTROL":
            if not data_object(response).get("id"):
                raise AssertionError("Valid auth control lacks actor ID")
            return
        if design["group"] == "robustness":
            if not 200 <= response.status < 300:
                raise AssertionError("Valid aggregate control did not succeed")
            if design["id"].endswith("COUNT"):
                data = data_list(response)
                if len(data) != 1 or int(data[0].get("count", {}).get("id", -1)) != len(self.expected[coll]):
                    raise AssertionError("Aggregate count differs from seed size")
            return
        if method == "GET":
            if "${target_id}" in path_template or "/${fixture." in path_template:
                item_id = int(path.rsplit("/", 1)[1])
                row = target_before or next(r for r in self.expected[coll] if r["id"] == item_id)
                fields = query.get("fields", FIELDS[coll])
                if fields == "*":
                    fields = PUBLIC_FIELDS if actor == "reader" and coll == "qa_articles" else FIELDS[coll]
                expected = self.project_row(row, fields)
                if not same(normalized(data_object(response)), normalized(expected)):
                    raise AssertionError("Detail / projected/nested field oracle differs")
            else:
                q = dict(query)
                if q.get("fields") == "*":
                    q["fields"] = PUBLIC_FIELDS if actor == "reader" and coll == "qa_articles" else FIELDS[coll]
                self.assert_query(response, coll, q, actor)
            if actor == "reader" and coll == "qa_articles":
                data = response.body.get("data")
                if "internal_notes" in json.dumps(data):
                    raise AssertionError("Reader data includes private field")
            return
        if method == "POST":
            row = data_object(response)
            if type(row.get("id")) is not int or row["id"] <= 0:
                raise AssertionError("POST lacks a positive integer ID")
            expected = {**body, "id": row["id"]}
            if coll == "qa_articles" and "status" not in expected:
                expected["status"] = "draft"
            actual = self.read(coll, row["id"])
            if not same(normalized(actual), normalized(expected)):
                raise AssertionError("POST full read-back differs from known input/default")
        elif method == "PATCH":
            if not 200 <= response.status < 300 or target_before is None:
                raise AssertionError("PATCH did not succeed")
            expected = {**target_before, **body}
            actual = self.read(coll, bindings["target_id"])
            if not same(normalized(actual), normalized(expected)):
                raise AssertionError("PATCH changed wrong field or lost an omitted field")
        elif method == "DELETE":
            if not 200 <= response.status < 300:
                raise AssertionError("DELETE did not succeed")
            self.absence(coll, bindings["target_id"])

    def project_row(self, row: dict[str, Any], fields: str) -> dict[str, Any]:
        expected = {f: row[f] for f in fields.split(",") if "." not in f and f in row}
        nested = [f for f in fields.split(",") if f.startswith("category.")]
        if nested:
            cat = next((r for r in self.expected["qa_categories"] if r["id"] == row.get("category")), None)
            expected["category"] = {f.split(".")[1]: cat[f.split(".")[1]] for f in nested} if cat else None
        return expected

    def run_case(self, design: dict[str, Any]) -> dict[str, Any]:
        probe = hashlib.sha256((os.environ.get("LAB_RUN_ID", "local") + "\0" + design["id"]).encode()).hexdigest()[:24]
        result: dict[str, Any] = {"id": design["id"], "BR": design["BR"], "AC": design["AC"], "actor": design["actor"],
                  "oracle_readiness": design["oracle_readiness"], "status": "running", "steps": [], "bindings": {},
                  "expected_response": design["expected_response"], "expected_state": design["expected_state"],
                  "verdicts": {"business": "not_run", "authorization": "not_applicable", "contract": "not_run", "robustness": "not_run"},
                  "cleanup_status": "not_run", "replay_scope": "full_designed_case", "started_at": utc_now()}
        self.result = result
        before = None
        try:
            self.stage = "precondition"
            before = self.snapshot()
            try:
                self.assert_snapshot(before, self.expected)
            except AssertionError as error:
                raise PreconditionError(str(error)) from error
            self.execute(design, before, probe)
            if result["verdicts"]["business"] == "not_run":
                result["verdicts"]["business"] = "passed"
            result["status"] = "failed" if "failed" in result["verdicts"].values() else "open" if design["oracle_readiness"] == "OPEN" else "passed"
        except PreconditionError as error:
            result.update(status="blocked", reason=str(error))
        except BudgetExpired as error:
            result.update(status="incomplete", reason=str(error))
        except Exception as error:
            result.update(status="failed", reason=self.api.scrub(str(error)), error_type=type(error).__name__)
            if result["verdicts"]["business"] == "not_run":
                result["verdicts"]["business"] = "failed"
        finally:
            if before is not None:
                try:
                    self.cleanup(before)
                    result["cleanup_status"] = "passed"
                except (AssertionError, RuntimeError, KeyError, ValueError, TypeError) as error:
                    result["cleanup_status"] = "failed"
                    result["cleanup_error"] = self.api.scrub(str(error))
                    result["status"] = "failed"
            result["finished_at"] = utc_now()
            self.result = None
            self.cleaning = False
            write_json(self.run_dir / ("case-" + design["id"] + ".json"), result)
        return result


def run_selected(runner: Runner, selected: list[dict[str, Any]], report: dict[str, Any], run_dir: Path) -> None:
    for design in selected:
        result = runner.run_case(design)
        report["cases"].append(result)
        print("Designed", result["id"], result["status"], result.get("reason", ""))
        if result["cleanup_status"] == "failed":
            report["stop_reason"] = "cleanup_failed"
        elif result["status"] in {"blocked", "incomplete"}:
            report["stop_reason"] = result["status"]
        write_json(run_dir / "designed-report.json", report)
        if report["stop_reason"]:
            break


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case")
    parser.add_argument("--group")
    parser.add_argument("--selection", choices=["course", "short", "all", "assertable"], default="course",
                        help="course: seven cases supplementing the six scenarios (default); other selections are extended suites")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()
    designs = catalogue()
    selected = select_cases(designs, args.selection, args.case, args.group)
    if args.list:
        print(json.dumps([{"id": c["id"], "readiness": c["oracle_readiness"]} for c in selected], indent=2))
        return 0
    run_dir = Path(os.environ["LAB_RUN_DIR"])
    report: dict[str, Any] = {"schema": 1, "run_id": os.environ.get("LAB_RUN_ID"), "started_at": utc_now(),
        "selection": {"name": args.selection, "case": args.case, "group": args.group, "ids": [c["id"] for c in selected]},
        "catalog_total": len(designs), "catalog_not_selected": [c["id"] for c in designs if c not in selected], "cases": [],
        "setup_status": "running", "stop_reason": None, "execution_complete": False, "replay_mode": os.environ.get("LAB_DESIGNED_REPLAY")}
    exit_code = 1
    def interrupted(signum: int, frame: Any) -> None:
        raise BudgetExpired("interrupted by signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        lab = Lab(run_dir)
        lab.authenticate()
        lab.load_fixture()
        runner = Runner(lab, run_dir, float(os.environ.get("LAB_DETERMINISTIC_MAX_TIME", "600")))
        runner.preflight()
        report["setup_status"] = "passed"
        write_json(run_dir / "designed-report.json", report)
        run_selected(runner, selected, report, run_dir)
        report["execution_complete"] = len(report["cases"]) == len(selected) and not report["stop_reason"]
        if report["stop_reason"] is None:
            report["stop_reason"] = "selected_cases_exhausted"
        exit_code = 0 if report["execution_complete"] and all(c["status"] == "passed" for c in report["cases"]) else 1
    except Exception as error:
        report.update(setup_status="failed" if report["setup_status"] != "passed" else report["setup_status"], stop_reason="precondition_or_runner_error", error_type=type(error).__name__, error=str(error))
    finally:
        report["finished_at"] = utc_now()
        report["runner_exit_code"] = exit_code
        report["summary"] = {status: sum(c["status"] == status for c in report["cases"]) for status in ["passed", "failed", "blocked", "open", "incomplete"]}
        report["selected_not_run"] = [c["id"] for c in selected if c["id"] not in {r["id"] for r in report["cases"]}]
        write_json(run_dir / "designed-report.json", report)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
