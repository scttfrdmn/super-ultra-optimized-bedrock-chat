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

## Development Best Practices

- Always commit code before making any import changes
- When adding new dependencies or making significant architecture changes, create a branch first
- When modifying AWS client code, use the boto3 Session pattern to maintain profile settings:
  ```python
  session = boto3.Session(profile_name=profile)  # Create session first
  client = session.client('bedrock', region_name=region)  # Then create client from session
  ```

## Common Issues

- Package installation requires building the distributable wheel file first
- When running `pipx install super-ultra-optimized-bedrock-chat`, the package must be published to PyPI first
- For local development, use `pipx install .` or `pipx install dist/super_ultra_optimized_bedrock_chat-X.Y.Z-py3-none-any.whl`
- If your changes aren't being applied, make sure to clean the build artifacts first with `rm -rf build dist *.egg-info`
- AWS region-specific features like provisioned throughput models may need to be queried across multiple regions