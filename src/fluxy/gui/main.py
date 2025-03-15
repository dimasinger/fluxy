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
    QMessageBox,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas

from fluxy.design import Design, HoleZone
from fluxy.gui.holes import ConfigureCircuitLayersDialog

_SELECT_FILE = "Select layout file"


class FluxyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.design = None
        self.hole_zone = None

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
        self.canvas_fig, self.canvas_ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvas(self.canvas_fig)
        self.update_image()
        display_layout.addWidget(self.canvas, 4)

        # Button panel (20% width)
        button_layout = QVBoxLayout()
        self.buttons = []

        self.add_holes_button = QPushButton("Add holes...")
        button_layout.addWidget(self.add_holes_button)
        self.buttons.append(self.add_holes_button)
        self.add_holes_button.clicked.connect(self.add_holes)

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
            self.design = Design(file_name)

            dialog = ConfigureCircuitLayersDialog(self, self.design.layers)

            if not dialog.exec():
                return

            self.circuit_layers = dialog.selected_layers()

            self.hole_zone = HoleZone(
                self.design,
                self.circuit_layers,
                dialog.minimum_distance(),
            )

            self.filename_display.setText(file_name)
            self.update_image()

    def add_holes(self):
        layers = list(range(10))

        if self.hole_zone is None:
            QMessageBox.critical(self, "Error", "Please open a design first!")
            return

    def update_image(self):
        self.canvas_ax.clear()
        self.canvas_ax.set_position([0, 0, 1, 1])
        self.canvas_ax.set_axis_off()

        if self.design is not None:
            for layer in self.circuit_layers:
                self.design.plot(self.canvas_ax, layer=layer)

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluxyApp()
    window.show()
    sys.exit(app.exec_())
