import pandas as pd
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

if __name__ == "__main__":
    test_df = get_apps("mental health", n_apps=5, reviews_per_app=10)
    print(test_df[["title", "score", "installs", "free", "reviews_count"]])