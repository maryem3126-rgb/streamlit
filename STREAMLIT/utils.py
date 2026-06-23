import pandas as pd
import streamlit as st
from google_play_scraper import search, app, reviews, Sort
def get_app_reviews(app_id, count=50, lang="en", country="us"):
    """
    Recupere jusqu'a `count` avis pour une application donnee.
    Renvoie une liste de dictionnaires (un par avis).
    """
    try:
        result, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count,
            filter_score_with=None,
        )
    except Exception:
        # Si les avis echouent pour une app, on renvoie une liste vide
        # plutot que de faire planter toute la recherche.
        return []

    cleaned = []
    for r in result:
        cleaned.append({
            "userName": r.get("userName"),
            "score": r.get("score"),
            "content": r.get("content"),
            "thumbsUp": r.get("thumbsUpCount"),
            "date": str(r.get("at")),
        })
    return cleaned

@st.cache_data
def get_apps(search_term: str, n_apps: int = 20, reviews_per_app: int = 30,
             country: str = "us", lang: str = "en") -> pd.DataFrame:
    """
    Recherche des apps sur le Play Store pour un terme donne et renvoie
    un DataFrame. Pour chaque app, recupere aussi ses avis (comme au Lab 1).

    Parametres
    ----------
    search_term : str
        Le terme tape par l'utilisateur (recherche dynamique).
    n_apps : int
        Nombre d'apps a recuperer.
    reviews_per_app : int
        Nombre d'avis a recuperer par app (mettre 0 pour ne pas en recuperer).

    Renvoie
    -------
    pd.DataFrame
        Une ligne par app, avec une colonne 'reviews' contenant la liste d'avis.
    """
    # 1. Recherche : liste legere d'apps correspondant au terme.
    results = search(search_term, lang=lang, country=country, n_hits=n_apps)

    # 2. Pour chaque resultat : details complets + avis.
    rows = []
    for r in results:
        try:
            details = app(r["appId"], lang=lang, country=country)
            app_reviews = []
            if reviews_per_app > 0:
                app_reviews = get_app_reviews(
                    r["appId"], count=reviews_per_app, lang=lang, country=country
                )

            rows.append({
                "appId": details.get("appId"),
                "title": details.get("title"),
                "developer": details.get("developer"),
                "genre": details.get("genre"),
                "score": details.get("score"),
                "ratings": details.get("ratings"),
                "reviews": app_reviews,                     # liste des avis
                "reviews_count": len(app_reviews),          # nb d'avis recuperes
                "installs": details.get("installs"),
                "realInstalls": details.get("realInstalls"),
                "free": details.get("free"),
                "price": details.get("price"),
                "containsAds": details.get("containsAds"),
                "description": details.get("description"),
            })
        except Exception as e:
            print(f"App ignoree {r.get('appId')} : {e}")

    df = pd.DataFrame(rows)
    return df
# =====================================================================
# ANALYSE DE SENTIMENT (Section D)
# A coller dans utils.py, AVANT le bloc "if __name__ == '__main__':"
# =====================================================================

# Le modele est charge une seule fois et mis en cache par Streamlit
# (le decorateur @st.cache_resource evite de le recharger a chaque rerun).
# On importe streamlit ici si ce n'est pas deja fait en haut du fichier.
import streamlit as st
from transformers import pipeline


@st.cache_resource
def load_sentiment_model():
    """
    Charge le modele d'analyse de sentiment (une seule fois).
    Modele multilingue : renvoie positive / neutral / negative.
    Le modele se telecharge automatiquement au premier appel.
    """
    return pipeline(
        "sentiment-analysis",
        model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    )


def analyze_reviews_sentiment(reviews_list):
    """
    Prend une liste d'avis (chaque avis est un dict avec une cle 'content')
    et calcule le sentiment de chacun.

    Renvoie la liste des avis enrichie d'un champ 'sentiment'
    (positive / neutral / negative) et 'sentiment_score'.
    """
    model = load_sentiment_model()
    analyzed = []
    for review in reviews_list:
        text = review.get("content")
        if not text:                      # avis sans texte : on saute
            continue
        # Le modele a une limite de longueur : on tronque a 512 caracteres.
        result = model(text[:512])[0]
        analyzed.append({
            **review,                      # garde les champs existants
            "sentiment": result["label"],  # positive / neutral / negative
            "sentiment_score": result["score"],
        })
    return analyzed


def compute_app_sentiment(reviews_list):
    """
    Calcule un score de sentiment GLOBAL pour une application,
    a partir de ses avis analyses.

    Renvoie un dict : nombre de positifs/neutres/negatifs + un score net.
    Le score net = (positifs - negatifs) / total, entre -1 et +1.
    """
    analyzed = analyze_reviews_sentiment(reviews_list)
    if not analyzed:
        return {"positive": 0, "neutral": 0, "negative": 0,
                "net_score": 0, "analyzed_reviews": []}

    pos = sum(1 for r in analyzed if r["sentiment"] == "positive")
    neu = sum(1 for r in analyzed if r["sentiment"] == "neutral")
    neg = sum(1 for r in analyzed if r["sentiment"] == "negative")
    total = len(analyzed)

    net_score = (pos - neg) / total       # entre -1 (tout negatif) et +1 (tout positif)

    return {
        "positive": pos,
        "neutral": neu,
        "negative": neg,
        "total": total,
        "net_score": net_score,
        "analyzed_reviews": analyzed,
    }
if __name__ == "__main__":
    test_df = get_apps("mental health", n_apps=5, reviews_per_app=10)
    print(test_df[["title", "score", "installs", "free", "reviews_count"]])