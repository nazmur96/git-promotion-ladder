# HD-103 — The first deployment

**Builds:** the `develop` and `staging` branches, three GitHub Environments, and
`deploy-dev.yml`.
**Teaches:** a trigger and a gate are different things that happen to live in the
same file.

## The ticket

> CI proves the code is correct. It does not prove the code *runs*. Add a dev
> environment and deploy to it automatically.

## Step 1 — the long-lived branches

```bash
git switch -c develop main
git push -u origin develop

git switch -c staging main
git push -u origin staging
```

Create them from an **explicit start point** (`main`), not from wherever you
happen to be standing. Three long-lived branches now exist and none of them will
ever be deleted:

| Branch | Lifetime | Deleted when |
|---|---|---|
| `feature/*` | hours or days | merged |
| `develop`, `staging`, `main` | forever | never |

## Step 2 — the environments

Settings → Environments → New environment. Create `dev`, `staging`, `production`.

Leave all three with **zero rules** for now. That's deliberate. The gates get added
as their own lessons, and it's worth seeing what an ungated environment feels like
first: completely invisible.

## Step 3 — the workflow

```yaml
name: Deploy to dev

on:
  push:
    branches:
      - develop        # ← WHEN the workflow runs

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: dev   # ← WHETHER the job is allowed to proceed

    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Deploying $GITHUB_SHA to dev"
          echo "Triggered by $GITHUB_ACTOR on $GITHUB_REF_NAME"
```

## The distinction that matters

Those two marked lines are the whole ticket.

- **`on:`** decides *when the workflow starts*. It is a trigger. Nothing else
  decides this — not the environment, not the branch rules.
- **`environment:`** decides *whether the job may proceed*. Before step one runs,
  GitHub stops and asks that environment three questions: is this branch allowed?
  is a reviewer required? is there a wait timer?

Right now `dev` has no rules, so it answers *yes* instantly and the job runs. The
gate is there — it's just empty. Production will be the same machinery with the
answers set to "ask a human first."

## Deploying is not building

The deploy step is an `echo`. That is on purpose and it is not a cop-out. Every
mechanism this repo teaches — approvals, wait timers, branch policies, deployment
records, artifact promotion, rollback — is identical whether the last line is
`echo` or `kubectl apply`. Swapping in a real deploy target changes one line and
nothing else.

## What to look at

Merge something into `develop`, then go to the repo's **Environments** panel. There
is now a **deployment record** attached to a commit SHA. Not a branch — a SHA.

That distinction becomes the whole of HD-106.

---

Next: **[HD-104 — Gating staging](hd-104-gating-staging.md)**
