from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QWidget
import win32evtlog
import sys

from scapy.modules.nmap import nmap_match_one_sig


class LogViewerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # UI 레이아웃 설정
        self.setWindowTitle("파일 관련 어플리케이션 로그 보기")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 파일 선택 버튼
        self.select_file_button = QPushButton("파일 선택")
        self.select_file_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_file_button)

        # 로그 표시 영역
        self.log_text_area = QTextEdit()
        self.log_text_area.setReadOnly(True)
        layout.addWidget(self.log_text_area)

        self.setLayout(layout)

    def select_file(self):
        # 파일 선택 대화 상자 열기
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "All Files (*);;Text Files (*.txt)",
                                                   options=options)

        if file_path:
            # 로그 가져와서 표시
            logs = self.get_application_logs_for_file(file_path)
            self.log_text_area.clear()
            if logs:
                for log in logs:
                    self.log_text_area.append(log)
            else:
                self.log_text_area.append("해당 파일에 대한 로그가 없습니다.")

    def get_application_logs_for_file(self, file_path):
        hand = win32evtlog.OpenEventLog(None, "Application")

        flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        logs = []

        # 어플리케이션 로그 읽기
        events = win32evtlog.ReadEventLog(hand, flags, 0)
        for event in events:
            if event.StringInserts:
                # 로그 메시지에서 파일 경로와 일치하는 이벤트 찾기
                if any(file_path in message for message in event.StringInserts):
                    log_entry = (f"Event ID: {event.EventID}\n"
                                 f"Source Name: {event.SourceName}\n"
                                 f"Time Generated: {event.TimeGenerated}\n"
                                 f"Message: {' '.join(event.StringInserts)}\n\n")
                    logs.append(log_entry)

        return logs


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = LogViewerApp()
    viewer.show()
    sys.exit(app.exec_())
