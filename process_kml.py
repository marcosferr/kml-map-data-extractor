import base64
import csv
import requests
from tqdm import tqdm
from xml.etree import ElementTree as ET

# Cargar y parsear el archivo KML
kml_file = "baches.kml"
tree = ET.parse(kml_file)
root = tree.getroot()

# Manejar namespaces
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

# Crear lista para los datos
data_rows = []

# Buscar todos los placemarks
placemarks = root.findall('.//kml:Placemark', namespace)

for placemark in tqdm(placemarks, desc="Procesando baches"):
    # Extraer coordenadas
    coord_text = placemark.find('.//kml:coordinates', namespace)
    if coord_text is None:
        continue

    coords = coord_text.text.strip().split(',')
    lng, lat = coords[0], coords[1]

    # Buscar la URL de imagen (usamos solo la primera encontrada)
    description = placemark.find('.//kml:description', namespace)
    image_url = None
    if description is not None and "<img src=" in description.text:
        start = description.text.find('<img src="') + len('<img src="')
        end = description.text.find('"', start)
        image_url = description.text[start:end]

    if not image_url:
        continue  # Saltar si no hay imagen

    # Descargar imagen
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Codificar en base64
            img_base64 = base64.b64encode(response.content).decode('utf-8')
            data_rows.append({
                'lat': lat,
                'lng': lng,
                'imagen_base64': img_base64
            })
        else:
            print(f"Error descargando imagen en {lat}, {lng}")
    except Exception as e:
        print(f"Error en descarga: {e}")

# Guardar como CSV
csv_file = "baches.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['lat', 'lng', 'imagen_base64'])
    writer.writeheader()
    for row in data_rows:
        writer.writerow(row)

print(f"\nProceso terminado: {len(data_rows)} baches guardados en '{csv_file}'")
