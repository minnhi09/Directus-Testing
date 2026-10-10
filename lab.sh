#!/usr/bin/env bash

set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
COMPOSE_FILE="$ROOT_DIR/compose.yaml"
ENV_FILE="$ROOT_DIR/config/lab.env"
PROJECT_NAME="r06-k05"
API_URL="http://127.0.0.1:8055"

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
  ./lab.sh test schema-smoke|scenarios|raw|guided
  ./lab.sh replay <case-id>
  ./lab.sh reset
EOF
}

compose() {
	docker compose \
		--project-name "$PROJECT_NAME" \
		--env-file "$ENV_FILE" \
		--file "$COMPOSE_FILE" \
		"$@"
}

config_has_key() {
	local key="$1"
	[[ -f "$ENV_FILE" ]] && awk -F= -v key="$key" '$1 == key { found = 1 } END { exit(found ? 0 : 1) }' "$ENV_FILE"
}

config_value() {
	local key="$1"
	awk -F= -v key="$key" '$1 == key { sub(/^[^=]*=/, ""); print; exit }' "$ENV_FILE"
}

require_config() {
	[[ -f "$ENV_FILE" ]] || die "Thiếu $ENV_FILE. Sao chép config/lab.env.example và điền giá trị cục bộ."
	[[ "$(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE")" =~ ^6?00$|^400$|^600$ ]] || die "$ENV_FILE phải chỉ cho owner đọc/ghi (chmod 600)."
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

doctor() {
	local failures=0
	local key
	local image
	local api_status
	local lab_container_id
	local lab_container_state

	printf 'Lab: %s\n' "$PROJECT_NAME"
	printf 'Root: %s\n' "$ROOT_DIR"

	for key in docker curl jq; do
		check_command "$key" || failures=$((failures + 1))
	done

	if docker info >/dev/null 2>&1; then
		printf 'OK   Docker daemon\n'
	else
		printf 'FAIL Docker daemon unavailable\n'
		failures=$((failures + 1))
	fi

	if docker compose version >/dev/null 2>&1; then
		printf 'OK   Docker Compose\n'
	else
		printf 'FAIL Docker Compose unavailable\n'
		failures=$((failures + 1))
	fi

	if [[ ! -f "$ENV_FILE" ]]; then
		printf 'FAIL config missing: %s\n' "$ENV_FILE"
		failures=$((failures + 1))
	else
		printf 'OK   config exists: %s\n' "$ENV_FILE"
		if [[ "$(stat -c '%a' "$ENV_FILE" 2>/dev/null || stat -f '%Lp' "$ENV_FILE")" =~ ^6?00$|^400$|^600$ ]]; then
			printf 'OK   config permissions\n'
		else
			printf 'FAIL config permissions; use chmod 600 %s\n' "$ENV_FILE"
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

		for key in DB_PASSWORD DIRECTUS_KEY DIRECTUS_SECRET ADMIN_PASSWORD; do
			case "$(config_value "$key")" in
				''|REPLACE_*)
					printf 'FAIL config key %-18s still uses placeholder\n' "$key"
					failures=$((failures + 1))
					;;
			esac
		done

		if compose config --quiet >/dev/null 2>&1; then
			printf 'OK   compose config\n'
		else
			printf 'FAIL compose config\n'
			failures=$((failures + 1))
		fi

		local compose_images
		if compose_images="$(compose config --images 2>/dev/null)"; then
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
		else
			printf 'FAIL unable to render compose images\n'
			failures=$((failures + 1))
		fi

		image="$(config_value SCHEMATHESIS_IMAGE)"
		if [[ "$image" == *@sha256:* ]] && docker image inspect "$image" >/dev/null 2>&1; then
			printf 'OK   runner image present\n'
		else
			printf 'FAIL runner image missing; required before schema-smoke\n'
			failures=$((failures + 1))
		fi
	fi

	if lab_container_id="$(compose ps -q directus 2>/dev/null)"; then
		:
	else
		lab_container_id=""
	fi

	if api_status="$(curl -fsS --max-time 1 -o /dev/null -w '%{http_code}' "$API_URL/server/ping" 2>/dev/null)" && [[ "$api_status" == 200 ]]; then
		if [[ -z "$lab_container_id" ]]; then
			printf 'FAIL API URL responds, but r06-k05 Directus container is absent\n'
			failures=$((failures + 1))
		elif lab_container_state="$(docker inspect --format '{{.State.Status}}' "$lab_container_id" 2>/dev/null)" && [[ "$lab_container_state" == running ]]; then
			printf 'INFO API liveness already responds 200 from r06-k05\n'
		else
			printf 'FAIL API URL responds, but r06-k05 Directus container is not running\n'
			failures=$((failures + 1))
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
	compose config --quiet
	compose up -d
	wait_for_health
}

down() {
	require_config
	compose down
}

unimplemented() {
	local name="$1"
	printf 'Chưa triển khai: %s. Chủ sở hữu theo G0 phải tích hợp phần bàn giao trước khi chạy lệnh này.\n' "$name" >&2
	return 2
}

dispatch() {
	local command_name="$1"
	shift
	case "$command_name" in
		seed|smoke|export-schema)
			unimplemented "$command_name"
			;;
		schema-smoke|scenarios|raw|guided)
			unimplemented "test $command_name"
			;;
		replay)
			[[ $# -eq 1 ]] || die 'replay cần một case-id.'
			unimplemented "replay $1"
			;;
		reset)
			unimplemented reset
			;;
		*)
			usage >&2
			return 2
			;;
	esac
}

main() {
	local command_name="${1:-}"

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
		seed|smoke|export-schema|reset)
			dispatch "$command_name"
			;;
		test)
			[[ $# -eq 2 ]] || die 'test cần một profile.'
			dispatch "$2"
			;;
		replay)
			shift
			dispatch replay "$@"
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
