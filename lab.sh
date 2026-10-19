#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
COMPOSE_FILE="$ROOT_DIR/compose.yaml"
ENV_FILE="$ROOT_DIR/config/lab.env"
PROJECT_NAME="r06-k05"
DEFAULT_API_URL="http://127.0.0.1:8055"
DEFAULT_RUNNER_API_URL="http://directus:8055"
API_URL="$DEFAULT_API_URL"
RUNNER_API_URL="$DEFAULT_RUNNER_API_URL"

ARTIFACT_ROOT="$ROOT_DIR/artifacts/runs"
RUNTIME_ROOT="$ROOT_DIR/runtime"
RUNTIME_PROFILE="${LAB_RUNTIME_PROFILE:-}"
if [[ -n "$RUNTIME_PROFILE" ]]; then
	[[ "$RUNTIME_PROFILE" =~ ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$ ]] || {
		printf 'ERROR: LAB_RUNTIME_PROFILE chỉ được chứa chữ, số, gạch ngang và gạch dưới.\n' >&2
		exit 1
	}
	RUNTIME_ROOT="$RUNTIME_ROOT/profiles/$RUNTIME_PROFILE"
fi
RUN_DIR=""
RUN_LOG=""
RUN_METADATA=""
RUN_ID=""
RUN_COMMAND=""
RUN_STARTED_AT=""
RUN_STARTED_EPOCH=0
RUN_FINALIZED=0
REDACTION_VALUES=()

die() {
	printf 'ERROR: %s\n' "$*" >&2
	exit 1
}

usage() {
	cat <<'EOF'
Usage:
  ./lab.sh doctor
  ./lab.sh up|down
  ./lab.sh seed|smoke|export-schema
  ./lab.sh swagger up|down
  ./lab.sh test smoke|schema-smoke|scenarios|invariants|designed|cost-query|raw|guided
  ./lab.sh test cost-query --set exhaustive|pairwise
  ./lab.sh test designed [--case ID|--selection course|short|all|assertable|--group GROUP]
  Course suite: test scenarios (6) + test designed --selection course (7)
  ./lab.sh replay <case-id>
  ./lab.sh reset
  ./lab.sh help
EOF
}

compose() {
	docker compose \
		--project-name "$PROJECT_NAME" \
		--env-file "$ENV_FILE" \
		--file "$COMPOSE_FILE" \
		"$@"
}

json_escape() {
	local value="$1"

	if command -v jq >/dev/null 2>&1; then
		jq -Rn --arg value "$value" '$value'
		return 0
	fi

	# Metadata values are restricted to non-secret paths, URLs, identifiers and
	# statuses. This fallback keeps the run record valid when jq is unavailable;
	# doctor still reports jq as a required dependency for the lab.
	value="${value//\\/\\\\}"
	value="${value//\"/\\\"}"
	value="${value//$'\n'/\\n}"
	printf '"%s"' "$value"
}

json_or_null() {
	if [[ -n "$1" ]]; then
		json_escape "$1"
	else
		printf 'null'
	fi
}

config_has_key() {
	local key="$1"
	[[ -f "$ENV_FILE" ]] && awk -F= -v key="$key" '$1 == key { found = 1 } END { exit(found ? 0 : 1) }' "$ENV_FILE"
}

config_value() {
	local key="$1"
	awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "$ENV_FILE"
}

config_value_or_default() {
	local key="$1"
	local fallback="$2"
	local value=""

	if [[ -f "$ENV_FILE" ]]; then
		value="$(config_value "$key" 2>/dev/null || true)"
	fi
	if [[ -n "$value" ]]; then
		printf '%s' "$value"
	else
		printf '%s' "$fallback"
	fi
}

configure_urls() {
	API_URL="${LAB_API_URL:-$(config_value_or_default API_URL "$DEFAULT_API_URL")}"
	RUNNER_API_URL="${LAB_RUNNER_API_URL:-$(config_value_or_default RUNNER_API_URL "$DEFAULT_RUNNER_API_URL")}"
}

config_permissions_safe() {
	case "$(uname -s)" in
		MINGW*|MSYS*|CYGWIN*)
			# NTFS permissions are ACLs; Git Bash's mode bits do not reflect them.
			LAB_CONFIG_ACL_PATH="$(cygpath -w "$ENV_FILE")" powershell.exe -NoProfile -NonInteractive -Command '
				$ErrorActionPreference = "Stop"
				$acl = [System.IO.File]::GetAccessControl($env:LAB_CONFIG_ACL_PATH)
				$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
				$allowed = @($sid, "S-1-5-18", "S-1-5-32-544")
				foreach ($rule in $acl.GetAccessRules($true, $true, [System.Security.Principal.SecurityIdentifier])) {
					if ($rule.AccessControlType -eq "Allow" -and $rule.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value -notin $allowed) { exit 1 }
				}
				exit 0
			' >/dev/null 2>&1
			;;
		*)
			[[ "$(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE")" =~ ^6?00$|^400$|^600$ ]]
			;;
	esac
}

require_config() {
	[[ -f "$ENV_FILE" ]] || die "Thiếu $ENV_FILE. Sao chép config/lab.env.example và điền giá trị cục bộ."
	config_permissions_safe || die "$ENV_FILE phải có quyền riêng tư (chmod 600 trên Unix hoặc ACL riêng trên Windows)."
}

check_command() {
	local command_name="$1"
	if command -v "$command_name" >/dev/null 2>&1; then
		printf 'OK   command %-12s %s\n' "$command_name" "$(command -v "$command_name")"
		return 0
	fi
	printf 'FAIL command %-12s missing\n' "$command_name"
	return 1
}

require_docker() {
	command -v docker >/dev/null 2>&1 || die 'Không tìm thấy Docker CLI trong PATH của phiên shell này.'
	docker info >/dev/null 2>&1 || die 'Docker CLI có nhưng Docker daemon không khả dụng trong phiên shell này.'
	docker compose version >/dev/null 2>&1 || die 'Docker Compose plugin không khả dụng trong phiên shell này.'
	verify_project_checkout
}

verify_project_checkout() {
	local container_id owner owner_unix root_unix containers
	containers="$(docker ps -aq --filter "label=com.docker.compose.project=$PROJECT_NAME")" || die 'Không kiểm tra được container của project lab.'
	for container_id in $containers; do
		owner="$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}' "$container_id")" || die "Không kiểm tra được checkout của container $container_id."
		[[ -n "$owner" && "$owner" != '<no value>' ]] || die "Container $container_id thiếu nhãn checkout."
		if [[ "$owner" == "$ROOT_DIR" ]]; then continue; fi
		case "$(uname -s)" in
			MINGW*|MSYS*|CYGWIN*)
				owner_unix="$(cygpath -u "$owner")" || die "Không chuẩn hóa được checkout của container $container_id."
				root_unix="$(cygpath -u "$ROOT_DIR")" || die 'Không chuẩn hóa được checkout hiện tại.'
				[[ "${owner_unix,,}" == "${root_unix,,}" ]] && continue
				;;
		esac
		die "Project $PROJECT_NAME thuộc checkout khác ($owner), không phải $ROOT_DIR."
	done
}

verify_compose_target() {
	[[ "$API_URL" == http://127.0.0.1:8055 || "$API_URL" == http://localhost:8055 ]] || die 'Host API URL ngoài baseline loopback:8055.'
	[[ "$RUNNER_API_URL" == http://directus:8055 ]] || die 'Runner URL ngoài baseline directus:8055.'
	local service container_id configured_image actual_image expected_image
	for service in directus database; do
		container_id="$(compose ps -q "$service")"
		[[ -n "$container_id" ]] || die "Service $service chưa chạy; dùng up trước test."
		[[ "$(docker inspect --format '{{index .Config.Labels "com.docker.compose.project"}}' "$container_id")" == r06-k05 ]] || die 'Container không thuộc project lab.'
		if [[ "$service" == directus ]]; then
			configured_image="$(config_value DIRECTUS_IMAGE)"
			[[ "$(docker inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$container_id")" == 4f77933bf9551cac6b289576078783e189b8f4e3 ]] || die 'Directus revision không đúng source pin.'
			docker inspect --format '{{json .HostConfig.PortBindings}}' "$container_id" | jq -e '."8055/tcp" | length == 1 and .[0].HostIp == "127.0.0.1" and .[0].HostPort == "8055"' >/dev/null || die 'Directus port binding khác lab loopback.'
		else
			configured_image="$(config_value POSTGRES_IMAGE)"
		fi
		[[ "$configured_image" == *@sha256:* ]] || die 'Image cần digest pin.'
		expected_image="$(docker image inspect --format '{{.Id}}' "$configured_image")"
		actual_image="$(docker inspect --format '{{.Image}}' "$container_id")"
		[[ "$expected_image" == "$actual_image" ]] || die "Service $service không dùng image cấu hình."
	done
	jq -n --arg project r06-k05 --arg revision 4f77933bf9551cac6b289576078783e189b8f4e3 \
		'{project:$project,directus_revision:$revision,container_images_match_config:true,loopback_binding_verified:true}' > "$RUN_DIR/target-verification.json"
}

snapshot_run_inputs() {
	command -v jq >/dev/null 2>&1 || return 0
	local file
	{
		for file in lab.sh compose.yaml manifest/baseline.yaml README.md config/lab.env.example scripts/*.py scripts/*.sh scripts/*.ps1 scripts/data/*.json scripts/windows/jq tests/*.py; do
			[[ -f "$ROOT_DIR/$file" ]] || continue
			printf '%s\t%s\n' "$file" "$(sha256sum "$ROOT_DIR/$file" | awk '{print $1}')"
		done
	} | jq -Rn '{files:[inputs | split("\t") | {path:.[0],sha256:.[1]}]}' > "$RUN_DIR/harness-inputs.json"
	if [[ -f "$RUNTIME_ROOT/fixture-ids.json" ]]; then cp -- "$RUNTIME_ROOT/fixture-ids.json" "$RUN_DIR/fixture-ids-input.json"; fi
	local version="${LAB_FIXTURE_VERSION:-$(config_value_or_default LAB_FIXTURE_VERSION r06-k05-v2)}"
	for file in admin editor reader anonymous; do
		if [[ -f "$RUNTIME_ROOT/schemas/$version/$file.json" ]]; then
			cp -- "$RUNTIME_ROOT/schemas/$version/$file.json" "$RUN_DIR/input-schema-$file.json"
		fi
	done
}

working_tree_state() {
	if ! command -v git >/dev/null 2>&1; then
		printf 'git_unavailable'
	elif git -C "$ROOT_DIR" diff --quiet --ignore-submodules -- && \
		git -C "$ROOT_DIR" diff --cached --quiet --ignore-submodules -- && \
		[[ -z "$(git -C "$ROOT_DIR" status --porcelain --untracked-files=normal 2>/dev/null)" ]]; then
		printf 'clean'
	else
		printf 'dirty'
	fi
}

harness_sha() {
	if command -v git >/dev/null 2>&1; then
		git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || printf 'no_commit'
	else
		printf 'git_unavailable'
	fi
}

valid_run_id() {
	[[ "$1" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]
}

valid_actor() {
	case "$1" in
		admin|editor|reader|anonymous|unspecified)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

load_redaction_values() {
	local key
	local value
	REDACTION_VALUES=()

	for key in DB_PASSWORD DIRECTUS_KEY DIRECTUS_SECRET ADMIN_PASSWORD EDITOR_PASSWORD READER_PASSWORD LICENSE_KEY; do
		value="$(config_value "$key" 2>/dev/null || true)"
		case "$value" in
			''|REPLACE_*)
				;;
			*)
				REDACTION_VALUES+=("$value")
				;;
		esac
	done
}

redact_stream() {
	local line
	local secret

	while IFS= read -r line || [[ -n "$line" ]]; do
		for secret in "${REDACTION_VALUES[@]}"; do
			line="${line//"$secret"/[REDACTED]}"
		done
		printf '%s\n' "$line"
	done
}

admin_authenticated_health() {
	local admin_email
	local admin_password
	local login_response
	local access_token
	local health_status
	local null_output='/dev/null'
	case "$(uname -s)" in
		MINGW*|MSYS*|CYGWIN*) null_output='NUL' ;;
	esac

	admin_email="$(config_value ADMIN_EMAIL 2>/dev/null || true)"
	admin_password="$(config_value ADMIN_PASSWORD 2>/dev/null || true)"
	case "$admin_email:$admin_password" in
		:*|*:|REPLACE_*|*:REPLACE_*)
			return 2
			;;
	esac

	if ! login_response="$(
		printf '{"email":%s,"password":%s}' "$(json_escape "$admin_email")" "$(json_escape "$admin_password")" |
			curl -fsS --max-time 5 -H 'Content-Type: application/json' --data-binary @- "$API_URL/auth/login" 2>/dev/null
	)"; then
		return 1
	fi

	access_token="$(printf '%s' "$login_response" | jq -r '.data.access_token // empty' 2>/dev/null || true)"
	[[ -n "$access_token" ]] || return 1

	if ! health_status="$(
		{
			printf 'url = "%s/server/health"\n' "$API_URL"
			printf 'header = "Authorization: Bearer %s"\n' "$access_token"
			printf 'output = "%s"\n' "$null_output"
			printf 'write-out = "%%{http_code}"\n'
			printf 'silent\nshow-error\nfail\nmax-time = 5\n'
		} | curl --config - 2>/dev/null
	)"; then
		return 1
	fi
	[[ "$health_status" == 200 ]]
}

admin_license_summary() {
	local admin_email
	local admin_password
	local login_response
	local access_token
	local license_response

	admin_email="$(config_value ADMIN_EMAIL 2>/dev/null || true)"
	admin_password="$(config_value ADMIN_PASSWORD 2>/dev/null || true)"
	case "$admin_email:$admin_password" in
		:*|*:|REPLACE_*|*:REPLACE_*)
			return 2
			;;
	esac

	login_response="$(
		printf '{"email":%s,"password":%s}' "$(json_escape "$admin_email")" "$(json_escape "$admin_password")" |
			curl -fsS --max-time 5 -H 'Content-Type: application/json' --data-binary @- "$API_URL/auth/login" 2>/dev/null
	)" || return 1
	access_token="$(printf '%s' "$login_response" | jq -r '.data.access_token // empty' 2>/dev/null || true)"
	[[ -n "$access_token" ]] || return 1
	license_response="$(curl -fsS --max-time 5 -H "Authorization: Bearer $access_token" "$API_URL/license" 2>/dev/null)" || return 1
	printf '%s' "$license_response" | jq -c '
		{
			source: (.data.source // null),
			status: (.data.status // null),
			custom_permission_rules_enabled: (
				.data.entitlements.custom_permission_rules_enabled as $entitlement
				| if ($entitlement | (has("override") and .override != null)) then $entitlement.override else $entitlement.default end
			)
		}
	'
}

write_run_metadata() {
	local status="$1"
	local exit_code="$2"
	local finished_at="$3"
	local fixture_version="${LAB_FIXTURE_VERSION:-}"
	local schema_hash="${LAB_SCHEMA_HASH:-}"
	local seed="${LAB_SEED:-}"
	local budget="${LAB_BUDGET:-}"
	local actor="${LAB_ACTOR:-unspecified}"
	local duration_seconds='null'
	local campaign_index=''
	local swagger_schema_manifest=''
	local directus_image
	local postgres_image
	local schemathesis_image
	local metadata_tmp="$RUN_METADATA.tmp"
	local execution='null'

	[[ -n "$RUN_METADATA" ]] || return 0
	if [[ -f "$RUN_DIR/execution-config.json" ]]; then
		execution="$(jq -c . "$RUN_DIR/execution-config.json")"
	fi
	directus_image="$(config_value_or_default DIRECTUS_IMAGE '')"
	postgres_image="$(config_value_or_default POSTGRES_IMAGE '')"
	schemathesis_image="$(config_value_or_default SCHEMATHESIS_IMAGE '')"
	if [[ -z "$schema_hash" && -f "$RUN_DIR/schema-manifest.json" ]] && command -v jq >/dev/null 2>&1; then
		schema_hash="$(jq -r '.actors.editor.sha256 // empty' "$RUN_DIR/schema-manifest.json" 2>/dev/null || true)"
	fi
	if [[ -z "$schema_hash" && -f "$RUN_DIR/pilot-summary.json" ]] && command -v jq >/dev/null 2>&1; then
		schema_hash="$(jq -r '.source_schema_sha256 // empty' "$RUN_DIR/pilot-summary.json" 2>/dev/null || true)"
	fi
	if [[ -f "$RUN_DIR/campaign-index.json" ]] && command -v jq >/dev/null 2>&1; then
		campaign_index="$RUN_DIR/campaign-index.json"
		if [[ -z "$schema_hash" ]]; then
			schema_hash="$(jq -r '[.campaigns[]?.schema_sha256] | unique | join(",")' "$campaign_index" 2>/dev/null || true)"
		fi
		if [[ -z "$seed" ]]; then
			seed="$(jq -r '.seeds | map(tostring) | join(",")' "$campaign_index" 2>/dev/null || true)"
		fi
		if [[ -z "$budget" ]]; then
			budget="$(jq -c '.campaigns[0].budget // empty' "$campaign_index" 2>/dev/null || true)"
		fi
	fi
	if [[ -f "$RUN_DIR/swagger-schema-manifest.json" ]]; then
		swagger_schema_manifest="$RUN_DIR/swagger-schema-manifest.json"
	fi
	if [[ -z "$seed" && -f "$RUN_DIR/pilot-summary.json" ]] && command -v jq >/dev/null 2>&1; then
		seed="$(jq -r '.seed // empty' "$RUN_DIR/pilot-summary.json" 2>/dev/null || true)"
	fi
	if [[ -z "$budget" && -f "$RUN_DIR/pilot-summary.json" ]] && command -v jq >/dev/null 2>&1; then
		budget="$(jq -r '.budget // empty' "$RUN_DIR/pilot-summary.json" 2>/dev/null || true)"
	fi
	if [[ -z "$fixture_version" && -f "$RUNTIME_ROOT/fixture-ids.json" ]] && command -v jq >/dev/null 2>&1; then
		fixture_version="$(jq -r '.fixture_version // empty' "$RUNTIME_ROOT/fixture-ids.json" 2>/dev/null || true)"
	fi
	if [[ -z "$schema_hash" && -n "$fixture_version" && -f "$RUNTIME_ROOT/schemas/$fixture_version/editor.json" ]]; then
		schema_hash="$(sha256sum "$RUNTIME_ROOT/schemas/$fixture_version/editor.json" | awk '{print $1}')"
	fi
	if [[ "$RUN_STARTED_EPOCH" =~ ^[0-9]+$ ]] && (( RUN_STARTED_EPOCH > 0 )); then
		duration_seconds="$(( $(date +%s) - RUN_STARTED_EPOCH ))"
	fi

	{
		printf '{\n'
		printf '  "schema": 1,\n'
		printf '  "run_id": %s,\n' "$(json_escape "$RUN_ID")"
		printf '  "command": %s,\n' "$(json_escape "$RUN_COMMAND")"
		printf '  "status": %s,\n' "$(json_escape "$status")"
		printf '  "exit_code": %s,\n' "$exit_code"
		printf '  "started_at": %s,\n' "$(json_escape "$RUN_STARTED_AT")"
		printf '  "finished_at": %s,\n' "$(json_or_null "$finished_at")"
		printf '  "duration_seconds": %s,\n' "$duration_seconds"
		printf '  "harness_sha": %s,\n' "$(json_escape "$(harness_sha)")"
		printf '  "working_tree": %s,\n' "$(json_escape "$(working_tree_state)")"
		printf '  "harness_inputs": %s,\n' "$(json_escape "$RUN_DIR/harness-inputs.json")"
		printf '  "fixture_map_input": %s,\n' "$(json_escape "$RUN_DIR/fixture-ids-input.json")"
		printf '  "project": %s,\n' "$(json_escape "$PROJECT_NAME")"
		printf '  "runtime_profile": %s,\n' "$(json_or_null "$RUNTIME_PROFILE")"
		printf '  "api_url": %s,\n' "$(json_escape "$API_URL")"
		printf '  "runner_api_url": %s,\n' "$(json_escape "$RUNNER_API_URL")"
		printf '  "actor": %s,\n' "$(json_escape "$actor")"
		printf '  "fixture_version": %s,\n' "$(json_or_null "$fixture_version")"
		printf '  "schema_hash": %s,\n' "$(json_or_null "$schema_hash")"
		printf '  "seed": %s,\n' "$(json_or_null "$seed")"
		printf '  "budget": %s,\n' "$(json_or_null "$budget")"
		printf '  "execution": %s,\n' "$execution"
		printf '  "baseline": {\n'
		printf '    "directus_image": %s,\n' "$(json_or_null "$directus_image")"
		printf '    "postgres_image": %s,\n' "$(json_or_null "$postgres_image")"
		printf '    "schemathesis_image": %s\n' "$(json_or_null "$schemathesis_image")"
		printf '  },\n'
		printf '  "campaign_index": %s,\n' "$(json_or_null "$campaign_index")"
		printf '  "swagger_schema_manifest": %s,\n' "$(json_or_null "$swagger_schema_manifest")"
		printf '  "fixture_map": %s,\n' "$(json_escape "$RUNTIME_ROOT/fixture-ids.json")"
		printf '  "artifact_dir": %s,\n' "$(json_escape "$RUN_DIR")"
		printf '  "log_file": %s\n' "$(json_escape "$RUN_LOG")"
		printf '}\n'
	} > "$metadata_tmp"
	mv -- "$metadata_tmp" "$RUN_METADATA"
}

begin_run() {
	local command_label="$1"
	local timestamp
	local requested_id="${LAB_RUN_ID:-}"
	local requested_actor="${LAB_ACTOR:-unspecified}"

	configure_urls
	valid_actor "$requested_actor" || die 'LAB_ACTOR phải là admin, editor, reader, anonymous hoặc unspecified.'
	if [[ -n "$requested_id" ]]; then
		valid_run_id "$requested_id" || die 'LAB_RUN_ID chỉ được chứa chữ, số, dấu chấm, gạch ngang và gạch dưới (tối đa 64 ký tự).'
		RUN_ID="$requested_id"
	else
		timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
		RUN_ID="${timestamp}-${BASHPID}"
	fi
	RUN_COMMAND="$command_label"
	RUN_STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
	RUN_STARTED_EPOCH="$(date +%s)"
	RUN_DIR="$ARTIFACT_ROOT/$RUN_ID"
	RUN_LOG="$RUN_DIR/run.log"
	RUN_METADATA="$RUN_DIR/metadata.json"
	[[ ! -e "$RUN_DIR" ]] || die "LAB_RUN_ID đã tồn tại: $RUN_ID. Dùng run ID mới để không ghi đè artefact."
	mkdir -p "$RUN_DIR" "$RUNTIME_ROOT"
	load_redaction_values

	# Keep command output reviewable while masking configured credentials in the
	# terminal and the local log. Generated tokens must still never be printed
	# by a seed or test implementation.
	exec > >(redact_stream | tee "$RUN_LOG") 2>&1
	snapshot_run_inputs
	write_run_metadata running null ''
	printf 'Run: %s\n' "$RUN_ID"
	printf 'Artefact directory: %s\n' "$RUN_DIR"
}

finish_run() {
	local exit_code="${1:-0}"
	local status='passed'

	[[ "$exit_code" -eq 0 ]] || status='failed'
	if [[ "$RUN_FINALIZED" -eq 0 && -n "$RUN_METADATA" ]]; then
		RUN_FINALIZED=1
		if [[ -f "$RUNTIME_ROOT/fixture-ids.json" ]]; then cp -- "$RUNTIME_ROOT/fixture-ids.json" "$RUN_DIR/fixture-ids-output.json"; fi
		if ! write_run_metadata "$status" "$exit_code" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"; then
			printf 'ERROR: không ghi được metadata cho run %s\n' "$RUN_ID" >&2
		fi
		printf 'Run status: %s (exit %s)\n' "$status" "$exit_code"
	fi
	if [[ "${LAB_LOCK_OWNER:-}" == "$RUN_ID" && -f "$ROOT_DIR/runtime/.mutation-lock/owner" ]] &&
		[[ "$(cat "$ROOT_DIR/runtime/.mutation-lock/owner")" == "$RUN_ID" ]]; then
		rm -- "$ROOT_DIR/runtime/.mutation-lock/owner"
		rmdir -- "$ROOT_DIR/runtime/.mutation-lock"
	fi
}

acquire_lab_lock() {
	mkdir -p "$ROOT_DIR/runtime"
	if ! mkdir "$ROOT_DIR/runtime/.mutation-lock" 2>/dev/null; then
		printf 'ERROR: lab đang bị khóa; xem runtime/.mutation-lock/owner. Không chạy hai suite ghi đồng thời.\n' >&2
		return 1
	fi
	printf '%s\n' "$RUN_ID" > "$ROOT_DIR/runtime/.mutation-lock/owner"
	LAB_LOCK_OWNER="$RUN_ID"
}

doctor() {
	local failures=0
	local key
	local image
	local api_status
	local lab_container_id
	local lab_container_state
	local docker_ready=0
	local compose_ready=0
	local api_url_allowed=1
	local license_summary

	configure_urls

	printf 'Lab: %s\n' "$PROJECT_NAME"
	printf 'Root: %s\n' "$ROOT_DIR"
	if [[ "$API_URL" != "$DEFAULT_API_URL" ]]; then
		printf 'FAIL API_URL must remain loopback: %s\n' "$API_URL"
		failures=$((failures + 1))
		api_url_allowed=0
	fi
	if [[ "$RUNNER_API_URL" != "$DEFAULT_RUNNER_API_URL" ]]; then
		printf 'FAIL RUNNER_API_URL must remain the lab hostname: %s\n' "$RUNNER_API_URL"
		failures=$((failures + 1))
	fi

	for key in docker curl jq; do
		check_command "$key" || failures=$((failures + 1))
	done

	if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
		printf 'OK   Docker daemon\n'
		docker_ready=1
	else
		printf 'FAIL Docker daemon unavailable\n'
		failures=$((failures + 1))
	fi

	if (( docker_ready == 1 )) && docker compose version >/dev/null 2>&1; then
		printf 'OK   Docker Compose\n'
		compose_ready=1
	else
		printf 'FAIL Docker Compose unavailable\n'
		failures=$((failures + 1))
	fi
	if (( docker_ready == 1 )) && ! (verify_project_checkout); then
		return 1
	fi

	if [[ ! -f "$ENV_FILE" ]]; then
		printf 'FAIL config missing: %s\n' "$ENV_FILE"
		failures=$((failures + 1))
	else
		printf 'OK   config exists: %s\n' "$ENV_FILE"
		if config_permissions_safe; then
			printf 'OK   config permissions\n'
		else
			printf 'FAIL config permissions; restrict Unix mode or Windows ACL: %s\n' "$ENV_FILE"
			failures=$((failures + 1))
		fi

		for key in DIRECTUS_IMAGE POSTGRES_IMAGE SCHEMATHESIS_IMAGE DB_DATABASE DB_USER DB_PASSWORD DIRECTUS_KEY DIRECTUS_SECRET ADMIN_EMAIL ADMIN_PASSWORD; do
			if config_has_key "$key"; then
				printf 'OK   config key %-18s present\n' "$key"
			else
				printf 'FAIL config key %-18s missing\n' "$key"
				failures=$((failures + 1))
			fi
		done

		for key in EDITOR_EMAIL EDITOR_PASSWORD READER_EMAIL READER_PASSWORD; do
			if config_has_key "$key"; then
				case "$(config_value "$key")" in
					''|REPLACE_*)
						printf 'INFO actor key %-18s is still a placeholder\n' "$key"
						;;
					*)
						printf 'OK   actor key %-18s present\n' "$key"
						;;
				esac
			else
				printf 'INFO actor key %-18s missing; seed/suites will require it\n' "$key"
			fi
		done

		if config_has_key LICENSE_KEY; then
			case "$(config_value LICENSE_KEY)" in
				''|REPLACE_*)
					printf 'INFO license key is not configured; Reader custom rules may remain disabled\n'
					;;
				*)
					printf 'OK   license key configured (value redacted)\n'
					;;
			esac
		else
			printf 'INFO license key config key missing; Directus will use its default entitlement\n'
		fi

		for key in DB_PASSWORD DIRECTUS_KEY DIRECTUS_SECRET ADMIN_PASSWORD; do
			case "$(config_value "$key")" in
				''|REPLACE_*)
					printf 'FAIL config key %-18s still uses placeholder\n' "$key"
					failures=$((failures + 1))
					;;
			esac
		done

		if (( compose_ready == 1 )) && compose config --quiet >/dev/null 2>&1; then
			printf 'OK   compose config\n'
		elif (( compose_ready == 0 )); then
			printf 'SKIP compose config (Docker Compose unavailable)\n'
		else
			printf 'FAIL compose config\n'
			failures=$((failures + 1))
		fi

		local compose_images
		if (( compose_ready == 1 )) && compose_images="$(compose config --images 2>/dev/null)"; then
			while IFS= read -r image; do
				[[ -n "$image" ]] || continue
				if [[ "$image" != *@sha256:* ]]; then
					printf 'FAIL image is not digest-pinned: %s\n' "$image"
					failures=$((failures + 1))
				elif docker image inspect "$image" >/dev/null 2>&1; then
					printf 'OK   image present: %s\n' "$image"
				else
					printf 'FAIL image missing: %s\n' "$image"
					failures=$((failures + 1))
				fi
			done <<< "$compose_images"
		elif (( compose_ready == 0 )); then
			printf 'SKIP image inspection (Docker Compose unavailable)\n'
		else
			printf 'FAIL unable to render compose images\n'
			failures=$((failures + 1))
		fi

		image="$(config_value SCHEMATHESIS_IMAGE)"
		if (( docker_ready == 1 )) && [[ "$image" == *@sha256:* ]] && docker image inspect "$image" >/dev/null 2>&1; then
			printf 'OK   runner image present\n'
		elif (( docker_ready == 0 )); then
			printf 'SKIP runner image inspection (Docker unavailable)\n'
		else
			printf 'FAIL runner image missing; required before schema-smoke\n'
			failures=$((failures + 1))
		fi
	fi

	if (( compose_ready == 1 )) && lab_container_id="$(compose ps -q directus 2>/dev/null)"; then
		:
	else
		lab_container_id=""
	fi

	if [[ -f "$RUNTIME_ROOT/fixture-ids.json" ]]; then
		if command -v jq >/dev/null 2>&1 && jq -e '
			.schema == 1
			and (.fixture_version | type == "string" and length > 0)
			and (.fixtures | type == "object")
			and all(.fixtures[]; type == "object")
			and all(.fixtures[] | to_entries[]; .value | (type == "number" and floor == . and . > 0))
		' "$RUNTIME_ROOT/fixture-ids.json" >/dev/null 2>&1; then
			printf 'OK   fixture ID map\n'
		else
			printf 'FAIL fixture ID map is not valid: %s\n' "$RUNTIME_ROOT/fixture-ids.json"
			failures=$((failures + 1))
		fi
	else
		printf 'INFO fixture ID map not present; seed has not completed\n'
	fi

	if (( api_url_allowed == 0 )); then
		printf 'SKIP API liveness (URL is outside the approved lab endpoint)\n'
	elif ! command -v curl >/dev/null 2>&1; then
		printf 'SKIP API liveness (curl unavailable)\n'
	elif api_status="$(curl -fsS --max-time 1 -o /dev/null -w '%{http_code}' "$API_URL/server/ping" 2>/dev/null)" && [[ "$api_status" == 200 ]]; then
		if [[ -z "$lab_container_id" ]]; then
			printf 'FAIL API URL responds, but r06-k05 Directus container is absent\n'
			failures=$((failures + 1))
		elif lab_container_state="$(docker inspect --format '{{.State.Status}}' "$lab_container_id" 2>/dev/null)" && [[ "$lab_container_state" == running ]]; then
			printf 'INFO API liveness already responds 200 from r06-k05\n'
		else
			printf 'FAIL API URL responds, but r06-k05 Directus container is not running\n'
			failures=$((failures + 1))
		fi
		if [[ -z "$lab_container_id" || "$lab_container_state" != running ]]; then
			printf 'SKIP authenticated health (r06-k05 Directus container is not running)\n'
		elif [[ -z "$(config_value ADMIN_EMAIL 2>/dev/null || true)" || -z "$(config_value ADMIN_PASSWORD 2>/dev/null || true)" ]]; then
			printf 'INFO authenticated health skipped; admin credential keys are missing\n'
		else
			if admin_authenticated_health 2>/dev/null; then
				printf 'OK   Directus authenticated health\n'
				if license_summary="$(admin_license_summary 2>/dev/null)"; then
					printf 'INFO Directus license %s\n' "$license_summary"
				else
					printf 'INFO Directus license probe unavailable\n'
				fi
			else
				printf 'FAIL Directus authenticated health\n'
				failures=$((failures + 1))
			fi
		fi
	else
		printf 'INFO API liveness not responding; this is expected before ./lab.sh up\n'
	fi

	if (( failures > 0 )); then
		printf 'Doctor: FAIL (%d check(s))\n' "$failures"
		return 1
	fi
	printf 'Doctor: PASS\n'
}

wait_for_health() {
	local container_id
	local health
	local attempt

	for attempt in {1..30}; do
		if container_id="$(compose ps -q directus 2>/dev/null)"; then
			:
		else
			container_id=""
		fi
		if [[ -n "$container_id" ]]; then
			if health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id" 2>/dev/null)"; then
				:
			else
				health=""
			fi
			if [[ "$health" == healthy ]]; then
				printf 'API liveness: healthy\n'
				return 0
			fi
			printf 'Waiting for Directus (%s/30): %s\n' "$attempt" "${health:-unknown}"
		else
			printf 'Waiting for Directus (%s/30): container not created\n' "$attempt"
		fi
		sleep 2
	done

	compose ps
	return 1
}

up() {
	require_config
	require_docker
	compose config --quiet
	compose up -d
	wait_for_health
}

down() {
	require_config
	require_docker
	compose --profile docs down
}

swagger() {
	local action="$1"
	local fixture_version configured_version directus_container swagger_spec_dir served_file actor attempt ready
	local SWAGGER_SPEC_DIR

	require_config
	require_docker
	if [[ "$action" == down ]]; then
		compose --profile docs stop swagger-ui
		printf 'Swagger UI đã dừng; các service lab và database vẫn chạy.\n'
		return 0
	fi

	[[ "$API_URL" == "$DEFAULT_API_URL" ]] || die 'Swagger yêu cầu API_URL=http://127.0.0.1:8055.'
	verify_compose_target
	directus_container="$(compose ps -q directus)"
	docker inspect "$directus_container" | jq -e '
		.[0].Config.Env
		| (index("CORS_ENABLED=true") != null)
		  and (index("CORS_ORIGIN=http://127.0.0.1:8086") != null)
		  and (index("CORS_CREDENTIALS=false") != null)
	' >/dev/null || die 'Directus đang chạy chưa có CORS cho Swagger; áp dụng Compose mới cho riêng service directus.'
	[[ -f "$RUNTIME_ROOT/fixture-ids.json" ]] || die 'Thiếu fixture ID map; chạy ./lab.sh seed trước.'
	fixture_version="$(jq -er '.fixture_version | select(type == "string" and length > 0)' "$RUNTIME_ROOT/fixture-ids.json")" || die 'Fixture ID map không có version hợp lệ.'
	[[ "$fixture_version" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'Fixture version không hợp lệ cho đường dẫn Swagger.'
	configured_version="${LAB_FIXTURE_VERSION:-$(config_value_or_default LAB_FIXTURE_VERSION 'r06-k05-v2')}"
	[[ "$fixture_version" == "$configured_version" ]] || die 'Fixture version trong map khác cấu hình lab.'
	swagger_spec_dir="$RUNTIME_ROOT/swagger/$fixture_version"
	bash "$ROOT_DIR/scripts/swagger-spec.sh" \
		"$RUNTIME_ROOT/schemas/$fixture_version" "$swagger_spec_dir" "$RUN_DIR" "$fixture_version" "$DEFAULT_API_URL"
	SWAGGER_SPEC_DIR="$swagger_spec_dir"
	case "$(uname -s)" in
		MINGW*|MSYS*|CYGWIN*) SWAGGER_SPEC_DIR="$(cygpath -m "$swagger_spec_dir")" ;;
	esac
	export SWAGGER_SPEC_DIR
	compose --profile docs config --quiet
	compose --profile docs up -d --no-deps swagger-ui
	for actor in editor reader; do
		served_file="$RUN_DIR/swagger-served-$actor.json"
		ready=0
		for attempt in {1..10}; do
			if curl -fsS --max-time 3 -o "$served_file" "http://127.0.0.1:8086/specs/$actor.json" 2>/dev/null &&
				[[ "$(sha256sum "$served_file" | awk '{print $1}')" == "$(sha256sum "$swagger_spec_dir/$actor.json" | awk '{print $1}')" ]]; then
				ready=1
				break
			fi
			sleep 1
		done
		[[ "$ready" -eq 1 ]] || die "Swagger không phục vụ đúng schema $actor tại 127.0.0.1:8086."
	done
	printf 'Swagger UI: http://127.0.0.1:8086\n'
	printf 'Dùng /auth/login của từng actor, sau đó nhập Bearer <access_token> trong Authorize.\n'
}

run_component() {
	local profile="$1"
	shift
	local component_script="$ROOT_DIR/scripts/lab-components.sh"
	local admin_email
	local admin_password
	local editor_email
	local editor_password
	local reader_email
	local reader_password
	local schemathesis_image
	local campaign_seeds
	local max_time
	local max_examples
	local workers
	local rate_limit
	local request_timeout

	require_config
	require_docker
	verify_compose_target
	[[ -f "$component_script" ]] || die "Thiếu component script: $component_script"
	admin_email="$(config_value ADMIN_EMAIL 2>/dev/null || true)"
	admin_password="$(config_value ADMIN_PASSWORD 2>/dev/null || true)"
	editor_email="$(config_value EDITOR_EMAIL 2>/dev/null || true)"
	editor_password="$(config_value EDITOR_PASSWORD 2>/dev/null || true)"
	reader_email="$(config_value READER_EMAIL 2>/dev/null || true)"
	reader_password="$(config_value READER_PASSWORD 2>/dev/null || true)"
	schemathesis_image="$(config_value SCHEMATHESIS_IMAGE 2>/dev/null || true)"
	campaign_seeds="${LAB_CAMPAIGN_SEEDS:-$(config_value_or_default LAB_CAMPAIGN_SEEDS '101,202,303')}"
	max_time="${LAB_MAX_TIME:-$(config_value_or_default LAB_MAX_TIME '1200')}"
	max_examples="${LAB_MAX_EXAMPLES:-$(config_value_or_default LAB_MAX_EXAMPLES '100')}"
	workers="${LAB_WORKERS:-$(config_value_or_default LAB_WORKERS '1')}"
	rate_limit="${LAB_RATE_LIMIT:-$(config_value_or_default LAB_RATE_LIMIT '5/s')}"
	request_timeout="${LAB_REQUEST_TIMEOUT:-$(config_value_or_default LAB_REQUEST_TIMEOUT '10')}"

	env \
		LAB_ROOT_DIR="$ROOT_DIR" \
		LAB_RUN_DIR="$RUN_DIR" \
		LAB_RUNTIME_ROOT="$RUNTIME_ROOT" \
		LAB_API_URL="$API_URL" \
		LAB_RUNNER_API_URL="$RUNNER_API_URL" \
		LAB_PROJECT_NAME="$PROJECT_NAME" \
		LAB_NETWORK_NAME="${PROJECT_NAME}_network" \
		LAB_RUN_ID="$RUN_ID" \
		LAB_FIXTURE_VERSION="${LAB_FIXTURE_VERSION:-$(config_value_or_default LAB_FIXTURE_VERSION 'r06-k05-v2')}" \
		LAB_ADMIN_EMAIL="$admin_email" \
		LAB_ADMIN_PASSWORD="$admin_password" \
		LAB_EDITOR_EMAIL="$editor_email" \
		LAB_EDITOR_PASSWORD="$editor_password" \
		LAB_READER_EMAIL="$reader_email" \
		LAB_READER_PASSWORD="$reader_password" \
		LAB_SCHEMATHESIS_IMAGE="$schemathesis_image" \
			LAB_CAMPAIGN_SEEDS="$campaign_seeds" \
			LAB_MAX_TIME="$max_time" \
			LAB_MAX_EXAMPLES="$max_examples" \
			LAB_WORKERS="$workers" \
			LAB_RATE_LIMIT="$rate_limit" \
			LAB_REQUEST_TIMEOUT="$request_timeout" \
		bash "$component_script" "$profile" "$@"
}

reset_lab() {
	local expected_volume="${PROJECT_NAME}_db_data"
	local configured_volume
	local volume_project
	local volume_kind

	require_config
	require_docker
	configured_volume="$(compose config --format json | jq -r '.volumes.db_data.name // empty')"
	[[ "$configured_volume" == "$expected_volume" ]] || die "Compose volume không đúng baseline: ${configured_volume:-<trống>}"
	if docker volume inspect "$expected_volume" >/dev/null 2>&1; then
		volume_project="$(docker volume inspect --format '{{index .Labels "com.docker.compose.project"}}' "$expected_volume")"
		volume_kind="$(docker volume inspect --format '{{index .Labels "com.docker.compose.volume"}}' "$expected_volume")"
		[[ "$volume_project" == "$PROJECT_NAME" && "$volume_kind" == 'db_data' ]] || die 'Volume tồn tại nhưng label không thuộc r06-k05; dừng để bảo vệ dữ liệu.'
	fi

	compose --profile docs down
	if docker volume inspect "$expected_volume" >/dev/null 2>&1; then
		docker volume rm "$expected_volume"
	fi
	if [[ -d "$RUNTIME_ROOT" ]]; then
		find "$RUNTIME_ROOT" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
	fi
	printf 'Reset: đã xóa volume %s và runtime artefact của lab r06-k05.\n' "$expected_volume"
}

dispatch() {
	local command_name="$1"
	shift
	case "$command_name" in
		seed|smoke|export-schema|schema-smoke|scenarios|invariants|designed|cost-query|raw|guided)
			run_component "$command_name" "$@"
			;;
		replay)
			[[ $# -eq 1 ]] || die 'replay cần một case-id.'
			run_component replay "$1"
			;;
		reset)
			reset_lab
			;;
		*)
			usage >&2
			return 2
			;;
	esac
}

main() {
	local command_name="${1:-}"
	local run_command=""

	case "$command_name" in
		help|-h|--help)
			usage
			return 0
			;;
		doctor|up|down|seed|smoke|export-schema|reset)
			run_command="$command_name"
			;;
		swagger)
			[[ $# -eq 2 && ( "$2" == up || "$2" == down ) ]] || die 'swagger cần up hoặc down.'
			run_command="swagger $2"
			;;
		test)
			if [[ $# -eq 2 && ( "$2" == 'help' || "$2" == '-h' || "$2" == '--help' ) ]]; then
				usage
				return 0
			fi
			[[ $# -ge 2 ]] || die 'test cần một profile.'
			[[ $# -eq 2 || "$2" == designed || "$2" == cost-query ]] || die 'Chỉ test designed/cost-query nhận tùy chọn bổ sung.'
			run_command="test $2"
			;;
		replay)
			[[ $# -eq 2 ]] || die 'replay cần một case-id.'
			run_command="replay $2"
			;;
		'')
			usage >&2
			return 2
			;;
		*)
			usage >&2
			return 2
			;;
	esac

	# The pilot always uses the editor token. Record that actor in run metadata
	# instead of leaving a successful component invocation as "unspecified".
	if [[ "$run_command" == 'test schema-smoke' || "$run_command" == 'test raw' || "$run_command" == 'test guided' || "$run_command" == 'test cost-query' ]]; then
		case "${LAB_ACTOR:-unspecified}" in
			unspecified|editor) LAB_ACTOR=editor ;;
			*) die 'test schema-smoke/raw/guided cố định actor editor; không được gắn actor khác vào metadata.' ;;
		esac
	fi

	begin_run "$run_command"
	trap 'finish_run "$?"' EXIT
	if [[ "$command_name" != doctor ]]; then acquire_lab_lock || return 1; fi

	case "$command_name" in
		doctor)
			doctor
			;;
		up)
			up
			;;
		down)
			down
			;;
		swagger)
			swagger "$2"
			;;
		seed|smoke|export-schema|reset)
			dispatch "$command_name"
			;;
		test)
			shift
			dispatch "$@"
			;;
		replay)
			dispatch replay "$2"
			;;
		'')
			usage >&2
			return 2
			;;
		*)
			usage >&2
			return 2
			;;
	esac
}

main "$@"
