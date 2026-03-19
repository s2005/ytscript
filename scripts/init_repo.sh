#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "======================================"
echo "ytscript-public repository setup"
echo "======================================"
echo ""

if [ ! -d .git ]; then
    git init
    git branch -m main
    echo "Initialized git repository"
else
    echo "Git repository already exists"
fi

if [ -n "${GIT_USER:-}" ]; then
    git config user.name "$GIT_USER"
    echo "Configured git user.name from environment"
fi

if [ -n "${GIT_EMAIL:-}" ]; then
    git config user.email "$GIT_EMAIL"
    echo "Configured git user.email from environment"
fi

if [ -n "${GITHUB_REPO:-}" ]; then
    remote_url="git@github.com:${GITHUB_REPO}.git"
    if git remote get-url origin >/dev/null 2>&1; then
        git remote set-url origin "$remote_url"
        echo "Updated origin to $remote_url"
    else
        git remote add origin "$remote_url"
        echo "Added origin $remote_url"
    fi
else
    echo "GITHUB_REPO is not set; skipping remote configuration"
fi
