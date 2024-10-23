import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()

        # 레이아웃 설정
        self.layout = QVBoxLayout()
        
        # 버튼 생성
        self.select_button = QPushButton('파일 및 폴더 선택')
        self.select_button.clicked.connect(self.open_file_dialog)

        # 경로 표시 레이블
        self.file_path_label = QLabel('선택한 파일의 경로: ')

        # 레이아웃에 위젯 추가
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.file_path_label)

        self.setLayout(self.layout)
        self.setWindowTitle('파일 선택기')
        self.setGeometry(300, 300, 400, 200)

    def open_file_dialog(self):
        # 파일 다이얼로그 열기
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "파일 선택", "", "실행 파일 (*.exe);;모든 파일 (*)", options=options)
        
        if file_name:
            # 선택한 파일 경로 표시
            self.file_path_label.setText(f'선택한 파일의 경로: {file_name}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileSelector()
    window.show()
    sys.exit(app.exec_())
