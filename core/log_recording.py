import win32evtlog
import subprocess

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

def parse_and_interpret_event_logs(target_file):
    """
    Windows Security 로그에서 특정 파일 관련 이벤트를 파싱하고 해석
    Args:
        target_file (str): 추적할 파일 경로
    """
    log_type = 'Security'  #필요에 따라 Application으로 변경 가능
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

                if event_message and target_file in str(event_message).replace('\\\\', '\\'):
                    log_data = interpret_event(event_id, event_message, event_time)
                    if log_data:
                        events.append(log_data)
    except Exception as e:
        print(f"Error reading logs: {e}")
    finally:
        win32evtlog.CloseEventLog(hand)

    # 출력: 사람이 읽을 수 있는 형태로 정리
    for event in events:
        print("-" * 50)
        print(f"Time: {event['time']}")
        print(f"User: {event['user_name']} ({event['user_sid']})")
        print(f"Domain: {event['domain_name']}")
        print(f"Accessed File: {event['object_name']}")
        print(f"Event Type: {event['event_type']}")
        if "access_type" in event:
            print(f"Access Type: {event['access_type']}")
        if "process_name" in event:
            print(f"Process Name: {event['process_name']}")
        print("-" * 50)


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
        "0x100":"WriteAttributes",
        "0x10000": "DELETE",
        "0x20000": "Write Attributes"
    }
    return access_types.get(access_mask, f"Unknown Access (Mask: {access_mask})")


if __name__ == "__main__":
    # 추적할 파일 경로
    target_path = r"C:\Users\SINDE\Downloads"
    enable_audit_policy()
    set_audit_with_powershell(target_path)

    target_file = target_path + r"\test"

    # # 로그 파싱 및 해석
    parse_and_interpret_event_logs(target_file)
