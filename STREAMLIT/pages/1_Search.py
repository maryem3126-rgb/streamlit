import streamlit as st
from utils import get_apps

st.title("Search Results")

# USER INPUT
search_term = st.text_input(
    "Enter a search term",
    value="note taking ai",
    help="e.g. note taking ai, mental health, language learning",
)

# Let the user control how many apps to pull (more = slower).
n_apps = st.slider("Number of apps to fetch", min_value=5, max_value=50, value=20)


# RUN THE SEARCH
if st.button("Search"):
    with st.spinner(f"Fetching apps for '{search_term}'..."):
        df = get_apps(search_term, n_apps=n_apps)

  
    st.session_state["data"] = df
    st.session_state["search_term"] = search_term
    st.success(f"Found {len(df)} apps for '{search_term}'")

# DISPLAY
if "data" in st.session_state:
    df = st.session_state["data"]

    st.subheader(f"Results for '{st.session_state['search_term']}'")

    # Show the most useful columns as an interactive table.
    st.dataframe(
        df[["title", "developer", "genre", "score", "installs", "free", "price"]],
        use_container_width=True,
    )

    st.caption("Now open the Visualizations page from the sidebar →")
else:
    # Friendly prompt before any search has run.
    st.info("Enter a search term above and click **Search** to begin.")