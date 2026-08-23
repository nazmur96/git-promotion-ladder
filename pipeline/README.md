# Pipeline workflows

The three deployment workflows. Copy them into `.github/workflows/` **after** the
environments exist:

```bash
cp pipeline/workflows/*.yml .github/workflows/
```

They live here rather than in `.github/workflows/` because `deploy-production.yml`
triggers on push to `main` — shipping it live in a fresh clone fires a production
deploy against an environment that doesn't exist, looking for an artifact that was
never built. Red X, no fault of yours.

| File | Trigger | Environment | What it does |
|---|---|---|---|
| `deploy-dev.yml` | push to `develop` | `dev` | **builds** the wheel, records its sha256, stores it, then deploys it |
| `deploy-staging.yml` | push to `staging` | `staging` | finds the artifact for this version, downloads it, verifies the checksum |
| `deploy-production.yml` | push to `main`, or manual | `production` | same, plus a `workflow_dispatch` input to redeploy any earlier version |

Only `deploy-dev.yml` ever builds anything. That is the whole point — see
[HD-106](../docs/hd-106-build-once.md).

`deploy-production.yml` is also the rollback lever:

```bash
gh workflow run deploy-production.yml --ref main -f version=0.1.0
```

All three need `permissions: actions: read` to look artifacts up across workflow
runs.
