import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QProgressBar, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap
from utils import embed_watermark, extract_watermark  # Assuming these functions exist in your utils.py

# Worker Thread for processing images without freezing the UI
class WatermarkWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    done_signal = pyqtSignal()  # Only emit once all images are processed

    def __init__(self, originals_folder, watermarked_folder, mode="embed", wm_shape=1063):
        super().__init__()
        self.originals_folder = originals_folder
        self.watermarked_folder = watermarked_folder
        self.mode = mode
        self.wm_shape = wm_shape  # For extraction

    def run(self):
        try:
            images = [img for img in os.listdir(self.originals_folder) if img.endswith(('jpg', 'jpeg', 'png'))]
            total_images = len(images)
            self.progress_signal.emit(0)  # Initialize progress bar at 0
            self.progress_signal.emit(total_images)  # Set the progress bar maximum

            # Process each image
            for i, image_name in enumerate(images):
                if self.mode == "embed":
                    self.log_signal.emit(f"Embedding watermark in: {image_name} ({i+1}/{total_images})")
                    embed_watermark(image_name, self.originals_folder, self.watermarked_folder)
                elif self.mode == "extract":
                    self.log_signal.emit(f"Extracting watermark from: {image_name} ({i+1}/{total_images})")
                    extracted_log, validation_status = extract_watermark(image_name, self.wm_shape, self.watermarked_folder)
                    self.log_signal.emit(extracted_log)
                
                # Update progress after each image
                self.progress_signal.emit(i + 1)

            # Emit the done signal when processing is complete
            self.done_signal.emit()

        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")

# Main GUI class
class WatermarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Window settings
        self.setWindowTitle("Eastland Jones Creative Digital Watermark")
        self.setGeometry(100, 100, 400, 500)  # Adjust window size to accommodate logo
        self.setAcceptDrops(True)  # Enable drag-and-drop

        # Layout
        layout = QVBoxLayout()

        # Add logo to the UI (Correct the path to the logo)
        logo_label = QLabel(self)
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")  # Correct logo path
        pixmap = QPixmap(logo_path)

        if not pixmap.isNull():  # Ensure the pixmap loaded successfully
            # Resize the logo (width: 200px, height: 100px as an example)
            scaled_pixmap = pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)  # Center the logo
        else:
            logo_label.setText("Logo not found")  # Display a fallback message if the logo is missing

        layout.addWidget(logo_label, alignment=Qt.AlignTop | Qt.AlignHCenter)  # Align logo to the top and center

        # Radio buttons for choosing Embed or Extract
        self.radio_embed = QRadioButton("Embed Watermark")
        self.radio_extract = QRadioButton("Extract Watermark")
        self.radio_embed.setChecked(True)  # Default selection

        # Button group to ensure only one can be selected at a time
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_embed)
        self.radio_group.addButton(self.radio_extract)

        layout.addWidget(self.radio_embed)
        layout.addWidget(self.radio_extract)

        # Label to show drag-and-drop instruction
        self.drop_label = QLabel("Drag and drop a folder with images to watermark or extract")
        layout.addWidget(self.drop_label)

        # Text box for real-time log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.log_display)

        # Progress bar for showing progress
        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        # Status label for displaying status
        self.status_label = QLabel("Status: Waiting for action", self)
        layout.addWidget(self.status_label)

        # Set the layout to the window
        self.setLayout(layout)

    # Enable drag-and-drop for folders
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        # Handle folder drop
        for url in event.mimeData().urls():
            folder_path = url.toLocalFile()
            if os.path.isdir(folder_path):  # Only accept directories
                self.status_label.setText(f"Folder dropped: {folder_path}")
                self.process_folder(folder_path)

    def process_folder(self, folder_path):
        # Specify originals and watermarked directories
        originals_folder = folder_path
        watermarked_folder = os.path.join(folder_path, "../watermarked")

        # Create the watermarked folder if it doesn't exist
        os.makedirs(watermarked_folder, exist_ok=True)

        # Determine whether to embed or extract based on the radio button selection
        mode = "embed" if self.radio_embed.isChecked() else "extract"

        # Start the watermarking or extraction process in a separate thread
        wm_shape = 1063  # Example watermark shape size, adjust if necessary for extraction
        self.worker = WatermarkWorker(originals_folder, watermarked_folder, mode=mode, wm_shape=wm_shape)
        self.worker.log_signal.connect(self.update_log)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.done_signal.connect(self.watermarking_done)
        self.worker.start()

    def update_log(self, message):
        # Append the log message to the display
        self.log_display.append(message)

    def update_progress(self, value):
        # Update the progress bar based on value
        self.progress.setValue(value)

    def watermarking_done(self):
        # Update status when done
        self.status_label.setText("Watermarking/Extraction completed")
        self.log_display.append("Processing complete.")

# Main application entry
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = WatermarkApp()
    ex.show()
    sys.exit(app.exec_())