import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Competitor Analysis")

if "data" not in st.session_state:
    st.warning("No data yet. Go to the **Search** page and run a search first.")
    st.stop()

df = st.session_state["data"].copy()
search_term = st.session_state.get("search_term", "your search")

st.caption(f"Competitive landscape for: **{search_term}**")

# Sidebar filters

all_apps = df["title"].dropna().tolist()
selected = st.sidebar.multiselect("Filter by app", options=all_apps, default=all_apps)
filtered = df[df["title"].isin(selected)] if selected else df

# KPI summary row 
st.subheader("Market Overview")

total_apps = len(filtered)
avg_rating = filtered["score"].mean()
pct_free = filtered["free"].mean() * 100 if "free" in filtered.columns else None
total_installs = filtered["realInstalls"].sum() if "realInstalls" in filtered.columns else None

k1, k2, k3, k4 = st.columns(4)
k1.metric("Apps analysed", total_apps)
k2.metric("Avg rating", f"{avg_rating:.2f} ★" if pd.notna(avg_rating) else "N/A")
if pct_free is not None:
    k3.metric("% Free apps", f"{pct_free:.0f}%")
if total_installs:
    k4.metric("Total installs", f"{total_installs:,.0f}")

st.divider()

# 1. Competitive positioning matrix (installs vs rating) 
st.subheader("Competitive Positioning Matrix")
st.caption("Bubble size = number of ratings. Top-right = market leaders.")

if "realInstalls" in filtered.columns and "score" in filtered.columns:
    pos_df = filtered.dropna(subset=["realInstalls", "score", "ratings"]).copy()
    if not pos_df.empty:
        fig_matrix = px.scatter(
            pos_df,
            x="realInstalls",
            y="score",
            size="ratings",
            color="genre",
            hover_name="title",
            hover_data={"developer": True, "installs": True, "free": True},
            labels={"realInstalls": "Total Installs", "score": "Average Rating"},
            size_max=60,
        )
        fig_matrix.update_layout(xaxis_type="log", xaxis_title="Installs (log scale)")
        st.plotly_chart(fig_matrix, use_container_width=True)
    else:
        st.info("Not enough data for the positioning matrix.")

st.divider()

# 2. Market share by installs
col1, col2 = st.columns(2)

with col1:
    st.subheader("Market Share by Installs")
    if "realInstalls" in filtered.columns:
        share_df = filtered[["title", "realInstalls"]].dropna().sort_values("realInstalls", ascending=False)
        fig_share = px.pie(share_df, names="title", values="realInstalls",
                           hole=0.4)
        fig_share.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_share, use_container_width=True)
    else:
        st.info("Install data not available.")

with col2:
    st.subheader("Rating vs Volume of Reviews")
    if "ratings" in filtered.columns and "score" in filtered.columns:
        rv_df = filtered.dropna(subset=["ratings", "score"]).copy()
        fig_rv = px.bar(
            rv_df.sort_values("ratings", ascending=False).head(15),
            x="title", y="ratings", color="score",
            color_continuous_scale="RdYlGn",
            labels={"ratings": "# Ratings", "title": ""},
            range_color=[1, 5],
        )
        fig_rv.update_layout(xaxis_tickangle=-45, coloraxis_colorbar_title="Rating")
        st.plotly_chart(fig_rv, use_container_width=True)
    else:
        st.info("Ratings data not available.")

st.divider()

#3. Top apps by installs (horizontal bar) 

with col3:
    st.subheader("Top 10 Apps by Installs")
    if "realInstalls" in filtered.columns:
        top_inst = filtered.dropna(subset=["realInstalls"]).sort_values("realInstalls", ascending=False).head(10)
        fig_inst = px.bar(top_inst, x="realInstalls", y="title", orientation="h",
                          color="free",
                          color_discrete_map={True: "#4CAF50", False: "#F44336"},
                          labels={"realInstalls": "Installs", "title": "", "free": "Free"})
        fig_inst.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_inst, use_container_width=True)

with col4:
    st.subheader("Top 10 Apps by Rating")
    top_rated = filtered.dropna(subset=["score"]).sort_values("score", ascending=False).head(10)
    fig_bar = px.bar(top_rated, x="score", y="title", orientation="h",
                     color="score", color_continuous_scale="RdYlGn",
                     range_color=[1, 5],
                     labels={"score": "Rating", "title": ""})
    fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

#4. Monetisation & Ads analysis 
st.subheader("Monetisation & Ads Strategy")

col5, col6 = st.columns(2)

with col5:
    if "free" in filtered.columns:
        free_counts = filtered["free"].value_counts().reset_index()
        free_counts.columns = ["type", "count"]
        free_counts["type"] = free_counts["type"].map({True: "Free", False: "Paid"})
        fig_free = px.pie(free_counts, names="type", values="count",
                          color="type",
                          color_discrete_map={"Free": "#4CAF50", "Paid": "#F44336"},
                          title="Free vs Paid")
        st.plotly_chart(fig_free, use_container_width=True)

with col6:
    if "containsAds" in filtered.columns:
        ads_counts = filtered["containsAds"].value_counts().reset_index()
        ads_counts.columns = ["ads", "count"]
        ads_counts["ads"] = ads_counts["ads"].map({True: "Contains Ads", False: "No Ads"})
        fig_ads = px.pie(ads_counts, names="ads", values="count",
                         color="ads",
                         color_discrete_map={"Contains Ads": "#FF9800", "No Ads": "#2196F3"},
                         title="Ads Presence")
        st.plotly_chart(fig_ads, use_container_width=True)

# Price distribution for paid apps
paid = filtered[filtered["free"] == False] if "free" in filtered.columns else pd.DataFrame()
if not paid.empty and "price" in paid.columns:
    st.subheader("Price Distribution (Paid Apps)")
    fig_price = px.histogram(paid, x="price", nbins=10,
                             labels={"price": "Price ($)", "count": "# Apps"})
    st.plotly_chart(fig_price, use_container_width=True)

st.divider()

# 5. Developer dominance 
st.subheader("Developer Dominance")

if "developer" in filtered.columns:
    dev_df = (filtered.groupby("developer")
              .agg(app_count=("title", "count"),
                   avg_rating=("score", "mean"),
                   total_installs=("realInstalls", "sum"))
              .reset_index()
              .sort_values("total_installs", ascending=False)
              .head(10))
    dev_df["avg_rating"] = dev_df["avg_rating"].round(2)

    fig_dev = px.bar(dev_df, x="developer", y="total_installs",
                     color="avg_rating", color_continuous_scale="RdYlGn",
                     range_color=[1, 5],
                     text="app_count",
                     labels={"developer": "Developer", "total_installs": "Total Installs",
                             "avg_rating": "Avg Rating", "app_count": "# Apps"},
                     hover_data={"app_count": True, "avg_rating": True})
    fig_dev.update_traces(texttemplate="%{text} app(s)", textposition="outside")
    fig_dev.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_dev, use_container_width=True)

st.divider()

# 6. Genre landscape 
col7, col8 = st.columns(2)

with col7:
    st.subheader("Genre Distribution")
    genre_counts = filtered["genre"].value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]
    fig_genre = px.bar(genre_counts, x="genre", y="count",
                       labels={"genre": "", "count": "# Apps"})
    fig_genre.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_genre, use_container_width=True)

with col8:
    st.subheader("Avg Rating by Genre")
    if "genre" in filtered.columns and "score" in filtered.columns:
        genre_rating = (filtered.groupby("genre")["score"].mean()
                        .reset_index()
                        .sort_values("score", ascending=False))
        fig_gr = px.bar(genre_rating, x="genre", y="score",
                        color="score", color_continuous_scale="RdYlGn",
                        range_color=[1, 5],
                        labels={"genre": "", "score": "Avg Rating"})
        fig_gr.update_layout(xaxis_tickangle=-30, yaxis_range=[0, 5])
        st.plotly_chart(fig_gr, use_container_width=True)

st.divider()

# 7. Rating distribution 
st.subheader("Rating Distribution")
fig_hist = px.histogram(filtered, x="score", nbins=10, color_discrete_sequence=["#667eea"])
fig_hist.update_layout(xaxis_title="Star Rating", yaxis_title="# Apps")
st.plotly_chart(fig_hist, use_container_width=True)

# Raw data
with st.expander("See raw data table"):
    display_cols = [c for c in ["title", "developer", "genre", "score", "ratings",
                                "installs", "realInstalls", "free", "price", "containsAds"]
                    if c in filtered.columns]
    st.dataframe(filtered[display_cols], use_container_width=True)
