#!/usr/bin/env python3
"""Tong hop coverage tracecov (WP6) tu cac file schemathesis-coverage.json cua cac run WP5.

Chi doc artifacts/runs/<run_id>/<profile>/seed-*/schemathesis-coverage.json va
campaign-summary.json; khong goi API, khong khoi dong lab. Ghi ra docs/k05/wp6/.

Dinh nghia (theo tracecov 0.25.2 trong Schemathesis 4.30.0):
  operations        so operation duoc gui it nhat mot request
  parameters        tham so (query/path/header/body) duoc thu du cac nhanh hop le/khong hop le
  keywords          tu khoa JSON Schema (type, required, nullable, ...) co ca ca hop le va ca khong hop le
  examples          example trong schema da duoc dung
  responses         ma phan hoi DUOC MO TA trong schema da gap it nhat mot lan
  response_keywords tu khoa trong schema phan hoi da duoc cham toi (reached) / bi vi pham (violated)
Day la coverage THEO SCHEMA, khong phai coverage ma nguon Directus.

Hop (union) qua ba seed:
  * operation / ma phan hoi: dat neu dat o it nhat mot seed;
  * keyword: file bao cao chi liet ke tu khoa CHUA du; tu khoa du neu khong nam trong danh sach
    cua it nhat mot seed, hoac tong valid va tong invalid cua cac seed deu > 0.
Khong tinh union cho tham so va example vi file bao cao chi cho so dem, khong liet ke tung muc.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "artifacts" / "runs"
WP5 = ROOT / "docs" / "k05" / "wp5" / "campaign-summaries.json"
OUT = ROOT / "docs" / "k05" / "wp6"

DIMS = ("operations", "parameters", "keywords", "examples", "responses", "response_keywords")


def pct(part: int, total: int) -> float | None:
    return round(100.0 * part / total, 2) if total else None


def default_run_ids() -> list[str]:
    data = json.loads(WP5.read_text(encoding="utf-8"))
    seen: list[str] = []
    for item in data["runs"]:
        if item["run_id"] not in seen:
            seen.append(item["run_id"])
    return seen


def load_seeds(run_ids: list[str]) -> list[dict]:
    seeds = []
    for run_id in run_ids:
        for cov in sorted((RUNS / run_id).glob("*/seed-*/schemathesis-coverage.json")):
            seed_dir = cov.parent
            summary = json.loads((seed_dir / "campaign-summary.json").read_text(encoding="utf-8"))
            seeds.append({
                "run_id": run_id,
                "profile": summary["profile"],
                "actor": summary["actor"],
                "seed": summary["seed"],
                "complete": bool(summary.get("run_complete")),
                "cov": json.loads(cov.read_text(encoding="utf-8")),
                "path": cov,
            })
    return seeds


def summary_count(cov_summary: dict, dim: str) -> dict:
    s = cov_summary[dim]
    covered = s.get("covered", s.get("reached", 0))
    return {"covered": covered, "partial": s.get("partial", 0), "violated": s.get("violated", 0), "total": s["total"]}


def union_keywords(seeds: list[dict]) -> dict:
    """Union tu khoa tham so: (method, path, location, name, media_type) -> (total, so chua du)."""
    totals: dict[tuple, int] = {}
    lists: dict[tuple, list[dict[str, tuple[int, int]]]] = collections.defaultdict(list)
    for s in seeds:
        for op in s["cov"]["operations"]:
            for p in op.get("parameters", []):
                key = (op["method"], op["path"], p["location"], p.get("name", ""), p.get("media_type", ""))
                totals[key] = p["coverage"]["total"]
                lists[key].append({k["schema_path"]: (k.get("valid", 0), k.get("invalid", 0)) for k in p.get("keywords", [])})
    total_kw = uncovered = 0
    for key, total in totals.items():
        per_seed = lists[key]
        miss = set(per_seed[0])
        for d in per_seed[1:]:
            miss &= set(d)
        still = 0
        for path in miss:
            valid = sum(d[path][0] for d in per_seed)
            invalid = sum(d[path][1] for d in per_seed)
            if not (valid > 0 and invalid > 0):
                still += 1
        total_kw += total
        uncovered += still
    return {"total": total_kw, "covered": total_kw - uncovered}


def union_ops_responses(seeds: list[dict]) -> dict:
    ops_hit: dict[tuple, int] = {}
    docs: dict[tuple, bool] = {}
    undocumented: dict[tuple, set] = collections.defaultdict(set)
    for s in seeds:
        for op in s["cov"]["operations"]:
            k = (op["method"], op["path"])
            ops_hit[k] = ops_hit.get(k, 0) + op["hits"]
            for r in op.get("responses", []):
                docs[(k, r["status"])] = docs.get((k, r["status"]), False) or r["hits"] > 0
            for u in op.get("unexpected_responses", []):
                undocumented[k].add(u["status"])
    return {"ops_hit": ops_hit, "docs": docs, "undocumented": undocumented}


def groups(seeds: list[dict]) -> dict[tuple, list[dict]]:
    g: dict[tuple, list[dict]] = collections.defaultdict(list)
    for s in seeds:
        g[(s["actor"], s["profile"])].append(s)
    return g


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", action="append", help="run_id (lap lai duoc); mac dinh: cac run cua WP5")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    run_ids = args.run or default_run_ids()
    seeds = load_seeds(run_ids)
    if not seeds:
        print("khong tim thay schemathesis-coverage.json", file=sys.stderr)
        return 2
    versions = sorted({s["cov"]["tracecov_version"] for s in seeds})

    # 1) theo seed
    rows = []
    for s in sorted(seeds, key=lambda x: (x["actor"], x["profile"], x["seed"])):
        sm = s["cov"]["summary"]
        row = [s["actor"], s["profile"], s["seed"], s["run_id"], s["complete"]]
        for dim in DIMS:
            c = summary_count(sm, dim)
            row += [c["covered"], c["total"], sm[dim].get("percent")]
        rows.append(row)
    header = ["actor", "profile", "seed", "run_id", "run_complete"]
    for dim in DIMS:
        header += [f"{dim}_covered", f"{dim}_total", f"{dim}_percent"]
    write_csv(args.out / "coverage-theo-seed.csv", header, rows)

    # 2) theo nhom (actor, profile): min/max/mean cua ba seed va union
    grows = []
    summary_json = {"tracecov_version": versions, "groups": []}
    for (actor, profile), items in sorted(groups(seeds).items()):
        u = union_ops_responses(items)
        ukw = union_keywords(items)
        n_ops = len(u["ops_hit"])
        ops_hit = sum(1 for v in u["ops_hit"].values() if v > 0)
        doc_total = len(u["docs"])
        doc_hit = sum(1 for v in u["docs"].values() if v)
        row = [actor, profile, len(items)]
        entry = {"actor": actor, "profile": profile, "seeds": len(items), "dimensions": {}}
        for dim in ("operations", "parameters", "keywords", "examples", "responses", "response_keywords"):
            vals = [s["cov"]["summary"][dim].get("percent") for s in items]
            vals = [v for v in vals if v is not None]
            lo, hi = (min(vals), max(vals)) if vals else (None, None)
            mean = round(sum(vals) / len(vals), 2) if vals else None
            total = items[0]["cov"]["summary"][dim]["total"]
            row += [total, lo, mean, hi]
            entry["dimensions"][dim] = {"total": total, "min": lo, "mean": mean, "max": hi}
        row += [f"{ops_hit}/{n_ops}", f"{doc_hit}/{doc_total}", f"{ukw['covered']}/{ukw['total']}", pct(ukw["covered"], ukw["total"])]
        entry["union"] = {
            "operations": {"covered": ops_hit, "total": n_ops},
            "documented_responses": {"covered": doc_hit, "total": doc_total},
            "parameter_keywords": ukw,
        }
        grows.append(row)
        summary_json["groups"].append(entry)
    gheader = ["actor", "profile", "seeds"]
    for dim in DIMS:
        gheader += [f"{dim}_total", f"{dim}_min_pct", f"{dim}_mean_pct", f"{dim}_max_pct"]
    gheader += ["union_operations", "union_documented_responses", "union_parameter_keywords", "union_keywords_pct"]
    write_csv(args.out / "coverage-theo-nhom.csv", gheader, grows)

    # 3) theo cap (actor, operation): hop tren moi run cua actor
    prow = []
    by_actor = collections.defaultdict(list)
    for s in seeds:
        by_actor[s["actor"]].append(s)
    for actor, items in sorted(by_actor.items()):
        u = union_ops_responses(items)
        keys = sorted(u["ops_hit"])
        for k in keys:
            statuses = sorted(st for (kk, st) in u["docs"] if kk == k)
            hit = sorted(st for (kk, st) in u["docs"] if kk == k and u["docs"][(kk, st)])
            missed = [st for st in statuses if st not in hit]
            und = sorted(u["undocumented"].get(k, set()))
            prow.append([actor, k[0], k[1], u["ops_hit"][k], ";".join(statuses), ";".join(hit), ";".join(missed), ";".join(und)])
    write_csv(args.out / "coverage-theo-cap.csv",
              ["actor", "method", "path", "tracecov_hits", "documented_statuses", "documented_hit", "documented_missed", "undocumented_seen"],
              prow)

    summary_json["seed_count"] = len(seeds)
    summary_json["run_ids"] = run_ids
    (args.out / "coverage-summary.json").write_text(json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"tracecov {versions}; {len(seeds)} seed; ghi vao {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
