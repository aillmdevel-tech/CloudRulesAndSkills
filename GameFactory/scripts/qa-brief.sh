#!/usr/bin/env bash
set -eu

if [ "$#" -lt 3 ] || [ "$2" != "--" ]; then
  printf 'Usage: %s CHECK -- COMMAND [ARG ...]\n' "$0" >&2
  exit 64
fi

check=$1
shift 2
case "$check" in
  ''|*[!a-zA-Z0-9_-]*) printf 'Invalid check name: %s\n' "$check" >&2; exit 64 ;;
esac

log_dir=${GAMEFACTORY_QA_LOG_DIR:-"$PWD/tools/out/qa"}
mkdir -p "$log_dir"
log_path=$(mktemp "$log_dir/$check.XXXXXX")

if "$@" >"$log_path" 2>&1; then
  printf '%s PASS · %s\n' "$check" "$log_path"
else
  status=$?
  printf '%s FAIL (%s) · %s\n' "$check" "$status" "$log_path" >&2
  tail -n 18 "$log_path" | cut -c 1-240 >&2
  exit "$status"
fi
