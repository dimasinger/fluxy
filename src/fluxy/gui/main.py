import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QFrame,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

_SELECT_FILE = "Select layout file"


class FluxyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Fluxy")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # File selection layout
        file_layout = QVBoxLayout()
        self.file_button = QPushButton(_SELECT_FILE)
        self.file_button.clicked.connect(self.select_file)

        self.filename_display = QLabel("No file selected")
        self.filename_display.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.filename_display)
        main_layout.addLayout(file_layout)

        # Main display layout
        display_layout = QHBoxLayout()

        # Image display (80% width)
        self.image_label = QLabel("overview")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        display_layout.addWidget(self.image_label, 4)

        # Button panel (20% width)
        button_layout = QVBoxLayout()
        self.buttons = []

        self.add_holes_button = QPushButton("Add holes...")
        button_layout.addWidget(self.add_holes_button)
        self.buttons.append(self.add_holes_button)

        button_layout.addStretch()
        display_layout.addLayout(button_layout, 1)

        main_layout.addLayout(display_layout)

        self.setLayout(main_layout)

    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            _SELECT_FILE,
            "",
            "Designs (*.gds *.oas);;All Files (*)",
            options=options,
        )

        if file_name:
            self.filename_display.setText(file_name)
            self.display_image(file_name)

    def display_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluxyApp()
    window.show()
    sys.exit(app.exec_())
