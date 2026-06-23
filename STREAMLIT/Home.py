import streamlit as st
st.set_page_config(
    page_title="Competitor Analysis",
    layout="wide",
)

st.title("Competitor Analysis")

st.markdown(
    """
    Welcome! This app lets you explore and compare applications on the
    **Google Play Store** for any search term you choose.

    ### What it does
    - **Search** – type a search term and pull live app data
      (ratings, installs, price, genre) from the Play Store.
    - **Visualizations** – charts that turn that data into insight:
      rating distributions, top apps, free-vs-paid breakdown, and more.
    - **Sentiment Analysis** – analyzes user reviews with a Hugging Face
      model to show how users feel about each app.

    ### Key Features
    - Dynamic search: choose any search term you want.
    - Interactive charts: ratings, genres, free vs paid, top apps.
    - Sidebar filter to focus the charts on specific apps.
    - Sentiment analysis on user reviews using a Hugging Face model.

    ### How to improve it
    - Add more data sources (ProductHunt, GitHub).
    - Add richer visualizations (heatmaps, box plots, word clouds).

    """
)
# A sidebar note that shows on every page.
st.sidebar.success("Select a page above to begin.")