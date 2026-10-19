#!/usr/bin/env bash

# Build a Swagger UI copy from the actor snapshots. Never modify the raw schema
# consumed by Schemathesis.
set -Eeuo pipefail

[[ $# -eq 5 ]] || {
	printf 'Usage: swagger-spec.sh <raw-dir> <viewer-dir> <run-dir> <fixture-version> <api-url>\n' >&2
	exit 2
}

raw_dir="$1"
viewer_dir="$2"
run_dir="$3"
fixture_version="$4"
api_url="$5"
temporary_file=''

cleanup_temporary_file() {
	if [[ -n "$temporary_file" && -f "$temporary_file" ]]; then
		rm -- "$temporary_file"
	fi
}
trap cleanup_temporary_file EXIT

[[ "$api_url" == 'http://127.0.0.1:8055' ]] || {
	printf 'ERROR: Swagger chỉ được trỏ tới API lab 127.0.0.1:8055.\n' >&2
	exit 1
}

for actor in editor reader; do
	source_file="$raw_dir/$actor.json"
	[[ -f "$source_file" ]] || {
		printf 'ERROR: thiếu schema %s; chạy ./lab.sh seed và ./lab.sh export-schema trước.\n' "$source_file" >&2
		exit 1
	}
	jq -e --arg api_url "$api_url" '
		.openapi == "3.0.1"
		and (.paths | type == "object" and has("/items/qa_articles") and has("/items/qa_categories") and has("/auth/login"))
		and (.servers | type == "array" and length == 1 and .[0].url == $api_url)
		and (.components.securitySchemes.Auth | .type == "apiKey" and .in == "header" and .name == "Authorization")
	' "$source_file" >/dev/null || {
		printf 'ERROR: schema %s không khớp OpenAPI/URL/Auth của lab.\n' "$source_file" >&2
		exit 1
	}
done

mkdir -p "$viewer_dir" "$run_dir"
for actor in editor reader; do
	source_file="$raw_dir/$actor.json"
	viewer_file="$viewer_dir/$actor.json"
	source_sha="$(sha256sum "$source_file" | awk '{print $1}')"
	temporary_file="$(mktemp "$viewer_dir/.$actor.XXXXXX")"
	jq '
		def public_path($path):
			["/auth/login", "/auth/refresh", "/auth/password/request",
			 "/auth/password/reset", "/auth/oauth", "/auth/oauth/{provider}",
			 "/server/info", "/server/ping"] | index($path) != null;
		.paths |= with_entries(
			.key as $path
			| .value |= with_entries(
				if (.key | IN("get", "post", "put", "patch", "delete", "head", "options", "trace"))
				   and (.value | has("security") | not)
				   and (public_path($path) | not)
				then .value.security = [{"Auth": []}]
				else . end
			)
		)
	' "$source_file" > "$temporary_file"
	chmod 644 "$temporary_file"
	mv -- "$temporary_file" "$viewer_file"
	temporary_file=''
	[[ "$(sha256sum "$source_file" | awk '{print $1}')" == "$source_sha" ]] || {
		printf 'ERROR: schema gốc %s thay đổi trong lúc tạo bản Swagger.\n' "$source_file" >&2
		exit 1
	}
	viewer_sha="$(sha256sum "$viewer_file" | awk '{print $1}')"
	cp -- "$viewer_file" "$run_dir/swagger-$actor.json"
	jq -n --slurpfile original "$source_file" --slurpfile viewer "$viewer_file" \
		--arg source_file "$source_file" --arg viewer_file "$viewer_file" \
		--arg source_sha "$source_sha" --arg viewer_sha "$viewer_sha" '
		{
			source_file: $source_file,
			source_sha256: $source_sha,
			viewer_file: $viewer_file,
			viewer_sha256: $viewer_sha,
			reason: "Swagger UI uses Auth to attach Authorization on operations where the raw Directus schema omits security; this is a UI convenience, not a claim about the API contract",
			security_diff: [
				$viewer[0].paths | to_entries[] | .key as $path | .value | to_entries[]
				| .key as $method
				| select($method | IN("get", "post", "put", "patch", "delete", "head", "options", "trace"))
				| {
					path: $path,
					method: ($method | ascii_upcase),
					before: ($original[0].paths[$path][$method].security // null),
					after: (.value.security // null)
				  }
				| select(.before != .after)
			]
		}' > "$run_dir/swagger-overlay-$actor.json"
	printf 'Swagger schema %s: raw=%s viewer=%s\n' "$actor" "$source_sha" "$viewer_sha"
done

jq -n --slurpfile editor "$run_dir/swagger-overlay-editor.json" \
	--slurpfile reader "$run_dir/swagger-overlay-reader.json" \
	--arg fixture_version "$fixture_version" --arg api_url "$api_url" '
	{
		schema: 1,
		purpose: "swagger_ui_display_only",
		fixture_version: $fixture_version,
		api_url: $api_url,
		actors: {editor: $editor[0], reader: $reader[0]}
	}' > "$run_dir/swagger-schema-manifest.json"
printf 'Swagger manifest: %s\n' "$run_dir/swagger-schema-manifest.json"
