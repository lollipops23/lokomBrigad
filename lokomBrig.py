import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import cv2
from deepface import DeepFace
import json
import time

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

        self.photo_rect = QLabel(self)
        self.photo_rect.setGeometry(50, 50, 300, 400)
        self.photo_rect.setStyleSheet("border: 2px solid black")

        self.camera_rect = QLabel(self)
        self.camera_rect.setGeometry(450, 50, 300, 400)
        self.camera_rect.setStyleSheet("border: 2px solid black")

        self.emotion_label = QLabel(self)
        self.emotion_label.setGeometry(450, 470, 300, 30)
        self.emotion_label.setStyleSheet("color: red; font-size: 16px;")

        self.message_box = QTextEdit(self)
        self.message_box.setGeometry(50, 500, 300, 50)
        self.message_box.setReadOnly(True)

        photo_path = "photo/Tirsina.jpg"
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
        self.timer_video.start(500)
        self.show()

    def take_photo_and_verify(self):
        self.last_photo_time = time.time()
        ret, frame = self.capture.read()
        if ret:
            cv2.imwrite('temp_frame.jpg', frame)
            img_2 = 'temp_frame.jpg'
            self.verified = face_verify('photo/Tirsina.jpg', img_2)
            if self.verified:
                self.photo_rect.setPixmap(self.photo_pixmap.scaled(self.photo_rect.size(), Qt.KeepAspectRatio))
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
            
            convert_to_qt_format = QImage(display_image.data, display_image.shape[1], display_image.shape[0], display_image.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            
            self.camera_rect.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())