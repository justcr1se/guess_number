import asyncio
import logging
from typing import AsyncIterator, Iterable

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from bot.config import GEMINI_API_KEY, GEMINI_MODEL
from bot.prompts import (
    ANALYZE_PROFILE_HINT,
    PROFILE_BLOCK_TEMPLATE,
    SYSTEM_PROMPT_ANALYZE,
    SYSTEM_PROMPT_FOLLOWUP,
)

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Raised when Gemini fails to produce a usable response."""


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _build_parts(text: str | None, images: Iterable[bytes]) -> list[types.Part]:
    parts: list[types.Part] = []
    for image_bytes in images:
        parts.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))
    if text:
        parts.append(types.Part.from_text(text=text))
    if not parts:
        parts.append(types.Part.from_text(text="Расшифруй этот анализ."))
    return parts


def _system_for_analyze(profile: str) -> str:
    base = SYSTEM_PROMPT_ANALYZE
    if profile:
        return base + ANALYZE_PROFILE_HINT.format(profile=profile)
    return base


def _system_for_followup(analyses: list[str], profile: str) -> str:
    if analyses:
        blocks = []
        for idx, text in enumerate(analyses, start=1):
            label = f"Анализ #{idx}" + (" (последний)" if idx == len(analyses) else "")
            blocks.append(f"=== {label} ===\n{text}")
        analyses_block = "\n\n".join(blocks)
    else:
        analyses_block = "(анализов в сессии нет)"
    profile_block = PROFILE_BLOCK_TEMPLATE.format(profile=profile) if profile else ""
    return SYSTEM_PROMPT_FOLLOWUP.format(
        analyses_block=analyses_block,
        profile_block=profile_block,
    )


async def stream_analyze_document(
    text: str | None,
    images: list[bytes],
    profile: str = "",
) -> AsyncIterator[str]:
    parts = _build_parts(text, images)
    async for chunk in _stream_with_retry(
        system_instruction=_system_for_analyze(profile),
        parts=parts,
        max_output_tokens=8192,
    ):
        yield chunk


async def answer_followup(
    question: str,
    analyses: list[str],
    profile: str = "",
) -> str:
    system = _system_for_followup(analyses, profile)
    parts = [types.Part.from_text(text=question)]
    return await _call_with_retry(
        system_instruction=system,
        parts=parts,
        max_output_tokens=4096,
    )


async def _stream_with_retry(
    system_instruction: str,
    parts: list[types.Part],
    max_output_tokens: int,
) -> AsyncIterator[str]:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            stream = await _get_client().aio.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=[types.Content(role="user", parts=parts)],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=max_output_tokens,
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                ),
            )
            produced_any = False
            async for chunk in stream:
                text = getattr(chunk, "text", None) or ""
                if text:
                    produced_any = True
                    yield text
            if produced_any:
                return
            logger.warning("Gemini stream returned empty on attempt %s", attempt + 1)
            last_error = GeminiServiceError("empty stream")
        except genai_errors.ClientError as exc:
            logger.warning("Gemini stream client error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
            status = getattr(exc, "code", None)
            if status and status != 429:
                break
        except genai_errors.APIError as exc:
            logger.warning("Gemini stream API error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
        except Exception as exc:
            logger.warning("Gemini stream unexpected error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
        if attempt == 0:
            await asyncio.sleep(1.0)
    raise GeminiServiceError(str(last_error) if last_error else "unknown error")


async def _call_with_retry(
    system_instruction: str,
    parts: list[types.Part],
    max_output_tokens: int,
) -> str:
    last_error: Exception | None = None
    for attempt in range(2):
        try:
            response = await _get_client().aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=[types.Content(role="user", parts=parts)],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=max_output_tokens,
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                ),
            )
            text = (response.text or "").strip()
            if text:
                return text
            logger.warning("Gemini returned empty response on attempt %s", attempt + 1)
            last_error = GeminiServiceError("empty response")
        except genai_errors.ClientError as exc:
            logger.warning("Gemini client error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
            status = getattr(exc, "code", None)
            if status and status != 429:
                break
        except genai_errors.APIError as exc:
            logger.warning("Gemini API error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
        except Exception as exc:
            logger.warning("Gemini unexpected error on attempt %s: %s", attempt + 1, exc)
            last_error = exc
        if attempt == 0:
            await asyncio.sleep(1.0)
    raise GeminiServiceError(str(last_error) if last_error else "unknown error")
