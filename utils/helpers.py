# utils/helpers.py

import logging
import sys
import uuid
import json
from contextvars import ContextVar
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# REQUEST ID — Tracks a single request across all layers
# ══════════════════════════════════════════════════════════════════
request_id_var: ContextVar[str] = ContextVar("request_id", default="NO-REQUEST")

def generate_request_id() -> str:
    """Generate a short unique request ID like 'REQ-a1b2c3d4'."""
    return f"REQ-{uuid.uuid4().hex[:8]}"


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
    Custom formatter that adds:
    - ANSI colors based on log level
    - Request ID from context variable
    - Multi-line message support (prefix only on first line)

    Format: TIMESTAMP | LEVEL | REQUEST_ID | MODULE | MESSAGE
    """

    LEVEL_COLORS = {
        "DEBUG":    CYAN,
        "INFO":     GREEN,
        "WARNING":  YELLOW,
        "ERROR":    RED,
        "CRITICAL": f"{BOLD}{RED}",
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelname, "")
        req_id = request_id_var.get()
        timestamp = self.formatTime(record, self.datefmt)

        prefix = (
            f"{DIM}{timestamp}{RESET} | "
            f"{color}{BOLD}{record.levelname:<8}{RESET} | "
            f"{MAGENTA}{req_id:<12}{RESET} | "
            f"{BLUE}{record.name}{RESET}"
        )

        msg = record.getMessage()
        lines = msg.split("\n")
        result = f"{prefix} | {lines[0]}"
        for line in lines[1:]:
            result += f"\n{line}"

        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            result += f"\n{RED}{record.exc_text}{RESET}"

        return result


# ══════════════════════════════════════════════════════════════════
# SETUP LOGGING — Call once at application startup
# ══════════════════════════════════════════════════════════════════
def setup_logging():
    """Configure the entire logging system with colored output and debug level."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()
    root.addHandler(handler)

    # Suppress noisy third-party libraries
    for lib in ["httpx", "openai", "httpcore", "uvicorn.access", "watchfiles", "asyncio"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f"{CYAN}{'═' * 60}{RESET}")
    logger.info(f"{CYAN}{BOLD}  LOGGING SYSTEM INITIALIZED — DEBUG level for all app modules{RESET}")
    logger.info(f"{CYAN}{'═' * 60}{RESET}")


# ══════════════════════════════════════════════════════════════════
# BANNER BUILDERS — Visual request/response lifecycle blocks
# ══════════════════════════════════════════════════════════════════
def build_request_banner(req_id: str, method: str, path: str, client_ip: str,
                         body_text: str, timestamp: str) -> str:
    """
    Build the FRONTEND → BACKEND banner showing full request details.
    """
    border = f"{CYAN}{BOLD}{'═' * 64}{RESET}"
    title  = f"{CYAN}{BOLD}{'FRONTEND  →  BACKEND':^64}{RESET}"

    lines = [
        "",
        border,
        title,
        border,
        f"  {WHITE}Request ID{RESET}  : {MAGENTA}{BOLD}{req_id}{RESET}",
        f"  {WHITE}Timestamp{RESET}   : {DIM}{timestamp}{RESET}",
        f"  {WHITE}Method{RESET}      : {GREEN}{BOLD}{method}{RESET}",
        f"  {WHITE}Endpoint{RESET}    : {GREEN}{BOLD}{path}{RESET}",
        f"  {WHITE}Client IP{RESET}   : {DIM}{client_ip}{RESET}",
    ]

    # Try to extract user message and pretty-print JSON
    if body_text:
        try:
            body_json = json.loads(body_text)
            pretty_body = json.dumps(body_json, indent=4, ensure_ascii=False)
            user_msg = body_json.get("message", "")
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
    """
    Build the BACKEND → FRONTEND banner showing full response details.
    """
    border = f"{MAGENTA}{BOLD}{'═' * 64}{RESET}"
    title  = f"{MAGENTA}{BOLD}{'BACKEND  →  FRONTEND':^64}{RESET}"

    # Status color
    if status_code >= 500:
        status_color = RED
        status_label = f"{status_code} SERVER ERROR ❌"
    elif status_code >= 400:
        status_color = YELLOW
        status_label = f"{status_code} CLIENT ERROR ⚠️"
    elif status_code >= 300:
        status_color = CYAN
        status_label = f"{status_code} REDIRECT ↩️"
    else:
        status_color = GREEN
        status_label = f"{status_code} OK ✅"

    lines = [
        "",
        border,
        title,
        border,
        f"  {WHITE}Request ID{RESET}  : {MAGENTA}{BOLD}{req_id}{RESET}",
        f"  {WHITE}HTTP Status{RESET} : {status_color}{BOLD}{status_label}{RESET}",
        f"  {WHITE}Duration{RESET}    : {CYAN}{BOLD}{duration_ms:.1f}ms{RESET}",
    ]

    # Pretty-print JSON response body
    if body_text:
        try:
            body_json = json.loads(body_text)
            # Extract assistant reply if present
            reply = body_json.get("reply", "")
            if reply:
                preview = reply[:200] + ("..." if len(reply) > 200 else "")
                lines.append("")
                lines.append(f"  {YELLOW}{BOLD}Assistant Response:{RESET}")
                lines.append(f"  {WHITE}\"{preview}\"{RESET}")

            pretty_body = json.dumps(body_json, indent=4, ensure_ascii=False)
            # Truncate very long response bodies in the banner
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