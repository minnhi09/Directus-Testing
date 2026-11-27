#!/usr/bin/env python3
"""Gom failure cua cac luot sinh tu dong: tu NDJSON cua Schemathesis sang nhom nguyen nhan.

Chi doc artifacts/runs/<run_id>/<profile>/seed-*/schemathesis-events.ndjson va campaign-summary.json;
khong goi API, khong khoi dong lab. Ghi ra results/failures/:
  failure-groups.csv   moi dong mot nhom (actor, operation, check, loai failure, ma phan hoi, thong diep chuan hoa)
  failure-stats.json   ba con so khac nhau: request, check bi fail, nhom
  group-exemplars.json moi nhom mot request/phan hoi mau (da loc bi mat) de lam reproducer

Ba con so KHONG duoc dong nhat:
  requests       so tuong tac HTTP ghi trong NDJSON
  check_failures so lan mot check bao that bai (mot request co the that bai nhieu check)
  groups         so nhom nguyen nhan sau khi gom
  defects        so loi san pham da xac nhan: KHONG tinh o day, quyet dinh bang tay trong README
"""
from __future__ import annotations

import argparse
import base64
import collections
import csv
import datetime
import json
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "artifacts" / "runs"
SUMMARIES = ROOT / "results" / "campaign" / "campaign-summaries.json"
OUT = ROOT / "results" / "failures"
SECRET_HEADERS = {"authorization", "cookie", "set-cookie"}


def b64_text(node, limit: int = 400) -> str:
    if node is None:
        return ""
    if isinstance(node, dict) and "$base64" in node:
        try:
            raw = base64.b64decode(node["$base64"]).decode("utf-8", "replace")
        except Exception:
            return "<khong giai ma duoc>"
    else:
        raw = str(node)
    return raw if len(raw) <= limit else raw[:limit] + "...(cat)"


def norm_message(text: str) -> str:
    text = re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<uuid>", text)
    text = re.sub(r"\d+", "<n>", text)
    return " ".join(text.split())[:240]


def error_summary(content: str) -> str:
    """Rut gon body loi cua Directus thanh 'CODE: message' neu parse duoc."""
    try:
        data = json.loads(content)
        err = data["errors"][0]
        return f"{err.get('extensions', {}).get('code', '?')}: {err.get('message', '')}"
    except Exception:
        return content[:160]


INT4_MAX = 2147483647

# Bang nguyen nhan (RC). category: PRODUCT, SCHEMA, HARNESS, ENV, UNRESOLVED.
RC = {
    "RC01": ("PRODUCT", "ID trong duong dan hoac body ngoai khoang int4 -> loi DB khong duoc dich o duong doc/sua/xoa, tra 500"),
    "RC02": ("PRODUCT", "aggregate sai cau truc (gia tri khong phai mang/chuoi, hoac khong phai JSON) -> TypeError, tra 500"),
    "RC03": ("PRODUCT", "published_at khong phai ngay gio (boolean/chuoi/so) -> loi PostgreSQL 22007 khong duoc dich, tra 500"),
    "RC04": ("PRODUCT", "chuoi chua ky tu NUL (U+0000) -> loi PostgreSQL 22021 khong duoc dich, tra 500"),
    "RC12": ("PRODUCT", "phan tu null trong mang body cua POST -> TypeError, tra 500"),
    "RC13": ("PRODUCT", "id/khoa ngoai sai kieu (boolean, chuoi rong, mang, chuoi khong phai so) hoac so >= 1e21 (bieu dien mu) -> loi PostgreSQL 22P02 khong duoc dich, tra 500"),
    "RC14": ("PRODUCT", "export=csv voi fields tro toi duong dan khong co that (vi du sections.item:headings.title) -> 500"),
    "RC15": ("PRODUCT", "page x limit vuot gioi han so nguyen 64 bit -> loi DB, tra 500"),
    "RC16": ("PRODUCT", "groupBy co dau ngoac dong dat truoc dau ngoac mo (vi du a)b() -> TypeError, tra 500"),
    "RC05": ("PRODUCT", "phuong thuc khong ho tro (TRACE) tra 404 thay vi 405 (muc do thap, chua ro la co y)"),
    "RC06": ("SCHEMA", "schema mo ta 200 nhung Directus tra 204 No Content"),
    "RC07": ("SCHEMA", "schema khong mo ta cac ma loi 4xx ma Directus tra ve (400, 401, 403, 404, 415...)"),
    "RC08": ("SCHEMA", "Content-Type phan hoi khac schema (ping tra text/html; export csv/xml/yaml)"),
    "RC09": ("SCHEMA", "schema phan hoi qua cung: fields chon cot lam doi hinh du lieu, POST tra doi tuong thay vi mang, export=json tra mang tran"),
    "RC10": ("SCHEMA", "request hop le theo schema nhung bi tu choi (rang buoc runtime khong co trong schema: otp rong, thieu refresh_token, multipart...)"),
    "RC11": ("UNRESOLVED", "du lieu/tham so sai nhung duoc chap nhan (Directus bo qua tham so la, PATCH chi {id}); chua ket luan la loi hay thiet ke"),
    "RC99": ("UNRESOLVED", "chua phan loai duoc"),
}


def decode_text(node) -> str:
    if node is None:
        return ""
    if isinstance(node, dict) and "$base64" in node:
        try:
            return base64.b64decode(node["$base64"]).decode("utf-8", "replace")
        except Exception:
            return ""
    return str(node)


def _bad_datetime(value) -> bool:
    if value is None:
        return False
    if not isinstance(value, str):
        return True
    try:
        datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return False
    except ValueError:
        return True


def _bad_id(value) -> bool:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return abs(value) >= 10**21  # JS dung bieu dien so mu tu 1e21: PostgreSQL bao 22P02 thay vi 22003
    if value is None:
        return False
    if isinstance(value, str):
        return not value.lstrip("-").isdigit()
    return True


def cause_5xx(uri: str, body_text: str) -> str:
    """Xac dinh nguyen nhan cua mot phan hoi 5xx tu CHINH request.

    Cac nguyen nhan da duoc xac nhan bang replay (scripts/k05_wp7_replay.py va cac probe bo sung);
    khong khop quy tac nao thi tra ve RC99 (chua phan loai).
    """
    path, _, query = uri.partition("?")
    params = dict(urllib.parse.parse_qsl(query, keep_blank_values=True, errors="replace")) if query else {}
    m = re.search(r"/items/[^/]+/(-?\d+)$", path)
    if m and abs(int(m.group(1))) > INT4_MAX:
        return "RC01"
    if "aggregate" in params:
        return "RC02"
    if "%00" in query or "\\u0000" in body_text or "\x00" in body_text:
        return "RC04"
    gb = params.get("groupBy", "")
    if ")" in gb and "(" in gb and gb.index(")") < gb.rindex("("):
        return "RC16"
    if str(params.get("export", "")).startswith("csv") and ":" in params.get("fields", ""):
        return "RC14"
    try:
        if "page" in params and "limit" in params and int(params["page"]) * int(params["limit"]) > 2**63 - 1:
            return "RC15"
    except ValueError:
        pass
    try:
        data = json.loads(body_text) if body_text else None
    except ValueError:
        data = None
    items = data if isinstance(data, list) else [data]
    if isinstance(data, list) and any(el is None for el in data):
        return "RC12"
    for el in items:
        if not isinstance(el, dict):
            continue
        if "published_at" in el and _bad_datetime(el["published_at"]):
            return "RC03"
        if "id" in el and _bad_id(el["id"]):
            return "RC13"
        cat = el.get("category")
        if isinstance(cat, dict) and "id" in cat and _bad_id(cat["id"]):
            return "RC13"
        if "category" in el and not isinstance(cat, dict) and _bad_id(cat):
            return "RC13"
    return "RC99"


def classify(ftype: str, status, uri: str, body_text: str) -> str:
    if (status or 0) >= 500:
        return cause_5xx(uri, body_text)
    if ftype == "UnsupportedMethodResponse":
        return "RC05"
    if ftype == "UndefinedStatusCode":
        return "RC06" if status == 204 else "RC07"
    if ftype == "UndefinedContentType":
        return "RC08"
    if ftype == "JsonSchemaError":
        return "RC09"
    if ftype == "RejectedPositiveData":
        return "RC10"
    if ftype == "AcceptedNegativeData":
        return "RC11"
    return "RC99"


def default_run_ids() -> list[str]:
    data = json.loads(SUMMARIES.read_text(encoding="utf-8"))
    out: list[str] = []
    for item in data["runs"]:
        if item["run_id"] not in out:
            out.append(item["run_id"])
    return out


def scan_seed(ndjson: Path, actor: str, profile: str, seed: int, groups: dict, exemplars: dict, stats: dict, census: collections.Counter) -> None:
    for line in ndjson.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        ev = json.loads(line)
        if "ScenarioFinished" not in ev:
            continue
        body = ev["ScenarioFinished"]
        phase = body.get("phase", "?")
        rec = body["recorder"]
        interactions = rec.get("interactions") or {}
        stats["requests"] += len(interactions)
        for _cid, _i in interactions.items():
            _resp = _i.get("response") or {}
            if (_resp.get("status_code") or 0) >= 500:
                _rq = _i["request"]
                census[classify("ServerError", _resp["status_code"], _rq["uri"], decode_text(_rq.get("body")))] += 1
        stats["cases_without_response"] += sum(1 for k in (rec.get("cases") or {}) if k not in interactions)
        for case_id, checks in (rec.get("checks") or {}).items():
            inter = interactions.get(case_id)
            status = inter["response"]["status_code"] if inter and inter.get("response") else None
            for chk in checks:
                stats["checks_run"] += 1
                if chk["status"] != "failure":
                    continue
                stats["check_failures"] += 1
                fail = chk["failure_info"]["failure"]
                msg = norm_message(fail.get("message", ""))
                resp_text = ""
                if inter and inter.get("response"):
                    resp_text = error_summary(b64_text(inter["response"].get("content"), 2000))
                # nhom 5xx theo ma loi cua Directus; cac nhom khac theo thong diep chuan hoa
                detail = norm_message(resp_text) if (status and status >= 500) else msg
                rc = "RC99"
                if inter:
                    rq = inter["request"]
                    rc = classify(fail.get("type", "?"), status, rq["uri"], decode_text(rq.get("body")))
                key = (actor, fail.get("operation", rec.get("label", "?")), chk["name"], fail.get("type", "?"), status, detail, rc)
                g = groups.setdefault(key, {"count": 0, "profiles": set(), "seeds": set(), "phases": set(), "severity": fail.get("severity", "")})
                g["count"] += 1
                g["profiles"].add(profile)
                g["seeds"].add(seed)
                g["phases"].add(phase)
                if key not in exemplars and inter:
                    req = inter["request"]
                    exemplars[key] = {
                        "actor": actor, "profile": profile, "seed": seed, "phase": phase,
                        "check": chk["name"], "failure_type": fail.get("type"),
                        "operation": fail.get("operation"), "message": fail.get("message"), "root_cause": rc,
                        "request": {
                            "method": req["method"], "uri": req["uri"],
                            "headers": {k: v for k, v in req.get("headers", {}).items() if k.lower() not in SECRET_HEADERS},
                            "body": b64_text(req.get("body")),
                        },
                        "response": {
                            "status": status,
                            "content_type": (inter["response"]["headers"].get("content-type") or [""])[0],
                            "body": b64_text(inter["response"].get("content")),
                        },
                    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="append", help="run_id (lap lai duoc); mac dinh: cac run trong results/campaign")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    groups: dict = {}
    exemplars: dict = {}
    census: collections.Counter = collections.Counter()
    per_seed = []
    for run_id in args.run or default_run_ids():
        for nd in sorted((RUNS / run_id).glob("*/seed-*/schemathesis-events.ndjson")):
            summary = json.loads((nd.parent / "campaign-summary.json").read_text(encoding="utf-8"))
            stats = {"requests": 0, "checks_run": 0, "check_failures": 0, "cases_without_response": 0}
            before = len(groups)
            scan_seed(nd, summary["actor"], summary["profile"], summary["seed"], groups, exemplars, stats, census)
            tc = (summary.get("schemathesis") or {}).get("test_cases") or {}
            per_seed.append({
                "run_id": run_id, "actor": summary["actor"], "profile": summary["profile"], "seed": summary["seed"],
                **stats, "schemathesis_unique_failures": tc.get("unique_failures"),
                "schemathesis_generated_cases": tc.get("generated"),
                "schemathesis_errored_cases": tc.get("errored"),
            })
    if not per_seed:
        print("khong tim thay schemathesis-events.ndjson", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    rows = []
    for key, g in sorted(groups.items(), key=lambda kv: (kv[0][6], kv[0][0], kv[0][1], kv[0][2], kv[0][3], str(kv[0][4]), kv[0][5])):
        actor, op, check, ftype, status, detail, rc = key
        rows.append([rc, RC[rc][0], actor, op, check, ftype, status, detail, g["count"], ";".join(sorted(g["profiles"])),
                     len(g["seeds"]), ";".join(sorted(g["phases"])), g["severity"]])
    with (args.out / "failure-groups.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["root_cause", "category", "actor", "operation", "check", "failure_type", "response_status", "detail", "occurrences", "profiles", "seed_count", "phases", "severity"])
        w.writerows(rows)

    totals = {k: sum(s[k] for s in per_seed) for k in ("requests", "checks_run", "check_failures", "cases_without_response")}
    stats_out = {"seeds": len(per_seed), "totals": totals, "groups": len(groups), "per_seed": per_seed}
    by_actor = collections.defaultdict(lambda: collections.Counter())
    by_rc = collections.defaultdict(lambda: collections.Counter())
    for (actor, op, check, ftype, status, detail, rc), g in groups.items():
        by_actor[actor]["groups"] += 1
        by_actor[actor]["check_failures"] += g["count"]
        by_rc[rc]["groups"] += 1
        by_rc[rc]["check_failures"] += g["count"]
        by_rc[rc][f"actor_{actor}"] += g["count"]
    stats_out["by_actor"] = {a: dict(c) for a, c in by_actor.items()}
    stats_out["by_root_cause"] = {rc: {"category": RC[rc][0], "description": RC[rc][1], **dict(c)} for rc, c in sorted(by_rc.items())}
    cat = collections.Counter()
    for rc, c in by_rc.items():
        cat[RC[rc][0]] += c["check_failures"]
    stats_out["check_failures_by_category"] = dict(cat)
    stats_out["server_error_interactions"] = {"total": sum(census.values()), "by_root_cause": dict(sorted(census.items()))}
    (args.out / "failure-stats.json").write_text(json.dumps(stats_out, ensure_ascii=False, indent=2), encoding="utf-8")

    ex_out = [dict(key=list(map(str, k)), **v) for k, v in sorted(exemplars.items(), key=lambda kv: tuple(map(str, kv[0])))]
    (args.out / "group-exemplars.json").write_text(json.dumps(ex_out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(per_seed)} seed; {totals['requests']} request; {totals['check_failures']} check fail; {len(groups)} nhom -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
