import csv
import base64
import os
import sys
from io import BytesIO
from PIL import Image
from tqdm import tqdm

# Increase CSV field size limit
max_int = sys.maxsize
while True:
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:
        max_int = int(max_int / 10)

# Configuration
input_csv = "baches.csv"
output_csv = "baches_optimized.csv"
max_width = 800  # Maximum width in pixels
image_quality = 85  # JPEG quality (0-100)
batch_size = 10  # Number of rows to process in each batch


def optimize_base64_image(base64_str):
    """Optimize a single base64 image"""
    try:
        # Decode base64 string
        img_data = base64.b64decode(base64_str)

        # Open and process image with PIL
        with Image.open(BytesIO(img_data)) as img:
            # Calculate new dimensions maintaining aspect ratio
            width, height = img.size
            if width > max_width:
                new_height = int((max_width / width) * height)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Save as optimized JPEG to BytesIO object
            output_buffer = BytesIO()
            img.save(output_buffer, format="JPEG", quality=image_quality, optimize=True)

            # Get the base64 string of the optimized image
            optimized_base64 = base64.b64encode(output_buffer.getvalue()).decode(
                "utf-8"
            )

            # Calculate sizes for reporting
            original_size = len(base64_str) * 3 / 4  # Approximate size in bytes
            optimized_size = len(optimized_base64) * 3 / 4

            return (
                optimized_base64,
                original_size / 1024,
                optimized_size / 1024,
            )  # Sizes in KB

    except Exception as e:
        print(f"Error optimizing image: {str(e)}")
        return base64_str, None, None  # Return original if there's an error


def count_rows(csv_file):
    """Count the number of rows in the CSV file"""
    with open(csv_file, "r", newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.reader(f)) - 1  # Subtract 1 for header


def main():
    try:
        # Check if input CSV exists
        if not os.path.exists(input_csv):
            print(f"Error: Input CSV file not found: {input_csv}")
            return

        # Count total rows for progress tracking
        print(f"Counting rows in {input_csv}...")
        total_rows = count_rows(input_csv)
        print(f"Found {total_rows} rows to process")

        # Initialize counters
        total_original_size = 0
        total_optimized_size = 0
        processed_count = 0
        error_count = 0

        # Open input and output CSV files
        with open(input_csv, "r", newline="", encoding="utf-8") as infile, open(
            output_csv, "w", newline="", encoding="utf-8"
        ) as outfile:

            # Set up CSV reader and writer
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            # Process rows with progress bar
            for row_num, row in tqdm(
                enumerate(reader, 1),
                total=total_rows,
                desc="Processing CSV",
                unit="row",
            ):
                try:
                    # Check if the row has the image column
                    if "imagen_base64" not in row or not row["imagen_base64"]:
                        writer.writerow(row)
                        continue

                    # Optimize the image
                    optimized_base64, original_kb, optimized_kb = optimize_base64_image(
                        row["imagen_base64"]
                    )

                    # Update the row with optimized image
                    row["imagen_base64"] = optimized_base64
                    writer.writerow(row)

                    # Update statistics
                    if original_kb is not None and optimized_kb is not None:
                        processed_count += 1
                        total_original_size += original_kb
                        total_optimized_size += optimized_kb

                        # Print info every batch
                        if row_num % batch_size == 0 or row_num == total_rows:
                            reduction = (
                                (original_kb - optimized_kb) / original_kb
                            ) * 100
                            print(f"\nBatch update: Row {row_num}/{total_rows}")
                            print(
                                f"Last image: {original_kb:.1f}KB → {optimized_kb:.1f}KB ({reduction:.1f}% reduction)"
                            )

                except Exception as e:
                    print(f"\nError processing row {row_num}: {str(e)}")
                    error_count += 1
                    # Still write the original row to the output CSV
                    writer.writerow(row)

        # Print summary
        if processed_count > 0:
            total_reduction = (
                (total_original_size - total_optimized_size) / total_original_size
            ) * 100
            print("\nOptimization Summary:")
            print(f"Total images processed: {processed_count}")
            print(f"Total original size: {total_original_size/1024:.2f} MB")
            print(f"Total optimized size: {total_optimized_size/1024:.2f} MB")
            print(
                f"Total space saved: {(total_original_size-total_optimized_size)/1024:.2f} MB ({total_reduction:.1f}%)"
            )

        if error_count > 0:
            print(f"Errors encountered: {error_count}")

        print(f"\nOptimized CSV saved to: {output_csv}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
