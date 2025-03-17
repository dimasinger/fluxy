from os import path

import numpy as np

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
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt

from PIL import Image

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas

from fluxy.design import Design, HoleZone
from fluxy.gui.holes import ConfigureCircuitLayersDialog, AddHolesDialog

_SELECT_FILE = "Select layout file"


def _draw_design(design: Design, layers: list[int]) -> QPixmap:
    fig, ax = plt.subplots(figsize=(6, 6))
    canvas = FigureCanvas(fig)

    ax.set_position([0, 0, 1, 1])
    ax.set_axis_off()
    for layer in layers:
        design.plot(ax, layer)

    canvas.draw()
    size = canvas.size()
    width, height = size.width(), size.height()

    im = QImage(canvas.buffer_rgba(), width, height, QImage.Format_ARGB32)
    return QPixmap(im)


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
        self.file_button.clicked.connect(self.load_file)

        self.filename_display = QLabel("No file selected")
        self.filename_display.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.filename_display)
        main_layout.addLayout(file_layout)

        # Main display layout
        display_layout = QHBoxLayout()

        # Image display (80% width)
        self.canvas_label = QLabel("")
        display_layout.addWidget(self.canvas_label, 4)

        # Button panel (20% width)
        button_layout = QVBoxLayout()

        self.add_holes_button = QPushButton("Add holes...")
        self.add_holes_button.clicked.connect(self.add_holes)
        button_layout.addWidget(self.add_holes_button)

        self.save_button = QPushButton("Save design")
        self.save_button.clicked.connect(self.save_file)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()
        display_layout.addLayout(button_layout, 1)

        main_layout.addLayout(display_layout)

        self.setLayout(main_layout)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            _SELECT_FILE,
            "",
            "Designs (*.gds *.oas);;All Files (*)",
            options=options,
        )

        if file_name:
            self.file_name = file_name
            self.design = Design(self.file_name)

            dialog = ConfigureCircuitLayersDialog(self, self.design.layers)

            if not dialog.exec():
                return

            self.circuit_layers = dialog.selected_layers()

            self.filename_display.setText("Loading...")
            QApplication.processEvents()

            self.create_image()
            self.filename_display.setText("Pre-processing...")
            self.hole_zone = HoleZone(
                self.design,
                self.circuit_layers,
                dialog.minimum_distance(),
            )

            self.filename_display.setText(self.file_name)

    def save_file(self):
        if self.design is None:
            QMessageBox.critical(self, "Error", "Please open a design first!")
            return

        default_filename = path.splitext(self.file_name)[0] + "_holed.oas"

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "Save Design",
            default_filename,
            "OAS Files (*.oas);;GDS Files (*.gds);;All Files (*)",
            options=options,
        )

        self.design.save(file_name)

    def add_holes(self):
        if self.hole_zone is None:
            QMessageBox.critical(self, "Error", "Please open a design first!")
            return

        dialog = AddHolesDialog(self, self.design.layers)

        if not dialog.exec():
            return

        self.hole_zone.create_holes(
            hole_layer=dialog.layer_holes(),
            hole_zone_layer=dialog.layer_holezone(),
            grid_size=dialog.grid_size(),
            grid_type=dialog.grid_type(),
            hole_size=dialog.hole_size(),
            hole_type=dialog.hole_type(),
        )

    def create_image(self):
        self.circuit_pixmap = _draw_design(self.design, self.circuit_layers)
        self.canvas_label.setPixmap(
            self.circuit_pixmap.scaledToWidth(
                self.canvas_label.width(),
                Qt.SmoothTransformation,
            )
        )
