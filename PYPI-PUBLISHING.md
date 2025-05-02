# PyPI Publishing Guide for super-ultra-optimized-bedrock-chat

This guide provides instructions for publishing the package to PyPI.

## Prerequisites

1. Make sure you have a PyPI account
2. Create an API token at https://pypi.org/manage/account/token/
3. Install required tools in a clean virtual environment:

```bash
# Create and activate a virtual environment
python3 -m venv pypi_venv
source pypi_venv/bin/activate

# Install build and twine
pip install build twine
```

## Build the Package

Make sure to clean old build artifacts first:

```bash
# Clean old build artifacts
rm -rf build dist *.egg-info

# Build the package
python -m build
```

## Check the Package

Verify the package files are valid for PyPI:

```bash
python -m twine check dist/super_ultra_optimized_bedrock_chat-0.3.0-py3-none-any.whl dist/super_ultra_optimized_bedrock_chat-0.3.0.tar.gz
```

## Upload to PyPI

Use one of the following methods to upload:

### Option 1: Using Environment Variables

```bash
# Set PyPI credentials as environment variables
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your_api_token_here

# Upload to PyPI
python -m twine upload dist/*
```

### Option 2: Using Interactive Prompt

```bash
# Upload to PyPI (will prompt for credentials)
python -m twine upload dist/*

# When prompted:
# Username: __token__
# Password: your_api_token_here
```

### Option 3: Upload to TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test the installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ super-ultra-optimized-bedrock-chat

# If everything works, upload to the real PyPI
python -m twine upload dist/*
```

## Verify Installation

After publishing, verify the package can be installed:

```bash
# Install with pip
pip install super-ultra-optimized-bedrock-chat==0.3.0

# Or install with pipx (recommended for CLI tools)
pipx install super-ultra-optimized-bedrock-chat==0.3.0
```

## Updating PyPI Information

If you need to update metadata, make changes to `pyproject.toml` and rebuild/reupload:

1. Update version number in `bedrock_chat/__version__.py`
2. Update `pyproject.toml` if needed
3. Follow the build and upload steps again

---

**Note:** Once a specific version is uploaded to PyPI, it cannot be replaced - you must bump the version number to upload a new package.