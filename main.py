import sys
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import numpy

from rekognition import Rekognition

face_cascade = cv2.CascadeClassifier('/home/danimar/projetos/python3/lib/python3.6/site-packages/cv2/data/haarcascade_frontalface_default.xml')  # noqa


class QtCapture(QtWidgets.QWidget):
    def __init__(self, *args):
        super(QtWidgets.QWidget, self).__init__()

        self.fps = 10
        self.cap = cv2.VideoCapture(*args)

        self.video_frame = QtWidgets.QLabel()
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.video_frame)

        self.cleanup_index = QtWidgets.QPushButton('Cleanup Index Face')
        self.cleanup_index.clicked.connect(self.cleanup_index_collection)

        self.identifier = QtWidgets.QLineEdit()

        self.index_image = QtWidgets.QPushButton('Save Image to Index')
        self.index_image.clicked.connect(self.save_image_to_index)

        self.search_image = QtWidgets.QPushButton('Search Image')
        self.search_image.clicked.connect(self.search_image_from_index)
        lay.addWidget(self.cleanup_index)
        lay.addWidget(self.identifier)
        lay.addWidget(self.index_image)
        lay.addWidget(self.search_image)

        self.label_user = QtWidgets.QLabel('Resultado...')
        self.label_user.setAlignment(QtCore.Qt.AlignCenter)
        lay.addWidget(self.label_user)

        self.setLayout(lay)

        # ------ Modification ------ #
        self.isCapturing = False
        self.ith_frame = 1
        # ------ Modification ------ #

    def cleanup_index_collection(self):
        rek = Rekognition('', '')
        rek.delete_faces()

    def save_image_to_index(self):
        identifier = self.identifier.text().strip()
        if len(identifier) > 5:
            rek = Rekognition('', '')
            ret, frame = self.cap.read()
            image = numpy.array(cv2.imencode('.png', frame)[1]).tostring()
            resp = rek.index_image(image, identifier)
            print(resp)
        else:
            QtWidgets.QMessageBox.warning(
                self, "Atenção!", "Preencha o identificador!")

    def search_image_from_index(self):
        rek = Rekognition('', '')
        ret, frame = self.cap.read()
        image = numpy.array(cv2.imencode('.png', frame)[1]).tostring()
        resp = rek.search_face(image)
        if len(resp['FaceMatches']) == 0:
            self.label_user.setText('Nenhum rosto encontrado')
        for face in resp['FaceMatches']:
            self.label_user.setText(face['Face']['ExternalImageId'])
        print(resp)

    def setFPS(self, fps):
        self.fps = fps

    def nextFrameSlot(self):
        ret, frame = self.cap.read()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # ------ Modification ------ #
        # Save images if isCapturing
        if self.isCapturing:
            cv2.imwrite('img_%05d.jpg' % self.ith_frame, frame)
            self.ith_frame += 1
        # ------ Modification ------ #

        # My webcam yields frames in BGR format
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QtGui.QImage(frame, frame.shape[1], frame.shape[0],
                           QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

    def stop(self):
        self.timer.stop()

    # ------ Modification ------ #
    def capture(self):
        if not self.isCapturing:
            self.isCapturing = True
        else:
            self.isCapturing = False
    # ------ Modification ------ #

    def deleteLater(self):
        self.cap.release()
        super(QtWidgets.QWidget, self).deleteLater()


class ControlWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.capture = None

        self.start_button = QtWidgets.QPushButton('Start')
        self.start_button.clicked.connect(self.startCapture)
        self.quit_button = QtWidgets.QPushButton('End')
        self.quit_button.clicked.connect(self.endCapture)
        self.end_button = QtWidgets.QPushButton('Stop')

        # ------ Modification ------ #
        self.capture_button = QtWidgets.QPushButton('Capture')
        self.capture_button.clicked.connect(self.saveCapture)
        # ------ Modification ------ #

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)

        # ------ Modification ------ #
        vbox.addWidget(self.capture_button)
        # ------ Modification ------ #

        self.setLayout(vbox)
        self.setWindowTitle('Control Panel')
        self.setGeometry(100, 100, 200, 200)
        self.show()

    def startCapture(self):
        if not self.capture:
            self.capture = QtCapture(0)
            self.end_button.clicked.connect(self.capture.stop)
            # self.capture.setFPS(1)
            self.capture.setParent(self)
            self.capture.setWindowFlags(QtCore.Qt.Tool)
        self.capture.start()
        self.capture.show()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

    # ------ Modification ------ #
    def saveCapture(self):
        if self.capture:
            self.capture.capture()
    # ------ Modification ------ #


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ControlWindow()
    sys.exit(app.exec_())
