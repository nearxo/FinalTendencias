import csv
from some_module import nombre_a_appid  # podría venir de Steam-App-ID-Finder

input_file = "juegos.csv"
output_file = "juegos_con_appid.csv"

with open(input_file, newline='', encoding='utf-8') as f_in, \
     open(output_file, 'w', newline='', encoding='utf-8') as f_out:

    reader = csv.DictReader(f_in)
    fieldnames = ['steamid', 'game', 'appid']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        name = row['game']
        try:
            appid = nombre_a_appid(name)  # función que busca el appid
        except Exception as e:
            appid = None
        writer.writerow({
            'steamid': row['steamid'],
            'game': name,
            'appid': appid
        })
