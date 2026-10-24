'''from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    results = tavily.search(query=query,max_results=5)
    out=[]
    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n" #this is written in dictionary fomat the results are title , url and contents will be within 300 characters 
        )
    return "\n----\n".join(out)    #.join is used to join all the o/p in the list to form a string better way of showing the result and this is the first tool we created
@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"}) # timeout= 8 after 8 sec it'll be closed 
        soup = BeautifulSoup(resp.text, "html.parser") #resp.text=raw html text
        for tag in soup(["script", "style", "nav", "footer"]): # all the part written inside the bracket will be removed
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000] #only 3000 characters
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
'''

from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup



from ddgs import DDGS


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



