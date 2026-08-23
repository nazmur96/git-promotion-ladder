# HD-101 — The first pull request

**Builds:** nothing. **Teaches:** why the next six tickets exist.

## The ticket

> Add a feature to the helpdesk CLI. Don't push to `main` — open a pull request.

## What you do

```bash
git switch -c hd-101-priority-filter
# ... write the code ...
git add -A
git commit -m "feat: filter tickets by priority"
git push -u origin hd-101-priority-filter

gh pr create --base main --head hd-101-priority-filter \
  --title "HD-101: filter tickets by priority" \
  --body "Adds --priority to the list command."
```

Then merge it.

## What actually happened

The PR merged. Green tick, satisfying. And **nothing had checked anything.**

There were no tests running, no required reviewers, no status checks. The PR was a
change of scenery, not a gate. Anyone could have merged anything.

That is the entire point of this ticket. You are supposed to feel how empty it is.

## The two words that cause the most confusion

Every PR has a **base** and a **head**:

| Word | Means |
|---|---|
| **base** | **Destination.** Where the code lands. |
| **head** | **Source.** Where the code comes from. |

`--base main --head hd-101-priority-filter` reads: *this branch ends up in `main`*.

Get these backwards and you will open a PR proposing to merge `main` into your
feature branch, which looks almost right and is completely wrong. It happens to
everyone at least once. It happened here — see [mistakes.md](mistakes.md).

**Also:** a PR's `head` has nothing to do with git's `HEAD` pointer. Same word,
unrelated meanings. Git's `HEAD` is "where I am standing right now"; a PR's head is
"the branch being proposed".

## What to look at before moving on

Open the merged PR and look at the checks section. It's empty. Remember that.

---

Next: **[HD-102 — Continuous integration](hd-102-continuous-integration.md)**
