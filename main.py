import os
import sys
from logger import get_len_wm_from_log
from utils import embed_watermark, extract_watermark

# Define directories relative to the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINALS_DIR = os.path.join(BASE_DIR, 'images', 'originals')  # Path to original images
WATERMARKED_DIR = os.path.join(BASE_DIR, 'images', 'watermarked')  # Path to watermarked images
EXTRACTED_DIR = os.path.join(BASE_DIR, 'images', 'extracted')  # Path for extracted images

# Ensure directories exist
os.makedirs(ORIGINALS_DIR, exist_ok=True)
os.makedirs(WATERMARKED_DIR, exist_ok=True)
os.makedirs(EXTRACTED_DIR, exist_ok=True)

# Dictionary to store watermark bit lengths
watermark_lengths = {}

def embed_workflow():
    """Embed watermarks into all images in the originals directory."""
    print("[DEBUG] Starting embedding workflow")
    for image_name in os.listdir(ORIGINALS_DIR):
        if image_name.endswith(('jpg', 'jpeg', 'png')):  # Process only image files
            print(f"[DEBUG] Processing original image: {image_name}")
            len_wm = embed_watermark(image_name, ORIGINALS_DIR, WATERMARKED_DIR)
            watermark_lengths[image_name] = len_wm  # Store watermark bit length
            print(f"[DEBUG] Stored watermark length for {image_name}: {len_wm}")

def extract_workflow():
    """
    Extract watermarks from all watermarked images.
    """
    print("[DEBUG] Starting extraction workflow")

    for watermarked_image_name in os.listdir(WATERMARKED_DIR):
        if watermarked_image_name.endswith(('jpg', 'jpeg', 'png')):
            original_image_name = watermarked_image_name.replace("watermarked_", "")
            print(f"[DEBUG] Processing watermarked image: {watermarked_image_name}")
            
            # Retrieve the watermark bit length from the log
            len_wm = get_len_wm_from_log(original_image_name)
            if len_wm:
                extract_watermark(original_image_name, len_wm, WATERMARKED_DIR)
            else:
                print(f"[DEBUG] Warning: No watermark length found for {original_image_name}, skipping extraction.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <embed|extract>")
        sys.exit(1)

    mode = sys.argv[1].lower()
    if mode == "embed":
        embed_workflow()
    elif mode == "extract":
        extract_workflow()
    else:
        print("Invalid mode. Use 'embed' or 'extract'.")
        sys.exit(1)

if __name__ == "__main__":
    main()