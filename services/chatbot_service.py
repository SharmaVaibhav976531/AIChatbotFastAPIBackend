# services/chatbot_service.py

from openai import OpenAI, APIError, APITimeoutError, APIConnectionError, AuthenticationError
from core.settings import get_settings
import logging
import time

logger = logging.getLogger(__name__)


class ChatbotService:
    """Core service that communicates with the AI model via OpenRouter."""

    def __init__(self):
        logger.info("[SERVICE INIT] ── Step 1/3: Loading settings...")
        self.settings = get_settings()
        logger.info("[SERVICE INIT] ── Step 1/3: ✅ Settings loaded")

        logger.info("[SERVICE INIT] ── Step 2/3: Creating OpenAI client...")
        logger.info(f"  → Base URL : {self.settings.base_url}")
        logger.info(f"  → Timeout  : 30.0s")
        logger.info(f"  → Retries  : 3")
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.openrouter_api_key,
            timeout=30.0,
            max_retries=3,
        )
        logger.info("[SERVICE INIT] ── Step 2/3: ✅ OpenAI client created")

        self.system_prompt = "You are a helpful, concise AI assistant."
        # In-memory conversation history
        self.messages: list[dict] = [{"role": "system", "content": self.system_prompt}]
        logger.info(f"[SERVICE INIT] ── Step 3/3: ✅ History initialized (system prompt set)")
        logger.info("[SERVICE INIT] ✅ ChatbotService fully initialized")

    def get_response(self, user_message: str) -> str:
        """Send user message to AI and return the reply."""
        func_start = time.time()
        logger.info("─" * 50)
        logger.info(f"[SERVICE] get_response() CALLED")
        logger.info(f"[SERVICE]   → User message: ({len(user_message)} chars)")

        # Add user message to conversation history
        self.messages.append({"role": "user", "content": user_message})
        logger.info(f"[SERVICE]   → Message added to history → total: {len(self.messages)}")

        try:
            # Log the API call parameters
            logger.info(f"[SERVICE] Preparing OpenRouter API call:")
            logger.info(f"  → Model             : {self.settings.model_name}")
            logger.info(f"  → Context messages  : {len(self.messages)}")
            logger.info(f"  → Temperature       : {self.settings.temperature}")
            logger.info(f"  → Max tokens        : {self.settings.max_tokens}")
            logger.info(f"  → Top P             : {self.settings.top_p}")
            logger.info(f"  → Frequency penalty : {self.settings.frequency_penalty}")

            api_start = time.time()
            logger.info("[SERVICE] 🚀 Sending request to OpenRouter...")

            completion = self.client.chat.completions.create(
                model=self.settings.model_name,
                messages=self.messages,
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
                top_p=self.settings.top_p,
                frequency_penalty=self.settings.frequency_penalty,
            )

            api_ms = (time.time() - api_start) * 1000
            logger.info(f"[SERVICE] ✅ OpenRouter responded in {api_ms:.1f}ms")

            if completion and completion.choices:
                reply = completion.choices[0].message.content
                finish = completion.choices[0].finish_reason

                logger.info(f"[SERVICE] Response details:")
                logger.info(f"  → Finish reason : {finish}")
                logger.info(f"  → Reply length  : {len(reply)} chars")

                if completion.usage:
                    logger.info(f"  → Prompt tokens     : {completion.usage.prompt_tokens}")
                    logger.info(f"  → Completion tokens : {completion.usage.completion_tokens}")
                    logger.info(f"  → Total tokens      : {completion.usage.total_tokens}")

                self.messages.append({"role": "assistant", "content": reply})
                logger.info(f"[SERVICE] Assistant reply added → total: {len(self.messages)} messages")

                total_ms = (time.time() - func_start) * 1000
                logger.info(f"[SERVICE] get_response() COMPLETED in {total_ms:.1f}ms")
                logger.info("─" * 50)
                return reply

            logger.warning("[SERVICE] ⚠️ API returned NO CHOICES — empty response")
            return "[No choices returned by the API]"

        except AuthenticationError:
            logger.error("[SERVICE] ❌ AUTH ERROR — API key invalid/expired")
            logger.error("  → Fix: Check OPENROUTER_API_KEY in .env file")
            self.messages.pop()
            raise
        except APITimeoutError:
            logger.error("[SERVICE] ❌ TIMEOUT — No response within 30 seconds")
            logger.error("  → Fix: Model may be overloaded, try again later")
            self.messages.pop()
            raise
        except APIConnectionError:
            logger.error("[SERVICE] ❌ CONNECTION ERROR — Cannot reach OpenRouter")
            logger.error("  → Fix: Check internet connection")
            self.messages.pop()
            raise
        except APIError as e:
            logger.error(f"[SERVICE] ❌ API ERROR — {type(e).__name__}: {e}")
            self.messages.pop()
            raise
        except Exception as e:
            logger.error(f"[SERVICE] ❌ UNEXPECTED — {type(e).__name__}: {e}")
            self.messages.pop()
            raise

    def reset_conversation(self):
        """Clear all conversation history and start fresh."""
        old_count = len(self.messages) - 1  # exclude system prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]
        logger.info(f"[SERVICE] 🗑️ reset_conversation() → cleared {old_count} messages")

    def get_history(self) -> list[dict]:
        """Return conversation history excluding the system prompt."""
        # Exclude system prompt for a cleaner history view
        history = [msg for msg in self.messages if msg["role"] != "system"]
        logger.debug(f"[SERVICE] get_history() → returning {len(history)} messages")
        return history