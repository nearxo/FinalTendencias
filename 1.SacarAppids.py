from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_games_with_selenium(steamid):
    url = f"https://steamid.pro/es/lookup/{steamid}"
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=opts)
    driver.get(url)
    time.sleep(3)  # espera que cargue JS
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table.table-games")
    games = []
    if table:
        for tr in table.select("tbody tr"):
            td = tr.select_one("td")
            if td:
                games.append(td.get_text(strip=True))
    return games
