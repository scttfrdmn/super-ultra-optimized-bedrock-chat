# Claude Development Guide

## Development Commands

- Build package: `python -m build` (use virtual environment)
- Install locally: `pipx install .` or `pip install -e .`

## Installation Instructions

1. Build the package first:
   ```
   source venv/bin/activate
   python -m build
   ```

2. Install with pipx directly from the current directory:
   ```
   pipx install --force .
   ```

## Common Issues

- Package installation requires building the distributable wheel file first
- When running `pipx install ultra-optimized-bedrock-chat`, the package must be published to PyPI first
- For local development, use `pipx install .` or `pipx install dist/ultra_optimized_bedrock_chat-X.Y.Z-py3-none-any.whl`