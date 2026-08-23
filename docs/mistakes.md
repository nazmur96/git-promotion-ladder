# The mistakes ledger

Every wrong turn taken while building this, in order, with the fix. Some were
designed into the exercise; most were not.

---

### 1. `git pull develop`

**What happened:** ran while standing on a different branch, expecting to update
`develop`.

**Why it's wrong:** git parses the first argument as a **remote**, not a branch. It
went looking for a remote called `develop`.

**Fix:** `git switch develop` then a bare `git pull`. Pull updates the branch you
are standing on. Nothing else.

---

### 2. `git branch -d` refused after a squash merge

**What happened:** the branch was merged and GitHub had deleted it remotely, but
`git branch -d` locally said it wasn't merged.

**Why:** the squash created a **new commit** with a different SHA. The original
commit is genuinely not an ancestor of `develop`, so git is technically right.

```bash
git merge-base --is-ancestor <branch-tip> origin/develop   # → false
```

**Fix:** prove it's safe by content, then force:

```bash
git diff <branch> origin/develop    # must be empty
git branch -D <branch>
```

**Lesson:** `-d` asks about *containment*. After a squash, containment is gone even
though the content survived. This is the first hint of what [HD-105](hd-105-production-lane.md#squash-or-merge)
is about.

---

### 3. Reading "allow admins to bypass" as the gate itself

**What happened:** assumed unchecking admin bypass would protect the environments.

**Why it's wrong:** all three environments had `rules: []`. There was nothing to
bypass. Admin enforcement is a **qualifier on existing rules**, not a rule.

**Fix:** add actual rules — required reviewers, deployment branch policies — then
decide whether admins are bound by them.

---

### 4. Requiring a **production** deployment before merging to `main`

**What happened:** switched on *"require deployments to succeed before merging"* on
`main` and ticked `production`, reasoning "you shouldn't merge before it deploys."

**Why it's wrong:** production deploys **from** `main`. Nothing can be merged until
it's deployed, and it can't deploy until it's merged. With admin enforcement on,
`main` became permanently unmergeable.

**Fix:** untick it; require the environment **one rung below** — `staging`. See
[rule 6](rules-of-thumb.md#6-require-the-deployment-one-rung-below-never-the-same-one).

**Note:** this field is not exposed by the REST branch-protection API. Only GraphQL
`requiredDeploymentEnvironments` shows it.

---

### 5. Base and head inverted on a promotion PR

**What happened:** opened the `develop → staging` promotion with `--base develop`.

**Why it's wrong:** base is the **destination**. That PR proposed to merge staging
*into* develop — backwards down the ladder.

**Fix:** `--base staging --head develop`. Read the direction out loud first.

Later the same field appeared in an IDE labelled **"base reference"**, pre-filled
with the wrong branch. Same trap, different word.

---

### 6. Thinking a promotion was a local `switch` and `pull`

**What happened:** assumed promoting meant checking out `staging` and pulling
`develop` into it locally.

**Why it's wrong:** that bypasses the gate entirely. Local merges answer to nothing.

**Fix:** promotions are PRs, merged server-side. **If you can do it from your laptop,
you have walked around your own gate.**

---

### 7. Declaring a ticket done while the deploy sat at `waiting`

**What happened:** the workflow had triggered, so it looked finished.

**Why it's wrong:** `waiting` means the job has not run a single step. The gate
pausing *is* the deliverable, and it hadn't been cleared.

**Fix:** check the deployment status trail, not just "a run exists".

---

### <a name="8"></a>8. Committing straight to `develop`, then squash-merging a promotion

**What happened:** made changes directly on `develop` instead of a feature branch,
then squash-merged the `develop → main` promotion.

**Why it's wrong:** the squash minted a brand-new commit on `main` that exists
nowhere else. `main` shared **no ancestry** with `develop` or `staging`. Content was
identical everywhere; identity was gone.

**Fix:** backmerge to repair the chain, and merge-commit every promotion from then
on. See [HD-105](hd-105-production-lane.md#squash-or-merge).

This happened **twice**. The root cause was not ignorance — it was a wrong-by-default
dropdown at the end of a long session. The durable fix is to automate promotion with
the merge strategy hardcoded, so a human never picks. (Note: `GITHUB_TOKEN`-authored
merges do not trigger downstream workflows, so that automation needs a PAT or a
GitHub App token.)

---

### 9. A promotion PR that skipped a rung

**What happened:** opened `develop → main` directly, bypassing `staging`.

**Why it's wrong:** production then ran code that had never been through the staging
environment. Nothing enforced the ladder because `main`'s deployment requirement was
not behaving (see #11).

**Fix:** promote one rung at a time, always.

---

### 10. A dropped line in a long paste — twice

**What happened:** once a `git add` at the end of a block never ran; once a `sed`
bumping the version at the start never ran.

**Why it matters:** the second one merged cleanly with green CI and only failed at
the build step, four minutes later.

**Fix:** `grep` the thing you just changed *before* committing. Three seconds.

**The good part:** the pipeline caught it anyway. The build refused to rebuild an
existing version → dev never deployed → the `staging` rule refused the promotion.
Sealed off three rungs down, unattended.

---

### <a name="11"></a>11. Two `main` rules that did not behave as documented — UNRESOLVED

Both of these are switched on, with `isAdminEnforced: true`, and both allowed a merge
they should have blocked:

| Rule | Expected | Observed |
|---|---|---|
| `requiredDeploymentEnvironments: ["staging"]` | block merge until the commit has a successful staging deployment | merged with a head commit that had **no** staging deployment |
| `requiresStrictStatusChecks: true` | block merge until the head branch is up to date with base | merged while `staging` was **1 commit behind** `main`, with no "Update branch" event in the PR timeline |

GitHub's own wording is ambiguous about *what* must have been deployed:

> *Choose which environments must be successfully deployed to before branches can be
> merged into a branch that matches this rule.*

The PR's head commit? The environment's most recent deployment, whatever commit that
was? Something else? Three readings, no statement either way.

**This is written down rather than explained because the honest answer is "I don't
know yet."** If you know, please open an issue.
