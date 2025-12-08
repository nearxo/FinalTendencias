# FinalTendencias

Este proyecto recopila, procesa y analiza datos de videojuegos de Steam y Metacritic, incluyendo información de precios, usuarios y logros.

## Flujo de trabajo

1. **Extracción de AppIDs**
   - Obtención de identificadores únicos de juegos de Steam.
2. **Extracción de información de juegos**
   - Recopilación de datos relevantes desde Steam y Metacritic.
3. **Webscraping adicional**
   - Scraping para obtener datos complementarios de los juegos.
4. **Procesamiento de datos importantes**
   - Filtrado y procesamiento de juegos relevantes para el análisis.
5. **Subida y procesamiento de precios**
   - Recopilación y procesamiento del histórico de precios.
6. **Gestión de usuarios**
   - Obtención y procesamiento de datos de usuarios y sus juegos asociados.
7. **Archivos finales y procesados**
   - Generación de archivos finales listos para análisis y visualización.

## Archivos principales

- Scripts numerados según el flujo de trabajo.
- Archivos de datos intermedios y finales en formato `.jsonl` y `.csv`.

## Requisitos

- Python 3.x
- Recomendable usar un entorno virtual (`env/` incluido).

## Ejecución

1. Instala las dependencias necesarias (si las hay).
2. Ejecuta los scripts en el orden sugerido para reproducir el flujo de datos.
