#!/usr/bin/env bash
# Create the two long-lived branches from main, with an explicit start point.
set -euo pipefail

git fetch origin

for branch in develop staging; do
  if git show-ref --quiet "refs/remotes/origin/$branch"; then
    echo "origin/$branch already exists - skipping"
  else
    git branch "$branch" origin/main
    git push -u origin "$branch"
    echo "created origin/$branch from main"
  fi
done

echo
echo "Long-lived branches: develop, staging, main. None of these is ever deleted."
