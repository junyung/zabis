# -*- coding: utf-8 -*-
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_TOKEN, TELEGRAM_ALLOWED_IDS, ZABIS_NAME
from core.brain import think

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)


def _is_allowed(user_id: int) -> bool:
    if not TELEGRAM_ALLOWED_IDS:
        return True
    return user_id in TELEGRAM_ALLOWED_IDS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not _is_allowed(user_id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    await update.message.reply_text(
        f"{ZABIS_NAME}입니다. 무엇을 도와드릴까요?\n"
        f"/clear — 대화 기록 초기화\n"
        f"/id — 내 텔레그램 ID 확인"
    )


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        return
    from core.memory import clear_history
    clear_history()
    await update.message.reply_text("대화 기록을 초기화했습니다.")


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"내 ID: `{update.effective_user.id}`", parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return

    user_text = update.message.text
    await update.message.chat.send_action("typing")

    try:
        reply = think(user_text)
    except Exception as e:
        reply = f"오류가 발생했습니다: {e}"

    # 텔레그램 메시지 길이 제한 4096자
    if len(reply) > 4096:
        for i in range(0, len(reply), 4096):
            await update.message.reply_text(reply[i:i+4096])
    else:
        await update.message.reply_text(reply)


def run_telegram_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError(".env 파일에 TELEGRAM_TOKEN이 설정되지 않았습니다.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"텔레그램 봇 시작됨. {ZABIS_NAME}가 메시지를 기다립니다...")
    app.run_polling(drop_pending_updates=True)
