import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QWidget,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor

from models import Acceleration

"""Annotate Acceleration Data From Accelerometer And Save data as CSV file"""


class AnnotateAccelerometerData(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Annotate Accelerometer Data")
        self.setGeometry(100, 100, 500, 300)
        self.fall_state = "default"

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        fall_button = QPushButton("Start Fall", self)
        fall_button.setStyleSheet(
            "QPushButton { padding: 10px; font-size: 18px; background-color: red; color: white;}"
        )
        fall_button.setFixedSize(200, 100)
        fall_button.clicked.connect(self.fall_button_clicked)
        layout.addWidget(fall_button)

        not_fall_button = QPushButton("Stop Fall", self)
        not_fall_button.setStyleSheet(
            "QPushButton { padding: 10px; font-size: 18px; background-color: green; color: white;}"
        )
        not_fall_button.setFixedSize(200, 100)
        not_fall_button.clicked.connect(self.not_fall_button_clicked)
        layout.addWidget(not_fall_button)

    def fall_button_clicked(self):
        self.fall_state = "Start"
        print("Fall", self.fall_state)

    def not_fall_button_clicked(self):
        self.fall_state = "Stop"
        print("Not Fall", self.fall_state)

    def on_data_received(self, acceleration: Acceleration):
        print(acceleration)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnotateAccelerometerData()
    window.show()
