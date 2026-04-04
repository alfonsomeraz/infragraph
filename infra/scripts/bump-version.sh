#!/bin/bash
# Usage: bash infra/scripts/bump-version.sh 0.2.0
# Bumps VERSION, backend/pyproject.toml, cli/pyproject.toml, and frontend/package.json

set -e

if [ -z "$1" ]; then
  echo "Usage: bash infra/scripts/bump-version.sh <version>"
  echo "Example: bash infra/scripts/bump-version.sh 0.2.0"
  exit 1
fi

NEW_VERSION="$1"
CURRENT_VERSION=$(cat VERSION)

echo "Bumping version from $CURRENT_VERSION to $NEW_VERSION..."

# Update VERSION file
echo "$NEW_VERSION" > VERSION
echo "✓ Updated VERSION"

# Update backend/pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" backend/pyproject.toml
rm -f backend/pyproject.toml.bak
echo "✓ Updated backend/pyproject.toml"

# Update cli/pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" cli/pyproject.toml
rm -f cli/pyproject.toml.bak
echo "✓ Updated cli/pyproject.toml"

# Update frontend/package.json
sed -i.bak "s/\"version\": \".*\"/\"version\": \"$NEW_VERSION\"/" frontend/package.json
rm -f frontend/package.json.bak
echo "✓ Updated frontend/package.json"

echo ""
echo "Next steps:"
echo "1. Update CHANGELOG.md with the new version and changes"
echo "2. Commit: git add -A && git commit -m 'Bump version to $NEW_VERSION'"
echo "3. Tag: git tag -a v$NEW_VERSION -m 'Release v$NEW_VERSION'"
echo "4. Push: git push origin main && git push origin v$NEW_VERSION"
