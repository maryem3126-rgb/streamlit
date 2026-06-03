# App Competitor Analysis — Streamlit

Application Streamlit d'analyse concurrentielle d'applications mobiles, construite dans le cadre du **Lab 2 — Data Applications**.

L'application interroge le **Google Play Store** à partir d'un terme de recherche choisi par l'utilisateur, récupère les données des applications correspondantes (notes, installations, genre, prix) ainsi que les avis des utilisateurs, puis présente le tout sous forme de tableau et de visualisations interactives.

## Fonctionnalités

- **Recherche dynamique** : l'utilisateur saisit son propre terme de recherche.
- **Tableau de résultats** : affichage des applications trouvées avec leurs principales métriques.
- **Visualisations interactives** (Plotly) :
  - Distribution des notes
  - Répartition gratuit / payant
  - Top 10 des applications par note
  - Répartition par genre
- **Filtre latéral** pour affiner les graphiques par application.
- **Récupération des avis** des utilisateurs, utile pour une future analyse de sentiment.

## Structure du projet

```
STREAMLIT/
├── Home.py                  # Page d'accueil de l'application
├── utils.py                 # Fonctions de récupération des données (API Play Store)
├── pages/
│   ├── 1_Results_Table.py   # Recherche + tableau des résultats
│   └── 2_Visualizations.py  # Graphiques et filtres
├── requirements.txt         # Dépendances
└── .gitignore
```

## Installation et lancement

1. Cloner le dépôt :
   ```
   git clone https://github.com/maryem3126-rgb/streamlit.git
   cd streamlit
   ```

2. Créer et activer un environnement, puis installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

3. Lancer l'application :
   ```
   streamlit run Home.py
   ```

L'application s'ouvre dans le navigateur à l'adresse `http://localhost:8501`.

## Technologies

- [Streamlit](https://streamlit.io) — framework d'application de données
- [google-play-scraper](https://pypi.org/project/google-play-scraper/) — extraction des données du Play Store
- [Plotly](https://plotly.com/python/) — visualisations interactives
- [pandas](https://pandas.pydata.org/) — manipulation des données


