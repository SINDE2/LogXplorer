from PyQt5.QtGui import QIcon
from PyQt5 import  QtCore
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QWidget, QDialog, QLabel
)
import os
import sys

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        # 아이콘 초기화 - 이미지 경로가 올바른지 확인해 주세요.
        self.drive_icon = QIcon("./file_icon.png")  # 아이콘 설정
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("종합 버튼 기능 구현")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 새로고침 버튼
        self.refresh_button = QPushButton("새로고침")
        self.refresh_button.clicked.connect(self.refresh_ui)
        layout.addWidget(self.refresh_button)

        # 파일 탐색기 스타일 트리 구조
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.itemClicked.connect(self.handle_item_click)
        self.file_tree.setIconSize(QtCore.QSize(16, 16))  # QTreeWidget의 아이콘 크기 설정

        # 기본 트리 노드 추가
        self.populate_root_nodes()

        layout.addWidget(self.file_tree)

        # 새 창 띄우기 버튼
        self.new_window_button = QPushButton("새 창 열기")
        self.new_window_button.clicked.connect(self.open_new_window)
        layout.addWidget(self.new_window_button)

        # 메인 레이아웃 설정
        self.setLayout(layout)

        if self.drive_icon.isNull():
            print("Failed to load drive icon")
        else:
            print("Drive icon loaded successfully")

    def populate_root_nodes(self):
        """
        초기 트리에 루트 노드(드라이브)를 추가합니다.
        """
        self.file_tree.clear()
        root = QTreeWidgetItem(self.file_tree, ["내 PC"])
        
        # 드라이브 아이콘 설정
        self.drive_icon = QIcon("./file_icon.png")  # 공통 드라이브 아이콘
        
        # 각 드라이브에 동일한 아이콘 적용
        c_drive = QTreeWidgetItem(root, ["로컬 디스크 (C:)"])
        c_drive.setIcon(0, self.drive_icon)
        c_drive.setData(0, 1, "C:")
        
        d_drive = QTreeWidgetItem(root, ["로컬 디스크 (D:)"])
        d_drive.setIcon(0, self.drive_icon)
        d_drive.setData(0, 1, "D:")
        
        e_drive = QTreeWidgetItem(root, ["로컬 디스크 (E:)"])
        e_drive.setIcon(0, self.drive_icon)
        e_drive.setData(0, 1, "E:")
        
        root.setExpanded(True)

    def add_drive(self, parent, drive_letter):
        """
        루트에 드라이브를 추가하고 아이콘을 설정합니다.
        """
        drive_item = QTreeWidgetItem(parent, [f"로컬 디스크 ({drive_letter})"])
        drive_item.setIcon(0, self.drive_icon)  # 드라이브 아이콘 설정
        drive_item.setData(0, 1, drive_letter)

    def handle_item_click(self, item, column):
        """
        트리 항목 클릭 이벤트 처리
        """
        drive_letter = item.data(0, 1)
        if drive_letter:
            print(f"{drive_letter} 드라이브 클릭됨")
            self.populate_directory(item, drive_letter)

    def populate_directory(self, parent_item, path):
        """
        선택된 디렉토리의 하위 항목을 동적으로 트리에 추가하고 아이콘을 설정합니다.
        """
        parent_item.takeChildren()
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    sub_item = QTreeWidgetItem(parent_item, [entry])
                    sub_item.setIcon(0, self.drive_icon)  # 폴더 아이콘 설정
                    sub_item.setData(0, 1, full_path)
        except PermissionError:
            print(f"권한 부족으로 {path}의 내용을 읽을 수 없습니다.")
        except FileNotFoundError:
            print(f"{path} 경로를 찾을 수 없습니다.")

    def refresh_ui(self):
        """
        새로고침 버튼 기능: 트리 및 기타 UI 초기화
        """
        print("새로고침 완료!")
        self.populate_root_nodes()

    def open_new_window(self):
        """
        새 창 띄우기 버튼 기능: QDialog를 띄움
        """
        message = "이것은 새로 열린 창입니다!"
        self.secondary_window = SecondaryWindow(message)
        self.secondary_window.exec_()

class SecondaryWindow(QDialog):
    def __init__(self, message):
        super().__init__()
        self.setWindowTitle("새 창")
        self.setGeometry(200, 200, 400, 200)

        layout = QVBoxLayout()
        label = QLabel(message)
        layout.addWidget(label)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
