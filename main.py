import sys

from PyQt5.QtWidgets import QApplication
from selectf import FileSelector
from setting_time import TimeSetter
from gui import LogXplorer
import win32evtlog

class MainApp:
    def __init__(self):
        # 파일 선택 기능 초기화
        self.file_selector = FileSelector()

        # 시간 설정 기능 초기화
        self.time_setter = TimeSetter()

        # 로그 기능 초기화
        self.log_feature = None

    def get_application_logs(self, file_identifier=None):
        """Application 로그를 검색하고 필요한 로그만 반환."""
        try:
            hand = win32evtlog.OpenEventLog(None, "Application")  # Application 로그 열기
            flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            logs = []

            while True:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if not events:  # 읽을 이벤트가 없으면 종료
                    break

                for event in events:
                    if event.StringInserts:
                        # 이벤트 필터링 (파일 식별자 포함 여부 확인)
                        if file_identifier and not any(file_identifier in msg for msg in event.StringInserts):
                            continue
                        
                        log_entry = {
                            "EventID": event.EventID,
                            "SourceName": event.SourceName,
                            "TimeGenerated": event.TimeGenerated.Format(),
                            "Message": ' '.join(event.StringInserts)
                        }
                        logs.append(log_entry)

                # 대량 로그 처리를 위한 제어 (대량 로그 처리 중단 조건 추가 가능)
                if len(logs) > 1000:
                    break

            return logs
        except Exception as e:
            print(f"로그 읽기 오류: {str(e)}")
            return []
        finally:
            win32evtlog.CloseEventLog(hand)  # 로그 핸들 닫기

    def run(self):
        # 파일 선택 기능 실행
        selected_file = self.file_selector.open_file_dialog()
        if selected_file:
            print(f"선택한 파일 경로: {selected_file}")
        else:
            print("파일을 선택하지 않았습니다.")
            return

        # 시간 설정 기능 실행
        print(f"시작 시간: {self.time_setter.get_start_time()}")
        print(f"종료 시간: {self.time_setter.get_end_time()}")

        # 로그 기능 실행
        print("로그를 검색합니다...")
        logs = self.get_application_logs(file_identifier=selected_file)
        if logs:
            print("검색된 로그:")
            for log in logs[:10]:  # 로그 상위 10개 출력
                print(f"Event ID: {log['EventID']}")
                print(f"Source Name: {log['SourceName']}")
                print(f"Time Generated: {log['TimeGenerated']}")
                print(f"Message: {log['Message']}")
                print("-" * 40)
        else:
            print("해당 파일에 관련된 로그가 없습니다.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = LogXplorer()
    main_window.show()
    sys.exit(app.exec_())
