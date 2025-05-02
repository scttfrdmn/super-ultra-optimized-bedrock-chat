# Ultra-Optimized Bedrock Chat

A complete AWS Bedrock chat interface in under 50 lines of code! 🚀

![GitHub License](https://img.shields.io/github/license/yourusername/ultra-optimized-bedrock-chat)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Lines of Code](https://img.shields.io/badge/code-49%20lines-brightgreen)
![Lines of README](https://img.shields.io/badge/readme-140%2B%20lines-yellow)

> **Yes, this README is 3x longer than the entire codebase.** 
> 
> *We spent so much time optimizing the code that we had plenty left over for documentation!*

## 🔥 Extreme Optimization

This project demonstrates the art of code optimization taken to its limits:

- **49 lines total** - A complete, production-ready chatbot in fewer lines than most class definitions
- **No functionality compromises** - All features of a pro-grade AWS chatbot in a tiny footprint
- **Maximum readability** - Still maintainable despite extreme optimization

## ✨ Features

Despite its tiny size, this chatbot packs an impressive set of capabilities:

- **Model Versatility**
  - Foundation model support (Claude, Titan, etc.)
  - Cross-region inference profile support
  - **Provisioned throughput model support** (Claude 3.7 and others)
  - ARN direct input for any model type
  - **Automatic model availability detection**

- **Interactive Experience**
  - Real-time streaming responses
  - Rich markdown rendering
  - Beautiful tables with colored status indicators
  - Conversation history management
  - Clear error messaging

- **Developer Friendly**
  - Dynamic model discovery
  - Multiple AWS profile support
  - Model availability filtering
  - Clean packaging with pipx support
  - Extensive documentation (perhaps too extensive? 😉)

## 📊 Size Comparison

| Feature | Ultra-Optimized-Bedrock-Chat | Typical Implementation | This README |
|---------|------------------------------|------------------------|-------------|
| Lines of code | 49 | 500-1000+ | 140+ |
| File size | ~2KB | 20-50KB | ~5KB |
| Dependencies | 3 | 10-20+ | 0 |
| Features | Complete set | Comparable | Just words |

## 🚀 Installation

Install with pipx (recommended):

```bash
pipx install ultra-optimized-bedrock-chat==0.2.1
```

Or with pip:

```bash
pip install ultra-optimized-bedrock-chat==0.2.1
```

### Why pipx?

We recommend using pipx for installation because:

1. **Isolation** - Creates a dedicated virtual environment for the application
2. **Global access** - Makes the command globally available without affecting other Python packages
3. **Clean uninstallation** - Easy removal without affecting other packages
4. **Dependency management** - Manages all dependencies in an isolated environment

See the [INSTALL-GUIDE.md](INSTALL-GUIDE.md) for detailed installation instructions.

## 💻 Usage

Simply run:

```bash
ultra-bedrock-chat
```

### Options
- `--version` / `-v`: Display version number
- `--region`: AWS region to use (default: us-east-1)
- `--profile`: AWS profile to use (default: None, uses default profile)
- `--allow-provisioned`: Allow access to models requiring provisioned throughput (hourly billing)

### Commands
- **Default** (no command): Start chat interface
  ```bash
  ultra-bedrock-chat [--clear] [--all]
  ```
  - `--clear`: Clear terminal before starting
  - `--all`: Show all models, not just enabled ones

- **list-models**: List all available models
  ```bash
  ultra-bedrock-chat list-models
  ```

- **list-provisioned**: Check active provisioned throughput commitments
  ```bash
  ultra-bedrock-chat list-provisioned
  ```
  ⚠️ Use this command to see what provisioned throughput you're being billed for

Don't worry, these instructions are already longer than several functions in the actual code!

## 🧩 How It Works

The chatbot achieves its tiny size through several advanced optimization techniques:

1. **Strategic imports** - Module-level imports to minimize lines
2. **Modern Python syntax** - Walrus operator, list comprehensions, ternary expressions
3. **Dictionary comprehensions** - Complex data transforms in single lines
4. **Smart error handling** - Minimal but effective exception management
5. **Optimized whitespace** - No wasted lines while maintaining readability
6. **Shortened variable names** - Strategic shortening without sacrificing clarity

If we had applied these same techniques to this README, it would be about 5 lines long!

## 📝 Example Session

```
┌─────────────────────── Ultra Bedrock Chat v0.2.7 ────────────────────────┐
│ Model           Type               ID                                    │
│ claude-haiku    On-Demand          anthropic.claude-3-haiku-20240307-v1:0│
│ claude-opus     On-Demand          anthropic.claude-3-opus-20240229-v1:0 │
│ claude-sonnet   On-Demand          anthropic.claude-3-sonnet-20240229-v1:0│
│ claude-3-7      [bold red]Provisioned $[/bold red]  us.anthropic.claude-3-7-sonnet-20240620...│
└──────────────────────────────────────────────────────────────────────────┘

Model: claude-sonnet
Using anthropic.claude-3-sonnet-20240229-v1:0

You: Explain quantum computing in two sentences

AI: Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to perform computations that would be impractical for classical computers. Unlike classical bits that are either 0 or 1, quantum bits (qubits) can exist in multiple states simultaneously, enabling exponential computational advantages for specific problems like factoring large numbers and simulating quantum systems.

You: exit
```

That example transcript alone is almost 20% the size of our entire codebase!

## 🧪 Advanced Usage

### Using Provisioned Throughput Models

This chatbot supports AWS Bedrock's provisioned throughput models, which provide dedicated capacity but incur hourly costs:

1. **Access requires opt-in**: By default, provisioned throughput models are hidden
2. Start with the `--allow-provisioned` flag to see available provisioned models:
   ```
   ultra-bedrock-chat --allow-provisioned
   ```
3. Choose a model with the `[Provisioned $]` type indicator from the menu

**Note**: This tool only shows models that already have provisioned throughput set up. It does not create new provisioned throughput profiles.

⚠️ **IMPORTANT: Cost Warning** ⚠️

Provisioned throughput models incur **hourly charges** regardless of usage:

- Charges continue until you explicitly delete the provisioned throughput in the AWS console
- Using this CLI tool does NOT automatically remove provisioned throughput
- You are billed for the entire commitment period (1-month or 6-months)
- Run the dedicated command to check your active commitments:
  ```
  ultra-bedrock-chat list-provisioned
  ```

### Multiple Model Types

The chatbot automatically discovers and supports:
- Foundation models (pay-as-you-go)
- Cross-region inference profiles
- Provisioned throughput models

> **Note on Model Availability**: This tool only works with models available through AWS Bedrock. OpenAI models (GPT-3.5, GPT-4, GPT-4o) are not available on Bedrock and require using OpenAI's API directly.

## 📏 Detailed Code Breakdown

Let's look at exactly how small this code is:

```
Total lines of code: 49

Breakdown:
- 1 line: shebang and docstring
- 4 lines: imports 
- 1 line: app and console initialization
- 30 lines: Chat class including initialization, model discovery, and streaming
- 13 lines: chat command function and execution
```

The file is approximately 2.1 KB in size, which is remarkably small for a full-featured chatbot.

For perspective:
- A typical "Hello World" example with these libraries: 10-15 lines
- This README file: 170+ lines
- A typical AWS Bedrock integration: 500+ lines
- The number of lines in average Python packages to accomplish the same task: thousands

Even the docstring in some enterprise Python modules is longer than our entire application!

## 🔍 Why So Small?

This project demonstrates the elegance and power of Python when pushed to its limits. By leveraging modern Python features and powerful libraries like Typer and Rich, we've created a professional-grade chatbot with minimal code.

The result is not just a technical showcase but a genuinely useful tool that's easy to understand, modify, and extend.

## 📏 The README Paradox

In a delightful twist of irony, this README is approximately 3 times longer than the actual code it describes. We like to think of it as the software development equivalent of writing "I'm sorry this letter is so long, I didn't have time to make it shorter."

Creating extremely concise, functional code actually requires more effort than verbose code. Similarly, a comprehensive yet concise README takes considerable effort. We just focused our brevity efforts on the code rather than the documentation!

## 🔧 Requirements

- Python 3.8+
- AWS credentials with Bedrock access
- boto3
- typer
- rich

## 📜 License

MIT

---

*This README contains 170+ lines explaining 49 lines of code, and that's perfectly fine. In fact, we're quite proud of it!*




