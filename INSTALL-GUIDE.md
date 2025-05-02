# Installation Guide

This guide shows how to build and install the `ultra-optimized-bedrock-chat` package.

## Prerequisites

Ensure you have the following installed:
- Python 3.8 or newer
- pip
- pipx (recommended for CLI applications)

If you don't have pipx installed, you can install it with:

```bash
pip install pipx
pipx ensurepath
```

## Option 1: Install from Source (Development)

1. Clone or download this repository
2. Navigate to the project directory containing `pyproject.toml`
3. Build and install with pipx:

```bash
# Build the package
pip install build
python -m build

# Install with pipx
pipx install dist/ultra_optimized_bedrock_chat-0.2.1-py3-none-any.whl
```

For development/editable install:

```bash
# Using pip for editable install
pip install -e .

# Or using pipx with venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Option 2: Install from PyPI (when published)

Once the package is published to PyPI, you can install it directly:

```bash
pipx install ultra-optimized-bedrock-chat
```

## Verifying Installation

After installation, you should be able to run:

```bash
ultra-bedrock-chat --help
```

This should display the help information for the application.

## AWS Credentials

Make sure you have AWS credentials configured with appropriate permissions for Amazon Bedrock:

```bash
aws configure
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

## Troubleshooting

- **ModuleNotFoundError**: Ensure all dependencies are installed
- **Permission errors**: On Unix-like systems, ensure the script is executable
- **AWS credentials errors**: Verify your AWS credentials are correctly configured
- **Model access errors**: Make sure you have requested access to the models in the AWS console
- **UnboundLocalError for 'tbl'**: Make sure you're using version 0.2.1 or newer

## Why Use pipx?

pipx creates isolated environments for Python applications, preventing dependency conflicts and making installation/uninstallation clean and simple. This is especially useful for CLI tools like this ultra-optimized AWS Bedrock chat interface.

