import sys
import csv

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

from datetime import datetime
from acc_types import Acceleration

"""Annotate Acceleration Data From Accelerometer And Save data as CSV file"""

DATA_POINTS = []


class AnnotateAccelerometerData(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Annotate Accelerometer Data")
        self.setGeometry(100, 100, 500, 300)
        self.fall_state = "0"

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

        save_button = QPushButton("Save As CSV", self)
        save_button.setStyleSheet(
            "QPushButton { padding: 10px; font-size: 18px; background-color: blue; color: white;}"
        )
        save_button.setFixedSize(200, 100)
        save_button.clicked.connect(self.save_as_csv)
        layout.addWidget(save_button)

    def fall_button_clicked(self):
        self.fall_state = "Start"
        print("Fall", self.fall_state)

    def not_fall_button_clicked(self):
        self.fall_state = "Stop"
        print("Not Fall", self.fall_state)

    def on_data_received(self, acceleration: Acceleration):
        print(acceleration)
        if self.fall_state == "Start":
            acceleration.fall_state = "1"
        elif self.fall_state == "Stop":
            acceleration.fall_state = "0"
        else:
            acceleration.fall_state = "0"
        DATA_POINTS.append(acceleration)

    def save_as_csv(self):
        with open(f"sensor_data_{datetime.now()}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            head = ["timestamp", "timestamp_local", "ax", "ay", "az", "fall_state"]
            writer.writerow(head)

            for field in DATA_POINTS:
                writer.writerow(field.as_csv_field())
        DATA_POINTS.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnnotateAccelerometerData()
    window.show()
