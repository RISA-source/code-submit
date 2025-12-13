# CodeSubmit

**CodeSubmit** is a command-line tool that automates the creation of submission-ready academic documents from source code. It eliminates manual copy-pasting, ensures reproducible execution, and produces professional PDF/DOCX reports.

## Features

*   **Automated Scanning**: Recursively finds source files (.py, .java, etc.) in your project.
*   **Execution as Proof**: Runs your code and captures `stdout`, `stderr`, and runtime duration (Python & Java support).
*   **Integrity Verification**: Hashes every source file (SHA256) to ensure the submission matches the code.
*   **Multi-Format Export**: Generates reports in Markdown, Word (DOCX), and PDF.
*   **Academic Formatting**: Clean, readable structure with cover page metadata.

## Installation

Requires Python 3.8+.

```bash
# Clone the repository
git clone https://github.com/your-repo/codesubmit.git
cd codesubmit

# Install
pip install .

# Optional: Install PDF support
pip install xhtml2pdf
```

## Quick Start

1.  **Initialize** a project:
    Create a `codesubmit.yaml` file in your assignment folder:
    ```yaml
    project:
      title: "CS101 Assignment 4"
      author: "Jane Doe"
      
    input:
      root: "."
      extensions: [".py"]
      
    execution:
      enabled: true
      timeout: 5
    ```

2.  **Generate** the submission:
    ```bash
    codesubmit generate
    ```
    This creates `submission.md` by default.

3.  **Export** to PDF or DOCX:
    ```bash
    codesubmit generate --format pdf --output Assignment4.pdf
    codesubmit generate --format docx --output Assignment4.docx
    ```

## Configuration (`codesubmit.yaml`)

| Section | Key | Description | Default |
| :--- | :--- | :--- | :--- |
| `project` | `title` | Title on cover page | "Assignment" |
| | `author` | Name on cover page | "Student" |
| `input` | `root` | Directory to scan | `.` |
| | `extensions` | List of extensions | `['.py', '.java']` |
| `execution` | `enabled` | Run code? | `true` |
| | `timeout` | Secs before timeout | `5` |
| | `stdin_input` | Text to pipe to stdin | `""` |

## Supported Languages

*   **Python**: Runs with `sys.executable`.
*   **Java**: Runs with `java single-source-file-launch` (Java 11+).

## License

MIT License
