import asyncio
import logging
from typing import Iterable

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from bot.config import GEMINI_API_KEY, GEMINI_MODEL
from bot.prompts import SYSTEM_PROMPT_ANALYZE, SYSTEM_PROMPT_FOLLOWUP

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


async def analyze_document(text: str | None, images: list[bytes]) -> str:
    parts = _build_parts(text, images)
    return await _call_with_retry(
        system_instruction=SYSTEM_PROMPT_ANALYZE,
        parts=parts,
        max_output_tokens=2000,
    )


async def answer_followup(question: str, last_analysis: str) -> str:
    system = SYSTEM_PROMPT_FOLLOWUP.format(last_analysis=last_analysis)
    parts = [types.Part.from_text(text=question)]
    return await _call_with_retry(
        system_instruction=system,
        parts=parts,
        max_output_tokens=1000,
    )


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
