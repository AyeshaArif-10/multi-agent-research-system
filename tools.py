from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


def web_search(query: str) -> str:
    """Search the web and return relevant titles, URLs, and snippets."""

    try:
        results = DDGS().text(
            query,
            max_results=5,
            backend="auto"
        )

        if not results:
            return "No search results found. Try a more specific query."

        output = []

        for result in results:
            output.append(
                f"Title: {result.get('title', 'No title')}\n"
                f"URL: {result.get('href', 'No URL')}\n"
                f"Snippet: {result.get('body', 'No description')}"
            )

        return "\n\n".join(output)

    except Exception as e:
        return f"Web search failed: {str(e)}"


def scrape_url(url: str) -> str:
    """Extract readable text from a webpage."""

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)

        return text[:10000] if text else "No readable text found."

    except Exception as e:
        return f"Webpage reading failed: {str(e)}"

