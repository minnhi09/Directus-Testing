#!/usr/bin/env python3
"""Lap mau so K05: moi cap (actor, operation) trong OpenAPI cua lab.

Offline va xac dinh. Chi doc 3 file schema theo actor (editor, reader,
anonymous); chi ghi 2 file ket qua. Khong goi server, khong khoi dong lab.
Admin khong thuoc mau so: admin khong phai tai khoan fuzz.

Mau so nay la quyet dinh pham vi cua nguoi dung ngay 23/11/2026 (duyet
"30 operation"), chua co xac nhan cua giang vien hay cua Lanh.

Schema doc vao la ban LICH SU (export 11/10/2026, hash duoc ghi vao ket qua).
Phai export lai tu lab da pin truoc khi dung cho ket luan hien hanh.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = ROOT / "runtime" / "schemas" / "r06-k05-v2"
DEFAULT_OUT_DIR = ROOT / "scripts" / "data"
ACTORS = ("editor", "reader", "anonymous")
METHODS = ("get", "post", "patch", "put", "delete", "search")
# 10 operation cua campaign chinh truoc day (Editor, khong co bulk).
MAIN_10 = {
    ("GET", "/items/qa_categories"), ("POST", "/items/qa_categories"),
    ("GET", "/items/qa_categories/{id}"), ("PATCH", "/items/qa_categories/{id}"),
    ("DELETE", "/items/qa_categories/{id}"),
    ("GET", "/items/qa_articles"), ("POST", "/items/qa_articles"),
    ("GET", "/items/qa_articles/{id}"), ("PATCH", "/items/qa_articles/{id}"),
    ("DELETE", "/items/qa_articles/{id}"),
}
BULK = {
    ("PATCH", "/items/qa_categories"), ("DELETE", "/items/qa_categories"),
    ("PATCH", "/items/qa_articles"), ("DELETE", "/items/qa_articles"),
}


def group_of(path: str) -> str:
    return path.strip("/").split("/", 1)[0]


def scope_class(method: str, path: str) -> str:
    key = (method, path)
    if key in MAIN_10:
        return "MAIN_10"
    if key in BULK:
        return "BULK"
    return "ADDED"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_operations(schema_path: Path) -> list[dict]:
    doc = json.loads(schema_path.read_text(encoding="utf-8"))
    ops = []
    for path, item in doc.get("paths", {}).items():
        for method in METHODS:
            if method in item:
                ops.append({
                    "method": method.upper(),
                    "path": path,
                    "operation_id": item[method].get("operationId", ""),
                })
    return ops


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--schema-note",
        default="ban lich su export 11/10/2026; export lai tu lab da pin truoc khi ket luan",
        help="Ghi chu nguon goc schema (ngay export, run id) de dua vao summary.",
    )
    args = parser.parse_args()

    rows: list[dict] = []
    hashes: dict[str, str] = {}
    for actor in ACTORS:
        schema_path = args.schema_dir / f"{actor}.json"
        if not schema_path.is_file():
            print(f"THIEU schema: {schema_path}", file=sys.stderr)
            return 2
        hashes[actor] = sha256(schema_path)
        for op in load_operations(schema_path):
            rows.append({
                "actor": actor,
                "method": op["method"],
                "path": op["path"],
                "operation_id": op["operation_id"],
                "group": group_of(op["path"]),
                "scope_class": scope_class(op["method"], op["path"]),
                "status": "NOT_RUN",
            })
    rows.sort(key=lambda r: (ACTORS.index(r["actor"]), r["path"], r["method"]))

    unique = {(r["method"], r["path"]) for r in rows}
    summary = {
        "schema": "k05-denominator/1",
        "approved_scope": "30 operation x actor co operation do trong schema (nguoi dung duyet 23/11/2026)",
        "schema_dir": str(args.schema_dir.relative_to(ROOT)) if args.schema_dir.is_relative_to(ROOT) else str(args.schema_dir),
        "schema_sha256": hashes,
        "schema_note": args.schema_note,
        "pairs_total": len(rows),
        "pairs_by_actor": {a: sum(1 for r in rows if r["actor"] == a) for a in ACTORS},
        "unique_operations": len(unique),
        "unique_by_scope_class": {
            c: sum(1 for k in unique if scope_class(*k) == c) for c in ("MAIN_10", "BULK", "ADDED")
        },
        "unique_by_group": {
            g: sum(1 for k in unique if group_of(k[1]) == g)
            for g in sorted({group_of(k[1]) for k in unique})
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.out_dir / "mau-so-30-operation.csv"
    json_path = args.out_dir / "mau-so-30-operation.summary.json"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nDa ghi: {csv_path}\nDa ghi: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
