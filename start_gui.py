import sys

from PyQt5.QtWidgets import QApplication

from fluxy.gui import FluxyApp


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluxyApp()
    window.show()
    sys.exit(app.exec_())
