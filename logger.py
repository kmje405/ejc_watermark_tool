import logging
import os

# Define log directory
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)  # Ensure the logs directory exists

# Configure the logger for watermark and extraction logs
def setup_logger(name, log_file, level=logging.INFO):
    """
    Sets up a logger with the specified name, log file, and logging level.
    :param name: Name of the logger.
    :param log_file: File where logs will be saved.
    :param level: Logging level (default: INFO).
    """
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Create a file handler to log messages to a file
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Create loggers for different purposes
watermark_logger = setup_logger('watermark', os.path.join(LOG_DIR, 'watermark_log.log'))
extraction_logger = setup_logger('extraction', os.path.join(LOG_DIR, 'extraction_log.log'))
debug_logger = setup_logger('debug', os.path.join(LOG_DIR, 'debug_log.log'), level=logging.DEBUG)

# Log watermarking record
def log_watermark(image_name, uuid, folder, timestamp, len_wm, image_hash):
    """
    Logs information about a watermarked image, including watermark bit length (len_wm) and image hash.
    :param image_name: Name of the image that was watermarked.
    :param uuid: UUID of the image.
    :param folder: Folder where the original image is located.
    :param timestamp: Timestamp when the image was watermarked.
    :param len_wm: Length of the watermark bit string (wm_bit).
    :param image_hash: Hash of the original image (MD5/SHA-256).
    """
    # Store the data in the info log and the debug log for more verbosity
    watermark_logger.info(
        f"Image '{image_name}' was watermarked. UUID={uuid}, Folder='{folder}', Time={timestamp}, len_wm={len_wm}, Hash={image_hash}"
    )
    debug_logger.debug(
        f"Watermarked image: {image_name}, UUID={uuid}, Folder={folder}, Timestamp={timestamp}, len_wm={len_wm}, Hash={image_hash}"
    )
    
# Log extraction record (no changes needed here)
def log_extraction(image_name, watermark_content, timestamp):
    extraction_logger.info(f"Watermark extracted from '{image_name}' at {timestamp}. Content: {watermark_content}")
    debug_logger.debug(f"Extracted watermark from: {image_name}, Content={watermark_content}, Timestamp={timestamp}")

# Function to read the watermark log and retrieve len_wm
def get_len_wm_from_log(image_name):
    """
    Reads the watermark log and retrieves the watermark bit length (len_wm) for a given image.
    :param image_name: The name of the image to retrieve len_wm for.
    :return: The len_wm value, or None if not found.
    """
    log_file_path = os.path.join(LOG_DIR, 'watermark_log.log')
    
    if not os.path.exists(log_file_path):
        return None
    
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if f"Image '{image_name}'" in line:
                # Look for len_wm in the log line
                len_wm_index = line.find("len_wm=")
                if len_wm_index != -1:
                    len_wm_str = line[len_wm_index + len("len_wm="):].strip()
                    return int(len_wm_str)
    
    return None

# Function to validate the extracted watermark data against the log records
# Function to validate the extracted watermark data against the log records
def validate_watermark(uuid):
    """
    Validates extracted watermark based on UUID.
    :param uuid: UUID extracted from the watermark.
    :return: True if validation passes, False otherwise.
    """
    log_file_path = os.path.join(LOG_DIR, 'watermark_log.log')
    
    print(f"[DEBUG] Starting validation for UUID: {uuid}")
    
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if "UUID=" in line:
                log_uuid_start = line.find("UUID=") + len("UUID=")
                log_uuid_end = line.find(" ", log_uuid_start)
                log_uuid = line[log_uuid_start:log_uuid_end].strip(",")  # Strip any trailing commas
                
                # Log the UUID found in the log file
                print(f"[DEBUG] Found UUID in log: {log_uuid}")
                
                if log_uuid == uuid:
                    print(f"[VALIDATION SUCCESS] Extracted UUID matches log UUID: {uuid}")
                    return True
    
    print(f"[VALIDATION FAILURE] No matching UUID found in log for extracted UUID: {uuid}")
    return False