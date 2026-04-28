import plotly.graph_objects as go


def score_gauge(value: int, title: str, color: str) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": color},
            "steps": [
                {"range": [0,  40], "color": "#FEE2E2"},
                {"range": [40, 70], "color": "#FEF9C3"},
                {"range": [70,100], "color": "#DCFCE7"},
            ],
        }
    ))
    fig.update_layout(height=200, margin=dict(t=30,b=0,l=10,r=10))
    return fig


def sentiment_donut(analyzed_articles: list) -> go.Figure:
    counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for a in analyzed_articles:
        counts[a.get("sentiment", "Neutral")] += 1

    fig = go.Figure(go.Pie(
        labels=list(counts.keys()),
        values=list(counts.values()),
        hole=0.55,
        marker_colors=["#1D9E75", "#C47D0E", "#D85A30"],
        textinfo="percent",
    ))
    fig.update_layout(
        height=240,
        margin=dict(t=10,b=10,l=10,r=10),
        showlegend=True,
        legend=dict(font=dict(size=11)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def pillar_bar(scores: dict) -> go.Figure:
    pillars = ["Environmental", "Social", "Governance"]
    values  = [scores.get(p, 50) for p in pillars]
    colors  = ["#1D9E75", "#7F77DD", "#C47D0E"]

    fig = go.Figure(go.Bar(
        x=values, y=pillars,
        orientation="h",
        marker_color=colors,
        text=[f"{v}/100" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        height=200,
        xaxis=dict(range=[0, 115]),
        margin=dict(t=10,b=10,l=10,r=50),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def risk_heatmap(analyzed_articles: list) -> go.Figure:
    neg = [a for a in analyzed_articles
           if a.get("sentiment") == "Negative"][:6]

    if not neg:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ No significant risks detected",
            showarrow=False,
            font=dict(size=14, color="#1D9E75")
        )
        fig.update_layout(
            height=150,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        return fig

    labels = [a["title"][:45]+"..." for a in neg]
    scores = [100 - a["score"] for a in neg]

    fig = go.Figure(go.Bar(
        x=scores, y=labels,
        orientation="h",
        marker_color="#D85A30",
        text=[f"Risk: {s}" for s in scores],
        textposition="outside",
    ))
    fig.update_layout(
        height=max(150, len(neg)*55),
        margin=dict(t=10,b=10,l=10,r=70),
        xaxis=dict(range=[0, 115]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig