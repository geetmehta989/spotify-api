#!/usr/bin/env bash
set -euo pipefail

# This script assumes you have gh CLI authenticated (gh auth login)
# and git is configured with your username/email. It will create a repo
# named tritone-task and push the current directory.

REPO_NAME="tritone-task"
REMOTE_URL=""

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: GitHub CLI (gh) not installed. Install from https://cli.github.com/" >&2
  exit 1
fi

# Ensure repository is initialized
if [[ ! -d .git ]]; then
  git init
  git add .
  git commit -m "Initial commit: Tritone task scaffolding and workflow"
fi

# Create GitHub repo if it doesn't exist; ignore error if already exists
if ! gh repo view "$REPO_NAME" >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" --private --source=. --description "Tritone coding task: Spotify cross-reference with ISRCs" --push
else
  # Set remote if missing
  if ! git remote get-url origin >/dev/null 2>&1; then
    USERNAME=$(gh api user --jq .login)
    git remote add origin "git@github.com:${USERNAME}/${REPO_NAME}.git"
  fi
  git add .
  git commit -m "Update: workflow and docs" || true
  git push -u origin HEAD
fi
