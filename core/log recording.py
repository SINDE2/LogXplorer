import xml.etree.ElementTree as ET


def load_event_logs(file_path, start_time, end_time):
    print(f"파일: {file_path}")
    print(f"시작 시간: {start_time}")
    print(f"종료 시간: {end_time}")
    print("\n로그:\n")

    # evtx 로그 불러오기 예시
    display_event_logs(file_path, start_time, end_time)


def display_event_logs(file_path, start_time, end_time):
    # 여기에 evtx 파일을 읽고, 시간 범위 내의 로그를 필터링하여 표시하는 로직을 구현
    try:
        # 실제로는 evtx 파일을 파싱해야 합니다. 예시로 XML 파싱 코드 작성
        tree = ET.parse(file_path)
        root = tree.getroot()

        for event in root.findall('.//Event'):
            event_time = event.find('TimeCreated').text  # 이벤트 시간 (실제 evtx 포맷에 따라 다를 수 있음)
            if start_time <= event_time <= end_time:
                message = event.find('Message').text
                print(message)

    except Exception as e:
        print(f"로그 불러오기 실패: {str(e)}")


# 예시 사용
file_path = "Application.evtx"  # evtx 파일 경로
start_time = "2024-01-01T00:00:00"   # 시작 시간
end_time = "2024-12-31T23:59:59"     # 종료 시간

load_event_logs(file_path, start_time, end_time)
