from core.selectf import FileSelector
from core.setting_time import TimeSetter

class MainApp:
    def __init__(self):
        # 파일 선택 기능 초기화
        self.file_selector = FileSelector()

        # 시간 설정 기능 초기화
        self.time_setter = TimeSetter()

        # 추가 기능을 위한 자리 (추후 구현 예정)
        self.additional_feature_1 = None
        self.additional_feature_2 = None
        self.additional_feature_3 = None

    def run(self):
        # 파일 선택 기능 실행
        selected_file = self.file_selector.open_file_dialog()
        if selected_file:
            print(f"선택한 파일 경로: {selected_file}")
        else:
            print("파일을 선택하지 않았습니다.")

        # 시간 설정 기능 실행
        print(f"시작 시간: {self.time_setter.get_start_time()}")
        print(f"종료 시간: {self.time_setter.get_end_time()}")

        # 추가 기능 실행을 위한 자리 (추후 기능 추가)
        # 로그 기록
        # 버튼 기능
        # GUI 파일


if __name__ == "__main__":
    app = MainApp()
    app.run()
