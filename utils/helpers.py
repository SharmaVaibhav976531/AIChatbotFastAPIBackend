# utils/helpers.py

import logging
import sys
import uuid
import json
from contextvars import ContextVar

# ══════════════════════════════════════════════════════════════════
# REQUEST ID — Tracks a single request across all layers
# ══════════════════════════════════════════════════════════════════
request_id_var: ContextVar[str] = ContextVar("request_id", default="NO-REQUEST")
execution_tree_var: ContextVar[list] = ContextVar("execution_tree", default=None)

def generate_request_id() -> str:
    """Generate a short unique request ID like 'REQ-a1b2c3d4'."""
    return f"REQ-{uuid.uuid4().hex[:8]}"

def record_execution_step(step_name: str) -> None:
    """Appends a node step to the active request's real execution tree."""
    tree = execution_tree_var.get()
    if tree is not None:
        tree.append(step_name)


# ══════════════════════════════════════════════════════════════════
# ANSI COLOR CODES — For colorful terminal output
# ══════════════════════════════════════════════════════════════════
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"
WHITE   = "\033[97m"
GREY    = "\033[90m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RESET   = "\033[0m"


# ══════════════════════════════════════════════════════════════════
# COLORED LOG FORMATTER — Pretty, structured terminal output
# ══════════════════════════════════════════════════════════════════
class ColoredFormatter(logging.Formatter):
    """
    Advanced formatter that injects Request IDs and applies level-based colors.
    """
    LEVEL_COLORS = {
        "DEBUG":    CYAN,
        "INFO":     GREEN,
        "WARNING":  YELLOW,
        "ERROR":    RED,
        "CRITICAL": f"{BOLD}{RED}",
    }

    def format(self, record):
        # Get color for the log level
        color = self.LEVEL_COLORS.get(record.levelname, WHITE)
        
        # Fetch the request ID from the ContextVar
        req_id = request_id_var.get()
        
        # Format timestamp
        timestamp = self.formatTime(record, self.datefmt)

        # Build the colorful prefix
        prefix = (
            f"{DIM}{timestamp}{RESET} | "
            f"{color}{BOLD}{record.levelname:<8}{RESET} | "
            f"{MAGENTA}{req_id:<12}{RESET} | "
            f"{BLUE}{record.name:<25}{RESET}"
        )

        # Process the log message
        msg = record.getMessage()
        lines = msg.split("\n")
        result = f"{prefix} | {lines[0]}"
        
        # Handle multi-line messages
        for line in lines[1:]:
            result += f"\n{line}"

        # Handle exceptions (tracebacks)
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            result += f"\n{RED}{record.exc_text}{RESET}"

        return result


# ══════════════════════════════════════════════════════════════════
# SETUP LOGGING — Call once at application startup
# ══════════════════════════════════════════════════════════════════
def setup_logging():
    """Configure the entire logging system with colored output."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    root = logging.getLogger()
    root.setLevel(logging.INFO) 
    root.handlers.clear()
    root.addHandler(handler)

    # Suppress noisy third-party libraries
    # Added sqlalchemy.engine so raw SQL queries don't ruin the beautiful banners
    noisy_libs = [
        "httpx", "openai", "httpcore", "uvicorn.access", 
        "watchfiles", "asyncio", "sqlalchemy.engine", "alembic"
    ]
    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.WARNING)
        
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"{CYAN}{'═' * 60}{RESET}")
    logger.info(f"{CYAN}{BOLD}  LOGGING SYSTEM INITIALIZED — Production Colorful Logger{RESET}")
    logger.info(f"{CYAN}{'═' * 60}{RESET}")


# ══════════════════════════════════════════════════════════════════
# BANNER BUILDERS — Visual request/response lifecycle blocks
# ══════════════════════════════════════════════════════════════════
def build_request_banner(req_id: str, method: str, path: str, client_ip: str,
                         body_text: str, timestamp: str) -> str:
    """Build the FRONTEND → BACKEND banner showing full request details."""
    border = f"{CYAN}{BOLD}{'═' * 64}{RESET}"
    title  = f"{CYAN}{BOLD}{'FRONTEND  →  BACKEND':^64}{RESET}"

    lines = [
        "", border, title, border,
        f"  {WHITE}Request ID{RESET}  : {MAGENTA}{BOLD}{req_id}{RESET}",
        f"  {WHITE}Timestamp{RESET}   : {DIM}{timestamp}{RESET}",
        f"  {WHITE}Method{RESET}      : {GREEN}{BOLD}{method}{RESET}",
        f"  {WHITE}Endpoint{RESET}    : {GREEN}{BOLD}{path}{RESET}",
        f"  {WHITE}Client IP{RESET}   : {DIM}{client_ip}{RESET}",
    ]

    if body_text:
        try:
            body_json = json.loads(body_text)
            pretty_body = json.dumps(body_json, indent=4, ensure_ascii=False)
            user_msg = body_json.get("message", "") if isinstance(body_json, dict) else ""
            
            if user_msg:
                lines.append("")
                lines.append(f"  {YELLOW}{BOLD}User Message:{RESET}")
                lines.append(f"  {WHITE}\"{user_msg}\"{RESET}")
            lines.append("")
            lines.append(f"  {WHITE}Request Body (JSON):{RESET}")
            for bl in pretty_body.split("\n"):
                lines.append(f"  {DIM}{bl}{RESET}")
        except json.JSONDecodeError:
            lines.append("")
            lines.append(f"  {WHITE}Request Body (raw):{RESET}")
            lines.append(f"  {DIM}{body_text[:500]}{RESET}")
    else:
        lines.append("")
        lines.append(f"  {DIM}(no request body){RESET}")

    lines.append(border)
    lines.append("")
    return "\n".join(lines)


def build_response_banner(req_id: str, status_code: int, duration_ms: float,
                          body_text: str) -> str:
    """Build the BACKEND → FRONTEND banner showing full response details."""
    border = f"{MAGENTA}{BOLD}{'═' * 64}{RESET}"
    title  = f"{MAGENTA}{BOLD}{'BACKEND  →  FRONTEND':^64}{RESET}"

    if status_code >= 500:
        status_color, status_label = RED, f"{status_code} SERVER ERROR ❌"
    elif status_code >= 400:
        status_color, status_label = YELLOW, f"{status_code} CLIENT ERROR ⚠️"
    elif status_code >= 300:
        status_color, status_label = CYAN, f"{status_code} REDIRECT ↩️"
    else:
        status_color, status_label = GREEN, f"{status_code} OK ✅"

    lines = [
        "", border, title, border,
        f"  {WHITE}Request ID{RESET}  : {MAGENTA}{BOLD}{req_id}{RESET}",
        f"  {WHITE}HTTP Status{RESET} : {status_color}{BOLD}{status_label}{RESET}",
        f"  {WHITE}Duration{RESET}    : {CYAN}{BOLD}{duration_ms:.1f}ms{RESET}",
    ]

    if body_text:
        try:
            body_json = json.loads(body_text)
            
            # Safely extract assistant reply if it's a dictionary
            if isinstance(body_json, dict):
                reply = body_json.get("reply", "")
                if reply:
                    preview = reply[:200] + ("..." if len(reply) > 200 else "")
                    lines.append("")
                    lines.append(f"  {YELLOW}{BOLD}Assistant Response:{RESET}")
                    lines.append(f"  {WHITE}\"{preview}\"{RESET}")

            pretty_body = json.dumps(body_json, indent=4, ensure_ascii=False)
            body_lines = pretty_body.split("\n")
            if len(body_lines) > 20:
                body_lines = body_lines[:18] + [f"    ... ({len(body_lines) - 18} more lines)"]
                
            lines.append("")
            lines.append(f"  {WHITE}Response Body (JSON):{RESET}")
            for bl in body_lines:
                lines.append(f"  {DIM}{bl}{RESET}")
        except json.JSONDecodeError:
            lines.append("")
            lines.append(f"  {WHITE}Response Body (raw):{RESET}")
            lines.append(f"  {DIM}{body_text[:300]}{RESET}")
    else:
        lines.append("")
        lines.append(f"  {DIM}(no response body){RESET}")

    lines.append(border)
    lines.append("")
    return "\n".join(lines)