#!/usr/bin/env bash
# Create the three environments and their gates.
#
# dev        - no rules. the proving ground.
# staging    - required reviewer, staging branch only.
# production - required reviewer, 1-minute wait timer, main branch only.
set -euo pipefail

REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
USER_ID=$(gh api user --jq .id)
echo "repo: $REPO"

# dev - deliberately ungated
gh api -X PUT "repos/$REPO/environments/dev" >/dev/null
echo "dev: created, no rules (deliberate)"

gate() {
  local env="$1" branch="$2" timer="$3"
  gh api -X PUT "repos/$REPO/environments/$env" --input - >/dev/null <<JSON
{
  "wait_timer": $timer,
  "prevent_self_review": false,
  "reviewers": [{"type": "User", "id": $USER_ID}],
  "deployment_branch_policy": {
    "protected_branches": false,
    "custom_branch_policies": true
  }
}
JSON
  # only this branch may deploy here
  gh api -X POST "repos/$REPO/environments/$env/deployment-branch-policies" \
    -f name="$branch" >/dev/null 2>&1 || echo "  (branch policy for $branch already present)"
  echo "$env: reviewer set, wait timer ${timer}m, deploys only from '$branch'"
}

gate staging    staging 0
gate production main    1

echo
echo "prevent_self_review is false because this is a solo setup."
echo "In a team, set it to true."
