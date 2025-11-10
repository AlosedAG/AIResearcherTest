# main.py - Simple web scraper using requests to Ollama API
import requests
from bs4 import BeautifulSoup
import json


def scrape_website(url):
    """Scrape all text from a website"""
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


def ask_ollama(content, question, model="tinyllama"):
    """Send question to Ollama via API"""
    try:
        url = "http://localhost:11434/api/generate"

        prompt = f"""Based on this website content, answer the question.

Website Content:
{content[:6000]}

Question: {question}

Answer:"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            return f"Error: Status {response.status_code}"

    except Exception as e:
        return f"Error: {str(e)}"


def main():
    print("=" * 80)
    print("Web Content Question Answering System")
    print("=" * 80)

    # Get URL from user
    url = input("\nEnter website URL: ").strip()

    if not url:
        print("No URL provided. Exiting.")
        return

    # Add https:// if not present
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Scrape the website
    print("\n" + "=" * 80)
    content = scrape_website(url)

    if not content:
        print("Failed to scrape content. Exiting.")
        return

    print(f"✓ Successfully scraped {len(content)} characters")
    print(f"\nPreview:\n{content[:300]}...")
    print("=" * 80)

    # Interactive Q&A
    print("\nYou can now ask questions about the content!")
    print("Type 'quit' to exit\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break

        if not question:
            continue

        print("\nThinking...\n")
        answer = ask_ollama(content, question)
        print(f"Answer: {answer}\n")
        print("-" * 80 + "\n")


if __name__ == "__main__":
    main()