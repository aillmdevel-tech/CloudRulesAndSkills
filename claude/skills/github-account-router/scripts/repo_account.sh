#!/usr/bin/env bash
# Bind a GitHub repo to the right locally logged-in gh account — per repository, never globally.
#
# usage:
#   repo_account.sh check  <url|owner/repo>              # which accounts can push (read-only)
#   repo_account.sh setup  <url|owner/repo> [dir] [--account LOGIN]
#        clone into dir (or configure dir if it already is that repo), then set LOCAL:
#        credential helper -> token of LOGIN via `gh auth token --user LOGIN`,
#        user.name / user.email -> LOGIN / <id>+LOGIN@users.noreply.github.com
#   repo_account.sh status [dir]                         # what this repo is bound to
#
# Global git config and the active gh account are not changed.
set -euo pipefail

die() { echo "ERROR: $*" >&2; exit 1; }
command -v gh >/dev/null || die "gh not installed"

parse() { # -> owner/repo
  local s="${1%.git}"; s="${s%/}"
  s="${s#https://github.com/}"; s="${s#http://github.com/}"; s="${s#git@github.com:}"; s="${s#github.com/}"
  s="${s#*@github.com/}"
  echo "$s" | cut -d/ -f1-2
}

accounts() { gh auth status 2>&1 | sed -n 's/.*Logged in to github.com account \([^ ]*\).*/\1/p'; }

perm() { # login repo -> admin|push|read|none
  local t; t="$(gh auth token --user "$1" 2>/dev/null)" || { echo none; return; }
  local r; r="$(GH_TOKEN="$t" gh api "repos/$2" --jq 'if .permissions.admin then "admin" elif .permissions.push then "push" else "read" end' 2>/dev/null)" || r=""
  case "$r" in admin|push|read) echo "$r" ;; *) echo none ;; esac
}

cmd="${1:-}"; shift || true
case "$cmd" in
  check)
    repo="$(parse "${1:?url}")"
    echo "repo: $repo"
    for a in $(accounts); do printf "  %-24s %s\n" "$a" "$(perm "$a" "$repo")"; done
    ;;
  setup)
    url="${1:?url}"; shift
    dir=""; acc=""
    while [ $# -gt 0 ]; do case "$1" in --account) acc="$2"; shift 2 ;; *) dir="$1"; shift ;; esac; done
    repo="$(parse "$url")"
    if [ -z "$acc" ]; then
      cands=()
      for a in $(accounts); do p="$(perm "$a" "$repo")"; [ "$p" = admin ] || [ "$p" = push ] && cands+=("$a"); done
      [ ${#cands[@]} -eq 0 ] && die "no logged-in account can push to $repo (accounts: $(accounts | tr '\n' ' ')). Log in: gh auth login --web, then rerun."
      if [ ${#cands[@]} -gt 1 ]; then
        owner="${repo%%/*}"
        for a in "${cands[@]}"; do [ "$(echo "$a" | tr A-Z a-z)" = "$(echo "$owner" | tr A-Z a-z)" ] && acc="$a"; done
        [ -z "$acc" ] && die "several accounts can push (${cands[*]}); rerun with --account LOGIN"
      else acc="${cands[0]}"; fi
    fi
    [ "$(perm "$acc" "$repo")" = none ] && die "$acc has no access to $repo"
    dir="${dir:-$(basename "$repo")}"
    if [ -d "$dir/.git" ]; then
      cur="$(git -C "$dir" remote get-url origin 2>/dev/null || true)"
      [ "$(parse "$cur")" = "$repo" ] || die "$dir is a git repo with origin '$cur', not $repo"
    elif [ -e "$dir" ] && [ -n "$(ls -A "$dir" 2>/dev/null)" ]; then
      die "$dir exists and is not empty / not a git repo"
    else
      GH_TOKEN="$(gh auth token --user "$acc")" gh repo clone "$repo" "$dir" -- -c credential.helper= >/dev/null
    fi
    id="$(GH_TOKEN="$(gh auth token --user "$acc")" gh api user --jq .id)"
    git -C "$dir" remote set-url origin "https://github.com/$repo.git"
    git -C "$dir" config --local --unset-all credential.helper 2>/dev/null || true
    git -C "$dir" config --local --add credential.helper ''
    git -C "$dir" config --local --add credential.helper "!f() { test \"\$1\" = get && echo username=$acc && echo password=\$(gh auth token --user $acc); }; f"
    git -C "$dir" config --local user.name "$acc"
    git -C "$dir" config --local user.email "${id}+${acc}@users.noreply.github.com"
    git -C "$dir" config --local gamefactory.ghAccount "$acc"
    echo "bound: $dir -> $repo as $acc ($(perm "$acc" "$repo"))"
    git -C "$dir" ls-remote --heads origin >/dev/null && echo "auth check: OK (ls-remote)"
    ;;
  status)
    dir="${1:-.}"
    echo "repo:    $(git -C "$dir" remote get-url origin 2>/dev/null || echo '-')"
    echo "account: $(git -C "$dir" config --local gamefactory.ghAccount || echo 'not bound (uses global/active)')"
    echo "author:  $(git -C "$dir" config user.name) <$(git -C "$dir" config user.email)>"
    ;;
  *) sed -n '2,13p' "$0"; exit 1 ;;
esac
