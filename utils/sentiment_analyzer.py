import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_articles(articles: list, company_name: str) -> list:
    articles = articles[:8]

    articles_text = ""
    for i, a in enumerate(articles):
        articles_text += f"""
Article {i+1}:
Title: {a['title']}
Description: {a['snippet']}
"""

    prompt = f"""You are a senior ESG analyst analyzing news about {company_name}.

Analyze each article and return a JSON array.
Each object must have:
- "index": article number (1, 2, 3...)
- "sentiment": one of "Positive", "Negative", "Neutral"
- "pillar": one of "Environmental", "Social", "Governance", "General"
- "score": integer 0-100 (100 = very positive for ESG reputation)
- "risk_flag": one short sentence about the ESG risk or strength

{articles_text}

Return ONLY a valid JSON array. No explanation. No markdown."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        results = json.loads(text)

        for r in results:
            idx = r.get("index", 1) - 1
            if 0 <= idx < len(articles):
                articles[idx]["sentiment"] = r.get("sentiment", "Neutral")
                articles[idx]["pillar"]    = r.get("pillar", "General")
                articles[idx]["score"]     = r.get("score", 50)
                articles[idx]["risk_flag"] = r.get("risk_flag", "")

    except Exception as e:
        print(f"Analysis error: {e}")
        for a in articles:
            a.setdefault("sentiment", "Neutral")
            a.setdefault("pillar",    "General")
            a.setdefault("score",     50)
            a.setdefault("risk_flag", "Could not analyze")

    return articles


def generate_brief(analyzed_articles: list, company_name: str) -> str:
    summary = ""
    for a in analyzed_articles[:6]:
        summary += f"- [{a.get('sentiment','Neutral')}] {a['title']}\n"

    prompt = f"""You are a senior ESG advisor writing a weekly intelligence brief.

Company: {company_name}
Recent ESG news:
{summary}

Write a 3-4 sentence intelligence brief covering:
1. Overall ESG reputation status
2. The strongest positive signal
3. The biggest risk or gap to watch
4. One specific recommendation

Professional business language. Be specific. No bullet points."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip()


def calculate_pillar_scores(analyzed_articles: list) -> dict:
    pillars = {"Environmental": [], "Social": [], "Governance": []}

    for a in analyzed_articles:
        pillar = a.get("pillar", "General")
        if pillar in pillars:
            pillars[pillar].append(a.get("score", 50))

    scores = {}
    for pillar, vals in pillars.items():
        scores[pillar] = round(sum(vals) / len(vals)) if vals else 50

    scores["Overall"] = round(sum(scores.values()) / 3)
    return scores