# Publishing to PyPI Guide

## One-Time Setup

### 1. Create PyPI Account
- Go to https://pypi.org/account/register/
- Verify your email

### 2. Create API Token
- Go to https://pypi.org/manage/account/token/
- Click "Add API token"
- Token name: `knowledgelm` (or any name you prefer)
- Scope: "Entire account" (for first upload; can be project-specific later)
- **SAVE THE TOKEN** - you'll only see it once!
- Format: `pypi-AgEIcHlwaS5vcmc...` (starts with `pypi-`)

### 3. Configure uv with Token
Store your token securely. You'll use it when publishing.

## Publishing Steps

### Step 1: Build the Package

```bash
uv build
```

This creates two files in `dist/`:
- `knowledgelm-4.0.0-py3-none-any.whl` (wheel)
- `knowledgelm-4.0.0.tar.gz` (source distribution)

### Step 2: Publish to PyPI

```bash
uv publish
```

When prompted:
- Username: `__token__`
- Password: `pypi-AgEIcHlwaS5vcmc...` (your API token)

**Alternative:** Set environment variable to avoid prompt:
```powershell
$env:UV_PUBLISH_TOKEN="pypi-AgEIcHlwaS5vcmc..."
uv publish
```

### Step 3: Verify

Visit https://pypi.org/project/knowledgelm/ to see your package!

## Test Installation

After publishing, test that it works:

```bash
# In a new environment
uv tool install knowledgelm
knowledgelm --version
```

## Future Updates

For subsequent releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Build: `uv build`
4. Publish: `uv publish`

## Troubleshooting

### "File already exists"
- You can't re-upload the same version
- Bump the version number and try again

### "Invalid credentials"
- Check your API token is correct
- Ensure username is `__token__` (with double underscores)

### "Package name already taken"
- Choose a different name in `pyproject.toml`
- Check availability: https://pypi.org/project/YOUR-NAME/

## Test PyPI (Optional)

To test before publishing to real PyPI:

1. Create account at https://test.pypi.org/
2. Get token from https://test.pypi.org/manage/account/token/
3. Publish to test:
   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/
   ```
4. Test install:
   ```bash
   uv tool install --index-url https://test.pypi.org/simple/ knowledgelm
   ```
