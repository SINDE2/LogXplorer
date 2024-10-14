from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, \
    QWidget, QTextEdit, QScrollArea, QDateTimeEdit
from PyQt5.QtCore import QDateTime
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("프로그램")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 레이아웃 설정
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # 왼쪽 영역 (버튼, 프로그램명)
        left_layout = QVBoxLayout()

        # 버튼 영역
        action_button = QPushButton("버튼")
        action_button.setStyleSheet("color: white; background-color: teal; font-size: 16px;")
        action_button.setFixedHeight(150)
        left_layout.addWidget(action_button)

        # 프로그램명 영역
        program_label = QLabel("프로그래밍")
        program_label.setStyleSheet("background-color: teal; color: white;")
        left_layout.addWidget(program_label)

        main_layout.addLayout(left_layout, 1)

        # 오른쪽 영역 (파일 선택, 시간 설정, 로그 기록)
        right_layout = QVBoxLayout()

        # 파일, 폴더 선택 영역
        file_button = QPushButton("파일, 폴더 선택")
        file_button.setStyleSheet("background-color: teal; color: white;")
        file_button.clicked.connect(self.select_file)
        right_layout.addWidget(file_button)

        # 시간 설정 영역
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)

        start_time_label = QLabel("시작 시간 설정")
        start_time_label.setFixedWidth(200)
        time_layout.addWidget(start_time_label)

        self.start_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time_edit.setCalendarPopup(True)
        self.start_time_edit.setStyleSheet("background-color: teal; color: white;")
        time_layout.addWidget(self.start_time_edit)

        end_time_label = QLabel("종료 시간 설정")
        end_time_label.setFixedWidth(200)
        time_layout.addWidget(end_time_label)

        self.end_time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setStyleSheet("background-color: teal; color: white;")
        time_layout.addWidget(self.end_time_edit)

        right_layout.addLayout(time_layout)

        # 로그 기록 영역
        log_frame = QWidget()
        log_frame.setStyleSheet("background-color: teal;")
        log_layout = QVBoxLayout(log_frame)
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("color: white; background-color: teal;")
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(log_frame)
        right_layout.addWidget(scroll_area)

        self.more_button = QPushButton("더 보기")
        self.more_button.setStyleSheet("background-color: teal; color: white;")
        self.more_button.clicked.connect(self.load_more_logs)
        self.more_button.setVisible(False)
        right_layout.addWidget(self.more_button)

        main_layout.addLayout(right_layout, 2)

        self.log_lines = []
        self.current_log_index = 0

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if file_path:
            self.analyze_log(file_path)
        else:
            self.log_text.append("파일을 선택해 주세요.")

    def analyze_log(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                log_content = file.readlines()
                self.log_lines = []
                start_time = self.start_time_edit.dateTime().toPyDateTime()
                end_time = self.end_time_edit.dateTime().toPyDateTime()
                for line in log_content:
                    timestamp_str = line.split(' ')[0]  # Assuming the timestamp is the first element
                    try:
                        timestamp = QDateTime.fromString(timestamp_str, "yyyy-MM-dd HH:mm:ss").toPyDateTime()
                        if start_time <= timestamp <= end_time:
                            self.log_lines.append(line)
                    except ValueError:
                        continue
                self.current_log_index = 0
                self.display_logs()

    def display_logs(self):
        self.log_text.clear()
        max_logs_per_page = 10
        end_index = min(self.current_log_index + max_logs_per_page, len(self.log_lines))
        for i in range(self.current_log_index, end_index):
            self.log_text.append(self.log_lines[i])
        self.current_log_index = end_index
        if self.current_log_index < len(self.log_lines):
            self.more_button.setVisible(True)
        else:
            self.more_button.setVisible(False)

    def load_more_logs(self):
        self.display_logs()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())