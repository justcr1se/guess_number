import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.config import TELEGRAM_BOT_TOKEN, validate_config
from bot.handlers.analyze import (
    callback_query_handler,
    handle_document,
    handle_photo,
)
from bot.handlers.questions import handle_text_question
from bot.handlers.start import (
    about_command,
    help_command,
    profile_command,
    reset_command,
    start_command,
)

logger = logging.getLogger(__name__)


async def _on_error(update: object, context) -> None:
    logger.exception("Unhandled exception while processing update", exc_info=context.error)


def build_application() -> Application:
    validate_config()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("profile", profile_command))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_question))

    app.add_handler(CallbackQueryHandler(callback_query_handler))

    app.add_error_handler(_on_error)
    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    app = build_application()
    logger.info("Starting bot in polling mode")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
