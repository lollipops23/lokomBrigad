import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QHBoxLayout
from PyQt5.QtGui import QPixmap


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    face_records_app = FaceRecordsApp()
    face_records_app.show()
    sys.exit(app.exec_())