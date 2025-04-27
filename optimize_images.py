import os
import sys
from PIL import Image
from tqdm import tqdm
import concurrent.futures

# Configuration
input_dir = "baches_images"
output_dir = "baches_images_optimized"
max_width = 800  # Maximum width in pixels
image_quality = 85  # JPEG quality (0-100)
batch_size = 10  # Number of images to process in each batch
num_workers = 4  # Number of parallel workers

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")


def optimize_image(img_path):
    """Resize and optimize a single image"""
    try:
        # Get filename and create output path
        filename = os.path.basename(img_path)
        output_filename = os.path.splitext(filename)[0] + ".jpg"
        output_path = os.path.join(output_dir, output_filename)

        # Skip if already processed
        if os.path.exists(output_path):
            return None, None, f"Skipped (already exists): {filename}"

        # Open and process image
        with Image.open(img_path) as img:
            # Calculate new dimensions maintaining aspect ratio
            width, height = img.size
            if width > max_width:
                new_height = int((max_width / width) * height)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

            # Convert to RGB if necessary
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            # Save as optimized JPEG
            img.save(output_path, "JPEG", quality=image_quality, optimize=True)

        # Get file sizes
        original_size = os.path.getsize(img_path) / 1024  # KB
        new_size = os.path.getsize(output_path) / 1024  # KB

        return original_size, new_size, filename

    except Exception as e:
        return None, None, f"Error processing {os.path.basename(img_path)}: {str(e)}"


def main():
    # Get list of all images
    all_images = []
    for filename in os.listdir(input_dir):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            all_images.append(os.path.join(input_dir, filename))

    total_images = len(all_images)
    if total_images == 0:
        print("No images found to process.")
        return

    print(f"Found {total_images} images to process")
    print(f"Processing in batches of {batch_size} using {num_workers} parallel workers")

    # Initialize counters
    total_original_size = 0
    total_new_size = 0
    processed_count = 0
    error_count = 0

    # Process in batches
    for i in range(0, total_images, batch_size):
        batch = all_images[i : i + batch_size]

        print(
            f"\nProcessing batch {i//batch_size + 1}/{(total_images + batch_size - 1)//batch_size}"
        )

        # Process batch in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(
                tqdm(
                    executor.map(optimize_image, batch),
                    total=len(batch),
                    desc="Optimizing images",
                    unit="img",
                )
            )

        # Process results
        for original_size, new_size, msg in results:
            if original_size is not None and new_size is not None:
                reduction = ((original_size - new_size) / original_size) * 100
                print(
                    f"Optimized: {msg} - {original_size:.1f}KB → {new_size:.1f}KB ({reduction:.1f}% reduction)"
                )
                total_original_size += original_size
                total_new_size += new_size
                processed_count += 1
            else:
                print(msg)
                if "Error" in msg:
                    error_count += 1

    # Print summary
    if processed_count > 0:
        total_reduction = (
            (total_original_size - total_new_size) / total_original_size
        ) * 100
        print("\nSummary:")
        print(f"Total images processed: {processed_count}")
        print(f"Total original size: {total_original_size/1024:.2f} MB")
        print(f"Total optimized size: {total_new_size/1024:.2f} MB")
        print(
            f"Total space saved: {(total_original_size-total_new_size)/1024:.2f} MB ({total_reduction:.1f}%)"
        )

    if error_count > 0:
        print(f"Errors encountered: {error_count}")


if __name__ == "__main__":
    main()
