#!/usr/bin/env bash
set -euo pipefail

# Usage:
#  - To push into an existing repo (no gh required):
#      ./scripts/github_publish.sh <EXISTING_REPO_URL>
#    Example:
#      ./scripts/github_publish.sh git@github.com:geetmehta989/spotify-api.git
#  - To create a new repo named tritone-task (gh required):
#      ./scripts/github_publish.sh

REPO_NAME="tritone-task"
EXISTING_URL="${1:-}"

if [[ -z "$EXISTING_URL" ]]; then
  if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: GitHub CLI (gh) not installed. Install from https://cli.github.com/ or pass an existing repo URL as the first argument." >&2
    exit 1
  fi
  USERNAME=$(gh api user --jq .login)
  TARGET_URL="git@github.com:${USERNAME}/${REPO_NAME}.git"
else
  TARGET_URL="$EXISTING_URL"
fi

# Ensure repository is initialized
if [[ ! -d .git ]]; then
  git init
  git add .
  git commit -m "Initial commit: Tritone task scaffolding and workflow"
fi

# Create GitHub repo if it doesn't exist; ignore error if already exists
if [[ -z "$EXISTING_URL" ]]; then
  if ! gh repo view "$REPO_NAME" >/dev/null 2>&1; then
    gh repo create "$REPO_NAME" --private --description "Tritone coding task: Spotify cross-reference with ISRCs"
  fi
fi

# Ensure origin points to the target repo
if git remote get-url origin >/dev/null 2>&1; then
  git remote set-url origin "$TARGET_URL"
else
  git remote add origin "$TARGET_URL"
fi

git add .
git commit -m "chore: add Tritone project files and automation" || true
git push -u origin HEAD
