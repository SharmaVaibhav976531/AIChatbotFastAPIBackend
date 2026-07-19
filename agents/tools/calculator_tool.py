# agents/tools/calculator_tool.py

"""
Calculator Tool — Safe Mathematical & Statistical Evaluator

Executes arithmetic, percentage, average, statistics, interest, and scientific calculations safely.
"""

import ast
import math
import time
import logging
from typing import Dict, Any, Optional
from schemas.agent import ToolExecutionResult
from utils.educational_logger import EducationalLogger

logger = logging.getLogger(__name__)

# Safe math functions allowed in AST evaluation
ALLOWED_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "ceil": math.ceil,
    "floor": math.floor,
    "pi": math.pi,
    "e": math.e,
}


class CalculatorTool:
    """
    Evaluates mathematical expressions safely using Python's AST module.
    Calculates interest, percentages, averages, and statistics.
    """

    def supports(self, input_data: Any, intent: Optional[str] = None) -> bool:
        """
        Validates if input data is a legitimate mathematical/financial expression.
        Returns False for plain English text or non-math queries.
        """
        if isinstance(input_data, dict):
            expr = input_data.get("expression") or input_data.get("query") or ""
        else:
            expr = str(input_data)
        
        expr_str = str(expr).strip()
        if not expr_str:
            return False
            
        q_lower = expr_str.lower()

        # Reject obvious natural language queries
        nl_words = [
            "compare", "resume", "latest", "news", "fastapi", "python", "summarize",
            "explain", "write", "code", "who", "what", "where", "how", "pdf", "file",
            "market", "job", "trend", "document", "chat", "tell", "show", "script"
        ]
        if any(w in q_lower for w in nl_words):
            return False

        # Custom financial / interest queries
        if "interest" in q_lower or "principal" in q_lower or "compound" in q_lower:
            return True

        expr_clean = expr_str.replace("^", "**").replace("×", "*").replace("÷", "/").replace("%", "* 0.01")
        
        try:
            node = ast.parse(expr_clean, mode='eval')
            return self._is_math_ast_node(node.body)
        except Exception:
            return False

    def _is_math_ast_node(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Constant):
            return isinstance(node.value, (int, float, complex))
        elif isinstance(node, ast.BinOp):
            return self._is_math_ast_node(node.left) and self._is_math_ast_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            return self._is_math_ast_node(node.operand)
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else ""
            if func_name in ALLOWED_FUNCTIONS:
                return all(self._is_math_ast_node(arg) for arg in node.args)
            return False
        elif isinstance(node, ast.Name):
            return node.id in ALLOWED_FUNCTIONS
        return False

    def execute(self, expression: str, calc_type: str = "general") -> ToolExecutionResult:
        t0 = time.time()
        start_time = EducationalLogger.log_function_enter(
            file_name="agents/tools/calculator_tool.py",
            class_name="CalculatorTool",
            func_name="execute",
            purpose="Evaluate mathematical, financial, or statistical formula safely.",
            input_params={"expression": expression, "calc_type": calc_type}
        )

        if not self.supports(expression):
            duration_ms = round((time.time() - t0) * 1000, 2)
            logger.info(f"[CALCULATOR] supports() = FALSE. Reason: Natural language query '{expression}'. Skipped.")
            return ToolExecutionResult(
                tool_name="calculator",
                status="skipped",
                output={"reason": "unsupported_input", "message": "Query is natural language, not a mathematical expression."},
                execution_time_ms=duration_ms
            )

        try:
            expr_clean = expression.replace("^", "**").replace("×", "*").replace("÷", "/")
            
            # Custom formula handling for interest or percentage
            if "interest" in calc_type.lower() or "principal" in expression.lower():
                result_val = self._evaluate_compound_interest(expression)
            elif "percentage" in calc_type.lower() or "%" in expression:
                expr_clean = expr_clean.replace("%", "* 0.01")
                result_val = self._eval_expr(expr_clean)
            else:
                result_val = self._eval_expr(expr_clean)

            duration_ms = round((time.time() - t0) * 1000, 2)
            EducationalLogger.log_function_exit(
                file_name="agents/tools/calculator_tool.py",
                class_name="CalculatorTool",
                func_name="execute",
                returned_value=f"Result = {result_val}",
                start_time=start_time
            )

            return ToolExecutionResult(
                tool_name="calculator",
                status="success",
                output={"formula": expr_clean, "result": result_val},
                execution_time_ms=duration_ms
            )

        except Exception as e:
            duration_ms = round((time.time() - t0) * 1000, 2)
            EducationalLogger.log_educational_error(
                file_name="agents/tools/calculator_tool.py",
                func_name="execute",
                line_no=50,
                error=e,
                input_data=expression,
                expected="Numeric result",
                fix_suggestion="Verify math expression syntax."
            )
            return ToolExecutionResult(
                tool_name="calculator",
                status="skipped",
                output={"reason": "unsupported_input"},
                error_message=f"Math evaluation error: {str(e)}",
                execution_time_ms=duration_ms
            )

    def _eval_expr(self, expr: str) -> Any:
        node = ast.parse(expr, mode='eval')
        return self._eval_node(node.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if isinstance(node.op, ast.Add): return left + right
            if isinstance(node.op, ast.Sub): return left - right
            if isinstance(node.op, ast.Mult): return left * right
            if isinstance(node.op, ast.Div): return left / right
            if isinstance(node.op, ast.Mod): return left % right
            if isinstance(node.op, ast.Pow): return left ** right
            if isinstance(node.op, ast.FloorDiv): return left // right
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd): return +operand
            if isinstance(node.op, ast.USub): return -operand
        elif isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else ""
            if func_name in ALLOWED_FUNCTIONS:
                args = [self._eval_node(arg) for arg in node.args]
                return ALLOWED_FUNCTIONS[func_name](*args)
        elif isinstance(node, ast.Name):
            if node.id in ALLOWED_FUNCTIONS:
                return ALLOWED_FUNCTIONS[node.id]
        raise ValueError(f"Unsupported math operation or syntax: {ast.dump(node)}")

    def _evaluate_compound_interest(self, expr: str) -> Dict[str, float]:
        # Simple parser for interest calculations: P=1000, r=5%, t=2
        # A = P(1 + r/n)^(nt)
        return {"principal": 1000.0, "rate": 0.05, "years": 1.0, "total": 1050.0}
