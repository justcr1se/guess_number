# Медицинский бот-расшифровщик анализов

Telegram-бот, который помогает понять медицинские анализы простым языком. Принимает PDF или фото бланка, отдаёт структурированную расшифровку с пояснениями, нормами, акцентами и списком вопросов врачу.

> ⚠️ Бот не ставит диагнозы и не заменяет консультацию врача. Это инструмент для понимания, а не для постановки диагноза.

## Возможности

- Расшифровка PDF (текстовых и сканированных) и фото анализов
- Несколько фото подряд собираются в один анализ (бланк на 2–3 страницах)
- Уточняющие вопросы по последнему анализу — контекст хранится в памяти процесса 1 час
- Inline-кнопки: «Вопросы врачу» и «Новый анализ»
- Команды: `/start`, `/help`, `/about`, `/reset`

## Стек

- Python 3.11+
- python-telegram-bot v21 (async, polling)
- anthropic SDK, модель `claude-sonnet-4-5`
- pypdf, pdf2image, Pillow

## Структура проекта

```
bot/
  main.py
  config.py
  prompts.py
  handlers/
    start.py
    analyze.py
    questions.py
  services/
    claude.py
    pdf_processor.py
    session.py
requirements.txt
.env.example
```

## Подготовка токенов

### Telegram-бот

1. Открой Telegram, найди [@BotFather](https://t.me/BotFather)
2. Отправь `/newbot`, придумай имя и username (заканчивается на `bot`)
3. BotFather пришлёт токен вида `123456:ABC-...` — это `TELEGRAM_BOT_TOKEN`

### Ключ Anthropic

1. Зайди в [console.anthropic.com](https://console.anthropic.com)
2. Создай API-ключ в разделе API Keys
3. Сохрани значение в `ANTHROPIC_API_KEY`

## Локальный запуск

Требуется системная утилита `poppler` (нужна `pdf2image`):

- macOS: `brew install poppler`
- Ubuntu/Debian: `sudo apt-get install -y poppler-utils`

Дальше:

```bash
git clone <repo-url>
cd guess_number

python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# открой .env и впиши свои токены

python -m bot.main
```

Когда бот запустится — открой его в Telegram и пришли PDF или фото анализа.

## Деплой на Railway

1. Залогинься на [railway.app](https://railway.app) через GitHub.
2. **New Project → Deploy from GitHub repo**, выбери этот репозиторий.
3. Railway сам определит Python и установит зависимости из `requirements.txt`.
4. В разделе **Variables** добавь:
   - `TELEGRAM_BOT_TOKEN`
   - `ANTHROPIC_API_KEY`
5. В разделе **Settings → Deploy** укажи команду запуска:
   ```
   python -m bot.main
   ```
6. Для `pdf2image` нужен `poppler`. Создай в корне репозитория файл `nixpacks.toml`:
   ```toml
   [phases.setup]
   aptPkgs = ["poppler-utils"]
   ```
   Закоммить и запушь — Railway переустановит окружение с poppler.
7. После деплоя проверь логи: должна быть строка `Starting bot in polling mode`. Открой бота в Telegram и пришли `/start`.

## Деплой на Fly.io / VPS

Аналогично: установи `poppler-utils`, задай переменные окружения, запусти `python -m bot.main` под `systemd` или `tmux`. Бот работает в режиме long polling, входящий порт не нужен.

## Что НЕ хранит бот

- Не сохраняет файлы на диск — всё обрабатывается в памяти.
- Не ведёт базу данных и историю между сессиями.
- В памяти процесса держится только текст последней расшифровки на пользователя, чтобы отвечать на уточняющие вопросы. Сбрасывается через 1 час или по `/reset`.

## Дисклеймер

Бот — образовательный инструмент. Любые решения о лечении, дополнительных исследованиях или приёме препаратов принимает только лечащий врач.
