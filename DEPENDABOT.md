# Dependabot Management Guide

## How to Ask Dependabot to Check Again

If you notice that Dependabot PRs are outdated or you want to trigger a fresh dependency scan, you have several options:

### 1. Comment Commands on PRs
You can use these commands in comments on existing Dependabot PRs:
- `@dependabot rebase` - Rebases the PR with the latest changes
- `@dependabot recreate` - Recreates the PR, overwriting any edits
- `@dependabot close` - Closes the PR (Dependabot will recreate it if needed)

### 2. Force a New Scan via Configuration
- Modify `.github/dependabot.yml` (add a comment or change configuration)
- Update version constraints in `pyproject.toml` to reflect current baseline
- Commit the changes to trigger a new scan

### 3. Manual Trigger
If dependencies are already updated in the lock file (`uv.lock`) but PRs are stale:
1. Close the outdated PRs
2. Dependabot will automatically recreate them if newer versions are available
3. Or update the minimum version requirements in `pyproject.toml`

### 4. Check Current Status
To see what dependencies are currently installed:
```bash
# Check what's in the lock file
grep -A 2 -B 1 "name.*\(package-name\)" uv.lock

# View dependency tree (if uv is installed)
uv tree
```

## Current Configuration
- **Schedule**: Weekly on both Python dependencies (uv) and GitHub Actions
- **Open PR Limit**: 10 for Python dependencies, 5 for GitHub Actions
- **Package Ecosystem**: `uv` for Python dependencies

## Recent Updates
This file was created as part of resolving outdated Dependabot PRs where the dependencies were already updated in the lock file but the PRs were still open with older versions.