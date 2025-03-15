import logging
import random
from typing import Dict, List
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackContext
)
from langchain_openai import ChatOpenAI
from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, SYSTEM_PROMPT, GPT_MODEL
from knowledge_base import initialize_knowledge_base
from language_utils import detect_language, translate_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global knowledge base
knowledge_base = None

# User state for conversation history
user_states = {}


class UserState:
    """Class to store user-specific state information"""
    def __init__(self):
        self.chat_history = []  # Store conversation history
        self.language = 'ru'    # Default language is Russian
        self.last_answer = ""   # Store the last answer for follow-up questions
        self.message_count = 0  # Track number of messages for follow-up logic
        self.gpt_answers = []   # Store GPT answers for summarization


def format_context(docs: List[str], metadata: List[Dict]) -> str:
    """Format retrieved documents into context for the LLM"""
    context = ""
    for i, (doc, meta) in enumerate(zip(docs, metadata)):
        if meta["source"] == "filter":
            return ""  # If filtered (irrelevant question), return empty context

        # Add source information and document content
        source_name = meta["source"].split("/")[-1]
        context += f"\nINFORMATION {i+1} (Source: {source_name}):\n{doc}\n"

    return context


async def generate_response(
    question: str,
    context: str,
    language: str,
    user_state: UserState
) -> str:
    """Generate a response using the OpenAI API"""
    try:
        # Initialize the language model
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=GPT_MODEL,  # Use a model with large context window
            temperature=0.2
        )

        # Define system message with context
        system_message = SYSTEM_PROMPT
        if context:
            system_prefix = "\n\nBelow is the retrieved information about LATOKEN:\n"
            system_message += system_prefix + context

        history = user_state.chat_history[-3:] if user_state.chat_history else []

        # Define follow-up questions
        follow_up_questions = [
            "Вы проверили Culture Deck от LATOKEN?",
            "Вы просмотрели информацию о компании LATOKEN?",
            "Вы смотрели детали хакатона от LATOKEN?",
            "Была ли эта информация полезной для вас?",
            "Вы знакомы с сервисами LATOKEN?",
            "Хотите узнать больше о процессе собеседования?",
            "У вас есть другие вопросы о LATOKEN?"
        ]

        # Create messages array
        messages = [{"role": "system", "content": system_message}]

        # Add conversation history to provide context
        for entry in history:
            messages.append({"role": "user", "content": entry["user"]})
            if "assistant" in entry:
                asst_msg = {"role": "assistant", "content": entry["assistant"]}
                messages.append(asst_msg)

        # Add the current question
        messages.append({"role": "user", "content": question})

        # Get response from LLM
        response = llm.invoke(messages)
        answer = response.content

        # Store the answer for summarization
        user_state.gpt_answers.append(answer)

        # Increment message count in user state
        user_state.message_count += 1

        # Check if we should generate a summary (every 3rd answer)
        if len(user_state.gpt_answers) >= 3 and len(user_state.gpt_answers) % 3 == 0:
            # Generate a summary and understanding check questions using GPT
            prompt = (
                "Based on the following 3 recent answers from a bot about LATOKEN, "
                "I need you to: \n"
                "1. Briefly summarize the main topics and concepts discussed\n"
                "2. Create 2-3 specific questions that would test if the user actually "
                "understood the key concepts from these answers (not just yes/no questions)\n\n"
                "Format your response like this:\n"
                "SUMMARY: [brief summary of the key topics]\n\n"
                "UNDERSTANDING CHECK:\n"
                "1. [first specific question about a concept covered in the answers]\n"
                "2. [second specific question about another concept covered]\n"
                "3. [optional third question if there were multiple important topics]\n\n"
                "Please provide the UNDERSTANDING CHECK section in Russian. "
                "Here are the recent answers:\n\n"
            )

            # Include the last 3 answers in the prompt
            for i, ans in enumerate(user_state.gpt_answers[-3:]):
                prompt += f"Answer {i+1}: {ans}\n\n"

            understanding_messages = [
                {"role": "system", "content": "You are an educational assessment specialist who evaluates comprehension. Always respond in Russian language."},
                {"role": "user", "content": prompt}
            ]

            check_response = llm.invoke(understanding_messages)
            understanding_check = check_response.content

            # Extract only the UNDERSTANDING CHECK part
            if "UNDERSTANDING CHECK" in understanding_check:
                parts = understanding_check.split("UNDERSTANDING CHECK")
                understanding_check = "ПРОВЕРКА ПОНИМАНИЯ" + parts[1]

            # Always translate to the user's language first
            if language != 'ru':
                understanding_check = translate_response(understanding_check, language)

            complete_answer = f"{answer}\n\n{understanding_check}"

        # Otherwise decide whether to add a standard follow-up question (every 3rd message)
        elif user_state.message_count % 3 == 0:
            # Simply choose a random follow-up question
            follow_up = random.choice(follow_up_questions)

            # Translate follow-up question if needed
            if language != 'ru':
                follow_up = translate_response(follow_up, language)

            complete_answer = f"{answer}\n\n{follow_up}"
        else:
            complete_answer = answer

        # Translate response if needed
        if language != 'ru' and complete_answer == answer:
            # Only translate if not already translated with follow-up
            complete_answer = translate_response(complete_answer, language)

        # Update user state
        user_state.last_answer = answer

        return complete_answer

    except Exception as e:
        logger.error(f"Error generating response: {e}")

        # Return error message in the appropriate language
        error_msg = "I'm sorry, I encountered an error while processing your request. Please try again later."
        if language != 'ru':
            error_msg = translate_response(error_msg, language)

        return error_msg


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the command /start is issued"""
    user_id = update.effective_user.id

    if user_id not in user_states:
        user_states[user_id] = UserState()

    welcome_message = (
        "👋 Welcome to the LATOKEN Assistant Bot!\n\n"
        "I can help you with information about:\n"
        "- LATOKEN company\n"
        "- LATOKEN Culture Deck\n"
        "- Ongoing hackathon\n"
        "- Interview process\n\n"
        "Just ask me anything related to these topics! I'll respond in the language you use."
    )

    # Detect language and translate welcome message if needed
    message_text = update.message.text
    if len(message_text) > 7:  # If there's text after /start
        detected_lang = detect_language(message_text[7:].strip())
        user_states[user_id].language = detected_lang
        if detected_lang != 'ru':
            welcome_message = translate_response(welcome_message, detected_lang)

    await update.message.reply_text(welcome_message)


async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages and generate responses"""
    if not knowledge_base:
        await update.message.reply_text(
            "The knowledge base is still initializing. Please try again in a moment."
        )
        return

    user_id = update.effective_user.id

    # Initialize user state if not exists
    if user_id not in user_states:
        user_states[user_id] = UserState()

    user_state = user_states[user_id]

    # Get user message
    user_message = update.message.text
    logger.info(f"User message: {user_message}")

    # Detect language
    detected_lang = detect_language(user_message)
    user_state.language = detected_lang

    # Send typing indicator
    await update.message.chat.send_action("typing")

    # Query the knowledge base
    retrieved_docs, metadata = knowledge_base.query(user_message)

    # Format context from retrieved documents
    context = format_context(retrieved_docs, metadata)

    # Generate response
    response = await generate_response(user_message, context, detected_lang, user_state)

    logger.info(f"Response: {response}")
    # Update chat history
    user_state.chat_history.append({
        "user": user_message,
        "assistant": response
    })

    # Send response
    await update.message.reply_text(response)


async def help_command(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the command /help is issued"""
    user_id = update.effective_user.id

    # Get user language or use Russian as default
    user_lang = 'ru'
    if user_id in user_states:
        user_lang = user_states[user_id].language

    help_text = (
        "🔍 LATOKEN Assistant Bot Help\n\n"
        "I'm an AI assistant designed to provide information about LATOKEN.\n\n"
        "Commands:\n"
        "- /start - Start the conversation\n"
        "- /help - Show this help message\n"
        "- /reset - Reset your conversation history\n\n"
        "I can answer questions about:\n"
        "- LATOKEN company and its services\n"
        "- LATOKEN Culture Deck\n"
        "- Hackathon details\n"
        "- Interview and hiring process\n\n"
        "Every third answer, I'll check your understanding with specific "
        "questions about the topics we've discussed to help you learn key "
        "concepts about LATOKEN.\n\n"
        "I'll automatically respond in the language you use for your question."
    )

    # Translate if needed
    if user_lang != 'ru':
        help_text = translate_response(help_text, user_lang)

    await update.message.reply_text(help_text)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset the conversation history for a user"""
    user_id = update.effective_user.id

    # Get user language and answers before resetting
    user_lang = 'ru'
    gpt_answers = []
    if user_id in user_states:
        user_lang = user_states[user_id].language
        gpt_answers = user_states[user_id].gpt_answers

    # Reset user state
    user_states[user_id] = UserState()
    user_states[user_id].language = user_lang  # Retain language preference
    user_states[user_id].gpt_answers = gpt_answers  # Retain GPT answers history

    reset_message = "Conversation history has been reset. You can start a new conversation now."

    # Translate if needed
    if user_lang != 'ru':
        reset_message = translate_response(reset_message, user_lang)

    await update.message.reply_text(reset_message)


def main() -> None:
    """Initialize and start the bot"""
    global knowledge_base

    # Initialize knowledge base
    logger.info("Initializing knowledge base...")
    knowledge_base = initialize_knowledge_base()

    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
                                           handle_message))

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
