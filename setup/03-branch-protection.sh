#!/usr/bin/env bash
# Branch protection for develop, staging and main.
#
# develop - loose:  PR + tests, admins may bypass. bottom rung, stays recoverable.
# staging - strict: PR + tests + up-to-date, admins bound.
# main    - strict: same as staging.
#
# Required approvals is 0 on purpose: GitHub will not let you approve your own PR,
# so requiring 1 deadlocks a solo repo. In a team, raise it.
set -euo pipefail

REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
echo "repo: $REPO"

protect() {
  local branch="$1" strict="$2" admins="$3"
  gh api -X PUT "repos/$REPO/branches/$branch/protection" --input - >/dev/null <<JSON
{
  "required_status_checks": { "strict": $strict, "contexts": ["test"] },
  "enforce_admins": $admins,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null
}
JSON
  echo "$branch: PR required, 'test' required, strict=$strict, enforce_admins=$admins"
}

protect develop false false
protect staging true  true
protect main    true  true

echo
echo "NOT set by this script - REST cannot write it. Do it in the UI:"
echo "  Settings -> Branches -> Require deployments to succeed before merging"
echo "    staging rule -> tick 'dev'"
echo "    main rule    -> tick 'staging'"
