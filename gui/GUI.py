from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, \
    QWidget, QTextEdit, QScrollArea, QDateTimeEdit
from PyQt5.QtCore import QDateTime
import subprocess
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogXploler")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        # 메인 위젯 설정
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 레이아웃 설정
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # 왼쪽 영역 (버튼)
        left_layout = QVBoxLayout()

        # 버튼 영역
        action_button = QPushButton("버튼")
        action_button.setStyleSheet("color: white; background-color: teal; font-size: 16px;")
        action_button.setFixedHeight(600)
        left_layout.addWidget(action_button)

        main_layout.addLayout(left_layout, 1)

        # 오른쪽 영역 (파일 선택, 시간 설정, 로그 기록)
        right_layout = QVBoxLayout()

        # 파일, 폴더 선택 영역
        file_button = QPushButton("파일, 폴더 선택")
        file_button.setStyleSheet("background-color: teal; color: white;")
        file_button.clicked.connect(self.select_file)
        file_button.setFixedHeight(50)
        right_layout.addWidget(file_button)

        # 선택한 파일 경로 표시
        self.file_path_label = QLabel("선택된 파일: 없음")
        self.file_path_label.setStyleSheet("background-color: teal; color: white;")
        right_layout.addWidget(self.file_path_label)

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

        # 검색 시작 버튼
        search_button = QPushButton("검색 시작")
        search_button.setStyleSheet("background-color: teal; color: white;")
        search_button.clicked.connect(self.load_event_logs)
        right_layout.addWidget(search_button)

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
        self.selected_file_path = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택")
        if file_path:
            self.selected_file_path = file_path
            self.file_path_label.setText(f"선택된 파일: {file_path}")
        else:
            self.file_path_label.setText("선택된 파일: 없음")

    def load_event_logs(self):
        if not self.selected_file_path:
            self.log_text.append("먼저 파일을 선택해 주세요.")
            return

        start_time = self.start_time_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        end_time = self.end_time_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ss")
        command = [
            "powershell",
            "-Command",
            "Get-WinEvent -LogName 'Application' -ErrorAction SilentlyContinue | Where-Object { $_.TimeCreated -ge '{}' -and $_.TimeCreated -le '{}' } | Select-Object -First 100 | Format-Table -HideTableHeaders Message".format(
                start_time, end_time)
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                self.log_lines = result.stdout.splitlines()
                self.current_log_index = 0
                self.display_logs()
            else:
                self.log_text.append("로그를 불러오는 중 오류가 발생했습니다: PowerShell 명령 실행 실패")
        except Exception as e:
            self.log_text.append(f"로그를 불러오는 중 오류가 발생했습니다: {str(e)}")

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