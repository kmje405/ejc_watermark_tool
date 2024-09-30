import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open

# Ensure the project root is included in sys.path before importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import generate_image_hash, embed_watermark, extract_watermark, extract_data_from_watermark


# Test for generate_image_hash
@patch("builtins.open", new_callable=mock_open, read_data=b"fake image data")
def test_generate_image_hash_sha256(mock_file):
    """Test SHA-256 hash generation from an image file"""
    fake_image_path = "test_image.jpg"
    expected_hash = "5b3397652358a6663a0225ee76466d4e4fd6c58d484d1aa25170bb617d6bb086"    
    result_hash = generate_image_hash(fake_image_path, 'sha256')
    
    assert result_hash == expected_hash
    mock_file.assert_called_once_with(fake_image_path, 'rb')

@patch("builtins.open", new_callable=mock_open, read_data=b"fake image data")
def test_generate_image_hash_md5(mock_file):
    """Test MD5 hash generation from an image file"""
    fake_image_path = "test_image.jpg"
    expected_hash = "c72d040ee1fdcd8bce09fc8b6e6c4794"  # Correct hash for the mocked data
    
    result_hash = generate_image_hash(fake_image_path, 'md5')
    
    assert result_hash == expected_hash
    mock_file.assert_called_once_with(fake_image_path, 'rb')


# Test for embed_watermark
@patch("utils.WaterMark")
@patch("utils.log_watermark")
@patch("utils.debug_logger")
@patch("utils.generate_image_hash", return_value="fake_image_hash")
def test_embed_watermark(mock_hash, mock_logger, mock_log_watermark, mock_watermark_class):
    """Test embedding watermark in an image"""
    # Mock WaterMark object behavior
    mock_watermark_instance = mock_watermark_class.return_value
    mock_watermark_instance.wm_bit = 'fake_watermark_bit_string'

    original_image_name = "test_image.jpg"
    originals_dir = "/path/to/originals"
    watermarked_dir = "/path/to/watermarked"
    
    len_wm = embed_watermark(original_image_name, originals_dir, watermarked_dir)
    
    # Verify the watermark is embedded correctly
    mock_watermark_class.return_value.read_img.assert_called_once_with(
        os.path.join(originals_dir, original_image_name)
    )
    mock_watermark_class.return_value.read_wm.assert_called_once()
    mock_watermark_class.return_value.embed.assert_called_once()
    mock_log_watermark.assert_called_once()
    
    # Ensure the length of the watermark bit string is returned
    assert len_wm == len(mock_watermark_instance.wm_bit)


# Test for extract_watermark
@patch("utils.WaterMark")
@patch("utils.log_extraction")
@patch("utils.debug_logger")
@patch("utils.validate_watermark", return_value=True)
def test_extract_watermark_success(mock_validate, mock_logger, mock_log_extraction, mock_watermark_class):
    """Test successful extraction of a watermark from an image"""
    # Mock WaterMark object behavior
    mock_watermark_instance = mock_watermark_class.return_value
    mock_watermark_instance.extract.return_value = "UUID=1234 Folder='test_folder'"
    
    watermarked_image_name = "watermarked_test_image.jpg"
    watermarked_dir = "/path/to/watermarked"
    wm_shape = 1063
    
    extracted_log, validation_status = extract_watermark(watermarked_image_name, wm_shape, watermarked_dir)
    
    # Verify that the extraction process ran correctly
    mock_watermark_class.return_value.extract.assert_called_once()
    mock_log_extraction.assert_called_once()
    
    assert "UUID" in extracted_log
    assert validation_status


@patch("utils.WaterMark")
@patch("utils.debug_logger")
def test_extract_watermark_failure(mock_logger, mock_watermark_class):
    """Test failure in extracting a watermark from an image"""
    # Simulate an exception during extraction
    mock_watermark_instance = mock_watermark_class.return_value
    mock_watermark_instance.extract.side_effect = Exception("Extraction error")
    
    watermarked_image_name = "watermarked_test_image.jpg"
    watermarked_dir = "/path/to/watermarked"
    wm_shape = 1063
    
    extracted_log, validation_status = extract_watermark(watermarked_image_name, wm_shape, watermarked_dir)
    
    # Verify that the extraction failed and the proper error was logged
    assert extracted_log is None
    assert not validation_status
    mock_logger.error.assert_called_once_with("Error during extraction: Extraction error")


# Test for extract_data_from_watermark
def test_extract_data_from_watermark_uuid():
    """Test extracting UUID from a watermark text"""
    watermark_text = "UUID=1234 Folder='test_folder'"
    extracted_uuid = extract_data_from_watermark(watermark_text, "UUID")
    
    assert extracted_uuid == "1234"

def test_extract_data_from_watermark_folder():
    """Test extracting Folder name from a watermark text"""
    watermark_text = "UUID=1234 Folder='test_folder'"
    extracted_folder = extract_data_from_watermark(watermark_text, "Folder")
    
    assert extracted_folder == 'test_folder'

def test_extract_data_from_watermark_invalid():
    """Test extraction when the data type is not present in the watermark text"""
    watermark_text = "UUID=1234 Folder='test_folder'"
    extracted_time = extract_data_from_watermark(watermark_text, "Time")
    
    assert extracted_time is None