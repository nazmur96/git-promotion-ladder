# Standing the pipeline up on your own fork

Requires the [GitHub CLI](https://cli.github.com/) authenticated as a repo admin.

Run in order, from the repo root:

```bash
./setup/01-branches.sh
./setup/02-environments.sh
./setup/03-branch-protection.sh
cp pipeline/workflows/*.yml .github/workflows/
```

Then commit the workflows on a feature branch and promote them up, the way the
tickets describe.

## One thing the scripts can't do

**"Require deployments to succeed before merging"** is not writable through the REST
branch-protection API. Set it by hand:

Settings → Branches → edit the rule → **Require deployments to succeed before
merging**:

- on the `staging` rule → tick **`dev`**
- on the `main` rule → tick **`staging`**
- never tick the environment that branch itself deploys to — see
  [rule 6](../docs/rules-of-thumb.md)

## Why the workflows don't ship in `.github/workflows/`

`deploy-production.yml` triggers on push to `main`. Ship it live and it fires
immediately against a `production` environment that doesn't exist yet, against an
artifact that was never built — a red X on a fresh clone, before you've done
anything wrong. Copy them in once the environments exist.
