"""Run the pinned Schemathesis checks against an already received response.

This module never calls the network or modifies the exported contract.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.metadata
import json
from typing import Any

_schemas: dict[str, Any] = {}
CHECKS = ("not_a_server_error", "status_code_conformance", "content_type_conformance", "response_schema_conformance")


def validate(schema: dict[str, Any], method: str, path: str, response: Any,
             *, path_parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    import requests
    import schemathesis
    import schemathesis.checks
    from schemathesis.core.failures import FailureGroup
    from schemathesis.core.transport import Response

    if importlib.metadata.version("schemathesis") != "4.30.0":
        raise RuntimeError("Contract adapter requires the pinned Schemathesis 4.30.0 image")
    digest = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
    if digest not in _schemas:
        _schemas[digest] = schemathesis.openapi.from_dict(copy.deepcopy(schema))
    case = _schemas[digest][path][method.upper()].Case(path_parameters=path_parameters)
    headers = {k.lower(): v for k, v in response.headers.items()}
    if response.content_type:
        headers["content-type"] = [response.content_type]
    actual = Response(status_code=response.status, headers=headers, content=response.raw,
                      request=requests.Request(method, "http://directus:8055" + path).prepare(),
                      elapsed=response.elapsed, verify=True)
    results = []
    for name in CHECKS:
        try:
            case.validate_response(actual, checks=[getattr(schemathesis.checks, name)])
            results.append({"name": name, "status": "passed", "failures": []})
        except FailureGroup as error:
            results.append({"name": name, "status": "failed", "failures": [
                {"type": type(f).__name__, "title": getattr(f, "title", type(f).__name__)} for f in error.exceptions
            ]})
        except Exception as error:
            results.append({"name": name, "status": "error", "error_type": type(error).__name__, "failures": []})
    return results
