import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from pathlib import Path
import requests
from BlurWindow.blurWindow import GlobalBlur
import qdarkstyle
from datetime import datetime
import os

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(700, 500)
        self.setWindowTitle("Internet Logger")

        GlobalBlur(self.winId(), Dark=True, QWidget=self)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

        self.label_status = QLabel("Internet Status: Unknown", self)
        self.label_status.setGeometry(10, 10, 200, 30)

        self.label_log_location = QLabel("Log Location:", self)
        self.label_log_location.setGeometry(10, 50, 90, 30)

        self.edit_log_location = QLineEdit(self)
        self.edit_log_location.setGeometry(100, 50, 500, 30)
        self.edit_log_location.setText("log.txt")  
        self.edit_log_location.setReadOnly(True)

        self.btn_change_location = QPushButton("Change Location", self)
        self.btn_change_location.setGeometry(610, 50, 90, 30)
        self.btn_change_location.clicked.connect(self.choose_log_location)

        self.btn_new_log = QPushButton("New Log File", self)
        self.btn_new_log.setGeometry(10, 130, 120, 30)
        self.btn_new_log.clicked.connect(self.create_new_log_file)

        self.btn_start = QPushButton("Start Logging", self)
        self.btn_start.setGeometry(10, 90, 120, 30)
        self.btn_start.clicked.connect(self.start_logging)

        self.btn_stop = QPushButton("Stop Logging", self)
        self.btn_stop.setGeometry(140, 90, 120, 30)
        self.btn_stop.clicked.connect(self.stop_logging)
        self.btn_stop.setEnabled(False)

        self.btn_clean_log = QPushButton("Clean Log", self)
        self.btn_clean_log.setGeometry(270, 90, 120, 30)
        self.btn_clean_log.clicked.connect(self.clean_log)

        self.log_file = self.edit_log_location.text()  
        self.logging_enabled = False

        self.text_edit_log = QTextEdit(self)
        self.text_edit_log.setGeometry(10, 170, 680, 270)
        self.text_edit_log.setReadOnly(True)

        open(self.log_file, 'a').close()

        self.check_internet_status()

        self.internet_check_timer = QTimer(self)
        self.internet_check_timer.timeout.connect(self.check_internet_status)
        self.internet_check_timer.start(30000)  

        self.load_default_location()

    def start_logging(self):
        self.logging_enabled = True
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log_message("Logging started.")

    def stop_logging(self):
        self.logging_enabled = False
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.log_message("Logging stopped.")

        self.update_log_text()

    def clean_log(self):
        open(self.log_file, 'w').close()
        self.update_log_text()

    def choose_log_location(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Text files (*.txt);;All Files (*)")

        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_file = file_dialog.selectedFiles()[0]
            self.edit_log_location.setText(selected_file)
            self.log_file = selected_file

    def create_new_log_file(self):
        appdata_path = os.path.join(os.getenv('APPDATA'), 'FoxyLogger')
        default_location_file = os.path.join(appdata_path, 'default_location.txt')

        if not os.path.exists(appdata_path):
            os.makedirs(appdata_path)

        with open(default_location_file, "w") as location_file:
            location_file.write(self.edit_log_location.text())

        self.log_file = self.edit_log_location.text()
        open(self.log_file, 'a').close()
        self.update_log_text()

    def load_default_location(self):
        appdata_path = os.path.join(os.getenv('APPDATA'), 'FoxyLogger')
        default_location_file = os.path.join(appdata_path, 'default_location.txt')

        if os.path.exists(default_location_file):
            with open(default_location_file, "r") as location_file:
                default_location = location_file.read().strip()
                self.edit_log_location.setText(default_location)
                self.log_file = default_location
                self.update_log_text()

    def check_internet_status(self):
        try:
            requests.get("http://www.google.com", timeout=5)
            self.label_status.setText("Internet Status: Connected")
        except requests.ConnectionError:
            self.label_status.setText("Internet Status: Disconnected")

        if self.logging_enabled:
            self.log_message(f"Internet Status: {self.label_status.text()}")

        self.update_log_text()

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log:
            log.write(f"{timestamp} - {message}\n")

    def update_log_text(self):
        with open(self.log_file, "r") as log:
            log_content = log.read()
            self.text_edit_log.setPlainText(log_content)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside2())

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
