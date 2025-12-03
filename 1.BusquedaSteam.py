# steam_achievements_continuo.py
import os
import time
import json
import random
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

API_KEY = None  # opcional: tu Steam API key (si la tienes)
OUTPUT_FILE = "appid2.json"
SLEEP_BETWEEN = (1.5, 3.0)  # pausa aleatoria entre peticiones
SAVE_EVERY = 5               # guarda el JSON cada N appids
START_APPID = 1        # valor inicial si no hay archivo previo
MAX_RETRIES = 4
BACKOFF_FACTOR = 2.0

session = requests.Session()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)",
]

def headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept-Language": "es-ES,es;q=0.9"}

def save_json(data):
    tmp = OUTPUT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUTPUT_FILE)

def load_json():
    if not os.path.exists(OUTPUT_FILE):
        return {}
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        logging.warning("No se pudo leer el JSON existente.")
        return {}

def fetch_via_scrape(appid):
    """Scrapea la página de logros de Steam."""
    url = f"https://steamcommunity.com/stats/{appid}/achievements/?l=spanish"
    r = session.get(url, headers=headers(), timeout=20)
    if r.status_code == 404 or "no se han encontrado logros" in r.text.lower():
        return None
    if r.status_code != 200:
        raise requests.HTTPError(f"Status {r.status_code}")
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.text.strip() if soup.title else f"App {appid}"
    achievements = [a.text.strip() for a in soup.select(".achieveTxt h3") if a.text.strip()]
    if not achievements:
        return None
    return {"appid": appid, "game": title, "achievements": achievements}

def try_fetch(appid):
    """Reintenta con backoff exponencial si falla."""
    attempt = 0
    wait = 1.0
    while attempt < MAX_RETRIES:
        try:
            return fetch_via_scrape(appid)
        except Exception as e:
            logging.warning(f"Error {e} en {appid}, reintento {attempt+1}/{MAX_RETRIES}")
            time.sleep(wait + random.random())
            wait *= BACKOFF_FACTOR
            attempt += 1
    logging.error(f"No se pudo obtener {appid} tras {MAX_RETRIES} intentos.")
    return None

def main():
    data = load_json()
    if data:
        processed_ids = [int(k) for k in data.keys() if k.isdigit()]
        start = max(processed_ids) + 1 if processed_ids else START_APPID
        logging.info(f"Continuando desde AppID {start}")
    else:
        start = START_APPID
        logging.info(f"Iniciando desde {start}")

    count = 0
    while True:
        appid = start + count
        if str(appid) in data:
            count += 1
            continue
        logging.info(f"Procesando {appid}...")
        res = try_fetch(appid)
        if res:
            data[str(appid)] = res
            logging.info(f"✅ {res['game']} ({len(res['achievements'])} logros)")
        else:
            data[str(appid)] = {"appid": appid, "found": False}
            logging.info(f"❌ Sin logros ({appid})")

        count += 1
        if count % SAVE_EVERY == 0:
            save_json(data)
            logging.info(f"💾 Progreso guardado ({len(data)} juegos)")

        time.sleep(random.uniform(*SLEEP_BETWEEN))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("⏹ Interrumpido manualmente. Guardando progreso final...")
        # guarda al salir
        try:
            data = load_json()
            save_json(data)
        except Exception:
            pass
        logging.info("Listo. Puedes reanudar cuando quieras.")
