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
# 3. Función para insertar CSV en historicoprecios
# ---------------------------------------------
def insertar_csv_precios(csv_file):
    if not os.path.exists(csv_file):
        print(f"❌ El archivo {csv_file} no existe.")
        return

    print("⏳ Iniciando carga de datos a historicoprecios...")

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        contador = 0
        for row in reader:
            try:
                appid = int(row["appid"])
                precio = float(row["precio"]) if row["precio"] else None

                # 🟦 Convertir fecha vacía a NULL
                fecha_raw = row["fecha"].strip()
                fecha = fecha_raw if fecha_raw else None

                reseñas = int(row["reseñas"]) if row["reseñas"] else 0

                cursor.execute("""
                    INSERT INTO historicoprecios (
                        appid, fecha, precio, reseñas
                    ) VALUES (%s, %s, %s, %s)
                    ON CONFLICT (appid, fecha) DO UPDATE SET
                        precio = EXCLUDED.precio,
                        reseñas = EXCLUDED.reseñas;
                """, (appid, fecha, precio, reseñas))

                contador += 1

                if contador % 200 == 0:
                    print(f"   -> {contador} filas procesadas...")

            except Exception as e:
                print(f"⚠️ Error al procesar fila: {row} | Error: {e}")

    conexion.commit()
    print(f"🎉 Carga finalizada. Total procesados: {contador}")

# ---------------------------------------------
# 4. EJECUCIÓN
# ---------------------------------------------
if __name__ == "__main__":
    insertar_csv_precios("juegos_procesados.csv")
    cursor.close()
    conexion.close()
