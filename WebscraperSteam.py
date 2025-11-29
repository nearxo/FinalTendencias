import requests
import pandas as pd
import time
import random

def get_steam_data(appid):
    """Obtiene datos básicos de un juego de Steam usando su appid."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
    try:
        r = requests.get(url, timeout=10)
        data = r.json().get(str(appid), {}).get("data", {})
        if not data:
            return None
        
        # Extraer los datos deseados
        name = data.get("name", "")
        price = data.get("price_overview", {}).get("final", 0) / 100 if data.get("price_overview") else 0
        genres = [g["description"] for g in data.get("genres", [])]
        platforms = [k for k, v in data.get("platforms", {}).items() if v]
        positive = data.get("recommendations", {}).get("total", 0)  # estimación
        release_date = data.get("release_date", {}).get("date", "")
        
        return {
            "appid": appid,
            "name": name,
            "price": price,
            "genre": ", ".join(genres),
            "platforms": ", ".join(platforms),
            "positive": positive,
            "release_date": release_date
        }
    except Exception as e:
        print(f"⚠️ Error en appid {appid}: {e}")
        return None

# Ejemplo: obtener varios juegos
appids = [570, 440, 730, 578080, 271590]  # Dota 2, TF2, CS2, PUBG, GTA V

steam_games = []
for appid in appids:
    info = get_steam_data(appid)
    if info:
        steam_games.append(info)
    time.sleep(random.uniform(1, 2))  # evitar bloqueo

steam_df = pd.DataFrame(steam_games)
print(steam_df.head())
