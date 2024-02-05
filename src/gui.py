from PyQt6.QtWidgets import *

from argparse import ArgumentParser
from PyQt6.QtWidgets import QApplication
import sys


class GatemetrixGui(QDialog):
    def __init__(self, application: QApplication):
        super(GatemetrixGui, self).__init__(parent=None)

        self._app = application

        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Start Fall Detection"))
        layout.addWidget(QPushButton("Stop Fall Detection"))

        self.setLayout(layout)
        self.setWindowTitle("Gate matrix")
        self.resize(50, 60)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--stage", type=str, default="dev")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    gui = GatemetrixGui(application=app)
    gui.show()

    sys.exit(app.exec())
