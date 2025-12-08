import csv
import psycopg2
import os
from dotenv import load_dotenv

# ---------------------------------------------
# 1. Cargar variables .env
# ---------------------------------------------
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("❌ No se encontró DATABASE_URL en el archivo .env")

# ---------------------------------------------
# 2. Conexión a Neon Postgres
# ---------------------------------------------
try:
    conexion = psycopg2.connect(DB_URL)
    cursor = conexion.cursor()
    print("✅ Conexión exitosa a Neon Postgres")
except Exception as e:
    print(f"❌ Error al conectar: {e}")
    exit()


# ---------------------------------------------
# 3. Función para cargar jugadores
# ---------------------------------------------
def insertar_jugadores(csv_file):
    if not os.path.exists(csv_file):
        print(f"❌ El archivo {csv_file} no existe.")
        return

    print("\n⏳ Iniciando carga de datos a la tabla jugadores...")

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contador = 0

        for row in reader:
            try:
                steamid = int(row["steamid"])
                game = int(row["game"])

                cursor.execute("""
                    INSERT INTO jugadores (idjugador, idjuego)
                    VALUES (%s, %s);
                """, (steamid, game))

                contador += 1
                if contador % 200 == 0:
                    print(f"   -> {contador} filas procesadas...")

            except Exception as e:
                print(f"⚠️ Error al procesar fila {row}: {e}")

    conexion.commit()
    print(f"🎉 Carga finalizada. Total procesados: {contador}")


# ---------------------------------------------
# 4. EJECUCIÓN
# ---------------------------------------------
if __name__ == "__main__":
    insertar_jugadores("4.2Jugadores.csv")
    cursor.close()
    conexion.close()
