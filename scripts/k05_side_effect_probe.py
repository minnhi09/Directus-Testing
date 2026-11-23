#!/usr/bin/env python3
"""WP4: thăm dò chủ động các thao tác có tác dụng phụ trên lab local.

Chỉ chạy với lab loopback http://127.0.0.1:8055 (dự án r06-k05). Chỉ dùng thư viện chuẩn của Python 3.
Đọc thông tin đăng nhập từ config/lab.env TRONG BỘ NHỚ; không in và không ghi mật khẩu/token/refresh token.

Các phép thử (đều tự dọn sau khi xong):
  A. auth/logout và auth/refresh: refresh token giả và thật ảnh hưởng gì tới access token đang dùng?
  B. đăng nhập sai nhiều lần: Directus có khóa/tạm ngưng tài khoản không? (dùng người dùng tạm, sau đó xóa)
  C. utils/cache/clear bằng Editor.
  D. utils/import bằng Editor vào qa_categories: tạo gì, ở đâu? (dọn bằng admin)
  E. xác nhận trạng thái cuối: fixture, số người dùng/file, tài khoản actor còn active.

Kết quả JSON ghi ra --out (mặc định in ra stdout).
"""
from __future__ import annotations

import argparse
import collections
import json
import secrets
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "http://127.0.0.1:8055"


def load_env() -> dict[str, str]:
    env = {}
    for line in (ROOT / "config" / "lab.env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def call(method: str, path: str, token: str | None = None, body=None, raw: bytes | None = None,
         content_type: str | None = None) -> tuple[int, object]:
    headers = {}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if raw is not None:
        data, headers["Content-Type"] = raw, content_type or "application/octet-stream"
    elif body is not None:
        data, headers["Content-Type"] = json.dumps(body).encode(), "application/json"
    req = urllib.request.Request(API + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            payload = r.read()
            status = r.status
    except urllib.error.HTTPError as e:
        payload, status = e.read(), e.code
    try:
        return status, json.loads(payload) if payload else None
    except ValueError:
        return status, None


def login(email: str, password: str) -> tuple[int, str | None, str | None]:
    status, body = call("POST", "/auth/login", body={"email": email, "password": password, "mode": "json"})
    d = (body or {}).get("data") if isinstance(body, dict) else None
    return status, (d or {}).get("access_token"), (d or {}).get("refresh_token")


def count(path_token_pair: tuple[str, str]) -> int | None:
    path, token = path_token_pair
    status, body = call("GET", path, token)
    if status == 200 and isinstance(body, dict):
        return len(body.get("data") or [])
    return None


def multipart(filename: str, content: bytes) -> tuple[bytes, str]:
    boundary = "----k05" + uuid.uuid4().hex
    head = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: application/json\r\n\r\n").encode()
    return head + content + f"\r\n--{boundary}--\r\n".encode(), f"multipart/form-data; boundary={boundary}"


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path)
    ap.add_argument("--wrong-logins", type=int, default=30, help="số lần đăng nhập sai (phép thử B)")
    args = ap.parse_args()

    env = load_env()
    result: dict = {"schema": "k05-side-effect-probe/1", "api": API, "probes": {}}

    s, admin, _ = login(env["ADMIN_EMAIL"], env["ADMIN_PASSWORD"])
    if not admin:
        print("Không đăng nhập được admin; dừng.", file=sys.stderr)
        return 2
    s, editor, editor_rt = login(env["EDITOR_EMAIL"], env["EDITOR_PASSWORD"])
    s2, reader, _ = login(env["READER_EMAIL"], env["READER_PASSWORD"])
    if not (editor and reader):
        print("Không đăng nhập được editor/reader; dừng.", file=sys.stderr)
        return 2

    def base_state():
        return {
            "categories": count(("/items/qa_categories?limit=-1&fields=id", admin)),
            "articles": count(("/items/qa_articles?limit=-1&fields=id", admin)),
            "users": count(("/users?limit=-1&fields=id", admin)),
            "files": count(("/files?limit=-1&fields=id", admin)),
        }

    before = base_state()
    result["state_before"] = before

    # A. logout / refresh
    a = {}
    a["logout_fake_refresh"] = call("POST", "/auth/logout", body={"refresh_token": "k05-not-a-real-refresh-token", "mode": "json"})[0]
    a["me_after_fake_logout"] = call("GET", "/users/me?fields=id", editor)[0]
    a["refresh_fake"] = call("POST", "/auth/refresh", body={"refresh_token": "k05-not-a-real-refresh-token", "mode": "json"})[0]
    a["logout_real_refresh"] = call("POST", "/auth/logout", body={"refresh_token": editor_rt, "mode": "json"})[0]
    a["me_after_real_logout_access_token_still_works"] = call("GET", "/users/me?fields=id", editor)[0]
    a["refresh_with_logged_out_token"] = call("POST", "/auth/refresh", body={"refresh_token": editor_rt, "mode": "json"})[0]
    a["editor_can_login_again"] = login(env["EDITOR_EMAIL"], env["EDITOR_PASSWORD"])[0]
    result["probes"]["A_logout_refresh"] = a

    # B. dang nhap sai nhieu lan voi nguoi dung tam
    tmp_email = f"k05-lockout-probe-{secrets.token_hex(4)}@example.com"
    tmp_pw = secrets.token_urlsafe(18)
    st, body = call("POST", "/users", admin, {"email": tmp_email, "password": tmp_pw, "status": "active"})
    tmp_id = ((body or {}).get("data") or {}).get("id") if isinstance(body, dict) else None
    b = {"create_temp_user": st}
    if tmp_id:
        seq = [call("POST", "/auth/login", body={"email": tmp_email, "password": "k05-wrong-" + str(i)})[0]
               for i in range(1, args.wrong_logins + 1)]
        runs = []
        for i, code in enumerate(seq, 1):
            if not runs or runs[-1][0] != code:
                runs.append([code, i, i])
            else:
                runs[-1][2] = i
        b["wrong_login_status_runs"] = [{"status": c, "from_attempt": f, "to_attempt": t} for c, f, t in runs]
        _, ubody = call("GET", f"/users/{tmp_id}?fields=status", admin)
        b["temp_user_status_after"] = ((ubody or {}).get("data") or {}).get("status")
        b["correct_login_after_wrong_attempts"] = login(tmp_email, tmp_pw)[0]
        b["delete_temp_user"] = call("DELETE", f"/users/{tmp_id}", admin)[0]
    result["probes"]["B_login_lockout"] = b

    # C. cache/clear
    result["probes"]["C_cache_clear"] = {
        "editor": call("POST", "/utils/cache/clear", editor)[0],
        "reader": call("POST", "/utils/cache/clear", reader)[0],
        "anonymous": call("POST", "/utils/cache/clear")[0],
    }

    # D. import vao qa_categories bang Editor
    d = {}
    raw, ctype = multipart("k05-import-probe.json", json.dumps([{"name": "k05-import-probe"}]).encode())
    d["import_status"] = call("POST", "/utils/import/qa_categories", editor, raw=raw, content_type=ctype)[0]
    after_import = base_state()
    d["delta"] = {k: (after_import[k] - before[k]) if None not in (after_import[k], before[k]) else None for k in before}
    status, body = call("GET", "/items/qa_categories?filter[name][_eq]=k05-import-probe&fields=id&limit=-1", admin)
    created = [r["id"] for r in ((body or {}).get("data") or [])] if status == 200 and isinstance(body, dict) else []
    d["rows_created_in_qa_categories"] = len(created)
    d["cleanup_deleted"] = [call("DELETE", f"/items/qa_categories/{i}", admin)[0] for i in created]
    result["probes"]["D_import_editor"] = d

    # E. trang thai cuoi
    after = base_state()
    result["state_after"] = after
    result["state_unchanged"] = after == before
    result["actor_logins_ok"] = {
        "admin": login(env["ADMIN_EMAIL"], env["ADMIN_PASSWORD"])[0],
        "editor": login(env["EDITOR_EMAIL"], env["EDITOR_PASSWORD"])[0],
        "reader": login(env["READER_EMAIL"], env["READER_PASSWORD"])[0],
    }

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Đã ghi: {args.out}")
    print(text)
    return 0 if result["state_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
