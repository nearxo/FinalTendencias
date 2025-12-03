import re
import json
import time
import random
import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------
# METACRITIC SCRAPER
# --------------------------------------------------------------------

def get_metacritic_score(game_name):
    try:
        # Normalizar para URL de Metacritic
        query = game_name.lower().strip()
        query = re.sub(r"[^a-z0-9\- ]", "", query)  # quitar símbolos no latinos para metacritic
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
# PROCESA TU TXT EXACTAMENTE COMO ESTÁ
# --------------------------------------------------------------------

def procesar_txt_unificado(input_file, output_file):

    juegos = []
    actual = {}

    with open(input_file, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()

            # Detectar appid
            m1 = re.match(r'"appid":\s*(\d+)', linea)
            if m1:
                actual["appid"] = int(m1.group(1))
                continue

            # Detectar game, acepta caracteres Unicode
            m2 = re.match(r'"game":\s*"(.+)"', linea)
            if m2:
                game_raw = m2.group(1).strip()
                actual["game"] = game_raw

                # cuando ya tenemos juego completo → lo guardamos
                if "appid" in actual:
                    juegos.append(actual)
                    actual = {}

    # Ahora combinamos datos Steam + Metacritic
    salida = open(output_file, "w", encoding="utf-8")

    for j in juegos:
        appid = j["appid"]
        game_name = j["game"]

        print(f"\n==============================")
        print(f"📌 Procesando: {appid} | {game_name}")

        # METACRITIC
        meta_score = get_metacritic_score(game_name)
        j["metacritic"] = meta_score
        print(f"⭐ Metacritic → {meta_score}")

        # STEAM
        steam_info = get_steam_data(appid)
        if steam_info:
            j.update(steam_info)
            print(f"🟦 Steam OK → {steam_info.get('steam_name')}")
        else:
            print("⚠️ Steam sin datos")

        # Guardar línea JSONL final
        salida.write(json.dumps(j, ensure_ascii=False) + "\n")

        # Pausa para evitar bloqueos
        time.sleep(random.uniform(1, 2))

    salida.close()
    print("\n🎉 Archivo generado:", output_file)


# -----------------------
# USO
# -----------------------

procesar_txt_unificado(
    input_file="appid.txt",
    output_file="juegos_final11302025.jsonl"
)
