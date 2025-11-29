import json
import os
import time
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import psycopg2

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service # Importación añadida
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# ================================
# 1. Config DB NEON
# ================================
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    # Usar un raise más informativo en español
    raise ValueError("❌ No existe DATABASE_URL en .env. Por favor, configura tu URL de conexión a Neon.")

try:
    conexion = psycopg2.connect(DB_URL)
    cursor = conexion.cursor()
    print("✅ Conectado a Neon Postgres")
except psycopg2.Error as e:
    print(f"❌ Error al conectar a Neon Postgres: {e}")
    exit()

# ================================
# 2. Configuración de Selenium
# ================================
def init_driver():
    chrome_options = Options()
    
    # Configuraciones Headless y Anti-detección
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Corrección del error: Usar Service para gestionar la ruta del driver
    service = Service(ChromeDriverManager().install())
    
    # Inicializar el driver usando Service y Options como argumentos de palabra clave
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver


driver = init_driver() # Línea 48 original: Ahora llama a la función corregida


# ================================
# 3. Extraer historial de SteamDB
# ================================
def obtener_historial_precios(appid):
    url = f"https://steamdb.info/app/{appid}/"
    print(f"🌐 Abriendo {url}")

    try:
        driver.get(url)
        time.sleep(random.uniform(2, 4))

        html = driver.page_source

        # Buscar el bloque con "Highcharts.chart"
        match = re.search(r"Highcharts\.chart\([^,]+,\s*(\{.*?series.*?})\);", html, re.S)

        if not match:
            print("❌ No se encontró el bloque Highcharts")
            return []

        chart_config_raw = match.group(1)

        # Extraer lista "data: [...]"
        data_match = re.search(r'"Final price".*?data"\s*:\s*(\[[^\]]+\])', chart_config_raw, re.S)

        if not data_match:
            print("❌ No se encontró la serie 'Final price'")
            return []

        data_json = data_match.group(1).replace("null", "0")

        # 🔥 Convertir a lista Python
        data = json.loads(data_json)

        historial = []

        for timestamp, price in data:
            # timestamp viene en milisegundos
            fecha = datetime.utcfromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")

            historial.append({
                "date": fecha,
                "price": price
            })

        return historial

    except Exception as e:
        print(f"⚠️ Error extrayendo datos Highcharts en {appid}: {e}")
        return []

# ================================
# 4. Guardar historial en SQL Neon
# ================================
def guardar_historial_sql(appid, precios):
    for p in precios:
        try:
            cursor.execute("""
                INSERT INTO precios_historicos (appid, fecha, precio)
                VALUES (%s, %s, %s)
                ON CONFLICT (appid, fecha) DO UPDATE SET
                    precio = EXCLUDED.precio;
            """, (appid, p["date"], p["price"]))
        
        except psycopg2.Error as e: # Capturar error específico de PostgreSQL
            print(f"⚠️ Error guardando precio {appid} - Fecha {p['date']}: {e}")
            # NOTA: No hacemos commit aquí, el commit se hará al final del bucle for, o se podría hacer dentro si se prefiere un commit por registro.

    conexion.commit()
    print(f"💾 Guardados/Actualizados {len(precios)} registros para {appid}")


# ================================
# 5. Proceso principal
# ================================
def procesar_jsonl(jsonl_file):
    if not os.path.exists(jsonl_file):
        print(f"❌ No existe el archivo {jsonl_file}")
        return

    registros_procesados = 0
    with open(jsonl_file, "r", encoding="utf-8") as f:
        for linea in f:
            try:
                juego = json.loads(linea)
                appid = juego["appid"]
            except json.JSONDecodeError:
                print(f"⚠️ Error de formato JSON en la línea: {linea.strip()}")
                continue

            print(f"\n==============================")
            print(f"🎮 Procesando appid: {appid}")
            print(f"==============================")

            precios = obtener_historial_precios(appid)

            if precios:
                print(f"✔ {len(precios)} registros obtenidos de SteamDB")
                guardar_historial_sql(appid, precios)
            else:
                print("❌ Sin datos históricos para guardar")

            time.sleep(random.uniform(2, 5))  # evitar bloqueo
            registros_procesados += 1
            
    print(f"\nProceso finalizado. {registros_procesados} AppIDs procesados.")


# ================================
# 6. Ejecutar
# ================================
if __name__ == "__main__":
    try:
        procesar_jsonl("juegos_final.jsonl")
    except Exception as e:
        print(f"\n🚫 ERROR CRÍTICO EN EL PROCESO PRINCIPAL: {e}")
    finally:
        # Asegurarse de cerrar todo al final
        print("\nCerrando conexiones...")
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conexion' in locals() and conexion:
            conexion.close()
        if 'driver' in globals() and driver:
            driver.quit()
        print("Cerrado.")