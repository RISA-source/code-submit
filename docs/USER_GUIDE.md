# User Guide

## Common Scenarios

### 1. Excluding Files
If you have files you don't want to submit (e.g., `test_temp.py`), use the exclusion pattern mechanism (Coming Soon) or simply move them out of the scanned path.
*Currently, CodeSubmit scans all files with matching extensions in the input root.*

### 2. Handling Input (stdin)
If your program asks for user input (e.g., `name = input("Enter name: ")`), it will hang if not configured!

**Solution**: Set `stdin_input` in `codesubmit.yaml`.
```yaml
execution:
  stdin_input: "Alice\n25\n" # simulating entering "Alice" then "25"
```
This input is fed to *every* script executed.

### 3. Java Execution
CodeSubmit assumes your Java files are "Single-File Source Code" programs (Java 11+).
*   It runs `java MyFile.java`.
*   If your code has package declarations that don't match the folder structure, it might fail. Only submit standalone files for best results.

## Troubleshooting

### "PDF export requires xhtml2pdf"
Run `pip install xhtml2pdf`. On Windows, this is usually straightforward. If you get errors related to wheels, ensure you have a recent version of pip: `python -m pip install --upgrade pip`.

### "Execution Timed Out"
The default timeout is 5 seconds. If your code is slow, increase it in `codesubmit.yaml`:
```yaml
execution:
  timeout: 30
```
