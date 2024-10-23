from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QHBoxLayout, QVBoxLayout, QDateTimeEdit, QWidget
from PyQt5.QtCore import QDateTime
import sys

class TimeSetterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("시간 설정")
        self.setGeometry(100, 100, 400, 200)
        self.initUI()

    def initUI(self):
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 레이아웃 설정
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # 시간 설정 영역
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)

        start_time_label = QLabel("시작 시간 설정")
        start_time_label.setFixedWidth(200)
        time_layout.addWidget(start_time_label)

        self.start_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time_edit.setCalendarPopup(True)
        time_layout.addWidget(self.start_time_edit)

        end_time_label = QLabel("종료 시간 설정")
        end_time_label.setFixedWidth(200)
        time_layout.addWidget(end_time_label)

        self.end_time_edit = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))  # 1시간 뒤로 설정
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time_edit.setCalendarPopup(True)
        time_layout.addWidget(self.end_time_edit)

        main_layout.addLayout(time_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimeSetterWindow()
    window.show()
    sys.exit(app.exec_())
