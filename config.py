import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

FREE_DAILY_LIMIT = 100
PREMIUM_PRICE_USD = 9.99
MAX_CONTEXT_MESSAGES = 8
GEMINI_MODEL = "gemini-2.5-flash"
DB_PATH = "data/bot.db"

ENABLE_REDDIT_FEED = False
ENABLE_PREMIUM = True
DEBUG = False
