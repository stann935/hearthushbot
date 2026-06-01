import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

FREE_DAILY_LIMIT = 100
PREMIUM_PRICE_USD = 9.99
MAX_CONTEXT_MESSAGES = 8
GROQ_MODEL = "llama-3.3-70b-versatile"
DB_PATH = "data/bot.db"

ENABLE_REDDIT_FEED = False
ENABLE_PREMIUM = True
DEBUG = False
