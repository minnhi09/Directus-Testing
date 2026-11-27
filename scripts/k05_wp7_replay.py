#!/usr/bin/env python3

"""Replay co chu dich cac nhom failure de tim nguyen nhan (chi loopback, lab r06-k05).



Doc config/lab.env TRONG BO NHO; khong in va khong ghi mat khau/token. Chi gui toi http://127.0.0.1:8055.

Moi probe ghi: gia thuyet, actor, request, ma phan hoi, ma loi Directus. Cuoi cung kiem tra

qa_* khong doi (so dong, ID lon nhat); neu probe lo tao dong thi bao cao va xoa bang admin.

Ghi ket qua vao results/failures/replay-results.json.

"""

from __future__ import annotations



import json

import sys

import time

import urllib.error

import urllib.parse

import urllib.request

from pathlib import Path



ROOT = Path(__file__).resolve().parents[1]

BASE = "http://127.0.0.1:8055"

OUT = ROOT / "results" / "failures" / "replay-results.json"





def load_env() -> dict[str, str]:

    env = {}

    for line in (ROOT / "config" / "lab.env").read_text(encoding="utf-8").splitlines():

        line = line.strip()

        if line and not line.startswith("#") and "=" in line:

            k, v = line.split("=", 1)

            env[k.strip()] = v.strip().strip('"').strip("'")

    return env





def call(method: str, path: str, token: str | None = None, body=None, raw_body: bytes | None = None, ctype: str | None = None):

    headers = {}

    data = None

    if token:

        headers["Authorization"] = f"Bearer {token}"

    if raw_body is not None:

        data = raw_body

        headers["Content-Type"] = ctype or "application/json"

    elif body is not None:

        data = json.dumps(body).encode()

        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)

    try:

        with urllib.request.urlopen(req, timeout=15) as r:

            return r.status, r.read().decode("utf-8", "replace")

    except urllib.error.HTTPError as e:

        return e.code, e.read().decode("utf-8", "replace")





def login(email: str, password: str) -> str:

    s, t = call("POST", "/auth/login", body={"email": email, "password": password})

    if s != 200:

        raise SystemExit(f"dang nhap that bai ({s})")

    return json.loads(t)["data"]["access_token"]





def brief(text: str) -> dict:

    try:

        j = json.loads(text)

        if "errors" in j:

            e = j["errors"][0]

            return {"code": e.get("extensions", {}).get("code"), "message": e.get("message", "")[:160]}

        d = j.get("data")

        if isinstance(d, list):

            return {"data_list_len": len(d)}

        if isinstance(d, dict):

            return {"data_keys": sorted(d)[:8]}

        return {"data": str(d)[:60]}

    except Exception:

        return {"raw": text[:120]}





def state(admin: str) -> dict:

    out = {}

    for c in ("qa_articles", "qa_categories"):

        s, t = call("GET", f"/items/{c}?limit=-1&fields=id", admin)

        ids = [r["id"] for r in json.loads(t)["data"]] if s == 200 else []

        out[c] = {"count": len(ids), "max_id": max(ids) if ids else None}

    return out





def purge_probe_rows(admin: str) -> list[dict]:

    """Xoa moi dong qa_* co nhan bat dau bang k05-probe (do probe lan truoc de lai); tra ve danh sach da xoa."""

    removed = []

    for c, field in (("qa_articles", "title"), ("qa_categories", "name")):

        s, t = call("GET", f"/items/{c}?limit=-1&fields=id,{field}", admin)

        if s != 200:

            continue

        for row in json.loads(t)["data"]:

            if str(row.get(field) or "").startswith("k05-probe"):

                ds, _ = call("DELETE", f"/items/{c}/{row['id']}", admin)

                removed.append({"collection": c, "id": row["id"], "delete_status": ds})

    return removed





def main() -> int:

    if hasattr(sys.stdout, "reconfigure"):

        sys.stdout.reconfigure(encoding="utf-8")

    env = load_env()

    tokens = {

        "admin": login(env["ADMIN_EMAIL"], env["ADMIN_PASSWORD"]),

        "editor": login(env["EDITOR_EMAIL"], env["EDITOR_PASSWORD"]),

        "reader": login(env["READER_EMAIL"], env["READER_PASSWORD"]),

    }

    purge_probe_rows(tokens["admin"])

    before = state(tokens["admin"])

    Q = urllib.parse.quote

    probes = [

        # H1: ID ngoai khoang int4 cua PostgreSQL

        ("H1", "GET id=2147483647 (max int4) - doi chung", "editor", "GET", "/items/qa_articles/2147483647", None),

        ("H1", "GET id=2147483648 (max int4 + 1)", "editor", "GET", "/items/qa_articles/2147483648", None),

        ("H1", "GET id=9999999999", "editor", "GET", "/items/qa_articles/9999999999", None),

        ("H1", "GET id=-173822012232 (am, ngoai int4)", "editor", "GET", "/items/qa_articles/-173822012232", None),

        ("H1", "GET id=-1 (am, trong int4)", "editor", "GET", "/items/qa_articles/-1", None),

        ("H1", "GET id=999999 (khong ton tai, trong int4)", "editor", "GET", "/items/qa_articles/999999", None),

        ("H1", "GET id=abc (khong phai so)", "editor", "GET", "/items/qa_articles/abc", None),

        ("H1", "DELETE id=9999999999", "editor", "DELETE", "/items/qa_articles/9999999999", None),

        ("H1", "DELETE id=999999 (khong ton tai)", "editor", "DELETE", "/items/qa_articles/999999", None),

        ("H1", "PATCH id=9999999999", "editor", "PATCH", "/items/qa_articles/9999999999", {"title": "k05-probe"}),

        ("H1", "PATCH id=999999 (khong ton tai)", "editor", "PATCH", "/items/qa_articles/999999", {"title": "k05-probe"}),

        ("H1", "GET qa_categories id=78159021685995732992", "editor", "GET", "/items/qa_categories/78159021685995732992", None),

        ("H1", "admin GET id=9999999999", "admin", "GET", "/items/qa_articles/9999999999", None),

        ("H1", "admin GET id=999999", "admin", "GET", "/items/qa_articles/999999", None),

        ("H1", "reader GET id=9999999999", "reader", "GET", "/items/qa_articles/9999999999", None),

        # H2: aggregate sai cau truc (P5-F01)

        ("H2", "aggregate={\"foo\":1}", "editor", "GET", "/items/qa_articles?aggregate=" + Q('{"foo":1}'), None),

        ("H2", "aggregate={\"count\":\"*\"} - doi chung hop le", "editor", "GET", "/items/qa_articles?aggregate=" + Q('{"count":"*"}'), None),

        ("H2", "aggregate={\"count\":[\"x\"]}", "editor", "GET", "/items/qa_articles?aggregate=" + Q('{"count":["x"]}'), None),

        ("H2", "aggregate=[]", "editor", "GET", "/items/qa_articles?aggregate=" + Q("[]"), None),

        ("H2", "aggregate=abc (khong phai JSON)", "editor", "GET", "/items/qa_articles?aggregate=abc", None),

        ("H2", "reader aggregate={\"foo\":1}", "reader", "GET", "/items/qa_articles?aggregate=" + Q('{"foo":1}'), None),

        ("H2", "qa_categories aggregate={\"foo\":1}", "editor", "GET", "/items/qa_categories?aggregate=" + Q('{"foo":1}'), None),

        ("H2", "admin aggregate={\"foo\":1}", "admin", "GET", "/items/qa_articles?aggregate=" + Q('{"foo":1}'), None),

        # H3: fields / deep / sort la

        ("H3", "fields=sections.item:headings.title", "editor", "GET", "/items/qa_articles?fields=" + Q("sections.item:headings.title"), None),

        ("H3", "fields=year(date_published)", "editor", "GET", "/items/qa_categories?fields=" + Q("year(date_published)"), None),

        ("H3", "sort=year(date_created)", "editor", "GET", "/items/qa_categories?sort=" + Q("year(date_created)"), None),

        ("H3", "deep={\"x\":[-8587]}", "editor", "GET", "/items/qa_articles?deep=" + Q('{"x":[-8587]}'), None),

        ("H3", "limit=-1 + page=2", "editor", "GET", "/items/qa_articles?limit=-1&page=2", None),

        # H4: id do client gui trong body POST

        ("H4", "POST articles toi thieu hop le (doi chung)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-ok", "score": 1}),

        ("H4", "POST articles id trong int4 (id=500000)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-id500000", "score": 1, "id": 500000}),

        ("H4", "POST articles id ngoai int4 (id=9999999999)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-idbig", "score": 1, "id": 9999999999}),

        ("H4", "POST categories id ngoai int4 (id=9999999999)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-idbig", "id": 9999999999}),

        ("H4", "POST categories mang co id ngoai int4", "editor", "POST", "/items/qa_categories", [{"name": "k05-probe-arr-idbig", "id": 9999999999}]),

        ("H4", "POST categories id am trong int4 (id=-29490)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-idneg", "id": -29490}),

        ("H4", "POST categories id am ngoai int4 (id=-5345389491970)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-idnegbig", "id": -5345389491970}),

        ("H4", "POST categories khoa la \"\" (rong)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-emptykey", "": -329}),

        # H4b: gia tri sai kieu / ky tu NUL trong body

        ("H4b", "POST published_at=false (boolean cho cot timestamp)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-pubfalse", "score": 1, "published_at": False}),

        ("H4b", "POST published_at=true", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-pubtrue", "score": 1, "published_at": True}),

        ("H4b", "POST published_at=\"abc\" (chuoi khong phai ngay)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-pubabc", "score": 1, "published_at": "abc"}),

        ("H4b", "POST published_at=123 (so)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-pub123", "score": 1, "published_at": 123}),

        ("H4b", "POST published_at=\"2026-11-24T00:00:00Z\" (doi chung hop le)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-pubok", "score": 1, "published_at": "2026-11-24T00:00:00Z"}),

        ("H4b", "PATCH published_at=false tren bai 1", "editor", "PATCH", "/items/qa_articles/1", {"published_at": False}),

        ("H4b", "POST name chua ky tu NUL (chr(0)) cho categories", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-nul" + chr(0) + "x"}),

        ("H4b", "POST title chua ky tu NUL (chr(0)) cho articles", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-nul" + chr(0) + "x", "score": 1}),

        ("H4b", "POST name chua U+0019 (khong NUL) - doi chung", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-ctl" + chr(25) + "x"}),

        # H7: phuong thuc khong ho tro
        ("H7", "TRACE /items/qa_articles (phuong thuc khong ho tro, duong dan ton tai)", "editor", "TRACE", "/items/qa_articles", None),
        ("H7", "TRACE /server/ping", "editor", "TRACE", "/server/ping", None),
        ("H7", "PUT /items/qa_articles/1 (khong ho tro)", "editor", "PUT", "/items/qa_articles/1", {"title": "k05-probe"}),
        # H8: nguyen nhan chi thay trong thong ke tuong tac 5xx (Schemathesis chi giu mot failure moi operation)
        ("H8", "RC04 search chua %00 (NUL trong query)", "editor", "GET", "/items/qa_categories?search=a%00b", None),
        ("H8", "RC12 POST mang chua null", "editor", "POST", "/items/qa_categories", [None]),
        ("H8", "RC13 POST id=true", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-idtrue", "id": True}),
        ("H8", "RC13 POST id=\"\" (chuoi rong)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-idempty", "id": ""}),
        ("H8", "RC13 POST id=1e21 (bieu dien mu)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-id1e21", "id": 1e21}),
        ("H8", "RC13 POST category.id=\"abc\" (khoa ngoai long)", "editor", "POST", "/items/qa_articles", {"title": "k05-probe-catabc", "score": 1, "category": {"id": "abc"}}),
        ("H8", "RC13 doi chung: id=100000000000000000000 (1e20, van co dang so nguyen)", "editor", "POST", "/items/qa_categories", {"name": "k05-probe-id1e20", "id": 100000000000000000000}),
        ("H8", "RC14 export=csv voi fields=sections.item:headings.title", "editor", "GET", "/items/qa_articles?fields=" + Q("sections.item:headings.title") + "&export=csv", None),
        ("H8", "RC14 doi chung: export=csv khong co fields", "editor", "GET", "/items/qa_articles?export=csv", None),
        ("H8", "RC15 limit=897434&page=17592186044417", "editor", "GET", "/items/qa_articles?limit=897434&page=17592186044417", None),
        ("H8", "RC15 doi chung: limit=100&page=1000000", "editor", "GET", "/items/qa_articles?limit=100&page=1000000", None),
        ("H8", "RC16 groupBy=a)b(", "editor", "GET", "/items/qa_articles?groupBy=" + Q("a)b(", safe=""), None),
        ("H8", "RC16 doi chung: groupBy=year(published_at)", "editor", "GET", "/items/qa_articles?groupBy=" + Q("year(published_at)", safe=""), None),
        # H5: Reader PATCH rong

        ("H5", "reader PATCH body rong {}", "reader", "PATCH", "/items/qa_articles/1", {}),

        ("H5", "reader PATCH co du lieu", "reader", "PATCH", "/items/qa_articles/1", {"title": "k05-probe"}),

        ("H5", "reader PATCH khong body", "reader", "PATCH", "/items/qa_articles/1", None),

        ("H5", "editor PATCH body rong {}", "editor", "PATCH", "/items/qa_articles/1", {}),

        # H6: utils/sort

        ("H6", "editor POST utils/sort/qa_articles body rong", "editor", "POST", "/utils/sort/qa_articles", {}),

        ("H6", "editor POST utils/sort/qa_articles {item,to} khong ton tai", "editor", "POST", "/utils/sort/qa_articles", {"item": 999998, "to": 999999}),

    ]

    results = []

    stamp = time.time()

    for pid, hyp, actor, method, path, body in probes:

        status, text = call(method, path, tokens[actor], body=body)

        results.append({"group": pid, "hypothesis": hyp, "actor": actor, "method": method, "path": path[:140],

                        "status": status, **brief(text)})

        print(pid, actor, method, path[:70], "->", status, brief(text))

    # Bang chung nguyen nhan: admin duoc tra thong diep goc cua loi 500 (editor/reader chi thay thong diep chung)
    admin_evidence = []
    evidence_tests = [
        ("RC01", "GET", "/items/qa_articles/9999999999", None),
        ("RC01", "DELETE", "/items/qa_articles/9999999999", None),
        ("RC02", "GET", "/items/qa_articles?aggregate=" + Q('{"foo":1}'), None),
        ("RC02", "GET", "/items/qa_articles?aggregate=abc", None),
        ("RC03", "POST", "/items/qa_articles", {"title": "k05-probe-ev1", "score": 1, "published_at": False}),
        ("RC03", "POST", "/items/qa_articles", {"title": "k05-probe-ev2", "score": 1, "published_at": "abc"}),
        ("RC04", "POST", "/items/qa_categories", {"name": "k05-probe-ev" + chr(0) + "x"}),
        ("RC04", "GET", "/items/qa_categories?search=a%00b", None),
        ("RC12", "POST", "/items/qa_categories", [None]),
        ("RC13", "POST", "/items/qa_categories", {"name": "k05-probe-ev-id", "id": True}),
        ("RC13", "POST", "/items/qa_categories", {"name": "k05-probe-ev-1e21", "id": 1e21}),
        ("RC13", "POST", "/items/qa_articles", {"title": "k05-probe-ev-cat", "score": 1, "category": {"id": "abc"}}),
        ("RC14", "GET", "/items/qa_articles?fields=" + Q("sections.item:headings.title") + "&export=csv", None),
        ("RC15", "GET", "/items/qa_articles?limit=897434&page=17592186044417", None),
        ("RC16", "GET", "/items/qa_articles?groupBy=" + Q("a)b(", safe=""), None),
    ]
    for rc, method, path, body in evidence_tests:
        status, text = call(method, path, tokens["admin"], body=body)
        try:
            msg = json.loads(text)["errors"][0]["message"]
        except Exception:
            msg = text[:200]
        admin_evidence.append({"root_cause": rc, "method": method, "path": path[:100], "status": status, "server_message": msg[:400]})
        print("EVID", rc, method, path[:60], status, msg[-110:].replace("\n", " "))
    after = state(tokens["admin"])

    cleaned = purge_probe_rows(tokens["admin"])

    final = state(tokens["admin"])

    OUT.parent.mkdir(parents=True, exist_ok=True)

    OUT.write_text(json.dumps({"base": BASE, "started_unix": stamp, "state_before": before, "state_after_probes": after,

                               "cleaned_rows": cleaned, "admin_evidence": admin_evidence, "state_final": final, "state_restored": final == before,

                               "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")

    print("state_before", before, "final", final, "restored", final == before, "cleaned", cleaned)

    return 0 if final == before else 1





if __name__ == "__main__":

    raise SystemExit(main())

