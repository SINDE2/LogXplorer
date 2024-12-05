from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTextEdit,
    QWidget, QSplitter, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QCoreApplication
from log_recording import set_eventlog_max_size, parse_and_interpret_event_logs, get_eventlog_usage, enable_audit_policy, set_audit_with_powershell
from selectf import FileSelector
from setting_time import TimeSetter
from button import MainApp
import os
import sys

class LogXplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_selector = FileSelector()
        self.time_setter = TimeSetter()
        self.selected_folder = None  # 선택된 폴더 경로

        # 로깅 폴더 선택
        self.select_logging_folder()

        self.initUI()

    def select_logging_folder(self):
        """
        프로그램 시작 시 로깅할 폴더를 선택
        """
        selected_folder = QFileDialog.getExistingDirectory(self, "로깅할 폴더 선택", "")
        if not selected_folder:
            QMessageBox.warning(self, "경고", "폴더를 선택하지 않았습니다. 프로그램을 종료합니다.")
            exit()
        self.selected_folder = selected_folder

        # 선택한 폴더에 대해 감사 정책 설정
        try:
            enable_audit_policy()
            set_audit_with_powershell(self.selected_folder)
            QMessageBox.information(self, "로깅 설정 완료", f"선택된 폴더: {self.selected_folder}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로깅 설정 중 오류 발생: {str(e)}")
            exit()

    def initUI(self):
        self.setWindowTitle("LogXplorer")
        self.setGeometry(100, 100, 1400, 800)

        # 메인 위젯과 레이아웃 설정
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Splitter로 레이아웃 구분
        splitter = QSplitter(Qt.Horizontal)

        # 좌측: 폴더 세부 내용 및 이벤트 로그 사용량
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # 선택된 폴더 세부 내용
        self.folder_content = QTextEdit()
        self.folder_content.setFont(QFont('Arial', 12))
        self.folder_content.setReadOnly(True)
        self.folder_content.setText(f"선택된 폴더: {self.selected_folder}")

        # Security 이벤트 로그 사용량
        self.log_usage = QTextEdit()
        self.log_usage.setFont(QFont('Arial', 12))
        self.log_usage.setReadOnly(True)
        self.update_eventlog_usage()

        # 선택된 폴더 세부 내용 (MainApp 트리 추가)
        self.file_tree_widget = MainApp(self.selected_folder)  # 폴더 경로를 전달
        self.file_tree_widget.setFixedHeight(300)
        left_layout.addWidget(QLabel("선택 폴더 세부내용:"))
        left_layout.addWidget(self.file_tree_widget)  # 트리를 추가합니다.

        left_layout.addWidget(QLabel("Security 이벤트 로그 사용량:"))
        left_layout.addWidget(self.log_usage, stretch=1)

        # 좌측 버튼: 폴더 재선택, 로그 용량 설정, 사용 설명서
        left_button_layout = QVBoxLayout()
        folder_reselect_button = QPushButton("폴더 재선택")
        folder_reselect_button.setFont(QFont('Arial', 12))
        folder_reselect_button.clicked.connect(self.select_file_or_folder)  # 전체 설정 초기화

        log_size_button = QPushButton("로그 용량 설정")
        log_size_button.setFont(QFont('Arial', 12))
        log_size_button.clicked.connect(self.set_log_size)

        manual_button = QPushButton("사용 설명서")
        manual_button.setFont(QFont('Arial', 12))
        manual_button.clicked.connect(self.show_manual)

        left_button_layout.addWidget(folder_reselect_button)
        left_button_layout.addWidget(log_size_button)
        left_button_layout.addWidget(manual_button)
        left_button_layout.addStretch()

        left_layout.addLayout(left_button_layout)
        left_widget.setLayout(left_layout)

        # 우측: 로그 분석 결과
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # 위쪽: 경로 선택 및 시간 설정
        path_and_time_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.setFont(QFont('Arial', 12))
        self.file_path.setReadOnly(True)
        self.file_path.setText(self.selected_folder)  # 기본 경로로 설정된 폴더

        path_button = QPushButton("분석할 폴더 선택")
        path_button.setFont(QFont('Arial', 12))
        path_button.clicked.connect(self.select_analysis_folder)  # 분석 폴더 선택

        path_and_time_layout.addWidget(QLabel("분석할 폴더 경로:"))
        path_and_time_layout.addWidget(self.file_path, stretch=4)
        path_and_time_layout.addWidget(path_button)



        time_layout = QHBoxLayout()
        start_label = QLabel("시작 시간:")
        start_label.setFont(QFont('Arial', 12))
        self.start_time = QLineEdit(self.time_setter.get_start_time())
        self.start_time.setFont(QFont('Arial', 12))

        end_label = QLabel("종료 시간:")
        end_label.setFont(QFont('Arial', 12))
        self.end_time = QLineEdit(self.time_setter.get_end_time())
        self.end_time.setFont(QFont('Arial', 12))

        time_layout.addWidget(start_label)
        time_layout.addWidget(self.start_time, stretch=2)
        time_layout.addWidget(end_label)
        time_layout.addWidget(self.end_time, stretch=2)

        # 로그 분석 결과 영역
        self.result_area = QTextEdit()
        self.result_area.setFont(QFont('Arial', 12))
        self.result_area.setReadOnly(True)

        analyze_button = QPushButton("로그 분석")
        analyze_button.setFont(QFont('Arial', 12))
        analyze_button.clicked.connect(self.analyze_logs)

        right_layout.addLayout(path_and_time_layout)
        right_layout.addLayout(time_layout)
        right_layout.addWidget(QLabel("로그 분석 내용:"))
        right_layout.addWidget(self.result_area, stretch=5)
        right_layout.addWidget(analyze_button)

        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # 스플리터 크기 설정
        splitter.setSizes([300, 1100])  # 왼쪽을 좁게, 오른쪽을 넓게 설정

        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def select_analysis_folder(self):
        """
        분석할 폴더를 선택 (UI 초기화 없음).
        """
        selected_path = QFileDialog.getExistingDirectory(self, "분석할 폴더 선택", self.selected_folder)
        if selected_path:
            self.file_path.setText(selected_path)
            QMessageBox.information(self, "폴더 선택 완료", f"분석할 폴더가 선택되었습니다: {selected_path}")

    def select_file_or_folder(self):
        """
        폴더 재선택 후 전체 UI 초기화.
        """
        selected_path = QFileDialog.getExistingDirectory(self, "폴더 재선택", self.selected_folder)
        if selected_path:
            self.selected_folder = selected_path
            self.folder_content.setText(f"선택된 폴더: {selected_path}")

            # 감사 정책 재적용
            try:
                enable_audit_policy()
                set_audit_with_powershell(self.selected_folder)
            except Exception as e:
                QMessageBox.critical(self, "오류", f"폴더 설정 중 오류 발생: {str(e)}")
                return

            # UI 전체 초기화
            self.initialize_ui_for_new_folder()

            QMessageBox.information(self, "폴더 재선택 완료", f"새 폴더가 선택되었습니다: {self.selected_folder}")

    def initialize_ui_for_new_folder(self):
        """
        새로운 폴더에 맞춰 UI를 초기화.
        """
        # 선택된 폴더 정보를 업데이트
        self.folder_content.setText(f"선택된 폴더: {self.selected_folder}")

        # 이벤트 로그 사용량 정보 업데이트
        self.update_eventlog_usage()

        # 로그 분석 결과 초기화
        self.result_area.clear()
        self.result_area.setText("새 폴더에 대한 로그 데이터를 불러오세요.")

    def update_eventlog_usage(self):
        """
        Security 이벤트 로그 사용량을 업데이트.
        """
        try:
            usage_info = get_eventlog_usage('Security')
            self.log_usage.setText(usage_info)
        except Exception as e:
            self.log_usage.setText(f"이벤트 로그 사용량 확인 중 오류 발생: {e}")

    def analyze_logs(self):
        """
        로그 분석 버튼 기능
        """
        target_path = self.file_path.text()
        start_time = self.start_time.text()
        end_time = self.end_time.text()

        if not target_path:
            QMessageBox.warning(self, "경고", "분석할 파일 또는 폴더를 선택해주세요.")
            return

        try:
            # `parse_and_interpret_event_logs` 호출
            self.result_area.clear()
            target_path = target_path.replace('/', r"\\")
            result = parse_and_interpret_event_logs(target_path, start_time, end_time)
            if result:
                self.result_area.setText(result)
            else:
                self.result_area.setText("해당 파일 또는 폴더에 대한 이벤트 로그가 없습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그 분석 중 오류 발생: {str(e)}")

    def set_log_size(self):
        """
        로그 용량 설정 버튼 기능
        """
        try:
            # 사용자 입력 대화 상자 표시
            log_size, ok = QInputDialog.getInt(
                self,
                "로그 용량 설정",
                "최대 로그 크기 (MB):",
                value=128,  # 기본값
                min=1,  # 최소값
                max=10240  # 최대값
            )
            if ok:  # 사용자가 확인 버튼을 누른 경우
                result = set_eventlog_max_size(log_name="Security", max_size_mb=log_size)
                if result is True:
                    QMessageBox.information(self, "성공", f"로그 크기를 {log_size} MB로 설정했습니다.")
                else:
                    QMessageBox.warning(self, "오류", f"로그 크기 설정 실패: {result}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그 크기 설정 중 오류 발생: {str(e)}")

    def show_manual(self):
        QMessageBox.information(self, "사용 설명서", "프로그램 사용 방법 설명.")
