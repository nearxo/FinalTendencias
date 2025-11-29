import re
import json
import time
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------
# SCRAPER DE METACRITIC (tu función ligeramente mejorada)
# ---------------------------------------------------------

def get_metacritic_score(game_name):
    try:
        query = game_name.lower().strip()
        query = re.sub(r"[^a-z0-9\- ]", "", query)  # quitar símbolos raros
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
        print(f"⚠️ Error con {game_name}: {e}")
        return None

# ---------------------------------------------------------
# PROCESADOR DEL TXT ORIGINAL (SIN CONVERTIRLO)
# ---------------------------------------------------------

def procesar_txt_original(input_file, output_file):
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

            # Detectar nombre del juego - acepta cualquier unicode
            m2 = re.match(r'"game":\s*"(.+)"', linea)
            if m2:
                game_raw = m2.group(1).strip()
                actual["game"] = game_raw

                # cuando ya tenemos appid + game → lo guardamos
                if "appid" in actual:
                    juegos.append(actual)
                    actual = {}

    # -----------------------------------------------------
    # Añadir Metacritic a cada juego
    # -----------------------------------------------------
    salida = open(output_file, "w", encoding="utf-8")

    for j in juegos:
        name = j["game"]
        print(f"📡 Buscando Metacritic de: {name}")

        score = get_metacritic_score(name)
        j["metacritic"] = score

        salida.write(json.dumps(j, ensure_ascii=False) + "\n")
        print(f"✔ {name} → {score}")
        time.sleep(1)

    salida.close()
    print("🎉 Archivo final generado:", output_file)


# ----------------------------
# USO:
# ----------------------------

procesar_txt_original(
    input_file="appid.txt",
    output_file="juegos_metacritic.jsonl"
)
