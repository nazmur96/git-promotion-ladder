# HD-105 — The production lane

**Builds:** `deploy-production.yml`, branch protection on `develop` and `staging`,
the production gate — then one change walked all the way up.
**Teaches:** commit identity, and why merge strategy is not a style preference.

## The ticket

> Finish the ladder. Protect the two unprotected branches, gate production, then
> walk one trivial change from a feature branch to production and watch every gate
> fire.

## Step 1 — protect the branches

| | `develop` | `staging` | `main` |
|---|---|---|---|
| Require a pull request | ✓ | ✓ | ✓ |
| Required approvals | 0 | 0 | 0 |
| Require `test` to pass | ✓ | ✓ | ✓ |
| Require branch up to date | — | ✓ | ✓ |
| Applies to admins | no | **yes** | **yes** |
| Must already have deployed to | — | **dev** | **staging** |

`develop` gets the loose version on purpose. It's the bottom rung and it's supposed
to be recoverable without ceremony. `staging` is one step from production, so no
shortcuts.

**Required approvals is 0** because this is a solo repo — GitHub will not let you
approve your own PR, so requiring 1 would deadlock everything. In a team it's 1 or 2.

Reproduce it with [`setup/03-branch-protection.sh`](../setup/03-branch-protection.sh).

## Step 2 — gate production

Settings → Environments → `production`:

- **Required reviewers** → yourself
- **Wait timer** → 1 minute
- **Deployment branches** → *Selected* → `main`

The wait timer is a cooling-off window. If someone realises mid-deploy that this is
the wrong thing, there's a minute to hit cancel. Real teams use 5–30 minutes for
production. You will feel the cost of it in [HD-107](hd-107-rollback.md) — during an
outage, that minute is expensive, and that trade-off is real.

## Step 3 — walk one change up

```
feature branch          squash        → develop   → dev deploy       (no gate)
develop                 merge commit  → staging   → staging deploy   (approval)
staging                 merge commit  → main      → production       (approval + timer)
```

An actual run of it:

```
develop  f0ef343  dev deploy: success
staging  adc1137  waiting 11:21:05 → success 11:23:59   (approved)
main     2a69f78  waiting 11:33:24 → success 11:34:59   (approved + 60s timer)
```

`f0ef343` — the commit that was actually authored — is contained in all three
branches. That is the property the next section is about.

## <a name="squash-or-merge"></a>Squash or merge?

> **Squash features. Merge promotions.** Never the other way round.

A commit's SHA is a hash of its content, its parents, and its metadata. Change any
of those and you get a different commit — one that may hold identical *content* but
is a **different object**.

| Operation | Does the original SHA survive? |
|---|---|
| fast-forward | **yes** — the pointer moves |
| merge commit | **yes** — the original is a parent |
| squash | **no** — new commit, new SHA |
| rebase | **no** |
| cherry-pick | **no** |
| amend | **no** |

Squash and rebase and cherry-pick **copy**. Merge and fast-forward **move**.

**For a feature:** copying is what you want. The eleven commits saying `wip`,
`fix typo`, `actually fix typo` are scaffolding. Squash them into one clean commit.
Nothing downstream needs to point at them.

**For a promotion:** copying is a disaster. The question a promotion has to answer
is *"is the exact thing that was tested in staging the exact thing now in
production?"* — and the only way to answer it is:

```bash
git merge-base --is-ancestor <commit> origin/main
```

Squash-merge a promotion and that returns **no**, forever, even though the files are
byte-identical. You've swapped containment ("this commit is in that branch") for
mere similarity ("these look the same"). One is checkable, the other is a vibe.

This mistake was made twice while building this repo. See
[mistakes.md](mistakes.md#8).

## Branch from your target

Related, and separate:

> **Branch from the thing you are going to merge into.**

A feature merges into `develop`, so branch from `develop`. Branch from `main`
instead and you're building on production code, missing everything already merged
to `develop` — your PR shows a confusing diff and you drag old code forward.

Note this is a *different* rule from the deployment one, and they are easy to fuse
into a wrong sentence. Features need no deployment gate **not** because they were
branched from `develop`, but because the code has never run anywhere, so there is
no deployment to point at. Branch a feature off `staging` and the answer is still
"no gate" — the origin isn't what decides.

| Question | Answer |
|---|---|
| Where do I branch from? | The branch I'm merging into. |
| What deployment do I require? | The environment one rung below the branch I'm merging into. |

The exception is long-lived branches themselves, which are created from `main` once
and then never again.

---

Next: **[HD-106 — Build once](hd-106-build-once.md)**
