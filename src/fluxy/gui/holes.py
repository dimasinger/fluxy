from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QComboBox,
    QGridLayout,
    QAbstractItemView,
    QMessageBox,
)

from fluxy.design.holezone import GridType, HoleType


class ConfigureCircuitLayersDialog(QDialog):
    def __init__(self, parent, layers: list[int]):
        super().__init__(parent)
        self.setWindowTitle("Configure circuit layers...")
        self.setMinimumWidth(300)

        # Layout
        layout = QVBoxLayout(self)

        # Circuit layers list
        self.layer_label = QLabel("Circuit layers:")
        layout.addWidget(self.layer_label)

        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for layer in layers:
            item = QListWidgetItem(str(layer))
            self.layer_list.addItem(item)
        layout.addWidget(self.layer_list)

        # Minimum distance input
        self.distance_label = QLabel("Minimum distance from hole to circuit layers:")
        layout.addWidget(self.distance_label)

        self.distance_input = QLineEdit("12")
        layout.addWidget(self.distance_input)

        # OK and Cancel buttons
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.check_accept)
        layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

    def selected_layers(self):
        """Returns a list of selected layer numbers."""
        return [int(item.text()) for item in self.layer_list.selectedItems()]

    def minimum_distance(self):
        """Returns the minimum distance entered as an integer."""
        try:
            return float(self.distance_input.text())
        except ValueError:
            return None  # Default value if invalid input

    def check_accept(self):
        if not self.selected_layers():
            QMessageBox.critical(
                self,
                "No circuit layer selected",
                "Please select at least one circuit layer!",
            )
            return

        if self.minimum_distance() is None:
            QMessageBox.critical(
                self,
                "Invalid minimum distance",
                "Please enter a valid number for the minimum distance!",
            )
            return

        if self.minimum_distance() < 0:
            QMessageBox.critical(
                self,
                "Invalid minimum distance",
                "Please enter a non-negative number for the minimum distance!",
            )
            return

        self.accept()


class AddHolesDialog(QDialog):
    def __init__(self, parent, layers: list[int]):
        super().__init__(parent)
        self.setWindowTitle("Add holes...")

        layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # First row
        grid_layout.addWidget(QLabel("Layer of hole zone"), 0, 0)
        self.layer_zone_cb = QComboBox()
        self.layer_zone_cb.addItems(map(str, layers))
        grid_layout.addWidget(self.layer_zone_cb, 0, 1)

        grid_layout.addWidget(QLabel("Layer of created holes"), 0, 2)
        self.layer_holes_cb = QComboBox()
        self.layer_holes_cb.setEditable(True)
        self.layer_holes_cb.addItems(map(str, layers))
        grid_layout.addWidget(self.layer_holes_cb, 0, 3)

        # Second row
        grid_layout.addWidget(QLabel("Grid type"), 1, 0)
        self.grid_type_cb = QComboBox()
        self.grid_type_cb.addItems([gt.value for gt in GridType])
        grid_layout.addWidget(self.grid_type_cb, 1, 1)

        grid_layout.addWidget(QLabel("Grid size"), 1, 2)
        self.grid_size_le = QLineEdit("12")
        grid_layout.addWidget(self.grid_size_le, 1, 3)

        # Third row
        grid_layout.addWidget(QLabel("Hole type"), 2, 0)
        self.hole_type_cb = QComboBox()
        self.hole_type_cb.addItems([ht.value for ht in HoleType])  # Dummy values
        grid_layout.addWidget(self.hole_type_cb, 2, 1)

        grid_layout.addWidget(QLabel("Hole size"), 2, 2)
        self.hole_size_le = QLineEdit("2")
        grid_layout.addWidget(self.hole_size_le, 2, 3)

        layout.addLayout(grid_layout)

        # Buttons
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self.ok_button.clicked.connect(self.check_accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def layer_holezone(self) -> int:
        return int(self.layer_zone_cb.currentText())

    def layer_holes(self) -> int:
        try:
            layer = int(self.layer_holes_cb.currentText())
            return None if layer < 0 else layer
        except ValueError:
            return None  # Default value if invalid input

    def grid_type(self) -> GridType:
        return GridType(self.grid_type_cb.currentText())

    def grid_size(self) -> float:
        try:
            return float(self.grid_size_le.text())
        except ValueError:
            return None  # Default value if invalid input

    def hole_type(self) -> HoleType:
        return HoleType(self.hole_type_cb.currentText())

    def hole_size(self) -> float:
        try:
            return float(self.hole_size_le.text())
        except ValueError:
            return None  # Default value if invalid input

    def check_accept(self):
        if self.layer_holes() is None:
            QMessageBox.critical(
                self,
                "Invalid hole layer",
                "Please enter a valid layer for the added holes!",
            )
            return

        if self.grid_size() is None:
            QMessageBox.critical(
                self,
                "Invalid grid size",
                "Please enter a valid number for the grid size!",
            )
            return

        if self.grid_size() < 0:
            QMessageBox.critical(
                self,
                "Invalid grid size",
                "Please enter a non-negative number for the grid size!",
            )
            return

        if self.hole_size() is None:
            QMessageBox.critical(
                self,
                "Invalid hole size",
                "Please enter a valid number for the hole size!",
            )
            return

        if self.hole_size() < 0:
            QMessageBox.critical(
                self,
                "Invalid hole size",
                "Please enter a non-negative number for the hole size!",
            )
            return

        self.accept()
