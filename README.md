# App Competitor Analysis — Streamlit

A Streamlit application for competitor analysis of mobile apps, built as part of **Lab 2 — Data Applications**.

The application queries the **Google Play Store** based on a search term chosen by the user, retrieves the data of the matching apps (ratings, installs, genre, price) as well as the user reviews, then displays everything as a table and interactive visualizations.

## Features

- **Dynamic search**: the user enters their own search term.
- **Results table**: displays the apps found with their main metrics.
- **Interactive visualizations** (Plotly):
  - Rating distribution
  - Free vs Paid breakdown
  - Top 10 apps by rating
  - Distribution by genre
- **Sidebar filter** to refine the charts by app.
- **User reviews retrieval**, useful for a future sentiment analysis.

## Project structure

​```
STREAMLIT/
├── Home.py                  # Application homepage
├── utils.py                 # Data retrieval functions (Play Store API)
├── pages/
│   ├── 1_Results_Table.py   # Search + results table
│   └── 2_Visualizations.py  # Charts and filters
├── requirements.txt         # Dependencies
└── .gitignore
​```

## Installation and run

1. Clone the repository:
   ​```
   git clone https://github.com/maryem3126-rgb/streamlit.git
   cd streamlit
   ​```

2. Create and activate an environment, then install the dependencies:
   ​```
   pip install -r requirements.txt
   ​```

3. Run the application:
   ​```
   streamlit run Home.py
   ​```

The application opens in the browser at `http://localhost:8501`.

## Technologies

- [Streamlit](https://streamlit.io/) — data application framework
- [google-play-scraper](https://pypi.org/project/google-play-scraper/) — Play Store data extraction
- [Plotly](https://plotly.com/python/) — interactive visualizations
- [pandas](https://pandas.pydata.org/) — data manipulation
