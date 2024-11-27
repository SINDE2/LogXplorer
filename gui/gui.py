import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget,
    QTreeWidget, QTreeWidgetItem, QDialog, QGridLayout, QSplitter, QFileDialog
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
from selectf import FileSelector
from setting_time import TimeSetter
from log_recording import LogViewer
from button import MainApp  # button.py에서 필요한 클래스 가져오기


class LogXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_selector = FileSelector()
        self.time_setter = TimeSetter()
        self.log_viewer = LogViewer()
        self.main_app = MainApp()  # button.py의 MainApp 인스턴스 생성
        self.initUI()

    def initUI(self):
        self.setWindowTitle("LogXplorer")
        self.setGeometry(100, 100, 1200, 800)

        # 드래그 앤 드롭 활성화
        self.setAcceptDrops(True)

        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        main_layout = QGridLayout()

        # 사이드 버튼과 메인 콘텐츠를 분리하는 스플리터
        main_splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 레이아웃 - 버튼 및 트리 뷰
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 파일 탐색기 트리 레이아웃
        self.file_tree = self.main_app.file_tree  # button.py에서 구현된 파일 트리 사용
        self.file_tree.setAcceptDrops(True)  # 파일 트리 드래그 앤 드롭 허용
        self.file_tree.dragEnterEvent = self.dragEnterEvent  # 드래그 이벤트 연결
        self.file_tree.dropEvent = self.dropEvent  # 드롭 이벤트 연결
        self.file_tree.itemClicked.connect(self.handle_item_click)
        left_layout.addWidget(self.file_tree)

        # 하단 버튼 레이아웃 (세로 배치)
        refresh_button = self.main_app.refresh_button  # button.py에서 가져온 새로고침 버튼 사용
        refresh_button.clicked.connect(self.refresh_ui)
        left_layout.addWidget(refresh_button)

        new_window_button = QPushButton("새 창 열기")
        new_window_button.setFont(QFont('Arial', 12))
        new_window_button.clicked.connect(self.open_new_window)
        left_layout.addWidget(new_window_button)

        left_widget.setLayout(left_layout)
        main_splitter.addWidget(left_widget)

        # 오른쪽 레이아웃 - 파일 경로, 시간 범위, 로그 테이블
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 파일 선택 레이아웃
        file_layout = QHBoxLayout()
        file_label = QLabel("선택한 파일 경로:")
        file_label.setFont(QFont('Arial', 12))
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setFont(QFont('Arial', 12))
        file_button = QPushButton("파일 및 폴더 선택")
        file_button.setFont(QFont('Arial', 12))
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(file_button)
        right_layout.addLayout(file_layout)

        # 시간 범위 레이아웃
        time_layout = QHBoxLayout()
        start_label = QLabel("시작 T:")
        start_label.setFont(QFont('Arial', 12))
        self.start_time = QLineEdit(self.time_setter.get_start_time())
        self.start_time.setFont(QFont('Arial', 12))
        end_label = QLabel("종료 T:")
        end_label.setFont(QFont('Arial', 12))
        self.end_time = QLineEdit(self.time_setter.get_end_time())
        self.end_time.setFont(QFont('Arial', 12))
        time_layout.addWidget(start_label)
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(end_label)
        time_layout.addWidget(self.end_time)
        right_layout.addLayout(time_layout)

        # 로그 분석을 위한 테이블
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["이벤트 ID", "소스 이름", "시간 생성", "메시지"])
        right_layout.addWidget(self.table)

        # 로그 분석 버튼
        analyze_button = QPushButton("로그 분석")
        analyze_button.setFont(QFont('Arial', 12))
        analyze_button.clicked.connect(self.analyze_logs)
        right_layout.addWidget(analyze_button)

        right_widget.setLayout(right_layout)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([300, 900])  # 스플리터 초기 크기 설정

        main_layout.addWidget(main_splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_file(self):
        selected_file, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "All Files (*.*)")
        if selected_file:
            self.file_path.setText(selected_file)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # 드래그 이벤트 처리
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        # 드롭 이벤트 처리
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.file_path.setText(file_path)
                print(f"드롭된 파일 경로: {file_path}")

    def analyze_logs(self):
        selected_file = self.file_path.text()
        start_time_str = self.start_time.text()
        end_time_str = self.end_time.text()

        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("시간 형식이 잘못되었습니다. yyyy-MM-dd HH:mm:ss 형식을 사용하십시오.")
            return

        # 로그 분석을 위해 LogViewer 사용
        logs = self.log_viewer.get_application_logs_for_file()
        filtered_logs = []

        for log in logs:
            if "Error" in log:
                continue  # 오류 로그는 건너뜁니다

            # 로그에서 필요한 정보 추출
            try:
                log_time = datetime.strptime(log["TimeGenerated"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            # 선택한 파일과 관련된 로그인지 확인 (SourceName 또는 Message에 파일 경로 포함)
            if start_time <= log_time <= end_time and (selected_file in log["SourceName"] or selected_file in log["Message"]):
                filtered_logs.append(log)

        if filtered_logs:
            self.table.setRowCount(len(filtered_logs) + 1)
            self.table.setItem(0, 0, QTableWidgetItem("지정된 로그 분석 결과"))
            self.table.setItem(0, 1, QTableWidgetItem("") )
            self.table.setItem(0, 2, QTableWidgetItem("") )
            self.table.setItem(0, 3, QTableWidgetItem("") )
            for row_idx, log in enumerate(filtered_logs):
                self.table.setItem(row_idx + 1, 0, QTableWidgetItem(str(log["EventID"])))
                self.table.setItem(row_idx + 1, 1, QTableWidgetItem(log["SourceName"]))
                self.table.setItem(row_idx + 1, 2, QTableWidgetItem(log["TimeGenerated"]))
                self.table.setItem(row_idx + 1, 3, QTableWidgetItem(log["Message"]))
        else:
            self.table.setRowCount(0)

    def refresh_ui(self):
        # UI 새로고침
        self.main_app.refresh_file_tree()  # button.py의 기능 사용

    def open_new_window(self):
        # 새 창 열기
        self.secondary_window = LogXplorer()
        self.secondary_window.show()

    def handle_item_click(self, item, column):
        # 파일 트리 아이템 클릭 처리
        drive_letter = item.data(0, 1)
        if drive_letter:
            self.populate_directory(item, drive_letter)

    def populate_directory(self, parent_item, path):
        # 디렉터리의 내용을 파일 트리에 추가
        parent_item.takeChildren()
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    sub_item = QTreeWidgetItem(parent_item, [entry])
                    sub_item.setData(0, 1, full_path)
        except PermissionError:
            print(f"권한 부족으로 {path}의 내용을 읽을 수 없습니다.")
        except FileNotFoundError:
            print(f"{path} 경로를 찾을 수 없습니다.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LogXplorer()
    main_window.show()
    sys.exit(app.exec_())
