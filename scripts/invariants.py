#!/usr/bin/env python3
"""Deterministic Directus scenarios and business invariants for the lab.

The runner deliberately uses only Python's standard library so a host does not
need a Python package installation.  It records response bodies locally for
triage, but never records login responses (which contain access tokens).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def env_required(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise RuntimeError(f"thiếu biến môi trường {name}")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def json_summary(body: Any) -> dict[str, Any]:
    if isinstance(body, dict) and isinstance(body.get("errors"), list):
        return {
            "errors": [
                {
                    "code": error.get("extensions", {}).get("code", error.get("code")),
                    "message": error.get("message"),
                }
                for error in body["errors"]
                if isinstance(error, dict)
            ]
        }
    if isinstance(body, dict) and "data" in body:
        data = body["data"]
        return {"data_type": type(data).__name__, "data_length": len(data) if isinstance(data, list) else None}
    if isinstance(body, dict):
        return {"keys": sorted(body.keys())}
    return {"body_type": type(body).__name__}


@dataclass
class ApiResponse:
    status: int
    body: Any
    raw: bytes
    content_type: str = ""
    error: str | None = None


class Api:
    def __init__(self, base_url: str, run_dir: Path, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.run_dir = run_dir
        self.timeout = timeout
        self.counter = 0
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def request(
        self,
        method: str,
        path: str,
        token: str = "",
        body: Any | None = None,
        *,
        record: bool = True,
    ) -> ApiResponse:
        payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if payload is not None:
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=payload, headers=headers, method=method.upper()
        )
        response: ApiResponse
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as raw_response:
                raw = raw_response.read()
                response = ApiResponse(
                    raw_response.status,
                    self._decode(raw),
                    raw,
                    raw_response.headers.get("Content-Type", ""),
                )
        except urllib.error.HTTPError as error:
            raw = error.read()
            response = ApiResponse(
                error.code,
                self._decode(raw),
                raw,
                error.headers.get("Content-Type", "") if error.headers else "",
            )
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            response = ApiResponse(0, {}, b"", error=str(error))

        if record:
            self.counter += 1
            target = self.run_dir / f"http-{self.counter}.json"
            target.write_bytes(response.raw if response.raw else b"{}")
        status_text = str(response.status) if response.status else "network-error"
        print(f"API {method.upper()} {path} -> {status_text}")
        return response

    @staticmethod
    def _decode(raw: bytes) -> Any:
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {"raw_body": "<non-json response>"}


@dataclass
class Case:
    case_id: str
    name: str
    status: str = "passed"
    expected: str = ""
    actual: str = ""
    details: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)

    def step(self, method: str, path: str, response: ApiResponse, expected: str) -> None:
        self.steps.append(
            {
                "method": method.upper(),
                "path": path,
                "status": response.status,
                "expected": expected,
                "actual": json_summary(response.body),
            }
        )

    def fail(self, expected: str, actual: str, details: str) -> None:
        self.status = "failed"
        self.expected = expected
        self.actual = actual
        self.details = details

    def block(self, expected: str, actual: str, details: str) -> None:
        self.status = "blocked"
        self.expected = expected
        self.actual = actual
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.case_id,
            "name": self.name,
            "status": self.status,
            "expected": self.expected,
            "actual": self.actual,
            "details": self.details,
            "steps": self.steps,
        }


class Lab:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.runtime_root = Path(env_required("LAB_RUNTIME_ROOT"))
        try:
            timeout = float(os.environ.get("LAB_REQUEST_TIMEOUT", "10"))
        except ValueError as error:
            raise RuntimeError("LAB_REQUEST_TIMEOUT không phải số") from error
        if timeout <= 0:
            raise RuntimeError("LAB_REQUEST_TIMEOUT phải lớn hơn 0")
        self.api = Api(env_required("LAB_API_URL"), run_dir, timeout)
        self.admin_email = env_required("LAB_ADMIN_EMAIL")
        self.admin_password = env_required("LAB_ADMIN_PASSWORD")
        self.editor_email = env_required("LAB_EDITOR_EMAIL")
        self.editor_password = env_required("LAB_EDITOR_PASSWORD")
        self.reader_email = env_required("LAB_READER_EMAIL")
        self.reader_password = env_required("LAB_READER_PASSWORD")
        self.admin_token = ""
        self.editor_token = ""
        self.reader_token = ""
        self.fixture_map: dict[str, Any] = {}
        self.reader_schema: dict[str, Any] = {}

    def login(self, email: str, password: str) -> str:
        response = self.api.request(
            "POST",
            "/auth/login",
            body={"email": email, "password": password},
            record=False,
        )
        token = response.body.get("data", {}).get("access_token", "") if isinstance(response.body, dict) else ""
        if response.status < 200 or response.status >= 300 or not token:
            raise RuntimeError(f"đăng nhập thất bại HTTP {response.status}")
        return str(token)

    def authenticate(self) -> None:
        self.admin_token = self.login(self.admin_email, self.admin_password)
        self.editor_token = self.login(self.editor_email, self.editor_password)
        self.reader_token = self.login(self.reader_email, self.reader_password)

    def load_fixture(self) -> None:
        path = self.runtime_root / "fixture-ids.json"
        self.fixture_map = json.loads(path.read_text(encoding="utf-8"))
        if self.fixture_map.get("schema") != 1:
            raise RuntimeError("fixture map không đúng schema 1")
        for collection in ("qa_categories", "qa_articles"):
            rows = self.fixture_map.get("fixtures", {}).get(collection)
            if not isinstance(rows, dict) or not rows:
                raise RuntimeError(f"fixture map thiếu {collection}")
            if not all(isinstance(value, int) and value > 0 for value in rows.values()):
                raise RuntimeError(f"fixture map {collection} có ID không hợp lệ")
        schema_root = self.runtime_root / "schemas" / self.fixture_map["fixture_version"]
        reader_path = schema_root / "reader.json"
        if reader_path.exists():
            self.reader_schema = json.loads(reader_path.read_text(encoding="utf-8"))

    def fixture_article_id(self, key: str) -> int:
        return int(self.fixture_map["fixtures"]["qa_articles"][key])

    def fixture_category_id(self, key: str) -> int:
        return int(self.fixture_map["fixtures"]["qa_categories"][key])

    def has_operation(self, method: str, path: str) -> bool:
        value = self.reader_schema.get("paths", {}).get(path, {})
        return method.lower() in value

    @staticmethod
    def path_params(params: dict[str, Any]) -> str:
        return "?" + urllib.parse.urlencode(params, doseq=True)

    def all_articles(self, token: str) -> ApiResponse:
        return self.api.request(
            "GET",
            "/items/qa_articles" + self.path_params(
                {"limit": "-1", "fields": "id,title,status,score,published_at,metadata,internal_notes,category"}
            ),
            token,
        )

    def case_auth_invalid_token(self) -> Case:
        case = Case("auth-invalid-token", "Đăng nhập và token không hợp lệ")
        response = self.api.request("GET", "/users/me", "not-a-valid-lab-token")
        case.step("GET", "/users/me", response, "request bị từ chối; status thực tế được giữ nguyên")
        if response.status == 0:
            case.fail("API trả response HTTP không thành công", "network error", response.error or "network error")
        elif 200 <= response.status < 300:
            case.fail("token không hợp lệ bị từ chối", str(response.status), "API chấp nhận token giả")
        else:
            case.expected = "token không hợp lệ bị từ chối"
            case.actual = str(response.status)
            case.details = "Không hard-code 401; giữ status thực tế của baseline."
        return case

    def case_anonymous_denied(self) -> Case:
        case = Case("anonymous-denied", "Anonymous không truy cập hai collection lab")
        checks = (
            "/items/qa_categories?limit=1&fields=id,name",
            "/items/qa_articles?limit=1&fields=id,title,status",
        )
        for path in checks:
            response = self.api.request("GET", path)
            case.step("GET", path, response, "request anonymous bị từ chối")
            if response.status == 0:
                case.fail("anonymous request có HTTP response", "network error", response.error or "network error")
                return case
            if 200 <= response.status < 300:
                case.fail("anonymous không đọc được collection", str(response.status), f"API cho phép {path}")
                return case
        case.expected = "anonymous bị từ chối trên qa_categories và qa_articles"
        case.actual = "cả hai request đều non-2xx"
        case.details = "Không gán cứng status 401/403; giữ status thực tế của baseline."
        return case

    def case_editor_crud(self) -> Case:
        case = Case("editor-crud", "Editor CRUD article và invariant read-back/delete")
        item_id: int | None = None
        title = f"Replay editor CRUD {os.environ.get('LAB_RUN_ID', 'local')}"
        body = {
            "title": title,
            "status": "draft",
            "score": 1,
            "published_at": None,
            "metadata": {"case": "editor-crud"},
            "internal_notes": "replay-only",
            "category": self.fixture_category_id("category_alpha"),
        }
        try:
            response = self.api.request("POST", "/items/qa_articles", self.editor_token, body)
            case.step("POST", "/items/qa_articles", response, "2xx và response có ID")
            if response.status < 200 or response.status >= 300:
                case.fail("tạo article thành công", str(response.status), "Editor không tạo được article")
                return case
            item_id = response.body.get("data", {}).get("id") if isinstance(response.body, dict) else None
            if not isinstance(item_id, int) or item_id <= 0:
                case.fail("response có ID số dương", repr(item_id), "response create không có ID hợp lệ")
                return case

            path = f"/items/qa_articles/{item_id}?fields=id,title,status,score,category"
            response = self.api.request("GET", path, self.editor_token)
            case.step("GET", path, response, "2xx và title giữ nguyên")
            if response.status < 200 or response.status >= 300 or response.body.get("data", {}).get("title") != title:
                case.fail("đọc lại được title vừa tạo", str(response.status), "create/read-back invariant thất bại")
                return case

            path = f"/items/qa_articles/{item_id}"
            response = self.api.request("PATCH", path, self.editor_token, {"score": 5})
            case.step("PATCH", path, response, "2xx")
            if response.status < 200 or response.status >= 300:
                case.fail("PATCH score thành công", str(response.status), "Editor không PATCH được article")
                return case

            response = self.api.request("GET", f"{path}?fields=id,title,score", self.editor_token)
            case.step("GET", f"{path}?fields=id,title,score", response, "2xx, score=5 và title không đổi")
            data = response.body.get("data", {}) if isinstance(response.body, dict) else {}
            if response.status < 200 or response.status >= 300 or data.get("score") != 5 or data.get("title") != title:
                case.fail("PATCH giữ field không cập nhật", str(response.status), "PATCH invariant thất bại")
                return case

            response = self.api.request("DELETE", path, self.editor_token)
            case.step("DELETE", path, response, "2xx")
            if response.status < 200 or response.status >= 300:
                case.fail("DELETE thành công", str(response.status), "Editor không xóa được article")
                return case
            item_id = None
            response = self.api.request("GET", f"{path}?fields=id", self.editor_token)
            case.step("GET", f"{path}?fields=id", response, "resource không còn data")
            if 200 <= response.status < 300 and isinstance(response.body, dict) and response.body.get("data"):
                case.fail("resource sau DELETE không còn truy cập được", str(response.status), "resource vẫn trả về")
                return case
            case.expected = "create/read/PATCH/delete invariants đạt"
            case.actual = "các bước CRUD đạt; GET sau DELETE không trả data"
            case.details = "ID được lấy từ response create, không hard-code."
            return case
        finally:
            if item_id is not None:
                cleanup = self.api.request("DELETE", f"/items/qa_articles/{item_id}", self.editor_token, record=False)
                if cleanup.status and not (200 <= cleanup.status < 300):
                    print(f"WARN cleanup editor-crud thất bại HTTP {cleanup.status}")

    def case_positive_operations(self) -> Case:
        case = Case("positive-operations", "Positive acceptance cho đủ 10 operation campaign")
        category_id: int | None = None
        article_id: int | None = None
        run_id = os.environ.get("LAB_RUN_ID", "local")
        category_name = f"Positive category {run_id}"
        article_title = f"Positive article {run_id}"

        def require_2xx(response: ApiResponse, expected: str) -> bool:
            if response.status < 200 or response.status >= 300:
                case.fail(expected, str(response.status), "Editor positive precondition không đạt")
                return False
            return True

        try:
            response = self.api.request("POST", "/items/qa_categories", self.editor_token, {"name": category_name})
            case.step("POST", "/items/qa_categories", response, "2xx và có ID")
            if not require_2xx(response, "POST category thành công"):
                return case
            category_id = response.body.get("data", {}).get("id") if isinstance(response.body, dict) else None
            if not isinstance(category_id, int) or category_id <= 0:
                case.fail("POST category trả ID số dương", repr(category_id), "response không có ID hợp lệ")
                return case

            list_path = "/items/qa_categories" + self.path_params(
                {"filter[id][_eq]": category_id, "fields": "id,name"}
            )
            response = self.api.request("GET", list_path, self.editor_token)
            case.step("GET", list_path, response, "2xx và chứa category vừa tạo")
            if not require_2xx(response, "GET category list thành công"):
                return case
            rows = response.body.get("data", []) if isinstance(response.body, dict) else []
            if not any(row.get("id") == category_id and row.get("name") == category_name for row in rows):
                case.fail("GET category list chứa fixture tạm", repr(rows), "category vừa tạo không đọc lại được")
                return case

            category_path = f"/items/qa_categories/{category_id}"
            response = self.api.request("GET", f"{category_path}?fields=id,name", self.editor_token)
            case.step("GET", category_path, response, "2xx và name đúng")
            if not require_2xx(response, "GET category detail thành công"):
                return case
            if response.body.get("data", {}).get("name") != category_name:
                case.fail("GET category detail giữ name", repr(response.body), "detail response sai dữ liệu")
                return case

            updated_category_name = f"{category_name} updated"
            response = self.api.request("PATCH", category_path, self.editor_token, {"name": updated_category_name})
            case.step("PATCH", category_path, response, "2xx")
            if not require_2xx(response, "PATCH category thành công"):
                return case
            response = self.api.request("GET", f"{category_path}?fields=id,name", self.editor_token)
            case.step("GET", f"{category_path}?fields=id,name", response, "2xx và name đã cập nhật")
            if not require_2xx(response, "đọc lại category sau PATCH"):
                return case
            if response.body.get("data", {}).get("name") != updated_category_name:
                case.fail("PATCH category được đọc lại", repr(response.body), "PATCH không giữ giá trị mới")
                return case

            article_body = {
                "title": article_title,
                "status": "draft",
                "score": 2,
                "published_at": None,
                "metadata": {"case": "positive-operations", "run_id": run_id},
                "internal_notes": "positive-operation probe",
                "category": category_id,
            }
            response = self.api.request("POST", "/items/qa_articles", self.editor_token, article_body)
            case.step("POST", "/items/qa_articles", response, "2xx và có ID")
            if not require_2xx(response, "POST article thành công"):
                return case
            article_id = response.body.get("data", {}).get("id") if isinstance(response.body, dict) else None
            if not isinstance(article_id, int) or article_id <= 0:
                case.fail("POST article trả ID số dương", repr(article_id), "response không có ID hợp lệ")
                return case

            article_list_path = "/items/qa_articles" + self.path_params(
                {"filter[id][_eq]": article_id, "fields": "id,title,status,score,category"}
            )
            response = self.api.request("GET", article_list_path, self.editor_token)
            case.step("GET", article_list_path, response, "2xx và chứa article vừa tạo")
            if not require_2xx(response, "GET article list thành công"):
                return case
            rows = response.body.get("data", []) if isinstance(response.body, dict) else []
            if not any(row.get("id") == article_id and row.get("title") == article_title for row in rows):
                case.fail("GET article list chứa fixture tạm", repr(rows), "article vừa tạo không đọc lại được")
                return case

            article_path = f"/items/qa_articles/{article_id}"
            response = self.api.request("GET", f"{article_path}?fields=id,title,status,score,category", self.editor_token)
            case.step("GET", article_path, response, "2xx và title/category đúng")
            if not require_2xx(response, "GET article detail thành công"):
                return case
            data = response.body.get("data", {})
            if data.get("title") != article_title or data.get("category") != category_id:
                case.fail("GET article detail giữ title/category", repr(data), "detail response sai dữ liệu")
                return case

            response = self.api.request("PATCH", article_path, self.editor_token, {"score": 4})
            case.step("PATCH", article_path, response, "2xx")
            if not require_2xx(response, "PATCH article thành công"):
                return case
            response = self.api.request("GET", f"{article_path}?fields=id,title,score,category", self.editor_token)
            case.step("GET", f"{article_path}?fields=id,title,score,category", response, "2xx và PATCH giữ title/category")
            if not require_2xx(response, "đọc lại article sau PATCH"):
                return case
            data = response.body.get("data", {})
            if data.get("score") != 4 or data.get("title") != article_title or data.get("category") != category_id:
                case.fail("PATCH article giữ field không cập nhật", repr(data), "PATCH invariant thất bại")
                return case

            response = self.api.request("DELETE", article_path, self.editor_token)
            case.step("DELETE", article_path, response, "2xx")
            if not require_2xx(response, "DELETE article thành công"):
                return case
            article_id = None
            response = self.api.request("GET", f"{article_path}?fields=id", self.editor_token)
            case.step("GET", f"{article_path}?fields=id", response, "resource article không còn data")
            if response.status == 0 or (200 <= response.status < 300 and response.body.get("data")):
                case.fail("article sau DELETE không còn truy cập được", str(response.status), "article vẫn trả về")
                return case

            response = self.api.request("DELETE", category_path, self.editor_token)
            case.step("DELETE", category_path, response, "2xx")
            if not require_2xx(response, "DELETE category thành công"):
                return case
            category_id = None
            response = self.api.request("GET", f"{category_path}?fields=id", self.editor_token)
            case.step("GET", f"{category_path}?fields=id", response, "resource category không còn data")
            if response.status == 0 or (200 <= response.status < 300 and response.body.get("data")):
                case.fail("category sau DELETE không còn truy cập được", str(response.status), "category vẫn trả về")
                return case

            case.expected = "đủ 10 operation có ca positive hợp lệ và DELETE không còn tài nguyên"
            case.actual = "qa_categories=5 operation, qa_articles=5 operation; create/PATCH/read-back/delete đạt"
            case.details = "ID được lấy từ response create; dữ liệu probe được xóa sau khi kiểm tra."
            return case
        finally:
            if article_id is not None:
                cleanup = self.api.request("DELETE", f"/items/qa_articles/{article_id}", self.editor_token, record=False)
                if cleanup.status and not (200 <= cleanup.status < 300):
                    print(f"WARN cleanup positive article thất bại HTTP {cleanup.status}")
            if category_id is not None:
                cleanup = self.api.request("DELETE", f"/items/qa_categories/{category_id}", self.editor_token, record=False)
                if cleanup.status and not (200 <= cleanup.status < 300):
                    print(f"WARN cleanup positive category thất bại HTTP {cleanup.status}")

    def case_query_fixture(self) -> Case:
        case = Case("query-fixture", "Filter, sort, pagination và projection trên fixture")
        response = self.all_articles(self.editor_token)
        case.step("GET", "/items/qa_articles?limit=-1&fields=...", response, "2xx và đủ fixture")
        if response.status < 200 or response.status >= 300:
            case.fail("đọc fixture articles", str(response.status), "Không có precondition cho query")
            return case
        rows = response.body.get("data", []) if isinstance(response.body, dict) else []
        fixture_ids = set(self.fixture_map["fixtures"]["qa_articles"].values())
        by_id = {row.get("id"): row for row in rows if isinstance(row, dict)}
        if not fixture_ids.issubset(by_id):
            case.fail("fixture map IDs tồn tại", repr(sorted(by_id)), "fixture map không khớp database hiện tại")
            return case
        expected = sorted(
            [by_id[item_id] for item_id in fixture_ids if by_id[item_id].get("status") == "published"],
            key=lambda row: (row.get("title", ""), row.get("id", 0)),
        )
        query = "/items/qa_articles" + self.path_params(
            {
                "filter[status][_eq]": "published",
                "sort": "title,id",
                "limit": "-1",
                "fields": "id,title,status",
            }
        )
        response = self.api.request("GET", query, self.editor_token)
        case.step("GET", query, response, "2xx và đúng tập published")
        actual = response.body.get("data", []) if isinstance(response.body, dict) else []
        if response.status < 200 or response.status >= 300:
            case.fail("published filter trả 2xx", str(response.status), "query thất bại")
            return case
        expected_ids = [row["id"] for row in expected]
        actual_ids = [row.get("id") for row in actual]
        if actual_ids != expected_ids or any(set(row) - {"id", "title", "status"} for row in actual):
            case.fail("filter/sort/projection khớp fixture", repr(actual_ids), "query result khác oracle fixture")
            return case

        all_fixture = sorted([by_id[item_id] for item_id in fixture_ids], key=lambda row: (row.get("title", ""), row.get("id", 0)))
        for offset, expected_page in ((0, all_fixture[:3]), (3, all_fixture[3:6])):
            page = "/items/qa_articles" + self.path_params(
                {"sort": "title,id", "limit": "3", "offset": str(offset), "fields": "id,title"}
            )
            response = self.api.request("GET", page, self.editor_token)
            case.step("GET", page, response, "2xx và page khớp sort title,id")
            actual_page = response.body.get("data", []) if isinstance(response.body, dict) else []
            if response.status < 200 or response.status >= 300 or [row.get("id") for row in actual_page] != [row["id"] for row in expected_page]:
                case.fail("pagination khớp sorted fixture", repr(actual_page), f"offset={offset} không khớp")
                return case
        case.expected = "filter status, sort title/id, offset pages và fields projection đúng"
        case.actual = f"published={len(actual_ids)}, pages=2"
        case.details = "Expected được tính từ fixture IDs và dữ liệu seed, không từ response của query đang kiểm tra."
        return case

    def case_relation_nullification(self) -> Case:
        case = Case("relation-nullification", "Quan hệ article.category đặt NULL khi xóa category")
        category_id: int | None = None
        article_id: int | None = None
        run_id = os.environ.get("LAB_RUN_ID", "local")
        try:
            category = self.api.request("POST", "/items/qa_categories", self.editor_token, {"name": f"Replay relation {run_id}"})
            case.step("POST", "/items/qa_categories", category, "2xx và có ID")
            if category.status < 200 or category.status >= 300:
                case.fail("tạo category probe", str(category.status), "không tạo được relation precondition")
                return case
            category_id = category.body.get("data", {}).get("id")
            article = self.api.request(
                "POST",
                "/items/qa_articles",
                self.editor_token,
                {
                    "title": f"Replay relation article {run_id}",
                    "status": "draft",
                    "score": 1,
                    "published_at": None,
                    "metadata": {"case": "relation-nullification"},
                    "internal_notes": "replay-only",
                    "category": category_id,
                },
            )
            case.step("POST", "/items/qa_articles", article, "2xx và có ID")
            if article.status < 200 or article.status >= 300:
                case.fail("tạo article relation probe", str(article.status), "không tạo được article probe")
                return case
            article_id = article.body.get("data", {}).get("id")
            deleted = self.api.request("DELETE", f"/items/qa_categories/{category_id}", self.editor_token)
            case.step("DELETE", f"/items/qa_categories/{category_id}", deleted, "2xx")
            if deleted.status < 200 or deleted.status >= 300:
                case.fail("xóa category probe", str(deleted.status), "xóa relation probe thất bại")
                return case
            category_id = None
            read_back = self.api.request("GET", f"/items/qa_articles/{article_id}?fields=id,category", self.editor_token)
            case.step("GET", f"/items/qa_articles/{article_id}?fields=id,category", read_back, "2xx và category=null")
            if read_back.status < 200 or read_back.status >= 300 or read_back.body.get("data", {}).get("category") is not None:
                case.fail("category được nullify", str(read_back.body), "on_delete SET NULL invariant thất bại")
                return case
            case.expected = "qa_articles.category == null sau DELETE category"
            case.actual = "category=null"
            return case
        finally:
            if article_id is not None:
                self.api.request("DELETE", f"/items/qa_articles/{article_id}", self.editor_token, record=False)
            if category_id is not None:
                self.api.request("DELETE", f"/items/qa_categories/{category_id}", self.editor_token, record=False)

    def case_invalid_field_rejection(self) -> Case:
        case = Case("invalid-field-rejection", "Dữ liệu score/status không hợp lệ bị từ chối")
        title = f"Invalid field probe {os.environ.get('LAB_RUN_ID', 'local')}"
        body = {
            "title": title,
            "status": "archived",
            "score": -1,
            "published_at": None,
            "metadata": None,
            "internal_notes": "probe",
            "category": self.fixture_category_id("category_alpha"),
        }
        response = self.api.request("POST", "/items/qa_articles", self.editor_token, body)
        case.step("POST", "/items/qa_articles", response, "non-2xx")
        if response.status == 0:
            case.fail("validation response non-2xx", "network error", response.error or "network error")
            return case
        if 200 <= response.status < 300:
            created_id = response.body.get("data", {}).get("id") if isinstance(response.body, dict) else None
            if created_id:
                self.api.request("DELETE", f"/items/qa_articles/{created_id}", self.editor_token, record=False)
            case.fail("score/status invalid bị từ chối", str(response.status), "validation probe được chấp nhận")
            return case
        query = "/items/qa_articles" + self.path_params({"filter[title][_eq]": title, "limit": "-1", "fields": "id,title"})
        read_back = self.api.request("GET", query, self.admin_token)
        case.step("GET", query, read_back, "2xx và không có row probe")
        rows = read_back.body.get("data", []) if isinstance(read_back.body, dict) else []
        if read_back.status < 200 or read_back.status >= 300 or rows:
            case.fail("request bị từ chối không làm thay đổi dữ liệu", repr(rows), "invalid probe để lại dữ liệu")
            return case
        case.expected = "score/status invalid bị từ chối và không tạo row"
        case.actual = f"POST HTTP {response.status}, rows=0"
        return case

    def case_reader_visibility(self) -> Case:
        case = Case("reader-visibility", "Reader chỉ đọc published và không lộ internal_notes")
        path = "/items/qa_articles"
        if not self.reader_schema:
            case.block("reader schema đã export", "thiếu reader.json", "chạy ./lab.sh export-schema trước")
            return case
        if not self.has_operation("GET", path):
            case.block("reader GET article xuất hiện trong schema", "operation absent", "không gửi request quyền bị cấm")
            return case
        request_path = path + self.path_params(
            {"filter[status][_eq]": "published", "limit": "-1", "fields": "id,title,status,internal_notes"}
        )
        response = self.api.request("GET", request_path, self.reader_token)
        case.step("GET", request_path, response, "2xx, published-only, không internal_notes")
        rows = response.body.get("data", []) if isinstance(response.body, dict) else []
        expected_ids = {
            value
            for key, value in self.fixture_map["fixtures"]["qa_articles"].items()
            if "_published_" in key
        }
        actual_ids = {row.get("id") for row in rows if isinstance(row, dict)}
        if response.status < 200 or response.status >= 300:
            case.fail("reader đọc published article", str(response.status), "reader operation có nhưng request thất bại")
        elif actual_ids != expected_ids or any(row.get("status") != "published" for row in rows):
            case.fail("reader chỉ nhận sáu published fixture", repr(actual_ids), "reader trả draft hoặc sai tập dữ liệu")
        elif any("internal_notes" in row for row in rows if isinstance(row, dict)):
            case.fail("internal_notes không xuất hiện", "field present", "private field bị lộ")
        else:
            case.expected = "published-only và internal_notes bị ẩn"
            case.actual = f"rows={len(rows)}"
        return case

    def case_reader_write(self) -> Case:
        case = Case("reader-write", "Reader bị từ chối ghi và dữ liệu không đổi")
        path = "/items/qa_articles/{id}"
        if not self.reader_schema:
            case.block("reader schema đã export", "thiếu reader.json", "chạy ./lab.sh export-schema trước")
            return case
        if not self.has_operation("PATCH", path):
            case.block("reader PATCH xuất hiện trong schema", "operation absent", "không gửi request quyền bị cấm")
            return case
        item_id = self.fixture_article_id("article_alpha_published_1")
        read_path = f"/items/qa_articles/{item_id}?fields=id,title,status,score"
        before = self.api.request("GET", read_path, self.editor_token)
        case.step("GET", read_path, before, "2xx precondition")
        if before.status < 200 or before.status >= 300:
            case.fail("editor đọc được target trước negative case", str(before.status), "precondition thất bại")
            return case
        before_data = before.body.get("data", {})
        new_score = (int(before_data.get("score", 0)) + 1) % 6
        patch_path = f"/items/qa_articles/{item_id}"
        denied = self.api.request("PATCH", patch_path, self.reader_token, {"score": new_score})
        case.step("PATCH", patch_path, denied, "non-2xx")
        if denied.status == 0 or 200 <= denied.status < 300:
            case.fail("reader PATCH bị từ chối", str(denied.status), "negative write được chấp nhận")
            return case
        after = self.api.request("GET", read_path, self.editor_token)
        case.step("GET", read_path, after, "2xx và data không đổi")
        if after.status < 200 or after.status >= 300 or after.body.get("data") != before_data:
            case.fail("target không đổi sau request bị từ chối", repr(after.body), "data thay đổi sau negative case")
            return case
        case.expected = "reader PATCH non-2xx, target unchanged"
        case.actual = f"PATCH HTTP {denied.status}, unchanged=true"
        return case


def git_head(root: Path) -> str:
    reported = os.environ.get("LAB_HARNESS_SHA", "")
    if reported:
        return reported
    try:
        return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "no_commit"


def run() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Directus invariants")
    parser.add_argument("--case", default="all", help="all or one of the stable replay case IDs")
    args = parser.parse_args()
    run_dir = Path(env_required("LAB_RUN_DIR"))
    run_dir.mkdir(parents=True, exist_ok=True)
    started_at = utc_now()
    lab = Lab(run_dir)
    lab.authenticate()
    lab.load_fixture()

    cases: dict[str, Callable[[], Case]] = {
        "auth-invalid-token": lab.case_auth_invalid_token,
        "anonymous-denied": lab.case_anonymous_denied,
        "editor-crud": lab.case_editor_crud,
        "positive-operations": lab.case_positive_operations,
        "query-fixture": lab.case_query_fixture,
        "relation-nullification": lab.case_relation_nullification,
        "invalid-field-rejection": lab.case_invalid_field_rejection,
        "reader-visibility": lab.case_reader_visibility,
        "reader-write": lab.case_reader_write,
    }
    if args.case == "all":
        selected = list(cases)
    elif args.case in cases:
        selected = [args.case]
    else:
        print(f"ERROR: case không hỗ trợ: {args.case}", file=sys.stderr)
        print("Case IDs: " + ", ".join(cases), file=sys.stderr)
        return 2

    results: list[Case] = []
    for case_id in selected:
        try:
            result = cases[case_id]()
        except (KeyError, RuntimeError, OSError, ValueError) as error:
            result = Case(case_id, case_id)
            result.fail("case chạy không phát sinh exception", "exception", str(error))
        results.append(result)
        print(f"Invariant {case_id}: {result.status}")
        if result.status in {"failed", "blocked"}:
            (run_dir / f"reproducer-{case_id}.json").write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "case_id": result.case_id,
                        "precondition": "lab đã up, seed đã chạy, credential lấy từ config/lab.env",
                        "case": result.as_dict(),
                        "created_at": utc_now(),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

    report = {
        "schema": 1,
        "run_id": os.environ.get("LAB_RUN_ID", "unknown"),
        "harness_sha": git_head(Path(env_required("LAB_ROOT_DIR"))),
        "fixture_version": lab.fixture_map.get("fixture_version"),
        "started_at": started_at,
        "finished_at": utc_now(),
        "cases": [case.as_dict() for case in results],
        "summary": {
            "passed": sum(case.status == "passed" for case in results),
            "failed": sum(case.status == "failed" for case in results),
            "blocked": sum(case.status == "blocked" for case in results),
            "total": len(results),
        },
    }
    (run_dir / "invariant-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    summary = report["summary"]
    print(f"Invariant report: {run_dir / 'invariant-report.json'}")
    print(f"Summary: passed={summary['passed']} failed={summary['failed']} blocked={summary['blocked']}")
    return 1 if summary["failed"] or summary["blocked"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except (RuntimeError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: invariant runner: {error}", file=sys.stderr)
        raise SystemExit(1)
