import json
import psycopg2
import os
from dotenv import load_dotenv

# 1. Cargar las variables del archivo .env
load_dotenv()

# 2. Obtener la URL de conexión
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("❌ No se encontró la variable DATABASE_URL en el archivo .env")

# ---------------------------------------------
# CONEXIÓN A NEON (POSTGRES)
# ---------------------------------------------
try:
    # psycopg2 es inteligente y puede leer toda la configuración desde la URL
    conexion = psycopg2.connect(DB_URL)
    cursor = conexion.cursor()
    print("✅ Conexión exitosa a Neon Postgres")

except Exception as e:
    print(f"❌ Error al conectar: {e}")
    exit()

# ---------------------------------------------
# INSERTAR CADA JUEGO DEL JSONL
# ---------------------------------------------
def insertar_en_sql(jsonl_file):
    if not os.path.exists(jsonl_file):
        print(f"❌ El archivo {jsonl_file} no existe.")
        return

    print("⏳ Iniciando inserción de datos...")
    
    with open(jsonl_file, "r", encoding="utf-8") as f:
        contador = 0
        for linea in f:
            try:
                juego = json.loads(linea)
                
                # Convertir lista de plataformas a string si es necesario (JSONB o TEXT)
                # Si tu columna 'platforms' en SQL es TEXT, usa: json.dumps(juego['platforms'])
                
                cursor.execute("""
                    INSERT INTO juegos (
                        appid, nombre, metacritic,
                        generos, plataformas, reseñas_positivas, fecha_salida
                    ) VALUES (
                        %(appid)s, %(game)s, %(metacritic)s,
                        %(genre)s, %(platforms)s, %(positive)s,
                        %(release_date)s
                    )
                    ON CONFLICT (appid) DO UPDATE SET
                        nombre = EXCLUDED.nombre,
                        metacritic = EXCLUDED.metacritic,
                        generos = EXCLUDED.generos,
                        plataformas = EXCLUDED.plataformas,
                        reseñas_positivas = EXCLUDED.reseñas_positivas,
                        fecha_salida = EXCLUDED.fecha_salida;
                """, juego)
                
                contador += 1
                # Opcional: imprimir progreso cada 100 juegos
                if contador % 100 == 0:
                    print(f"   -> Procesados {contador} juegos...")

            except Exception as e:
                print(f"⚠️ Error en la línea {contador + 1}: {e}")
                # connection.rollback() # Descomentar si quieres cancelar todo al primer error

    conexion.commit()
    print(f"🎉 Proceso finalizado. Total insertados/actualizados: {contador}")

# ---------------------------
# EJECUCIÓN
# ---------------------------
if __name__ == "__main__":
    insertar_en_sql("3.juegos_importantes.jsonl")
    cursor.close()
    conexion.close()