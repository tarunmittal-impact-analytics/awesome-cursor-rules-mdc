#!/usr/bin/env bash
# Install Cursor MDC rules into .cursor/rules
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- react fastapi
#   curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --stack python-backend
#   curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --custom base frontend --here
#   curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --custom-all --here
#
# Options:
#   --here              Install into ./.cursor/rules (default)
#   --target PATH       Install into a specific directory
#   --stack NAME        Install a preset stack (supports custom:rule refs)
#   --tag TAG           Install all library rules matching tag (repeatable)
#   --custom NAME       Install custom/personal rule (repeatable)
#   --custom-all        Install all custom/personal rules
#   --force             Overwrite existing files
#   --dry-run           Show what would be installed

set -euo pipefail

REPO="tarunmittal-impact-analytics/awesome-cursor-rules-mdc"
BRANCH="main"
RAW_BASE="https://raw.githubusercontent.com/${REPO}/${BRANCH}"

TARGET="./.cursor/rules"
FORCE=0
DRY_RUN=0
STACK=""
declare -a RULES=()
declare -a TAGS=()
declare -a CUSTOM_RULES=()
CUSTOM_ALL=0

usage() {
  sed -n '2,18p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

log() {
  printf '%s\n' "$*"
}

error() {
  printf 'Error: %s\n' "$*" >&2
  exit 1
}

require_python() {
  command -v python3 >/dev/null 2>&1 || error "python3 is required for --stack, --tag, and --custom-all."
}

fetch_json() {
  local path="$1"
  curl -fsSL "${RAW_BASE}/${path}"
}

rules_for_stack() {
  local stack="$1"
  fetch_json "stacks.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
stack = sys.argv[1]
stacks = data.get('stacks', {})
if stack not in stacks:
    print(f'Unknown stack: {stack}', file=sys.stderr)
    print('Available: ' + ', '.join(sorted(stacks)), file=sys.stderr)
    sys.exit(1)
print(' '.join(stacks[stack]['rules']))
" "$stack"
}

rules_for_tags() {
  local tags_csv
  tags_csv=$(printf '%s,' "${TAGS[@]}")
  tags_csv="${tags_csv%,}"
  fetch_json "rules.json" | TAGS_CSV="$tags_csv" python3 -c "
import json, os, sys
wanted = {t.strip().lower() for t in os.environ['TAGS_CSV'].split(',') if t.strip()}
data = json.load(sys.stdin)
matched = []
for entry in data.get('libraries', []):
    entry_tags = {t.lower() for t in entry.get('tags', [])}
    if wanted & entry_tags:
        matched.append(entry['name'])
print(' '.join(sorted(set(matched))))
"
}

all_custom_rules() {
  fetch_json "custom-rules.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(' '.join(entry['name'] for entry in data.get('rules', [])))
"
}

install_rule() {
  local ref="$1"
  local kind="library"
  local name="$ref"
  local subdir="rules-mdc"

  if [[ "$ref" == custom:* ]]; then
    kind="custom"
    name="${ref#custom:}"
    subdir="rules-custom"
  fi

  local dest="${TARGET}/${name}.mdc"
  local url="${RAW_BASE}/${subdir}/${name}.mdc"

  if [[ -f "$dest" && "$FORCE" -eq 0 ]]; then
    log "Skipped: ${name} (already exists, use --force to overwrite)"
    return 0
  fi

  if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Would install: ${name} (${kind}) -> ${dest}"
    return 0
  fi

  mkdir -p "$TARGET"
  if curl -fsSL "$url" -o "$dest"; then
    log "Installed: ${name} (${kind})"
  else
    log "Missing: ${name} (${kind}, not found on GitHub)" >&2
    return 1
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage 0
      ;;
    --here)
      TARGET="./.cursor/rules"
      shift
      ;;
    --target)
      [[ $# -ge 2 ]] || error "--target requires a path"
      TARGET="$2"
      shift 2
      ;;
    --stack)
      [[ $# -ge 2 ]] || error "--stack requires a name"
      STACK="$2"
      shift 2
      ;;
    --tag)
      [[ $# -ge 2 ]] || error "--tag requires a value"
      TAGS+=("$2")
      shift 2
      ;;
    --custom)
      shift
      while [[ $# -gt 0 && "$1" != --* ]]; do
        CUSTOM_RULES+=("$1")
        shift
      done
      ;;
    --custom-all)
      CUSTOM_ALL=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --)
      shift
      break
      ;;
    -*)
      error "Unknown option: $1"
      ;;
    *)
      RULES+=("$1")
      shift
      ;;
  esac
done

while [[ $# -gt 0 ]]; do
  RULES+=("$1")
  shift
done

if [[ -n "$STACK" ]]; then
  require_python
  read -r -a stack_rules <<< "$(rules_for_stack "$STACK")"
  RULES+=("${stack_rules[@]}")
fi

if [[ ${#TAGS[@]} -gt 0 ]]; then
  require_python
  read -r -a tag_rules <<< "$(rules_for_tags)"
  RULES+=("${tag_rules[@]}")
fi

if [[ "$CUSTOM_ALL" -eq 1 ]]; then
  require_python
  read -r -a all_custom <<< "$(all_custom_rules)"
  for name in "${all_custom[@]}"; do
    CUSTOM_RULES+=("$name")
  done
fi

for name in "${CUSTOM_RULES[@]}"; do
  RULES+=("custom:${name}")
done

if [[ ${#RULES[@]} -eq 0 ]]; then
  error "No rules selected. Pass rule names, --stack, --tag, --custom, or --custom-all."
fi

unique_rules=()
while IFS= read -r rule; do
  unique_rules+=("$rule")
done < <(printf '%s\n' "${RULES[@]}" | tr '[:upper:]' '[:lower:]' | sort -u)

log "Target: ${TARGET}"
log "Rules: ${#unique_rules[@]}"
log ""

failed=0
for rule in "${unique_rules[@]}"; do
  install_rule "$rule" || failed=1
done

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi
