import requests
from bs4 import BeautifulSoup
import logging
from config import SOURCES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_content(url):
    """
    Fetch content from a URL

    Args:
        url (str): The URL to fetch content from

    Returns:
        str: The text content of the page
    """
    try:
        logger.info(f"Fetching content from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the main content (might need adjustment based on page structure)
        # Remove script, style elements and navigation
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.extract()

        # Get the text content
        text = soup.get_text(separator=' ', strip=True)

        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return f"Error fetching content from {url}: {e}"


def fetch_all_sources():
    """
    Fetch content from all sources

    Returns:
        dict: A dictionary mapping source URLs to their content
    """
    logger.info("Fetching content from all sources")
    source_contents = {}

    for source in SOURCES:
        content = fetch_content(source)
        source_contents[source] = content

    return source_contents


if __name__ == "__main__":
    # Test the scraper
    contents = fetch_all_sources()
    for source, content in contents.items():
        print(f"Source: {source}")
        print(f"Content length: {len(content)}")
        print(f"Preview: {content[:500]}...")
        print("="*80)
