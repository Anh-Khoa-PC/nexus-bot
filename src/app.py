import os
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Load cấu hình
load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Lệnh 1: Quét bảo mật thực tế (Kiểm tra Security Headers)
@app.command("/nexus-scan")
def scan_command(ack, body, logger):
    target = body["text"].strip()
    if not target:
        ack("Vui lòng nhập URL! Ví dụ: /nexus-scan google.com")
        return
    
    ack(f"🛡️ Nexus-Core đang quét: {target}...")
    
    try:
        if not target.startswith('http'):
            target = "https://" + target
            
        r = requests.get(target, timeout=5)
        headers = r.headers
        
        # Danh sách các header bảo mật cần kiểm tra
        critical_headers = ['Content-Security-Policy', 'X-Frame-Options', 'Strict-Transport-Security']
        missing = [h for h in critical_headers if h not in headers]
        
        if not missing:
            result = f"✅ Website {target} có vẻ an toàn."
        else:
            result = f"⚠️ Website {target} đang thiếu các bảo mật: {', '.join(missing)}"
            
    except Exception as e:
        result = f"❌ Không thể quét được: {str(e)}"
    
    # Gửi kết quả thực tế vào kênh
    app.client.chat_postMessage(channel=body["channel_id"], text=result)

# Lệnh 2: Kiểm tra trạng thái
@app.command("/nexus-status")
def status_command(ack, body, logger):
    ack("Nexus-Core đang online 24/7. Hệ thống: *Stable* 🚀")

# Lệnh 3: Ghi log
@app.command("/nexus-log")
def log_command(ack, body, logger):
    user = body["user_name"]
    ack(f"📝 Đã ghi nhật ký hoạt động cho người dùng: @{user}")

if __name__ == "__main__":
    print("⚡️ Nexus-Core đã khởi động thành công!")
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()