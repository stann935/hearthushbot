from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import utils.database as db
import config

ADMIN_IDS = [8412193549]  # Replace with your Telegram ID


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.upsert_user(user.id, user.username or "", user.first_name or "")

    keyboard = [
        [
            InlineKeyboardButton("💬 Ask Anything", callback_data="ask"),
            InlineKeyboardButton("📚 Topics", callback_data="topics"),
        ],
        [
            InlineKeyboardButton("⭐ Go Premium", callback_data="premium"),
            InlineKeyboardButton("ℹ️ How It Works", callback_data="howto"),
        ],
    ]

    welcome = (
        f"Hey {user.first_name} 👋\n\n"
        "I am your personal relationship and life coach — "
        "powered by deep psychology and emotional intelligence.\n\n"
        "I can help you with:\n"
        "💔 Heartbreak and breakups\n"
        "💘 Attraction and dating\n"
        "🔗 Relationship patterns\n"
        "🗣️ Communication and conflict\n"
        "💪 Confidence and self-worth\n"
        "🏆 Boundaries and personal power\n"
        "🚀 Business mindset and goals\n"
        "💙 Just someone to talk to\n\n"
        "Just talk to me like a friend. No judgment.\n\n"
        f"Free plan: {config.FREE_DAILY_LIMIT} messages per day."
    )

    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "How to use me:\n\n"
        "Just type whatever is on your mind — a situation, "
        "a question, or how you are feeling.\n\n"
        "I will detect what you need and respond accordingly.\n\n"
        "Commands:\n"
        "/start — Welcome and main menu\n"
        "/menu — Show all topics\n"
        "/premium — Unlock unlimited access\n"
        "/clear — Clear conversation memory\n"
        "/stats — Bot statistics\n\n"
        "Example messages:\n"
        "My ex just texted me after 2 months\n"
        "I keep attracting emotionally unavailable people\n"
        "How do I stop people pleasing\n"
        "I just need someone to talk to\n"
        "Be real with me about my situation"
    )
    await update.message.reply_text(text)


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💔 Breakup & Heartbreak", callback_data="topic_breakup")],
        [InlineKeyboardButton("💘 Attraction & Dating", callback_data="topic_attraction")],
        [InlineKeyboardButton("🔗 Attachment Styles", callback_data="topic_attachment")],
        [InlineKeyboardButton("🗣️ Communication & Conflict", callback_data="topic_communication")],
        [InlineKeyboardButton("💪 Confidence & Self-Worth", callback_data="topic_confidence")],
        [InlineKeyboardButton("🏆 Power & Boundaries", callback_data="topic_power_boundaries")],
        [InlineKeyboardButton("🚀 Business & Goals", callback_data="topic_business_goals")],
        [InlineKeyboardButton("💙 Just Talk", callback_data="topic_companion")],
        [InlineKeyboardButton("⭐ Go Premium", callback_data="premium")],
    ]
    await update.message.reply_text(
        "What do you need help with today?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if db.is_premium(user.id):
        await update.message.reply_text(
            "You are already Premium. Enjoy unlimited access. 🌟"
        )
        return

    keyboard = [[
        InlineKeyboardButton(
            "Contact to Upgrade", url="https://t.me/christallman"
        )
    ]]
    await update.message.reply_text(
        f"Upgrade to Premium\n\n"
        f"Free plan: {config.FREE_DAILY_LIMIT} messages per day\n"
        "Premium: Unlimited messages\n\n"
        "Premium benefits:\n"
        "Unlimited daily messages\n"
        "Deeper and longer responses\n"
        "Full conversation memory\n"
        "Priority access to new features\n\n"
        f"Price: ${config.PREMIUM_PRICE_USD} per month\n\n"
        "Contact to upgrade:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Admin only.")
        return

    s = db.get_stats()
    await update.message.reply_text(
        f"Bot Statistics\n\n"
        f"Total users: {s['total_users']}\n"
        f"Premium users: {s['premium_users']}\n"
        f"Total messages: {s['total_messages']}\n"
        f"Active today: {s['active_today']}"
    )

async def addpremium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("Admin only.")
        return

    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: /addpremium USER_ID\n"
            "Example: /addpremium 123456789"
        )
        return

    try:
        target_id = int(args[0])
        conn = db.get_connection()
        conn.execute(
            "UPDATE users SET is_premium = 1 WHERE user_id = ?",
            (target_id,)
        )
        conn.commit()
        conn.close()
        await update.message.reply_text(
            f"Premium activated for user {target_id}"
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
async def clear_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.clear_history(update.effective_user.id)
    await update.message.reply_text(
        "Conversation memory cleared. Fresh start. 💙"
    )

