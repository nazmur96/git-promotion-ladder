# Gates reference

Every rule on every branch and environment, as actually configured, plus how to
read it back from the API.

## Branch protection

| | `develop` | `staging` | `main` |
|---|---|---|---|
| Require a pull request | ✓ | ✓ | ✓ |
| Required approvals | 0 | 0 | 0 |
| Required status checks | `test` | `test` | `test` |
| Require branch up to date (`strict`) | — | ✓ | ✓ |
| `enforce_admins` | no | **yes** | **yes** |
| `requiredDeploymentEnvironments` | — | `dev` | `staging` |

**Why 0 approvals:** GitHub does not let you approve your own PR. In a solo repo,
requiring 1 deadlocks everything. In a team this is 1 or 2.

**Why `develop` is loose:** it's the bottom rung and needs to stay recoverable
without ceremony.

## Environments

| | `dev` | `staging` | `production` |
|---|---|---|---|
| Required reviewers | — | owner | owner |
| `prevent_self_review` | — | false | false |
| Wait timer | — | — | **1 minute** |
| Deployment branches | any | `staging` only | `main` only |

**Why `dev` has no rules:** deliberate. It's the proving ground — the first place
code actually runs, and it's allowed to break. Gating it would grind the team for no
safety gain.

**Why `prevent_self_review: false`:** solo repo. In a team, turn it on.

## Reading it back

Branch protection (REST):

```bash
gh api repos/:owner/:repo/branches/staging/protection --jq '{
  pr: (.required_pull_request_reviews != null),
  approvals: .required_pull_request_reviews.required_approving_review_count,
  checks: .required_status_checks.contexts,
  strict: .required_status_checks.strict,
  enforce_admins: .enforce_admins.enabled
}'
```

**`requiredDeploymentEnvironments` is not in the REST response.** It only exists in
GraphQL:

```bash
gh api graphql -f query='
{
  repository(owner: "OWNER", name: "REPO") {
    branchProtectionRules(first: 10) {
      nodes {
        pattern
        requiresDeployments
        requiredDeploymentEnvironments
        requiresStrictStatusChecks
        isAdminEnforced
      }
    }
  }
}' --jq '.data.repository.branchProtectionRules.nodes[]'
```

Environments:

```bash
gh api repos/:owner/:repo/environments/production \
  --jq '[.protection_rules[] | {type, wait_timer, reviewers: [.reviewers[]?.reviewer.login]}]'

gh api repos/:owner/:repo/environments/production/deployment-branch-policies \
  --jq '.branch_policies[].name'
```

Deployment history for one environment:

```bash
gh api repos/:owner/:repo/deployments \
  --jq '[.[] | select(.environment=="production")] | .[0:5] | .[] | "\(.sha[0:7]) \(.created_at)"'
```

The status trail for a single deployment — this is where you see a gate holding:

```bash
gh api repos/:owner/:repo/deployments/<ID>/statuses --jq '.[] | "\(.state)  \(.created_at)"'
```

```
success      14:28:25
in_progress  14:28:18
queued       14:28:13   ← approved here
waiting      14:27:13   ← gate held it from here
```

## Caveat

Two `main` rules did not behave as documented during this build. See
[mistakes.md](mistakes.md#11) before relying on them.
