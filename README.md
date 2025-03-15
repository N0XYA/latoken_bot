# LATOKEN Assistant Telegram Bot

A Telegram bot that uses Retrieval-Augmented Generation (RAG) to answer questions about LATOKEN company, its culture, and ongoing hackathon.

## Features

- Answers questions about LATOKEN company
- Provides information about LATOKEN Culture Deck
- Gives details about the ongoing hackathon
- Responds in the user's language
- Tests users' knowledge with follow-up questions

## Sources

The bot uses the following sources for its knowledge base:
- https://coda.io/@latoken/latoken-talent/culture-139
- https://coda.io/@latoken/latoken-talent/latoken-161
- https://deliver.latoken.com/hackathon

## Requirements

- Python 3.8+
- Telegram bot token (from @BotFather)
- OpenAI API key

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd latoken_bot
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

## Usage

1. Run the bot:
```bash
python main.py
```

2. Open Telegram and find your bot (by the username you registered with @BotFather)

3. Start a conversation with the bot by sending the `/start` command

4. Ask questions about LATOKEN, its culture, or the hackathon

## Commands

- `/start` - Start the conversation
- `/help` - Show help information
- `/reset` - Reset conversation history

## Project Structure

- `main.py` - Entry point for the application
- `bot.py` - Main Telegram bot functionality
- `config.py` - Configuration and settings
- `knowledge_base.py` - RAG implementation using FAISS
- `scraper.py` - Web scraping functionality to fetch content
- `language_utils.py` - Language detection and translation

## Example Questions

- "Why does LATOKEN help people study and buy assets?"
- "What is the Sugar Cookie test for?"
- "Why is a Wartime CEO needed?"
- "When is stress useful and when is it harmful?"

## License

MIT 