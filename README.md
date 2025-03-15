# LATOKEN Assistant Telegram Bot

A Telegram bot that uses Retrieval-Augmented Generation (RAG) to answer questions about LATOKEN company, its culture, and ongoing hackathon. The bot can detect user language and provide responses in the same language, primarily supporting Russian and English.

## Project Overview

This bot serves as an AI assistant that:
- Provides accurate information about LATOKEN company and its operations
- Explains the LATOKEN Culture Deck and company values
- Offers details about ongoing hackathons and events
- Uses advanced RAG technology to retrieve relevant information from source documents
- Supports multilingual interactions with automatic language detection
- Maintains conversation context for natural dialogue flow
- Can test users' knowledge with follow-up questions

## Architecture

The bot leverages several technologies and components:
- **Telegram Bot API**: For user interaction through the Telegram messaging platform
- **OpenAI GPT Models**: For natural language understanding and response generation
- **FAISS Vector Database**: For efficient similarity search of embedded documents
- **LangChain**: For RAG implementation and document processing
- **Web Scraping**: To automatically gather information from specified sources

## Information Sources

The bot's knowledge base is built from these sources:
- [LATOKEN Culture Deck](https://coda.io/@latoken/latoken-talent/culture-139)
- [LATOKEN Company Information](https://coda.io/@latoken/latoken-talent/latoken-161)
- [LATOKEN Hackathon Details](https://deliver.latoken.com/hackathon)

## Technical Implementation

- `main.py`: Entry point that initializes the bot and checks environment variables
- `bot.py`: Core bot functionality including message handling and response generation
- `knowledge_base.py`: Implementation of the RAG system using FAISS for vector search
- `scraper.py`: Web scraping utilities to fetch and update information from sources
- `language_utils.py`: Language detection and translation services
- `generate_markdowns.py`: Processes source data into markdown files
- `config.py`: Configuration settings and environment variable management

## Requirements

- Python 3.8+
- Telegram bot token (from @BotFather)
- OpenAI API key
- Dependencies listed in `requirements.txt`

## Installation and Setup

1. Clone this repository:
```bash
git clone https://github.com/N0XYA/latoken_bot.git
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
   - Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

## Usage

1. Start the bot:
```bash
python main.py
```

2. Open Telegram and find your bot by the username registered with @BotFather

3. Start a conversation with `/start` command

4. Ask questions about LATOKEN, its culture, or hackathons

## Available Commands

- `/start` - Begin conversation with the bot
- `/help` - Display available commands and usage information
- `/reset` - Clear conversation history and start fresh

## Docker Support

The project includes Docker support for containerized deployment:

```bash
# Build the Docker image
docker build -t latoken-bot .

# Run the container
docker run -d --env-file .env --name latoken-bot-instance latoken-bot
```

## Example Questions

- "What are LATOKEN's core values?"
- "Tell me about the Sugar Cookie test"
- "What qualities does LATOKEN look for in employees?"
- "How does LATOKEN approach leadership?"
- "What is the current hackathon about?"
- "Explain the concept of a Wartime CEO"

## License

MIT 