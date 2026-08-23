# HD-104 — Gating staging

**Builds:** `deploy-staging.yml`, and the first real gate.
**Teaches:** what a deployment that waits for a human actually looks like.

## The ticket

> Anything merged to `staging` deploys instantly and unattended. Make it stop and
> ask.

## Step 1 — the workflow

Three lines different from dev: the name, the trigger branch, the environment.

```yaml
name: Deploy to staging

on:
  push:
    branches:
      - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploying $GITHUB_SHA to staging"
```

## Step 2 — the gate

Settings → Environments → `staging`:

- **Required reviewers** → add yourself
- **Prevent self-review** → leave **off** in a solo repo, or nothing can ever be
  approved. In a real team, turn it on.
- **Deployment branches** → *Selected branches* → `staging`

That last one is worth understanding. It says: **only code sitting on the `staging`
branch may ever deploy to the staging environment.** Even if someone wrote a
workflow that tried to deploy staging from a feature branch, GitHub would refuse at
the environment level. The workflow file is not the last line of defence.

## Step 3 — the promotion

This is the first promotion, and the shape of it matters:

```bash
gh pr create --base staging --head develop \
  --title "promote: develop -> staging"
```

**base `staging`, head `develop`.** Climbing.

Two things this is *not*:

- **Not a new branch.** You create nothing. `develop` already exists; it *is* the
  head. A promotion is a PR between two branches that both already exist.
- **Not a local operation.** You never check out `staging`, never pull it, never
  push to it. If you could promote from your laptop, you would have walked around
  your own gate. That is exactly why promotions happen server-side.

Merge it with a **merge commit**, not a squash. Why: [HD-105](hd-105-production-lane.md#squash-or-merge).

## What to look at

Go to the Actions tab. The run is sitting at **`waiting`**.

That's it. That's the deliverable. The workflow triggered, the job hit
`environment: staging`, and GitHub stopped it before step one and went looking for
a human.

Click **Review deployments** → **Approve and deploy**, then look at the deployment
status trail:

```
waiting      13:00:54    ← job stopped
queued       13:12:48    ← you approved
success      13:12:58
```

Twelve minutes of that was the gate. Ten seconds was the work.

## The trap in this ticket

While configuring gates it is very tempting to also switch on, for `main`:

> **Require deployments to succeed before merging** → ☑ production

Don't. Production deploys *from* `main`. So nothing could be merged into `main`
until it had been deployed to production, and it cannot deploy to production until
it is merged into `main`. With admin enforcement on, `main` becomes permanently
unmergeable.

The rule for all three rungs:

> **Never require a deployment from the environment that the branch you're merging
> *into* deploys to. Require the one below it.**

- merging into `staging` → require **dev**
- merging into `main` → require **staging**
- merging into `develop` → require **nothing**; it's the bottom rung

Full reasoning in [rules-of-thumb.md](rules-of-thumb.md).

---

Next: **[HD-105 — The production lane](hd-105-production-lane.md)**
