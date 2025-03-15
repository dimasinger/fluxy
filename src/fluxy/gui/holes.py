from PyQt5.QtWidgets import (
    QDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QAbstractItemView,
)


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
        self.ok_button.clicked.connect(self.accept)
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
            return int(self.distance_input.text())
        except ValueError:
            return 12  # Default value if invalid input
