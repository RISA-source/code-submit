# Implementation Plan - CodeSubmit (MVP)

## Goal Description
Build **CodeSubmit**, a CLI tool to automate the creation of submission-ready academic documents from source code. The tool will scan a directory, execute code to verify output, and generate a formatted Markdown/Text document with metadata.

## User Review Required
> [!NOTE]
> **Execution Security**: The tool executes code found in the directory. Ensure you only run this on trusted code (your own assignments) or within a controlled environment if grading others' work.

> [!IMPORTANT]
> **Dependencies**: The user must have the necessary compilers/interpreters (Python, Java, GCC, etc.) installed and in their system PATH for the code to execute successfully.

## Proposed Changes

### Project Structure
We will create a Python package named `codesubmit`.

```
codesubmit/
├── __init__.py
├── cli.py            # Entry point (Click)
├── config.py         # YAML Configuration loader
├── scanner.py        # File discovery logic
├── executor.py       # Code execution logic (subprocess)
├── formatters/       # Output formatting
│   ├── __init__.py
│   ├── markdown.py   # Markdown output generator
│   └── base.py       # Abstract base class
└── utils.py          # Helpers
```

### 1. Configuration (`config.py`)
- Define a `Config` dataclass.
- Load `codesubmit.yaml` if present, otherwise use defaults.
- Schema:
  - `project`: title, author, etc.
  - `input`: root dir, extensions.
  - `execution`: enabled, timeout.
  - `output`: format.

### 2. Source Scanner (`scanner.py`)
- `scan_directory(path, extensions, excludes)`
- Returns a list of `SourceFile` objects containing metadata (path, language, mod time).

### 3. Execution Engine (`executor.py`)
- Map extensions to runners (e.g., `.py` -> `python`, `.java` -> `javac + java`).
- `run_code(file_path, timeout)`
- Captures `stdout`, `stderr`, `exit_code`, and `duration`.

### 4. Output Generator (`formatters/`)
- `MarkdownFormatter`:
  - Generates the Header block.
  - Loops through results:
    - Writes file metadata.
    - Writes code block.
    - Writes output block (if execution enabled).

### 5. CLI (`cli.py`)
- Commands:
  - `generate`: Main command to run the flow.
  - `init`: Create a sample `codesubmit.yaml`.

## Verification Plan

### Automated Tests
- Create a dummy project structure with:
  - `hello.py` (prints "Hello World")
  - `error.py` (throws error)
- Run `codesubmit generate` on the dummy project.
- Verify the output `submission.md` contains:
  - The source code.
  - The correct "Hello World" output.
  - The captured error from `error.py`.

### Manual Verification
- User to run the tool on the provided specifications to see if the roadmap matches the output.
