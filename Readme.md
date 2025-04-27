# Baches Encarnación - Procesamiento de Datos KML

Este repositorio contiene scripts de Python para procesar un archivo KML que mapea baches en la ciudad de Encarnación, Paraguay. Los scripts extraen información geográfica e imágenes asociadas, las procesan y las optimizan.

## Créditos y Origen de los Datos

El relevamiento original de los datos de baches fue un esfuerzo comunitario documentado en Google My Maps y dado a conocer a través de Facebook.

- **Mapa Original (Google My Maps):** [Baches Encarnación](https://www.google.com/maps/d/u/0/viewer?mid=1sy8YNRV4M9OyMhqNLW8brI4SIoPJByo&ll=-27.336907276912186%2C-55.86546630000001&z=15)
- **Publicación Original (Facebook):** [Post de Juan Schmalko](https://www.facebook.com/juan.schmalko/posts/pfbid02UPggRrrCVfRokSFvDkMwFYCtDKzRBK5mW4xvP818VNBoEQUt48QoKg4C41v3nKhLl)

## Scripts y Uso

### 1. `process_kml.py`

- **Propósito:** Extrae datos de coordenadas (latitud, longitud) e imágenes de los `Placemark` dentro del archivo `baches.kml`.
- **Funcionamiento:**
  1.  Parsea el archivo `baches.kml`.
  2.  Para cada `Placemark`, extrae las coordenadas.
  3.  Busca la URL de la imagen dentro de la etiqueta `<description>`.
  4.  Descarga la imagen desde la URL encontrada.
  5.  Codifica el contenido de la imagen descargada en formato Base64.
  6.  Guarda la latitud, longitud y la cadena Base64 de la imagen en un archivo CSV llamado `baches.csv`.
- **Uso:** Ejecutar el script directamente.
  ```bash
  python process_kml.py
  ```
- **Salida:** `baches.csv`

### 2. `read_and_save_images.py`

- **Propósito:** Decodifica las imágenes Base64 del archivo `baches.csv` y las guarda como archivos de imagen individuales. Es útil para verificar visualmente que la extracción de imágenes del KML fue correcta.
- **Funcionamiento:**
  1.  Lee el archivo `baches.csv`.
  2.  Para un número limitado de filas (configurable con `max_rows`), decodifica la cadena Base64 de la columna `imagen_base64`.
  3.  Guarda la imagen decodificada como un archivo PNG en el directorio `baches_images`.
  4.  El nombre del archivo sigue el formato `bache_{lat}_{lng}.png`.
- **Uso:** Ejecutar el script directamente. Asegúrate de que `baches.csv` exista.
  ```bash
  python read_and_save_images.py
  ```
- **Salida:** Archivos PNG en la carpeta `baches_images`.

### 3. `optimize_csv_images.py`

- **Propósito:** Optimiza las imágenes codificadas en Base64 dentro del archivo `baches.csv` para reducir el tamaño total del archivo CSV.
- **Funcionamiento:**
  1.  Lee el archivo `baches.csv`.
  2.  Para cada fila, decodifica la imagen Base64.
  3.  Utiliza la librería PIL (Pillow) para:
      - Redimensionar la imagen si su ancho supera un máximo (`max_width`), manteniendo la proporción.
      - Convertir la imagen a formato RGB (si es necesario).
      - Guardar la imagen como JPEG optimizado con una calidad específica (`image_quality`) en un buffer en memoria.
  4.  Codifica la imagen JPEG optimizada de nuevo a Base64.
  5.  Escribe la fila original, pero reemplazando la cadena Base64 original por la optimizada, en el archivo `baches_optimized.csv`.
- **Uso:** Ejecutar el script directamente. Asegúrate de que `baches.csv` exista.
  ```bash
  python optimize_csv_images.py
  ```
- **Salida:** `baches_optimized.csv` (con imágenes Base64 más pequeñas).

### 4. `optimize_images.py`

- **Propósito:** Optimiza archivos de imagen individuales (no Base64 en CSV) que se encuentran en un directorio.
- **Funcionamiento:**
  1.  Busca archivos de imagen (`.png`, `.jpg`, `.jpeg`) en el directorio de entrada (`input_dir`, por defecto `baches_images`).
  2.  Para cada imagen, utiliza PIL (Pillow) para:
      - Redimensionar la imagen si su ancho supera un máximo (`max_width`), manteniendo la proporción.
      - Convertir la imagen a formato RGB (si es necesario).
      - Guardar la imagen como JPEG optimizado con una calidad específica (`image_quality`) en el directorio de salida (`output_dir`, por defecto `baches_images_optimized`).
  3.  Utiliza procesamiento en paralelo (`concurrent.futures`) para acelerar la optimización.
- **Uso:** Ejecutar el script directamente. Asegúrate de que el directorio de entrada (`baches_images`) exista y contenga imágenes.
  ```bash
  python optimize_images.py
  ```
- **Salida:** Archivos JPEG optimizados en la carpeta `baches_images_optimized`.

## Flujo de Trabajo Sugerido

1.  **Extraer datos del KML:** Ejecuta `process_kml.py` para generar `baches.csv`.
2.  **(Opcional) Verificar Imágenes:** Ejecuta `read_and_save_images.py` para guardar algunas imágenes como archivos y comprobar que se extrajeron correctamente.
3.  **Optimizar CSV:** Ejecuta `optimize_csv_images.py` para crear `baches_optimized.csv`, una versión más ligera del archivo CSV con imágenes optimizadas incrustadas en Base64. Este archivo es probablemente el más útil para aplicaciones posteriores que necesiten los datos y las imágenes de forma compacta.
4.  **(Alternativa) Optimizar Archivos de Imagen:** Si has usado `read_and_save_images.py` y prefieres tener las imágenes como archivos separados optimizados, ejecuta `optimize_images.py` sobre la carpeta `baches_images`.
