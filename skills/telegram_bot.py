# -*- coding: utf-8 -*-
import logging
import pytz
import apscheduler.schedulers.base as _apsched_base

_orig_astimezone = _apsched_base.astimezone
def _patched_astimezone(obj):
    if obj is not None and not hasattr(obj, 'localize'):
        return pytz.utc
    return _orig_astimezone(obj)
_apsched_base.astimezone = _patched_astimezone

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_TOKEN, TELEGRAM_ALLOWED_IDS, ZABIS_NAME
from core.brain import think

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.WARNING,
)

# 빠른 육아 액션 버튼 레이아웃
_QUICK_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🍼 수유 기록",    callback_data="quick:수유"),
        InlineKeyboardButton("🧷 기저귀 교체",  callback_data="quick:기저귀 갈았어"),
    ],
    [
        InlineKeyboardButton("😴 수면 시작",    callback_data="quick:잠들었어"),
        InlineKeyboardButton("☀️ 기상",         callback_data="quick:일어났어"),
    ],
    [
        InlineKeyboardButton("📋 오늘 요약",    callback_data="quick:오늘 육아 요약"),
        InlineKeyboardButton("💉 예방접종 일정", callback_data="quick:예방접종 일정"),
    ],
    [
        InlineKeyboardButton("🌱 발달 단계",    callback_data="quick:발달 단계"),
        InlineKeyboardButton("🍼 마지막 수유",   callback_data="quick:마지막 수유"),
    ],
])

_START_MESSAGE = (
    f"👶 {ZABIS_NAME} 육아 비서입니다.\n\n"
    "아래 버튼으로 빠르게 기록하거나, 텍스트로 자유롭게 물어보세요.\n\n"
    "📌 주요 명령어:\n"
    "  아기 등록 [이름] [YYYY-MM-DD]\n"
    "  수유 / 수유 120ml\n"
    "  기저귀 갈았어 / 기저귀 갈았어 대변\n"
    "  잠들었어 / 일어났어\n"
    "  키 75cm 몸무게 9.5kg\n"
    "  마지막 수유\n"
    "  오늘 육아 요약\n"
    "  예방접종 일정\n"
    "  발달 단계\n\n"
    "🔧 기타 명령:\n"
    "  /clear — 대화 기록 초기화\n"
    "  /id    — 내 텔레그램 ID 확인\n"
    "  /quick — 빠른 버튼 패널 열기"
)


def _is_allowed(user_id: int) -> bool:
    if not TELEGRAM_ALLOWED_IDS:
        return True
    return user_id in TELEGRAM_ALLOWED_IDS


async def _send_long(update: Update, text: str):
    """4096자 초과 시 분할 전송."""
    for i in range(0, len(text), 4096):
        await update.effective_message.reply_text(text[i:i + 4096])


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return
    await update.message.reply_text(_START_MESSAGE, reply_markup=_QUICK_KEYBOARD)


async def cmd_quick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        return
    await update.message.reply_text("빠른 육아 기록:", reply_markup=_QUICK_KEYBOARD)


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        return
    from core.memory import clear_history
    clear_history()
    await update.message.reply_text("✅ 대화 기록을 초기화했습니다.")


async def cmd_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"내 텔레그램 ID: `{update.effective_user.id}`", parse_mode="Markdown"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_allowed(update.effective_user.id):
        await update.message.reply_text("접근 권한이 없습니다.")
        return

    user_text = update.message.text
    await update.message.chat.send_action("typing")

    try:
        reply = await asyncio.to_thread(think, user_text)
    except Exception as e:
        reply = f"⚠️ 오류가 발생했습니다: {e}"

    await _send_long(update, reply)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """인라인 버튼 콜백 처리."""
    query = update.callback_query
    await query.answer()

    if not _is_allowed(query.from_user.id):
        await query.message.reply_text("접근 권한이 없습니다.")
        return

    if query.data.startswith("quick:"):
        command_text = query.data[len("quick:"):]
        await query.message.chat.send_action("typing")
        try:
            reply = await asyncio.to_thread(think, command_text)
        except Exception as e:
            reply = f"⚠️ 오류가 발생했습니다: {e}"

        await _send_long(update, reply)
        # 버튼 패널 다시 표시
        await query.message.reply_text("빠른 육아 기록:", reply_markup=_QUICK_KEYBOARD)


def run_telegram_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError(".env 파일에 TELEGRAM_TOKEN이 설정되지 않았습니다.")

    app = Application.builder().token(TELEGRAM_TOKEN).job_queue(None).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("quick", cmd_quick))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("id", cmd_id))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print(f"텔레그램 봇 시작됨. {ZABIS_NAME}가 메시지를 기다립니다...")
    app.run_polling(drop_pending_updates=True)
