import csv
import base64
import os
import sys  # Import sys module

# Increase CSV field size limit
max_int = sys.maxsize
while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:
        max_int = int(max_int / 10)

# Configuration
csv_file = "baches.csv"
output_dir = "baches_images"  # Changed folder name to avoid conflict with csv file name
max_rows = 10

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Read the CSV and process the first few rows
try:
    with open(csv_file, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        print(f"Reading data from {csv_file}...")

        for i, row in enumerate(reader):
            if i >= max_rows:
                print(f"Processed the first {max_rows} rows.")
                break

            try:
                lat = row["lat"]
                lng = row["lng"]
                img_base64 = row["imagen_base64"]

                # Decode base64 string
                img_data = base64.b64decode(img_base64)

                # Create filename
                filename = f"bache_{lat}_{lng}.png"
                filepath = os.path.join(output_dir, filename)

                # Save image as PNG
                with open(filepath, "wb") as img_file:
                    img_file.write(img_data)

                print(f"Saved image: {filename}")

            except KeyError as e:
                print(f"Skipping row {i+1}: Missing column {e}")
            except base64.binascii.Error as e:
                print(f"Skipping row {i+1} ({lat}, {lng}): Invalid base64 data - {e}")
            except Exception as e:
                print(f"Skipping row {i+1} ({lat}, {lng}): Error processing row - {e}")

        if i < max_rows:
            print(f"Processed all {i+1} rows in the file.")

except FileNotFoundError:
    print(f"Error: CSV file not found at '{csv_file}'")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("Image saving process finished.")
