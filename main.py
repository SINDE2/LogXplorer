import sys
from PyQt5.QtWidgets import QApplication
from gui import LogXplorer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # GUI를 실행하여 모든 기능 통합
    main_window = LogXplorer()
    main_window.show()

    # 어플리케이션 종료 관리
    sys.exit(app.exec_())
