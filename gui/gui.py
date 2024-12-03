from PyQt5.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QWidget, QGridLayout, QMessageBox, QSplitter, QFrame, QFileDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDateTime
from log_recording import enable_audit_policy, set_audit_with_powershell, parse_and_interpret_event_logs
from button import MainApp
from selectf import FileSelector
from setting_time import TimeSetter

class LogXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_selector = FileSelector()  # FileSelector 인스턴스 생성
        self.main_app = MainApp()  # MainApp 인스턴스 생성
        self.time_setter = TimeSetter()  # TimeSetter 인스턴스 생성 (시간 설정 관리)
        self.selected_folder = None  # 사용자가 탐색할 폴더
        self.select_folder_dialog()  # 폴더 선택 창 표시
        self.initUI()

    def select_folder_dialog(self):
        """
        프로그램 시작 시 탐색할 폴더를 선택하도록 폴더 선택 창을 표시
        """
        self.selected_folder = QFileDialog.getExistingDirectory(
            self, "탐색할 폴더 선택", "", QFileDialog.ShowDirsOnly
        )
        if not self.selected_folder:
            QMessageBox.warning(self, "경고", "폴더를 선택하지 않았습니다. 프로그램을 종료합니다.")
            exit()  # 폴더가 선택되지 않은 경우 프로그램 종료

        # 선택한 폴더에 대해 감사 정책 및 감사 규칙 설정
        enable_audit_policy()
        set_audit_with_powershell(self.selected_folder)

    def initUI(self):
        self.setWindowTitle("LogXplorer")
        self.setGeometry(100, 100, 1400, 800)

        # 메인 위젯과 레이아웃
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Splitter로 왼쪽 파일 탐색기와 오른쪽 로그 영역 분리
        splitter = QSplitter(Qt.Horizontal)

        # 왼쪽 위젯: 파일 탐색기 트리와 버튼들
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 파일 탐색기 트리 추가 (MainApp의 파일 탐색기 사용)
        self.file_tree = self.main_app.file_tree
        self.file_tree.setFrameShape(QFrame.StyledPanel)  # 경계선 설정
        self.file_tree.setMaximumWidth(250)  # 파일 탐색기 폭을 작게 조정

        # 선택된 폴더 내 파일 탐색 설정
        self.file_tree.clear()  # 기존 트리 초기화
        self.main_app.populate_directory(self.file_tree.invisibleRootItem(), self.selected_folder)
        left_layout.addWidget(self.file_tree, stretch=1)  # 파일 탐색기가 최대한 공간을 사용

        # 왼쪽 하단에 추가 버튼들 (새로고침, 새 창 열기, 사용설명서)
        refresh_button = self.main_app.refresh_button
        refresh_button.clicked.connect(self.refresh_ui)  # 새로고침 기능 연결
        new_window_button = QPushButton("새 창 열기")
        new_window_button.setFont(QFont('Arial', 12))
        new_window_button.clicked.connect(self.open_new_window)  # 새로운 LogXplorer 창 열기
        manual_button = QPushButton("사용설명서")
        manual_button.setFont(QFont('Arial', 12))
        manual_button.clicked.connect(self.show_manual)

        # 버튼들을 하단으로 최대한 이동시키기 위한 레이아웃 설정
        button_layout = QVBoxLayout()
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(new_window_button)
        button_layout.addWidget(manual_button)
        button_layout.addStretch()  # 버튼 위의 공간을 확보하여 파일 탐색기가 위로 확장되도록 함

        left_layout.addLayout(button_layout)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # 오른쪽 레이아웃 - 파일 선택, 시간 설정, 로그 분석, 결과 표시
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 파일 선택 및 시간 설정
        file_layout = QHBoxLayout()
        file_label = QLabel("선택한 파일 경로:")
        file_label.setFont(QFont('Arial', 12))
        self.file_path = QLineEdit()
        self.file_path.setReadOnly(True)
        self.file_path.setFont(QFont('Arial', 12))

        file_button = QPushButton("파일 선택")
        file_button.setFont(QFont('Arial', 12))
        file_button.clicked.connect(self.select_file)

        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(file_button)

        # 시간 설정 레이아웃
        time_layout = QHBoxLayout()
        start_label = QLabel("시작 시간:")
        start_label.setFont(QFont('Arial', 12))
        self.start_time = QLineEdit()
        self.start_time.setFont(QFont('Arial', 12))

        end_label = QLabel("종료 시간:")
        end_label.setFont(QFont('Arial', 12))
        self.end_time = QLineEdit()
        self.end_time.setFont(QFont('Arial', 12))

        # TimeSetter 클래스를 사용해 시작 시간과 종료 시간 설정
        self.start_time.setText(self.time_setter.get_start_time())
        self.end_time.setText(self.time_setter.get_end_time())

        time_layout.addWidget(start_label)
        time_layout.addWidget(self.start_time)
        time_layout.addWidget(end_label)
        time_layout.addWidget(self.end_time)

        # 로그 분석 버튼 (아래로 이동)
        analyze_button = QPushButton("로그 분석")
        analyze_button.setFont(QFont('Arial', 12))
        analyze_button.clicked.connect(self.analyze_logs)

        # 결과 표시 영역
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)

        # 오른쪽 레이아웃 구성
        right_layout.addLayout(file_layout)
        right_layout.addLayout(time_layout)
        right_layout.addWidget(self.result_area, stretch=5)  # 결과 영역을 더 크게 설정
        right_layout.addWidget(analyze_button)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # 스플리터 크기 설정 (왼쪽을 더 작게, 오른쪽을 더 크게)
        splitter.setSizes([250, 1150])  # 파일 탐색기 영역을 작게, 로그 분석 영역을 크게 설정

        # 메인 레이아웃에 스플리터 추가
        main_layout.addWidget(splitter)

        # 메인 위젯 설정
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_file(self):
        # 파일 선택 다이얼로그 열기
        options = QFileDialog.Options()
        selected_file, _ = QFileDialog.getOpenFileName(self, "파일 선택", self.selected_folder, "All Files (*)", options=options)
        if selected_file:
            self.file_path.setText(selected_file)

    def refresh_ui(self):
        # 새로고침 버튼 기능: 선택된 폴더 내 파일 트리 업데이트
        self.file_tree.clear()
        self.main_app.populate_directory(self.file_tree.invisibleRootItem(), self.selected_folder)
        QMessageBox.information(self, "새로고침", "폴더 새로고침 완료!")

    def analyze_logs(self):
        # 로그 분석 기능
        target_file = self.file_path.text()
        if not target_file:
            QMessageBox.warning(self, "경고", "파일을 선택해주세요.")
            return

        # 로그 파싱 및 해석
        try:
            start_time = self.start_time.text()
            end_time = self.end_time.text()
            events = parse_and_interpret_event_logs(target_file)

            # 결과 영역에 로그 출력
            self.result_area.clear()
            if events:
                for event in events:
                    self.result_area.append("-" * 50)
                    self.result_area.append(f"Time: {event['time']}")
                    self.result_area.append(f"User: {event['user_name']} ({event['user_sid']})")
                    self.result_area.append(f"Domain: {event['domain_name']}")
                    self.result_area.append(f"Accessed File: {event['object_name']}")
                    self.result_area.append(f"Event Type: {event['event_type']}")
                    if "access_type" in event:
                        self.result_area.append(f"Access Type: {event['access_type']}")
                    if "process_name" in event:
                        self.result_area.append(f"Process Name: {event['process_name']}")
                    self.result_area.append("-" * 50)
            else:
                self.result_area.append("로그에서 해당 파일에 대한 이벤트를 찾을 수 없습니다.")

            QMessageBox.information(self, "로그 분석 완료", "로그 분석이 완료되었습니다. 결과는 아래에 표시됩니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그 분석 중 오류 발생: {str(e)}")

    def open_new_window(self):
        # 새로운 LogXplorer 인스턴스를 생성하여 새 창 열기
        self.new_window = LogXplorer()
        self.new_window.show()

    def show_manual(self):
        # 사용 설명서 기능
        QMessageBox.information(self, "사용 설명서", "이 프로그램은 로그 분석 및 파일 선택 기능을 제공합니다.")
