# Claude Development Guide

## Development Commands

- Build package: `python -m build` (use virtual environment)
- Install locally: `pipx install .` or `pip install -e .`

## Installation Instructions

1. Clean build artifacts first (important to avoid stale files):
   ```
   rm -rf build dist *.egg-info
   ```

2. Build the package:
   ```
   source venv/bin/activate
   python -m build
   ```

3. Install with pipx directly from the current directory:
   ```
   pipx install --force .
   ```

## Common Issues

- Package installation requires building the distributable wheel file first
- When running `pipx install ultra-optimized-bedrock-chat`, the package must be published to PyPI first
- For local development, use `pipx install .` or `pipx install dist/ultra_optimized_bedrock_chat-X.Y.Z-py3-none-any.whl`
- If your changes aren't being applied, make sure to clean the build artifacts first with `rm -rf build dist *.egg-info`