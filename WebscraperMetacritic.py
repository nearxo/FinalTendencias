import requests
from bs4 import BeautifulSoup
import re

def get_metacritic_score(game_name):
    """Busca la puntuación de un juego en Metacritic."""
    try:
        query = game_name.lower().replace(" ", "-")
        url = f"https://www.metacritic.com/game/pc/{query}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        score_tag = soup.find("div", class_="c-siteReviewScore")
        if score_tag:
            score = int(re.findall(r"\d+", score_tag.text.strip())[0])
            return score
        return None
    except Exception as e:
        print(f"⚠️ Error al obtener Metacritic de {game_name}: {e}")
        return None

# Ejemplo
score = get_metacritic_score("Grand Theft Auto V")
print("Metacritic:", score)
