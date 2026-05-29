from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
import utils.database as db
from knowledge.knowledge_base import KNOWLEDGE_BASE, get_context_for_ai
from ai.gemini_client import get_ai_response
import config

TOPIC_INTROS = {
    "breakup": "💔 Breakup & Heartbreak\n\nTell me what happened. I am here for you.",
    "attraction": "💘 Attraction & Dating\n\nWhat is the situation? Tell me about it.",
    "attachment": "🔗 Attachment Styles\n\nWhat patterns keep showing up in your relationships?",
    "communication": "🗣️ Communication & Conflict\n\nWhat does the disconnect look like?",
    "confidence": "💪 Confidence & Self-Worth\n\nWhat is making you feel stuck or less than you know you are?",
    "power_boundaries": "🏆 Power & Boundaries\n\nWhere are people crossing lines with you?",
    "business_goals": "🚀 Business & Goals\n\nWhat are you building and where are you stuck?",
    "companion": "💙 I am here.\n\nTalk to me. What is on your mind right now?",
}


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user

    # Simple menu buttons
    if data == "ask":
        await query.message.reply_text(
            "Just type what is on your mind. "
            "I will pick up on what you need and respond. 💙"
        )
        return

    if data == "howto":
        await query.message.reply_text(
            "How I work:\n\n"
            "1. You tell me what is happening\n"
            "2. I detect the type of problem\n"
            "3. I pull from deep psychology on that topic\n"
            "4. I respond like a knowledgeable friend\n\n"
            "I also adapt my style based on what you need:\n"
            "Say just listen and I will be your companion\n"
            "Say be real with me and I will be direct\n"
            "Say teach me and I will be your mentor\n\n"
            "Use /clear to reset memory anytime."
        )
        return

    if data == "topics":
        keyboard = [
            [InlineKeyboardButton("💔 Breakup", callback_data="topic_breakup"),
             InlineKeyboardButton("💘 Attraction", callback_data="topic_attraction")],
            [InlineKeyboardButton("🔗 Attachment", callback_data="topic_attachment"),
             InlineKeyboardButton("🗣️ Communication", callback_data="topic_communication")],
            [InlineKeyboardButton("💪 Confidence", callback_data="topic_confidence"),
             InlineKeyboardButton("🏆 Boundaries", callback_data="topic_power_boundaries")],
            [InlineKeyboardButton("🚀 Business", callback_data="topic_business_goals"),
             InlineKeyboardButton("💙 Just Talk", callback_data="topic_companion")],
        ]
        await query.message.reply_text(
            "What do you need help with?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "premium":
        keyboard = [[
            InlineKeyboardButton(
                "Contact to Upgrade", url="https://t.me/YourUsername"
            )
        ]]
        await query.message.reply_text(
            f"Premium: ${config.PREMIUM_PRICE_USD} per month\n\n"
            "Unlimited messages\n"
            "Deeper responses\n"
            "Full memory\n"
            "Priority features\n\n"
            "Contact to upgrade:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Topic selection
    if data.startswith("topic_"):
        category = data.replace("topic_", "")
        intro = TOPIC_INTROS.get(category, "Tell me what is on your mind. 💙")
        await query.message.reply_text(intro)
        return

    # Insight buttons
    if "_" in data:
        parts = data.split("_", 1)
        action = parts[0]
        category = parts[1] if len(parts) > 1 else "companion"

        if category not in KNOWLEDGE_BASE:
            await query.message.reply_text(
                "Please send a new message and I will help you. 💙"
            )
            return

        node = KNOWLEDGE_BASE[category]

        if action == "insights":
            bullets = "\n".join(f"• {p}" for p in node["principles"])
            await query.message.reply_text(
                f"Key Insights — {node['topic']}\n\n{bullets}"
            )

        elif action == "redflags":
            bullets = "\n".join(f"🚩 {r}" for r in node["red_flags"])
            await query.message.reply_text(
                f"Warning Signs — {node['topic']}\n\n{bullets}"
            )

        elif action == "actions":
            bullets = "\n".join(f"✅ {a}" for a in node["action_steps"])
            await query.message.reply_text(
                f"Action Steps — {node['topic']}\n\n{bullets}"
            )

        elif action == "deeper":
            await query.message.chat.send_action(ChatAction.TYPING)
            history = db.get_history(user.id, limit=8)
            system_context = get_context_for_ai(category, "mentor")
            response = get_ai_response(
                "Go deeper on this. What are the underlying psychological "
                "dynamics most people miss about this situation?",
                system_context,
                history
            )
            await query.message.reply_text(response)
            db.save_message(user.id, "assistant", response, category)
