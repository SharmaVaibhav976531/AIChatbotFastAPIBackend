# utils/educational_logger.py

"""
Educational Logging Utility for FastAPI AI Chatbot

Provides 100% real, teacher-style formatted logging for terminal debugging:
- Real file entry & responsibility banners
- Function entry / exit telemetry
- Step-by-step function intent & call reasons
- Database & Repository execution breakdown (SQL, latency, row counts)
- Auth, Session, Message, Embedding, Vector Search & OpenRouter LLM telemetry
- Dynamic End-of-Request execution tree based ONLY on what actually executed
- Zero fake, misleading, or placeholder logs
"""

import logging
import time
import traceback
from typing import Any, Optional
from utils.helpers import (
    request_id_var, execution_tree_var, record_execution_step,
    CYAN, GREEN, YELLOW, RED, MAGENTA, BLUE, WHITE, BOLD, DIM, RESET
)

logger = logging.getLogger("educational")


class EducationalLogger:
    """
    Teacher-style logger that prints structured, colorful terminal logs
    explaining architectural flow, inputs, outputs, and database operations.
    """
    
    _file_logged: set[str] = set()

    @classmethod
    def log_file_execution(cls, file_name: str, purpose: str, responsibilities: list[str]) -> None:
        """Prints a banner when execution enters a new architectural file."""
        req_id = request_id_var.get()
        key = f"{req_id}:{file_name}"
        if key in cls._file_logged:
            return
        cls._file_logged.add(key)

        border = f"{CYAN}{BOLD}{'═' * 64}{RESET}"
        resp_lines = "\n".join([f"  {WHITE}• {r}{RESET}" for r in responsibilities])

        msg = (
            f"\n{border}\n"
            f"  {CYAN}{BOLD}NOW EXECUTING FILE{RESET}\n"
            f"  {CYAN}{'─' * 20}{RESET}\n"
            f"  {WHITE}File{RESET}           : {MAGENTA}{BOLD}{file_name}{RESET}\n"
            f"  {WHITE}Purpose{RESET}        : {WHITE}{purpose}{RESET}\n"
            f"  {WHITE}Responsibilities{RESET} :\n{resp_lines}\n"
            f"{border}\n"
        )
        logger.info(msg)
        record_execution_step(f"File: {file_name}")

    @classmethod
    def log_function_enter(cls, file_name: str, class_name: str | None, func_name: str, purpose: str, input_params: dict[str, Any]) -> float:
        """Logs function entry with inputs, purpose, and timestamp."""
        start_time = time.time()
        cls_str = f"{class_name}." if class_name else ""
        border = f"{BLUE}{'═' * 60}{RESET}"
        
        inputs_str = ", ".join([f"{k}={v}" for k, v in input_params.items()]) if input_params else "None"
        
        msg = (
            f"\n{border}\n"
            f"  {BLUE}{BOLD}ENTERING FUNCTION{RESET} -> {BLUE}{cls_str}{func_name}(){RESET}\n"
            f"  {WHITE}File{RESET}    : {DIM}{file_name}{RESET}\n"
            f"  {WHITE}Purpose{RESET} : {WHITE}{purpose}{RESET}\n"
            f"  {WHITE}Input{RESET}   : {YELLOW}{inputs_str}{RESET}\n"
            f"{border}"
        )
        logger.info(msg)
        record_execution_step(f"{cls_str}{func_name}()")
        return start_time

    @classmethod
    def log_function_exit(cls, file_name: str, class_name: str | None, func_name: str, returned_value: Any, start_time: float, status: str = "SUCCESS") -> None:
        """Logs function exit with execution duration and status."""
        duration_ms = round((time.time() - start_time) * 1000, 2)
        cls_str = f"{class_name}." if class_name else ""
        border = f"{GREEN if status == 'SUCCESS' else RED}{'═' * 60}{RESET}"
        
        val_str = str(returned_value)
        if len(val_str) > 120:
            val_str = val_str[:120] + "... [truncated]"

        msg = (
            f"\n{border}\n"
            f"  {GREEN if status == 'SUCCESS' else RED}{BOLD}EXITING FUNCTION{RESET} <- {GREEN if status == 'SUCCESS' else RED}{cls_str}{func_name}(){RESET}\n"
            f"  {WHITE}File{RESET}     : {DIM}{file_name}{RESET}\n"
            f"  {WHITE}Returned{RESET} : {WHITE}{val_str}{RESET}\n"
            f"  {WHITE}Time{RESET}     : {CYAN}{BOLD}{duration_ms} ms{RESET}\n"
            f"  {WHITE}Status{RESET}   : {GREEN if status == 'SUCCESS' else RED}{BOLD}{status}{RESET}\n"
            f"{border}"
        )
        logger.info(msg)

    @classmethod
    def log_function_intent(cls, target_func: str, reason: str, input_desc: str, expected_output: str) -> None:
        """Explains why a specific sub-function is being invoked."""
        msg = (
            f"\n  {YELLOW}👉 Calling Function{RESET} : {BOLD}{target_func}(){RESET}\n"
            f"     {WHITE}Reason{RESET}          : {reason}\n"
            f"     {WHITE}Input{RESET}           : {DIM}{input_desc}{RESET}\n"
            f"     {WHITE}Expected Output{RESET} : {GREEN}{expected_output}{RESET}"
        )
        logger.info(msg)

    @classmethod
    def log_auth_event(cls, event_type: str, user_identifier: str, success: bool, detail: str = "") -> None:
        """Logs actual authentication lifecycle events."""
        status_str = f"{GREEN}SUCCESS{RESET}" if success else f"{RED}FAILED{RESET}"
        msg = (
            f"  {MAGENTA}🔑 AUTH EVENT{RESET} | {BOLD}{event_type}{RESET} | User: {WHITE}{user_identifier}{RESET} | "
            f"Status: {status_str}" + (f" | {DIM}{detail}{RESET}" if detail else "")
        )
        logger.info(msg)
        record_execution_step(f"Auth: {event_type} ({user_identifier})")

    @classmethod
    def log_session_event(cls, action: str, session_id: str, detail: str = "") -> None:
        """Logs actual chat session lifecycle events."""
        msg = (
            f"  {CYAN}💬 SESSION EVENT{RESET} | {BOLD}{action}{RESET} | Session ID: {MAGENTA}{session_id}{RESET}"
            + (f" | {DIM}{detail}{RESET}" if detail else "")
        )
        logger.info(msg)
        record_execution_step(f"Session: {action} ({session_id[:8]}...)")

    @classmethod
    def log_message_event(cls, role: str, session_id: str, message_id: str, length: int) -> None:
        """Logs message creation and history loading events."""
        msg = (
            f"  {GREEN}✉️ MESSAGE PERSISTED{RESET} | Role: {YELLOW}{role}{RESET} | Session: {MAGENTA}{session_id[:8]}...{RESET} | "
            f"ID: {DIM}{message_id}{RESET} | Length: {CYAN}{length} chars{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"Message: Save {role} message")

    @classmethod
    def log_repo_operation(cls, repo_name: str, method_name: str, purpose: str, sql_op: str, table: str, input_params: dict[str, Any], output_summary: str, duration_ms: float) -> None:
        """Explains repository operations and database interactions."""
        msg = (
            f"\n  {CYAN}{BOLD}REPOSITORY EXECUTION{RESET}\n"
            f"  {CYAN}{'─' * 20}{RESET}\n"
            f"  {WHITE}Repository{RESET}   : {BOLD}{repo_name}{RESET}\n"
            f"  {WHITE}Method{RESET}       : {CYAN}{method_name}(){RESET}\n"
            f"  {WHITE}Purpose{RESET}      : {purpose}\n"
            f"  {WHITE}SQL Operation{RESET}: {YELLOW}{BOLD}{sql_op}{RESET} on table {MAGENTA}{BOLD}{table}{RESET}\n"
            f"  {WHITE}Input Params{RESET} : {DIM}{input_params}{RESET}\n"
            f"  {WHITE}Output Data{RESET}  : {GREEN}{output_summary}{RESET}\n"
            f"  {WHITE}Duration{RESET}     : {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"{repo_name}.{method_name}() [{sql_op} on {table}]")

    @classmethod
    def log_db_query(cls, operation: str, table: str, reason: str, rows_returned: int, duration_ms: float) -> None:
        """Explains direct database query executions."""
        msg = (
            f"  {CYAN}💾 DB QUERY{RESET} | {YELLOW}{operation}{RESET} on {MAGENTA}{table}{RESET} | "
            f"Reason: {reason} | Rows: {GREEN}{rows_returned}{RESET} | Time: {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)

    @classmethod
    def log_embedding_execution(cls, model_name: str, input_count: int, dimensions: int, duration_ms: float, truncated_dim: Optional[int] = None) -> None:
        """Logs vector embedding generation when it ACTUALLY occurs."""
        trunc_str = f" → Truncated to {truncated_dim} dims" if truncated_dim else ""
        msg = (
            f"  {MAGENTA}🧠 EMBEDDING GENERATED{RESET} | Model: {WHITE}{model_name}{RESET} | "
            f"Chunks: {GREEN}{input_count}{RESET} | Raw Dim: {CYAN}{dimensions}{RESET}{trunc_str} | Time: {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"EmbeddingService (Model: {model_name})")

    @classmethod
    def log_vector_search_execution(cls, metric: str, top_k: int, threshold: float, retrieved_count: int, chunk_ids: list[str], duration_ms: float) -> None:
        """Logs pgvector similarity search when it ACTUALLY occurs."""
        ids_str = ", ".join(chunk_ids[:3]) + ("..." if len(chunk_ids) > 3 else "") if chunk_ids else "None"
        msg = (
            f"  {MAGENTA}🔍 VECTOR SEARCH{RESET} | Metric: {WHITE}{metric}{RESET} | Top-K: {YELLOW}{top_k}{RESET} | "
            f"Threshold: {DIM}{threshold}{RESET} | Retrieved Chunks: {GREEN}{retrieved_count}{RESET} [{ids_str}] | Time: {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"VectorSearch (Retrieved {retrieved_count} chunks)")

    @classmethod
    def log_prompt_builder_execution(cls, system_prompt_len: int, context_len: int, history_count: int) -> None:
        """Logs prompt construction when RAG / System prompt is assembled."""
        msg = (
            f"  {YELLOW}📝 PROMPT ASSEMBLED{RESET} | System Prompt: {CYAN}{system_prompt_len} chars{RESET} | "
            f"RAG Context: {GREEN}{context_len} chars{RESET} | History Messages: {MAGENTA}{history_count}{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"PromptBuilder (Context: {context_len} chars, History: {history_count})")

    @classmethod
    def log_openrouter_execution(cls, model_name: str, messages_count: int, total_tokens: Optional[int], duration_ms: float) -> None:
        """Logs OpenRouter LLM completion call when it ACTUALLY occurs."""
        token_str = f"Total Tokens: {CYAN}{total_tokens}{RESET} | " if total_tokens is not None else ""
        msg = (
            f"  {GREEN}🤖 OPENROUTER LLM CALL{RESET} | Model: {WHITE}{model_name}{RESET} | "
            f"Messages: {YELLOW}{messages_count}{RESET} | {token_str}Duration: {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)
        record_execution_step(f"OpenRouter LLM ({model_name})")

    @classmethod
    def log_cache_event(cls, cache_key: str, event_type: str, ttl: Optional[int] = None) -> None:
        """Logs Redis cache hits and misses when they ACTUALLY occur."""
        color = GREEN if event_type.upper() == "HIT" else YELLOW
        ttl_str = f" (TTL: {ttl}s)" if ttl is not None else ""
        msg = (
            f"  {BLUE}⚡ REDIS CACHE {event_type.upper()}{RESET} | Key: {WHITE}{cache_key}{RESET}{ttl_str}"
        )
        logger.info(msg)

    @classmethod
    def log_rag_pipeline_banner(cls, query: str, session_id: str | None = None) -> None:
        """Prints a visual banner when the RAG retrieval pipeline begins."""
        border = f"{MAGENTA}{BOLD}{'═' * 64}{RESET}"
        msg = (
            f"\n{border}\n"
            f"  {MAGENTA}{BOLD}RAG RETRIEVAL PIPELINE STARTED{RESET}\n"
            f"  {MAGENTA}{'─' * 30}{RESET}\n"
            f"  {WHITE}User Query{RESET} : {WHITE}\"{query}\"{RESET}\n"
            f"  {WHITE}Session ID{RESET} : {MAGENTA}{session_id or 'Global'}{RESET}\n"
            f"{border}"
        )
        logger.info(msg)

    @classmethod
    def log_rag_step(cls, step_num: int, step_name: str, why_needed: str, input_data: Any, output_data: Any, duration_ms: float) -> None:
        """Prints details for each specific stage of the RAG pipeline when it ACTUALLY executes."""
        in_str = str(input_data)[:80]
        out_str = str(output_data)[:80]
        msg = (
            f"\n  {MAGENTA}📌 STEP {step_num}: {BOLD}{step_name.upper()}{RESET}\n"
            f"     {WHITE}Why Needed{RESET} : {why_needed}\n"
            f"     {WHITE}Input{RESET}      : {DIM}{in_str}{RESET}\n"
            f"     {WHITE}Output{RESET}     : {GREEN}{out_str}{RESET}\n"
            f"     {WHITE}Latency{RESET}    : {CYAN}{duration_ms} ms{RESET}"
        )
        logger.info(msg)

    @classmethod
    def log_dependency_injection(cls, dependency_name: str, purpose: str, injected_type: str) -> None:
        """Explains FastAPI Depends() dependency injection."""
        msg = (
            f"  {BLUE}💉 DEPENDENCY INJECTED{RESET} | {BOLD}{dependency_name}{RESET} ({injected_type})\n"
            f"     {DIM}Purpose: {purpose}{RESET}"
        )
        logger.info(msg)

    @classmethod
    def log_execution_tree(cls, nodes: Optional[list[str]] = None) -> None:
        """
        Prints an end-of-request visual execution tree showing ONLY nodes that ACTUALLY executed.
        If nodes is None, reads directly from the request's execution_tree_var ContextVar.
        """
        real_nodes = nodes
        if real_nodes is None:
            real_nodes = execution_tree_var.get()
        
        if not real_nodes:
            return

        border = f"{CYAN}{BOLD}{'═' * 64}{RESET}"
        tree_str = "\n".join([f"  {CYAN}↓{RESET} {WHITE}{node}{RESET}" if i > 0 else f"  {GREEN}●{RESET} {WHITE}{node}{RESET}" for i, node in enumerate(real_nodes)])
        msg = (
            f"\n{border}\n"
            f"  {CYAN}{BOLD}ACTUAL REQUEST EXECUTION TREE{RESET}\n"
            f"  {CYAN}{'─' * 28}{RESET}\n"
            f"{tree_str}\n"
            f"{border}\n"
        )
        logger.info(msg)

    @classmethod
    def log_educational_error(cls, file_name: str, func_name: str, line_no: int, error: Exception, input_data: Any, expected: str, fix_suggestion: str) -> None:
        """Prints detailed educational error diagnostic when failures occur."""
        border = f"{RED}{BOLD}{'═' * 64}{RESET}"
        msg = (
            f"\n{border}\n"
            f"  {RED}{BOLD}🚨 EDUCATIONAL ERROR DIAGNOSTIC{RESET}\n"
            f"  {RED}{'─' * 30}{RESET}\n"
            f"  {WHITE}Location{RESET}        : {MAGENTA}{file_name}{RESET}:{YELLOW}{line_no}{RESET} in {BOLD}{func_name}(){RESET}\n"
            f"  {WHITE}Error Type{RESET}      : {RED}{BOLD}{type(error).__name__}{RESET}\n"
            f"  {WHITE}Error Detail{RESET}    : {RED}{str(error)}{RESET}\n"
            f"  {WHITE}Input Data{RESET}      : {DIM}{input_data}{RESET}\n"
            f"  {WHITE}Expected Result{RESET} : {GREEN}{expected}{RESET}\n"
            f"  {WHITE}Suggested Fix{RESET}   : {YELLOW}{fix_suggestion}{RESET}\n"
            f"  {WHITE}Stack Trace{RESET}     :\n{RED}{traceback.format_exc()}{RESET}\n"
            f"{border}\n"
        )
        logger.error(msg)
