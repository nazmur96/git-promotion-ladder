# Rules of thumb

The short list. Everything here was learned by getting it wrong first — see
[mistakes.md](mistakes.md).

---

### 1. Merge → branch rules. Deploy → environment rules.

*"Why can't I merge?"* → Settings → **Branches**.
*"Why is my deploy stuck?"* → Settings → **Environments**.

Two independent layers. Confusing them is the biggest single source of wasted time.

### 2. Code only moves forward.

`feature → develop → staging → main`. Never sideways, never down. The one exception
is a **backmerge**, which exists to repair the chain, not to deliver anything.

### 3. Base is the destination. Head is the source.

Before clicking create, read the direction out loud: *"this branch ends up in
`___`."* Your IDE's "base reference" field means the same thing and it guesses wrong.

A PR's `head` has nothing to do with git's `HEAD`. Same word, unrelated.

### 4. Branch from the thing you're going to merge into.

Feature → branch from `develop`. Long-lived branches are created from `main` once
and never again. Hotfixes branch from `main`, because that's where they land.

### 5. Squash features. Merge promotions.

A feature's history is scaffolding — squash it. A promotion's history is the record
— preserve it. Squash a promotion and `git merge-base --is-ancestor` says *no*
forever, even when the files are identical. You trade a checkable fact for a vibe.

### 6. Require the deployment one rung *below*, never the same one.

- into `staging` → require **dev**
- into `main` → require **staging**
- into `develop` → require **nothing**

Requiring the environment that branch deploys to is a deadlock: it can't deploy
until it's merged, and it can't merge until it's deployed.

### 7. You can only require a deployment that has already happened.

Which is why `develop` has no deployment gate. It's the bottom rung — nothing has
run below it. That is also what `dev` is *for*: it's the first place code actually
runs, so it's allowed to break.

### 8. Tests prove it's correct. Deployments prove it runs.

Tests run in a fresh sandbox. Deploying is where you find out the config is wrong,
the env var is missing, it crashes on boot. Demand both before code climbs.

### 9. Promotions happen server-side.

You never check out `staging`, never pull it, never push to it. You open a PR and
merge it. **If you can promote from your laptop, you have walked around your own
gate.**

### 10. Build once. Promote the artifact, not the source.

Same bytes in every environment, checksum-verified. This is also what makes rollback
a download instead of a rebuild.

### 11. Versions are immutable.

Once bytes are published under a version, that name is spent forever. Enforce it in
CI, don't rely on discipline.

### 12. Green is not safe.

Every gate answers *"is this the code we approved?"* None answers *"is the code
correct?"* Nothing can.

### 13. Stop the bleeding first, fix the repo second.

Redeploy the last good artifact. *Then* work out the fix. A rollback that only moves
the deployment is a timer — the repo still says the broken version is current, and
the next merge to `main` reships it.

### 14. Build the rollback lever before you need it.

You cannot build one during an outage. It ships months early and sits unused.

### 15. Keep releases small and single-purpose.

Not for tidiness — for recoverability. Bundle infrastructure with product changes
and a revert can't separate them.

### 16. Read the output before you commit.

Two long pastes silently dropped a line while building this repo. `grep` the thing
you just changed. It costs three seconds and it caught neither time.
