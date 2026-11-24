#!/usr/bin/env python3
"""Replay recorded Schemathesis cases with typed, collection-scoped ID mapping.

Status equality alone is never called a reproduced check failure. Unsupported
checks / incomplete parents stay explicitly unverified and return nonzero.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any

from contract_checks import CHECKS, validate
from designed_cases import Runner, write_json
from invariants import Lab, utc_now


class ReplayError(RuntimeError):
    pass


def collection_path(uri: str) -> tuple[str, str, str | None]:
    parsed = urllib.parse.urlsplit(uri)
    path = urllib.parse.unquote(parsed.path)
    match = re.fullmatch(r"/items/(qa_articles|qa_categories)(?:/([^/]+))?", path)
    if not match or match.group(2) in {".", ".."} or parsed.fragment:
        raise ReplayError("Request path outside exact collection/detail allowlist")
    return match.group(1), parsed.path, match.group(2)


def response_json(interaction: dict[str, Any]) -> Any:
    content = interaction.get("response", {}).get("content", {})
    if not isinstance(content, dict) or "$base64" not in content:
        return None
    try:
        return json.loads(base64.b64decode(content["$base64"]))
    except (ValueError, UnicodeDecodeError):
        return None


def chain_ids(cases: dict[str, Any], target: str) -> list[str]:
    chain = []
    seen = set()
    current: str | None = target
    while current is not None:
        if current in seen or current not in cases:
            raise ReplayError("Missing or cyclic parent; target will not be sent")
        seen.add(current)
        chain.append(current)
        current = cases[current].get("parent_id")
    return list(reversed(chain))


def remap_request(uri: str, body: Any, mappings: dict[str, dict[str, int]]) -> tuple[str, Any]:
    coll, path, item_id = collection_path(uri)
    own_map = mappings.get(coll, {})
    if item_id is not None and item_id in own_map:
        path = "/items/" + coll + "/" + str(own_map[item_id])
    query = []
    for key, value in urllib.parse.parse_qsl(urllib.parse.urlsplit(uri).query, keep_blank_values=True):
        mapping = own_map if key == "filter[id][_eq]" else mappings.get("qa_categories", {}) if coll == "qa_articles" and key == "filter[category][_eq]" else {}
        query.append((key, str(mapping.get(value, value))))
    if query:
        path += "?" + urllib.parse.urlencode(query)
    copied = copy.deepcopy(body)
    # Schema-known FK only. Never walk every numeric value (score, limit,
    # metadata counters, strings containing an ID, or IDs of other collections).
    def relation(row: Any) -> None:
        if coll != "qa_articles" or not isinstance(row, dict):
            return
        value = row.get("category")
        mapping = mappings.get("qa_categories", {})
        if type(value) is int and str(value) in mapping:
            row["category"] = mapping[str(value)]
        elif isinstance(value, dict) and type(value.get("id")) is int and str(value["id"]) in mapping:
            row["category"] = {**value, "id": mapping[str(value["id"])]}
    for row in copied if isinstance(copied, list) else [copied]:
        relation(row)
    return path, copied


def identity(row: dict[str, Any], coll: str) -> tuple[str, Any]:
    if coll == "qa_articles":
        meta = row.get("metadata")
        if isinstance(meta, dict) and isinstance(meta.get("fixture_key"), str):
            return "fixture_key", meta["fixture_key"]
        if isinstance(row.get("title"), str):
            return "title", row["title"]
    elif isinstance(row.get("name"), str):
        return "name", row["name"]
    raise ReplayError("Producer row lacks a stable identity for safe ID remapping")


def map_ids(source: Any, actual: Any, coll: str) -> dict[str, int]:
    def rows(body: Any) -> list[dict[str, Any]]:
        if not isinstance(body, dict):
            raise ReplayError("Producer lacks JSON envelope")
        data = body.get("data")
        result = data if isinstance(data, list) else [data]
        if not result or any(not isinstance(r, dict) or type(r.get("id")) is not int for r in result):
            raise ReplayError("Producer lacks integer IDs")
        return result
    old_rows, new_rows = rows(source), rows(actual)
    new_by_identity: dict[tuple[str, Any], list[dict[str, Any]]] = {}
    for row in new_rows:
        new_by_identity.setdefault(identity(row, coll), []).append(row)
    seen = set()
    mapping = {}
    for row in old_rows:
        key = identity(row, coll)
        matched = new_by_identity.get(key, [])
        if key in seen or len(matched) != 1:
            raise ReplayError("Ambiguous/missing producer identity; positional ID zip is unsafe")
        seen.add(key)
        mapping[str(row["id"])] = matched[0]["id"]
    return mapping


def find_record(root: Path, case_id: str, explicit: str | None) -> tuple[Path, int, dict[str, Any]]:
    if explicit:
        candidate = Path(explicit).resolve()
        if not candidate.is_relative_to(root.resolve()):
            raise ReplayError("LAB_REPLAY_EVENTS must stay within artifacts/runs")
        files = [candidate]
    else:
        files = sorted(root.rglob("schemathesis-events.ndjson"))
    found = []
    for path in files:
        with path.open(encoding="utf-8") as stream:
            for line_no, line in enumerate(stream, 1):
                value = json.loads(line).get("ScenarioFinished", {}).get("recorder", {})
                if case_id in value.get("cases", {}):
                    found.append((path, line_no, value))
    if not found:
        raise ReplayError("Case ID not found in stored events")
    # The same case may be emitted in several final recorder copies. Equivalent
    # records can be deduplicated, independent runs with the same ID cannot.
    unique = {}
    for item in found:
        value = item[2]
        signature = (str(item[0]), json.dumps(value.get("interactions", {}).get(case_id), sort_keys=True))
        unique[signature] = item
    if len(unique) != 1:
        raise ReplayError("Case ID is ambiguous; select source with LAB_REPLAY_EVENTS")
    return next(iter(unique.values()))


def check_match(source_checks: list[dict[str, Any]], actual: list[dict[str, Any]], source_status: int, actual_status: int) -> dict[str, Any]:
    failed = [c for c in source_checks if c.get("status") == "failure"]
    matches, missing, unsupported = [], [], []
    for check in failed:
        name = check["name"]
        kind = check.get("failure_info", {}).get("failure", {}).get("type")
        if name not in CHECKS:
            unsupported.append(name)
            continue
        replay_check = next((c for c in actual if c["name"] == name), {})
        if replay_check.get("status") == "failed" and any(f["type"] == kind for f in replay_check.get("failures", [])):
            matches.append({"name": name, "failure_type": kind})
        else:
            missing.append({"name": name, "failure_type": kind})
    reproduced = bool(failed) and not missing and not unsupported and len(matches) == len(failed) and source_status == actual_status
    return {"reproduced": reproduced, "matched_checks": matches, "missing_checks": missing,
            "unsupported_checks": unsupported, "source_had_failures": bool(failed), "status_equal": source_status == actual_status}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_id")
    args = parser.parse_args()
    run_dir = Path(os.environ["LAB_RUN_DIR"])
    report: dict[str, Any] = {"schema": 2, "case_id": args.case_id, "started_at": utc_now(),
        "status": "not_sent", "target_sent": False, "sequence_replayed": False,
        "replay_scope": "not_sent", "steps": [], "id_mapping": {"qa_articles": {}, "qa_categories": {}}}
    rc = 1
    report_id = args.case_id if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", args.case_id) else "invalid-id-" + hashlib.sha256(args.case_id.encode()).hexdigest()[:16]
    try:
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}", args.case_id):
            raise ReplayError("Invalid case ID")
        lab = Lab(run_dir)
        lab.authenticate()
        lab.load_fixture()
        Runner(lab, run_dir, float(os.environ.get("LAB_DETERMINISTIC_MAX_TIME", "600"))).preflight()
        events, line, recorder = find_record(Path(os.environ["LAB_ARTIFACT_ROOT"]), args.case_id, os.environ.get("LAB_REPLAY_EVENTS") or None)
        schema_path = next((events.parent / name for name in ["schema-raw.json", "schema-guided.json"] if (events.parent / name).exists()), None)
        if schema_path is None:
            raise ReplayError("Source schema beside events missing; no fallback to a different current contract")
        schema = json.loads(schema_path.read_bytes())
        cases = recorder["cases"]
        chain = chain_ids(cases, args.case_id)
        target = cases[args.case_id]
        if target.get("is_transition_applied") and not target.get("parent_id"):
            raise ReplayError("Applied transition has no parent; no final-request fallback")
        report.update(source_events=str(events), source_line=line, source_sha256=hashlib.sha256(events.read_bytes()).hexdigest(),
                      schema_hash=hashlib.sha256(schema_path.read_bytes()).hexdigest(), sequence_case_ids=chain,
                      replay_scope="full_recorded_parent_chain" if len(chain) > 1 else "single_request")
        mappings = report["id_mapping"]
        for index, case_id in enumerate(chain):
            stored = cases[case_id]
            interaction = recorder.get("interactions", {}).get(case_id)
            if not interaction:
                raise ReplayError("Parent/target interaction absent; target not sent")
            request = interaction["request"]
            method, uri = request["method"], request["uri"]
            coll, old_path, item_id = collection_path(uri)
            if method not in {"GET", "POST", "PATCH", "DELETE", "TRACE"} or (method == "TRACE" and index != len(chain) - 1):
                raise ReplayError("Unsupported replay method")
            if stored.get("is_transition_applied"):
                transition = stored.get("transition", {})
                params = transition.get("parameters", {})
                allowed = params.get("path_parameters", {})
                if set(params) - {"path_parameters"} or set(allowed) - {"id"}:
                    raise ReplayError("Unsupported transition parameter; refusing broad substitution")
                if item_id is not None and item_id not in mappings[coll]:
                    raise ReplayError("Transition consumer ID has no verified producer mapping")
            body_b64 = request.get("body", {}).get("$base64") if isinstance(request.get("body"), dict) else None
            raw = base64.b64decode(body_b64) if body_b64 is not None else None
            parsed_body = None
            if raw is not None:
                try:
                    parsed_body = json.loads(raw)
                except (ValueError, UnicodeDecodeError):
                    if any(mappings.values()):
                        raise ReplayError("Cannot safely remap a non-JSON dependent request")
            path, mapped_body = remap_request(uri, parsed_body, mappings)
            response = lab.api.request(method, path, lab.editor_token,
                                       mapped_body, raw_body=raw if parsed_body is None else None,
                                       media_type=stored.get("value", {}).get("media_type", "application/json"))
            report["steps"].append({"case_id": case_id, "parent_id": stored.get("parent_id"), "method": method,
                                    "path": path, "status": response.status, "response_artifact": response.artifact,
                                    "transition": stored.get("transition"), "is_transition_applied": stored.get("is_transition_applied", False)})
            is_target = index == len(chain) - 1
            if not is_target:
                if not 200 <= response.status < 300:
                    raise ReplayError("Producer failed; target will not be sent")
                old_json = response_json(interaction)
                if old_json is not None:
                    mappings[coll].update(map_ids(old_json, response.body, coll))
            else:
                report["target_sent"] = True
                report["sequence_replayed"] = len(chain) > 1
                report["source_status"] = interaction.get("response", {}).get("status_code")
                report["actual_status"] = response.status
                canonical = "/items/" + coll + ("/{id}" if item_id is not None else "")
                actual = validate(schema, method, canonical, response,
                                  path_parameters={"id": urllib.parse.unquote(path.split("?")[0].rsplit("/", 1)[1])} if item_id is not None else None) if method != "TRACE" else []
                report["actual_checks"] = actual
                matched = check_match(recorder.get("checks", {}).get(case_id, []), actual, report["source_status"], response.status)
                report.update(matched)
                report["status"] = "reproduced" if matched["reproduced"] else "checks_unverified" if matched["unsupported_checks"] else "no_source_failure" if not matched["source_had_failures"] else "mismatch"
                rc = 0 if matched["reproduced"] else 1
    except (ReplayError, OSError, KeyError, ValueError, TypeError, RuntimeError) as error:
        report.update(status="sequence_setup_failed" if report["steps"] and not report["target_sent"] else "replay_failed", error=str(error), error_type=type(error).__name__)
    finally:
        report["finished_at"] = utc_now()
        report["runner_exit_code"] = rc
        write_json(run_dir / ("reproducer-schemathesis-" + report_id + ".json"), report)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
