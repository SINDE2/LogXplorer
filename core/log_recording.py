import win32evtlog

class LogViewer:
    def __init__(self, application_log="Application"):
        self.application_log = application_log

    def get_application_logs_for_file(self):
        """
        Application 로그에서 이벤트를 가져오고,
        핸들을 안전하게 닫는 예외 처리 및 성능 개선 코드 추가
        """
        try:
            # 로그 핸들 열기
            hand = win32evtlog.OpenEventLog(None, self.application_log)
            flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            logs = []

            while True:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                if not events:
                    break

                for event in events:
                    if event.StringInserts:
                        log_entry = {
                            "EventID": event.EventID,
                            "SourceName": event.SourceName,
                            "TimeGenerated": event.TimeGenerated.strftime("%Y-%m-%d %H:%M:%S"),
                            "Message": ' '.join(event.StringInserts)
                        }
                        logs.append(log_entry)

            return logs

        except Exception as e:
            return [{"Error": f"로그를 읽는 중 오류 발생: {str(e)}"}]

        finally:
            # 핸들 닫기
            try:
                win32evtlog.CloseEventLog(hand)
            except Exception as close_error:
                return [{"Error": f"로그 핸들을 닫는 중 오류 발생: {str(close_error)}"}]

# 사용 예시
if __name__ == "__main__":
    viewer = LogViewer()
    application_logs = viewer.get_application_logs_for_file()

    if application_logs:
        for log in application_logs:
            print(log)
    else:
        print("로그가 없습니다.")
