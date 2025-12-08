import re
import json
import time
import random
import requests
import csv
from bs4 import BeautifulSoup

# --------------------------------------------------------------------
# METACRITIC SCRAPER
# --------------------------------------------------------------------

def get_metacritic_score(game_name):
    try:
        query = game_name.lower().strip()
        query = re.sub(r"[^a-z0-9\- ]", "", query)
        query = query.replace(" ", "-")

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
        print(f"⚠️ Error Metacritic {game_name}: {e}")
        return None

# --------------------------------------------------------------------
# STEAM API SCRAPER
# --------------------------------------------------------------------

def get_steam_data(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=us&l=en"
    try:
        r = requests.get(url, timeout=10)
        data = r.json().get(str(appid), {}).get("data", {})
        if not data:
            return None
        
        name = data.get("name", "")
        price = data.get("price_overview", {}).get("final", 0) / 100 if data.get("price_overview") else 0
        genres = [g["description"] for g in data.get("genres", [])]
        platforms = [k for k, v in data.get("platforms", {}).items() if v]
        positive = data.get("recommendations", {}).get("total", 0)
        release_date = data.get("release_date", {}).get("date", "")

        return {
            "steam_name": name,
            "game": name,  # ← sirve para Metacritic
            "price": price,
            "genre": ", ".join(genres),
            "platforms": ", ".join(platforms),
            "positive": positive,
            "release_date": release_date
        }
    except Exception as e:
        print(f"⚠️ Error Steam appid {appid}: {e}")
        return None


# --------------------------------------------------------------------
# PROCESAR CSV SOLO CON AppID
# --------------------------------------------------------------------

def procesar_csv_unificado(csv_file, output_file):
    juegos = []

    # Leer solo columna AppID
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                juegos.append({"appid": int(row["AppID"])})
            except Exception as e:
                print(f"⚠️ Error leyendo fila CSV {row}: {e}")

    procesar_juegos(juegos, output_file)


# --------------------------------------------------------------------
# PROCESAR LISTA DE JUEGOS
# --------------------------------------------------------------------

def procesar_juegos(juegos, output_file):

    salida = open(output_file, "w", encoding="utf-8")

    for j in juegos:
        appid = j["appid"]

        print(f"\n==============================")
        print(f"📌 Procesando AppID: {appid}")

        # STEAM → primero, para obtener el nombre
        steam_info = get_steam_data(appid)
        if steam_info:
            j.update(steam_info)
            print(f"🟦 Steam OK → {steam_info.get('steam_name')}")
        else:
            print("⚠️ Steam sin datos, NO se puede buscar en Metacritic")
            salida.write(json.dumps(j, ensure_ascii=False) + "\n")
            continue

        # METACRITIC → usando el nombre real del juego
        game_name = j["game"]
        meta_score = get_metacritic_score(game_name)
        j["metacritic"] = meta_score
        print(f"⭐ Metacritic → {meta_score}")

        # Guardar JSONL
        salida.write(json.dumps(j, ensure_ascii=False) + "\n")

        # Anti-baneo
        time.sleep(random.uniform(1.0, 2.0))

    salida.close()
    print("\n🎉 Archivo generado:", output_file)


# -----------------------
# EJEMPLO DE USO
# -----------------------

# Para CSV con 1 columna AppID:
procesar_csv_unificado("unique_appids.csv", "juegos_importantes.jsonl")
