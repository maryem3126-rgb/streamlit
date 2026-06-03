# pages/2_Visualizations.py
# Page 2: turn the search results (stored in session state by page 1)
# into charts. Includes a sidebar filter and several chart types.

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📈 Visualizations")

# ----------------------------------------------------------------------
# GUARD: this page needs data from page 1. If the user lands here first,
# session state won't have "data" yet, so we stop early with a message.
# ----------------------------------------------------------------------
if "data" not in st.session_state:
    st.warning("No data yet. Go to the **Results Table** page and run a search first.")
    st.stop()   # halts the script here, so the rest doesn't run on empty data

# Read the data page 1 saved. .copy() so our edits don't affect the stored version.
df = st.session_state["data"].copy()
search_term = st.session_state.get("search_term", "your search")

st.caption(f"Showing analysis for: **{search_term}**")

# ----------------------------------------------------------------------
# SIDEBAR FILTER (required by the lab)
# Let the user narrow the data by app (using the title here, which is
# friendlier than the raw appId). The charts below all use the filtered df.
# ----------------------------------------------------------------------
st.sidebar.header("Filters")

all_apps = df["title"].dropna().tolist()
selected = st.sidebar.multiselect(
    "Filter by app",
    options=all_apps,
    default=all_apps,        # default: show everything
)

# Apply the filter. If nothing selected, keep all to avoid an empty chart.
filtered = df[df["title"].isin(selected)] if selected else df

# ----------------------------------------------------------------------
# LAYOUT: two charts side by side using columns
# ----------------------------------------------------------------------
col1, col2 = st.columns(2)

# --- Chart 1: Rating distribution (histogram) ---
with col1:
    st.subheader("Rating distribution")
    fig_hist = px.histogram(filtered, x="score", nbins=10)
    fig_hist.update_layout(xaxis_title="Star rating", yaxis_title="Number of apps")
    st.plotly_chart(fig_hist, width="stretch")

# --- Chart 2: Free vs Paid (pie) ---
with col2:
    st.subheader("Free vs Paid")
    # Count how many are free/paid, then plot as a pie.
    free_counts = filtered["free"].value_counts().reset_index()
    free_counts.columns = ["free", "count"]
    free_counts["free"] = free_counts["free"].map({True: "Free", False: "Paid"})
    fig_pie = px.pie(free_counts, names="free", values="count")
    st.plotly_chart(fig_pie, width="stretch")

# --- Chart 3: Top apps by rating (horizontal bar) ---
st.subheader("Top 10 apps by rating")
top = filtered.sort_values("score", ascending=False).head(10)
fig_bar = px.bar(top, x="score", y="title", orientation="h")
fig_bar.update_layout(yaxis={"categoryorder": "total ascending"},
                      xaxis_title="Rating", yaxis_title="")
st.plotly_chart(fig_bar, width="stretch")

# --- Chart 4: Genre distribution (bar) ---
st.subheader("Apps by genre")
genre_counts = filtered["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]
fig_genre = px.bar(genre_counts, x="genre", y="count")
fig_genre.update_layout(xaxis_title="", yaxis_title="Number of apps")
st.plotly_chart(fig_genre, width="stretch")

# Show the filtered data in an expander, so it's available but not cluttering.
with st.expander("See the filtered data table"):
    st.dataframe(filtered, width="stretch")