import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import compute_app_sentiment

st.title("Sentiment Analysis")

if "data" not in st.session_state:
    st.warning("No data yet. Go to the **Search** page and run a search first.")
    st.stop()

df = st.session_state["data"].copy()
search_term = st.session_state.get("search_term", "your search")
st.caption(f"Sentiment analysis for: **{search_term}**")

st.info(
    "Uses a multilingual Hugging Face model (positive / neutral / negative). "
    "First run downloads the model — this can take a minute."
)

# Run analysis 
if st.button("Run sentiment analysis", type="primary"):
    results = []
    all_reviews = []
    progress = st.progress(0)
    apps = df.to_dict("records")

    for i, app_row in enumerate(apps):
        reviews_list = app_row.get("reviews", [])
        sentiment = compute_app_sentiment(reviews_list)
        results.append({
            "title":    app_row.get("title"),
            "appId":    app_row.get("appId"),
            "score":    app_row.get("score"),
            "positive": sentiment["positive"],
            "neutral":  sentiment["neutral"],
            "negative": sentiment["negative"],
            "total":    sentiment.get("total", 0),
            "net_score": sentiment["net_score"],
            "analyzed_reviews": sentiment["analyzed_reviews"],
        })
        # Flatten all reviews for cross-app analysis
        for r in sentiment["analyzed_reviews"]:
            all_reviews.append({**r, "app_title": app_row.get("title")})
        progress.progress((i + 1) / len(apps))

    st.session_state["sentiment_results"] = pd.DataFrame(results)
    st.session_state["all_reviews"] = pd.DataFrame(all_reviews)
    st.success("Analysis complete!")

# Display
if "sentiment_results" not in st.session_state:
    st.stop()

sdf = st.session_state["sentiment_results"]
rdf = st.session_state.get("all_reviews", pd.DataFrame())


# SECTION 1 — Inter-app comparison
st.divider()
st.subheader("1 · App-by-App Comparison")

# 1a. Net sentiment score (horizontal bar)
fig_net = px.bar(
    sdf.sort_values("net_score", ascending=False),
    x="net_score", y="title", orientation="h",
    color="net_score",
    color_continuous_scale=["#F44336", "#FFEB3B", "#4CAF50"],
    range_color=[-1, 1],
    labels={"net_score": "Net score  (−1 = all negative · +1 = all positive)", "title": ""},
)
fig_net.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig_net, use_container_width=True)

# 1b. Stacked bar: pos / neutral / neg counts
st.subheader("Sentiment breakdown per app")
stack_df = sdf[["title", "positive", "neutral", "negative"]].copy()
stack_df = stack_df.sort_values("positive", ascending=False)
stack_melt = stack_df.melt(id_vars="title", var_name="sentiment", value_name="count")
fig_stack = px.bar(
    stack_melt,
    x="title", y="count", color="sentiment", barmode="stack",
    color_discrete_map={"positive": "#4CAF50", "neutral": "#BDBDBD", "negative": "#F44336"},
    labels={"title": "", "count": "# Reviews"},
)
fig_stack.update_layout(xaxis_tickangle=-30, legend_title="")
st.plotly_chart(fig_stack, use_container_width=True)

# 1c. Ranking table
st.subheader("Ranking table")
rank_df = sdf[["title", "net_score", "positive", "neutral", "negative", "total"]].copy()
rank_df = rank_df.sort_values("net_score", ascending=False).reset_index(drop=True)
rank_df.index += 1
rank_df.columns = ["App", "Net Score", "Positive", "Neutral", "Negative", "Total Reviews"]
rank_df["Net Score"] = rank_df["Net Score"].round(3)
st.dataframe(rank_df, use_container_width=True)


# SECTION 2 — Sentiment × Star rating cross-analysis
st.divider()
st.subheader("2 · Sentiment vs. Star Rating")

if not rdf.empty and "score" in rdf.columns:
    col1, col2 = st.columns(2)

    # 2a. Scatter: store star rating vs net_score per app
    with col1:
        scatter_df = sdf.merge(
            df[["title", "score"]].rename(columns={"score": "store_rating"}),
            on="title", how="left"
        ).dropna(subset=["store_rating", "net_score"])
        fig_scatter = px.scatter(
            scatter_df,
            x="store_rating", y="net_score",
            text="title", size="total",
            color="net_score",
            color_continuous_scale=["#F44336", "#FFEB3B", "#4CAF50"],
            range_color=[-1, 1],
            labels={"store_rating": "Store Rating (★)", "net_score": "Sentiment Net Score"},
            title="Store rating vs sentiment score",
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=9)
        fig_scatter.update_layout(coloraxis_showscale=False, showlegend=False)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption(
            "Apps above the trend: users rate them higher in reviews than the store score suggests. "
            "Apps below: hidden dissatisfaction despite a good store score."
        )

    # 2b. Review-level: sentiment distribution per star score
    with col2:
        star_sent = (
            rdf[rdf["score"].notna()]
            .groupby(["score", "sentiment"])
            .size()
            .reset_index(name="count")
        )
        star_sent["score"] = star_sent["score"].astype(int).astype(str) + "★"
        fig_star = px.bar(
            star_sent,
            x="score", y="count", color="sentiment", barmode="group",
            color_discrete_map={"positive": "#4CAF50", "neutral": "#BDBDBD", "negative": "#F44336"},
            labels={"score": "Review star score", "count": "# Reviews"},
            title="Sentiment per star score",
            category_orders={"score": ["1★", "2★", "3★", "4★", "5★"]},
        )
        fig_star.update_layout(legend_title="")
        st.plotly_chart(fig_star, use_container_width=True)
        st.caption(
            "Ideally 5★ reviews should be 'positive' and 1★ should be 'negative'. "
            "Mismatches reveal sarcasm, non-English text, or model errors."
        )

    # 2c. Sentiment consistency score (positive rate among 5★, negative rate among 1★)
    if not rdf.empty:
        st.subheader("Sentiment consistency (by star score)")
        for label, star_val, sent_label, color in [
            ("5★ reviews that are positive", 5, "positive", "#4CAF50"),
            ("1★ reviews that are negative", 1, "negative", "#F44336"),
        ]:
            subset = rdf[rdf["score"] == star_val]
            if not subset.empty:
                pct = (subset["sentiment"] == sent_label).mean() * 100
                st.metric(label, f"{pct:.0f}%")
else:
    st.info("Review-level star scores not available — run the search with reviews enabled.")

# SECTION 3 — Rich visualisations
st.divider()
st.subheader("3 · Rich Visualisations")

# 3a. Heatmap: app × sentiment %
st.markdown("**Sentiment heatmap (% of reviews per sentiment)**")
heat_df = sdf[["title", "positive", "neutral", "negative", "total"]].copy()
heat_df = heat_df[heat_df["total"] > 0].copy()
for col in ["positive", "neutral", "negative"]:
    heat_df[col + "_pct"] = (heat_df[col] / heat_df["total"] * 100).round(1)

heat_pivot = heat_df.set_index("title")[["positive_pct", "neutral_pct", "negative_pct"]]
heat_pivot.columns = ["Positive %", "Neutral %", "Negative %"]

fig_heat = px.imshow(
    heat_pivot,
    color_continuous_scale="RdYlGn",
    text_auto=True,
    aspect="auto",
    labels={"color": "%"},
    zmin=0, zmax=100,
)
fig_heat.update_layout(xaxis_title="", yaxis_title="")
st.plotly_chart(fig_heat, use_container_width=True)

# SECTION 4 — App deep-dive
st.divider()
st.subheader("4 · App Deep-Dive")

selected_app = st.selectbox("Choose an app", sdf["title"].tolist())
row = sdf[sdf["title"] == selected_app].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Net Sentiment Score", f"{row['net_score']:.2f}")
m2.metric("Positive", int(row["positive"]))
m3.metric("Neutral",  int(row["neutral"]))
m4.metric("Negative", int(row["negative"]))

# Donut for this app
donut_df = pd.DataFrame({
    "sentiment": ["Positive", "Neutral", "Negative"],
    "count":     [row["positive"], row["neutral"], row["negative"]],
})
fig_donut = px.pie(donut_df, names="sentiment", values="count", hole=0.5,
                   color="sentiment",
                   color_discrete_map={"Positive": "#4CAF50", "Neutral": "#BDBDBD", "Negative": "#F44336"})
st.plotly_chart(fig_donut, use_container_width=True)

# Review list with sentiment badge
with st.expander("Read analysed reviews"):
    sentiment_filter = st.multiselect(
        "Filter by sentiment",
        ["positive", "neutral", "negative"],
        default=["positive", "neutral", "negative"],
    )
    EMOJI = {"positive": "🟢", "neutral": "⚪", "negative": "🔴"}
    shown = 0
    for r in row["analyzed_reviews"]:
        if r["sentiment"] not in sentiment_filter:
            continue
        stars = "★" * int(r.get("score", 0)) if r.get("score") else ""
        st.markdown(
            f"{EMOJI[r['sentiment']]} **{r['sentiment'].capitalize()}** "
            f"· {stars} · *{r.get('userName', 'Anonymous')}*  \n"
            f"{r.get('content', '')[:300]}"
        )
        st.divider()
        shown += 1
        if shown >= 30:
            break
