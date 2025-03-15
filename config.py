import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

GPT_MODEL = "gpt-4o"
# Data sources
SOURCES = [
    "https://coda.io/@latoken/latoken-talent",
    "https://coda.io/@latoken/latoken-talent/jobs-150",
    "https://coda.io/@latoken/latoken-talent/jobs-123",
    "https://coda.io/@latoken/latoken-talent/hr-referral-program-148",  
    "https://coda.io/@latoken/latoken-talent/culture-139",
    "https://coda.io/@latoken/latoken-talent/latoken-161",
    "https://deliver.latoken.com/hackathon"
]

# Directory containing markdown resources
RESOURCES_DIR = "resources"

# Vector DB directory
VECTOR_DB_DIR = "vector_db"

# Create the vector DB directory if it doesn't exist
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# Create the resources directory if it doesn't exist
os.makedirs(RESOURCES_DIR, exist_ok=True)

# Topic definitions for filtering
RELEVANT_TOPICS = [
    "latoken", "hackathon", "culture", "interview", "hiring", "work", "job",
    "application", "company", "values", "team", "wartime", "ceo",
    "sugar cookie", "test", "culture deck", "stress"
]

# Maximum token limit for context
MAX_CONTEXT_TOKENS = 1500

# System prompt for the bot
SYSTEM_PROMPT = """
You are an AI assistant for LATOKEN, answering questions about the company,
its culture, the ongoing hackathon, and the hiring process. Strictly limit
your responses to information about LATOKEN, its Culture Deck, and hackathon.

If asked about unrelated topics, politely explain that you can only provide
information about LATOKEN and redirect the conversation back to relevant
topics.


Always be helpful, concise, and accurate based on the retrieved information.
"""
