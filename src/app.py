import os
import requests
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# --- PHẦN 1: Web server giả để Render luôn thấy bot "Online" ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Nexus-Core is alive and scanning!", 200

def run_flask():
    # Render chỉ định cổng qua biến môi trường PORT
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# Chạy server trong một luồng riêng biệt
Thread(target=run_flask, daemon=True).start()

# --- PHẦN 2: Core chính của Slack Bot ---
load_dotenv()
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

@app.command("/nexus-scan")
def scan_command(ack, body):
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
        critical_headers = ['Content-Security-Policy', 'X-Frame-Options', 'Strict-Transport-Security']
        missing = [h for h in critical_headers if h not in headers]
        
        if not missing:
            result = f"✅ Website {target} có vẻ an toàn."
        else:
            result = f"⚠️ Website {target} đang thiếu các bảo mật: {', '.join(missing)}"
    except Exception as e:
        result = f"❌ Không thể quét được: {str(e)}"
    
    app.client.chat_postMessage(channel=body["channel_id"], text=result)

@app.command("/nexus-status")
def status_command(ack):
    ack("Nexus-Core đang online 24/7. Hệ thống: *Stable* 🚀")

# --- PHẦN 3: Khởi chạy SocketMode ---
if __name__ == "__main__":
    print("⚡️ Nexus-Core đã khởi động thành công!")
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()