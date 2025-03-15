#!/usr/bin/env python3
import os
import logging
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
from openai import OpenAI
from config import SOURCES, RESOURCES_DIR, OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def fetch_html_content(url):
    """
    Fetch raw HTML content from a URL

    Args:
        url (str): The URL to fetch content from

    Returns:
        str: The HTML content of the page
    """
    try:
        logger.info(f"Fetching HTML from {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 '
            'Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error fetching content from {url}: {e}")
        return f"Error fetching content from {url}: {e}"


def get_page_title(html_content, url):
    """
    Extract page title from HTML content

    Args:
        html_content (str): HTML content
        url (str): URL for fallback

    Returns:
        str: Page title or default title based on URL
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else None

        if not title:
            # Extract domain and path as fallback title
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            path = parsed_url.path.strip('/')
            title = f"{domain} - {path}" if path else domain

        return title.strip()
    except Exception as e:
        logger.error(f"Error extracting title from {url}: {e}")
        return url


def generate_markdown_from_html(html_content, url):
    """
    Generate markdown content from HTML using GPT

    Args:
        html_content (str): HTML content of the page
        url (str): Original URL for reference

    Returns:
        str: Generated markdown content
    """
    # First, do a basic clean-up with BeautifulSoup to reduce token usage
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'iframe', 'noscript']):
        element.extract()

    # Get the text content
    raw_text = soup.get_text(separator='\n', strip=True)

    # Limit the content length to avoid token limit issues
    # GPT-4 max token limit is high, but we'll truncate to be safe
    max_chars = 15000  # Approx 3000-4000 tokens
    if len(raw_text) > max_chars:
        raw_text = raw_text[:max_chars] + "..."

    logger.info(f"Sending content from {url} to GPT for markdown conversion")

    prompt = f"""
You are an expert at extracting meaningful content from web pages that rely 
heavily on JavaScript.
I'll provide you with the raw HTML or text content from a JavaScript-heavy page 
from LATOKEN's website.

Your task is to:
1. Extract all relevant information about LATOKEN, its culture, values, hiring 
processes, or hackathon details
2. Ignore navigation elements, footers, and unrelated content
3. Format the extracted information as clean, structured Markdown with proper 
headings, lists, etc.
4. Prioritize information about company culture, values, work processes, and 
the hackathon
5. Create a cohesive, well-structured document
6. If the content seems incomplete or broken due to JavaScript rendering issues,
use your knowledge to create a reasonable representation of what the page 
likely contains

Original URL: {url}

Raw content:
{raw_text}
"""

    try:
        system_content = (
            "You convert content from JS-heavy websites into clean, "
            "structured markdown documents."
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4000
        )

        markdown_content = response.choices[0].message.content.strip()
        return markdown_content
    except Exception as e:
        logger.error(f"Error generating markdown with GPT: {e}")
        return f"# Error Processing {url}\n\nUnable to generate markdown: {e}"


def save_markdown_file(content, url):
    """
    Save markdown content to a file

    Args:
        content (str): Markdown content
        url (str): Source URL used for filename

    Returns:
        str: Path to saved file
    """
    # Create a filename based on the URL
    parsed_url = urlparse(url)

    # Extract domain and path for filename
    domain = parsed_url.netloc.replace('.', '_')
    path = parsed_url.path.strip('/')
    if path:
        path = path.replace('/', '_')
        filename = f"{domain}_{path}.md"
    else:
        filename = f"{domain}.md"

    file_path = os.path.join(RESOURCES_DIR, filename)

    logger.info(f"Saving markdown to {file_path}")

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    except Exception as e:
        logger.error(f"Error saving markdown file: {e}")
        return None


def process_url(url):
    """
    Process a single URL: fetch HTML, generate markdown, save to file

    Args:
        url (str): URL to process

    Returns:
        str: Path to saved markdown file or None if failed
    """
    logger.info(f"Processing URL: {url}")

    # Fetch HTML content
    html_content = fetch_html_content(url)
    if html_content.startswith("Error"):
        return None

    # Get page title
    title = get_page_title(html_content, url)

    # Generate markdown content
    markdown_content = generate_markdown_from_html(html_content, url)

    # Add title as h1 if not already present
    if not markdown_content.strip().startswith('# '):
        markdown_content = f"# {title}\n\n{markdown_content}"

    # Save to file
    file_path = save_markdown_file(markdown_content, url)

    return file_path


def process_all_sources():
    """
    Process all URLs in SOURCES config

    Returns:
        list: Paths to all generated markdown files
    """
    logger.info(f"Processing {len(SOURCES)} URLs from config")

    # Ensure resources directory exists
    os.makedirs(RESOURCES_DIR, exist_ok=True)

    generated_files = []

    for i, url in enumerate(SOURCES, 1):
        logger.info(f"Processing URL {i}/{len(SOURCES)}: {url}")
        file_path = process_url(url)

        if file_path:
            generated_files.append(file_path)

        # Add a delay to avoid rate limiting if processing many URLs
        if i < len(SOURCES):
            time.sleep(1)

    logger.info(f"Generated {len(generated_files)} markdown files")
    return generated_files


if __name__ == "__main__":
    logger.info("Starting markdown generation from URLs")
    generated_files = process_all_sources()

    # Print summary
    print("\nGenerated markdown files:")
    for file_path in generated_files:
        print(f"- {file_path}")
