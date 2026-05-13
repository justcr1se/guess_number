import asyncio
import logging
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from bot.config import (
    MAX_FILE_SIZE_BYTES,
    MAX_FILE_SIZE_MB,
    MAX_PAGES_PER_ANALYSIS,
    MAX_TELEGRAM_MESSAGE_LENGTH,
    PHOTO_GROUP_WAIT_SECONDS,
)
from bot.prompts import DISCLAIMER_SHORT, FOLLOWUP_HINT
from bot.services.gemini import GeminiServiceError, analyze_document
from bot.services.pdf_processor import normalize_image_bytes, process_pdf
from bot.services.session import session_store

logger = logging.getLogger(__name__)


SUPPORTED_IMAGE_MIME = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
PHOTO_BUFFER_KEY = "photo_buffer"
PHOTO_TASK_KEY = "photo_flush_task"


def _build_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📋 Вопросы врачу", callback_data="copy_questions")],
            [InlineKeyboardButton("🆕 Новый анализ", callback_data="new_analysis")],
        ]
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    if document is None:
        return

    mime = (document.mime_type or "").lower()
    file_name = (document.file_name or "").lower()

    is_pdf = mime == "application/pdf" or file_name.endswith(".pdf")
    is_image = mime in SUPPORTED_IMAGE_MIME or file_name.endswith((".jpg", ".jpeg", ".png", ".webp"))

    if not (is_pdf or is_image):
        await update.message.reply_text("Пришли PDF или фото анализа 🙂")
        return

    if document.file_size and document.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(
            f"Файл слишком большой, максимум {MAX_FILE_SIZE_MB} МБ."
        )
        return

    await _send_typing(update, context)
    progress_message = await update.message.reply_text("Читаю документ…")

    try:
        tg_file = await document.get_file()
        data = bytes(await tg_file.download_as_bytearray())
    except Exception as exc:
        logger.exception("Failed to download document: %s", exc)
        await progress_message.edit_text("Не удалось скачать файл, попробуй ещё раз.")
        return

    if len(data) > MAX_FILE_SIZE_BYTES:
        await progress_message.edit_text(
            f"Файл слишком большой, максимум {MAX_FILE_SIZE_MB} МБ."
        )
        return

    try:
        if is_pdf:
            extracted = await asyncio.to_thread(process_pdf, data)
            text, images = extracted.text, extracted.images
        else:
            image_bytes = await asyncio.to_thread(normalize_image_bytes, data)
            text, images = None, [image_bytes]
    except Exception as exc:
        logger.exception("Failed to process file: %s", exc)
        await progress_message.edit_text(
            "Не получилось прочитать файл. Проверь, что это PDF или фото анализа."
        )
        return

    await _run_analysis(update, context, progress_message, text=text, images=images)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo_sizes = update.message.photo
    if not photo_sizes:
        return

    largest = photo_sizes[-1]
    if largest.file_size and largest.file_size > MAX_FILE_SIZE_BYTES:
        await update.message.reply_text(
            f"Файл слишком большой, максимум {MAX_FILE_SIZE_MB} МБ."
        )
        return

    try:
        tg_file = await largest.get_file()
        raw = bytes(await tg_file.download_as_bytearray())
        image_bytes = await asyncio.to_thread(normalize_image_bytes, raw)
    except Exception as exc:
        logger.exception("Failed to download photo: %s", exc)
        await update.message.reply_text("Не удалось скачать фото, попробуй ещё раз.")
        return

    buffer: list[bytes] = context.user_data.setdefault(PHOTO_BUFFER_KEY, [])
    buffer.append(image_bytes)

    if len(buffer) > MAX_PAGES_PER_ANALYSIS:
        buffer[:] = buffer[-MAX_PAGES_PER_ANALYSIS:]

    pending_task: asyncio.Task | None = context.user_data.get(PHOTO_TASK_KEY)
    if pending_task and not pending_task.done():
        pending_task.cancel()

    context.user_data[PHOTO_TASK_KEY] = asyncio.create_task(
        _flush_photo_buffer_after_delay(update, context)
    )


async def _flush_photo_buffer_after_delay(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    try:
        await asyncio.sleep(PHOTO_GROUP_WAIT_SECONDS)
    except asyncio.CancelledError:
        return

    buffer: list[bytes] = context.user_data.get(PHOTO_BUFFER_KEY, [])
    if not buffer:
        return
    images = list(buffer)
    buffer.clear()
    context.user_data[PHOTO_TASK_KEY] = None

    await _send_typing(update, context)
    progress_message = await update.message.reply_text("Читаю документ…")
    await _run_analysis(update, context, progress_message, text=None, images=images)


async def _run_analysis(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    progress_message,
    text: str | None,
    images: list[bytes],
) -> None:
    user_id = update.effective_user.id
    try:
        answer = await analyze_document(text=text, images=images)
    except GeminiServiceError as exc:
        logger.warning("Gemini service error: %s", exc)
        await progress_message.edit_text(
            "Сервис временно недоступен, попробуй через минуту."
        )
        return
    except Exception as exc:
        logger.exception("Unexpected error during analysis: %s", exc)
        await progress_message.edit_text(
            "Что-то пошло не так. Попробуй прислать файл ещё раз."
        )
        return
    finally:
        del text, images

    questions_block = _extract_questions_block(answer)
    session_store.set(user_id, last_analysis=answer, questions_block=questions_block)

    full_text = f"{answer}\n\n{DISCLAIMER_SHORT}{FOLLOWUP_HINT}"
    chunks = _split_for_telegram(full_text)

    await _send_chunks(progress_message, chunks)


async def _send_chunks(progress_message, chunks: list[str]) -> None:
    keyboard = _build_keyboard()
    last_index = len(chunks) - 1
    for idx, chunk in enumerate(chunks):
        markup = keyboard if idx == last_index else None
        is_first = idx == 0
        try:
            if is_first:
                await progress_message.edit_text(
                    chunk, parse_mode=ParseMode.HTML, reply_markup=markup
                )
            else:
                await progress_message.reply_text(
                    chunk, parse_mode=ParseMode.HTML, reply_markup=markup
                )
        except Exception as exc:
            logger.warning("Failed to send formatted chunk, falling back to plain: %s", exc)
            plain = _strip_html_tags(chunk)
            if is_first:
                await progress_message.edit_text(plain, reply_markup=markup)
            else:
                await progress_message.reply_text(plain, reply_markup=markup)


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "new_analysis":
        session_store.clear(user_id)
        await query.message.reply_text("Жду новый анализ — пришли PDF или фото 🙂")
        return

    if query.data == "copy_questions":
        session = session_store.get(user_id)
        if not session or not session.questions_block:
            await query.message.reply_text(
                "Сначала пришли анализ — потом я подготовлю список вопросов врачу."
            )
            return
        text = (
            "Вопросы врачу (скопируй и перешли):\n\n"
            f"{session.questions_block}"
        )
        await query.message.reply_text(text)


async def _send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
    except Exception as exc:
        logger.debug("Failed to send typing action: %s", exc)


def _extract_questions_block(answer: str) -> str:
    match = re.search(r"❓[^\n]*\n(.+?)(?:\n\s*\n|\Z)", answer, re.DOTALL)
    if not match:
        return ""
    block = match.group(1).strip()
    return _strip_html_tags(block)


def _strip_html_tags(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return (
        text.replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&amp;", "&")
    )


def _split_for_telegram(text: str, limit: int = MAX_TELEGRAM_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        slice_ = remaining[:limit]
        split_at = slice_.rfind("\n\n")
        if split_at < limit // 2:
            split_at = slice_.rfind("\n")
        if split_at < limit // 2:
            split_at = slice_.rfind(" ")
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining:
        chunks.append(remaining)
    return chunks
