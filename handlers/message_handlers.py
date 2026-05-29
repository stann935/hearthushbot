from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import utils.database as db
from knowledge.knowledge_base import classify_problem, get_context_for_ai, detect_companion_mode
from knowledge.book_reader import enrich_context_with_books
from ai.gemini_client import get_ai_response, check_for_crisis, CRISIS_RESPONSE
import config


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text.strip()

    if not message:
        return

    # Register user
    db.upsert_user(user.id, user.username or "", user.first_name or "")

    # Crisis check — always runs first
    if check_for_crisis(message):
        await update.message.reply_text(CRISIS_RESPONSE)
        db.save_message(user.id, "user", message, "crisis")
        db.save_message(user.id, "assistant", CRISIS_RESPONSE, "crisis")
        return

    # Usage limit check
    if not db.is_within_limit(user.id):
        usage = db.get_daily_usage(user.id)
        keyboard = [[
            InlineKeyboardButton(
                "⭐ Upgrade to Premium", callback_data="premium"
            )
        ]]
        await update.message.reply_text(
            f"💙 You have used your {config.FREE_DAILY_LIMIT} free messages today.\n\n"
            "Upgrade to Premium for unlimited access — or come back tomorrow.\n\n"
            f"Today: {usage}/{config.FREE_DAILY_LIMIT} messages used.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Show typing indicator
    await update.message.chat.send_action(ChatAction.TYPING)

    # Classify problem and detect mode
    category = classify_problem(message)
    mode = detect_companion_mode(message)

    # Save user message
    db.save_message(user.id, "user", message, category)
    db.increment_usage(user.id)

    # Get conversation history
    history = db.get_history(user.id, limit=config.MAX_CONTEXT_MESSAGES * 2)

    # Build AI context
    system_context = get_context_for_ai(category, mode)
    system_context = enrich_context_with_books(category, system_context)

    # Get AI response
    response = get_ai_response(message, system_context, history)

    # Save assistant response and lead
    db.save_message(user.id, "assistant", response, category)
    db.save_lead(user.id, category, message[:200])

    # Build response buttons
    keyboard = [
        [
            InlineKeyboardButton("🔄 Go Deeper", callback_data=f"deeper_{category}"),
            InlineKeyboardButton("💡 Key Insights", callback_data=f"insights_{category}"),
        ],
        [
            InlineKeyboardButton("🚩 Warning Signs", callback_data=f"redflags_{category}"),
            InlineKeyboardButton("✅ Action Steps", callback_data=f"actions_{category}"),
        ],
    ]

    # Show premium upsell when getting close to limit
    usage = db.get_daily_usage(user.id)
    if not db.is_premium(user.id) and usage >= config.FREE_DAILY_LIMIT - 10:
        keyboard.append([
            InlineKeyboardButton(
                f"⭐ {config.FREE_DAILY_LIMIT - usage} messages left — Go Premium",
                callback_data="premium"
            )
        ])

    await update.message.reply_text(
        response,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
