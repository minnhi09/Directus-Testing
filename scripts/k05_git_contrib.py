#!/usr/bin/env python3
"""Thong ke dong gop tu lich su Git (chi doc) de lam bang chung cho danh gia cheo (WP9).

Chi dung du lieu Git that: so commit, so dong them/xoa, thu muc bi tac dong, theo tung tac gia da quy ve mot nguoi
(theo ten tac gia trong Git; khong doc va khong ghi email). Khong suy ra dong gop cua nguoi khong co commit.

Luu y quan trong khi doc ket qua (cung ghi trong file dau ra):
  * So commit va so dong khong phai thuoc do dong gop: commit nho/lon, tai lieu sinh tu cong cu, file sao chep,
    va cong viec khong de lai commit (phan tich, kiem tra, hop nhom) deu khong duoc do.
  * Mot so commit duoc tao trong phien lam viec co su ho tro cong cu AI; Git khong phan biet duoc dieu do.
Dung:
  python scripts/k05_git_contrib.py --ref origin/main --alias "Ten hien thi=ten tac gia 1,ten tac gia 2" ...
"""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "k05" / "wp9" / "git-contribution.json"
IGNORED_PREFIX = ("artifacts/", "runtime/", "tmp/")


def run(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def area(path: str) -> str:
    parts = path.split("/")
    if parts[0] == "docs" and len(parts) > 1:
        if parts[1] == "k05":
            return "docs/k05"
        if parts[1] == "HoanThanhPlan":
            return "docs/HoanThanhPlan"
        if parts[1] in ("coverage", "phan1", "phan2"):
            return f"docs/{parts[1]}"
        return "docs (khác)"
    if parts[0] in ("scripts", "tests", "evidence", "manifest", "config", "profiles"):
        return parts[0]
    return "gốc / khác"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--alias", action="append", required=True,
                    help='"Ten=tac gia 1,tac gia 2" (lap lai cho tung nguoi): cac ten tac gia trong Git duoc gop thanh mot nguoi')
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    owner: dict[str, str] = {}
    for item in args.alias:
        name, _, authors = item.partition("=")
        for e in authors.split(","):
            owner[e.strip().lower()] = name.strip()

    log = run("log", args.ref, "--no-merges", "--numstat", "--format=@@%H|%an|%ad", "--date=short")
    people: dict[str, dict] = {}
    unknown = collections.Counter()
    commit_of: dict[str, str] = {}
    cur = None
    for line in log.splitlines():
        if line.startswith("@@"):
            sha, author, date = line[2:].split("|")
            who = owner.get(author.strip().lower())
            if who is None:
                unknown[author] += 1
                cur = None
                continue
            p = people.setdefault(who, {"commits": 0, "added": 0, "deleted": 0, "first": date, "last": date,
                                        "days": set(), "areas": collections.Counter()})
            p["commits"] += 1
            p["first"] = min(p["first"], date)
            p["last"] = max(p["last"], date)
            p["days"].add(date)
            cur = p
            commit_of[sha] = who
        elif line.strip() and cur is not None:
            a, d, path = (line.split("\t") + ["", "", ""])[:3]
            if path.startswith(IGNORED_PREFIX) or not a.isdigit() or not d.isdigit():
                continue
            cur["added"] += int(a)
            cur["deleted"] += int(d)
            cur["areas"][area(path)] += int(a) + int(d)

    merges = run("log", args.ref, "--merges", "--format=%H").split()
    result = {
        "ref": args.ref,
        "head": run("rev-parse", "--short", args.ref).strip(),
        "commits_no_merge": sum(p["commits"] for p in people.values()),
        "merge_commits": len(merges),
        "unmapped_authors": dict(unknown),
        "people": {
            name: {
                "commits": p["commits"], "lines_added": p["added"], "lines_deleted": p["deleted"],
                "first_commit": p["first"], "last_commit": p["last"], "active_days": len(p["days"]),
                "lines_touched_by_area": dict(p["areas"].most_common()),
            } for name, p in sorted(people.items())
        },
        "caveats": [
            "So commit va so dong khong phai thuoc do dong gop.",
            "Cong viec khong de lai commit (phan tich, kiem tra, hop nhom, review) khong duoc do.",
            "Lich su main da duoc viet lai ngay 23/11/2026 de bo dong dong tac gia khoi 17 commit; tac gia va noi dung khong doi.",
            "Git khong phan biet duoc commit co su ho tro cua cong cu AI.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{args.ref} {result['head']}: {result['commits_no_merge']} commit khong merge, {len(merges)} merge, "
          f"{len(people)} nguoi; tac gia khong ghep duoc: {dict(unknown)}")
    for name, p in result["people"].items():
        print(f"  {name}: {p['commits']} commit, +{p['lines_added']}/-{p['lines_deleted']}, {p['active_days']} ngay, "
              f"{p['first_commit']}..{p['last_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
