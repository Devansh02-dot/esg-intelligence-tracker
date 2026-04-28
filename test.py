from utils.news_fetcher import fetch_esg_news

articles = fetch_esg_news("Infosys")

print(f"Found {len(articles)} articles\n")
for a in articles[:3]:
    print(a["title"])
    print(a["snippet"][:80])
    print("---")