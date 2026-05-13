import logging

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from bot.prompts import DISCLAIMER_SHORT
from bot.services.gemini import GeminiServiceError, answer_followup
from bot.services.session import session_store

logger = logging.getLogger(__name__)


async def handle_text_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if message is None or not message.text:
        return

    user_id = update.effective_user.id
    session = session_store.get(user_id)
    if session is None:
        await message.reply_text(
            "Пока нечего обсуждать 🙂 Пришли PDF или фото анализа — потом можно будет задать уточняющий вопрос."
        )
        return

    try:
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action=ChatAction.TYPING
        )
    except Exception:
        pass

    try:
        answer = await answer_followup(message.text, session.last_analysis)
    except GeminiServiceError as exc:
        logger.warning("Gemini service error during follow-up: %s", exc)
        await message.reply_text("Сервис временно недоступен, попробуй через минуту.")
        return
    except Exception as exc:
        logger.exception("Unexpected error in follow-up: %s", exc)
        await message.reply_text("Что-то пошло не так, попробуй задать вопрос ещё раз.")
        return

    full_text = f"{answer}\n\n{DISCLAIMER_SHORT}"
    try:
        await message.reply_text(full_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as exc:
        logger.warning("Failed to send markdown follow-up, falling back to plain: %s", exc)
        await message.reply_text(full_text)
