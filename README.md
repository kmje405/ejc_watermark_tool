# **Eastland Jones Creative Watermark Tool**

The **Eastland Jones Creative Watermark Tool** is a desktop application developed using PyQt5 for embedding and extracting digital watermarks into/from image files. The tool helps to secure and validate images by adding invisible watermarks using the `blind-watermark` library. The tool provides a user-friendly GUI, supports command-line execution, and includes features like progress tracking, logging, and error handling.

![Screenshot of the Application](/screenshot.png)

## **Table of Contents**

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Usage](#usage)
   - [Running the GUI](#running-the-gui)
   - [Running via Command Line](#running-via-command-line)
6. [Configuration](#configuration)
7. [Testing](#testing)
8. [Building a macOS App](#building-a-macos-app)
9. [Contributing](#contributing)
10. [License](#license)

## **Features**

- **Embed Watermarks**: Secure your images by embedding invisible watermarks with metadata such as UUIDs and timestamps.
- **Extract Watermarks**: Validate images by extracting and verifying embedded watermarks.
- **User Interface**: A PyQt5-based GUI for drag-and-drop folder selection, progress tracking, and log display.
- **Command-Line Interface**: Supports embedding and extraction via CLI.
- **Logging**: Detailed logging of operations including errors and warnings.
- **Testing**: Unit tests provided using `pytest` for all major functionalities.

## **Project Structure**

```
.
├── assets/                    # Contains assets like logos
├── images/                    # Directory to store original, watermarked, and extracted images
│   ├── extracted/
│   ├── originals/
│   └── watermarked/
├── logs/                      # Logs generated by the application
├── main.py                    # Command-line interface and workflow management
├── gui.py                     # PyQt5-based graphical user interface
├── utils.py                   # Watermark embedding and extraction utilities
├── logger.py                  # Logging configuration and utilities
├── tests/                     # Unit tests for utils and main functionalities
│   ├── test_utils.py
│   └── test_main.py
└── requirements.txt           # Python dependencies
```

## **Requirements**

- **Python**: 3.9+
- **Libraries**:
  - `PyQt5`: For creating the GUI
  - `blind-watermark`: For watermark embedding and extraction
  - `pytest`: For testing
  - Other dependencies listed in `requirements.txt`

## **Installation**

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/eastland-jones-watermark-tool.git
   cd eastland-jones-watermark-tool
   ```

2. **Set Up a Virtual Environment** (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## **Usage**

### Running the GUI

To run the graphical user interface, simply execute `gui.py`:

```bash
python gui.py
```

Once launched, you can:

- Drag and drop a folder containing images to watermark or extract from.
- Select whether to embed or extract watermarks using the radio buttons.
- View progress in the progress bar and see real-time logs.

### Running via Command Line

The tool can also be run via the command line. It accepts two modes: `embed` or `extract`.

- **Embed Watermarks**:

  ```bash
  python main.py embed
  ```

- **Extract Watermarks**:
  ```bash
  python main.py extract
  ```

The command-line interface processes all images in the `images/originals` folder and stores results in the `images/watermarked` folder.

### Configuration

- **Default Directories**:

  - **Original Images**: `images/originals/`
  - **Watermarked Images**: `images/watermarked/`

- **Logs**:
  Logs are saved in the `logs/` directory and capture important information about embedding, extraction, and errors.

### Testing

Unit tests are provided for key functionalities such as watermark embedding, extraction, and logging.

To run tests, use `pytest`:

```bash
pytest tests/
```

Make sure your environment is properly set up, and all dependencies are installed before running the tests.

### Building a macOS App

To build the application into a macOS `.app` bundle, you can use `PyInstaller`:

1. Install `PyInstaller`:

   ```bash
   pip install pyinstaller
   ```

2. Package the application:
   ```bash
   pyinstaller --name "EastlandJonesCreativeWatermark" --windowed --onefile gui.py
   ```

This will generate an `.app` file under the `dist/` directory.

#### Fixing macOS Signing Issues

If you encounter signing issues when building for macOS, run the following command to remove Finder metadata and sign the app manually:

```bash
xattr -cr dist/EastlandJonesCreativeWatermark.app
```

For more details, refer to Apple's [code-signing documentation](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution).

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.
