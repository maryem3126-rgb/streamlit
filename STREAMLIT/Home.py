import streamlit as st

# Set the browser tab title, icon, and layout. Must be the first
st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("📊 App Competitor Analysis")

st.markdown(
    """
    Welcome! This app lets you explore and compare applications on the
    **Google Play Store** for any search term you choose.

    ### What it does
    - **Results Table** – type a search term and pull live app data
      (ratings, installs, price, genre) from the Play Store.
    - **Visualizations** – charts that turn that data into insight:
      rating distributions, top apps, free-vs-paid breakdown, and more.

    ### How to use it
    1. Open the **Results Table** page from the left sidebar.
    2. Enter a search term (e.g. *note taking ai*, *mental health*) and run the search.
    3. Head to the **Visualizations** page to explore the charts.

    ### Tech
    Built with [Streamlit](https://streamlit.io) and the
    `google-play-scraper` library.

    """
)
# A sidebar note that shows on every page.
st.sidebar.success("Select a page above to begin.")