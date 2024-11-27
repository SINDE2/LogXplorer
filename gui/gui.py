import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget,
    QTreeWidget, QTreeWidgetItem, QDialog, QGridLayout, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from selectf import FileSelector
from setting_time import TimeSetter
from log_recording import LogViewer


class LogXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_selector = FileSelector()
        self.time_setter = TimeSetter()
        self.log_viewer = LogViewer()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("LogXplorer")
        self.setGeometry(100, 100, 1200, 800)

        # Main Widget and Layout
        main_widget = QWidget()
        main_layout = QGridLayout()

        # Splitter to separate the side buttons from the main content
        main_splitter = QSplitter(Qt.Horizontal)

        # Left Layout - Buttons and Tree View
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # File Explorer Tree Layout
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemClicked.connect(self.handle_item_click)
        self.populate_root_nodes()
        left_layout.addWidget(self.file_tree)

        # Bottom Buttons Layout (Vertical)
        refresh_button = QPushButton("새로고침")
        refresh_button.setFont(QFont('Arial', 12))
        refresh_button.clicked.connect(self.refresh_ui)
        left_layout.addWidget(refresh_button)

        new_window_button = QPushButton("새 창 열기")
        new_window_button.setFont(QFont('Arial', 12))
        new_window_button.clicked.connect(self.open_new_window)
        left_layout.addWidget(new_window_button)

        left_widget.setLayout(left_layout)
        main_splitter.addWidget(left_widget)

        # Right Layout - File Path, Time Range, and Log Table
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # File Selection Layout
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

        # Time Range Layout
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

        # Table for Analysis
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["이벤트 ID", "소스 이름", "시간 생성", "메시지"])
        right_layout.addWidget(self.table)

        # Analyze Button
        analyze_button = QPushButton("로그 분석")
        analyze_button.setFont(QFont('Arial', 12))
        analyze_button.clicked.connect(self.analyze_logs)
        right_layout.addWidget(analyze_button)

        right_widget.setLayout(right_layout)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([300, 900])  # Set initial sizes of the split pane

        main_layout.addWidget(main_splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_file(self):
        selected_file = self.file_selector.open_file_dialog()
        if selected_file:
            self.file_path.setText(selected_file)

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
            if start_time <= log_time <= end_time:
                if selected_file in log["SourceName"] or selected_file in log["Message"]:
                    filtered_logs.append(log)
                else:
                    print(f"파일과 관련 없는 로그: {log['SourceName']} 또는 {log['Message']}에 {selected_file}이 포함되어 있지 않음.")
            else:
                print(f"시간 범위 벗어난 로그: {log_time} (범위: {start_time} - {end_time})")

        if filtered_logs:
            self.table.setRowCount(len(filtered_logs) + 1)
            self.table.setItem(0, 0, QTableWidgetItem("지정된 로그 분석 결과"))
            self.table.setItem(0, 1, QTableWidgetItem(""))
            self.table.setItem(0, 2, QTableWidgetItem(""))
            self.table.setItem(0, 3, QTableWidgetItem(""))

            for row_idx, log in enumerate(filtered_logs):
                self.table.setItem(row_idx + 1, 0, QTableWidgetItem(str(log["EventID"])))
                self.table.setItem(row_idx + 1, 1, QTableWidgetItem(log["SourceName"]))
                self.table.setItem(row_idx + 1, 2, QTableWidgetItem(log["TimeGenerated"]))
                self.table.setItem(row_idx + 1, 3, QTableWidgetItem(log["Message"]))
        else:
            self.table.setRowCount(0)
            print("선택한 파일에 해당하는 로그가 지정된 시간 범위 내에 없습니다.")

    def populate_root_nodes(self):
        self.file_tree.clear()
        root = QTreeWidgetItem(self.file_tree, ["내 PC"])
        self.add_drive(root, "C:")
        self.add_drive(root, "D:")
        root.setExpanded(True)

    def add_drive(self, parent, drive_letter):
        drive_item = QTreeWidgetItem(parent, [f"로컬 디스크 ({drive_letter})"])
        drive_item.setData(0, 1, drive_letter)

    def handle_item_click(self, item, column):
        drive_letter = item.data(0, 1)
        if drive_letter:
            self.populate_directory(item, drive_letter)

    def populate_directory(self, parent_item, path):
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

    def refresh_ui(self):
        print("새로고침 완료!")
        self.populate_root_nodes()

    def open_new_window(self):
        self.secondary_window = LogXplorer()
        self.secondary_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LogXplorer()
    main_window.show()
    sys.exit(app.exec_())
