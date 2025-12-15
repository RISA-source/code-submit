import subprocess
import time
import os
import sys
import shlex
import threading
from dataclasses import dataclass, field
from typing import List, Tuple, Any, Dict, Optional
from .scanner import SourceFile

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    command: str
    context: Dict[str, str]
    timed_out: bool

    def to_dict(self):
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "duration": self.duration,
            "command": self.command,
            "context": self.context,
            "timed_out": self.timed_out
        }

def sys_python_executable():
    import sys
    return sys.executable

def stream_reader(pipe, out_buffer, stream_dest):
    """
    Reads from 'pipe' line by line (or chunk).
    Writes to 'out_buffer' (list of str).
    Writes to 'stream_dest' (e.g. sys.stdout).
    """
    try:
        # iter(pipe.readline, b'') works if pipe is binary
        # If text mode, just pipe.readline
        for line in iter(pipe.readline, ''):
            out_buffer.append(line)
            stream_dest.write(line)
            stream_dest.flush()
    except (ValueError, OSError):
        pass

def get_java_class_name(file_path: str) -> Optional[str]:
    """
    detects package name from file content and returns 'package.ClassName'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            import re
            # Simple regex to find "package xyz;"
            match = re.search(r'^\s*package\s+([a-zA-Z0-9_.]+)\s*;', content, re.MULTILINE)
            package = match.group(1) if match else ""
            
            basename = os.path.basename(file_path)
            classname = os.path.splitext(basename)[0]
            
            if package:
                return f"{package}.{classname}"
            return classname
    except:
        return None

def compile_java_project(root_dir: str):
    """Compiles all java files in the directory."""
    # Find all java files recursively? Or just in the root?
    # For now, let's assume valid source root.
    # We'll run javac on specific files found by scanner?
    pass # Implemented inline in execute_files

def execute_files(files: List[SourceFile], config) -> List[Tuple[SourceFile, Optional[ExecutionResult]]]:
    results = []
    
    if not config.execution_enabled:
        return [(f, None) for f in files]

    timeout = config.timeout
    
    # JAVA PRE-COMPILATION STEP
    java_files = [f for f in files if f.language == 'Java']
    if java_files:
        print("\n--- Compiling Java Files ---")
        # We need to compile relative to the input root so packages work.
        # Assuming config.input_root is the source root.
        
        # Build list of all java files to compile
        # We assume 'files' has absolute paths.
        java_paths = [f.path for f in java_files]
        
        # Compile command: javac -d . file1.java file2.java ...
        # We run this in the input_root/.. or input_root?
        # If files contain "package Workshop3;", they should be in "Workshop3" folder.
        # We should run javac from the parent of "Workshop3".
        
        # Heuristic: The directory containing the "package" folder structure.
        # If config.input_root is "D:\...\src\Workshop3", and package is "Workshop3",
        # we should compile from "D:\...\src".
        
        try:
             # Basic Compilation attempt: Compile all found files
             # We assume they are compatible.
             
             # Check if we can just run javac on the files
             cmd = ["javac", "-encoding", "UTF-8"] + java_paths
             # We run this command, but where? 
             # Ideally from the config.root or its parent?
             # Let's try running from the lowest common ancestor?
             
             # Actually, simpler: Java CLASSPATH.
             # If we set CLASSPATH to the input root, maybe?
             
             # Let's try running javac in the directory of the first file?
             # Or just run it.
             
             compile_proc = subprocess.run(cmd, capture_output=True, text=True)
             if compile_proc.returncode != 0:
                 print("Warning: Java Compilation Failed!")
                 print(compile_proc.stderr)
                 # We continue, but execution will likely fail for interdependent files.
             else:
                 print("Compilation Successful.")
                 
        except Exception as e:
             print(f"Warning: Compilation step failed: {e}")

    for file in files:
        cmd = []
        if file.language == 'Python':
            cmd = [sys_python_executable(), '-u', file.path]
        elif file.language == 'Java':
            # Run the CLASS file, not the source file.
            # Convert file path to class name
            full_class = get_java_class_name(file.path)
            if full_class:
                # We need to set the classpath
                # If file is D:\...\src\Workshop3\Task.java and package is Workshop3,
                # we need to run java -cp D:\...\src Workshop3.Task
                
                # Determine classpath: it's the folder containing the top package.
                # If package is "Workshop3", we look for "Workshop3" in the path.
                
                parts = full_class.split('.')
                # If we have package "a.b", we expect path to end in "a/b/File.java"
                
                # Naive approach: use the config input root's parent? 
                # If the user pointed to ".../src/Workshop3" and package is "Workshop3",
                # valid CP is ".../src".
                
                source_root = os.path.dirname(file.path) # Default
                if '.' in full_class:
                    pkg_path = full_class.rsplit('.', 1)[0].replace('.', os.sep)
                    if file.path.endswith(pkg_path + os.sep + os.path.basename(file.path)):
                         # E.g. path matches package structure
                         # CP is path minus package suffix
                         trim_len = len(pkg_path) + len(os.path.basename(file.path)) + 1
                         source_root = file.path[:-trim_len]
                
                cmd = ['java', '-cp', source_root, full_class]
            else:
                 # Fallback to single-file mode if no class detected
                 cmd = ['java', file.path]
                 
        if not cmd:
            print(f"Skipping execution for {file.rel_path} ({file.language}): No runner defined.")
            results.append((file, None))
            continue

        print(f"\n--- Executing {file.rel_path} ---")
        start_time = time.time()
        
        context = {
            "cwd": os.getcwd(),
            "env_user": os.environ.get("USERNAME", "unknown"),
            "env_os": os.name
        }

        timed_out = False
        captured_stdout = []
        captured_stderr = []
        exit_code = 0
        
        try:
            if config.interactive:
                # INTERACTIVE MODE: Full Session Capture
                # We need to capture what the user types AND what the program outputs.
                # Previous attempt (stdin=sys.stdin) bypassed capture.
                # New plan:
                # 1. Thread 1: Read process stdout -> Print to Console + Append to Log
                # 2. Thread 2: Read process stderr -> Print to Console + Append to Log
                # 3. Thread 3 (Main): Read Console stdin -> Write to Process stdin + Append to Log
                
                # Note: Reading sys.stdin on Windows can be blocking.
                # However, since we are in "Interactive Mode", blocking on user input is EXPECTED behavior.
                # We essentially act as a proxy.
                
                proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE, # We will write to this
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1, # Line buffered
                    errors='replace'
                )
                
                # Shared log for chronological order (optional, but nice)
                # For now, we append input to captured_stdout to make it look like a terminal session.
                
                # Actually, 'msvcrt' is low level console.
                # Simpler: Just run a thread that reads input() and writes line-by-line?
                # Does that show characters as they are typed? Yes, the terminal handles echo.
                
                def input_thread_func():
                    try:
                        while proc.poll() is None:
                            # Use input() to block wait for line?
                            # If we block, we can't exit when proc dies?
                            # Thread will die when daemonized?
                            line = sys.stdin.readline()
                            if not line: break
                            
                            try:
                                proc.stdin.write(line)
                                proc.stdin.flush()
                                captured_stdout.append(line) # Add USER INPUT to the captured log
                            except IOError:
                                break
                    except:
                        pass

                t_in = threading.Thread(target=input_thread_func)
                t_in.daemon = True # Die when main dies
                t_in.start()

                t_out = threading.Thread(target=stream_reader, args=(proc.stdout, captured_stdout, sys.stdout))
                t_err = threading.Thread(target=stream_reader, args=(proc.stderr, captured_stderr, sys.stderr))
                
                t_out.start()
                t_err.start()
                
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    timed_out = True
                
                t_out.join(timeout=1)
                t_err.join(timeout=1)
                # t_in might still be blocked on readline, but daemon=True handles it.
                
                exit_code = proc.returncode

            else:
                # BATCH MODE
                stdin_content = config.stdin_input.encode('utf-8') if config.stdin_input else b""
                proc = subprocess.run(
                    cmd,
                    input=stdin_content,
                    capture_output=True,
                    timeout=timeout,
                    check=False
                )
                captured_stdout = [proc.stdout.decode('utf-8', errors='replace')]
                captured_stderr = [proc.stderr.decode('utf-8', errors='replace')]
                exit_code = proc.returncode
            
            duration = time.time() - start_time
            
            res = ExecutionResult(
                stdout="".join(captured_stdout),
                stderr="".join(captured_stderr),
                exit_code=exit_code if exit_code is not None else -1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=timed_out
            )
            
        except Exception as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                stdout="".join(captured_stdout),
                stderr=str(e),
                exit_code=-1,
                duration=duration,
                command=shlex.join(cmd),
                context=context,
                timed_out=False
            )
            
        results.append((file, res))
        
    return results
