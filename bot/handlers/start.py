import html
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.prompts import ABOUT_MESSAGE, HELP_MESSAGE, WELCOME_MESSAGE
from bot.services.session import session_store

logger = logging.getLogger(__name__)

MAX_PROFILE_LENGTH = 500


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE, parse_mode=ParseMode.HTML)


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(ABOUT_MESSAGE, parse_mode=ParseMode.HTML)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session_store.clear_analyses(user_id)
    await update.message.reply_text(
        "Готово, забыл предыдущие анализы. Профиль пациента сохранён (сбросить — /profile clear)."
    )


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    args_text = " ".join(context.args).strip() if context.args else ""

    if not args_text:
        session = session_store.get(user_id)
        current = session.profile if session and session.profile else ""
        if current:
            await update.message.reply_text(
                f"<b>Текущий профиль:</b>\n{html.escape(current)}\n\n"
                "Изменить: <code>/profile женщина, 32, гипотиреоз</code>\n"
                "Сбросить: <code>/profile clear</code>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.message.reply_text(
                "<b>Профиль пациента не задан.</b>\n\n"
                "Зачем нужен: я буду учитывать пол, возраст и известные диагнозы при интерпретации анализов.\n\n"
                "Задать: <code>/profile женщина, 32, гипотиреоз, принимаю L-тироксин</code>\n"
                "Произвольный текст до 500 символов. Хранится в памяти сессии, не сохраняется надолго.",
                parse_mode=ParseMode.HTML,
            )
        return

    if args_text.lower() in {"clear", "сброс", "сбросить", "очистить", "off"}:
        session_store.set_profile(user_id, "")
        await update.message.reply_text("Профиль сброшен.")
        return

    if len(args_text) > MAX_PROFILE_LENGTH:
        await update.message.reply_text(
            f"Слишком длинный профиль, максимум {MAX_PROFILE_LENGTH} символов."
        )
        return

    session_store.set_profile(user_id, args_text)
    await update.message.reply_text(
        f"Профиль сохранён:\n{html.escape(args_text)}",
        parse_mode=ParseMode.HTML,
    )
