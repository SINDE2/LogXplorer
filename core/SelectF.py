from PyQt5.QtWidgets import QFileDialog

class FileSelector:
    def __init__(self):
        self.selected_file_path = ""

    def open_file_dialog(self):
        # 파일 다이얼로그 열기
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(None, "파일 선택", "", "모든 파일 (*);;텍스트 파일 (*.txt)", options=options)

        if file_name:
            # 선택한 파일 경로 저장
            self.selected_file_path = file_name
            return self.selected_file_path
        return None