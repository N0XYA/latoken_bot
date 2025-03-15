import logging
from langdetect import detect
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Language map for common languages
LANGUAGE_MAP = {
    'en': 'English',
    'ru': 'Russian',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic'
}


def detect_language(text):
    """
    Detect the language of the input text

    Args:
        text (str): The text to detect language for

    Returns:
        str: The detected language code or 'ru' if detection fails
    """
    try:
        lang_code = detect(text)
        logger.info(
            f"Detected language: {LANGUAGE_MAP.get(lang_code, lang_code)}"
        )
        return lang_code
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return 'ru'  # Default to Russian on error


def translate_response(response, target_language):
    """
    Use the OpenAI model to translate a response to the target language

    Args:
        response (str): The response to translate
        target_language (str): The target language code

    Returns:
        str: The translated response
    """
    # If already in English or target language not recognized, return as is
    if target_language == 'en' or target_language not in LANGUAGE_MAP:
        return response

    try:
        language_name = LANGUAGE_MAP.get(
            target_language, f"language with code {target_language}"
        )
        logger.info(f"Translating response to {language_name}")

        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY, 
            model="gpt-3.5-turbo",
            temperature=0
        )

        message = [
            {
                "role": "system",
                "content": (
                    f"You are a helpful translator. Translate the following "
                    f"text to {language_name}. Maintain the same meaning, "
                    f"tone, and formatting."
                )
            },
            {
                "role": "user",
                "content": response
            }
        ]

        result = llm.invoke(message)
        translated_response = result.content

        return translated_response
    except Exception as e:
        logger.error(f"Error translating response: {e}")
        return response  # Return original response on error


if __name__ == "__main__":
    # Test the language detection and translation
    test_texts = [
        "Hello, how can I help you with LATOKEN information?",
        "Привет, чем я могу помочь вам с информацией о LATOKEN?",
        "Bonjour, comment puis-je vous aider avec les informations LATOKEN?"
    ]

    for text in test_texts:
        detected_lang = detect_language(text)
        print(f"Text: '{text[:30]}...'")
        print(
            f"Detected language: {LANGUAGE_MAP.get(detected_lang, detected_lang)}"
        )

        # Test translation back to English if not already English
        if detected_lang != 'en':
            translated = translate_response(text, 'en')
            print(f"Translated to English: '{translated[:30]}...'")

        print("-" * 40)
