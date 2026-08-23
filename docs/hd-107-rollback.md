# HD-107 — Rollback under pressure

**Builds:** a `workflow_dispatch` rollback lever, then a real incident.
**Teaches:** rollback speed is bought *before* the incident, not during it.

## The setup

Ship `0.2.0`, adding an `--owner` filter with a one-character typo in it:

```python
tickets = [t for t in tickets if t.ownr == args.owner]
#                                  ^^^^
```

Everything is green. Tests pass — no test covers `--owner`. The build passes. All
three deploys succeed. Digests match at every rung. `0.2.0` reaches production
clean.

Two hours later: *"`helpdesk list --owner alex` just crashes."*

> **Green is not safe.** Every gate in this repo answers *"is this the code we
> approved?"* None of them answers *"is the code correct?"* Nothing can. That gap is
> permanent, and rollback is how you live with it.

## The first sixty seconds

Two wrong instincts:

- **Fix the typo and push it up the ladder.** It's one character! But that's three
  PRs, two approvals, a wait timer and a fresh build — twenty minutes minimum with
  production broken the whole time. You'd be optimising for elegance while customers
  are on fire.
- **Force-push `main` back one commit.** Fast, and it destroys the audit trail,
  breaks every clone, and won't work anyway because `main` is admin-enforced.

The right move is the lever:

```bash
gh workflow run deploy-production.yml --ref main -f version=0.1.0
```

No commit. No PR. No build. It triggers the production workflow and tells it to
deploy `0.1.0` instead of whatever `main` declares. The artifact still exists — it's
the one that ran fine that morning.

```
14:27:10  dispatched
14:27:13  waiting          ← the gate
14:28:13  queued           ← approved (60s: wait timer + human)
14:28:25  success
```

**75 seconds, 7 of which were work.** Production back on `0.1.0`, digest
`e3e8093…cd45a`, byte-identical to that morning.

## The lever

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to deploy, e.g. 0.1.0. Blank = whatever main declares.'
        required: false
        default: ''

# ...

- name: Decide which version to deploy
  id: version
  env:
    REQUESTED: ${{ inputs.version }}     # ← never inline user input into run:
  run: |
    if [ -n "$REQUESTED" ]; then
      VERSION="$REQUESTED"
      echo "::warning::Manual deploy requested: $VERSION (not the version on main)"
    else
      VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
    fi
    echo "value=$VERSION" >> "$GITHUB_OUTPUT"
```

Two things worth copying:

- **The input goes through `env:`, never straight into the `run:` line.**
  Interpolating `${{ inputs.anything }}` directly into a shell command is how
  workflows get command-injected.
- **This has to exist before you need it.** You cannot build a rollback mechanism
  during an outage. It ships months earlier and sits unused, which is exactly why it
  gets deprioritised, which is exactly why outages last hours.

**And it only works because of [HD-106](hd-106-build-once.md).** If each environment
rebuilt from source, rolling back would mean rebuilding six-week-old code against
dependencies that have moved and a base image that's been retagged. That is not a
rollback, it's an archaeology project at 2am.

## A rollback that only moves the deployment is a timer, not a fix

After the dispatch:

```
main declares:          0.2.0   ← broken
production is running:  0.1.0
```

**The repo is now lying about what's deployed.** And the production workflow fires
on *any* push to `main` — so the next merge, for any reason, quietly reships `0.2.0`
and the incident returns with nobody having touched the bug.

## Closing the gap: revert or roll forward?

**Option A — revert the promotion.**

```bash
git revert -m 1 018d4c9
```

`-m 1` is required for a merge commit: a merge has two parents and git can't guess
which history you want to keep. `1` means the first parent — the branch you merged
*into*.

**But it was the wrong choice here.** That merge carried three things: the version
bump, the broken filter, **and the rollback lever itself**. Reverting would have
deleted the lever that just saved the day.

> **A release is an all-or-nothing unit.** Bundle infrastructure changes with product
> changes and a revert can't separate them. This is the real argument for small,
> single-purpose releases — not tidiness, recoverability.

**Option B — roll forward.** Fix the typo, bump to `0.3.0`, walk the ladder.

Take B when the fix is small and understood. Take A when the change is large, the
cause is unclear, or you can't reason about a fix under pressure.

## Capture the incident as a test first

Before fixing anything:

```python
def test_list_filters_by_owner(self):
    result = self.run_cli("list", "--owner", "alex")
    self.assertEqual(result.returncode, 0)
    self.assertIn("INC-101", result.stdout)
    self.assertNotIn("INC-102", result.stdout)
```

Run it. Watch it fail. **That failure is the outage, now written down in a form the
pipeline can catch forever.** Then fix the typo, bump the version, and promote.

`0.2.0` stays burned. You can never reuse it — the artifact store already holds
bytes under that name, and [HD-106's guard](hd-106-build-once.md#the-guard-that-makes-it-a-rule)
will refuse. That's correct. Version numbers are cheap; ambiguity about what shipped
is not.

## The trade-off nobody tells you about

That 1-minute wait timer on production cost a full minute of a live outage.

Some teams exempt rollbacks from the timer. Some keep it, because a panicked
rollback is itself a common way to make an incident worse. Neither answer is free,
and you should pick yours deliberately rather than discovering it at 2am.

---

Back to the **[README](../README.md)**, or read the
**[mistakes ledger](mistakes.md)** — which is where most of the learning actually is.
