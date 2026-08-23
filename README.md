# The Git Promotion Ladder

A worked example of moving code from a developer's laptop to production through
three environments, with a real gate at every step — built by hand, one ticket at
a time, on GitHub.

This is not a tutorial someone wrote from memory. Every command, every failure and
every timing in `docs/` came out of actually building it, including the mistakes.

```
  BRANCH                        ENVIRONMENT
  ──────                        ───────────

  feature/*
     │  squash merge
     ▼
  develop  ────────────────►    dev          no gate. this is the proving ground.
     │  merge commit
     ▼
  staging  ────────────────►    staging      human approval.
     │  merge commit                          must already have deployed to dev.
     ▼
  main     ────────────────►    production   human approval + wait timer.
                                             must already have deployed to staging.
                                             only main may deploy here.
```

## The one idea

GitHub has two independent layers of protection, and confusing them is the single
biggest source of "why is this stuck?".

| | Branch protection | Environments |
|---|---|---|
| Lives in | Settings → Branches | Settings → Environments |
| Guards | **merging** | **deploying** |
| Asks | "can this code get *in* to this branch?" | "can this code get *out* to this running place?" |
| Blocks | the merge button | the job, mid-run |
| Example rule | must open a PR, tests must pass | a human must click Approve |

> **Merge → branch rules. Deploy → environment rules.**
>
> *"Why can't I merge?"* → Settings → Branches.
> *"Why is my deploy stuck?"* → Settings → Environments.

## The seven tickets

| | Ticket | What it builds | What it teaches |
|---|---|---|---|
| 1 | [HD-101](docs/hd-101-first-pull-request.md) | the first pull request | a PR with no checks on it is just a slower `git push` |
| 2 | [HD-102](docs/hd-102-continuous-integration.md) | CI, then a deliberate red build | your laptop is not the runner |
| 3 | [HD-103](docs/hd-103-first-deployment.md) | `deploy-dev.yml` | triggers and environments are different things |
| 4 | [HD-104](docs/hd-104-gating-staging.md) | the staging gate | a deployment that waits for a human |
| 5 | [HD-105](docs/hd-105-production-lane.md) | the full ladder | promotions are server-side, and merge strategy decides identity |
| 6 | [HD-106](docs/hd-106-build-once.md) | build once, promote the artifact | prove the bytes in production are the bytes you tested |
| 7 | [HD-107](docs/hd-107-rollback.md) | rollback under pressure | rollback speed is bought *before* the incident |

Read them in order. Each one exists because the previous one left a hole.

## Also in here

- **[Rules of thumb](docs/rules-of-thumb.md)** — the short list. If you read one file, read this one.
- **[Mistakes ledger](docs/mistakes.md)** — every wrong turn taken while building this, and what the fix was. Most of the learning is here.
- **[Gates reference](docs/gates-reference.md)** — the exact settings on every branch and environment, with the API calls to reproduce them.

## Running it yourself

```bash
git clone https://github.com/nazmur96/git-promotion-ladder
cd git-promotion-ladder
python3 -m unittest discover -s tests
python3 -m helpdesk list --priority high
```

The app is deliberately boring — a support-ticket CLI with about a hundred lines of
Python. It exists so the pipeline has something to carry. Nothing in `docs/` is
about the app.

To stand the pipeline up on your own fork, see **[setup/](setup/)**. The three
deployment workflows ship in [`pipeline/workflows/`](pipeline/workflows/) rather
than `.github/workflows/` on purpose — dropping them in live would fire a
production deploy against environments that don't exist yet.

## Further reading

The official docs, for when you want the authoritative version:

- [GitHub Actions documentation](https://docs.github.com/en/actions) — start here
- [Workflow syntax reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions) — everything valid inside a `.yml`
- [Deployment environments (REST)](https://docs.github.com/en/rest/deployments/environments) — the API behind Settings → Environments
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) — the other layer

## Honest caveats

- **Deployments are simulated.** Every deploy step is an `echo`. Nothing is hosted,
  nothing costs money, no credentials exist anywhere in this repo. The gates,
  approvals, artifacts and deployment records are all completely real — only the
  thing at the far end is pretend.
- **Two rules did not behave as documented.** On `main`, both *"require deployments
  to succeed before merging"* and *"require branches to be up to date"* allowed
  merges they should have blocked. This is written up honestly in
  [mistakes.md](docs/mistakes.md) rather than papered over. If you know why, open an
  issue — genuinely.
- **This is a solo setup.** Required reviewers are set to the repo owner and
  `prevent_self_review` is off, because otherwise nothing could ever be approved. In
  a real team both of those flip.

## Licence

MIT — see [LICENSE](LICENSE).
