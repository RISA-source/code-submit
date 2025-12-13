# Tasks - CodeSubmit

## Phase 1: Foundation (MVP)
- [x] Project Scaffolding
    - [x] Create project directory <!-- id: 0 -->
    - [x] Save specification documents <!-- id: 1 -->
    - [x] Initialize project structure (Python) <!-- id: 2 -->
    - [x] Create virtual environment and core dependencies <!-- id: 3 -->
- [x] Configuration Module
    - [x] Implement `codesubmit.yaml` parser using `PyYAML` <!-- id: 4 -->
    - [x] Define default configuration schema <!-- id: 5 -->
- [x] Source Scanner
    - [x] Implement recursive folder scanning <!-- id: 6 -->
    - [x] Add filtering by extension and exclusion patterns <!-- id: 7 -->
    - [x] Implement file hashing (SHA256) for integrity <!-- id: 7b -->
- [/] Execution Engine
    - [x] Define `ExecutionResult` dataclass (stdout, stderr, exit_code, duration, context) <!-- id: 8 -->
    - [x] Create `Executor` class with `subprocess` <!-- id: 8b -->
    - [x] Implement Input Strategy (handling stdin to prevent hangs) <!-- id: 9 -->
    - [x] Implement Environment and CWD capture <!-- id: 9b -->
    - [x] Implement timeout mechanisms <!-- id: 9c -->
    - [x] Add Runners for Python and Java <!-- id: 10 -->
- [x] Output Generator
    - [x] Implement Markdown builder (Pure: takes data, returns string) <!-- id: 11 -->
    - [x] Create document header, per-file section, and Integrity Manifest <!-- id: 12 -->
- [x] CLI Interface
    - [x] Implement `click` or `argparse` CLI entry point <!-- id: 13 -->
    - [x] Connect scanner, executor, and generator <!-- id: 14 -->

## Phase 2: Academic Polish
- [x] Advanced Output Formats
    - [x] Implement DOCX export (via `python-docx`) <!-- id: 15 -->
    - [x] Implement PDF export (Optional, via `xhtml2pdf`) <!-- id: 16 -->
- [ ] Templating System
    - [ ] Allow custom Jinja2 templates for headers <!-- id: 17 -->

## Phase 3: Advanced Proof
- [ ] Screenshot Capability (Optional)
    - [ ] Integrate `selenium` or `playwright` for capturing output screenshots (if requested) <!-- id: 18 -->

## Phase 4: Rock Solid Documentation
- [x] Project Documentation
    - [x] Create comprehensive `README.md` (Installation, Usage, Examples) <!-- id: 19 -->
    - [x] Create `CONTRIBUTING.md` (as DEVELOPER_GUIDE.md) <!-- id: 20 -->
    - [x] Update `walkthrough.md` with full tour of all features <!-- id: 21 -->

## Phase 5: Interactive Execution
- [x] Interactive Mode
    - [x] Implement `Tee` threading logic for live I/O <!-- id: 22 -->
    - [x] Add `interactive` flag to config and CLI <!-- id: 23 -->
