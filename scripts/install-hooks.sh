#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_DIR="$(git rev-parse --git-dir)/hooks"

echo "Installing Git hooks..."
cp "$SCRIPT_DIR/hooks/pre-push.sh" "$HOOK_DIR/pre-push"
cp "$SCRIPT_DIR/hooks/pre-commit.sh" "$HOOK_DIR/pre-commit"
chmod +x "$HOOK_DIR/pre-push" "$HOOK_DIR/pre-commit"
echo "Git hooks installed successfully!"
