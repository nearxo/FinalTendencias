import random

processed_records = []

for game in games_data:
    # 3. Extract appid
    appid = game.get('appid', None)

    # 4. Extract original price (precio) and release_date (fecha)
    original_price_raw = game.get('price', 0.0)
    try:
        original_precio = float(original_price_raw)
    except (ValueError, TypeError):
        original_precio = 0.0

    fecha = game.get('release_date', None)

    # 5. Calculate reseñas (total reviews)
    positive_reviews = game.get('positive', 0)
    negative_reviews = game.get('negative', 0)
    # Ensure reviews are numeric, default to 0 if not
    try:
        positive_reviews = int(positive_reviews)
    except (ValueError, TypeError):
        positive_reviews = 0
    try:
        negative_reviews = int(negative_reviews)
    except (ValueError, TypeError):
        negative_reviews = 0

    reseñas = positive_reviews + negative_reviews

    # 6. Create the first record
    record1 = {
        'appid': appid,
        'precio': round(original_precio, 2),
        'fecha': fecha,
        'reseñas': reseñas
    }
    processed_records.append(record1)

    # 7. Generate discounted_price for the second record
    discounted_price = 0.0
    if original_precio > 0:
        discount_percentage = random.uniform(0.10, 0.50) # 10% to 50% discount
        discounted_price = original_precio * (1 - discount_percentage)
        if discounted_price < 0: # Ensure price is not negative after discount
            discounted_price = 0.0

    # 8. Create the second record (with discounted price)
    record2 = {
        'appid': appid,
        'precio': round(discounted_price, 2),
        'fecha': fecha,
        'reseñas': reseñas
    }
    processed_records.append(record2)

    # 9. Create the third record (identical to the first)
    record3 = {
        'appid': appid,
        'precio': round(original_precio, 2),
        'fecha': fecha,
        'reseñas': reseñas
    }
    processed_records.append(record3)

print(f"Generated {len(processed_records)} records from {len(games_data)} game entries.")
if processed_records:
    print("First 3 processed records:")
    for i in range(3):
        print(processed_records[i])
        
import pandas as pd

# Convert the list of processed records into a pandas DataFrame
df_processed_games = pd.DataFrame(processed_records)
df_processed_games.to_csv('juegos_procesados.csv', index=False)