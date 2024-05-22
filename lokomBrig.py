import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QComboBox, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QRect
import cv2
from deepface import DeepFace
import json
import time
import sqlite3

def determine_state(emotions):
    state_mapping = {
        "tired": "Усталость",
        "happy": "Радость",
        "sad": "Грусть",
        "neutral": "Спокойствие"
    }
    
    if not emotions:
        return "В кадре нет лица"
    
    for emotion in emotions:
        if emotion in state_mapping:
            return state_mapping[emotion]
    
    return "Неопределенное состояние"

def face_verify(img_1, img_2):
    try:
        result_dict = DeepFace.verify(img1_path=img_1, img2_path=img_2)

        with open('result.json', 'w') as file:
            json.dump(result_dict, file, indent=4, ensure_ascii=False)

        if result_dict.get('verified'):
            return True
        return False

    except Exception as ex:
        return False

def detect_dominant_emotion(frame):
    try:
        predictions = DeepFace.analyze(frame, actions=['emotion'])

        dominant_emotions = []
        for prediction in predictions:
            dominant_emotion = max(prediction['emotion'], key=prediction['emotion'].get)
            dominant_emotions.append(dominant_emotion)

        return dominant_emotions

    except Exception as ex:
        print("Error during emotion detection:", ex)
        return None

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Идентификация")
        self.setGeometry(100, 100, 1200, 700)
        
        # Выпадающий список
        layout = QVBoxLayout()

        self.driver_combo = QComboBox(self)
        
        self.photo_rect = QRect(0, 0, 300, 400)
        combo_width = self.photo_rect.width()
        self.driver_combo.setFixedWidth(combo_width)
        self.driver_combo.setStyleSheet(f"QComboBox {{ width: {combo_width}px; }}")
        
        layout.addWidget(self.driver_combo)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.setLayout(layout)

        # Заполнение выпадающего списка
        with sqlite3.connect('driver.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, image_driv FROM driv_info")
            rows = cursor.fetchall()

            for row in rows:
                name, photo_path = row
                self.driver_combo.addItem(name, userData=photo_path)

        self.driver_combo.currentIndexChanged.connect(self.display_selected_driver_image)

        self.photo_rect = QLabel(self)
        self.photo_rect.setGeometry(50, 50, 300, 400)
        self.photo_rect.setStyleSheet("border: 2px solid black")

        self.camera_rect = QLabel(self)
        self.camera_rect.setGeometry(450, 50, 300, 400)
        self.camera_rect.setStyleSheet("border: 2px solid black")

        self.emotion_label = QLabel(self)
        self.emotion_label.setGeometry(450, 470, 300, 30)
        self.emotion_label.setStyleSheet("color: red; font-size: 16px;")

        self.emotion_label = QLabel(self)
        self.emotion_label.setGeometry(50, 470, 500, 30)
        self.emotion_label.setStyleSheet("color: blue; font-size: 16px;")
        
        self.message_box = QTextEdit(self)
        self.message_box.setGeometry(50, 500, 300, 50)
        self.message_box.setReadOnly(True)

        photo_path = "photo/abr.jpg"
        self.photo_pixmap = QPixmap(photo_path)
        self.photo_rect.setPixmap(self.photo_pixmap.scaled(self.photo_rect.size(), Qt.KeepAspectRatio))

        self.capture = cv2.VideoCapture(0)

        self.width = 640
        self.height = 480
        self.camera_rect.setFixedSize(self.width, self.height)

        self.last_photo_time = time.time()
        self.verified = False

        self.timer_photo = QTimer(self)
        self.timer_photo.timeout.connect(self.take_photo_and_verify)
        self.timer_photo.start(30000)
        
        self.timer_video = QTimer(self)
        self.timer_video.timeout.connect(self.update_frame)
        self.timer_video.start(200)
        self.show()

    def display_selected_driver_image(self, index):
        selected_photo_path = self.driver_combo.currentData()
        pixmap = QPixmap(selected_photo_path)
        self.photo_rect.setPixmap(pixmap.scaled(self.photo_rect.size(), Qt.KeepAspectRatio))

    def take_photo_and_verify(self):
        self.last_photo_time = time.time()
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite('temp_frame.jpg', frame)
            
            selected_photo_path = self.driver_combo.currentData()
            
            self.verified = face_verify(selected_photo_path, 'temp_frame.jpg')  
            if self.verified:
                self.photo_rect.setPixmap(QPixmap(selected_photo_path).scaled(self.photo_rect.size(), Qt.KeepAspectRatio))
                self.message_box.append('Проверка пройдена. Пропустить.')
            else:
                self.message_box.append('Нарушитель! Задержать!!!')

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            display_image = rgb_image.copy()
            
            for (x, y, w, h) in faces:
                cv2.rectangle(display_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                face_roi = gray_image[y:y+h, x:x+w]
                face_roi_rgb = cv2.merge([face_roi, face_roi, face_roi])

                emotional_text = detect_dominant_emotion(face_roi_rgb)
                if emotional_text:
                    cv2.putText(display_image, ", ".join(emotional_text), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    
                    state = determine_state(emotional_text)
                    self.emotion_label.setText("Состояние: " + state)

                else:
                    self.emotion_label.setText("Лицо не обнаружено")

            convert_to_qt_format = QImage(display_image.data, display_image.shape[1], display_image.shape[0], display_image.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            
            self.camera_rect.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())