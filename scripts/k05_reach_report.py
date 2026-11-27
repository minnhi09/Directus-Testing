#!/usr/bin/env python3
"""Bang C1/C2 cua K05: moi cap (actor, operation) trong mau so da nhan phan hoi nao.

Doc cac thu muc run campaign (artifacts/runs/<run_id>) va file mau so
scripts/data/mau-so-30-operation.csv. Chi doc, khong goi API, khong khoi dong lab.

Quy tac dem (de khong thoi phong so lieu):
  * chi dem tuong tac co phuong thuc HTTP trung phuong thuc cua operation. Request
    "unsupported_method" (TRACE...) la phep thu am tinh, khong phai bang chung cho operation;
  * tuong tac trong pha stateful duoc gan operation bang phuong thuc + duong dan, khong dua vao nhan;
  * evidence_class la nhan mo ta, khong phai ket luan dung/sai cua Directus.

evidence_class:
  SUCCESS_2XX     co it nhat mot phan hoi 2xx
  DENIED_401_403  khong co 2xx; co 401/403 (request toi tang xac thuc/phan quyen)
  REJECTED_4XX    khong co 2xx/401/403; co 4xx khac
  SERVER_ERROR    chi co 5xx
  NO_RESPONSE     co request nhung khong co phan hoi
  NOT_EXECUTED    cap (actor, operation) khong co request nao trong cac run da cho
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENOMINATOR = ROOT / "scripts" / "data" / "mau-so-30-operation.csv"
RUNS = ROOT / "artifacts" / "runs"
LABEL_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE|SEARCH) (/\S*)$")


def load_denominator(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def template_matcher(paths: list[str]):
    compiled = []
    for p in sorted(set(paths)):
        regex = "^" + re.sub(r"\\\{[^}]+\\\}", "[^/]+", re.escape(p)) + "$"
        compiled.append((p, re.compile(regex)))
    # most specific first (more literal characters)
    compiled.sort(key=lambda x: -len(re.sub(r"\{[^}]+\}", "", x[0])))

    def match(uri_path: str):
        for template, rx in compiled:
            if rx.match(uri_path):
                return template
        return None

    return match


def uri_path(uri: str) -> str:
    rest = uri.split("://", 1)[-1]
    path = "/" + rest.split("/", 1)[1] if "/" in rest else "/"
    return path.split("?", 1)[0]


def iter_seed_dirs(run_dir: Path):
    for events in sorted(run_dir.glob("*/seed-*/schemathesis-events.ndjson")):
        yield events.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("runs", nargs="+", help="run_id hoac duong dan thu muc run (artifacts/runs/<id>)")
    ap.add_argument("--denominator", type=Path, default=DENOMINATOR)
    ap.add_argument("--out", type=Path, help="ghi bang theo cap (actor, operation) ra CSV")
    args = ap.parse_args()

    denominator = load_denominator(args.denominator)
    match = template_matcher([r["path"] for r in denominator])
    stats: dict[tuple, dict] = {}
    for row in denominator:
        key = (row["actor"], row["method"], row["path"])
        stats[key] = {"codes": collections.Counter(), "profiles": set(), "runs": set(), "requests": 0}

    unknown = collections.Counter()
    for token in args.runs:
        run_dir = Path(token) if Path(token).is_dir() else RUNS / token
        if not run_dir.is_dir():
            print(f"THIEU thu muc run: {token}", file=sys.stderr)
            return 2
        for seed_dir in iter_seed_dirs(run_dir):
            summary_file = seed_dir / "campaign-summary.json"
            summary = json.loads(summary_file.read_text(encoding="utf-8")) if summary_file.is_file() else {}
            actor = summary.get("actor", "editor")
            profile = summary.get("profile", seed_dir.parent.name)
            with (seed_dir / "schemathesis-events.ndjson").open(encoding="utf-8") as f:
                for line in f:
                    try:
                        sf = json.loads(line).get("ScenarioFinished")
                    except ValueError:
                        continue
                    if not sf:
                        continue
                    rec = sf.get("recorder", {})
                    label = LABEL_RE.match(rec.get("label", ""))
                    for inter in (rec.get("interactions") or {}).values():
                        req = (inter or {}).get("request") or {}
                        method = (req.get("method") or "").upper()
                        template = label.group(2) if label else match(uri_path(req.get("uri", "")))
                        if label and method != label.group(1):
                            continue  # negative probe with another method
                        key = (actor, method, template)
                        if key not in stats:
                            unknown[key] += 1
                            continue
                        st = stats[key]
                        st["requests"] += 1
                        st["profiles"].add(profile)
                        st["runs"].add(run_dir.name)
                        code = ((inter or {}).get("response") or {}).get("status_code")
                        st["codes"]["none" if code is None else code] += 1

    def classify(st: dict) -> str:
        if st["requests"] == 0:
            return "NOT_EXECUTED"
        codes = st["codes"]
        ints = [c for c in codes if isinstance(c, int)]
        if any(200 <= c < 300 for c in ints):
            return "SUCCESS_2XX"
        if any(c in (401, 403) for c in ints):
            return "DENIED_401_403"
        if any(400 <= c < 500 for c in ints):
            return "REJECTED_4XX"
        if any(c >= 500 for c in ints):
            return "SERVER_ERROR"
        return "NO_RESPONSE"

    out_rows = []
    for row in denominator:
        key = (row["actor"], row["method"], row["path"])
        st = stats[key]
        codes = st["codes"]
        ints = [c for c in codes if isinstance(c, int)]
        out_rows.append({
            "actor": row["actor"], "method": row["method"], "path": row["path"],
            "scope_class": row["scope_class"],
            "requests": st["requests"],
            "n_2xx": sum(v for c, v in codes.items() if isinstance(c, int) and 200 <= c < 300),
            "n_3xx": sum(v for c, v in codes.items() if isinstance(c, int) and 300 <= c < 400),
            "n_4xx": sum(v for c, v in codes.items() if isinstance(c, int) and 400 <= c < 500),
            "n_5xx": sum(v for c, v in codes.items() if isinstance(c, int) and c >= 500),
            "status_codes": ";".join(f"{c}x{v}" for c, v in sorted(codes.items(), key=lambda kv: str(kv[0]))),
            "profiles": ",".join(sorted(st["profiles"])),
            "runs": ",".join(sorted(st["runs"])),
            "evidence_class": classify(st),
        })

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            w.writeheader()
            w.writerows(out_rows)

    total = len(out_rows)
    by_class = collections.Counter(r["evidence_class"] for r in out_rows)
    by_actor = {a: collections.Counter(r["evidence_class"] for r in out_rows if r["actor"] == a)
                for a in ("editor", "reader", "anonymous")}
    print(f"Mau so: {total} cap (actor, operation); {sum(1 for r in out_rows if r['requests'] > 0)} cap co request")
    for cls in ("SUCCESS_2XX", "DENIED_401_403", "REJECTED_4XX", "SERVER_ERROR", "NO_RESPONSE", "NOT_EXECUTED"):
        print(f"  {cls:15s} {by_class[cls]:3d}   " + "  ".join(f"{a}={by_actor[a][cls]}" for a in by_actor))
    with_5xx = [r for r in out_rows if r["n_5xx"] > 0]
    print(f"Cap (actor, operation) co it nhat mot phan hoi 5xx: {len(with_5xx)} (so tuong tac 5xx khong phai so defect)")
    if unknown:
        print(f"Tuong tac khong thuoc mau so (bo qua): {sum(unknown.values())}")
    if args.out:
        print(f"Da ghi: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
