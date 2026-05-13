import asyncio
import base64
import logging
from typing import Iterable

from anthropic import AsyncAnthropic, APIError, APIStatusError

from bot.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from bot.prompts import SYSTEM_PROMPT_ANALYZE, SYSTEM_PROMPT_FOLLOWUP

logger = logging.getLogger(__name__)


class ClaudeServiceError(Exception):
    """Raised when Claude fails to produce a usable response."""


_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _build_user_content(text: str | None, images: Iterable[bytes]) -> list[dict]:
    blocks: list[dict] = []
    for image_bytes in images:
        blocks.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": base64.standard_b64encode(image_bytes).decode("ascii"),
                },
            }
        )
    if text:
        blocks.append({"type": "text", "text": text})
    if not blocks:
        blocks.append({"type": "text", "text": "Расшифруй этот анализ."})
    return blocks


async def analyze_document(text: str | None, images: list[bytes]) -> str:
    user_content = _build_user_content(text, images)
    return await _call_with_retry(
        system=SYSTEM_PROMPT_ANALYZE,
        messages=[{"role": "user", "content": user_content}],
        max_tokens=2000,
    )


async def answer_followup(question: str, last_analysis: str) -> str:
    system = SYSTEM_PROMPT_FOLLOWUP.format(last_analysis=last_analysis)
    return await _call_with_retry(
        system=system,
        messages=[{"role": "user", "content": question}],
        max_tokens=1000,
    )


async def _call_with_retry(system: str, messages: list[dict], max_tokens: int) -> str:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = await _get_client().messages.create(
                model=CLAUDE_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            text = _extract_text(response)
            if text:
                return text
            logger.warning("Claude returned empty response on attempt %s", attempt + 1)
            last_error = ClaudeServiceError("empty response")
        except APIStatusError as exc:
            logger.warning("Claude API status error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
            if exc.status_code and 400 <= exc.status_code < 500 and exc.status_code != 429:
                break
        except APIError as exc:
            logger.warning("Claude API error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
        if attempt == 0:
            await asyncio.sleep(1.0)
    raise ClaudeServiceError(str(last_error) if last_error else "unknown error")


def _extract_text(response) -> str:
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "".join(parts).strip()
