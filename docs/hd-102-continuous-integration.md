# HD-102 — Continuous integration

**Builds:** `.github/workflows/ci.yml`, then branch protection.
**Teaches:** your laptop is not the runner.

## The ticket

> The last PR merged with nothing checking it. Make the tests run automatically on
> every push and every pull request.

## The workflow

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python3 -m unittest discover -s tests
```

Note `on: push:` with **no branch filter**. That means every branch, forever. It's
the right default for CI — you want to know a branch is broken before you open the
PR, not after.

## HD-102b — the deliberate red build

The interesting half of this ticket is breaking it on purpose.

The CLI gained a deprecated `--prio` alias, written with argparse's built-in
support:

```python
list_parser.add_argument("--prio", dest="priority", deprecated=True)
```

That passed locally. It failed on CI with a `TypeError`.

**Why:** `deprecated=True` was added in Python **3.13**. The laptop was running
3.14, so it worked. The workflow pins **3.12**, so it didn't.

This is the single most common category of CI failure, and it has nothing to do
with your code being wrong:

> **"Works on my machine" is not a defence. It is a description of the bug.**

The fix was to stop relying on a version-specific feature and write the behaviour
explicitly, as a custom `argparse.Action` that prints the warning itself. See
[`helpdesk/cli.py`](../helpdesk/cli.py).

## Then: make the check mandatory

A green check that nobody is required to look at is decoration. Turn it into a
gate — Settings → Branches → add a rule for `main`:

- **Require a pull request before merging**
- **Require status checks to pass before merging** → add `test`

Now the empty checks section from HD-101 is impossible.

## What to look at

Open a new PR and try to merge it while CI is still running. The button is
disabled. That is the first real gate in this repo.

---

Next: **[HD-103 — The first deployment](hd-103-first-deployment.md)**
