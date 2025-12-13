# Tasks - CodeSubmit

## Phase 1: Foundation (MVP)
- [/] Project Scaffolding
    - [ ] Initialize project structure (Python) <!-- id: 1 -->
    - [ ] Create virtual environment and core dependencies <!-- id: 2 -->
- [ ] Configuration Module
    - [ ] Implement `codesubmit.yaml` parser using `PyYAML` <!-- id: 3 -->
    - [ ] Define default configuration schema <!-- id: 4 -->
- [ ] Source Scanner
    - [ ] Implement recursive folder scanning <!-- id: 5 -->
    - [ ] Add filtering by extension and exclusion patterns <!-- id: 6 -->
- [ ] Execution Engine
    - [ ] Create `Executor` class for running shell commands <!-- id: 7 -->
    - [ ] Implement timeout and error capturing (stdout/stderr) <!-- id: 8 -->
    - [ ] Add language-specific constants (e.g., how to run .py vs .java) <!-- id: 9 -->
- [ ] Output Generator
    - [ ] Implement Markdown builder <!-- id: 10 -->
    - [ ] Create document header and per-file section templates <!-- id: 11 -->
- [ ] CLI Interface
    - [ ] Implement `click` or `argparse` CLI entry point <!-- id: 12 -->
    - [ ] Connect scanner, executor, and generator <!-- id: 13 -->

## Phase 2: Academic Polish
- [ ] Advanced Output Formats
    - [ ] Implement PDF export (via `weasyprint` or `pandoc`) <!-- id: 14 -->
    - [ ] Implement DOCX export (via `python-docx` or `pandoc`) <!-- id: 15 -->
- [ ] Templating System
    - [ ] Allow custom Jinja2 templates for headers <!-- id: 16 -->

## Phase 3: Advanced Proof
- [ ] Screenshot Capability
    - [ ] Integrate a library for taking screenshots of output (optional) <!-- id: 17 -->
- [ ] Security & Hashing
    - [ ] Add file hashing for integrity checks <!-- id: 18 -->
