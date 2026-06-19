# Contributing to Distributed Firewall VDC

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to this project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one.

**How Do I Submit A Bug Report?**

Bugs are tracked as GitHub issues. Create an issue and provide:
- A clear and descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment details (OS, VMware version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:
- A clear and descriptive title
- A detailed description of the suggested enhancement
- Why this enhancement would be useful
- Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Markdown Styleguide

- Use ATX-style headers (`#` for H1, `##` for H2, etc.)
- Use fenced code blocks with language specification
- Use tables for structured data
- Include alt text for images

### Script Styleguide

**Bash Scripts**
- Follow Google Shell Style Guide
- Include `#!/bin/bash` shebang
- Use `set -euo pipefail` for error handling
- Comment all functions
- Use lowercase for variable names (except constants)

**PowerShell Scripts**
- Follow Microsoft PowerShell style guide
- Use Verb-Noun naming for functions
- Include comment-based help
- Use approved verbs

**Python Scripts**
- Follow PEP 8 style guide
- Use type hints
- Include docstrings for all functions and classes
- Use `argparse` for CLI arguments

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/Distributed-Firewall-VDC.git
cd Distributed-Firewall-VDC

# Install Python dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
