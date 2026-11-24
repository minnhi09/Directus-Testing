#!/usr/bin/env python3
"""Kiem tra lien ket tuong doi trong cac file Markdown (chi doc, khong goi mang).

Bao cao moi lien ket [text](duong/dan) tro toi file hoac thu muc khong ton tai, va neu co #anchor
thi kiem tra tieu de tuong ung trong file dich. Bo qua http(s), mailto va anchor thuan trong cung file
(anchor trong cung file van duoc kiem tra). Khong kiem tra lien ket nam trong khoi ma (```).

Dung:
  python scripts/check_md_links.py                  # quet moi file .md ma Git dang theo doi
  python scripts/check_md_links.py docs/k05         # quet mot thu muc hoac mot file
Ma thoat 1 neu co lien ket hong.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")


def slug(text: str) -> str:
    """Quy tac tao anchor kieu GitHub: chu thuong, bo dau cau, khoang trang thanh '-'."""
    text = re.sub(r"[`*_~]", "", text.strip().lower())
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    out: set[str] = set()
    seen: dict[str, int] = {}
    fence = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = HEADING_RE.match(line)
        if m:
            s = slug(m.group(1))
            n = seen.get(s, 0)
            seen[s] = n + 1
            out.add(s if n == 0 else f"{s}-{n}")
    return out


def iter_links(path: Path):
    fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        stripped = re.sub(r"`[^`]*`", "", line)  # bo ma inline
        for rx in (LINK_RE, IMG_RE):
            for m in rx.finditer(stripped):
                yield lineno, m.group(1)


def check_file(md: Path) -> list[tuple[int, str, str]]:
    problems = []
    for lineno, target in iter_links(md):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):  # http:, https:, mailto: ...
            continue
        path_part, _, frag = target.partition("#")
        path_part = unquote(path_part)
        if not path_part:
            dest = md
        else:
            dest = (md.parent / path_part).resolve() if not path_part.startswith("/") else (ROOT / path_part.lstrip("/")).resolve()
            if not dest.exists():
                problems.append((lineno, target, "dich khong ton tai"))
                continue
        if frag and dest.is_file() and dest.suffix.lower() == ".md":
            if unquote(frag).lower() not in {a.lower() for a in anchors_of(dest)}:
                problems.append((lineno, target, "khong co tieu de tuong ung"))
    return problems


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", help="file hoac thu muc; mac dinh: moi file .md Git dang theo doi")
    args = ap.parse_args()
    files: list[Path] = []
    if args.paths:
        for raw in args.paths:
            t = Path(raw)
            t = t if t.is_absolute() else (Path.cwd() / t)
            if t.is_file():
                files.append(t)
            elif t.is_dir():
                files.extend(sorted(t.rglob("*.md")))
    else:  # mac dinh: chi cac file Markdown da duoc Git theo doi
        out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        files = [ROOT / line for line in out.stdout.splitlines() if line.strip()]
    bad = 0
    for md in files:
        for lineno, target, why in check_file(md):
            bad += 1
            print(f"{md.relative_to(ROOT)}:{lineno}: {target} ({why})")
    print(f"{len(files)} file; {bad} lien ket hong")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
