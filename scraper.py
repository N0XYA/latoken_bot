import requests
from bs4 import BeautifulSoup
import logging
import glob
from pathlib import Path
from config import SOURCES, RESOURCES_DIR

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
        chunks = (phrase.strip() for line in lines
                  for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return f"Error fetching content from {url}: {e}"


def read_markdown_file(file_path):
    """
    Read content from a markdown file

    Args:
        file_path (str): Path to the markdown file

    Returns:
        str: The text content of the file
    """
    try:
        logger.info(f"Reading content from file {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except Exception as e:
        logger.error(f"Error reading content from {file_path}: {e}")
        return f"Error reading content from {file_path}: {e}"


def get_markdown_files():
    """
    Get all markdown files from the resources directory

    Returns:
        list: List of markdown file paths
    """
    resources_path = Path(RESOURCES_DIR)
    if not resources_path.exists():
        logger.warning(f"Resources directory {RESOURCES_DIR} does not exist")
        return []

    markdown_files = glob.glob(
        str(resources_path / "**" / "*.md"), recursive=True
    )
    logger.info(
        f"Found {len(markdown_files)} markdown files in {RESOURCES_DIR}"
    )
    return markdown_files


def fetch_all_sources():
    """
    Fetch content from all sources (URLs and markdown files)

    Returns:
        dict: A dictionary mapping source identifiers to their content
    """
    logger.info("Fetching content from all sources")
    source_contents = {}

    # Fetch URL sources
    for source in SOURCES:
        content = fetch_content(source)
        source_contents[source] = content

    # Fetch markdown files
    markdown_files = get_markdown_files()
    for file_path in markdown_files:
        content = read_markdown_file(file_path)
        source_contents[file_path] = content

    logger.info(f"Fetched content from {len(source_contents)} sources total")
    return source_contents


if __name__ == "__main__":
    # Test the scraper
    contents = fetch_all_sources()
    for source, content in contents.items():
        print(f"Source: {source}")
        print(f"Content length: {len(content)}")
        print(f"Preview: {content[:200]}...")
        print("="*80)
