import sys
import pytest
import os
from unittest.mock import patch, MagicMock
import main  # Import the entire main module to access variables like directories and functions

# Use the same paths as in main.py
ORIGINALS_DIR = main.ORIGINALS_DIR
WATERMARKED_DIR = main.WATERMARKED_DIR


# Test for embed_workflow
@patch("main.embed_watermark")
@patch("main.os.listdir", return_value=["test_image1.jpg", "test_image2.png"])
@patch("main.os.makedirs")  # Mock os.makedirs to prevent actual directory creation
def test_embed_workflow(mock_makedirs, mock_listdir, mock_embed_watermark):
    """Test embedding watermarks for images in the originals directory."""
    
    # Mock the behavior of embed_watermark to return a fake watermark length
    mock_embed_watermark.side_effect = [1063, 2048]  # Assume lengths for two images
    
    # Run the embed_workflow function
    main.embed_workflow()
    
    # Check if embed_watermark was called for both images
    mock_embed_watermark.assert_any_call("test_image1.jpg", ORIGINALS_DIR, WATERMARKED_DIR)
    mock_embed_watermark.assert_any_call("test_image2.png", ORIGINALS_DIR, WATERMARKED_DIR)
    
    # Check if the watermark lengths were stored correctly
    assert "test_image1.jpg" in main.watermark_lengths
    assert main.watermark_lengths["test_image1.jpg"] == 1063
    assert main.watermark_lengths["test_image2.png"] == 2048


# Test for extract_workflow
@patch("main.extract_watermark")
@patch("main.get_len_wm_from_log")
@patch("main.os.listdir", return_value=["watermarked_test_image1.jpg", "watermarked_test_image2.png"])
@patch("main.os.makedirs")  # Mock os.makedirs to prevent actual directory creation
def test_extract_workflow(mock_makedirs, mock_listdir, mock_get_len_wm_from_log, mock_extract_watermark):
    """Test extracting watermarks from watermarked images."""
    
    # Mock the behavior of get_len_wm_from_log to return lengths for images
    mock_get_len_wm_from_log.side_effect = [1063, None]  # Return length for the first image, None for the second
    
    # Run the extract_workflow function
    main.extract_workflow()
    
    # Check if extract_watermark was called only for the first image (since the second has no length)
    mock_extract_watermark.assert_called_once_with("test_image1.jpg", 1063, WATERMARKED_DIR)
    
    # Ensure warning message for the second image (with no watermark length) was printed
    assert mock_get_len_wm_from_log.call_count == 2
    mock_get_len_wm_from_log.assert_any_call("test_image1.jpg")
    mock_get_len_wm_from_log.assert_any_call("test_image2.png")

@patch("sys.exit")
def test_invalid_mode(mock_sys_exit, capsys):
    """Test that an invalid mode exits the program with an error message."""
    # Mock sys.argv to simulate invalid mode input
    with patch.object(sys, 'argv', ["main.py", "invalid_mode"]):
        main.main()

    # Capture printed output
    captured = capsys.readouterr()
    
    # Check if sys.exit was called with the correct exit code
    mock_sys_exit.assert_called_once_with(1)
    
    # Check if the correct error message was printed

    assert "Invalid mode. Use 'embed' or 'extract'." in captured.out

# Test for valid embed mode
@patch("main.embed_workflow")
@patch("sys.exit")
def test_valid_embed_mode(mock_sys_exit, mock_embed_workflow):
    """Test that the valid embed mode triggers embed_workflow."""
    # Mock sys.argv to simulate valid mode input
    with patch.object(sys, 'argv', ["main.py", "embed"]):
        main.main()

        # Ensure that embed_workflow was called
        mock_embed_workflow.assert_called_once()
        mock_sys_exit.assert_not_called()

# Test for valid extract mode
@patch("main.extract_workflow")
@patch("sys.exit")
def test_valid_extract_mode(mock_sys_exit, mock_extract_workflow):
    """Test that the valid extract mode triggers extract_workflow."""
    # Mock sys.argv to simulate valid mode input
    with patch.object(sys, 'argv', ["main.py", "extract"]):
        main.main()

        # Ensure that extract_workflow was called
        mock_extract_workflow.assert_called_once()
        mock_sys_exit.assert_not_called()