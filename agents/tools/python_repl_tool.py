# agents/tools/python_repl_tool.py

"""
Python REPL Tool — Secure Sandboxed Execution Environment

Executes Python code, CSV/JSON manipulation, math, and Pandas logic
without OS access, subprocess execution, or network calls.
"""

import sys
import io
import ast
import time
import logging
import traceback
from typing import Dict, Any, Optional
from schemas.agent import ToolExecutionResult
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

# Forbidden modules and builtins for sandboxing
FORBIDDEN_KEYWORDS = [
    "import os", "import sys", "import subprocess", "import socket", "import httpx",
    "import requests", "import urllib", "import shutil", "os.", "sys.", "subprocess.",
    "eval(", "exec(", "__import__", "open(", "file(", "input("
]


class PythonREPLTool:
    """
    Sandboxed Python REPL for executing data transformations, algorithm logic, and CSV/JSON analysis.
    """

    def supports(self, input_data: Any, intent: Optional[str] = None) -> bool:
        """
        Validates if input data is valid executable Python code.
        Returns False for plain text requests ('Write Python code', 'Execute this Python code' without code snippet).
        """
        if isinstance(input_data, dict):
            code_str = input_data.get("code") or input_data.get("script") or input_data.get("query") or ""
        else:
            code_str = str(input_data)

        code_clean = str(code_str).strip()
        if not code_clean:
            return False

        q_lower = code_clean.lower()
        
        # Requests to write or explain code should NOT execute Python tool
        if any(phrase in q_lower for phrase in ["write python", "write code", "how to write", "explain code", "explain python"]):
            return False

        if q_lower in ["execute this python code", "run python", "run script", "execute code"]:
            return False

        try:
            ast.parse(code_clean)
            return True
        except Exception:
            return False

    def execute(self, code: str) -> ToolExecutionResult:
        t0 = time.time()
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/tools/python_repl_tool.py",
            class_name="PythonREPLTool",
            func_name="execute",
            purpose="Execute sandboxed Python code for data processing or algorithmic logic.",
            input_params={"code_len": len(code)}
        )

        if not self.supports(code):
            duration_ms = round((time.time() - t0) * 1000, 2)
            logger.info(f"[PYTHON_REPL] supports() = FALSE for input '{code[:40]}...'. Skipped.")
            return ToolExecutionResult(
                tool_name="python_repl",
                status="skipped",
                output={"reason": "unsupported_input", "message": "Python tool executes code only, not code generation or explanation."},
                execution_time_ms=duration_ms
            )

        # Check sandbox security rules
        for forbidden in FORBIDDEN_KEYWORDS:
            if forbidden in code:
                duration_ms = round((time.time() - t0) * 1000, 2)
                err_msg = f"Security Exception: Restricted module/call '{forbidden}' is prohibited in sandbox."
                EducationalLogger.log_educational_error(
                    file_name="agents/tools/python_repl_tool.py",
                    func_name="execute",
                    line_no=35,
                    error=SecurityError(err_msg),
                    input_data=code,
                    expected="Safe Python execution",
                    fix_suggestion="Remove restricted OS/network calls."
                )
                return ToolExecutionResult(
                    tool_name="python_repl",
                    status="error",
                    output=None,
                    error_message=err_msg,
                    execution_time_ms=duration_ms
                )

        # Capture stdout/stderr during execution
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        globals_dict: Dict[str, Any] = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
                "enumerate": enumerate, "float": float, "format": format, "int": int,
                "len": len, "list": list, "map": map, "max": max, "min": min,
                "pow": pow, "print": print, "range": range, "round": round,
                "set": set, "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
                "zip": zip, "True": True, "False": False, "None": None
            }
        }
        locals_dict: Dict[str, Any] = {}

        try:
            exec(code, globals_dict, locals_dict)
            captured_stdout = redirected_output.getvalue()
            sys.stdout = old_stdout
            duration_ms = round((time.time() - t0) * 1000, 2)

            res_val = captured_stdout if captured_stdout else str(locals_dict.get("result", "Execution completed successfully."))

            EducationalLogger.log_function_exit(
                file_name="agents/tools/python_repl_tool.py",
                class_name="PythonREPLTool",
                func_name="execute",
                returned_value=f"Output ({len(res_val)} chars)",
                start_time=start_time
            )

            return ToolExecutionResult(
                tool_name="python_repl",
                status="success",
                output={"stdout": captured_stdout, "variables": {k: str(v) for k, v in locals_dict.items() if not k.startswith("_")}},
                execution_time_ms=duration_ms
            )

        except Exception as e:
            sys.stdout = old_stdout
            duration_ms = round((time.time() - t0) * 1000, 2)
            EducationalLogger.log_educational_error(
                file_name="agents/tools/python_repl_tool.py",
                func_name="execute",
                line_no=70,
                error=e,
                input_data=code,
                expected="Clean execution output",
                fix_suggestion="Fix Python syntax or runtime error in generated code."
            )
            return ToolExecutionResult(
                tool_name="python_repl",
                status="error",
                output=None,
                error_message=f"Runtime Error: {str(e)}",
                execution_time_ms=duration_ms
            )


class SecurityError(Exception):
    pass
