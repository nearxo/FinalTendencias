import requests
from bs4 import BeautifulSoup
import time
import random
import csv

HEADERS = {"User-Agent": "Mozilla/5.0"}
INPUT_FILE = "steamids.txt"
OUTPUT_FILE = "steam_games.csv"


def get_games_for_id(steamid):
    """Scrapea los nombres de los juegos de un usuario de SteamID.pro"""
    url = f"https://steamid.pro/es/lookup/{steamid}"

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
    except Exception as e:
        print(f"[ERROR] {steamid} -> {e}")
        return []

    if r.status_code != 200:
        print(f"[HTTP {r.status_code}] {steamid}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    games = []

    # Buscar todos los <td class="gname">
    for td in soup.select("td.gname"):
        name = td.get_text(strip=True)
        if name:
            games.append(name)

    if not games:
        print(f"[NO-JUEGOS] {steamid} — perfil privado o sin datos")
    else:
        print(f"[OK] {steamid} — {len(games)} juegos extraídos")

    return games


def scrape_all():
    """Lee steamids.txt y scrapea todos los juegos"""

    # Leer IDs
    with open(INPUT_FILE, "r") as f:
        steamids = [line.strip() for line in f if line.strip()]

    print(f"Cargando {len(steamids)} SteamIDs…\n")

    # Crear CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["steamid", "game"])

        # Scrapeo por cada ID
        for sid in steamids:
            games = get_games_for_id(sid)

            for g in games:
                writer.writerow([sid, g])

            # Delay para evitar bloqueo (random)
            time.sleep(random.uniform(1.2, 2.4))

    print(f"\n✔ Todo listo. Datos guardados en {OUTPUT_FILE}")


if __name__ == "__main__":
    scrape_all()
