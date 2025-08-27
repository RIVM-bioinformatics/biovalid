# Release Process Documentation

This document describes the automated release and publishing process for biovalid.

## Overview

This project uses [release-please](https://github.com/googleapis/release-please) to automate:
- Version bumping based on conventional commits
- CHANGELOG.md generation
- GitHub release creation  
- PyPI package publishing

## Setup Required

### 1. PyPI Trusted Publishing

To publish to PyPI automatically, you need to configure trusted publishing:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new trusted publisher with these settings:
   - **PyPI Project Name**: `biovalid`
   - **Owner**: `RIVM-bioinformatics`
   - **Repository name**: `biovalid`
   - **Workflow filename**: `release-please.yml`
   - **Environment name**: `pypi`

3. For TestPyPI, go to https://test.pypi.org/manage/account/publishing/ and add:
   - **PyPI Project Name**: `biovalid`
   - **Owner**: `RIVM-bioinformatics`
   - **Repository name**: `biovalid`
   - **Workflow filename**: `test-pypi.yml`
   - **Environment name**: `testpypi`

### 2. GitHub Environments

Create environments in your GitHub repository settings:

1. Go to Settings → Environments
2. Create environment named `pypi`
3. Create environment named `testpypi`

## How It Works

### Conventional Commits

Use conventional commit messages to trigger releases:

- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)  
- `feat!:` or `fix!:` - Breaking changes (major version bump)
- `docs:`, `test:`, `ci:`, etc. - Other changes (no version bump)

Examples:
```bash
git commit -m "feat: add new validator for VCF files"
git commit -m "fix: handle empty FASTA files correctly"
git commit -m "feat!: change API structure (breaking change)"
```

### Release Process

1. **Commit and Push**: When you push commits to `main`/`master`, release-please analyzes the commit messages.

2. **Release PR**: If there are releasable changes, release-please creates/updates a release PR with:
   - Updated version numbers
   - Updated CHANGELOG.md
   - Release notes

3. **Merge Release PR**: When you merge the release PR:
   - A new GitHub release is created
   - The package is automatically built and published to PyPI

### Test Publishing

- Pushes to the `dev` branch automatically publish to TestPyPI
- This lets you test the package installation before releasing

## Files Created

- `release-please-config.json` - Configuration for release-please
- `.release-please-manifest.json` - Tracks current version
- `.github/workflows/release-please.yml` - Main release workflow
- `.github/workflows/test-pypi.yml` - TestPyPI publishing workflow
- `CHANGELOG.md` - Auto-generated changelog

## Manual Operations

### Force a Release

To create a release without conventional commits:
```bash
# Create an empty commit with release trigger
git commit --allow-empty -m "chore: release 1.2.3"
```

### Skip CI

Add `[skip ci]` to commit messages to skip workflow runs:
```bash
git commit -m "docs: update README [skip ci]"
```

## Troubleshooting

### Release Not Created
- Check that commits follow conventional commit format
- Ensure you're pushing to the default branch (`main`)
- Look at the release-please workflow logs

### PyPI Publishing Failed
- Verify trusted publishing is configured correctly
- Check that the PyPI project name matches exactly
- Ensure the environment names match the workflow configuration

### Version Conflicts
- Check that `biovalid/version.py` and `.release-please-manifest.json` are in sync
- Release-please should handle this automatically, but manual fixes may be needed if they diverge
