# Developer Guide

This guide explains the internal architecture of **CodeSubmit** and how to contribute to it.

## Architecture Overview

The application follows a pipelined architecture:
1.  **Configuration** (`config.py`): Parses user YAML settings.
2.  **Scanner** (`scanner.py`): Finds files and computes hashes (SHA256).
3.  **Executor** (`executor.py`): Orchestrates subprocess execution.
4.  **Formatters** (`formatters/`): Transforms results into final artifacts.

## Extending the Tool

### Adding a New Language

To support a new language (e.g., Rust), modify `executor.py`:

1.  Update `detect_language` in `scanner.py` (if extension is new).
2.  Update `get_runner_command` in `executor.py`:

```python
def get_runner_command(file_path: str, language: str) -> List[str]:
    # ... existing ...
    elif language == 'Rust':
        # Compile and run? Or use cargo run-script?
        # For simple scripts: rustc ... && ./...
        pass 
```

### Adding a New Formatter

1.  Create `codesubmit/formatters/myfmt.py`.
2.  Inherit from `BaseFormatter`.
3.  Implement `save(self, results, config, path)`.
4.  Register it in `cli.py` under the `generate` command.

## Running Tests

(TODO: Add `pytest` instructions once tests are implemented)

```bash
python -m unittest discover tests
```
