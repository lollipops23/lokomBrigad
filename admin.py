import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import numpy as np

class FaceRecordsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QLabel()
        self.pixmap = None
        self.image_window = None 
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Админка')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.display_face_records()

        self.table.cellClicked.connect(self.show_image)
        
        btn_show_emotions_chart = QPushButton('График эмоций')
        btn_show_emotions_chart.clicked.connect(self.show_emotions_chart)
        layout.addWidget(btn_show_emotions_chart)

    def display_face_records(self):
        with sqlite3.connect('driver.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM face")
            rows = cursor.fetchall()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(rows[0]))

            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(i, j, item)

    def show_image(self, row, col):
        image_path = self.table.item(row, 2).text()

        self.pixmap = QPixmap(image_path)

        if self.pixmap.isNull():
            print("Невозможно загрузить фото")
            return

        if self.image_window:
            self.image_window.deleteLater() 

        self.image.setPixmap(self.pixmap)
        self.image.resize(self.pixmap.width(), self.pixmap.height())

        self.image_window = QWidget() 
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image)
        self.image_window.setLayout(image_layout)
        self.image_window.setWindowTitle('Фото с камеры')
        self.image_window.show()
    
    def show_emotions_chart(self):
        with sqlite3.connect('driver.db') as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT name, dom_emotion, time FROM face INNER JOIN driv_info ON face.machine_ID = driv_info.id")
            rows = cursor.fetchall()

            driver_emotions = {}

            for row in rows:
                driver_name = row[0]
                emotion = row[1]
                time = row[2]

                if driver_name not in driver_emotions:
                    driver_emotions[driver_name] = {"times": [], "emotions": []}

                driver_emotions[driver_name]["times"].append(time)
                driver_emotions[driver_name]["emotions"].append(emotion)

            for driver, data in driver_emotions.items():
                times = data["times"]
                emotions = data["emotions"]

                plt.figure()
                plt.plot(times, emotions, marker='o', label=driver)
                plt.xlabel('Время')
                plt.ylabel('Эмоции')
                plt.title(f'Эмоции {driver}')
                plt.legend()
                plt.grid(True)

            plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    face_records_app = FaceRecordsApp()
    face_records_app.show()
    sys.exit(app.exec_())