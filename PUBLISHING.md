# Publishing Guide

This guide explains how to publish The Discoverer to PyPI and npm.

## Prerequisites

### For PyPI Publishing
1. Create a PyPI account: https://pypi.org/account/register/
2. Create an API token: https://pypi.org/manage/account/token/
3. Install build tools:
   ```bash
   pip install build twine
   ```

### For npm Publishing
1. Create an npm account: https://www.npmjs.com/signup
2. Login to npm:
   ```bash
   npm login
   ```

## Publishing Python Package to PyPI

### Step 1: Prepare for Publishing

```bash
# Clean previous builds
make clean

# Or manually:
rm -rf build dist *.egg-info
```

### Step 2: Build the Package

```bash
# Build source distribution and wheel
python -m build

# This creates:
# - dist/the-discoverer-1.0.0.tar.gz (source distribution)
# - dist/the_discoverer-1.0.0-py3-none-any.whl (wheel)
```

### Step 3: Check the Distribution

```bash
# Verify the package
twine check dist/*

# Test installation locally
pip install dist/the_discoverer-*.whl
```

### Step 4: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ the-discoverer
```

### Step 5: Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Or use token authentication
twine upload --username __token__ --password <your-api-token> dist/*
```

### Step 6: Verify Publication

```bash
# Install from PyPI
pip install the-discoverer

# Verify it works
discoverer --help
```

## Publishing JavaScript SDK to npm

### Step 1: Build the SDK

```bash
cd src/sdk/javascript

# Install dependencies
npm install

# Build the package
npm run build
```

### Step 2: Test the Build

```bash
# Run tests
npm test

# Check linting
npm run lint
```

### Step 3: Dry Run (Test Without Publishing)

```bash
# See what would be published
npm publish --dry-run
```

### Step 4: Publish to npm

```bash
# Login (if not already)
npm login

# Publish
npm publish

# For scoped packages, you may need:
npm publish --access public
```

### Step 5: Verify Publication

```bash
# Install from npm
npm install @discoverer/sdk

# Or test in a new project
npm init -y
npm install @discoverer/sdk
```

## Version Management

### Updating Version

Before publishing a new version, update the version number:

1. **Python package**: Update `version` in `pyproject.toml`
2. **JavaScript SDK**: Update `version` in `src/sdk/javascript/package.json`
3. **Git tag**: Create a git tag for the version
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### Semantic Versioning

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backward compatible
- **PATCH** (0.0.1): Bug fixes, backward compatible

## GitHub Release

After publishing, create a GitHub release:

1. Go to: https://github.com/khannoussi-malek/exploarer/releases/new
2. Create a new tag (e.g., `v1.0.0`)
3. Add release notes from `CHANGELOG.md`
4. Attach release artifacts if needed

## Quick Commands

```bash
# Full Python publishing workflow
make clean && python -m build && twine check dist/* && twine upload dist/*

# Full JavaScript publishing workflow
cd src/sdk/javascript && npm run build && npm publish
```

## Troubleshooting

### PyPI Issues

- **Package name already taken**: Choose a different name or use a namespace
- **Authentication failed**: Check your API token
- **Upload failed**: Ensure version number is incremented

### npm Issues

- **Scoped package requires access**: Use `--access public`
- **Package name conflict**: Change the package name in `package.json`
- **Build fails**: Check TypeScript configuration and dependencies

## Notes

- Always test on TestPyPI before publishing to PyPI
- Use `--dry-run` for npm before actual publishing
- Keep version numbers in sync between Python and JavaScript packages
- Update CHANGELOG.md before each release
- Tag releases in git for better version tracking


