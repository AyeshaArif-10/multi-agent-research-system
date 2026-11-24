```python
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup


def web_search(query: str = None, queries: list = None) -> str:
    """Search the web and return relevant titles, URLs, and snippets."""

    try:
        search_queries = []

        if query:
            search_queries.append(query)

        if queries:
            search_queries.extend(queries)

        if not search_queries:
            return "No search query provided."

        output = []
        seen_urls = set()

        with DDGS() as ddgs:
            for search_query in search_queries[:2]:

                results = ddgs.text(
                    search_query,
                    max_results=5,
                    backend="auto"
                )

                if not results:
                    continue

                for result in results:
                    url = result.get("href", "No URL")

                    if url in seen_urls:
                        continue

                    seen_urls.add(url)

                    output.append(
                        f"Title: {result.get('title', 'No title')}\n"
                        f"URL: {url}\n"
                        f"Snippet: {result.get('body', 'No description')}"
                    )

                    if len(output) >= 5:
                        break

                if len(output) >= 5:
                    break

        if not output:
            return "No search results found. Try a different search query."

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
```
