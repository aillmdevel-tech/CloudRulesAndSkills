---
name: github-account-router
description: Use whenever work involves a GitHub repository — the user gives a github.com link or owner/repo, asks to clone, push, commit and upload, open a PR, "залей/загрузи изменения в репо", "вот ссылка на репозиторий", or a git push/gh call fails with 403/404/auth errors. Alex has several GitHub accounts logged into gh; this picks the account that has push access to that repo and binds the repo to it LOCALLY (credential helper + commit author per repository) without switching the global/active gh account, and handles logging in a new account.
---

# GitHub account router

Several accounts are logged into `gh` on this Mac (check: `gh auth status`). Each repository must push
as the account that owns/has access to it. Never fix this by switching the global account.

Script: `~/.claude/skills/github-account-router/scripts/repo_account.sh`

## Procedure
1. **Before cloning/pushing to any GitHub repo** (link from Alex, or the current repo's `origin`):
   `repo_account.sh check <url>` → shows admin/push/read/none for every logged-in account.
2. **Bind**: `repo_account.sh setup <url> [dir]` — clones if needed (or configures the existing local
   repo with the same origin) and sets, in `.git/config` only:
   - credential helper → `gh auth token --user <login>` (independent of the active gh account)
   - `user.name` = login, `user.email` = `<id>+<login>@users.noreply.github.com`
   - `gamefactory.ghAccount` = login (shown by `repo_account.sh status`)
   If several accounts can push and none is the owner → ask Alex which one (`--account LOGIN`).
   If Alex wants a specific commit email instead of noreply, set `git config user.email` locally.
3. **Already bound?** `repo_account.sh status [dir]` — if `gamefactory.ghAccount` is set, just work.
4. **gh commands** (PR, issues, releases) in that repo: prefix with the bound account's token —
   `GH_TOKEN=$(gh auth token --user <login>) gh pr create ...` — don't `gh auth switch`.
5. **No account has access** → tell Alex which accounts are logged in and offer to add one:
   run `gh auth login --hostname github.com --git-protocol https --web` (Alex confirms the one-time
   code in the browser — never type passwords). Login makes the new account active, so afterwards
   restore the previously active one with `gh auth switch --user <previous>`. Then rerun setup.

## Rules
- Pushing, creating repos, PRs — only when Alex asked (normal git rules). Don't change
  `git config --global` or the active gh account unless Alex explicitly asks.
- Report which account a push went to (`repo_account.sh status`).
- Tokens never go into files, URLs or chat output.
