import requests
import time
import random

def obtener_historial_precios(appid):
    url = f"https://steamcharts.com/app/{appid}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print(f"❌ No hay historial para appid {appid}")
            return []

        print(f"✅ Historial obtenido para appid {appid}")
    
    except Exception as e:
        print(f"⚠️ Error historial appid {appid}: {e}")
        return []

obtener_historial_precios(570)  # Ejemplo con Dota 2