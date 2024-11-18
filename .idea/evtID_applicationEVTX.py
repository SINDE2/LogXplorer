#Application.evtx에서 이벤트 로그 대조 및 출력
def parse_and_display_logs(file_path, target_evtids):
    results = []
    with Evtx(file_path) as evtx_file:
        for record in evtx_file.records_json():
            log = json.loads(record)
            event_id = log.get("Event", {}).get("System", {}).get("EventID", {}).get("#text", None)
            if event_id and int(event_id) in target_evtids:
                results.append({
                    "EventID": int(event_id),
                    "TimeCreated": log.get("Event", {}).get("System", {}).get("TimeCreated", {}).get("@SystemTime", "Unknown"),
                    "EventType": log.get("Event", {}).get("System", {}).get("Level", "Unknown"),  # Level은 타입(정보/경고 등)
                    "EventData": log.get("Event", {}).get("EventData", {}).get("Data", [])
                })

#GUI 결과 표시
    display_results(results)

def display_results(results):
    result_window = tk.Toplevel()
    result_window.title("Event Log Details")
    text = tk.Text(result_window)
    text.pack(fill=tk.BOTH, expand=True)

    text.insert(tk.END, "Matched Events:\n\n")
    for result in results:
        text.insert(tk.END, f"Event ID: {result['EventID']}\n")
        text.insert(tk.END, f"Time Created: {result['TimeCreated']}\n")
        text.insert(tk.END, f"Event Type: {result['EventType']}\n")
        text.insert(tk.END, f"Event Data: {result['EventData']}\n")
        text.insert(tk.END, "-" * 40 + "\n")

def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Event Log Files", "*.evtx")],
        title="Select an .evtx File"
    )
    if file_path:
        target_evtids = [1000, 1001]  # 검색할 이벤트 ID 리스트
        parse_and_display_logs(file_path, target_evtids)
def main():
    root = tk.Tk()
    root.title("Event Log File Explorer")
    root.geometry("400x200")
    btn = tk.Button(root, text="Open .evtx File", command=openfile)
    btn.pack(pady=20)
    root.mainloop()

if name == "_main":
    main()
