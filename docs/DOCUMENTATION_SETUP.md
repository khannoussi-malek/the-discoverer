# Documentation Setup Guide

## Overview

Navo documentation is built using [MkDocs](https://www.mkdocs.org/) with the [Material theme](https://squidfunk.github.io/mkdocs-material/), providing a beautiful, searchable documentation website.

## Documentation URL

Once enabled, your documentation will be available at:
**https://khannoussi-malek.github.io/navo**

## Enabling GitHub Pages

1. Go to your repository on GitHub: https://github.com/khannoussi-malek/navo
2. Click on **Settings** (in the repository menu)
3. Scroll down to **Pages** (in the left sidebar)
4. Under **Source**, select:
   - **Source**: `gh-pages` branch
   - **Folder**: `/ (root)`
5. Click **Save**

## Automatic Deployment

The documentation is automatically deployed via GitHub Actions whenever you:
- Push changes to the `main` branch
- Modify files in the `docs/` folder
- Update `mkdocs.yml`

The GitHub Actions workflow (`.github/workflows/docs.yml`) will:
1. Build the documentation
2. Deploy it to the `gh-pages` branch
3. Make it available on GitHub Pages

## Local Development

### Preview Locally

To preview the documentation locally before pushing:

```bash
# Install dependencies
pip install -r requirements-docs.txt

# Start the development server
mkdocs serve
```

Then open http://127.0.0.1:8000 in your browser.

### Build Locally

To build the documentation without serving:

```bash
mkdocs build
```

The built site will be in the `site/` directory (which is gitignored).

## Documentation Structure

- **Configuration**: `mkdocs.yml` - Main configuration file
- **Source Files**: `docs/` - All markdown documentation files
- **Build Output**: `site/` - Generated HTML (not committed to git)

## Features

- ✅ **Search**: Full-text search across all documentation
- ✅ **Responsive**: Works on desktop, tablet, and mobile
- ✅ **Dark Mode**: Toggle between light and dark themes
- ✅ **Navigation**: Easy navigation with tabs and sections
- ✅ **Code Highlighting**: Syntax highlighting for code blocks
- ✅ **Copy Code**: One-click copy for code snippets

## Customization

Edit `mkdocs.yml` to customize:
- Site name and description
- Theme colors
- Navigation structure
- Plugins and extensions

## Troubleshooting

### Documentation Not Updating

1. Check GitHub Actions: Go to the **Actions** tab in your repository
2. Verify the workflow ran successfully
3. Wait a few minutes for GitHub Pages to update (can take up to 10 minutes)

### Build Errors

If you see build errors:
1. Check `mkdocs.yml` syntax
2. Verify all referenced files exist in `docs/`
3. Check for broken links in your markdown files

### Local Preview Issues

If `mkdocs serve` doesn't work:
1. Ensure dependencies are installed: `pip install -r requirements-docs.txt`
2. Check Python version (requires Python 3.7+)
3. Verify `mkdocs.yml` is valid

## Need Help?

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)

