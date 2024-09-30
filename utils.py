import hashlib
import os
from blind_watermark import WaterMark
from datetime import datetime
import uuid
from logger import log_watermark, log_extraction, debug_logger, validate_watermark

def generate_image_hash(image_path, hash_algorithm='sha256'):
    """
    Generate a hash of the original image using the specified algorithm (MD5/SHA-256).
    :param image_path: Path to the image file.
    :param hash_algorithm: Hashing algorithm to use ('md5' or 'sha256'). Default is 'sha256'.
    :return: Hexadecimal hash of the image.
    """
    hash_func = hashlib.sha256() if hash_algorithm.lower() == 'sha256' else hashlib.md5()

    # Read the image in binary mode and update the hash function with its content
    with open(image_path, 'rb') as img_file:
        while chunk := img_file.read(8192):  # Read the image in chunks
            hash_func.update(chunk)
    
    # Return the hexadecimal digest of the hash
    return hash_func.hexdigest()

# Utility function to embed a watermark into an image
def embed_watermark(image_name, originals_dir, watermarked_dir):
    """
    Embed a watermark in an image using the original folder name, UUID, and timestamp in a log format.
    Also generates and logs the hash of the original image.
    """
    debug_logger.debug(f"Embedding watermark in {image_name}")
    
    # File paths
    original_image_path = os.path.join(originals_dir, image_name)
    watermarked_image_path = os.path.join(watermarked_dir, f"watermarked_{image_name}")

    debug_logger.debug(f"Original image path: {original_image_path}")
    debug_logger.debug(f"Watermarked image will be saved to: {watermarked_image_path}")
    
    # Capture the folder name where the originals came from
    folder_name = os.path.basename(os.path.dirname(original_image_path))

    # Generate UUID and timestamp
    image_uuid = uuid.uuid1()  # Generate a unique UUID for the image
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current timestamp

    # Log-like watermark text including folder name, UUID, and timestamp
    watermark_text = (
        f"[{timestamp}] [WATERMARK EMBED] UUID={image_uuid} Folder='{folder_name}' Message='Image was watermarked.'"
    )

    debug_logger.debug(f"Watermark text (log style): {watermark_text}")

    # Initialize the WaterMark object
    bwm1 = WaterMark(password_img=1, password_wm=1)

    # Read the original image and embed the watermark text
    bwm1.read_img(original_image_path)
    bwm1.read_wm(watermark_text, mode='str')  # Embed the watermark as a string

    # Embed the watermark into the image and save the watermarked image
    bwm1.embed(watermarked_image_path)
    debug_logger.debug(f"Watermarked image saved at: {watermarked_image_path}")

    # Get the length of the watermark bit string (len_wm)
    len_wm = len(bwm1.wm_bit)

    # Generate and log the hash of the original image
    image_hash = generate_image_hash(original_image_path, 'sha256')
    debug_logger.debug(f"Generated SHA-256 hash for {image_name}: {image_hash}")

    # Log the watermarking event, including the watermark bit length and image hash
    log_watermark(image_name, image_uuid, folder_name, timestamp, len_wm, image_hash)

    return len_wm

# Utility function to extract a watermark from a watermarked image
def extract_watermark(image_name, wm_shape, watermarked_dir):
    """
    Extract the watermark from a watermarked image and return it in a log format.
    :param image_name: Name of the watermarked image file.
    :param wm_shape: Length of the watermark bit string (wm_bit) to aid extraction.
    :param watermarked_dir: Path to the watermarked images directory.
    """
    debug_logger.debug(f"Extracting watermark from {image_name}")

    # Check if the image name is already prefixed with "watermarked_"
    if not image_name.startswith("watermarked_"):
        watermarked_image_name = f"watermarked_{image_name}"
    else:
        watermarked_image_name = image_name

    # File path of the watermarked image
    watermarked_image_path = os.path.join(watermarked_dir, watermarked_image_name)
    
    debug_logger.debug(f"Watermarked image path: {watermarked_image_path}")
    
    # Initialize the WaterMark object for extraction
    bwm1 = WaterMark(password_img=1, password_wm=1)

    # Extract the watermark from the watermarked image
    try:
        wm_extract = bwm1.extract(watermarked_image_path, wm_shape=wm_shape, mode='str')
    except Exception as e:
        debug_logger.error(f"Error during extraction: {str(e)}")
        return None, False

    # Adjust extracted watermark to follow log format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Timestamp for extraction log
    extracted_log = f"[{timestamp}] [WATERMARK EXTRACT] Extracted Watermark: {wm_extract}"

    # Log the extraction event
    log_extraction(image_name, wm_extract, timestamp)

    # Parse extracted watermark for validation (assuming the watermark contains "UUID=")
    extracted_uuid = extract_data_from_watermark(wm_extract, "UUID")

    # Validate against log records using only the UUID
    validation_status = validate_watermark(extracted_uuid)

    if validation_status:
        debug_logger.debug(f"Validation successful for UUID: {extracted_uuid}")
    else:
        debug_logger.debug(f"Validation failed for UUID: {extracted_uuid}")

    return extracted_log, validation_status  # Return the log-formatted extracted watermark and validation status
# Helper function to extract specific data from the watermark text (e.g., UUID, folder, time)
def extract_data_from_watermark(watermark_text, data_type):
    """
    Extract specific information (e.g., UUID, Folder, Timestamp) from the watermark text.
    :param watermark_text: The extracted watermark text.
    :param data_type: The type of data to extract (e.g., "UUID", "Folder", "Time").
    :return: The extracted value.
    """
    if data_type in watermark_text:
        start_idx = watermark_text.find(data_type) + len(data_type) + 1
        end_idx = watermark_text.find(" ", start_idx)
        return watermark_text[start_idx:end_idx].strip()
    return None

