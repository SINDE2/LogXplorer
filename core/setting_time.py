from PyQt5.QtCore import QDateTime

class TimeSetter:
    def __init__(self):
        # 현재 시간 설정
        self.start_time = QDateTime.currentDateTime()
        self.end_time = self.start_time.addSecs(3600)  # 1시간 뒤 종료 시간 설정

    def get_start_time(self):
        # 시작 시간 반환 (형식: yyyy-MM-dd HH:mm:ss)
        return self.start_time.toString("yyyy-MM-dd HH:mm:ss")

    def get_end_time(self):
        # 종료 시간 반환 (형식: yyyy-MM-dd HH:mm:ss)
        return self.end_time.toString("yyyy-MM-dd HH:mm:ss")

    def set_start_time(self, new_time):
        # 새로운 시작 시간 설정
        self.start_time = new_time
        self.update_end_time()

    def update_end_time(self):
        # 시작 시간에 1시간 추가하여 종료 시간 설정
        self.end_time = self.start_time.addSecs(3600)

# 사용 예시
if __name__ == "__main__":
    time_setter = TimeSetter()
    print(f"시작 시간: {time_setter.get_start_time()}")
    print(f"종료 시간: {time_setter.get_end_time()}")
