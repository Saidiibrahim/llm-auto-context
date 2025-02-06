# 🦜 LLM-Auto-Context

A CLI tool for generating code snapshots for AI code assistants such as ChatGPT and Claude.

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Installation

Using UV (recommended):
```bash
uv pip install llm-auto-context
```

Using pip:
```bash
pip install llm-auto-context
```

## Usage

Basic usage:
```bash
llm_auto_context
```

This will use the default config file `.codesnapshot.json` in your current directory.

### Configuration

Create a `.codesnapshot.json` file in your project root:

```json
{
    "directories": ["src", "lib"],
    "output_file": "code_snapshot.md",
    "include_extensions": [".py", ".js", ".ts"],
    "exclude_dirs": ["node_modules", ".git", "build"],
    "exclude_files": ["secrets.env"]
}
```

### CLI Options

- `--config`: Path to config file (default: .codesnapshot.json)
- `-d, --directory`: Override directories to scan (can be used multiple times)
- `-o, --output`: Override output file path
- `--include`: Override file extensions to include (can be used multiple times)
- `--exclude-dir`: Additional directories to exclude (can be used multiple times)
- `--exclude-file`: Additional files to exclude (can be used multiple times)

Example:
```bash
llm_auto_context -d src -d lib -o snapshot.md --exclude-dir tests
```

## Development

1. Clone the repository
2. Create a virtual environment:
```bash
uv venv
```

3. Install dependencies:
```bash
uv pip install -e ".[dev]"
```

4. Run tests:
```bash
pytest
```

## License

MIT