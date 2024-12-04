import win32evtlog
import winreg
import os
import subprocess
import datetime


def enable_audit_policy():
    """
    Enable audit policy for object access
    """
    try:
        command = [
            "powershell",
            "-Command",
            "Start-Process",
            "powershell.exe",
            "-ArgumentList",
            "'auditpol /set /category:\"개체 액세스\" /success:enable /failure:enable'",
            "-Verb", "RunAs"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print("Audit policy for 'Object Access' successfully enabled.")
        else:
            print(f"Failed to enable audit policy: {result.stderr}")
    except Exception as e:
        print(f"Error enabling audit policy: {e}")


def set_audit_with_powershell(target_path, user="Everyone"):
    """
    특정 파일/폴더와 모든 하위 항목에 감사 항목 추가
    Args:
        target_path (str): 감사 항목을 추가할 상위 폴더 경로
        user (str): 감사 항목을 설정할 사용자 (기본값: "Everyone")
    """
    try:
        command = [
            "powershell",
            "-Command",
            f"$acl = Get-Acl '{target_path}'; "
            f"$audit = New-Object System.Security.AccessControl.FileSystemAuditRule("
            f"'{user}', 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Success,Failure'); "
            f"$acl.AddAuditRule($audit); "
            f"Set-Acl '{target_path}' $acl"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully set audit rule for {target_path} and its subdirectories.")
        else:
            print(f"Failed to set audit rule: {result.stderr}")
    except Exception as e:
        print(f"Error setting audit rule: {e}")


def parse_and_interpret_event_logs(target_file, start_time=None, end_time=None):
    """
    Windows Security 로그에서 특정 파일 관련 이벤트를 파싱하고 해석
    Args:
        target_file (str): 추적할 파일 경로
    Returns:
        str: 사람이 읽을 수 있는 이벤트 로그 데이터
    """
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else None
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else None

    log_type = 'Security'
    server = None  # 로컬 시스템
    hand = win32evtlog.OpenEventLog(server, log_type)

    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = []

    try:
        while True:
            logs = win32evtlog.ReadEventLog(hand, flags, 0)
            if not logs:
                break
            for event in logs:
                event_id = event.EventID
                event_message = event.StringInserts
                event_time = event.TimeGenerated

                if event_message and target_file in str(event_message):
                    log_data = interpret_event(event_id, event_message, event_time)
                    if log_data:
                        events.append(log_data)
    except Exception as e:
        return f"Error reading logs: {e}"
    finally:
        win32evtlog.CloseEventLog(hand)
    print('done!')
    # 결과 문자열로 변환
    output = []
    for event in events:
        if start_time and end_time:
            event_time = datetime.datetime.strptime(event["time"], "%Y-%m-%d %H:%M:%S")
            if not (start_time <= event_time <= end_time):
                continue
        output.append("-" * 50)
        output.append(f"Time: {event['time']}")
        output.append(f"User: {event['user_name']} ({event['user_sid']})")
        output.append(f"Domain: {event['domain_name']}")
        output.append(f"Accessed File: {event['object_name']}")
        output.append(f"Event Type: {event['event_type']}")
        if "access_type" in event:
            output.append(f"Access Type: {event['access_type']}")
        if "process_name" in event:
            output.append(f"Process Name: {event['process_name']}")
        output.append("-" * 50)
    print(output[:3])
    return "\n".join(output)



def interpret_event(event_id, event_message, event_time):
    """
    이벤트 메시지를 해석하여 의미 있는 데이터 추출
    Args:
        event_id (int): 이벤트 ID
        event_message (list): 이벤트 메시지 데이터
        event_time (datetime): 이벤트 발생 시간
    Returns:
        dict: 해석된 이벤트 데이터
    """
    try:
        # 이벤트 메시지의 각 데이터 매핑
        data_mapping = {
            "subject_user_sid": event_message[0],
            "user_name": event_message[1],
            "domain_name": event_message[2],
            "logon_id": event_message[3],
            "object_server": event_message[4],
            "object_type": event_message[5],
            "object_name": event_message[6],
            "handle_id": event_message[7],
            "access_list": event_message[8],
            "access_mask": event_message[9],
            "process_id": event_message[10],
            "process_name": event_message[11],
            "resource_attributes": event_message[12] if len(event_message) > 12 else None
        }

        # 이벤트 ID 별 해석
        if event_id == 4663:  # 객체 액세스 이벤트
            access_type = interpret_access_mask(data_mapping["access_mask"])
            event_type = "File Access Attempt"
        elif event_id == 4656:  # 핸들 요청
            access_type = "Handle Requested"
            event_type = "File Handle Requested"
        elif event_id == 4658:  # 핸들 닫기
            access_type = "Handle Closed"
            event_type = "File Handle Closed"
        elif event_id == 4670:  # 권한 변경
            access_type = "Permissions Changed"
            event_type = "File Permissions Changed"
        elif event_id == 5140:  # 네트워크 공유 파일 액세스
            access_type = "Network Share Access"
            event_type = "Network File Access"
        else:
            access_type = "Unknown Access"
            event_type = "Unknown Event"

        # 해석된 데이터 반환
        return {
            "time": event_time.strftime("%Y-%m-%d %H:%M:%S"),
            "user_sid": data_mapping["subject_user_sid"],
            "user_name": data_mapping["user_name"],
            "domain_name": data_mapping["domain_name"],
            "object_name": data_mapping["object_name"],
            "access_type": access_type,
            "event_type": event_type,
            "process_name": data_mapping["process_name"]
        }
    except Exception as e:
        print(f"Error interpreting event: {e}")
        return None


def interpret_access_mask(access_mask):
    """
    Access Mask 값을 해석
    Args:
        access_mask (str): Access Mask 값
    Returns:
        str: 액세스 유형
    """
    access_types = {
        "0x1": "ReadData",
        "0x2": "WriteData",
        "0x4": "AppendData",
        "0x8": "ReadEA",
        "0x10": "WriteEA",
        "0x20": "Execute/Traverse",
        "0x40": "DeleteChild",
        "0x80": "ReadAttributes",
        "0x100": "WriteAttributes",
        "0x10000": "DELETE",
        "0x20000": "Write Attributes"
    }
    return access_types.get(access_mask, f"Unknown Access (Mask: {access_mask})")

def set_eventlog_max_size(log_name='Security', max_size_mb=128):
    """
    이벤트 로그의 최대 크기를 설정합니다.
    Args:
        log_name (str): 로그 이름 (예: Security, Application 등)
        max_size_mb (int): 설정할 최대 크기 (MB 단위)
    Returns:
        str 또는 True: 성공 시 True, 실패 시 오류 메시지
    """
    try:
        reg_path = f"SYSTEM\\CurrentControlSet\\Services\\EventLog\\{log_name}"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_WRITE)

        # 바이트로 변환
        max_size_bytes = max_size_mb * 1024 * 1024

        # 최대 크기 설정
        winreg.SetValueEx(key, "MaxSize", 0, winreg.REG_DWORD, max_size_bytes)
        winreg.CloseKey(key)

        return True
    except Exception as e:
        return f"Error setting log size: {str(e)}"



def expand_environment_variables(path):
    """
    환경 변수가 포함된 경로를 실제 경로로 변환합니다.
    """
    import win32api
    try:
        return win32api.ExpandEnvironmentStrings(path)
    except Exception:
        return path


def get_eventlog_usage(log_name='Security'):
    """
    이벤트 로그의 현재 사용량 정보를 반환합니다.
    """
    try:
        # 레지스트리에서 정보 가져오기
        reg_path = f"SYSTEM\\CurrentControlSet\\Services\\EventLog\\{log_name}"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        max_size = winreg.QueryValueEx(key, "MaxSize")[0]
        log_file_path = winreg.QueryValueEx(key, "File")[0]
        winreg.CloseKey(key)

        # 환경 변수 확장
        real_log_path = expand_environment_variables(log_file_path)

        # 현재 로그 파일 크기 확인
        current_size = os.path.getsize(real_log_path)

        # 현재 로그 정보 가져오기
        handle = win32evtlog.OpenEventLog(None, log_name)
        total_records = win32evtlog.GetNumberOfEventLogRecords(handle)

        # 최신 레코드 시간 가져오기
        newest_time = None
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(handle, flags, 0)
        if events:
            newest_time = events[0].TimeGenerated

        # 가장 오래된 레코드 시간 가져오기
        oldest_time = None
        handle_f = win32evtlog.OpenEventLog(None, log_name)
        flags = win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ
        events = win32evtlog.ReadEventLog(handle_f, flags, 0)
        if events:
            oldest_time = events[0].TimeGenerated

        win32evtlog.CloseEventLog(handle)

        # 결과 문자열로 반환
        result = [
            f"최대 크기: {max_size / (1024 * 1024):.2f} MB",
            f"현재 크기: {current_size / (1024 * 1024):.2f} MB",
            f"사용량: {(current_size / max_size) * 100:.1f}%",
            f"가장 오래된 레코드 시간\n- {oldest_time.strftime('%Y-%m-%d %H:%M:%S') if oldest_time else 'N/A'}\n",
            f"최신 레코드 시간\n- {newest_time.strftime('%Y-%m-%d %H:%M:%S') if newest_time else 'N/A'}\n",
        ]

        if oldest_time and newest_time:
            time_diff = newest_time - oldest_time
            retention_days = time_diff.days
            retention_hours = time_diff.total_seconds() / 3600

            if retention_days > 0:
                result.append(f"로그 보존 기간: {retention_days} 일")
            else:
                result.append(f"로그 보존 기간: {retention_hours:.1f} 시간")

        return "\n".join(result)

    except Exception as e:
        return f"Error: {str(e)}"


# if __name__ == "__main__":
#     # 추적할 파일 경로
#     target_path = r""  # 로깅하고 싶은 파일 주소 입력
#     enable_audit_policy()
#     set_audit_with_powershell(target_path)

#     # Security 이벤트 로그 사용량 확인
#     set_eventlog_max_size()
#     get_eventlog_usage('Security')
#     print("\n")

#     target_file = target_path + r""  # 파일 이름 입력

#     # 이 파일 실행 시 시간 설정 조금 짧게 해야함
#     start_time = "2024-12-04 17:57:40"
#     end_time = "2024-12-04 18:15:16"

#     # # 로그 파싱 및 해석
#     parse_and_interpret_event_logs(target_file, start_time, end_time)