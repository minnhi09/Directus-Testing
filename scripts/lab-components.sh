#!/usr/bin/env bash

# Temporary G1 implementation used by lab.sh. All credentials arrive through
# the parent process and are never written into reports.
set -Eeuo pipefail

RUN_DIR="$LAB_RUN_DIR"
RUNTIME_ROOT="$LAB_RUNTIME_ROOT"
API_URL="$LAB_API_URL"
RUNNER_API_URL="$LAB_RUNNER_API_URL"
PROJECT_NAME="$LAB_PROJECT_NAME"
NETWORK_NAME="$LAB_NETWORK_NAME"
ADMIN_EMAIL="$LAB_ADMIN_EMAIL"
ADMIN_PASSWORD="$LAB_ADMIN_PASSWORD"
EDITOR_EMAIL="$LAB_EDITOR_EMAIL"
EDITOR_PASSWORD="$LAB_EDITOR_PASSWORD"
READER_EMAIL="$LAB_READER_EMAIL"
READER_PASSWORD="$LAB_READER_PASSWORD"
SCHEMATHESIS_IMAGE="$LAB_SCHEMATHESIS_IMAGE"
RUN_ID="$LAB_RUN_ID"
FIXTURE_VERSION="$LAB_FIXTURE_VERSION"
[[ -n "$FIXTURE_VERSION" ]] || FIXTURE_VERSION='r06-k05-v1'
SCHEMA_ROOT="$RUNTIME_ROOT/schemas/$FIXTURE_VERSION"
FIXTURE_MAP="$RUNTIME_ROOT/fixture-ids.json"

API_STATUS=''
API_BODY=''
API_CURL_RC=0
HTTP_COUNTER=0
ADMIN_TOKEN=''
EDITOR_TOKEN=''
READER_TOKEN=''

fail() {
	printf 'ERROR: %s\n' "$*" >&2
	return 1
}

require_tools() {
	local command_name
	for command_name in curl jq docker; do
		command -v "$command_name" >/dev/null 2>&1 || {
			printf 'ERROR: thiếu command %s\n' "$command_name" >&2
			return 1
		}
	done
}

valid_http_success() {
	[[ "$1" =~ ^2[0-9][0-9]$ ]]
}

http_summary() {
	local body_file="$1"
	if [[ -s "$body_file" ]]; then
		jq -c 'if (.errors? // null) != null then {errors:(.errors|map({code:(.extensions.code // .code // null),message:(.message // null)}))} elif (.data? // null) != null then {data_type:(.data|type)} else {keys:(keys|sort)} end' "$body_file" 2>/dev/null || printf '{"body":"invalid_json"}'
	else
		printf '{"body":"empty"}'
	fi
}

api_request() {
	local method="$1"
	local path="$2"
	local token=''
	local body=''
	local response_file
	local http_status
	local curl_rc
	[[ "$#" -ge 3 ]] && token="$3"
	[[ "$#" -ge 4 ]] && body="$4"

	HTTP_COUNTER=$((HTTP_COUNTER + 1))
	response_file="$RUN_DIR/http-$HTTP_COUNTER.json"
	local -a args
	args=(-sS --globoff --max-time 10 -o "$response_file" -w '%{http_code}' -X "$method")
	[[ -n "$token" ]] && args+=(-H "Authorization: Bearer $token")
	if [[ -n "$body" ]]; then
		args+=(-H 'Content-Type: application/json' --data-binary "$body")
	fi

	set +e
	http_status="$(curl "${args[@]}" "$API_URL$path")"
	curl_rc=$?
	set -e
	API_STATUS="$http_status"
	API_BODY="$response_file"
	API_CURL_RC="$curl_rc"
	if (( curl_rc != 0 )); then
		printf 'API request failed: %s %s (curl=%s)\n' "$method" "$path" "$curl_rc" >&2
		return 1
	fi
	return 0
}

api_expect_2xx() {
	local context="$1"
	shift
	api_request "$@" || {
		printf 'FAIL %s: network error\n' "$context" >&2
		return 1
	}
	if ! valid_http_success "$API_STATUS"; then
		printf 'FAIL %s: HTTP %s %s\n' "$context" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	fi
	return 0
}

login() {
	local email="$1"
	local password="$2"
	local response
	local token
	[[ -n "$email" && -n "$password" ]] || return 1
	response="$(
		jq -n --arg email "$email" --arg password "$password" '{email:$email,password:$password}' |
			curl -fsS --max-time 10 -H 'Content-Type: application/json' --data-binary @- "$API_URL/auth/login"
	)" || return 1
	token="$(printf '%s' "$response" | jq -r '.data.access_token // empty' 2>/dev/null || true)"
	[[ -n "$token" && "$token" != "null" ]] || return 1
	printf '%s' "$token"
}

require_admin_login() {
	ADMIN_TOKEN="$(login "$ADMIN_EMAIL" "$ADMIN_PASSWORD")" || {
		printf 'ERROR: admin login thất bại\n' >&2
		return 1
	}
}

require_actor_logins() {
	[[ -n "$EDITOR_EMAIL" && -n "$EDITOR_PASSWORD" && -n "$READER_EMAIL" && -n "$READER_PASSWORD" ]] || {
		printf 'ERROR: thiếu EDITOR_* hoặc READER_* trong config/lab.env\n' >&2
		return 1
	}
	EDITOR_TOKEN="$(login "$EDITOR_EMAIL" "$EDITOR_PASSWORD")" || {
		printf 'ERROR: editor login thất bại\n' >&2
		return 1
	}
	READER_TOKEN="$(login "$READER_EMAIL" "$READER_PASSWORD")" || {
		printf 'ERROR: reader login thất bại\n' >&2
		return 1
	}
}

ensure_collection() {
	local collection="$1"
	local note="$2"
	local collections_json="$3"
	local count body
	count="$(jq -r --arg collection "$collection" '[.[] | select(.collection == $collection)] | length' <<< "$collections_json")"
	if [[ "$count" -gt 1 ]]; then
		printf 'ERROR: collection %s xuất hiện nhiều hơn một lần\n' "$collection" >&2
		return 1
	elif [[ "$count" -eq 1 ]]; then
		jq -e --arg collection "$collection" '
			.[]
			| select(.collection == $collection)
			| (.schema.name == $collection and (.meta.status // "active") == "active")
		' <<< "$collections_json" >/dev/null || {
			printf 'ERROR: collection %s không tương thích\n' "$collection" >&2
			return 1
		}
		printf 'Schema collection đã có: %s\n' "$collection"
		return 0
	fi
	body="$(jq -cn --arg collection "$collection" --arg note "$note" '{collection:$collection,meta:{icon:"database",note:$note},schema:{}}')"
	api_expect_2xx "tạo collection $collection" POST '/collections' "$ADMIN_TOKEN" "$body" || return 1
	printf 'Schema collection đã tạo: %s\n' "$collection"
}

field_compatible() {
	local body_file="$1"
	local spec="$2"
	local field="$3"
	jq -e --argjson spec "$spec" --arg field "$field" '
		.data[]
		| select(.field == $field)
		| .type == $spec.type
		and (($spec.schema | has("is_nullable") | not) or .schema.is_nullable == $spec.schema.is_nullable)
		and (($spec.schema.max_length == null) or .schema.max_length == $spec.schema.max_length)
		and (($spec.schema.default_value == null) or .schema.default_value == $spec.schema.default_value)
		and (($spec.meta.required == null) or .meta.required == $spec.meta.required)
		and (($spec.meta.validation == null) or .meta.validation == $spec.meta.validation)
	' "$body_file" >/dev/null
}

ensure_field() {
	local collection="$1"
	local spec="$2"
	local field response count
	field="$(jq -r '.field' <<< "$spec")"
	api_request GET "/fields/$collection" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc field %s.%s thất bại HTTP %s %s\n' "$collection" "$field" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	response="$API_BODY"
	count="$(jq -r --arg field "$field" '[.data[] | select(.field == $field)] | length' "$response")"
	if [[ "$count" -gt 1 ]]; then
		printf 'ERROR: field %s.%s xuất hiện nhiều lần\n' "$collection" "$field" >&2
		return 1
	elif [[ "$count" -eq 1 ]]; then
		field_compatible "$response" "$spec" "$field" || {
			printf 'ERROR: field %s.%s không tương thích\n' "$collection" "$field" >&2
			return 1
		}
		printf 'Schema field đã có: %s.%s\n' "$collection" "$field"
		return 0
	fi
	api_expect_2xx "tạo field $collection.$field" POST "/fields/$collection" "$ADMIN_TOKEN" "$spec" || return 1
	printf 'Schema field đã tạo: %s.%s\n' "$collection" "$field"
}

ensure_primary_id() {
	local collection="$1"
	api_request GET "/fields/$collection" "$ADMIN_TOKEN" || return 1
	if ! valid_http_success "$API_STATUS"; then
		printf 'ERROR: không đọc được field của %s\n' "$collection" >&2
		return 1
	fi
	if ! jq -e '
		.data as $fields
		| ($fields | map(select(.field == "id"))) as $ids
		| ($ids|length) == 1
		and $ids[0].type == "integer"
		and $ids[0].schema.is_primary_key == true
		and $ids[0].schema.has_auto_increment == true
		and $ids[0].schema.is_nullable == false
	' "$API_BODY" >/dev/null; then
		printf 'ERROR: primary id của %s không đúng contract\n' "$collection" >&2
		return 1
	fi
}

ensure_relation() {
	local relation
	api_expect_2xx 'đọc relations' GET '/relations?limit=-1&fields=collection,field,related_collection,schema,meta' "$ADMIN_TOKEN" || return 1
	relation="$(jq -c '[.data[] | select(.collection == "qa_articles" and .field == "category")]' "$API_BODY")"
	if [[ "$(jq -r 'length' <<< "$relation")" -gt 1 ]]; then
		printf 'ERROR: qa_articles.category có nhiều relation\n' >&2
		return 1
	elif [[ "$(jq -r 'length' <<< "$relation")" -eq 1 ]]; then
		jq -e '
			.[0].related_collection == "qa_categories"
			and ((.[0].schema.on_delete // .[0].schema.onDelete // "SET NULL") == "SET NULL")
		' <<< "$relation" >/dev/null || {
			printf 'ERROR: relation qa_articles.category không tương thích\n' >&2
			return 1
		}
		printf 'Schema relation đã có: qa_articles.category -> qa_categories\n'
		return 0
	fi
	relation='{"collection":"qa_articles","field":"category","related_collection":"qa_categories","schema":{"on_delete":"SET NULL"},"meta":{"one_field":"articles","one_deselect_action":"nullify"}}'
	api_expect_2xx 'tạo relation qa_articles.category' POST '/relations' "$ADMIN_TOKEN" "$relation" || return 1
	printf 'Schema relation đã tạo: qa_articles.category -> qa_categories\n'
}

ensure_schema() {
	local collections_json status_validation score_validation
	api_expect_2xx 'đọc collections' GET '/collections?limit=-1&fields=collection,schema,meta' "$ADMIN_TOKEN" || return 1
	collections_json="$(jq -c '.data' "$API_BODY")"
	ensure_collection qa_categories 'K05 fixture categories' "$collections_json" || return 1
	ensure_collection qa_articles 'K05 fixture articles' "$collections_json" || return 1
	ensure_primary_id qa_categories || return 1
	ensure_primary_id qa_articles || return 1
	ensure_field qa_categories '{"field":"name","type":"string","schema":{"is_nullable":false,"max_length":80},"meta":{"interface":"input","required":true,"width":"full"}}' || return 1
	status_validation='{"status":{"_in":["draft","published"]}}'
	score_validation='{"score":{"_gte":0,"_lte":5}}'
	ensure_field qa_articles '{"field":"title","type":"string","schema":{"is_nullable":false,"max_length":120},"meta":{"interface":"input","required":true,"width":"full"}}' || return 1
	ensure_field qa_articles "$(jq -cn --argjson validation "$status_validation" '{field:"status",type:"string",schema:{is_nullable:false,max_length:16,default_value:"draft"},meta:{interface:"select-dropdown",required:true,width:"half",validation:$validation}}')" || return 1
	ensure_field qa_articles "$(jq -cn --argjson validation "$score_validation" '{field:"score",type:"integer",schema:{is_nullable:false},meta:{interface:"input",required:true,width:"half",validation:$validation}}')" || return 1
	ensure_field qa_articles '{"field":"published_at","type":"timestamp","schema":{"is_nullable":true},"meta":{"interface":"datetime","required":false,"width":"half"}}' || return 1
	ensure_field qa_articles '{"field":"metadata","type":"json","schema":{"is_nullable":true},"meta":{"interface":"input-code","required":false,"width":"full"}}' || return 1
	ensure_field qa_articles '{"field":"internal_notes","type":"text","schema":{"is_nullable":true},"meta":{"interface":"input-multiline","required":false,"width":"full"}}' || return 1
	ensure_field qa_articles '{"field":"category","type":"integer","schema":{"is_nullable":true},"meta":{"interface":"select-dropdown-m2o","required":false,"width":"half"}}' || return 1
	ensure_relation || return 1
	printf 'Schema fixture: PASS\n'
}

role_id_by_name() {
	local name="$1"
	local encoded
	local count
	encoded="$(printf '%s' "$name" | jq -sRr @uri)"
	api_request GET "/roles?filter[name][_eq]=$encoded&fields=id,name" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc role %s thất bại HTTP %s %s\n' "$name" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	count="$(jq -r '.data|length' "$API_BODY")"
	[[ "$count" -le 1 ]] || {
		printf 'ERROR: role %s xuất hiện nhiều lần\n' "$name" >&2
		return 1
	}
	if [[ "$count" -eq 1 ]]; then
		jq -r '.data[0].id' "$API_BODY"
	else
		printf ''
	fi
}

ensure_role() {
	local name="$1"
	local icon="$2"
	local role_id
	local body
	role_id="$(role_id_by_name "$name")"
	if [[ -n "$role_id" ]]; then
		printf '%s' "$role_id"
		return 0
	fi
	body="$(jq -cn --arg name "$name" --arg icon "$icon" '{name:$name,icon:$icon,description:"R06/K05 lab actor role",parent:null}')"
	api_expect_2xx "tạo role $name" POST '/roles' "$ADMIN_TOKEN" "$body" || return 1
	role_id="$(jq -r '.data.id // empty' "$API_BODY")"
	[[ -n "$role_id" && "$role_id" != "null" ]] || {
		printf 'ERROR: Directus không trả role id cho %s\n' "$name" >&2
		return 1
	}
	printf '%s' "$role_id"
}

policy_id_by_name() {
	local name="$1"
	local encoded
	local count
	encoded="$(printf '%s' "$name" | jq -sRr @uri)"
	api_request GET "/policies?filter[name][_eq]=$encoded&fields=id,name,admin_access,app_access" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc policy %s thất bại HTTP %s %s\n' "$name" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	count="$(jq -r '.data|length' "$API_BODY")"
	[[ "$count" -le 1 ]] || {
		printf 'ERROR: policy %s xuất hiện nhiều lần\n' "$name" >&2
		return 1
	}
	if [[ "$count" -eq 1 ]]; then
		jq -e '.data[0].admin_access == false and .data[0].app_access == false' "$API_BODY" >/dev/null || {
			printf 'ERROR: policy %s có quyền global ngoài contract\n' "$name" >&2
			return 1
		}
		jq -r '.data[0].id' "$API_BODY"
	else
		printf ''
	fi
}

ensure_policy() {
	local name="$1"
	local policy_id
	local body
	policy_id="$(policy_id_by_name "$name")"
	if [[ -n "$policy_id" ]]; then
		printf '%s' "$policy_id"
		return 0
	fi
	body="$(jq -cn --arg name "$name" '{name:$name,icon:"security",description:"R06/K05 lab API-only policy",admin_access:false,app_access:false}')"
	api_expect_2xx "tạo policy $name" POST '/policies' "$ADMIN_TOKEN" "$body" || return 1
	policy_id="$(jq -r '.data.id // empty' "$API_BODY")"
	[[ -n "$policy_id" && "$policy_id" != "null" ]] || {
		printf 'ERROR: Directus không trả policy id cho %s\n' "$name" >&2
		return 1
	}
	printf '%s' "$policy_id"
}

ensure_access() {
	local role_id="$1"
	local policy_id="$2"
	local body
	api_request GET "/access?filter[role][_eq]=$role_id&filter[policy][_eq]=$policy_id&fields=id,role,policy" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc access thất bại HTTP %s %s\n' "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	[[ "$(jq -r '.data|length' "$API_BODY")" -le 1 ]] || {
		printf 'ERROR: access role/policy bị trùng\n' >&2
		return 1
	}
	if [[ "$(jq -r '.data|length' "$API_BODY")" -eq 1 ]]; then
		return 0
	fi
	body="$(jq -cn --arg role "$role_id" --arg policy "$policy_id" '{role:$role,policy:$policy}')"
	api_expect_2xx 'gắn policy vào role' POST '/access' "$ADMIN_TOKEN" "$body" || return 1
}

permission_matches() {
	local body_file="$1"
	local expected="$2"
	jq -e --argjson expected "$expected" '
		.data[0].collection == $expected.collection
		and .data[0].action == $expected.action
		and .data[0].policy == $expected.policy
		and .data[0].fields == $expected.fields
		and ((.data[0].permissions // null) == ($expected.permissions // null))
		and ((.data[0].validation // null) == null)
	' "$body_file" >/dev/null
}

ensure_permission() {
	local policy_id="$1"
	local collection="$2"
	local action="$3"
	local fields_json="$4"
	local permissions_json="$5"
	local body
	local existing_count
	body="$(jq -cn --arg policy "$policy_id" --arg collection "$collection" --arg action "$action" --argjson fields "$fields_json" --argjson permissions "$permissions_json" '{policy:$policy,collection:$collection,action:$action,fields:$fields,permissions:$permissions,validation:null,presets:null}')"
	api_request GET "/permissions?filter[policy][_eq]=$policy_id&filter[collection][_eq]=$collection&filter[action][_eq]=$action&fields=id,policy,collection,action,fields,permissions,validation,presets" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc permission %s/%s/%s thất bại HTTP %s %s\n' "$policy_id" "$collection" "$action" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	existing_count="$(jq -r '.data|length' "$API_BODY")"
	[[ "$existing_count" -le 1 ]] || {
		printf 'ERROR: permission %s/%s/%s bị trùng\n' "$policy_id" "$collection" "$action" >&2
		return 1
	}
	if [[ "$existing_count" -eq 1 ]]; then
		permission_matches "$API_BODY" "$body" || {
			printf 'ERROR: permission %s/%s/%s không tương thích\n' "$policy_id" "$collection" "$action" >&2
			return 1
		}
		return 0
	fi
	api_expect_2xx "tạo permission $collection/$action" POST '/permissions' "$ADMIN_TOKEN" "$body" || return 1
}

require_custom_rules_license() {
	local entitled
	api_expect_2xx 'đọc trạng thái license' GET '/license' "$ADMIN_TOKEN" || return 1
	entitled="$(jq -r '
		.data.entitlements.custom_permission_rules_enabled
		| if has("override") and .override != null then .override else .default end
	' "$API_BODY")"
	if [[ "$entitled" != true ]]; then
		printf 'ERROR: Directus license không bật custom_permission_rules_enabled; không thể tạo filter/policy reader và không được bypass license\n' >&2
		return 1
	fi
}

ensure_user() {
	local email="$1"
	local password="$2"
	local role_id="$3"
	local display_name="$4"
	local user_id
	local body
	local encoded
	encoded="$(printf '%s' "$email" | jq -sRr @uri)"
	api_request GET "/users?filter[email][_eq]=$encoded&fields=id,email,role,status" "$ADMIN_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: đọc user %s thất bại HTTP %s %s\n' "$email" "$API_STATUS" "$(http_summary "$API_BODY")" >&2
		return 1
	}
	[[ "$(jq -r '.data|length' "$API_BODY")" -le 1 ]] || {
		printf 'ERROR: user %s xuất hiện nhiều lần\n' "$email" >&2
		return 1
	}
	body="$(jq -cn --arg email "$email" --arg password "$password" --arg role "$role_id" --arg name "$display_name" '{email:$email,password:$password,role:$role,status:"active",first_name:$name}')"
	if [[ "$(jq -r '.data|length' "$API_BODY")" -eq 1 ]]; then
		user_id="$(jq -r '.data[0].id' "$API_BODY")"
		jq -e --arg role "$role_id" '.data[0].role == $role and .data[0].status == "active"' "$API_BODY" >/dev/null || {
			printf 'ERROR: user %s không gắn đúng role hoặc không active\n' "$email" >&2
			return 1
		}
		if login "$email" "$password" >/dev/null 2>&1; then
			printf 'Actor đã có và đăng nhập được: %s\n' "$email"
			return 0
		fi
		api_expect_2xx "đồng bộ password actor $email" PATCH "/users/$user_id" "$ADMIN_TOKEN" "$(jq -cn --arg password "$password" '{password:$password,status:"active"}')" || return 1
		login "$email" "$password" >/dev/null 2>&1 || {
			printf 'ERROR: actor %s vẫn không đăng nhập được sau khi cập nhật password\n' "$email" >&2
			return 1
		}
		printf 'Actor đã có, password cục bộ đã đồng bộ: %s\n' "$email"
		return 0
	fi
	api_expect_2xx "tạo actor $email" POST '/users' "$ADMIN_TOKEN" "$body" || return 1
	user_id="$(jq -r '.data.id // empty' "$API_BODY")"
	[[ -n "$user_id" && "$user_id" != "null" ]] || {
		printf 'ERROR: Directus không trả user id cho %s\n' "$email" >&2
		return 1
	}
	login "$email" "$password" >/dev/null 2>&1 || {
		printf 'ERROR: actor %s tạo xong nhưng login thất bại\n' "$email" >&2
		return 1
	}
	printf 'Actor đã tạo: %s\n' "$email"
}

ensure_permissions_and_users() {
	local editor_role reader_role editor_policy reader_policy
	local article_fields='["id","title","status","score","published_at","metadata","category"]'
	editor_role="$(ensure_role 'R06 Editor' 'edit')"
	reader_role="$(ensure_role 'R06 Reader' 'visibility')"
	editor_policy="$(ensure_policy 'R06 Editor API Policy')"
	reader_policy="$(ensure_policy 'R06 Reader API Policy')"
	ensure_access "$editor_role" "$editor_policy" || return 1
	ensure_access "$reader_role" "$reader_policy" || return 1
	local collection action
	for collection in qa_categories qa_articles; do
		for action in create read update delete; do
			ensure_permission "$editor_policy" "$collection" "$action" '["*"]' 'null' || return 1
		done
	done
	ensure_permission "$reader_policy" qa_categories read '["*"]' 'null' || return 1
	ensure_user "$EDITOR_EMAIL" "$EDITOR_PASSWORD" "$editor_role" 'R06 Editor' || return 1
	ensure_user "$READER_EMAIL" "$READER_PASSWORD" "$reader_role" 'R06 Reader' || return 1
	require_custom_rules_license || return 1
	ensure_permission "$reader_policy" qa_articles read "$article_fields" '{"status":{"_eq":"published"}}' || return 1
	# Keep PATCH visible when Directus includes a permission with no writable
	# fields. The scenario sends a request only when the reader schema contains
	# the operation; otherwise it records a blocked precondition.
	ensure_permission "$reader_policy" qa_articles update '[]' 'null' || return 1
	printf 'Policy/actor fixture: PASS\n'
}

CATEGORY_KEYS='category_alpha category_beta category_gamma'
ARTICLE_KEYS='article_alpha_draft_1 article_alpha_draft_2 article_alpha_published_1 article_alpha_published_2 article_beta_draft_1 article_beta_draft_2 article_beta_published_1 article_beta_published_2 article_gamma_draft_1 article_gamma_draft_2 article_gamma_published_1 article_gamma_published_2'
CATEGORY_MAP_JSON='{}'
ARTICLE_MAP_JSON='{}'

category_spec() {
	local key="$1"
	case "$key" in
		category_alpha) printf '%s' '{"name":"Danh mục Alpha — Unicode"}' ;;
		category_beta) printf '%s' '{"name":"Danh mục Beta / Kiểm thử"}' ;;
		category_gamma) printf '%s' '{"name":"Danh mục Gamma"}' ;;
		*) return 1 ;;
	esac
}

article_spec() {
	local key="$1"
	local category_id="$2"
	local title status score published_at locale metadata_mode
	case "$key" in
		article_alpha_draft_1)
			title='Alpha 01 — bản nháp'
			status=draft
			score=1
			published_at='null'
			locale='vi'
			metadata_mode=object
			;;
		article_alpha_draft_2)
			title='Alpha 02 — bản nháp có Unicode'
			status=draft
			score=2
			published_at='null'
			locale='vi'
			metadata_mode=unicode
			;;
		article_alpha_published_1)
			title='Alpha 03 — đã xuất bản'
			status=published
			score=4
			published_at='2026-10-01T08:00:00Z'
			locale='vi'
			metadata_mode=object
			;;
		article_alpha_published_2)
			title='Alpha 04 — xuất bản nullable metadata'
			status=published
			score=5
			published_at='2026-10-02T08:00:00Z'
			locale='vi'
			metadata_mode=null
			;;
		article_beta_draft_1)
			title='Beta 01 — bản nháp'
			status=draft
			score=0
			published_at='null'
			locale='vi'
			metadata_mode=object
			;;
		article_beta_draft_2)
			title='Beta 02 — bản nháp & rỗng thời điểm'
			status=draft
			score=3
			published_at='null'
			locale='vi'
			metadata_mode=object
			;;
		article_beta_published_1)
			title='Beta 03 — đã xuất bản'
			status=published
			score=3
			published_at='2026-10-03T08:00:00Z'
			locale='vi'
			metadata_mode=object
			;;
		article_beta_published_2)
			title='Beta 04 — publication spéciale'
			status=published
			score=4
			published_at='2026-10-04T08:00:00Z'
			locale=fr
			metadata_mode=object
			;;
		article_gamma_draft_1)
			title='Gamma 01 — bản nháp'
			status=draft
			score=2
			published_at='null'
			locale='vi'
			metadata_mode=object
			;;
		article_gamma_draft_2)
			title='Gamma 02 — bản nháp Unicode 漢字'
			status=draft
			score=5
			published_at='null'
			locale=zh
			metadata_mode=object
			;;
		article_gamma_published_1)
			title='Gamma 03 — đã xuất bản'
			status=published
			score=1
			published_at='2026-10-05T08:00:00Z'
			locale='vi'
			metadata_mode=object
			;;
		article_gamma_published_2)
			title='Gamma 04 — đã xuất bản cuối'
			status=published
			score=5
			published_at='2026-10-06T08:00:00Z'
			locale='vi'
			metadata_mode=object
			;;
		*) return 1 ;;
	esac
	if [[ "$metadata_mode" == object ]]; then
		if [[ "$published_at" == null ]]; then
			jq -cn --arg key "$key" --arg version "$FIXTURE_VERSION" --arg title "$title" --arg status "$status" --arg locale "$locale" --arg category "$category_id" --argjson score "$score" '{title:$title,status:$status,score:$score,published_at:null,metadata:{fixture_key:$key,fixture_version:$version,locale:$locale},internal_notes:("Ghi chú nội bộ " + $key),category:($category|tonumber)}'
		else
			jq -cn --arg key "$key" --arg version "$FIXTURE_VERSION" --arg title "$title" --arg status "$status" --arg published_at "$published_at" --arg locale "$locale" --arg category "$category_id" --argjson score "$score" '{title:$title,status:$status,score:$score,published_at:$published_at,metadata:{fixture_key:$key,fixture_version:$version,locale:$locale},internal_notes:("Ghi chú nội bộ " + $key),category:($category|tonumber)}'
		fi
	elif [[ "$metadata_mode" == unicode ]]; then
		jq -cn --arg key "$key" --arg version "$FIXTURE_VERSION" --arg title "$title" --arg status "$status" --arg locale "$locale" --arg category "$category_id" --argjson score "$score" '{title:$title,status:$status,score:$score,published_at:null,metadata:{fixture_key:$key,fixture_version:$version,locale:$locale,unicode:"Đà Nẵng"},internal_notes:("Ghi chú nội bộ " + $key),category:($category|tonumber)}'
	else
		jq -cn --arg key "$key" --arg version "$FIXTURE_VERSION" --arg title "$title" --arg status "$status" --arg published_at "$published_at" --arg locale "$locale" --arg category "$category_id" --argjson score "$score" '{title:$title,status:$status,score:$score,published_at:$published_at,metadata:null,internal_notes:("Ghi chú nội bộ " + $key),category:($category|tonumber)}'
	fi
}

seed_categories() {
	local rows key name count id body
	api_expect_2xx 'đọc category fixture' GET '/items/qa_categories?limit=-1&fields=id,name' "$ADMIN_TOKEN" || return 1
	rows="$(jq -c '.data' "$API_BODY")"
	for key in $CATEGORY_KEYS; do
		name="$(category_spec "$key" | jq -r '.name')"
		count="$(jq -r --arg name "$name" '[.[] | select(.name == $name)] | length' <<< "$rows")"
		[[ "$count" -le 1 ]] || {
			printf 'ERROR: category fixture %s trùng tên\n' "$key" >&2
			return 1
		}
		if [[ "$count" -eq 1 ]]; then
			id="$(jq -r --arg name "$name" '.[] | select(.name == $name) | .id' <<< "$rows")"
		else
			body="$(category_spec "$key")"
			api_expect_2xx "tạo category $key" POST '/items/qa_categories' "$ADMIN_TOKEN" "$body" || return 1
			id="$(jq -r '.data.id // empty' "$API_BODY")"
		fi
		[[ "$id" =~ ^[1-9][0-9]*$ ]] || {
			printf 'ERROR: category %s không có ID số dương\n' "$key" >&2
			return 1
		}
		CATEGORY_MAP_JSON="$(jq -cn --argjson current "$CATEGORY_MAP_JSON" --arg key "$key" --arg id "$id" '$current + {($key):($id|tonumber)}')"
		printf 'Category fixture %s -> id %s\n' "$key" "$id"
	done
}

article_existing_matches() {
	local row="$1"
	local spec="$2"
	jq -e --argjson spec "$spec" '
		.id > 0
		and .title == $spec.title
		and .status == $spec.status
		and .score == $spec.score
		and (if ($spec.published_at == null) then .published_at == null else ((.published_at|sub("\\.[0-9]+Z$";"Z")|fromdateiso8601) == ($spec.published_at|fromdateiso8601)) end)
		and .category == $spec.category
		and ((.metadata // null) == ($spec.metadata // null))
		and ((.internal_notes // null) == ($spec.internal_notes // null))
	' <<< "$row" >/dev/null
}

seed_articles() {
	local rows key category_id spec title count id body category_key
	api_expect_2xx 'đọc article fixture' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	rows="$(jq -c '.data' "$API_BODY")"
	for key in $ARTICLE_KEYS; do
		case "$key" in
			article_alpha_*) category_key=category_alpha ;;
			article_beta_*) category_key=category_beta ;;
			article_gamma_*) category_key=category_gamma ;;
			*) return 1 ;;
		esac
		category_id="$(jq -r --arg key "$category_key" '.[$key]' <<< "$CATEGORY_MAP_JSON")"
		spec="$(article_spec "$key" "$category_id")"
		title="$(jq -r '.title' <<< "$spec")"
		count="$(jq -r --arg title "$title" '[.[] | select(.title == $title)] | length' <<< "$rows")"
		[[ "$count" -le 1 ]] || {
			printf 'ERROR: article fixture %s trùng title\n' "$key" >&2
			return 1
		}
		if [[ "$count" -eq 1 ]]; then
			id="$(jq -r --arg title "$title" '.[] | select(.title == $title) | .id' <<< "$rows")"
			article_existing_matches "$(jq -c --arg title "$title" '.[] | select(.title == $title)' <<< "$rows")" "$spec" || {
				printf 'ERROR: article fixture %s đã tồn tại nhưng dữ liệu khác contract\n' "$key" >&2
				return 1
			}
		else
			body="$spec"
			api_expect_2xx "tạo article $key" POST '/items/qa_articles' "$ADMIN_TOKEN" "$body" || return 1
			id="$(jq -r '.data.id // empty' "$API_BODY")"
		fi
		[[ "$id" =~ ^[1-9][0-9]*$ ]] || {
			printf 'ERROR: article %s không có ID số dương\n' "$key" >&2
			return 1
		}
		ARTICLE_MAP_JSON="$(jq -cn --argjson current "$ARTICLE_MAP_JSON" --arg key "$key" --arg id "$id" '$current + {($key):($id|tonumber)}')"
		printf 'Article fixture %s -> id %s\n' "$key" "$id"
	done
}

write_fixture_map() {
	local tmp
	mkdir -p "$RUNTIME_ROOT"
	tmp="$RUNTIME_ROOT/.fixture-ids.json.tmp"
	jq -n --arg version "$FIXTURE_VERSION" --arg project "$PROJECT_NAME" --arg run "$RUN_ID" --argjson categories "$CATEGORY_MAP_JSON" --argjson articles "$ARTICLE_MAP_JSON" '{schema:1,fixture_version:$version,project:$project,seed_run_id:$run,fixtures:{qa_categories:$categories,qa_articles:$articles}}' > "$tmp"
	mv -- "$tmp" "$FIXTURE_MAP"
	printf 'Fixture map: %s\n' "$FIXTURE_MAP"
}

load_fixture_map() {
	[[ -f "$FIXTURE_MAP" ]] || {
		printf 'ERROR: thiếu fixture map %s; chạy ./lab.sh seed trước\n' "$FIXTURE_MAP" >&2
		return 1
	}
	jq -e '
		.schema == 1
		and (.fixture_version|type == "string" and length > 0)
		and (.fixtures.qa_categories|type == "object")
		and (.fixtures.qa_articles|type == "object")
		and all(.fixtures[]|to_entries[];.value|type == "number" and floor == . and . > 0)
	' "$FIXTURE_MAP" >/dev/null || {
		printf 'ERROR: fixture map không hợp lệ\n' >&2
		return 1
	}
	FIXTURE_VERSION="$(jq -r '.fixture_version' "$FIXTURE_MAP")"
	SCHEMA_ROOT="$RUNTIME_ROOT/schemas/$FIXTURE_VERSION"
	CATEGORY_MAP_JSON="$(jq -c '.fixtures.qa_categories' "$FIXTURE_MAP")"
	ARTICLE_MAP_JSON="$(jq -c '.fixtures.qa_articles' "$FIXTURE_MAP")"
}

check_field_validation() {
	local category_id
	local body
	local invalid_status
	local invalid_score
	local temporary_id
	local checks='[]'
	category_id="$(jq -r '.fixtures.qa_categories.category_alpha' "$FIXTURE_MAP")"
	body="$(jq -cn --arg category "$category_id" '{title:"Validation probe",status:"draft",score:-1,published_at:null,metadata:null,internal_notes:"validation probe",category:($category|tonumber)}')"
	api_request POST '/items/qa_articles' "$EDITOR_TOKEN" "$body" || return 1
	invalid_score="$API_STATUS"
	if valid_http_success "$invalid_score"; then
		temporary_id="$(jq -r '.data.id // empty' "$API_BODY")"
		cleanup_item "$temporary_id"
		printf 'ERROR: score=-1 đã được chấp nhận\n' >&2
		return 1
	fi
	checks="$(jq -cn --argjson rows "$checks" --arg status "$invalid_score" '$rows + [{rule:"score 0..5",status:$status,accepted:false}]')"
	body="$(jq -cn --arg category "$category_id" '{title:"Validation probe",status:"archived",score:3,published_at:null,metadata:null,internal_notes:"validation probe",category:($category|tonumber)}')"
	api_request POST '/items/qa_articles' "$EDITOR_TOKEN" "$body" || return 1
	invalid_status="$API_STATUS"
	if valid_http_success "$invalid_status"; then
		temporary_id="$(jq -r '.data.id // empty' "$API_BODY")"
		cleanup_item "$temporary_id"
		printf 'ERROR: status=archived đã được chấp nhận\n' >&2
		return 1
	fi
	checks="$(jq -cn --argjson rows "$checks" --arg status "$invalid_status" '$rows + [{rule:"status draft|published",status:$status,accepted:false}]')"
	printf '%s\n' "$(jq -cn --argjson checks "$checks" '{schema:1,checks:$checks}')" > "$RUN_DIR/contract-validation.json"
	printf 'Field validation: PASS (score=%s,status=%s)\n' "$invalid_score" "$invalid_status"
}

check_relation_nullification() {
	local category_id=''
	local article_id=''
	local category_body article_body
	local after_category
	category_body="$(jq -cn --arg run "$RUN_ID" '{name:("Relation probe " + $run)}')"
	api_request POST '/items/qa_categories' "$EDITOR_TOKEN" "$category_body" || return 1
	if ! valid_http_success "$API_STATUS"; then
		printf 'ERROR: relation probe không tạo được category\n' >&2
		return 1
	fi
	category_id="$(jq -r '.data.id // empty' "$API_BODY")"
	article_body="$(jq -cn --arg category "$category_id" --arg run "$RUN_ID" '{title:("Relation probe " + $run),status:"draft",score:1,published_at:null,metadata:{scenario:"relation",run_id:$run},internal_notes:"relation probe",category:($category|tonumber)}')"
	api_request POST '/items/qa_articles' "$EDITOR_TOKEN" "$article_body" || return 1
	if ! valid_http_success "$API_STATUS"; then
		printf 'ERROR: relation probe không tạo được article\n' >&2
		if ! api_request DELETE "/items/qa_categories/$category_id" "$EDITOR_TOKEN" >/dev/null 2>&1; then
			printf 'WARN: cleanup category relation probe lỗi network\n' >&2
		elif ! valid_http_success "$API_STATUS"; then
			printf 'WARN: cleanup category relation probe HTTP %s\n' "$API_STATUS" >&2
		fi
		return 1
	fi
	article_id="$(jq -r '.data.id // empty' "$API_BODY")"
	api_request DELETE "/items/qa_categories/$category_id" "$EDITOR_TOKEN" || return 1
	valid_http_success "$API_STATUS" || {
		printf 'ERROR: xóa category relation probe thất bại HTTP %s\n' "$API_STATUS" >&2
		return 1
	}
	api_expect_2xx 'đọc relation probe article' GET "/items/qa_articles/$article_id?fields=id,category" "$EDITOR_TOKEN" || return 1
	after_category="$(jq -r '.data.category // "null"' "$API_BODY")"
	if ! api_request DELETE "/items/qa_articles/$article_id" "$EDITOR_TOKEN" >/dev/null 2>&1; then
		printf 'ERROR: cleanup relation probe article lỗi network\n' >&2
		return 1
	fi
	if ! valid_http_success "$API_STATUS"; then
		printf 'ERROR: cleanup relation probe article HTTP %s\n' "$API_STATUS" >&2
		return 1
	fi
	if [[ "$after_category" != null ]]; then
		printf 'ERROR: xóa category không đặt article.category về null (actual=%s)\n' "$after_category" >&2
		return 1
	fi
	printf 'Relation on_delete: PASS (SET NULL)\n'
}

seed() {
	require_tools
	require_admin_login
	ensure_schema || return 1
	seed_categories || return 1
	seed_articles || return 1
	write_fixture_map
	ensure_permissions_and_users || return 1
	printf 'Seed: PASS (3 categories, 12 articles, 6 draft, 6 published)\n'
}

smoke() {
	require_tools
	require_admin_login
	require_actor_logins
	load_fixture_map
	api_expect_2xx 'smoke server ping' GET '/server/ping' '' || return 1
	api_expect_2xx 'smoke editor categories' GET '/items/qa_categories?limit=-1&fields=id,name' "$EDITOR_TOKEN" || return 1
	[[ "$(jq -r '.data|length' "$API_BODY")" -ge 3 ]] || {
		printf 'ERROR: editor không đọc đủ category fixture\n' >&2
		return 1
	}
	check_field_validation || return 1
	check_relation_nullification || return 1
	api_expect_2xx 'smoke reader published articles' GET '/items/qa_articles?limit=-1&fields=id,title,status,category' "$READER_TOKEN" || return 1
	jq -e '(.data|length) == 6 and all(.data[];.status == "published")' "$API_BODY" >/dev/null || {
		printf 'ERROR: reader nhìn thấy dữ liệu ngoài tập published\n' >&2
		return 1
	}
	printf 'Smoke: PASS (actor login, category read, reader published filter)\n'
}

schema_operations_json() {
	local schema_file="$1"
	jq -c '
		[.paths // {} | to_entries[]
		| select(.key | startswith("/items/qa_"))
		| .key as $path
		| .value | to_entries[]
		| select(.key | IN("get","post","patch","delete"))
		| {method:(.key|ascii_upcase),path:$path,operation_id:(.value.operationId // null)}]
		| sort_by(.path,.method)
	' "$schema_file"
}

schema_manifest_add() {
	local actor="$1"
	local schema_file="$2"
	local sha="$3"
	local operation_count="$4"
	local operations="$5"
	local current="$SCHEMA_MANIFEST_JSON"
	if [[ -z "$current" ]]; then
		current="$(jq -cn --arg version "$FIXTURE_VERSION" '{schema:1,fixture_version:$version,actors:{}}')"
	fi
	SCHEMA_MANIFEST_JSON="$(jq -cn --argjson current "$current" --arg actor "$actor" --arg file "$schema_file" --arg sha "$sha" --argjson count "$operation_count" --argjson operations "$operations" '$current + {actors:($current.actors + {($actor):{file:$file,sha256:$sha,operation_count:$count,operations:$operations}})}')"
}

export_one_schema() {
	local actor="$1"
	local token="$2"
	local canonical="$SCHEMA_ROOT/$actor.json"
	local run_copy="$RUN_DIR/schema-$actor.json"
	local sha
	local existing_sha
	local operations
	local operation_count

	api_expect_2xx "xuất schema actor $actor" GET '/server/specs/oas' "$token" || return 1
	jq -e '.openapi == "3.0.1" and (.paths|type == "object")' "$API_BODY" >/dev/null || {
		printf 'ERROR: schema actor %s không phải OpenAPI 3 hợp lệ\n' "$actor" >&2
		return 1
	}
	sha="$(sha256sum "$API_BODY" | awk '{print $1}')"
	operations="$(schema_operations_json "$API_BODY")"
	operation_count="$(jq -r 'length' <<< "$operations")"
	cp -- "$API_BODY" "$run_copy"
	mkdir -p "$SCHEMA_ROOT"
	if [[ -f "$canonical" ]]; then
		existing_sha="$(sha256sum "$canonical" | awk '{print $1}')"
		if [[ "$existing_sha" != "$sha" ]]; then
			printf 'ERROR: raw schema %s đã tồn tại nhưng hash thay đổi; không overwrite\n' "$canonical" >&2
			return 1
		fi
	else
		cp -- "$API_BODY" "$canonical"
	fi
	schema_manifest_add "$actor" "$canonical" "$sha" "$operation_count" "$operations"
	printf 'Schema %s: sha256=%s operations=%s\n' "$actor" "$sha" "$operation_count"
}

export_schema() {
	require_tools
	require_admin_login
	require_actor_logins
	load_fixture_map
	mkdir -p "$SCHEMA_ROOT"
	SCHEMA_MANIFEST_JSON="$(jq -cn --arg version "$FIXTURE_VERSION" '{schema:1,fixture_version:$version,actors:{}}')"
	export_one_schema admin "$ADMIN_TOKEN" || return 1
	export_one_schema editor "$EDITOR_TOKEN" || return 1
	export_one_schema reader "$READER_TOKEN" || return 1
	export_one_schema anonymous '' || return 1
	printf '%s\n' "$SCHEMA_MANIFEST_JSON" > "$RUN_DIR/schema-manifest.json"
	printf 'Schema manifest: %s\n' "$RUN_DIR/schema-manifest.json"
}

SCENARIO_REPORT=''
SCENARIO_FAILURES=0
SCENARIO_BLOCKED=0

scenario_record() {
	local scenario_id="$1"
	local name="$2"
	local result="$3"
	local expected="$4"
	local actual="$5"
	local details="$6"
	local tmp="$RUN_DIR/.scenario-report.tmp"
	jq --arg id "$scenario_id" --arg name "$name" --arg result "$result" --arg expected "$expected" --arg actual "$actual" --arg details "$details" \
		'.scenarios += [{id:$id,name:$name,status:$result,expected:$expected,actual:$actual,details:$details}]' "$SCENARIO_REPORT" > "$tmp"
	mv -- "$tmp" "$SCENARIO_REPORT"
	case "$result" in
		passed) ;;
		blocked) SCENARIO_BLOCKED=$((SCENARIO_BLOCKED + 1)) ;;
		*) SCENARIO_FAILURES=$((SCENARIO_FAILURES + 1)) ;;
	esac
	printf 'Scenario %s: %s\n' "$scenario_id" "$result"
}

fixture_article_id() {
	jq -r --arg key "$1" '.fixtures.qa_articles[$key]' "$FIXTURE_MAP"
}

schema_has_operation() {
	local actor="$1"
	local method="$2"
	local path="$3"
	local schema_file="$SCHEMA_ROOT/$actor.json"
	[[ -f "$schema_file" ]] || return 1
	jq -e --arg method "$(printf '%s' "$method" | tr '[:upper:]' '[:lower:]')" --arg path "$path" '.paths[$path][$method] != null' "$schema_file" >/dev/null
}

ensure_reader_schema() {
	if [[ ! -f "$SCHEMA_ROOT/reader.json" ]]; then
		export_schema || return 1
	fi
}

cleanup_item() {
	local item_id="$1"
	[[ -n "$item_id" ]] || return 0
	if ! api_request DELETE "/items/qa_articles/$item_id" "$EDITOR_TOKEN" >/dev/null 2>&1; then
		printf 'WARN: cleanup article %s lỗi network\n' "$item_id" >&2
		return 1
	fi
	if ! valid_http_success "$API_STATUS"; then
		printf 'WARN: cleanup article %s HTTP %s\n' "$item_id" "$API_STATUS" >&2
		return 1
	fi
}

scenario_editor_crud() {
	local category_id
	local body
	local item_id=''
	local title
	local before_title
	local deleted_status
	local score
	category_id="$(jq -r '.fixtures.qa_categories.category_alpha' "$FIXTURE_MAP")"
	title="Scenario CRUD $RUN_ID"
	body="$(jq -cn --arg title "$title" --arg category "$category_id" '{title:$title,status:"draft",score:1,published_at:null,metadata:{scenario:"crud",run_id:$ENV_RUN_ID},internal_notes:"scenario-only",category:($category|tonumber)}' --arg ENV_RUN_ID "$RUN_ID")"
	api_request POST '/items/qa_articles' "$EDITOR_TOKEN" "$body" || {
		scenario_record S1 'Editor CRUD' failed 'POST create 2xx, GET/PATCH/DELETE invariants' 'network error' 'create request failed'
		return 1
	}
	if ! valid_http_success "$API_STATUS"; then
		scenario_record S1 'Editor CRUD' failed 'POST create 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	fi
	item_id="$(jq -r '.data.id // empty' "$API_BODY")"
	if [[ ! "$item_id" =~ ^[1-9][0-9]*$ ]]; then
		scenario_record S1 'Editor CRUD' failed 'response contains positive id' 'missing id' 'create response malformed'
		return 1
	fi
	api_expect_2xx 'CRUD read detail' GET "/items/qa_articles/$item_id?fields=id,title,status,score,category" "$EDITOR_TOKEN" || {
		cleanup_item "$item_id"
		scenario_record S1 'Editor CRUD' failed 'created item readable by editor' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	before_title="$(jq -r '.data.title // empty' "$API_BODY")"
	[[ "$before_title" == "$title" ]] || {
		cleanup_item "$item_id"
		scenario_record S1 'Editor CRUD' failed 'title preserved after create' "$before_title" 'read-back title mismatch'
		return 1
	}
	api_expect_2xx 'CRUD patch detail' PATCH "/items/qa_articles/$item_id" "$EDITOR_TOKEN" '{"score":5}' || {
		cleanup_item "$item_id"
		scenario_record S1 'Editor CRUD' failed 'PATCH detail 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	api_expect_2xx 'CRUD read patched detail' GET "/items/qa_articles/$item_id?fields=id,title,score" "$EDITOR_TOKEN" || {
		cleanup_item "$item_id"
		scenario_record S1 'Editor CRUD' failed 'read-back PATCH 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	score="$(jq -r '.data.score // empty' "$API_BODY")"
	before_title="$(jq -r '.data.title // empty' "$API_BODY")"
	[[ "$score" == 5 && "$before_title" == "$title" ]] || {
		cleanup_item "$item_id"
		scenario_record S1 'Editor CRUD' failed 'PATCH changes score and keeps title' "score=$score,title=$before_title" 'field preservation failed'
		return 1
	}
	api_request DELETE "/items/qa_articles/$item_id" "$EDITOR_TOKEN" || {
		scenario_record S1 'Editor CRUD' failed 'DELETE detail succeeds' 'network error' 'delete request failed'
		return 1
	}
	deleted_status="$API_STATUS"
	if ! valid_http_success "$deleted_status"; then
		scenario_record S1 'Editor CRUD' failed 'DELETE detail 2xx' "HTTP $deleted_status" "$(http_summary "$API_BODY")"
		return 1
	fi
	api_request GET "/items/qa_articles/$item_id?fields=id" "$EDITOR_TOKEN" || {
		scenario_record S1 'Editor CRUD' failed 'post-delete read returns an HTTP response' 'network error' 'read-back request failed'
		return 1
	}
	if valid_http_success "$API_STATUS" && jq -e '.data != null' "$API_BODY" >/dev/null 2>&1; then
		scenario_record S1 'Editor CRUD' failed 'deleted item is unavailable' "HTTP $API_STATUS" 'item still returned'
		return 1
	fi
	scenario_record S1 'Editor CRUD' passed 'create/read/PATCH/delete with field preservation' "create=2xx,patch=2xx,delete=$deleted_status" 'temporary item removed'
}

scenario_filter_status() {
	local expected_ids
	local actual_ids
	api_expect_2xx 'filter published' GET '/items/qa_articles?filter[status][_eq]=published&limit=-1&fields=id,title,status' "$EDITOR_TOKEN" || {
		scenario_record S2 'Filter status' failed 'published filter returns 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	expected_ids="$(jq -c '[.fixtures.qa_articles | to_entries[] | select(.key|contains("_published_")) | .value] | sort' "$FIXTURE_MAP")"
	actual_ids="$(jq -c '[.data[] | .id] | sort' "$API_BODY")"
	if [[ "$actual_ids" != "$expected_ids" ]] || ! jq -e 'all(.data[];.status == "published")' "$API_BODY" >/dev/null; then
		scenario_record S2 'Filter status' failed 'six published fixture IDs and status=published' "$actual_ids" 'filter result differs from fixture map'
		return 1
	fi
	scenario_record S2 'Filter status' passed 'published filter returns six fixture rows' "$actual_ids" 'editor query'
}

scenario_sort_pagination() {
	local all_rows page_one page_two expected_one expected_two
	api_expect_2xx 'sorted article list' GET '/items/qa_articles?sort=title,id&limit=-1&fields=id,title' "$EDITOR_TOKEN" || {
		scenario_record S3 'Sort/pagination' failed 'sorted list returns 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	all_rows="$(jq -c '.data' "$API_BODY")"
	[[ "$(jq -r 'length' <<< "$all_rows")" -ge 12 ]] || {
		scenario_record S3 'Sort/pagination' failed 'at least twelve fixture rows' "$(jq -r 'length' <<< "$all_rows")" 'fixture rows missing'
		return 1
	}
	api_expect_2xx 'pagination page one' GET '/items/qa_articles?sort=title,id&limit=3&offset=0&fields=id,title' "$EDITOR_TOKEN" || {
		scenario_record S3 'Sort/pagination' failed 'page one returns 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	page_one="$(jq -c '.data' "$API_BODY")"
	api_expect_2xx 'pagination page two' GET '/items/qa_articles?sort=title,id&limit=3&offset=3&fields=id,title' "$EDITOR_TOKEN" || {
		scenario_record S3 'Sort/pagination' failed 'page two returns 2xx' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	page_two="$(jq -c '.data' "$API_BODY")"
	expected_one="$(jq -c '.[0:3]' <<< "$all_rows")"
	expected_two="$(jq -c '.[3:6]' <<< "$all_rows")"
	if [[ "$page_one" != "$expected_one" || "$page_two" != "$expected_two" ]]; then
		scenario_record S3 'Sort/pagination' failed 'offset pages match deterministic title,id order' "page1=$page_one page2=$page_two" 'page result mismatch'
		return 1
	fi
	scenario_record S3 'Sort/pagination' passed 'sort=title,id with limit/offset' 'pages 0..2 and 3..5' 'matches full sorted list'
}

scenario_reader_no_draft() {
	local draft_id
	draft_id="$(fixture_article_id article_alpha_draft_1)"
	if ! schema_has_operation reader GET '/items/qa_articles/{id}'; then
		scenario_record S4 'Reader không đọc draft' blocked 'reader detail GET must be present before negative request' 'operation absent from reader schema' 'permission operation filtered; request not sent'
		return 1
	fi
	api_request GET "/items/qa_articles/$draft_id?fields=id,title,status,internal_notes" "$READER_TOKEN" || {
		scenario_record S4 'Reader không đọc draft' failed 'request reaches API' 'network error' 'request failed'
		return 1
	}
	if valid_http_success "$API_STATUS" && jq -e '.data != null' "$API_BODY" >/dev/null 2>&1; then
		scenario_record S4 'Reader không đọc draft' failed 'draft data not exposed' "HTTP $API_STATUS" 'reader received draft data'
		return 1
	fi
	scenario_record S4 'Reader không đọc draft' passed 'draft detail is rejected or empty' "HTTP $API_STATUS" 'no draft payload returned'
}

scenario_reader_hidden_field() {
	local published_id
	published_id="$(fixture_article_id article_alpha_published_1)"
	if ! schema_has_operation reader GET '/items/qa_articles/{id}'; then
		scenario_record S5 'Reader không lộ internal_notes' blocked 'reader detail GET must be present before field request' 'operation absent from reader schema' 'permission operation filtered; request not sent'
		return 1
	fi
	api_expect_2xx 'reader published precondition' GET "/items/qa_articles/$published_id?fields=id,title,status" "$READER_TOKEN" || {
		scenario_record S5 'Reader không lộ internal_notes' failed 'reader can read published article' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	api_request GET "/items/qa_articles/$published_id?fields=id,title,internal_notes" "$READER_TOKEN" || {
		scenario_record S5 'Reader không lộ internal_notes' failed 'request reaches API' 'network error' 'request failed'
		return 1
	}
	if valid_http_success "$API_STATUS" && ! jq -e '.data | has("internal_notes") | not' "$API_BODY" >/dev/null 2>&1; then
		scenario_record S5 'Reader không lộ internal_notes' failed 'internal_notes absent from response' "HTTP $API_STATUS" 'private field returned'
		return 1
	fi
	scenario_record S5 'Reader không lộ internal_notes' passed 'private field is omitted or request rejected' "HTTP $API_STATUS" 'no internal_notes value exposed'
}

scenario_reader_write() {
	local published_id before before_score new_score after
	published_id="$(fixture_article_id article_alpha_published_1)"
	if ! schema_has_operation reader PATCH '/items/qa_articles/{id}'; then
		scenario_record S6 'Reader ghi bị từ chối' blocked 'reader PATCH must be present before intentional negative request' 'operation absent from reader schema' 'permission operation filtered; request not sent'
		return 1
	fi
	api_expect_2xx 'reader write precondition' GET "/items/qa_articles/$published_id?fields=id,title,status,score" "$EDITOR_TOKEN" || {
		scenario_record S6 'Reader ghi bị từ chối' failed 'editor precondition read succeeds' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	before="$(jq -c '.data' "$API_BODY")"
	before_score="$(jq -r '.score' <<< "$before")"
	new_score=$(( (before_score + 1) % 6 ))
	api_request PATCH "/items/qa_articles/$published_id" "$READER_TOKEN" "$(jq -cn --argjson score "$new_score" '{score:$score}')"
	if (( API_CURL_RC != 0 )); then
		scenario_record S6 'Reader ghi bị từ chối' failed 'reader PATCH request reaches API' 'network error' 'request failed'
		return 1
	fi
	if valid_http_success "$API_STATUS"; then
		scenario_record S6 'Reader ghi bị từ chối' failed 'reader PATCH is rejected' "HTTP $API_STATUS" 'write request accepted'
		return 1
	fi
	api_expect_2xx 'reader write unchanged check' GET "/items/qa_articles/$published_id?fields=id,title,status,score" "$EDITOR_TOKEN" || {
		scenario_record S6 'Reader ghi bị từ chối' failed 'post-denial read succeeds' "HTTP $API_STATUS" "$(http_summary "$API_BODY")"
		return 1
	}
	after="$(jq -c '.data' "$API_BODY")"
	if [[ "$after" != "$before" ]]; then
		scenario_record S6 'Reader ghi bị từ chối' failed 'target data unchanged' "$after" 'reader rejection did not preserve data'
		return 1
	fi
	scenario_record S6 'Reader ghi bị từ chối' passed 'reader PATCH rejected and target unchanged' "HTTP $API_STATUS" 'editor read-back equals precondition'
}

scenarios() {
	local overall=0
	require_tools
	require_admin_login
	require_actor_logins
	load_fixture_map
	ensure_reader_schema || return 1
	SCENARIO_REPORT="$RUN_DIR/scenario-report.json"
	jq -n --arg version "$FIXTURE_VERSION" '{schema:1,fixture_version:$version,scenarios:[]}' > "$SCENARIO_REPORT"
	scenario_editor_crud || overall=1
	scenario_filter_status || overall=1
	scenario_sort_pagination || overall=1
	scenario_reader_no_draft || overall=1
	scenario_reader_hidden_field || overall=1
	scenario_reader_write || overall=1
	printf 'Scenario report: %s\n' "$SCENARIO_REPORT"
	jq -c '{passed:([.scenarios[]|select(.status=="passed")]|length),failed:([.scenarios[]|select(.status=="failed")]|length),blocked:([.scenarios[]|select(.status=="blocked")]|length)}' "$SCENARIO_REPORT"
	if (( overall != 0 || SCENARIO_FAILURES != 0 || SCENARIO_BLOCKED != 0 )); then
		return 1
	fi
}

snapshot_fixture_articles() {
	local snapshot="$RUN_DIR/pre-pilot-articles.json"
	api_expect_2xx 'snapshot fixture trước pilot' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	cp -- "$API_BODY" "$snapshot"
	printf 'Pilot snapshot: %s\n' "$snapshot"
}

restore_fixture_articles() {
	local snapshot="$RUN_DIR/pre-pilot-articles.json"
	local current_file
	local current_id
	local original_row
	local body
	local restore_failures=0
	[[ -f "$snapshot" ]] || {
		printf 'ERROR: thiếu snapshot để khôi phục fixture\n' >&2
		return 1
	}
	api_expect_2xx 'đọc article sau pilot' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	current_file="$API_BODY"
	while IFS= read -r current_id; do
		if ! jq -e --argjson id "$current_id" 'any(.data[]; .id == $id)' "$snapshot" >/dev/null; then
			api_request DELETE "/items/qa_articles/$current_id" "$ADMIN_TOKEN" || restore_failures=$((restore_failures + 1))
			if (( API_CURL_RC == 0 )) && ! valid_http_success "$API_STATUS"; then
				restore_failures=$((restore_failures + 1))
			fi
		fi
	done < <(jq -r '.data[]|.id' "$current_file")
	while IFS= read -r original_row; do
		current_id="$(jq -r '.id' <<< "$original_row")"
		if jq -e --argjson id "$current_id" 'any(.data[]; .id == $id)' "$current_file" >/dev/null; then
			body="$(jq -c 'del(.id)' <<< "$original_row")"
			api_request PATCH "/items/qa_articles/$current_id" "$ADMIN_TOKEN" "$body" || restore_failures=$((restore_failures + 1))
		else
			api_request POST '/items/qa_articles' "$ADMIN_TOKEN" "$original_row" || restore_failures=$((restore_failures + 1))
		fi
		if (( API_CURL_RC == 0 )) && ! valid_http_success "$API_STATUS"; then
			restore_failures=$((restore_failures + 1))
		fi
	done < <(jq -c '.data[]' "$snapshot")
	api_expect_2xx 'xác minh fixture sau khôi phục' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	if ! jq -e --slurpfile expected "$snapshot" '.data | sort_by(.id) == ($expected[0].data | sort_by(.id))' "$API_BODY" >/dev/null; then
		printf 'ERROR: article fixture sau pilot không khớp snapshot\n' >&2
		restore_failures=$((restore_failures + 1))
	fi
	if (( restore_failures != 0 )); then
		printf 'ERROR: khôi phục fixture gặp %s lỗi\n' "$restore_failures" >&2
		return 1
	fi
	printf 'Pilot restore: PASS (fixture article snapshot khớp)\n'
}

CAMPAIGN_BASE_RUN_DIR=''
CAMPAIGN_SUMMARIES='[]'
CAMPAIGN_SEEDS="${LAB_CAMPAIGN_SEEDS:-101,202,303}"
CAMPAIGN_MAX_TIME="${LAB_MAX_TIME:-1200}"
CAMPAIGN_MAX_EXAMPLES="${LAB_MAX_EXAMPLES:-100}"
CAMPAIGN_WORKERS="${LAB_WORKERS:-1}"
CAMPAIGN_RATE_LIMIT="${LAB_RATE_LIMIT:-5/s}"
CAMPAIGN_REQUEST_TIMEOUT="${LAB_REQUEST_TIMEOUT:-10}"
TARGET_OPERATIONS_JSON=''

target_operations_json() {
	jq -cn '[
		{method:"GET",path:"/items/qa_articles"},
		{method:"POST",path:"/items/qa_articles"},
		{method:"GET",path:"/items/qa_articles/{id}"},
		{method:"PATCH",path:"/items/qa_articles/{id}"},
		{method:"DELETE",path:"/items/qa_articles/{id}"},
		{method:"GET",path:"/items/qa_categories"},
		{method:"POST",path:"/items/qa_categories"},
		{method:"GET",path:"/items/qa_categories/{id}"},
		{method:"PATCH",path:"/items/qa_categories/{id}"},
		{method:"DELETE",path:"/items/qa_categories/{id}"}
	]'
}

campaign_validate_config() {
	local value
	for value in "$CAMPAIGN_MAX_TIME" "$CAMPAIGN_MAX_EXAMPLES" "$CAMPAIGN_WORKERS" "$CAMPAIGN_REQUEST_TIMEOUT"; do
		[[ "$value" =~ ^[1-9][0-9]*$ ]] || {
			printf 'ERROR: campaign numeric config không hợp lệ: %s\n' "$value" >&2
			return 1
		}
	done
	[[ "$CAMPAIGN_RATE_LIMIT" =~ ^[1-9][0-9]*/[smh]$ ]] || {
		printf 'ERROR: LAB_RATE_LIMIT phải có dạng 5/s, 100/m hoặc 1/h\n' >&2
		return 1
	}
}

campaign_require_inputs() {
	local source schema_operations expected_count
	require_tools
	command -v sha256sum >/dev/null 2>&1 || {
		printf 'ERROR: thiếu sha256sum để ghi schema hash\n' >&2
		return 1
	}
	campaign_validate_config || return 1
	require_admin_login
	require_actor_logins
	load_fixture_map
	TARGET_OPERATIONS_JSON="$(target_operations_json)"
	source="$SCHEMA_ROOT/editor.json"
	if [[ ! -f "$source" ]]; then
		export_schema || return 1
	fi
	[[ -f "$source" ]] || {
		printf 'ERROR: thiếu raw editor schema: %s\n' "$source" >&2
		return 1
	}
	schema_operations="$(schema_operations_json "$source")"
	expected_count="$(jq -r 'length' <<< "$TARGET_OPERATIONS_JSON")"
	jq -n -e --argjson expected "$TARGET_OPERATIONS_JSON" --argjson actual "$schema_operations" '
		($actual | map({method,path}) | sort_by(.path,.method)) as $actual_ops
		| ($expected | sort_by(.path,.method)) as $expected_ops
		| (($expected_ops - $actual_ops) | length) == 0
	' >/dev/null 2>/dev/null || {
		printf 'ERROR: editor raw schema không có đủ inventory %s operation\n' "$expected_count" >&2
		return 1
	}
	[[ "$SCHEMATHESIS_IMAGE" == *@sha256:* ]] || {
		printf 'ERROR: SCHEMATHESIS_IMAGE chưa được digest-pin\n' >&2
		return 1
	}
	docker image inspect "$SCHEMATHESIS_IMAGE" >/dev/null 2>&1 || {
		printf 'ERROR: runner image chưa có trên máy\n' >&2
		return 1
	}
}

campaign_build_schema() {
	local profile="$1"
	local source="$SCHEMA_ROOT/editor.json"
	local target="$RUN_DIR/schema-$profile.json"
	local source_copy="$RUN_DIR/source-editor.json"
	local article_id
	local category_id
	local diff_status
	cp -- "$source" "$source_copy"
	article_id="$(jq -r '.fixtures.qa_articles.article_alpha_published_1' "$FIXTURE_MAP")"
	category_id="$(jq -r '.fixtures.qa_categories.category_alpha' "$FIXTURE_MAP")"
	jq --arg profile "$profile" --arg fixture_version "$FIXTURE_VERSION" --argjson article_id "$article_id" --argjson category_id "$category_id" '
		.paths = (.paths | with_entries(
			if .key == "/items/qa_articles" or .key == "/items/qa_categories" then
				.value |= with_entries(select(.key == "get" or .key == "post"))
			elif .key == "/items/qa_articles/{id}" or .key == "/items/qa_categories/{id}" then
				.value |= with_entries(select(.key == "get" or .key == "patch" or .key == "delete"))
			else empty
			end
		))
		| if $profile == "guided" then
			.paths["/items/qa_articles/{id}"].get.parameters = ((.paths["/items/qa_articles/{id}"].get.parameters // []) | map(
				if .name == "id" then . + {example:$article_id} else . end
			))
			| .paths["/items/qa_articles/{id}"].patch.parameters = ((.paths["/items/qa_articles/{id}"].patch.parameters // []) | map(
				if .name == "id" then . + {example:$article_id} else . end
			))
			| .paths["/items/qa_articles/{id}"].delete.parameters = ((.paths["/items/qa_articles/{id}"].delete.parameters // []) | map(
				if .name == "id" then . + {example:$article_id} else . end
			))
			| .paths["/items/qa_categories/{id}"].get.parameters = ((.paths["/items/qa_categories/{id}"].get.parameters // []) | map(
				if .name == "id" then . + {example:$category_id} else . end
			))
			| .paths["/items/qa_categories/{id}"].patch.parameters = ((.paths["/items/qa_categories/{id}"].patch.parameters // []) | map(
				if .name == "id" then . + {example:$category_id} else . end
			))
			| .paths["/items/qa_categories/{id}"].delete.parameters = ((.paths["/items/qa_categories/{id}"].delete.parameters // []) | map(
				if .name == "id" then . + {example:$category_id} else . end
			))
			| .paths["/items/qa_articles"].post.requestBody.content["application/json"].example = {
				title:"Guided Schemathesis article",
				status:"draft",
				score:3,
				published_at:null,
				metadata:{source:"guided",fixture_version:$fixture_version},
				internal_notes:"guided probe",
				category:$category_id
			}
			| .paths["/items/qa_categories"].post.requestBody.content["application/json"].example = {name:"Guided Schemathesis category"}
			| .paths["/items/qa_articles/{id}"].patch.requestBody.content["application/json"].example = {score:4}
			| .paths["/items/qa_categories/{id}"].patch.requestBody.content["application/json"].example = {name:"Guided category update"}
			| .["x-r06-k05-guidance"] = {
				profile:"guided",
				reason:"fixture IDs and valid request examples improve reachability; raw schema remains unchanged",
				fixture_ids:{article:$article_id,category:$category_id},
				query_focus:["fields","filter","sort","limit","offset","page","search"]
			}
		else .
		end
	' "$source" > "$target"
	set +e
	diff -u "$source_copy" "$target" > "$RUN_DIR/schema-$profile.diff"
	diff_status=$?
	set -e
	[[ "$diff_status" -eq 0 || "$diff_status" -eq 1 ]] || {
		printf 'ERROR: không tạo được diff schema %s\n' "$profile" >&2
		return 1
	}
	jq -e '.openapi == "3.0.1" and (.paths|type == "object")' "$target" >/dev/null || {
		printf 'ERROR: schema scope %s không hợp lệ\n' "$target" >&2
		return 1
	}
	jq -n --arg profile "$profile" --arg source "$source" --arg target "$target" \
		--arg source_sha "$(sha256sum "$source" | awk '{print $1}')" \
		--arg target_sha "$(sha256sum "$target" | awk '{print $1}')" \
		--arg reason "$(if [[ "$profile" == guided ]]; then printf '%s' 'guided adds fixture ID examples and valid request examples in a separate overlay'; else printf '%s' 'raw selects only the approved 10 method-path pairs; operation contracts are not edited'; fi)" \
		--argjson operations "$TARGET_OPERATIONS_JSON" \
		'{schema:1,profile:$profile,source_schema:$source,source_sha256:$source_sha,scoped_schema:$target,scoped_sha256:$target_sha,reason:$reason,operations:$operations}' \
		> "$RUN_DIR/schema-manifest.json"
	printf 'Campaign schema %s: %s\n' "$profile" "$target"
}

campaign_snapshot() {
	api_expect_2xx 'snapshot categories trước campaign' GET '/items/qa_categories?limit=-1&fields=id,name' "$ADMIN_TOKEN" || return 1
	cp -- "$API_BODY" "$RUN_DIR/baseline-categories.json"
	api_expect_2xx 'snapshot articles trước campaign' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	cp -- "$API_BODY" "$RUN_DIR/baseline-articles.json"
}

campaign_delete_extras() {
	local collection="$1"
	local snapshot="$2"
	local fields="$3"
	local current_file
	local item_id
	local failures=0
	api_expect_2xx "đọc $collection sau campaign" GET "/items/$collection?limit=-1&fields=$fields" "$ADMIN_TOKEN" || return 1
	current_file="$API_BODY"
	while IFS= read -r item_id; do
		if ! jq -e --argjson id "$item_id" 'any(.data[]; .id == $id)' "$snapshot" >/dev/null; then
			if ! api_request DELETE "/items/$collection/$item_id" "$ADMIN_TOKEN"; then
				failures=$((failures + 1))
			elif ! valid_http_success "$API_STATUS"; then
				failures=$((failures + 1))
			fi
		fi
	done < <(jq -r '.data[]|.id' "$current_file")
	(( failures == 0 )) || {
		printf 'ERROR: xóa row ngoài snapshot %s gặp %s lỗi\n' "$collection" "$failures" >&2
		return 1
	}
}

campaign_restore_collection() {
	local collection="$1"
	local snapshot="$2"
	local current_file="$3"
	local item_id
	local row
	local body
	local failures=0
	while IFS= read -r row; do
		item_id="$(jq -r '.id' <<< "$row")"
		if jq -e --argjson id "$item_id" 'any(.data[]; .id == $id)' "$current_file" >/dev/null; then
			body="$(jq -c 'del(.id)' <<< "$row")"
			if ! api_request PATCH "/items/$collection/$item_id" "$ADMIN_TOKEN" "$body"; then
				failures=$((failures + 1))
			elif ! valid_http_success "$API_STATUS"; then
				failures=$((failures + 1))
			fi
		else
			if ! api_request POST "/items/$collection" "$ADMIN_TOKEN" "$row"; then
				failures=$((failures + 1))
			elif ! valid_http_success "$API_STATUS"; then
				failures=$((failures + 1))
			fi
		fi
	done < <(jq -c '.data[]' "$snapshot")
	(( failures == 0 )) || {
		printf 'ERROR: khôi phục collection %s gặp %s lỗi\n' "$collection" "$failures" >&2
		return 1
	}
}

campaign_restore() {
	local failures=0
	local current_categories
	local current_articles
	if ! campaign_delete_extras qa_articles "$RUN_DIR/baseline-articles.json" 'id,title,status,score,published_at,metadata,internal_notes,category'; then
		failures=$((failures + 1))
	fi
	if ! campaign_delete_extras qa_categories "$RUN_DIR/baseline-categories.json" 'id,name'; then
		failures=$((failures + 1))
	fi
	api_expect_2xx 'đọc categories để restore' GET '/items/qa_categories?limit=-1&fields=id,name' "$ADMIN_TOKEN" || return 1
	current_categories="$API_BODY"
	campaign_restore_collection qa_categories "$RUN_DIR/baseline-categories.json" "$current_categories" || failures=$((failures + 1))
	api_expect_2xx 'đọc articles để restore' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	current_articles="$API_BODY"
	campaign_restore_collection qa_articles "$RUN_DIR/baseline-articles.json" "$current_articles" || failures=$((failures + 1))
	api_expect_2xx 'xác minh categories sau restore' GET '/items/qa_categories?limit=-1&fields=id,name' "$ADMIN_TOKEN" || return 1
	jq -e --slurpfile expected "$RUN_DIR/baseline-categories.json" '.data | sort_by(.id) == ($expected[0].data | sort_by(.id))' "$API_BODY" >/dev/null || failures=$((failures + 1))
	api_expect_2xx 'xác minh articles sau restore' GET '/items/qa_articles?limit=-1&fields=id,title,status,score,published_at,metadata,internal_notes,category' "$ADMIN_TOKEN" || return 1
	jq -e --slurpfile expected "$RUN_DIR/baseline-articles.json" '.data | sort_by(.id) == ($expected[0].data | sort_by(.id))' "$API_BODY" >/dev/null || failures=$((failures + 1))
	if (( failures != 0 )); then
		printf 'ERROR: restore campaign không đạt (%s lỗi)\n' "$failures" >&2
		return 1
	fi
	printf 'Campaign restore: PASS (categories + articles khớp snapshot)\n'
}

replay_schemathesis_case() {
	local case_id="$1"
	local events_file
	local match
	local case_json=''
	local request_method
	local request_uri
	local request_path
	local request_body_b64
	local request_body=''
	local uri_without_scheme
	local expected_status
	local actual_status='network-error'
	local actual_summary='{}'
	local request_rc=0
	local restore_rc=1
	local replay_status='not_reproduced'
	local source_schema="$SCHEMA_ROOT/editor.json"
	local replay_schema_path
	local replay_schema_hash
	local source_file="$RUN_DIR/schemathesis-case.json"
	local response_file="$RUN_DIR/schemathesis-replay-response.json"
	local reproducer_file="$RUN_DIR/reproducer-schemathesis-$case_id.json"
	[[ "$case_id" =~ ^[A-Za-z0-9._-]{1,64}$ ]] || {
		printf 'ERROR: Schemathesis case-id chỉ được chứa chữ, số, ., _ hoặc - (tối đa 64 ký tự)\n' >&2
		return 2
	}

	require_tools
	require_admin_login
	require_actor_logins
	load_fixture_map
	[[ -f "$source_schema" ]] || export_schema || return 1

	[[ -d "$LAB_ROOT_DIR/artifacts/runs" ]] || {
		printf 'ERROR: chưa có artifact campaign để tìm Schemathesis case %s\n' "$case_id" >&2
		return 2
	}
	while IFS= read -r -d '' events_file; do
		if match="$(jq -c --arg case_id "$case_id" --arg source "$events_file" '
			select(.ScenarioFinished != null and .ScenarioFinished.recorder.cases[$case_id] != null)
			| .ScenarioFinished as $scenario
			| {source:$source,case_id:$case_id,case:$scenario.recorder.cases[$case_id],checks:($scenario.recorder.checks[$case_id] // []),interaction:($scenario.recorder.interactions[$case_id] // null)}
			| select(.interaction != null)
		' "$events_file" | sed -n '1p')"; then
			if [[ -n "$match" ]]; then
				case_json="$match"
				break
			fi
		fi
	done < <(find "$LAB_ROOT_DIR/artifacts/runs" -type f -name 'schemathesis-events.ndjson' -print0)

	[[ -n "$case_json" ]] || {
		printf 'ERROR: không tìm thấy Schemathesis case-id %s trong artifacts/runs\n' "$case_id" >&2
		return 2
	}
	replay_schema_path="$(dirname "$events_file")/schema-raw.json"
	[[ -f "$replay_schema_path" ]] || replay_schema_path="$(dirname "$events_file")/schema-guided.json"
	if [[ -f "$replay_schema_path" ]]; then
		replay_schema_hash="$(sha256sum "$replay_schema_path" | awk '{print $1}')"
	else
		replay_schema_hash="$(sha256sum "$source_schema" | awk '{print $1}')"
	fi
	printf '%s\n' "$case_json" > "$source_file"

	request_method="$(jq -r '.interaction.request.method // empty' <<< "$case_json")"
	request_uri="$(jq -r '.interaction.request.uri // empty' <<< "$case_json")"
	request_body_b64="$(jq -r '.interaction.request.body["$base64"] // empty' <<< "$case_json")"
	case "$request_method" in
		GET|POST|PATCH|DELETE|TRACE) ;;
		*) printf 'ERROR: method trong Schemathesis case không nằm trong replay allowlist: %s\n' "$request_method" >&2; return 2 ;;
	esac
	[[ "$request_uri" == http://* || "$request_uri" == https://* ]] || {
		printf 'ERROR: URI Schemathesis case không phải absolute HTTP URI\n' >&2
		return 2
	}
	uri_without_scheme="${request_uri#*://}"
	[[ "$uri_without_scheme" == */* ]] || {
		printf 'ERROR: URI Schemathesis case thiếu path\n' >&2
		return 2
	}
	request_path="/${uri_without_scheme#*/}"
	[[ "$request_path" == /items/qa_articles* || "$request_path" == /items/qa_categories* ]] || {
		printf 'ERROR: chỉ replay case trên qa_articles/qa_categories; nhận %s\n' "$request_path" >&2
		return 2
	}
	if [[ -n "$request_body_b64" ]]; then
		if ! request_body="$(printf '%s' "$request_body_b64" | base64 --decode)"; then
			printf 'ERROR: không decode được request body case %s\n' "$case_id" >&2
			return 2
		fi
	fi
	expected_status="$(jq -r '
		[.checks[] | select(.status == "failure") | .failure_info.failure.message // ""]
		| map(try capture("(?<status>[0-9]{3})").status catch null)
		| map(select(. != null))
		| .[0] // empty
	' <<< "$case_json")"

	campaign_snapshot || return 1
	printf 'Schemathesis replay %s: %s %s\n' "$case_id" "$request_method" "$request_path"
	if [[ -n "$request_body" ]]; then
		if ! api_request "$request_method" "$request_path" "$EDITOR_TOKEN" "$request_body"; then
			request_rc=1
		fi
	else
		if ! api_request "$request_method" "$request_path" "$EDITOR_TOKEN"; then
			request_rc=1
		fi
	fi
	actual_status="${API_STATUS:-network-error}"
	if [[ -f "$API_BODY" ]]; then
		cp -- "$API_BODY" "$response_file"
		actual_summary="$(http_summary "$API_BODY")"
	fi
	set +e
	campaign_restore
	restore_rc=$?
	set -e

	if (( request_rc == 0 && restore_rc == 0 )); then
		if [[ -z "$expected_status" || "$actual_status" == "$expected_status" ]]; then
			replay_status='reproduced'
		else
			replay_status='mismatch'
		fi
	fi
	jq -n --arg schema_version "$FIXTURE_VERSION" --arg case_id "$case_id" --arg source "$events_file" \
		--arg method "$request_method" --arg path "$request_path" --arg expected_status "$expected_status" \
		--arg actual_status "$actual_status" --arg status "$replay_status" --arg actor editor \
		--arg schema_hash "$replay_schema_hash" \
		--argjson case "$case_json" --argjson actual "$actual_summary" --argjson request_rc "$request_rc" --argjson restore_rc "$restore_rc" \
		'{schema:1,case_id:$case_id,source_events:$source,fixture_version:$schema_version,actor:$actor,schema_hash:$schema_hash,precondition:"fixture snapshot captured before request; current editor token from config/lab.env",request:{method:$method,path:$path},expected_status:($expected_status|if . == "" then null else tonumber end),actual_status:($actual_status|if test("^[0-9]+$") then tonumber else . end),status:$status,request_exit_code:$request_rc,restore_exit_code:$restore_rc,expected_checks:$case.checks,schemathesis_case:$case,actual_summary:$actual}' \
		> "$reproducer_file"
	printf 'Schemathesis replay report: %s (status=%s restore=%s)\n' "$reproducer_file" "$replay_status" "$restore_rc"
	[[ "$replay_status" == reproduced ]]
}

campaign_inventory() {
	local report_file="$RUN_DIR/schemathesis-report.json"
	local coverage_file="$RUN_DIR/schemathesis-coverage.json"
	local coverage='{}'
	if [[ -f "$coverage_file" ]]; then
		coverage="$(cat "$coverage_file")"
	fi
	jq -n --arg profile "$1" --arg seed "$2" --argjson expected "$TARGET_OPERATIONS_JSON" --argjson coverage "$coverage" '
		[ $expected[] as $op
		| (($coverage.operations // []) | map(select(.method == $op.method and .path == $op.path)) | .[0] // {}) as $hit
		| $op + {hits:($hit.hits // null),covered:(($hit.hits // 0) > 0)}
		] as $rows
		| {schema:1,profile:$profile,seed:($seed|tonumber),expected_operation_count:($rows|length),
		   covered_operation_count:([$rows[]|select(.covered)]|length),operations:$rows}
	' > "$RUN_DIR/operation-inventory.json"
	if [[ -f "$report_file" ]]; then
		jq -n --arg profile "$1" --arg seed "$2" --slurpfile report "$report_file" --slurpfile inventory "$RUN_DIR/operation-inventory.json" \
			'{schema:1,profile:$profile,seed:($seed|tonumber),operation_inventory:$inventory[0],schemathesis:{operations:($report[0].operations // null),test_cases:($report[0].test_cases // null),failures:($report[0].failures // []),warnings:($report[0].warnings // {})}}' \
			> "$RUN_DIR/metrics.json"
	else
		jq -n --arg profile "$1" --arg seed "$2" --slurpfile inventory "$RUN_DIR/operation-inventory.json" \
			'{schema:1,profile:$profile,seed:($seed|tonumber),operation_inventory:$inventory[0],schemathesis:null}' \
			> "$RUN_DIR/metrics.json"
	fi
}

campaign_one() {
	local profile="$1"
	local seed="$2"
	local base_dir="$CAMPAIGN_BASE_RUN_DIR"
	local runner_rc=1
	local restore_rc=1
	local report_present=false
	local coverage_present=false
	local termination='not_started'
	local status='failed'
	local report_summary='null'
	local campaign_dir="$base_dir/$profile/seed-$seed"
	local schema_file
	mkdir -p "$campaign_dir"
	RUN_DIR="$campaign_dir"
	if ! campaign_snapshot; then
		printf 'ERROR: không snapshot được baseline cho %s seed=%s\n' "$profile" "$seed" >&2
		RUN_DIR="$base_dir"
		return 1
	fi
	if ! campaign_build_schema "$profile"; then
		RUN_DIR="$base_dir"
		return 1
	fi
	schema_file="$RUN_DIR/schema-$profile.json"
	printf 'Schemathesis %s: 10 operation, max-examples=%s, seed=%s, max-time=%ss\n' "$profile" "$CAMPAIGN_MAX_EXAMPLES" "$seed" "$CAMPAIGN_MAX_TIME"
	set +e
	docker run --rm --user "$(id -u):$(id -g)" --network "$NETWORK_NAME" \
		-e SCHEMA_TOKEN="$EDITOR_TOKEN" \
		-e RUNNER_API_URL="$RUNNER_API_URL" \
		-e LAB_WORKERS="$CAMPAIGN_WORKERS" \
		-e LAB_MAX_EXAMPLES="$CAMPAIGN_MAX_EXAMPLES" \
		-e LAB_SEED="$seed" \
		-e LAB_REQUEST_TIMEOUT="$CAMPAIGN_REQUEST_TIMEOUT" \
		-e LAB_RATE_LIMIT="$CAMPAIGN_RATE_LIMIT" \
		-e LAB_MAX_TIME="$CAMPAIGN_MAX_TIME" \
		-e LAB_PHASES="$(if [[ "$profile" == guided ]]; then printf '%s' 'examples,coverage,fuzzing,stateful'; else printf '%s' 'examples,coverage,fuzzing'; fi)" \
		--mount "type=bind,src=$schema_file,dst=/work/schema.json,readonly" \
		--mount "type=bind,src=$RUN_DIR,dst=/work/run" \
		--entrypoint /bin/sh "$SCHEMATHESIS_IMAGE" \
		-c 'exec schemathesis run /work/schema.json --url "$RUNNER_API_URL" --workers "$LAB_WORKERS" --max-examples "$LAB_MAX_EXAMPLES" --seed "$LAB_SEED" --request-timeout "$LAB_REQUEST_TIMEOUT" --rate-limit "$LAB_RATE_LIMIT" --max-time "$LAB_MAX_TIME" --phases "$LAB_PHASES" --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance,unsupported_method,negative_data_rejection,positive_data_acceptance --report json,ndjson --report-json-path /work/run/schemathesis-report.json --report-ndjson-path /work/run/schemathesis-events.ndjson --coverage-format json --coverage-report-json-path /work/run/schemathesis-coverage.json --generation-database /work/run/schemathesis-examples.sqlite3 --generation-unique-inputs --output-sanitize true --output-truncate true --no-color -H "Authorization: Bearer $SCHEMA_TOKEN"'
	runner_rc=$?
	set -e
	if [[ -f "$RUN_DIR/schemathesis-report.json" ]]; then
		report_present=true
		termination="$(jq -r '.stop_reason // "unknown"' "$RUN_DIR/schemathesis-report.json")"
		report_summary="$(jq -c '{operations,test_cases,failures,errors,stop_reason,complete,exit_code,running_time}' "$RUN_DIR/schemathesis-report.json")"
	fi
	[[ -f "$RUN_DIR/schemathesis-coverage.json" ]] && coverage_present=true
	set +e
	campaign_restore
	restore_rc=$?
	set -e
	campaign_inventory "$profile" "$seed"
	if (( runner_rc == 0 && restore_rc == 0 )) && [[ "$report_present" == true && "$coverage_present" == true ]]; then
		if [[ "$termination" == max_time ]]; then
			status='incomplete'
		else
			status='passed'
		fi
	fi
	if [[ "$status" == passed ]]; then
		printf 'Campaign %s seed=%s: PASS\n' "$profile" "$seed"
	else
		printf 'Campaign %s seed=%s: %s (runner=%s restore=%s termination=%s)\n' "$profile" "$seed" "$status" "$runner_rc" "$restore_rc" "$termination"
	fi
	jq -n --arg profile "$profile" --arg seed "$seed" --arg status "$status" --arg termination "$termination" \
		--arg schema_sha "$(sha256sum "$schema_file" | awk '{print $1}')" \
		--argjson runner_rc "$runner_rc" --argjson restore_rc "$restore_rc" \
		--argjson report_present "$report_present" --argjson coverage_present "$coverage_present" \
		--argjson report "$report_summary" \
		--arg max_time "$CAMPAIGN_MAX_TIME" --arg max_examples "$CAMPAIGN_MAX_EXAMPLES" --arg workers "$CAMPAIGN_WORKERS" --arg rate_limit "$CAMPAIGN_RATE_LIMIT" --arg request_timeout "$CAMPAIGN_REQUEST_TIMEOUT" \
		'{schema:1,profile:$profile,seed:($seed|tonumber),status:$status,termination:$termination,schema_sha256:$schema_sha,runner_exit_code:$runner_rc,restore_exit_code:$restore_rc,report_present:$report_present,coverage_present:$coverage_present,budget:{max_time_seconds:($max_time|tonumber),max_examples_per_operation:($max_examples|tonumber),workers:($workers|tonumber),rate_limit:$rate_limit,request_timeout_seconds:($request_timeout|tonumber)},schemathesis:$report}' \
		> "$RUN_DIR/campaign-summary.json"
	CAMPAIGN_SUMMARIES="$(jq -cn --argjson current "$CAMPAIGN_SUMMARIES" --slurpfile next "$RUN_DIR/campaign-summary.json" '$current + [$next[0]]')"
	RUN_DIR="$base_dir"
	[[ "$status" == passed ]] || return 1
}

campaign() {
	local profile="$1"
	local seed
	local overall=0
	local base_dir="$RUN_DIR"
	local -a seeds
	case "$profile" in
		raw|guided) ;;
		*) printf 'ERROR: campaign profile phải là raw hoặc guided\n' >&2; return 2 ;;
	esac
	campaign_require_inputs || return 1
	CAMPAIGN_BASE_RUN_DIR="$base_dir"
	CAMPAIGN_SUMMARIES='[]'
	IFS=',' read -r -a seeds <<< "$CAMPAIGN_SEEDS"
	[[ "${#seeds[@]}" -gt 0 ]] || {
		printf 'ERROR: LAB_CAMPAIGN_SEEDS rỗng\n' >&2
		return 1
	}
	for seed in "${seeds[@]}"; do
		[[ "$seed" =~ ^[0-9]+$ ]] || {
			printf 'ERROR: seed không hợp lệ: %s\n' "$seed" >&2
			return 1
		}
		campaign_one "$profile" "$seed" || overall=1
	done
	RUN_DIR="$base_dir"
	jq -n --arg profile "$profile" --arg fixture "$FIXTURE_VERSION" --arg seeds "$CAMPAIGN_SEEDS" --argjson campaigns "$CAMPAIGN_SUMMARIES" \
		--argjson expected_seed_count "${#seeds[@]}" \
		'{schema:1,profile:$profile,fixture_version:$fixture,seeds:($seeds|split(",")|map(tonumber)),operation_count:10,campaigns:$campaigns,status:(if (($campaigns|length) == $expected_seed_count and all($campaigns[];.status == "passed")) then "passed" else "failed_or_incomplete" end)}' \
		> "$base_dir/campaign-index.json"
	printf 'Campaign index: %s\n' "$base_dir/campaign-index.json"
	return "$overall"
}

invariants() {
	local harness_sha
	require_tools
	[[ -n "$SCHEMATHESIS_IMAGE" && "$SCHEMATHESIS_IMAGE" == *@sha256:* ]] || {
		printf 'ERROR: SCHEMATHESIS_IMAGE chưa được digest-pin\n' >&2
		return 1
	}
	docker image inspect "$SCHEMATHESIS_IMAGE" >/dev/null 2>&1 || {
		printf 'ERROR: runner image chưa có trên máy\n' >&2
		return 1
	}
	[[ -f "$LAB_ROOT_DIR/scripts/invariants.py" && -d "$RUNTIME_ROOT" ]] || {
		printf 'ERROR: thiếu invariant script hoặc runtime mount\n' >&2
		return 1
	}
	harness_sha="$(git -C "$LAB_ROOT_DIR" rev-parse HEAD 2>/dev/null || printf 'no_commit')"
	docker run --rm --user "$(id -u):$(id -g)" --network "$NETWORK_NAME" \
		-e PYTHONDONTWRITEBYTECODE=1 \
		-e LAB_ROOT_DIR=/work \
		-e LAB_RUN_DIR=/work/run \
		-e LAB_RUNTIME_ROOT=/work/runtime \
		-e LAB_API_URL="$RUNNER_API_URL" \
		-e LAB_RUN_ID="$RUN_ID" \
		-e LAB_HARNESS_SHA="$harness_sha" \
		-e LAB_REQUEST_TIMEOUT="${LAB_REQUEST_TIMEOUT:-10}" \
		-e LAB_ADMIN_EMAIL="$ADMIN_EMAIL" \
		-e LAB_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
		-e LAB_EDITOR_EMAIL="$EDITOR_EMAIL" \
		-e LAB_EDITOR_PASSWORD="$EDITOR_PASSWORD" \
		-e LAB_READER_EMAIL="$READER_EMAIL" \
		-e LAB_READER_PASSWORD="$READER_PASSWORD" \
		--mount "type=bind,src=$LAB_ROOT_DIR/scripts/invariants.py,dst=/work/invariants.py,readonly" \
		--mount "type=bind,src=$RUNTIME_ROOT,dst=/work/runtime,readonly" \
		--mount "type=bind,src=$RUN_DIR,dst=/work/run" \
		--entrypoint python3 "$SCHEMATHESIS_IMAGE" /work/invariants.py --case all
}

replay_case() {
	local case_id="$1"
	case "$case_id" in
		auth-invalid-token|anonymous-denied|editor-crud|positive-operations|query-fixture|relation-nullification|invalid-field-rejection|reader-visibility|reader-write)
			local harness_sha
			require_tools
			[[ -n "$SCHEMATHESIS_IMAGE" && "$SCHEMATHESIS_IMAGE" == *@sha256:* ]] || {
				printf 'ERROR: SCHEMATHESIS_IMAGE chưa được digest-pin\n' >&2
				return 1
			}
			docker image inspect "$SCHEMATHESIS_IMAGE" >/dev/null 2>&1 || {
				printf 'ERROR: runner image chưa có trên máy\n' >&2
				return 1
			}
			harness_sha="$(git -C "$LAB_ROOT_DIR" rev-parse HEAD 2>/dev/null || printf 'no_commit')"
			docker run --rm --user "$(id -u):$(id -g)" --network "$NETWORK_NAME" \
				-e PYTHONDONTWRITEBYTECODE=1 \
				-e LAB_ROOT_DIR=/work \
				-e LAB_RUN_DIR=/work/run \
				-e LAB_RUNTIME_ROOT=/work/runtime \
				-e LAB_API_URL="$RUNNER_API_URL" \
				-e LAB_RUN_ID="$RUN_ID" \
				-e LAB_HARNESS_SHA="$harness_sha" \
				-e LAB_REQUEST_TIMEOUT="${LAB_REQUEST_TIMEOUT:-10}" \
				-e LAB_ADMIN_EMAIL="$ADMIN_EMAIL" \
				-e LAB_ADMIN_PASSWORD="$ADMIN_PASSWORD" \
				-e LAB_EDITOR_EMAIL="$EDITOR_EMAIL" \
				-e LAB_EDITOR_PASSWORD="$EDITOR_PASSWORD" \
				-e LAB_READER_EMAIL="$READER_EMAIL" \
				-e LAB_READER_PASSWORD="$READER_PASSWORD" \
				--mount "type=bind,src=$LAB_ROOT_DIR/scripts/invariants.py,dst=/work/invariants.py,readonly" \
				--mount "type=bind,src=$RUNTIME_ROOT,dst=/work/runtime,readonly" \
				--mount "type=bind,src=$RUN_DIR,dst=/work/run" \
				--entrypoint python3 "$SCHEMATHESIS_IMAGE" /work/invariants.py --case "$case_id"
			;;
		*)
			replay_schemathesis_case "$case_id"
			;;
	esac
}

schema_smoke() {
	local schema_file="$SCHEMA_ROOT/editor.json"
	local pilot_schema="$RUN_DIR/editor-pilot-schema.json"
	local operations
	local operation_count
	local expected_count=5
	local report_file="$RUN_DIR/schemathesis-report.json"
	local coverage_file="$RUN_DIR/schemathesis-coverage.json"
	local runner_summary="$RUN_DIR/pilot-summary.json"
	local runner_rc
	local report_present=false
	local coverage_present=false
	local operation method path
	local restore_rc
	load_fixture_map
	require_actor_logins
	require_admin_login
	if [[ ! -f "$schema_file" ]]; then
		export_schema || return 1
	fi
	jq '
		. as $root
		| ($root.paths
		| with_entries(
			if .key == "/items/qa_articles" then
				.value |= with_entries(select(.key == "get" or .key == "post"))
			elif .key == "/items/qa_articles/{id}" then
				.value |= with_entries(select(.key == "get" or .key == "patch" or .key == "delete"))
			else
				.value = {}
			end
		)
		| with_entries(select(.value | length > 0))
		) as $pilot_paths
		| ($root | .paths = $pilot_paths)
	' "$schema_file" > "$pilot_schema"
	operations="$(schema_operations_json "$pilot_schema")"
	operation_count="$(jq -r 'length' <<< "$operations")"
	for operation in \
		'GET /items/qa_articles' \
		'POST /items/qa_articles' \
		'GET /items/qa_articles/{id}' \
		'PATCH /items/qa_articles/{id}' \
		'DELETE /items/qa_articles/{id}'; do
		method="$(printf '%s' "$operation" | awk '{print $1}')"
		path="$(printf '%s' "$operation" | cut -d' ' -f2-)"
		if ! schema_has_operation editor "$method" "$path"; then
			printf 'ERROR: editor schema thiếu operation %s\n' "$operation" >&2
			return 1
		fi
	done
	[[ -n "$SCHEMATHESIS_IMAGE" && "$SCHEMATHESIS_IMAGE" == *@sha256:* ]] || {
		printf 'ERROR: SCHEMATHESIS_IMAGE chưa được digest-pin\n' >&2
		return 1
	}
	docker image inspect "$SCHEMATHESIS_IMAGE" >/dev/null 2>&1 || {
		printf 'ERROR: runner image chưa có trên máy\n' >&2
		return 1
	}
	snapshot_fixture_articles || return 1
	printf 'Schemathesis pilot: 5 operation, max-examples=20, seed=101, max-time=300s\n'
	set +e
	docker run --rm --user "$(id -u):$(id -g)" --network "$NETWORK_NAME" \
		-e SCHEMA_TOKEN="$EDITOR_TOKEN" \
		-e RUNNER_API_URL="$RUNNER_API_URL" \
		--mount "type=bind,src=$pilot_schema,dst=/work/schema.json,readonly" \
		--mount "type=bind,src=$RUN_DIR,dst=/work/run" \
		--entrypoint /bin/sh "$SCHEMATHESIS_IMAGE" \
		-c 'exec schemathesis run "$1" --url "$RUNNER_API_URL" --include-path-regex "^/items/qa_articles(/\\{id\\})?$" --workers 1 --max-examples 20 --seed 101 --request-timeout 10 --rate-limit 5/s --max-time 300 --phases examples,fuzzing --checks not_a_server_error,status_code_conformance,content_type_conformance,response_schema_conformance,unsupported_method,negative_data_rejection,positive_data_acceptance --report json --report-json-path /work/run/schemathesis-report.json --coverage-format json --coverage-report-json-path /work/run/schemathesis-coverage.json --output-sanitize true --no-color -H "Authorization: Bearer $SCHEMA_TOKEN"' \
		sh /work/schema.json
	runner_rc=$?
	set -e
	set +e
	restore_fixture_articles
	restore_rc=$?
	set -e
	if (( restore_rc != 0 )); then
		runner_rc=1
	fi
	[[ -f "$report_file" ]] && report_present=true
	[[ -f "$coverage_file" ]] && coverage_present=true
	jq -n --arg version "$FIXTURE_VERSION" --arg actor editor --arg source_sha "$(sha256sum "$schema_file" | awk '{print $1}')" --arg overlay_reason 'pilot allowlist keeps GET/POST list and GET/PATCH/DELETE detail; raw schema is preserved' --argjson operations "$operations" --argjson count "$operation_count" --argjson expected "$expected_count" --argjson seed 101 --arg budget 'max-time=300s,max-examples=20,workers=1,request-timeout=10,rate-limit=5/s' --argjson exit_code "$runner_rc" --argjson report "$report_present" --argjson coverage "$coverage_present" \
		'{schema:1,fixture_version:$version,actor:$actor,source_schema_sha256:$source_sha,overlay_reason:$overlay_reason,operation_count:$count,expected_operation_count:$expected,operations:$operations,seed:$seed,budget:$budget,exit_code:$exit_code,report_present:$report,coverage_present:$coverage,status:(if $exit_code == 0 and $report and $coverage then "passed" else "failed" end)}' > "$runner_summary"
	printf 'Pilot summary: %s\n' "$runner_summary"
	if (( runner_rc != 0 )); then
		return "$runner_rc"
	fi
	[[ "$report_present" == true && "$coverage_present" == true ]] || return 1
}

main() {
	local command_name="$1"
	case "$command_name" in
		seed) seed ;;
		smoke) smoke ;;
		export-schema) export_schema ;;
		scenarios) scenarios ;;
		invariants) invariants ;;
		schema-smoke) schema_smoke ;;
		raw) campaign raw ;;
		guided) campaign guided ;;
		replay)
			[[ "$#" -eq 2 ]] || { printf 'ERROR: replay cần một case-id\n' >&2; return 2; }
			replay_case "$2"
			;;
		*) printf 'ERROR: component không hỗ trợ profile %s\n' "$command_name" >&2; return 2 ;;
	esac
}

main "$@"
