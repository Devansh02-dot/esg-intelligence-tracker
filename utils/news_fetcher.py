import os
import requests
from dotenv import load_dotenv

load_dotenv()  # loads your .env file

SERPER_KEY = os.getenv("SERPER_API_KEY")

def fetch_esg_news(company_name: str) -> list:
    """
    Fetches ESG-related news for a given company.
    Returns a list of article dictionaries.
    """

    # Three different searches to get broad coverage
    search_queries = [
        f"{company_name} ESG sustainability environment 2024",
        f"{company_name} social responsibility diversity governance",
        f"{company_name} ESG controversy scandal risk",
    ]

    all_articles = []

    for query in search_queries:
        headers = {
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json"
        }

        body = {"q": query, "num": 5}

        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json=body
        )

        # Extract results
        results = response.json().get("organic", [])

        for r in results:
            article = {
                "title":   r.get("title", "No title"),
                "snippet": r.get("snippet", "No description"),
                "source":  r.get("source", "Unknown"),
                "date":    r.get("date", "Unknown date"),
                "link":    r.get("link", "#"),
            }
            all_articles.append(article)

    # Remove duplicates
    seen = set()
    unique_articles = []
    for a in all_articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique_articles.append(a)

    return unique_articles