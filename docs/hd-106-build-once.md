# HD-106 — Build once, promote the artifact

**Builds:** a build job on `develop`, and deploy jobs that download instead of
rebuild.
**Teaches:** how to *prove* the thing in production is the thing you tested.

## The problem

Every deploy job so far starts with `checkout`. If those jobs actually built the
app, you would build it three times — once per environment.

Three builds are three chances to differ. A dependency resolves to a newer patch. A
base image gets retagged. A download flakes and a cache fills the gap. You test
artifact A in staging and ship artifact B to production.

That is the real shape of "but it worked in staging".

## The fix

Build **once**, on `develop`. Store the result. Staging and production **download
that same file** and refuse to rebuild it.

Every stage prints the artifact's `sha256`. If all three print the same digest, the
same bytes ran in all three places. That digest is the deliverable.

```
dev         0.1.0   built here            e3e8093…cd45a   12:30
staging     0.1.0   from run 32639594664  e3e8093…cd45a   12:43
production  0.1.0   from run 32639594664  e3e8093…cd45a   12:50
```

Staging built nothing. It read `0.1.0` out of `pyproject.toml`, asked GitHub *"which
run produced `helpdesk-0.1.0`?"*, got dev's run from thirteen minutes earlier,
downloaded that exact zip, and verified the wheel against the checksum dev recorded.

## Why the key is the version, not the commit SHA

The obvious idea is to name the artifact after the commit. It doesn't work.

Merge-commit promotions mint a **new tip SHA at every rung** — `f0ef343` becomes
`adc1137` becomes `2a69f78`. The branch tip is a different object at each level even
though the code is identical. So the tip SHA can't be the lookup key.

The version in `pyproject.toml` is the thing that stays constant as code climbs.
That is why real teams bump a version to ship: **the version is the unit of
promotion.**

## The guard that makes it a rule

```yaml
- name: Refuse to build a version that already exists
  env:
    GH_TOKEN: ${{ github.token }}
    VERSION: ${{ steps.version.outputs.value }}
  run: |
    COUNT=$(gh api "repos/$GITHUB_REPOSITORY/actions/artifacts?name=helpdesk-$VERSION" --jq '.total_count')
    if [ "$COUNT" != "0" ]; then
      echo "::error::helpdesk-$VERSION was already built. Bump the version in pyproject.toml."
      exit 1
    fi
```

Without this, "build once" is a suggestion. With it, publishing two different sets
of bytes under one version name is impossible.

**It fired for real while building this.** A `sed` line was dropped from a paste, so
the version never got bumped. CI passed. The PR merged. Then:

```
##[error] helpdesk-0.1.0 was already built. Bump the version in pyproject.toml.
```

And because the build failed, dev never deployed that commit — and because dev never
deployed it, the `staging` branch rule refused to accept it. **One typo, sealed off
three rungs down, with nobody watching.** That is what a gate is for.

## The mechanism: reaching into another workflow run

Artifacts are normally trapped inside the run that produced them. Two pieces let
staging reach back into dev's run:

```yaml
- name: Locate the build that produced it
  id: find
  env:
    GH_TOKEN: ${{ github.token }}
    VERSION: ${{ steps.version.outputs.value }}
  run: |
    RUN_ID=$(gh api "repos/$GITHUB_REPOSITORY/actions/artifacts?name=helpdesk-$VERSION" \
      --jq '.artifacts[0].workflow_run.id // empty')
    if [ -z "$RUN_ID" ]; then
      echo "::error::No artifact named helpdesk-$VERSION exists. That version was never built."
      exit 1
    fi
    echo "run_id=$RUN_ID" >> "$GITHUB_OUTPUT"

- uses: actions/download-artifact@v4
  with:
    name: helpdesk-${{ steps.version.outputs.value }}
    path: dist
    run-id: ${{ steps.find.outputs.run_id }}      # ← the cross-run part
    github-token: ${{ github.token }}

- run: cd dist && sha256sum -c SHA256SUMS
```

This needs `permissions: actions: read` on the workflow.

Full files: [`pipeline/workflows/`](../pipeline/workflows/).

## What to look at

Compare the `sha256` line in the dev, staging and production logs. Sixty-four
identical characters means you can answer *"is production running what we tested?"*
with evidence instead of a shrug.

---

Next: **[HD-107 — Rollback under pressure](hd-107-rollback.md)**
