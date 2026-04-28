import streamlit as st
from utils.news_fetcher import fetch_esg_news
from utils.sentiment_analyzer import (analyze_articles,
                                       generate_brief,
                                       calculate_pillar_scores)
from utils.charts import (score_gauge, sentiment_donut,
                           pillar_bar, risk_heatmap)
from utils.pdf_generator import generate_pdf

st.set_page_config(
    page_title="ESG Intelligence Tracker",
    page_icon="🌍",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1D9E75, #7F77DD);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .main-header h1 { color: white; font-size: 28px; margin: 0; font-weight: 600; }
    .main-header p  { color: rgba(255,255,255,0.85); margin: 6px 0 0 0; font-size: 14px; }
    .brief-box {
        background: linear-gradient(135deg, #0d2b22, #1a1635);
        border: 1px solid #1D9E75;
        border-radius: 10px;
        padding: 18px 20px;
        color: #e0f5ee;
        font-size: 14px;
        line-height: 1.7;
    }
    .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #e0e0e0;
        margin-bottom: 12px;
        padding-bottom: 6px;
        border-bottom: 1px solid #2D3250;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state — saves results across button clicks ──
if "analyzed"   not in st.session_state: st.session_state.analyzed   = None
if "scores"     not in st.session_state: st.session_state.scores     = None
if "brief"      not in st.session_state: st.session_state.brief      = None
if "company"    not in st.session_state: st.session_state.company    = None
if "pdf_path"   not in st.session_state: st.session_state.pdf_path   = None

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 ESG Intelligence")
    st.markdown("---")

    company = st.text_input(
        "🏢 Company name",
        placeholder="e.g. Infosys, Tesla, Tata Motors"
    )
    industry = st.selectbox(
        "🏭 Industry",
        ["Technology","Finance","Energy","Manufacturing","Retail","Healthcare"]
    )
    compare_company = st.text_input(
        "⚖️ Compare with (optional)",
        placeholder="e.g. TCS, Wipro"
    )
    run = st.button("🔍 Analyse ESG", type="primary",
                    use_container_width=True)

    st.markdown("---")
    st.markdown("**How it works:**")
    st.caption("1. Pulls latest ESG news from web")
    st.caption("2. AI classifies sentiment & pillar")
    st.caption("3. Scores across E, S, G dimensions")
    st.caption("4. Flags reputational risks")
    st.caption("5. Generates PDF report")
    st.markdown("---")
    st.caption("Powered by Groq AI + Llama 3.3")

# ── Header ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌍 ESG Intelligence Tracker</h1>
    <p>Real-time ESG sentiment analysis & reputational risk monitoring — powered by AI</p>
</div>
""", unsafe_allow_html=True)

# ── Run analysis only when button clicked ─────────────────
if run and company:
    st.session_state.pdf_path = None  # reset old PDF

    progress = st.progress(0, text="Starting analysis...")

    with st.spinner(f"📰 Fetching ESG news for {company}..."):
        articles = fetch_esg_news(company)
    progress.progress(33, text="News fetched — running AI analysis...")

    with st.spinner("🤖 Analysing sentiment with Groq AI..."):
        analyzed = analyze_articles(articles, company)
        scores   = calculate_pillar_scores(analyzed)
    progress.progress(66, text="Scores calculated — generating brief...")

    with st.spinner("✍️ Generating intelligence brief..."):
        brief = generate_brief(analyzed, company)
    progress.progress(100, text="Analysis complete!")

    # Save everything to session state
    st.session_state.analyzed = analyzed
    st.session_state.scores   = scores
    st.session_state.brief    = brief
    st.session_state.company  = company

# ── Welcome screen if no results yet ─────────────────────
if st.session_state.analyzed is None:
    col1, col2, col3 = st.columns(3)
    with col1: st.info("📰 **Step 1**\nEnter any company name in the sidebar")
    with col2: st.info("🤖 **Step 2**\nAI analyses ESG news in real time")
    with col3: st.info("📊 **Step 3**\nGet scores, risks and PDF report")
    st.stop()

# ── Use saved results ─────────────────────────────────────
analyzed = st.session_state.analyzed
scores   = st.session_state.scores
brief    = st.session_state.brief
company  = st.session_state.company

st.success(f"✅ Analysis complete — {len(analyzed)} articles analysed for **{company}**")
st.markdown("---")

# ── Score gauges ──────────────────────────────────────────
st.markdown('<div class="section-title">📊 ESG Sentiment Scores</div>',
            unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
for col, val, title, color in [
    (col1, scores["Overall"],       "Overall",       "#1D9E75"),
    (col2, scores["Environmental"], "Environmental", "#1D9E75"),
    (col3, scores["Social"],        "Social",        "#7F77DD"),
    (col4, scores["Governance"],    "Governance",    "#C47D0E"),
]:
    col.plotly_chart(score_gauge(val, title, color),
                     use_container_width=True)

# ── Metric cards ──────────────────────────────────────────
def sentiment_label(s):
    return "🟢 Strong" if s >= 70 else ("🟡 Moderate" if s >= 50 else "🔴 At Risk")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Overall",       f"{scores['Overall']}/100",       sentiment_label(scores['Overall']))
col2.metric("Environmental", f"{scores['Environmental']}/100", sentiment_label(scores['Environmental']))
col3.metric("Social",        f"{scores['Social']}/100",        sentiment_label(scores['Social']))
col4.metric("Governance",    f"{scores['Governance']}/100",    sentiment_label(scores['Governance']))
st.markdown("---")

# ── Charts ────────────────────────────────────────────────
col_left, col_right = st.columns([1.4, 1])
with col_left:
    st.markdown('<div class="section-title">📈 Pillar Score Breakdown</div>',
                unsafe_allow_html=True)
    st.plotly_chart(pillar_bar(scores), use_container_width=True)
with col_right:
    st.markdown('<div class="section-title">🧭 Sentiment Distribution</div>',
                unsafe_allow_html=True)
    st.plotly_chart(sentiment_donut(analyzed), use_container_width=True)
st.markdown("---")

# ── Risk heatmap ──────────────────────────────────────────
st.markdown('<div class="section-title">⚠️ Top Reputational Risk Areas</div>',
            unsafe_allow_html=True)
st.plotly_chart(risk_heatmap(analyzed), use_container_width=True)
st.markdown("---")

# ── AI Brief ─────────────────────────────────────────────
st.markdown('<div class="section-title">🤖 AI Intelligence Brief</div>',
            unsafe_allow_html=True)
st.markdown(f'<div class="brief-box">{brief}</div>',
            unsafe_allow_html=True)
st.markdown("---")

# ── News feed ─────────────────────────────────────────────
st.markdown('<div class="section-title">📰 Analysed News Articles</div>',
            unsafe_allow_html=True)
sent_filter = st.multiselect(
    "Filter by sentiment",
    ["Positive", "Neutral", "Negative"],
    default=["Positive", "Neutral", "Negative"]
)
sent_icons = {"Positive":"🟢","Neutral":"🟡","Negative":"🔴"}
for a in analyzed:
    if a.get("sentiment") not in sent_filter:
        continue
    icon = sent_icons.get(a.get("sentiment"), "⚪")
    with st.expander(
        f"{icon} {a.get('sentiment')} · {a.get('pillar')} · {a['title'][:65]}"
    ):
        st.write(a["snippet"])
        st.caption(f"📰 {a.get('source')} | 📅 {a.get('date')}")
        st.caption(f"🔍 Risk flag: {a.get('risk_flag','')}")
        st.markdown(f"[Read full article ↗]({a.get('link','#')})")
st.markdown("---")

# ── Comparison ────────────────────────────────────────────
if compare_company:
    st.markdown(f'<div class="section-title">⚖️ {company} vs {compare_company}</div>',
                unsafe_allow_html=True)
    with st.spinner(f"Fetching data for {compare_company}..."):
        c2_art    = fetch_esg_news(compare_company)
        c2_ana    = analyze_articles(c2_art, compare_company)
        c2_scores = calculate_pillar_scores(c2_ana)
    import plotly.graph_objects as go
    pillars = ["Environmental","Social","Governance"]
    fig = go.Figure()
    fig.add_trace(go.Bar(name=company, x=pillars,
                         y=[scores[p] for p in pillars],
                         marker_color="#1D9E75"))
    fig.add_trace(go.Bar(name=compare_company, x=pillars,
                         y=[c2_scores[p] for p in pillars],
                         marker_color="#7F77DD"))
    fig.update_layout(barmode="group", height=300,
                      plot_bgcolor="rgba(0,0,0,0)",
                      paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# ── PDF ───────────────────────────────────────────────────
st.markdown('<div class="section-title">📄 Download Report</div>',
            unsafe_allow_html=True)
st.markdown("Generate a professional PDF with all scores, AI brief, and articles.")

if st.button("📄 Generate PDF Report", type="secondary"):
    with st.spinner("Generating your PDF..."):
        path = generate_pdf(company, scores, brief, analyzed)
        st.session_state.pdf_path = path

if st.session_state.pdf_path:
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ Download ESG Report PDF",
            data=f,
            file_name=f"{company}_ESG_Report.pdf",
            mime="application/pdf",
            type="primary"
        )
    st.success("✅ PDF ready — click above to download!")