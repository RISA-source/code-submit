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
  - `input`: root dir, extensions, `input_file` (optional global stdin).
  - `execution`: enabled, timeout, `command_overrides` (dict).
  - `output`: format.

### 2. Source Scanner (`scanner.py`)
- `scan_directory(path, extensions, excludes)`
- Returns a list of `SourceFile` objects.
- **New**: Computes SHA256 hash of every source file immediately upon discovery.

### 3. Execution Engine (`executor.py`)
- **Architecture Update**: Return a structured `ExecutionResult` object, not tuples.
  ```python
  @dataclass
  class ExecutionResult:
      stdout: str
      stderr: str
      exit_code: int
      duration: float
      command: str      # Exact command run
      context: dict     # cwd, env vars subset
      timed_out: bool
  ```
- **Input Handling**:
  - Check config for input strategy.
  - Options: `none` (default), `file` (feed a specific text file to stdin).
  - If no input config is strict, default to empty stdin to prevent hangs.
- **Runners**: Restricted to Python (`python`) and Java (`javac` + `java`) for Phase 1. 

### 4. Output Generator (`formatters/`)
- **Purity**: Formatter receives `List[Tuple[SourceFile, ExecutionResult]]`. It does *not* run code.
- `MarkdownFormatter`:
  - Generates the Header block.
  - Loops through results:
    - Writes file metadata (including Hash).
    - Writes code block.
    - Writes output block (if execution enabled).
  - Appends a "Manifest" section with hashes of all files for integrity.
- **[NEW] `DocxFormatter`**:
  - Uses `python-docx` to generate native Word documents.
  - Features:
    - Page break between files.
    - Monospace font (Courier New) for code blocks.
    - Proper headers and footers.
    - Syntax highlighting (optional/difficult in raw docx, maybe plain mono text).
- **[NEW] `PdfFormatter`**:
  - Strategy: Generate clean HTML with `jinja2`, then convert using `weasyprint`.
  - **Fallback**: If `weasyprint` is missing, warn user and suggest DOCX or HTML.
  - Styles: CSS for print (A4 page size, margins, font sizes).

### 6. Documentation
- **User Guide**:
  - `generate` command usage with all flags.
  - Configuration file reference (`codesubmit.yaml`).
  - How to handle dependencies (Java, Python path).
- **Developer Guide**:
  - How to add new languages.
  - How to write new formatters.

### 7. Optional Features (Phase 3)
- **Screenshots**:
  - Use `Process` output to HTML, then `html2image` or `playwright`?
  - *Decision*: Keep it simple. If screenshots are enabled, maybe just try to capture the terminal buffer if possible, or skip for now if too heavy. 
  - *Refined Plan*: Focus on "Rock Solid Documentation" first as requested, treat screenshots as low priority unless explicitly pushed again.


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
