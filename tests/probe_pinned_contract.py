"""Offline probe executed only inside the pinned Schemathesis runner."""
import hashlib
import importlib.metadata
import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from contract_checks import validate
from invariants import ApiResponse
from schemathesis.specs.openapi import formats


def probe(property_schema, value, status=200):
    schema = {"openapi": "3.0.1", "info": {"title": "offline probe", "version": "1"}, "paths": {
        "/items/qa_articles": {"get": {"responses": {"200": {"description": "ok", "content": {
            "application/json": {"schema": {"type": "object", "required": ["data"], "properties": {
                "data": {"type": "object", "required": ["value"], "properties": {"value": property_schema}}}}}}}}}}}}
    body = {"data": {"value": value}}
    response = ApiResponse(status, body, json.dumps(body).encode(), "application/json")
    return validate(schema, "GET", "/items/qa_articles", response)


def main():
    observed = {
        "timestamp_arbitrary_string": probe({"type": "string", "format": "timestamp"}, "not-a-date"),
        "nullable_integer_null": probe({"type": "integer", "nullable": True}, None),
        "nonnullable_integer_null": probe({"type": "integer"}, None),
        "typeless_nullable_scalar": probe({"nullable": True}, "scalar"),
        "oneof_nullable_null": probe({"nullable": True, "oneOf": [{"type": "integer"}, {"type": "object"}]}, None),
        "unexpected_204": probe({"type": "integer"}, 1, 204),
        "server_500": probe({"type": "integer"}, 1, 500),
    }
    def verdict(name, check):
        return next(c["status"] for c in observed[name] if c["name"] == check)
    assert verdict("nonnullable_integer_null", "response_schema_conformance") == "failed"
    assert verdict("nullable_integer_null", "response_schema_conformance") == "passed"
    assert verdict("timestamp_arbitrary_string", "response_schema_conformance") == "passed"
    assert verdict("typeless_nullable_scalar", "response_schema_conformance") == "passed"
    assert verdict("unexpected_204", "status_code_conformance") == "failed"
    assert verdict("server_500", "not_a_server_error") == "failed"
    source = Path(inspect.getfile(formats))
    keys = sorted(formats.get_default_format_strategies())
    print(json.dumps({"schemathesis": importlib.metadata.version("schemathesis"),
        "formats_module": str(source), "formats_source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "default_generation_formats": keys, "timestamp_registered": "timestamp" in keys,
        "observations": observed, "assertions": "passed", "network": "disabled"}, indent=2))


if __name__ == "__main__":
    main()
